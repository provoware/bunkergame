"""Ensure prerelease documentation includes every catalog element."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ElementCoverageTests(unittest.TestCase):
    def test_catalog_elements_are_documented(self):
        tree = ast.parse((ROOT / "Data/catalog.py").read_text(encoding="utf-8"))
        text = (ROOT / "Docs/VORRELEASE_SPIELELEMENTE.md").read_text(encoding="utf-8")
        for node in tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            name = getattr(node.targets[0], "id", "")
            if name == "A":
                abilities = ast.literal_eval(node.value)
                self.assertEqual(len(abilities), 20)
                for ability in abilities:
                    self.assertIn(ability[0], text)
            elif name == "TASK_SPECS":
                tasks = ast.literal_eval(node.value)
                self.assertEqual(len(tasks), 6)
                for task in tasks:
                    self.assertIn(task[0], text)
                    self.assertIn("TASK_" + task[0][4:], text)
            elif name == "CHARACTERS":
                for key in node.value.keys:
                    self.assertIn(key.value, text)


if __name__ == "__main__":
    unittest.main()
