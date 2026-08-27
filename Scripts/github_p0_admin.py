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
from datetime import datetime, timezone
from pathlib import Path

REPO = "provoware/bunkergame"
BRANCH = "main"
REQUIRED_CHECKS = ["static-and-contract", "repository-quality"]
ROOT = Path(__file__).resolve().parents[1]
READINESS_REPORT = ROOT / "Diagnostics" / "Runtime" / "runner_readiness.json"
MAX_READINESS_AGE_SECONDS = 30 * 60


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

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"[FAIL] Ungültige GitHub-Antwort: {exc}")
        return False

    checks = {
        c.get("context")
        for c in data.get("required_status_checks", {}).get("checks", [])
        if isinstance(c, dict)
    }
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


def parse_utc(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return parsed.astimezone(timezone.utc)


def validate_fresh_readiness(report_path: Path = READINESS_REPORT) -> tuple[bool, str]:
    if not report_path.is_file():
        return False, f"Readiness-Evidence fehlt: {report_path}"
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"Readiness-Evidence ist ungültig: {exc}"

    if data.get("schema_version") != 2:
        return False, f"unerwartete Readiness-Schema-Version: {data.get('schema_version')}"
    if data.get("kind") != "UE58_RUNNER_READINESS":
        return False, "falscher Evidence-Typ"
    if data.get("status") != "PASS":
        return False, f"Readiness-Status ist {data.get('status')!r}, nicht PASS"
    if data.get("runtime_executed") is not False or data.get("cp1_pass") is not False:
        return False, "Readiness-Evidence vermischt unzulässig Runtime-/CP1-Status"

    checks = data.get("checks")
    if not isinstance(checks, dict) or not checks or not all(value is True for value in checks.values()):
        return False, "nicht alle Readiness-Checks sind PASS"
    if checks.get("engine_version_exact_5_8") is not True:
        return False, "UE-Version ist nicht exakt 5.8 bestätigt"

    stamp = data.get("generated_at_utc")
    if not isinstance(stamp, str):
        return False, "Freshness-Zeitstempel fehlt"
    try:
        generated = parse_utc(stamp)
    except (ValueError, TypeError) as exc:
        return False, f"Freshness-Zeitstempel ungültig: {exc}"

    age = (datetime.now(timezone.utc) - generated).total_seconds()
    if age < -300:
        return False, "Readiness-Evidence liegt unplausibel in der Zukunft"
    if age > MAX_READINESS_AGE_SECONDS:
        return False, f"Readiness-Evidence ist zu alt ({int(age)} s > {MAX_READINESS_AGE_SECONDS} s)"

    return True, f"frische Readiness-Evidence bestätigt ({int(max(age, 0))} s alt)"


def set_runner_variable() -> None:
    ready, detail = validate_fresh_readiness()
    if not ready:
        raise RuntimeError(
            "UE58_RUNNER_ENABLED bleibt gesperrt. " + detail +
            "\nZuerst auf der echten UE-Maschine `python3 Scripts/runner_readiness.py` erfolgreich ausführen."
        )
    print(f"[PASS] {detail}")
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
        help="UE58_RUNNER_ENABLED=true setzen; verlangt frische RUNNER_READINESS: PASS Evidence",
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
        if not ok:
            return 2
        if args.enable_runner_variable:
            set_runner_variable()
        return 0
    except RuntimeError as exc:
        print(f"[FAIL] {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
