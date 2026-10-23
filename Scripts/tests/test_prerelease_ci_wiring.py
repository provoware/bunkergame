"""Regression guard: Validate must execute all prerelease contracts exactly once.

Static CI wiring evidence is not evidence of Unreal runtime success.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "Scripts/ci_verify.py"
VALIDATE = ROOT / ".github/workflows/validate.yml"
REQUIRED = (
    "Scripts/prerelease_gate.py",
    "Scripts/tests/test_prerelease_matrix.py",
    "Scripts/tests/test_prerelease_elements.py",
    "Scripts/tests/test_prerelease_ci_wiring.py",
    "Scripts/tests/test_runner_evidence_binding.py",
)


def extract_commands(source: str) -> list[str]:
    tree = ast.parse(source)
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "COMMANDS"
            for target in statement.targets
        ):
            scripts = []
            for command in statement.value.elts:
                if not isinstance(command, ast.List) or len(command.elts) != 2:
                    raise ValueError("unexpected CI command shape")
                arg = command.elts[1]
                if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
                    raise ValueError("CI command script must be a literal string")
                scripts.append(arg.value)
            return scripts
    raise ValueError("CI COMMANDS not found")


def assert_contracts(scripts: list[str]) -> None:
    for required in REQUIRED:
        if scripts.count(required) != 1:
            raise AssertionError(f"{required}: expected exactly one call")


class PrereleaseCIWiringTests(unittest.TestCase):
    def test_all_prerelease_contracts_run_exactly_once(self):
        scripts = extract_commands(VERIFY.read_text(encoding="utf-8"))
        assert_contracts(scripts)
        for required in REQUIRED:
            self.assertTrue((ROOT / required).is_file(), required)

    def test_missing_or_duplicate_contract_is_detectable(self):
        scripts = extract_commands(VERIFY.read_text(encoding="utf-8"))
        for required in REQUIRED:
            with self.subTest(required=required):
                missing = [script for script in scripts if script != required]
                duplicate = scripts + [required]
                with self.assertRaises(AssertionError):
                    assert_contracts(missing)
                with self.assertRaises(AssertionError):
                    assert_contracts(duplicate)

    def test_validate_workflow_invokes_ci_verify(self):
        content = VALIDATE.read_text(encoding="utf-8")
        self.assertIn("python3 Scripts/ci_verify.py", content)


if __name__ == "__main__":
    unittest.main()
