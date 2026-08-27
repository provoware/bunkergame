from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_JSON = [p for p in ROOT.rglob("*.json") if "Diagnostics" not in p.parts]
PYTHON = [p for p in ROOT.rglob("*.py") if "Diagnostics" not in p.parts]
COMMANDS = [
    [sys.executable, "Tests/test_cp1_package_integrity.py"],
    [sys.executable, "Tests/Quality/test_cp1_runtime_contract.py"],
    [sys.executable, "Tests/Quality/validate_v7.py"],
    [sys.executable, "Tests/Quality/test_fault_spectrum.py"],
    [sys.executable, "Tests/Quality/test_solution_learning.py"],
    [sys.executable, "Tests/Quality/test_regression_learning.py"],
    [sys.executable, "Tests/test_toolchain_context.py"],
]


def main() -> int:
    failures: list[str] = []

    for path in PYTHON:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            failures.append(f"Python syntax: {path.relative_to(ROOT)}: {exc}")

    for path in TEXT_JSON:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"JSON: {path.relative_to(ROOT)}: {exc}")

    for command in COMMANDS:
        proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        name = " ".join(command[1:])
        print(f"\n=== {name} ===")
        print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, file=sys.stderr, end="")
        if proc.returncode != 0:
            failures.append(f"Command failed ({proc.returncode}): {name}")

    if failures:
        print("\nCI_VERIFY: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("\nCI_VERIFY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
