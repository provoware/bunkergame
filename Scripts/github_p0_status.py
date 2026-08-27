#!/usr/bin/env python3
"""Read-only GitHub P0 status verifier for BUNKER BEATS.

Ruleset-first: repository rulesets are independently readable with repository
read access. Classic Branch Protection remains a fallback path.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys

from github_p0_ruleset import (
    BRANCH,
    REPO,
    REQUIRED_CHECKS,
    RULESET_NAME,
    evaluate_ruleset,
    find_named_ruleset,
)

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


def evaluate_ruleset_live() -> tuple[bool, str]:
    code, items, error = gh_json(f"repos/{REPO}/rulesets")
    if code != 0 or not isinstance(items, list):
        return False, f"Ruleset-Liste nicht lesbar — {error}"

    matches = [item for item in items if isinstance(item, dict) and item.get("name") == RULESET_NAME]
    if len(matches) > 1:
        return False, "mehrere gleichnamige P0-Rulesets vorhanden"

    summary = find_named_ruleset(items)
    if not isinstance(summary, dict):
        return False, "P0-Ruleset nicht vorhanden"
    ruleset_id = summary.get("id")
    if not isinstance(ruleset_id, int):
        return False, "P0-Ruleset hat keine gültige ID"

    code, detail, error = gh_json(f"repos/{REPO}/rulesets/{ruleset_id}")
    if code != 0 or not isinstance(detail, dict):
        return False, f"P0-Ruleset-Detail nicht lesbar — {error}"

    ok, failures = evaluate_ruleset(detail)
    if ok:
        return True, f"Ruleset {ruleset_id} erfüllt den vollständigen P0-Vertrag"
    return False, "; ".join(failures)


def evaluate_classic_branch_protection() -> tuple[bool, str]:
    code, branch, error = gh_json(f"repos/{REPO}/branches/{BRANCH}")
    if code != 0 or not isinstance(branch, dict):
        return False, f"Branch-Metadaten nicht lesbar — {error}"
    if not branch_protected_hint(branch):
        return False, f"GitHub-Server meldet {BRANCH}.protected=false"

    code, protection, error = gh_json(f"repos/{REPO}/branches/{BRANCH}/protection")
    if code != 0 or not isinstance(protection, dict):
        category = classify_read_error(error)
        return False, f"Protection aktiv, Details nicht beweisbar — {category}: {error}"

    ok, checks = evaluate_protection(protection)
    if not ok:
        missing = [required for required in REQUIRED_CHECKS if required not in checks]
        return False, "Classic Protection unvollständig" + (f"; fehlend: {', '.join(missing)}" if missing else "")
    return True, "klassische Branch Protection erfüllt den P0-Vertrag"


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
    evidence_path = "NONE"

    ruleset_ok, ruleset_detail = evaluate_ruleset_live()
    if ruleset_ok:
        branch_gate_ok = True
        evidence_path = "RULESET"
        print(f"[PASS] P0 Ruleset — {ruleset_detail}")
    else:
        print(f"[WAIT] P0 Ruleset — {ruleset_detail}")
        classic_ok, classic_detail = evaluate_classic_branch_protection()
        if classic_ok:
            branch_gate_ok = True
            evidence_path = "CLASSIC_PROTECTION"
            print(f"[PASS] Classic Branch Protection — {classic_detail}")
        else:
            print(f"[FAIL] main Branch Gate — {classic_detail}")
            print("  - Nächster Schritt: python3 Scripts/github_p0_admin.py --doctor")
            print("  - Empfohlen danach: python3 Scripts/github_p0_admin.py --apply-ruleset")

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

    print("\nHinweis: Ruleset-/Branch-Gate-PASS beweist nur den GitHub-Schutz. Ein online Runner beweist noch kein CP1.")
    print(f"GITHUB_P0_EVIDENCE_PATH: {evidence_path}")
    print(f"GITHUB_P0_BRANCH_GATE: {'PASS' if branch_gate_ok else 'INCOMPLETE'}")
    if runner_known:
        print(f"GITHUB_P0_RUNNER_STATE: {'ONLINE' if runner_ready else 'WAIT'}")
    else:
        print("GITHUB_P0_RUNNER_STATE: UNKNOWN")
    print(f"GITHUB_P0_STATUS: {'PASS' if branch_gate_ok else 'INCOMPLETE'}")
    return 0 if branch_gate_ok else 2


if __name__ == "__main__":
    sys.exit(main())
