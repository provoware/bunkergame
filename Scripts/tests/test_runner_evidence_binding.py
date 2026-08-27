#!/usr/bin/env python3
"""Regression tests for UE runner readiness context binding."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import runner_identity as identity
import runner_readiness_contract as contract


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


admin = load_module("runner_binding_admin", SCRIPTS / "github_p0_admin.py")
readiness = load_module("runner_binding_readiness", SCRIPTS / "runner_readiness.py")


class RepositoryIdentityTests(unittest.TestCase):
    def test_https_remote_is_normalized(self):
        self.assertEqual(
            identity.normalize_repository_identity("https://github.com/provoware/bunkergame.git"),
            identity.EXPECTED_REPOSITORY,
        )

    def test_scp_ssh_remote_is_normalized(self):
        self.assertEqual(
            identity.normalize_repository_identity("git@github.com:provoware/bunkergame.git"),
            identity.EXPECTED_REPOSITORY,
        )

    def test_ssh_url_remote_is_normalized(self):
        self.assertEqual(
            identity.normalize_repository_identity("ssh://git@github.com/provoware/bunkergame.git"),
            identity.EXPECTED_REPOSITORY,
        )

    def test_non_github_remote_is_rejected(self):
        self.assertIsNone(identity.normalize_repository_identity("https://example.com/provoware/bunkergame.git"))


class RunnerReadinessContractTests(unittest.TestCase):
    HEAD = "a" * 40
    OTHER_HEAD = "b" * 40
    FINGERPRINT = "c" * 64
    OTHER_FINGERPRINT = "d" * 64

    def make_report(self, *, now: datetime | None = None) -> dict:
        observed = now or datetime.now(timezone.utc)
        return {
            "schema_version": contract.SCHEMA_VERSION,
            "kind": contract.KIND,
            "generated_at_utc": observed.isoformat().replace("+00:00", "Z"),
            "runtime_executed": False,
            "cp1_pass": False,
            "status": "PASS",
            "repository": identity.EXPECTED_REPOSITORY,
            "git_head_sha": self.HEAD,
            "machine_fingerprint_sha256": self.FINGERPRINT,
            "machine_identity_scheme": identity.MACHINE_IDENTITY_SCHEME,
            "engine_version": "5.8",
            "engine_version_raw": {"MajorVersion": 5, "MinorVersion": 8},
            "checks": {name: True for name in contract.REQUIRED_CHECKS},
        }

    def validate(self, report: dict, *, now: datetime | None = None):
        return contract.validate_readiness_report(
            report,
            expected_repository=identity.EXPECTED_REPOSITORY,
            expected_head=self.HEAD,
            expected_machine_fingerprint=self.FINGERPRINT,
            now=now,
        )

    def test_exact_bound_report_passes(self):
        ok, detail = self.validate(self.make_report())
        self.assertTrue(ok, detail)
        self.assertIn("checkout- und maschinengebundene", detail)

    def test_different_git_head_is_blocked(self):
        report = self.make_report()
        report["git_head_sha"] = self.OTHER_HEAD
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("anderem Git-HEAD", detail)

    def test_different_machine_is_blocked(self):
        report = self.make_report()
        report["machine_fingerprint_sha256"] = self.OTHER_FINGERPRINT
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("nicht von dieser Maschine", detail)

    def test_wrong_repository_is_blocked(self):
        report = self.make_report()
        report["repository"] = "someone/else"
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("falschen Repository", detail)

    def test_missing_required_check_is_blocked(self):
        report = self.make_report()
        report["checks"].pop("git_head_bound")
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("fehlend", detail)

    def test_extra_check_is_blocked(self):
        report = self.make_report()
        report["checks"]["invented_check"] = True
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("unerwartet", detail)

    def test_false_required_check_is_blocked(self):
        report = self.make_report()
        report["checks"]["repository_identity_exact"] = False
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("exakt true", detail)

    def test_boolean_schema_is_blocked(self):
        report = self.make_report()
        report["schema_version"] = True
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("Schema-Version", detail)

    def test_old_schema_v2_is_blocked(self):
        report = self.make_report()
        report["schema_version"] = 2
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("Schema-Version", detail)

    def test_boolean_engine_major_is_blocked(self):
        report = self.make_report()
        report["engine_version_raw"]["MajorVersion"] = True
        ok, detail = self.validate(report)
        self.assertFalse(ok)
        self.assertIn("nicht echte Integer", detail)

    def test_stale_report_is_blocked(self):
        observed = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)
        report = self.make_report(now=observed)
        ok, detail = self.validate(report, now=observed + timedelta(minutes=31))
        self.assertFalse(ok)
        self.assertIn("zu alt", detail)

    def test_future_report_is_blocked(self):
        reference = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)
        report = self.make_report(now=reference + timedelta(minutes=10))
        ok, detail = self.validate(report, now=reference)
        self.assertFalse(ok)
        self.assertIn("Zukunft", detail)


class AdminRunnerBindingTests(unittest.TestCase):
    HEAD = "a" * 40
    FINGERPRINT = "c" * 64

    def make_report(self) -> dict:
        return {
            "schema_version": contract.SCHEMA_VERSION,
            "kind": contract.KIND,
            "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "runtime_executed": False,
            "cp1_pass": False,
            "status": "PASS",
            "repository": identity.EXPECTED_REPOSITORY,
            "git_head_sha": self.HEAD,
            "machine_fingerprint_sha256": self.FINGERPRINT,
            "machine_identity_scheme": identity.MACHINE_IDENTITY_SCHEME,
            "engine_version": "5.8",
            "engine_version_raw": {"MajorVersion": 5, "MinorVersion": 8},
            "checks": {name: True for name in contract.REQUIRED_CHECKS},
        }

    def setUp(self):
        self.original_repo = admin.current_repository_identity
        self.original_head = admin.current_git_head
        self.original_machine = admin.machine_fingerprint
        self.original_clean = admin.git_worktree_clean

        admin.current_repository_identity = lambda root: (identity.EXPECTED_REPOSITORY, "ok")
        admin.current_git_head = lambda root: (self.HEAD, "ok")
        admin.machine_fingerprint = lambda: (self.FINGERPRINT, identity.MACHINE_IDENTITY_SCHEME)
        admin.git_worktree_clean = lambda root: (True, "clean")

    def tearDown(self):
        admin.current_repository_identity = self.original_repo
        admin.current_git_head = self.original_head
        admin.machine_fingerprint = self.original_machine
        admin.git_worktree_clean = self.original_clean

    def validate_file(self, report: dict):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "runner_readiness.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            return admin.validate_fresh_readiness(path)

    def test_admin_accepts_bound_report_on_same_clean_checkout(self):
        ok, detail = self.validate_file(self.make_report())
        self.assertTrue(ok, detail)
        self.assertIn("Worktree erneut sauber", detail)

    def test_admin_blocks_dirty_worktree_after_readiness(self):
        admin.git_worktree_clean = lambda root: (False, "1 changed/untracked path(s)")
        ok, detail = self.validate_file(self.make_report())
        self.assertFalse(ok)
        self.assertIn("nicht sauber", detail)

    def test_admin_blocks_head_change_after_readiness(self):
        admin.current_git_head = lambda root: ("b" * 40, "ok")
        ok, detail = self.validate_file(self.make_report())
        self.assertFalse(ok)
        self.assertIn("anderem Git-HEAD", detail)

    def test_admin_blocks_machine_change_after_readiness(self):
        admin.machine_fingerprint = lambda: ("d" * 64, identity.MACHINE_IDENTITY_SCHEME)
        ok, detail = self.validate_file(self.make_report())
        self.assertFalse(ok)
        self.assertIn("nicht von dieser Maschine", detail)


class EngineVersionTypeTests(unittest.TestCase):
    def test_boolean_major_version_is_rejected_by_collector(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            version = root / "Engine" / "Build" / "Build.version"
            version.parent.mkdir(parents=True)
            version.write_text(json.dumps({"MajorVersion": True, "MinorVersion": 8}), encoding="utf-8")
            ok, _, _ = readiness.read_engine_version(root)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
