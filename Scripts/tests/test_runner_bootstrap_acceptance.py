#!/usr/bin/env python3
"""Regression tests for UE 5.8 runner bootstrap acceptance and public proof."""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import github_runner_bootstrap_public_verify as public
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
