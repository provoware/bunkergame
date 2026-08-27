from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def step(name: str, command: list[str], accepted: set[int] = {0}) -> int:
    print(f"\n=== {name} ===")
    proc = subprocess.run(command, cwd=ROOT)
    if proc.returncode not in accepted:
        print(f"{name}: FAIL/BLOCKED (exit={proc.returncode})")
    return proc.returncode


def main() -> int:
    if step("Repository preflight", [sys.executable, "Scripts/ci_verify.py"]) != 0:
        return 2
    runtime_rc = step(
        "UE 5.8 Build + CP1 Character Spawn + Movement + Evidence",
        [sys.executable, "Launcher/runtime/cp1_runtime_evidence.py"],
        {0, 3},
    )
    if runtime_rc == 3:
        print("CP1: BLOCKED - UE 5.8 was not available/discoverable.")
        return 3
    if runtime_rc != 0:
        return 2
    return step("CP1 runtime gate", [sys.executable, "Scripts/cp1_gate_runtime.py"])


if __name__ == "__main__":
    raise SystemExit(main())
