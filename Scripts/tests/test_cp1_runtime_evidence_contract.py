#!/usr/bin/env python3
"""Regression tests for the CP1 runtime evidence contract.

Synthetic fixtures test rejection/validation logic only. They are never runtime
proof and cannot create a production CP1 GREEN state.
"""

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

import cp1_runtime_evidence_contract as contract
import runner_identity


def load_collector():
    path = ROOT / "Launcher" / "runtime" / "cp1_runtime_evidence.py"
    spec = importlib.util.spec_from_file_location("cp1_runtime_evidence_test_module", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


collector = load_collector()


class CP1RuntimeEvidenceContractTests(unittest.TestCase):
    HEAD = "a" * 40
    OTHER_HEAD = "b" * 40
    MACHINE = "c" * 64
    OTHER_MACHINE = "d" * 64
    RUN_ID = "e" * 32

    def telemetry(self, **overrides) -> dict:
        data = {
            "schema": contract.TELEMETRY_SCHEMA,
            "run_id": self.RUN_ID,
            "frame_samples": 3,
            "frame_time_ms_avg": 16.666667,
            "frame_time_ms_min": 16.666667,
            "frame_time_ms_max": 16.666667,
            "wall_frame_time_ms_avg": 16.0,
            "position_before": [0.0, 0.0, 100.0],
            "position_after": [1.0, 0.0, 100.0],
            "velocity": [60.0, 0.0, 0.0],
            "speed_cm_s": 60.0,
            "displacement_cm": 1.0,
            "movement_component": {
                "valid": True,
                "active": True,
                "tick_enabled": True,
                "class": "CharacterMovementComponent",
                "movement_mode": "MOVE_Walking",
                "max_walk_speed": 600.0,
                "run_physics_without_controller": True,
            },
        }
        data.update(overrides)
        return data

    def raw(self, data: dict) -> bytes:
        return (json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")

    def evidence(self, *, now: datetime | None = None, telemetry: dict | None = None, **overrides) -> tuple[dict, dict, bytes]:
        timestamp = now or datetime.now(timezone.utc)
        telem = telemetry or self.telemetry()
        raw = self.raw(telem)
        data = {
            "schema_version": contract.SCHEMA_VERSION,
            "kind": contract.KIND,
            "started_at_utc": (timestamp - timedelta(minutes=2)).isoformat().replace("+00:00", "Z"),
            "finished_at_utc": timestamp.isoformat().replace("+00:00", "Z"),
            "runtime_executed": True,
            "cp1_pass": True,
            "status": "GREEN",
            "code": "CP1-CHARACTER-MOVEMENT-OK",
            "run_id": self.RUN_ID,
            "repository": runner_identity.EXPECTED_REPOSITORY,
            "git_head_sha": self.HEAD,
            "machine_fingerprint_sha256": self.MACHINE,
            "machine_identity_scheme": runner_identity.MACHINE_IDENTITY_SCHEME,
            "ue": {
                "version": "5.8",
                "version_raw": {"MajorVersion": 5, "MinorVersion": 8},
            },
            "steps": [
                {"step": "build", "status": "GREEN", "evidence": {"returncode": 0}},
                {
                    "step": "cp1_character_movement",
                    "status": "GREEN",
                    "evidence": {"returncode": 0},
                    "run_id": self.RUN_ID,
                },
            ],
            "telemetry": telem,
            "telemetry_path": contract.TELEMETRY_RELATIVE_PATH,
            "telemetry_sha256": contract.telemetry_digest(raw),
            "telemetry_error": None,
        }
        data.update(overrides)
        data = contract.seal_runtime_evidence(data)
        return data, telem, raw

    def validate(self, data: dict, telemetry: dict, raw: bytes, *, now: datetime | None = None, head: str | None = None, machine: str | None = None, repository: str | None = None):
        return contract.validate_runtime_evidence(
            data,
            expected_repository=repository or runner_identity.EXPECTED_REPOSITORY,
            expected_head=head or self.HEAD,
            expected_machine_fingerprint=machine or self.MACHINE,
            telemetry_data=telemetry,
            telemetry_raw=raw,
            now=now,
        )

    def test_canonical_green_runtime_evidence_passes(self):
        now = datetime(2026, 8, 27, 18, 0, tzinfo=timezone.utc)
        data, telemetry, raw = self.evidence(now=now)
        ok, failures = self.validate(data, telemetry, raw, now=now + timedelta(minutes=1))
        self.assertTrue(ok, failures)
        self.assertEqual(failures, [])

    def test_schema_v2_is_blocked(self):
        data, telemetry, raw = self.evidence(schema_version=2)
        data = contract.seal_runtime_evidence(data)
        ok, failures = self.validate(data, telemetry, raw)
        self.assertFalse(ok)
        self.assertTrue(any("schema_version" in item for item in failures))

    def test_runtime_and_cp1_flags_must_be_exact_true(self):
        data, telemetry, raw = self.evidence(runtime_executed=False, cp1_pass=False)
        data = contract.seal_runtime_evidence(data)
        ok, failures = self.validate(data, telemetry, raw)
        self.assertFalse(ok)
        self.assertTrue(any("runtime_executed" in item for item in failures))
        self.assertTrue(any("cp1_pass" in item for item in failures))

    def test_other_checkout_head_is_blocked(self):
        data, telemetry, raw = self.evidence()
        ok, failures = self.validate(data, telemetry, raw, head=self.OTHER_HEAD)
        self.assertFalse(ok)
        self.assertTrue(any("HEAD drift" in item for item in failures))

    def test_other_machine_is_blocked(self):
        data, telemetry, raw = self.evidence()
        ok, failures = self.validate(data, telemetry, raw, machine=self.OTHER_MACHINE)
        self.assertFalse(ok)
        self.assertTrue(any("different machine" in item for item in failures))

    def test_wrong_repository_is_blocked(self):
        data, telemetry, raw = self.evidence()
        ok, failures = self.validate(data, telemetry, raw, repository="someone/else")
        self.assertFalse(ok)
        self.assertTrue(any("current checkout" in item for item in failures))

    def test_stale_and_future_runtime_evidence_are_blocked(self):
        observed = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)
        data, telemetry, raw = self.evidence(now=observed)
        ok, failures = self.validate(data, telemetry, raw, now=observed + timedelta(hours=1))
        self.assertFalse(ok)
        self.assertTrue(any("stale" in item for item in failures))

        future = datetime(2026, 8, 27, 14, 20, tzinfo=timezone.utc)
        data, telemetry, raw = self.evidence(now=future)
        ok, failures = self.validate(data, telemetry, raw, now=future - timedelta(minutes=10))
        self.assertFalse(ok)
        self.assertTrue(any("future" in item for item in failures))

    def test_step_set_sequence_and_returncode_are_fail_closed(self):
        data, telemetry, raw = self.evidence()
        data["steps"] = [data["steps"][0], data["steps"][0], data["steps"][1]]
        data = contract.seal_runtime_evidence(data)
        ok, failures = self.validate(data, telemetry, raw)
        self.assertFalse(ok)
        self.assertTrue(any("sequence" in item or "duplicates" in item for item in failures))

        data, telemetry, raw = self.evidence()
        data["steps"][0]["evidence"]["returncode"] = False
        data = contract.seal_runtime_evidence(data)
        ok, failures = self.validate(data, telemetry, raw)
        self.assertFalse(ok)
        self.assertTrue(any("returncode" in item for item in failures))

    def test_telemetry_schema_and_run_id_are_bound(self):
        bad = self.telemetry(schema="bunkerbeats.cp1.movement.telemetry.v2")
        data, _, raw = self.evidence(telemetry=bad)
        ok, failures = self.validate(data, bad, raw)
        self.assertFalse(ok)
        self.assertTrue(any("telemetry schema" in item for item in failures))

        bad = self.telemetry(run_id="f" * 32)
        data, _, raw = self.evidence(telemetry=bad)
        ok, failures = self.validate(data, bad, raw)
        self.assertFalse(ok)
        self.assertTrue(any("run_id mismatch" in item for item in failures))

    def test_boolean_numeric_telemetry_is_blocked(self):
        bad = self.telemetry(frame_samples=True)
        data, _, raw = self.evidence(telemetry=bad)
        ok, failures = self.validate(data, bad, raw)
        self.assertFalse(ok)
        self.assertTrue(any("frame_samples" in item for item in failures))

    def test_telemetry_digest_and_embedded_content_must_match_actual_file(self):
        data, telemetry, raw = self.evidence()
        altered_raw = self.raw(dict(telemetry, speed_cm_s=61.0))
        ok, failures = self.validate(data, telemetry, altered_raw)
        self.assertFalse(ok)
        self.assertTrue(any("digest mismatch" in item for item in failures))

        actual = dict(telemetry, speed_cm_s=61.0)
        actual_raw = self.raw(actual)
        data["telemetry_sha256"] = contract.telemetry_digest(actual_raw)
        data = contract.seal_runtime_evidence(data)
        ok, failures = self.validate(data, actual, actual_raw)
        self.assertFalse(ok)
        self.assertTrue(any("embedded telemetry differs" in item for item in failures))

    def test_evidence_tampering_breaks_integrity(self):
        data, telemetry, raw = self.evidence()
        data["code"] = "MANUALLY-EDITED"
        ok, failures = self.validate(data, telemetry, raw)
        self.assertFalse(ok)
        self.assertTrue(any("integrity mismatch" in item for item in failures))

    def test_displacement_must_match_positions(self):
        bad = self.telemetry(displacement_cm=20.0)
        data, _, raw = self.evidence(telemetry=bad)
        ok, failures = self.validate(data, bad, raw)
        self.assertFalse(ok)
        self.assertTrue(any("inconsistent with positions" in item for item in failures))


class RuntimeCollectorSafetyTests(unittest.TestCase):
    def test_stale_runtime_artifacts_are_purged_before_new_run(self):
        original_output = collector.OUTPUT
        original_telemetry = collector.TELEMETRY
        original_report_dir = collector.AUTOMATION_REPORT_DIR
        try:
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                collector.OUTPUT = root / "Diagnostics" / "Runtime" / "CP1_runtime_evidence.json"
                collector.TELEMETRY = root / "Saved" / "Automation" / "CP1_RuntimeTelemetry.json"
                collector.AUTOMATION_REPORT_DIR = root / "Diagnostics" / "Runtime" / "CP1"
                collector.OUTPUT.parent.mkdir(parents=True)
                collector.TELEMETRY.parent.mkdir(parents=True)
                collector.AUTOMATION_REPORT_DIR.mkdir(parents=True)
                collector.OUTPUT.write_text('{"status":"GREEN"}\n', encoding="utf-8")
                collector.TELEMETRY.write_text('{"schema":"old"}\n', encoding="utf-8")
                (collector.AUTOMATION_REPORT_DIR / "old.txt").write_text("old", encoding="utf-8")

                ok, failures = collector.purge_stale_runtime_artifacts()
                self.assertTrue(ok, failures)
                self.assertFalse(collector.OUTPUT.exists())
                self.assertFalse(collector.TELEMETRY.exists())
                self.assertFalse(collector.AUTOMATION_REPORT_DIR.exists())
        finally:
            collector.OUTPUT = original_output
            collector.TELEMETRY = original_telemetry
            collector.AUTOMATION_REPORT_DIR = original_report_dir

    def test_cpp_and_collector_share_run_id_and_v3_telemetry_contract(self):
        cpp = (ROOT / "Source" / "BunkerBeats" / "Private" / "Tests" / "BunkerBeatsCP1MovementSmokeTest.cpp").read_text(encoding="utf-8")
        py = (ROOT / "Launcher" / "runtime" / "cp1_runtime_evidence.py").read_text(encoding="utf-8")
        self.assertIn("CP1EvidenceRunId=", cpp)
        self.assertIn("bunkerbeats.cp1.movement.telemetry.v3", cpp)
        self.assertIn("\\\"run_id\\\"", cpp)
        self.assertIn("-CP1EvidenceRunId={run_id}", py)


if __name__ == "__main__":
    unittest.main()
