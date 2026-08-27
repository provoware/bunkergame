#!/usr/bin/env python3
"""Regression tests for the machine-readable GitHub P0 evidence bundle."""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import github_p0_evidence as evidence
import github_p0_evidence_validate as validator
import github_p0_ruleset as ruleset


class InfrastructureEvidenceBundleTests(unittest.TestCase):
    MAIN_SHA = "a" * 40
    OTHER_SHA = "b" * 40
    RULESET_ID = 42

    def make_detail(self) -> dict:
        detail = json.loads(json.dumps(ruleset.ruleset_payload()))
        detail["id"] = self.RULESET_ID
        return detail

    def make_getter(
        self,
        *,
        main_sha: str | None = None,
        ruleset_id: int | None = None,
        detail: dict | None = None,
        missing_ruleset: bool = False,
    ):
        sha = main_sha or self.MAIN_SHA
        rid = ruleset_id or self.RULESET_ID
        ruleset_detail = detail or self.make_detail()

        def fake_get(path: str):
            if path.endswith("/branches/main"):
                return True, {"name": "main", "commit": {"sha": sha}}, ""
            if path.endswith("/rulesets"):
                if missing_ruleset:
                    return True, [], ""
                return True, [{"id": rid, "name": ruleset.RULESET_NAME}], ""
            if path.endswith(f"/rulesets/{rid}"):
                return True, ruleset_detail, ""
            return False, None, f"unexpected endpoint: {path}"

        return fake_get

    def make_pass_evidence(self, *, now: datetime | None = None) -> dict:
        return evidence.collect_evidence(getter=self.make_getter(), now=now)

    def test_collector_creates_pass_bundle_from_complete_live_contract(self):
        data = self.make_pass_evidence()
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["contract_status"], "PASS")
        self.assertEqual(data["main_sha"], self.MAIN_SHA)
        self.assertEqual(data["ruleset_id"], self.RULESET_ID)
        self.assertEqual(data["failures"], [])
        self.assertEqual(data["integrity_sha256"], evidence.compute_integrity(data))

    def test_collector_writes_fail_state_when_live_ruleset_is_missing(self):
        data = evidence.collect_evidence(getter=self.make_getter(missing_ruleset=True))
        self.assertEqual(data["status"], "FAIL")
        self.assertEqual(data["contract_status"], "FAIL")
        self.assertTrue(any("found 0" in item for item in data["failures"]))
        self.assertEqual(data["integrity_sha256"], evidence.compute_integrity(data))

    def test_fresh_sealed_pass_record_is_structurally_valid(self):
        now = datetime(2026, 8, 27, 14, 0, tzinfo=timezone.utc)
        data = self.make_pass_evidence(now=now)
        ok, failures = validator.validate_record(data, now=now + timedelta(minutes=5))
        self.assertTrue(ok, failures)
        self.assertEqual(failures, [])

    def test_tampered_bundle_is_blocked_by_integrity_digest(self):
        data = self.make_pass_evidence()
        data["main_sha"] = self.OTHER_SHA
        ok, failures = validator.validate_record(data)
        self.assertFalse(ok)
        self.assertTrue(any("integrity_sha256 mismatch" in item for item in failures))

    def test_stale_bundle_is_blocked(self):
        observed = datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc)
        data = self.make_pass_evidence(now=observed)
        ok, failures = validator.validate_record(data, now=observed + timedelta(hours=40))
        self.assertFalse(ok)
        self.assertTrue(any("stale" in item for item in failures))

    def test_wrong_repository_is_blocked_even_after_resealing(self):
        data = self.make_pass_evidence()
        data["repository"] = "someone/else"
        data = evidence.seal_evidence(data)
        ok, failures = validator.validate_record(data)
        self.assertFalse(ok)
        self.assertTrue(any("different repository" in item for item in failures))

    def test_live_recheck_blocks_main_sha_drift(self):
        data = self.make_pass_evidence()
        ok, failures = validator.live_recheck(
            data,
            getter=self.make_getter(main_sha=self.OTHER_SHA),
        )
        self.assertFalse(ok)
        self.assertTrue(any("main SHA drift" in item for item in failures))

    def test_live_recheck_blocks_ruleset_id_drift(self):
        data = self.make_pass_evidence()
        ok, failures = validator.live_recheck(
            data,
            getter=self.make_getter(ruleset_id=99),
        )
        self.assertFalse(ok)
        self.assertTrue(any("ruleset id drift" in item for item in failures))

    def test_live_recheck_blocks_ruleset_contract_drift(self):
        data = self.make_pass_evidence()
        drifted = self.make_detail()
        drifted["enforcement"] = "evaluate"
        ok, failures = validator.live_recheck(
            data,
            getter=self.make_getter(detail=drifted),
        )
        self.assertFalse(ok)
        self.assertTrue(any("live contract drift" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
