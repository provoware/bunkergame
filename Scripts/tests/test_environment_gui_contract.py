from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "Launcher" / "core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import assistant
from environment_contract import (
    SUMMARY_SCHEMA_VERSION,
    normalize_result_payload,
    serialize_findings,
)


class EnvironmentPayloadContractTests(unittest.TestCase):
    def test_current_after_phase_is_preferred(self):
        payload = {
            "summary": {
                "schema_version": SUMMARY_SCHEMA_VERSION,
                "overall": "YELLOW",
                "before": [
                    {"id": "UNREAL", "status": "YELLOW", "message": "vorher", "detail": {}}
                ],
                "after": [
                    {"id": "UNREAL", "status": "YELLOW", "message": "nachher", "detail": {}}
                ],
            }
        }
        view = normalize_result_payload(payload)
        self.assertEqual(view["phase"], "after")
        self.assertEqual(view["rows"][0]["message"], "nachher")
        self.assertEqual(view["label"], "🟡 TEILWEISE / BLOCKIERT")

    def test_legacy_tuple_after_is_accepted(self):
        payload = {
            "summary": {
                "overall": "GREEN",
                "after": [("PROJECT", "GREEN", "Projektdatei gefunden.", {"path": "/tmp/x"})],
            }
        }
        view = normalize_result_payload(payload)
        self.assertEqual(view["phase"], "after")
        self.assertEqual(view["rows"][0]["id"], "PROJECT")

    def test_missing_after_falls_back_to_before_without_exception(self):
        payload = {
            "summary": {
                "overall": "YELLOW",
                "before": [("UNREAL", "YELLOW", "Unreal fehlt.", {"available": False})],
            }
        }
        view = normalize_result_payload(payload)
        self.assertEqual(view["phase"], "before")
        self.assertEqual(view["rows"][0]["id"], "UNREAL")

    def test_missing_before_and_after_falls_back_to_issues(self):
        payload = {
            "summary": {
                "overall": "YELLOW",
                "issues": [
                    {
                        "code": "ENV-UNREAL-001",
                        "title": "UNREAL",
                        "status": "YELLOW",
                        "message": "Unreal fehlt.",
                    }
                ],
            }
        }
        view = normalize_result_payload(payload)
        self.assertEqual(view["phase"], "issues")
        self.assertTrue(view["warnings"])

    def test_missing_summary_is_fail_safe_red(self):
        view = normalize_result_payload({"run_id": "x"})
        self.assertEqual(view["overall"], "RED")
        self.assertEqual(view["phase"], "none")
        self.assertTrue(view["warnings"])

    def test_malformed_after_row_is_skipped_instead_of_crashing(self):
        payload = {
            "summary": {
                "overall": "RED",
                "after": [None, {"id": "PROJECT", "status": "RED", "message": "Fehlt", "detail": {}}],
            }
        }
        view = normalize_result_payload(payload)
        self.assertEqual(len(view["rows"]), 1)
        self.assertIn("übersprungen", " ".join(view["warnings"]))

    def test_invalid_overall_is_derived_from_rows(self):
        payload = {
            "summary": {
                "overall": "UNKNOWN",
                "after": [("UNREAL", "YELLOW", "Unreal fehlt.", {})],
            }
        }
        view = normalize_result_payload(payload)
        self.assertEqual(view["overall"], "YELLOW")

    def test_serialize_findings_rejects_invalid_rows(self):
        with self.assertRaises(ValueError):
            serialize_findings([("PROJECT", "BROKEN", "bad", {})])


class EnvironmentAssistantContractTests(unittest.TestCase):
    class FakeLogger:
        run_id = "run-contract-test"

        def __init__(self):
            self.events = []

        def emit(self, *args, **kwargs):
            self.events.append((args, kwargs))

        def report(self, summary):
            self.summary = summary
            return Path("Diagnostics/Launcher/fake.json")

    class FakeRepairAction:
        def __init__(self):
            self.repair_id = "REPAIR-UE-001"
            self.title = "Unreal Engine 5.8 bereitstellen"
            self.status = "BLOCKED"
            self.safe = False
            self.automatic = False
            self.explanation = "Manuelle Installation erforderlich."
            self.changed_paths = []

    class FakeEngine:
        def __init__(self):
            self.scan_count = 0

        def scan(self):
            self.scan_count += 1
            if self.scan_count == 1:
                return [
                    ("PROJECT", "GREEN", "Projektdatei gefunden.", {"path": "project"}),
                    ("UNREAL", "YELLOW", "Unreal fehlt.", {"available": False}),
                ]
            return [
                ("PROJECT", "GREEN", "Projektdatei gefunden.", {"path": "project"}),
                ("UNREAL", "YELLOW", "Unreal fehlt weiterhin.", {"available": False}),
            ]

        def safe_repair(self, finding):
            return EnvironmentAssistantContractTests.FakeRepairAction()

    def setUp(self):
        self.old_record = assistant.regression_knowledge.record
        self.old_derive = assistant.regression_knowledge.derive
        assistant.regression_knowledge.record = lambda *args, **kwargs: None
        assistant.regression_knowledge.derive = lambda *args, **kwargs: None

    def tearDown(self):
        assistant.regression_knowledge.record = self.old_record
        assistant.regression_knowledge.derive = self.old_derive

    def test_assistant_always_returns_explicit_pre_and_post_validation(self):
        instance = assistant.EnvironmentAssistant.__new__(assistant.EnvironmentAssistant)
        instance.logger = self.FakeLogger()
        instance.engine = self.FakeEngine()

        result = instance.run(repair=False)
        summary = result["summary"]

        self.assertEqual(summary["schema_version"], SUMMARY_SCHEMA_VERSION)
        self.assertEqual(len(summary["before"]), 2)
        self.assertEqual(len(summary["after"]), 2)
        self.assertEqual(summary["after"][1]["message"], "Unreal fehlt weiterhin.")
        self.assertEqual(summary["overall"], "YELLOW")
        self.assertEqual(instance.engine.scan_count, 2)

    def test_repair_run_records_actions_and_revalidates(self):
        instance = assistant.EnvironmentAssistant.__new__(assistant.EnvironmentAssistant)
        instance.logger = self.FakeLogger()
        instance.engine = self.FakeEngine()

        result = instance.run(repair=True)
        summary = result["summary"]

        self.assertTrue(summary["repair_requested"])
        self.assertEqual(len(summary["repairs"]), 1)
        self.assertEqual(summary["repairs"][0]["status"], "BLOCKED")
        self.assertEqual(instance.engine.scan_count, 2)


if __name__ == "__main__":
    unittest.main()
