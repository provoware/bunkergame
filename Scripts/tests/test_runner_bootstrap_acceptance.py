#!/usr/bin/env python3
"""Regression tests for UE 5.8 runner bootstrap acceptance and public proof."""

from __future__ import annotations

import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import github_p0_admin as admin
import github_runner_bootstrap_public_verify as public
import p0_preflight as preflight
import runner_bootstrap_contract as contract


class RunnerBootstrapContractTests(unittest.TestCase):
    SHA = "a" * 40
    NOW = datetime(2026, 8, 27, 19, 0, tzinfo=timezone.utc)

    def make_run(self) -> dict:
        stamp = (self.NOW - timedelta(minutes=2)).isoformat().replace("+00:00", "Z")
        return {
            "id": 1234,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": self.SHA,
            "path": contract.WORKFLOW_PATH,
            "repository": {"full_name": contract.EXPECTED_REPOSITORY},
            "status": "completed",
            "conclusion": "success",
            "run_attempt": 1,
            "run_number": 7,
            "created_at": stamp,
            "updated_at": stamp,
        }

    def make_job(self) -> dict:
        return {
            "name": contract.JOB_NAME,
            "status": "completed",
            "conclusion": "success",
            "runner_name": "ue58-linux-01",
            "runner_group_name": "Default",
            "labels": ["self-hosted", "Linux", "X64", "unreal", "ue-5.8"],
            "steps": [
                {"name": name, "status": "completed", "conclusion": "success"}
                for name in contract.REQUIRED_SUCCESS_STEPS
            ],
        }

    def test_current_main_manual_success_run_passes(self):
        ok, detail = contract.validate_workflow_run(self.make_run(), self.SHA, now=self.NOW)
        self.assertTrue(ok, detail)

    def test_non_manual_run_is_blocked(self):
        run = self.make_run()
        run["event"] = "pull_request"
        ok, detail = contract.validate_workflow_run(run, self.SHA, now=self.NOW)
        self.assertFalse(ok)
        self.assertIn("workflow_dispatch", detail)

    def test_old_main_sha_is_blocked(self):
        run = self.make_run()
        run["head_sha"] = "b" * 40
        selected, detail = contract.select_latest_current_main_run([run], self.SHA)
        self.assertIsNone(selected)
        self.assertIn("aktuellen main-SHA", detail)

    def test_stale_run_is_blocked(self):
        run = self.make_run()
        run["updated_at"] = (self.NOW - timedelta(minutes=31)).isoformat().replace("+00:00", "Z")
        ok, detail = contract.validate_workflow_run(run, self.SHA, now=self.NOW)
        self.assertFalse(ok)
        self.assertIn("zu alt", detail)

    def test_missing_required_runner_label_is_blocked(self):
        job = self.make_job()
        job["labels"].remove("ue-5.8")
        ok, detail = contract.validate_runner_job(job)
        self.assertFalse(ok)
        self.assertIn("ue-5.8", detail)

    def test_missing_readiness_step_is_blocked(self):
        job = self.make_job()
        job["steps"] = [item for item in job["steps"] if item["name"] != "UE 5.8 runner readiness v3"]
        ok, detail = contract.validate_runner_job(job)
        self.assertFalse(ok)
        self.assertIn("Pflichtschritt", detail)

    def test_runner_name_is_required(self):
        job = self.make_job()
        job["runner_name"] = None
        ok, detail = contract.validate_runner_job(job)
        self.assertFalse(ok)
        self.assertIn("Runner", detail)


class PublicRunnerBootstrapVerifierTests(RunnerBootstrapContractTests):
    def setUp(self):
        self.original_get = public.github_get

    def tearDown(self):
        public.github_get = self.original_get

    def test_public_verifier_passes_only_with_live_run_and_job(self):
        run = self.make_run()
        job = self.make_job()

        def fake_get(path: str):
            if path.endswith("/branches/main"):
                return True, {"name": "main", "commit": {"sha": self.SHA}}, ""
            if "/actions/workflows/" in path:
                return True, {"workflow_runs": [run]}, ""
            if f"/actions/runs/{run['id']}/jobs" in path:
                return True, {"jobs": [job]}, ""
            return False, None, "unexpected endpoint"

        public.github_get = fake_get
        ok, detail, proof = public.verify_public_runner_bootstrap(now=self.NOW)
        self.assertTrue(ok, detail)
        self.assertEqual(proof["runner_name"], "ue58-linux-01")
        self.assertEqual(proof["main_sha"], self.SHA)

    def test_public_verifier_rejects_latest_failed_run(self):
        run = self.make_run()
        run["conclusion"] = "failure"

        def fake_get(path: str):
            if path.endswith("/branches/main"):
                return True, {"name": "main", "commit": {"sha": self.SHA}}, ""
            if "/actions/workflows/" in path:
                return True, {"workflow_runs": [run]}, ""
            return False, None, "jobs must not be queried"

        public.github_get = fake_get
        ok, detail, _ = public.verify_public_runner_bootstrap(now=self.NOW)
        self.assertFalse(ok)
        self.assertIn("nicht erfolgreich", detail)


class RunnerActivationGateTests(unittest.TestCase):
    SHA = "a" * 40

    def setUp(self):
        self.original_bootstrap = admin.verify_public_runner_bootstrap
        self.original_repo = admin.current_repository_identity
        self.original_head = admin.current_git_head
        self.original_clean = admin.git_worktree_clean
        self.original_run = admin.run
        self.calls: list[list[str]] = []

        admin.verify_public_runner_bootstrap = lambda: (
            True,
            "server bootstrap pass",
            {"main_sha": self.SHA, "run_id": 1234, "runner_name": "ue58-linux-01"},
        )
        admin.current_repository_identity = lambda root: (admin.EXPECTED_REPOSITORY, "ok")
        admin.current_git_head = lambda root: (self.SHA, "ok")
        admin.git_worktree_clean = lambda root: (True, "clean")

        def fake_run(args, **kwargs):
            self.calls.append(list(args))
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

        admin.run = fake_run

    def tearDown(self):
        admin.verify_public_runner_bootstrap = self.original_bootstrap
        admin.current_repository_identity = self.original_repo
        admin.current_git_head = self.original_head
        admin.git_worktree_clean = self.original_clean
        admin.run = self.original_run

    def test_activation_checkout_must_match_public_main(self):
        admin.current_git_head = lambda root: ("b" * 40, "ok")
        ok, detail = admin.validate_activation_checkout(self.SHA)
        self.assertFalse(ok)
        self.assertIn("aktuellem main", detail)

    def test_activation_checkout_must_be_clean(self):
        admin.git_worktree_clean = lambda root: (False, "dirty")
        ok, detail = admin.validate_activation_checkout(self.SHA)
        self.assertFalse(ok)
        self.assertIn("nicht sauber", detail)

    def test_runner_variable_write_requires_public_bootstrap_proof(self):
        admin.set_runner_variable()
        self.assertTrue(any(call[:3] == ["gh", "variable", "set"] for call in self.calls))

    def test_missing_public_bootstrap_blocks_before_variable_write(self):
        admin.verify_public_runner_bootstrap = lambda: (False, "no current bootstrap", None)
        with self.assertRaises(RuntimeError):
            admin.set_runner_variable()
        self.assertEqual(self.calls, [])


class PreflightBootstrapDecisionTests(unittest.TestCase):
    def result(self, step, code: int):
        return preflight.StepResult(step, code)

    def baseline(self):
        return [self.result(step, 0) for step in preflight.BASE_STEPS]

    def test_full_preflight_blocks_activation_when_server_bootstrap_is_missing(self):
        results = self.baseline() + [
            self.result(preflight.BOOTSTRAP_STEP, 2),
            self.result(preflight.READINESS_STEP, 0),
        ]
        action = preflight.next_action(results, True)
        self.assertIn("Runner Bootstrap Acceptance", action)
        self.assertNotIn("enable-runner-variable", action)


class RunnerBootstrapWorkflowStaticTests(unittest.TestCase):
    def test_workflow_is_manual_only_and_never_runs_cp1(self):
        path = ROOT / ".github" / "workflows" / "ue58-runner-bootstrap.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("push:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("runs-on: [self-hosted, unreal, ue-5.8]", text)
        self.assertIn("python3 Scripts/runner_readiness.py", text)
        self.assertIn("python3 Scripts/runner_bootstrap_evidence.py", text)
        self.assertNotIn("run_cp1_ue58.py", text)
        self.assertNotIn("UE58_RUNNER_ENABLED", text)
        self.assertIn("contents: read", text)


if __name__ == "__main__":
    unittest.main()
