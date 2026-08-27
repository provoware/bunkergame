#!/usr/bin/env python3
"""Read-only GitHub P0 status verifier for BUNKER BEATS.

Uses the authenticated GitHub CLI but never changes repository state.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

REPO = "provoware/bunkergame"
BRANCH = "main"
REQUIRED_CHECKS = ["static-and-contract", "repository-quality"]


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


def main() -> int:
    print("=== BUNKER BEATS P0 STATUS ===")
    if shutil.which("gh") is None:
        print("[BLOCKED] GitHub CLI (gh) fehlt.")
        return 3
    auth = run(["gh", "auth", "status"])
    if auth.returncode != 0:
        print("[BLOCKED] `gh` ist nicht angemeldet. Einmal `gh auth login` ausführen.")
        return 3

    failures = 0

    code, protection, error = gh_json(f"repos/{REPO}/branches/{BRANCH}/protection")
    if code != 0 or not isinstance(protection, dict):
        print(f"[FAIL] Branch-Schutz: nicht aktiv/lesbar — {error}")
        failures += 1
    else:
        checks = {
            c.get("context")
            for c in protection.get("required_status_checks", {}).get("checks", [])
            if isinstance(c, dict)
        }
        checks.update(protection.get("required_status_checks", {}).get("contexts", []))
        strict = protection.get("required_status_checks", {}).get("strict", False)
        admins = protection.get("enforce_admins", {}).get("enabled", False)
        pr_gate = bool(protection.get("required_pull_request_reviews"))
        force = protection.get("allow_force_pushes", {}).get("enabled", False)
        delete = protection.get("allow_deletions", {}).get("enabled", False)

        branch_ok = pr_gate and strict and admins and not force and not delete
        for required in REQUIRED_CHECKS:
            branch_ok = branch_ok and required in checks
        print(f"[{'PASS' if branch_ok else 'FAIL'}] main Branch Gate")
        for required in REQUIRED_CHECKS:
            print(f"  - {required}: {'PASS' if required in checks else 'FAIL'}")
        if not branch_ok:
            failures += 1

    code, variables, error = gh_json(f"repos/{REPO}/actions/variables")
    if code != 0 or not isinstance(variables, dict):
        print(f"[WARN] Repository-Variablen nicht lesbar — {error}")
    else:
        values = {item.get('name'): item.get('value') for item in variables.get('variables', [])}
        enabled = values.get("UE58_RUNNER_ENABLED") == "true"
        print(f"[{'PASS' if enabled else 'WAIT'}] UE58_RUNNER_ENABLED={'true' if enabled else 'nicht true'}")

    code, runners, error = gh_json(f"repos/{REPO}/actions/runners")
    if code != 0 or not isinstance(runners, dict):
        print(f"[WARN] Runner-Liste nicht lesbar — {error}")
    else:
        matching = []
        for runner in runners.get("runners", []):
            labels = {label.get("name") for label in runner.get("labels", [])}
            if {"self-hosted", "unreal", "ue-5.8"}.issubset(labels):
                matching.append(runner)
        online = [r for r in matching if r.get("status") == "online"]
        print(f"[{'PASS' if online else 'WAIT'}] UE-5.8 Runner: {len(online)} online / {len(matching)} passend")

    print("\nHinweis: Ein online Runner beweist noch kein CP1. Danach `Scripts/runner_readiness.py` und den echten CP1-Workflow ausführen.")
    print(f"GITHUB_P0_STATUS: {'PASS' if failures == 0 else 'INCOMPLETE'}")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
