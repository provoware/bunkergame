#!/usr/bin/env python3
"""Safely configure the BUNKER BEATS P0 GitHub branch gate via GitHub CLI.

Default mode is DRY-RUN. Nothing is changed unless --apply is supplied.
Requires an authenticated `gh` CLI session with repository administration rights.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

REPO = "provoware/bunkergame"
BRANCH = "main"
REQUIRED_CHECKS = ["static-and-contract", "repository-quality"]


def run(args: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def require_gh() -> None:
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI (gh) fehlt. Installation: https://cli.github.com/")
    auth = run(["gh", "auth", "status"], check=False)
    if auth.returncode != 0:
        raise RuntimeError("GitHub CLI ist nicht angemeldet. Einmal `gh auth login` ausführen.")


def protection_payload() -> dict:
    return {
        "required_status_checks": {
            "strict": True,
            "contexts": REQUIRED_CHECKS,
        },
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 0,
            "require_last_push_approval": False,
        },
        "restrictions": None,
        "required_linear_history": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "block_creations": False,
        "required_conversation_resolution": True,
        "lock_branch": False,
        "allow_fork_syncing": True,
    }


def show_plan() -> None:
    print("=== BUNKER BEATS GITHUB P0 ADMIN ===")
    print(f"Repository: {REPO}")
    print(f"Branch:     {BRANCH}")
    print("Modus:      DRY-RUN")
    print("\nGeplante Schutzregeln:")
    print("- Pull Request vor Integration")
    print("- Branch muss vor Merge aktuell sein")
    print("- Required Check: static-and-contract")
    print("- Required Check: repository-quality")
    print("- Admins unterliegen dem Schutz")
    print("- veraltete Reviews werden verworfen")
    print("- offene Review-Diskussionen blockieren")
    print("- Force-Push gesperrt")
    print("- Branch-Löschen gesperrt")
    print("\nNicht global required: cp1-runtime")
    print("Grund: Der UE-5.8-Self-hosted-Runner ist noch nicht dauerhaft verfügbar.")


def apply_protection() -> None:
    payload = json.dumps(protection_payload())
    result = run(
        [
            "gh",
            "api",
            "--method",
            "PUT",
            f"repos/{REPO}/branches/{BRANCH}/protection",
            "--input",
            "-",
        ],
        input_text=payload,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Branch-Schutz konnte nicht gesetzt werden:\n{result.stderr.strip()}")
    print("[PASS] Branch-Schutz wurde von GitHub angenommen.")


def verify() -> bool:
    result = run(
        ["gh", "api", f"repos/{REPO}/branches/{BRANCH}/protection"],
        check=False,
    )
    if result.returncode != 0:
        print("[FAIL] Branch-Schutz konnte nicht gelesen werden.")
        print(result.stderr.strip())
        return False

    data = json.loads(result.stdout)
    checks = {
        c.get("context")
        for c in data.get("required_status_checks", {}).get("checks", [])
        if isinstance(c, dict)
    }
    # GitHub may expose legacy contexts separately.
    checks.update(data.get("required_status_checks", {}).get("contexts", []))

    missing = [name for name in REQUIRED_CHECKS if name not in checks]
    force = data.get("allow_force_pushes", {}).get("enabled", False)
    delete = data.get("allow_deletions", {}).get("enabled", False)
    admins = data.get("enforce_admins", {}).get("enabled", False)
    pr_gate = bool(data.get("required_pull_request_reviews"))
    strict = data.get("required_status_checks", {}).get("strict", False)

    print("\n=== NACHPRÜFUNG ===")
    print(f"Pull-Request-Gate:       {'PASS' if pr_gate else 'FAIL'}")
    print(f"Required Checks aktuell: {'PASS' if strict else 'FAIL'}")
    print(f"Admins geschützt:        {'PASS' if admins else 'FAIL'}")
    print(f"Force-Push gesperrt:     {'PASS' if not force else 'FAIL'}")
    print(f"Branch-Löschen gesperrt: {'PASS' if not delete else 'FAIL'}")
    for name in REQUIRED_CHECKS:
        print(f"Check {name}: {'PASS' if name in checks else 'FAIL'}")

    ok = pr_gate and strict and admins and not force and not delete and not missing
    print(f"\nGITHUB_P0_BRANCH_GATE: {'PASS' if ok else 'FAIL'}")
    return ok


def set_runner_variable() -> None:
    result = run(
        [
            "gh",
            "variable",
            "set",
            "UE58_RUNNER_ENABLED",
            "--repo",
            REPO,
            "--body",
            "true",
        ],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Repository-Variable konnte nicht gesetzt werden:\n{result.stderr.strip()}")
    print("[PASS] UE58_RUNNER_ENABLED=true gesetzt.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Branch-Schutz wirklich setzen")
    parser.add_argument(
        "--enable-runner-variable",
        action="store_true",
        help="UE58_RUNNER_ENABLED=true setzen; erst NACH realem RUNNER_READINESS: PASS verwenden",
    )
    args = parser.parse_args()

    show_plan()
    try:
        require_gh()
    except RuntimeError as exc:
        print(f"\n[BLOCKED] {exc}")
        return 3

    if not args.apply:
        print("\nKeine Änderung durchgeführt. Zum Anwenden: python3 Scripts/github_p0_admin.py --apply")
        return 0

    try:
        apply_protection()
        ok = verify()
        if args.enable_runner_variable:
            print("\n[WARN] Die Runner-Variable darf erst nach einem echten RUNNER_READINESS: PASS aktiviert werden.")
            set_runner_variable()
        return 0 if ok else 2
    except RuntimeError as exc:
        print(f"[FAIL] {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
