"""Regression tests for the prerelease inventory and catalog."""
import ast
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts"))
import prerelease_gate as gate


class MatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(gate.MATRIX.read_text(encoding="utf-8"))

    def test_matrix_is_valid(self):
        self.assertEqual(gate.validate(self.matrix), [])
        self.assertGreaterEqual(len(self.matrix["requirements"]), 40)

    def test_catalog_is_covered(self):
        tree = ast.parse((ROOT / "Data/catalog.py").read_text(encoding="utf-8"))
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and target.id in {"A", "TASK_SPECS", "CHARACTERS"}:
                    values[target.id] = (
                        [key.value for key in node.value.keys]
                        if target.id == "CHARACTERS" else ast.literal_eval(node.value)
                    )
        self.assertEqual(len(values["A"]), 20)
        self.assertEqual(len(values["TASK_SPECS"]), 6)
        self.assertEqual(set(values["CHARACTERS"]), {"Pppoppi", "Atze"})
        ids = {r["id"] for r in self.matrix["requirements"]}
        self.assertTrue({"ABILITIES_ALL", "INTERACTIONS_ALL", "TASKS_ALL", "CHARACTERS_BOTH"} <= ids)

    def test_missing_requirement_rejected(self):
        data = copy.deepcopy(self.matrix)
        data["requirements"] = [r for r in data["requirements"] if r["id"] != "SAVE_ATOMIC"]
        self.assertTrue(any("SAVE_ATOMIC" in e for e in gate.validate(data)))

    def test_duplicate_requirement_rejected(self):
        data = copy.deepcopy(self.matrix)
        data["requirements"].append(copy.deepcopy(data["requirements"][0]))
        self.assertTrue(any("duplicate id" in e for e in gate.validate(data)))

    def test_unproven_pass_rejected(self):
        data = copy.deepcopy(self.matrix)
        data["requirements"][0]["status"] = "PASS"
        self.assertTrue(any("PASS requires" in e for e in gate.validate(data)))

    def test_unknown_status_rejected(self):
        data = copy.deepcopy(self.matrix)
        data["requirements"][0]["status"] = "GREEN"
        self.assertTrue(any("invalid area or status" in e for e in gate.validate(data)))

    def test_release_is_blocked(self):
        blockers = gate.release_blockers(self.matrix)
        self.assertIn("user_release_approved", blockers)
        self.assertIn("candidate_frozen", blockers)


if __name__ == "__main__":
    unittest.main()
