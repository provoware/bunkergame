#!/usr/bin/env python3
"""Read-only GitHub P0 status verifier for BUNKER BEATS.

Uses the authenticated GitHub CLI but never changes repository state.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys

REPO = "provoware/bunkergame"
BRANCH = "main"
REQUIRED_CHECKS = ["static-and-contract", "repository-quality"]
HTTP_STATUS_RE = re.compile(r"(?:HTTP\s*)?(403|404|422)\b", re.IGNORECASE)


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def gh_json(endpoint: str) -> tuple[int, dict | list | None, str]:
    result = run(["gh", "api", endpoint])
    if result.returncode != 0:
        return result.returncode, None, result.stderr.strip()
    try:
        return 0, json.loads(result.stdout), ""
    except json.JSONDecodeError as exc:
        return 2, None, f"Ungültige GitHub-Antwort: {exc}"


def branch_protected_hint(data: dict) -> bool:
    return data.get("name") == BRANCH and data.get("protected") is True


def classify_read_error(error: str) -> str:
    text = error or ""
    match = HTTP_STATUS_RE.search(text)
    status = match.group(1) if match else None
    lower = text.lower()
    if status == "403" or "resource not accessible" in lower:
        return "DETAIL_READ_403"
    if status == "404" or "not found" in lower:
        return "DETAIL_READ_404"
    return "DETAIL_READ_ERROR"


def evaluate_protection(protection: dict) -> tuple[bool, set[str]]:
    checks = {
        c.get("context")
        for c in protection.get("required_status_checks", {}).get("checks", [])
        if isinstance(c, dict) and c.get("context")
    }
    checks.update(protection.get("required_status_checks", {}).get("contexts", []))
    strict = protection.get("required_status_checks", {}).get("strict", False)
    admins = protection.get("enforce_admins", {}).get("enabled", False)
    pr_gate = bool(protection.get("required_pull_request_reviews"))
    force = protection.get("allow_force_pushes", {}).get("enabled", False)
    delete = protection.get("allow_deletions", {}).get("enabled", False)

    ok = pr_gate and strict and admins and not force and not delete
    for required in REQUIRED_CHECKS:
        ok = ok and required in checks
    return ok, checks


def main() -> int:
    print("=== BUNKER BEATS P0 STATUS ===")
    if shutil.which("gh") is None:
        print("[BLOCKED] GitHub CLI (gh) fehlt.")
        return 3
    auth = run(["gh", "auth", "status"])
    if auth.returncode != 0:
        print("[BLOCKED] `gh` ist nicht angemeldet. Einmal `gh auth login` ausführen.")
        return 3

    branch_gate_ok = False

    code, branch, error = gh_json(f"repos/{REPO}/branches/{BRANCH}")
    if code != 0 or not isinstance(branch, dict):
        print(f"[BLOCKED] Branch-Metadaten nicht lesbar — {error}")
    elif not branch_protected_hint(branch):
        print(f"[FAIL] {BRANCH} Branch Gate — GitHub-Server meldet protected=false")
        print("  - Required Checks: noch nicht serverseitig beweisbar")
        print("  - Nächster Schritt: python3 Scripts/github_p0_admin.py --doctor")
    else:
        print(f"[PASS] GitHub-Server meldet {BRANCH}.protected=true")
        code, protection, error = gh_json(f"repos/{REPO}/branches/{BRANCH}/protection")
        if code != 0 or not isinstance(protection, dict):
            category = classify_read_error(error)
            print(f"[BLOCKED] Protection ist aktiv, Details aber nicht beweisbar — {category}")
            print(f"  - GitHub: {error}")
            print("  - Nächster Schritt: Anmeldung/Token-Rechte für Repository Administration prüfen")
        else:
            branch_gate_ok, checks = evaluate_protection(protection)
            print(f"[{'PASS' if branch_gate_ok else 'FAIL'}] main Branch Gate Detailprüfung")
            for required in REQUIRED_CHECKS:
                print(f"  - {required}: {'PASS' if required in checks else 'FAIL'}")

            strict = protection.get("required_status_checks", {}).get("strict", False)
            admins = protection.get("enforce_admins", {}).get("enabled", False)
            pr_gate = bool(protection.get("required_pull_request_reviews"))
            force = protection.get("allow_force_pushes", {}).get("enabled", False)
            delete = protection.get("allow_deletions", {}).get("enabled", False)
            print(f"  - Pull Request erforderlich: {'PASS' if pr_gate else 'FAIL'}")
            print(f"  - Branch aktuell vor Merge: {'PASS' if strict else 'FAIL'}")
            print(f"  - Admins geschützt: {'PASS' if admins else 'FAIL'}")
            print(f"  - Force-Push gesperrt: {'PASS' if not force else 'FAIL'}")
            print(f"  - Branch-Löschen gesperrt: {'PASS' if not delete else 'FAIL'}")

    runner_known = False
    runner_ready = False

    code, variables, error = gh_json(f"repos/{REPO}/actions/variables")
    if code != 0 or not isinstance(variables, dict):
        print(f"[WARN] Repository-Variablen nicht lesbar — {error}")
    else:
        runner_known = True
        values = {item.get('name'): item.get('value') for item in variables.get('variables', [])}
        enabled = values.get("UE58_RUNNER_ENABLED") == "true"
        print(f"[{'PASS' if enabled else 'WAIT'}] UE58_RUNNER_ENABLED={'true' if enabled else 'nicht true'}")

    code, runners, error = gh_json(f"repos/{REPO}/actions/runners")
    if code != 0 or not isinstance(runners, dict):
        print(f"[WARN] Runner-Liste nicht lesbar — {error}")
    else:
        runner_known = True
        matching = []
        for runner in runners.get("runners", []):
            labels = {label.get("name") for label in runner.get("labels", [])}
            if {"self-hosted", "unreal", "ue-5.8"}.issubset(labels):
                matching.append(runner)
        online = [r for r in matching if r.get("status") == "online"]
        runner_ready = bool(online)
        print(f"[{'PASS' if online else 'WAIT'}] UE-5.8 Runner: {len(online)} online / {len(matching)} passend")

    print("\nHinweis: Ein online Runner beweist noch kein CP1. Danach `Scripts/runner_readiness.py` und den echten CP1-Workflow ausführen.")
    print(f"GITHUB_P0_BRANCH_GATE: {'PASS' if branch_gate_ok else 'INCOMPLETE'}")
    if runner_known:
        print(f"GITHUB_P0_RUNNER_STATE: {'ONLINE' if runner_ready else 'WAIT'}")
    else:
        print("GITHUB_P0_RUNNER_STATE: UNKNOWN")
    print(f"GITHUB_P0_STATUS: {'PASS' if branch_gate_ok else 'INCOMPLETE'}")
    return 0 if branch_gate_ok else 2


if __name__ == "__main__":
    sys.exit(main())
