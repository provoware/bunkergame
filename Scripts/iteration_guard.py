#!/usr/bin/env python3
"""Enforce per-iteration documentation learning rules on pull requests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WICHTIG = "WICHTIG.md"
CODEQ = "CODEQUALITÄT.md"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=ROOT,
        check=check,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def read_at_revision(revision: str, path: str) -> str | None:
    result = git("show", f"{revision}:{path}", check=False)
    if result.returncode != 0:
        return None
    return result.stdout


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: iteration_guard.py <base-sha>")
        return 2

    base = sys.argv[1]
    errors: list[str] = []

    changed_result = git("diff", "--name-only", f"{base}...HEAD")
    changed = {line.strip() for line in changed_result.stdout.splitlines() if line.strip()}

    print(f"Base: {base}")
    print(f"Changed files: {len(changed)}")

    if not changed:
        errors.append("pull request has no changed files")

    if WICHTIG not in changed:
        errors.append("every iteration must update WICHTIG.md")

    if CODEQ not in changed:
        errors.append("every iteration must append one entry to CODEQUALITÄT.md")

    old_codeq = read_at_revision(base, CODEQ)
    new_path = ROOT / CODEQ
    if not new_path.is_file():
        errors.append("CODEQUALITÄT.md is missing from current revision")
    else:
        new_codeq = new_path.read_text(encoding="utf-8")
        if old_codeq is not None and not new_codeq.startswith(old_codeq):
            errors.append("CODEQUALITÄT.md is append-only: existing content was modified or removed")

        old_entries = 0 if old_codeq is None else old_codeq.count("\n## CQ-")
        new_entries = new_codeq.count("\n## CQ-")
        expected = old_entries + 1
        if new_entries != expected:
            errors.append(
                f"CODEQUALITÄT.md must add exactly one CQ entry per iteration: "
                f"old={old_entries}, new={new_entries}, expected={expected}"
            )

    wichtig_path = ROOT / WICHTIG
    if not wichtig_path.is_file():
        errors.append("WICHTIG.md is missing from current revision")
    else:
        current_focus_count = wichtig_path.read_text(encoding="utf-8").count("\n## W-")
        if current_focus_count != 1:
            errors.append(f"WICHTIG.md must contain exactly one current W entry, found {current_focus_count}")

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print(f"ITERATION_GUARD: FAIL ({len(errors)} issue(s))")
        return 1

    print("ITERATION_GUARD: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
