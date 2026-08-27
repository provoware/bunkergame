#!/usr/bin/env python3
"""Detect accidental continued development on a branch whose PR was already merged.

Read-only. Uses git locally and GitHub CLI only for PR metadata.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "provoware/bunkergame"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def current_branch() -> str | None:
    env_branch = os.environ.get("GITHUB_HEAD_REF")
    if env_branch:
        return env_branch
    result = run(["git", "branch", "--show-current"])
    branch = result.stdout.strip()
    return branch or None


def parse_merged_prs(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def branch_reused_after_merge(branch: str, merged_prs: list[dict], commits_ahead: int) -> bool:
    if branch == "main":
        return False
    return bool(merged_prs) and commits_ahead > 0


def commits_ahead_of_main() -> tuple[int | None, str]:
    result = run(["git", "rev-list", "--count", "origin/main..HEAD"])
    if result.returncode != 0:
        return None, result.stderr.strip()
    try:
        return int(result.stdout.strip()), ""
    except ValueError:
        return None, "git rev-list returned no integer"


def main() -> int:
    print("=== BUNKER BEATS BRANCH LIFECYCLE GUARD ===")
    branch = current_branch()
    if not branch:
        print("[BLOCKED] Aktueller Branch konnte nicht eindeutig bestimmt werden.")
        return 3
    print(f"Branch: {branch}")

    if branch == "main":
        print("[PASS] main ist kein Feature-Branch-Reuse-Fall.")
        print("BRANCH_LIFECYCLE: PASS")
        return 0

    if shutil.which("gh") is None:
        print("[BLOCKED] GitHub CLI (gh) fehlt; Merge-Historie kann nicht geprüft werden.")
        return 3

    auth = run(["gh", "auth", "status"])
    if auth.returncode != 0:
        print("[BLOCKED] gh ist nicht angemeldet. `gh auth login` ausführen.")
        return 3

    prs = run([
        "gh", "pr", "list", "--repo", REPO, "--head", branch,
        "--state", "merged", "--json", "number,mergedAt,url",
    ])
    if prs.returncode != 0:
        print(f"[BLOCKED] PR-Historie nicht lesbar: {prs.stderr.strip()}")
        return 3

    merged = parse_merged_prs(prs.stdout)
    ahead, error = commits_ahead_of_main()
    if ahead is None:
        print(f"[BLOCKED] Abstand zu origin/main nicht bestimmbar: {error}")
        return 3

    print(f"Gemergte PRs mit diesem Branch: {len(merged)}")
    print(f"Commits vor origin/main: {ahead}")

    if branch_reused_after_merge(branch, merged, ahead):
        number = merged[0].get("number", "?")
        print(f"[FAIL] Branch wurde nach Merge von PR #{number} weiterverwendet.")
        print("NÄCHSTER SCHRITT: neuen Branch vom aktuellen main erstellen und dort fortsetzen.")
        print("BRANCH_LIFECYCLE: FAIL")
        return 2

    print("[PASS] Kein Weiterentwickeln auf einem bereits gemergten Feature-Branch erkannt.")
    print("BRANCH_LIFECYCLE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
