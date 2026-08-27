#!/usr/bin/env python3
"""Regression tests for the GitHub/UE P0 control plane."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


admin = load_module("github_p0_admin", ROOT / "Scripts" / "github_p0_admin.py")
readiness = load_module("runner_readiness", ROOT / "Scripts" / "runner_readiness.py")
preflight = load_module("p0_preflight", ROOT / "Scripts" / "p0_preflight.py")


class ReadinessEvidenceTests(unittest.TestCase):
    def make_report(self, **overrides) -> dict:
        data = {
            "schema_version": 2,
            "kind": "UE58_RUNNER_READINESS",
            "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "runtime_executed": False,
            "cp1_pass": False,
            "status": "PASS",
            "checks": {
                "project_file": True,
                "editor_target": True,
                "engine_root_detected": True,
                "unreal_editor_detected": True,
                "engine_build_script_detected": True,
                "engine_version_exact_5_8": True,
                "python_available": True,
                "repo_writable": True,
                "free_disk_gt_5gb": True,
                "git_worktree_clean_before_runtime": True,
            },
        }
        data.update(overrides)
        return data

    def validate(self, data: dict) -> tuple[bool, str]:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "runner_readiness.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return admin.validate_fresh_readiness(path)

    def test_fresh_pass_is_accepted(self):
        ok, detail = self.validate(self.make_report())
        self.assertTrue(ok, detail)

    def test_missing_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            ok, detail = admin.validate_fresh_readiness(Path(td) / "missing.json")
        self.assertFalse(ok)
        self.assertIn("fehlt", detail)

    def test_failed_status_is_blocked(self):
        ok, detail = self.validate(self.make_report(status="FAIL"))
        self.assertFalse(ok)
        self.assertIn("nicht PASS", detail)

    def test_old_evidence_is_blocked(self):
        stamp = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
        ok, detail = self.validate(self.make_report(generated_at_utc=stamp))
        self.assertFalse(ok)
        self.assertIn("zu alt", detail)

    def test_future_evidence_is_blocked(self):
        stamp = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat().replace("+00:00", "Z")
        ok, detail = self.validate(self.make_report(generated_at_utc=stamp))
        self.assertFalse(ok)
        self.assertIn("Zukunft", detail)

    def test_wrong_schema_is_blocked(self):
        ok, detail = self.validate(self.make_report(schema_version=1))
        self.assertFalse(ok)
        self.assertIn("Schema", detail)

    def test_runtime_claim_in_readiness_is_blocked(self):
        ok, detail = self.validate(self.make_report(runtime_executed=True))
        self.assertFalse(ok)
        self.assertIn("Runtime", detail)

    def test_non_58_engine_check_is_blocked(self):
        data = self.make_report()
        data["checks"]["engine_version_exact_5_8"] = False
        ok, detail = self.validate(data)
        self.assertFalse(ok)
        self.assertIn("Readiness-Checks", detail)


class EngineVersionTests(unittest.TestCase):
    def write_version(self, root: Path, major: int, minor: int) -> None:
        path = root / "Engine" / "Build" / "Build.version"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"MajorVersion": major, "MinorVersion": minor}), encoding="utf-8")

    def test_exact_58_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_version(root, 5, 8)
            ok, data, detail = readiness.read_engine_version(root)
        self.assertTrue(ok)
        self.assertEqual(data["MajorVersion"], 5)
        self.assertEqual(detail, "5.8")

    def test_57_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_version(root, 5, 7)
            ok, _, detail = readiness.read_engine_version(root)
        self.assertFalse(ok)
        self.assertEqual(detail, "5.7")

    def test_missing_version_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            ok, data, detail = readiness.read_engine_version(Path(td))
        self.assertFalse(ok)
        self.assertIsNone(data)
        self.assertIn("missing", detail)


class PreflightDecisionTests(unittest.TestCase):
    def result(self, key: str, code: int) -> object:
        steps = {step.key: step for step in (*preflight.BASE_STEPS, preflight.READINESS_STEP)}
        return preflight.StepResult(steps[key], code)

    def test_static_failure_is_first_action(self):
        results = [self.result("static", 1), self.result("quality", 0), self.result("github", 0)]
        self.assertIn("Statische Fehler", preflight.next_action(results, False))

    def test_quality_failure_is_second_action(self):
        results = [self.result("static", 0), self.result("quality", 1), self.result("github", 0)]
        self.assertIn("Quality Guard", preflight.next_action(results, False))

    def test_github_failure_points_to_branch_admin(self):
        results = [self.result("static", 0), self.result("quality", 0), self.result("github", 2)]
        self.assertIn("github_p0_admin.py --apply", preflight.next_action(results, False))

    def test_hosted_pass_points_to_ue_machine(self):
        results = [self.result("static", 0), self.result("quality", 0), self.result("github", 0)]
        self.assertIn("--full", preflight.next_action(results, False))

    def test_full_readiness_failure_blocks_activation(self):
        results = [
            self.result("static", 0),
            self.result("quality", 0),
            self.result("github", 0),
            self.result("readiness", 1),
        ]
        action = preflight.next_action(results, True)
        self.assertIn("Readiness", action)
        self.assertNotIn("enable-runner-variable", action)

    def test_full_pass_points_to_guarded_activation(self):
        results = [
            self.result("static", 0),
            self.result("quality", 0),
            self.result("github", 0),
            self.result("readiness", 0),
        ]
        action = preflight.next_action(results, True)
        self.assertIn("--enable-runner-variable", action)
        self.assertIn("CP1 UE 5.8 Runtime", action)


if __name__ == "__main__":
    unittest.main()
