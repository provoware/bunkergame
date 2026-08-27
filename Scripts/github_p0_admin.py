#!/usr/bin/env python3
"""Safely configure the BUNKER BEATS P0 GitHub gate via GitHub CLI.

Default mode is DRY-RUN. Nothing is changed unless --apply or
--apply-ruleset is supplied. Ruleset mode is preferred because its complete
server configuration remains independently readable with repository read access.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from github_p0_ruleset import (
    BRANCH,
    REPO,
    REQUIRED_CHECKS,
    RULESET_NAME,
    evaluate_ruleset,
    find_named_ruleset,
    ruleset_payload,
)
from runner_identity import (
    EXPECTED_REPOSITORY,
    current_git_head,
    current_repository_identity,
    git_worktree_clean,
    machine_fingerprint,
)
from runner_readiness_contract import validate_readiness_report

ROOT = Path(__file__).resolve().parents[1]
READINESS_REPORT = ROOT / "Diagnostics" / "Runtime" / "runner_readiness.json"
HTTP_STATUS_RE = re.compile(r"(?:HTTP\s*)?(403|404|422)\b", re.IGNORECASE)


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


def parse_json_output(text: str, label: str) -> dict:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label}: ungültige GitHub-Antwort: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{label}: unerwarteter Antworttyp")
    return data


def parse_json_list(text: str, label: str) -> list:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label}: ungültige GitHub-Antwort: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError(f"{label}: unerwarteter Antworttyp")
    return data


def repo_admin_capability(data: dict) -> tuple[bool, str]:
    if data.get("full_name") != REPO:
        return False, f"falsches Repository in GitHub-Antwort: {data.get('full_name')!r}"
    if data.get("archived") is True:
        return False, "Repository ist archiviert"
    permissions = data.get("permissions")
    if not isinstance(permissions, dict):
        return False, "Repository-Rechte konnten nicht bestimmt werden"
    if permissions.get("admin") is True:
        return True, "Repository-Adminrecht bestätigt"
    if permissions.get("maintain") is True:
        return False, "nur Maintain-Recht erkannt; Branch-Administration benötigt Admin"
    if permissions.get("push") is True:
        return False, "Schreibrecht erkannt, aber kein Repository-Adminrecht"
    return False, "kein Repository-Adminrecht erkannt"


def classify_gh_error(stderr: str) -> tuple[str, str, str]:
    text = (stderr or "").strip()
    lower = text.lower()
    match = HTTP_STATUS_RE.search(text)
    status = match.group(1) if match else None

    if status == "403" or "resource not accessible" in lower or "forbidden" in lower:
        return (
            "AUTHORIZATION_403",
            "GitHub verweigert die Administrationsaktion.",
            "Mit einem Repository-Admin-Konto anmelden. Bei Fine-grained Tokens muss Repository Administration auf Read and write stehen.",
        )
    if status == "404" or "not found" in lower:
        return (
            "RESOURCE_404",
            "Repository, Branch oder Ruleset/Protection-Ressource wurde nicht gefunden bzw. ist für diesen Token nicht sichtbar.",
            f"`gh repo view {REPO}` und `gh api repos/{REPO}/branches/{BRANCH}` prüfen; danach Anmeldung/Berechtigungen kontrollieren.",
        )
    if status == "422" or "validation failed" in lower:
        return (
            "VALIDATION_422",
            "GitHub hat die Schutzkonfiguration als ungültig abgelehnt.",
            "Fehlertext auf ungültige Required-Checks oder nicht unterstützte Ruleset-/Protection-Felder prüfen; nichts erzwingen oder abschwächen.",
        )
    return (
        "UNKNOWN_GITHUB_ERROR",
        "GitHub-Aktion ist fehlgeschlagen.",
        "Die unveränderte GitHub-Fehlermeldung prüfen und erst danach erneut anwenden.",
    )


def describe_failure(action: str, stderr: str) -> str:
    code, meaning, next_step = classify_gh_error(stderr)
    raw = (stderr or "").strip() or "keine zusätzliche GitHub-Fehlermeldung"
    return (
        f"{action} fehlgeschlagen.\n"
        f"Diagnose: {code}\n"
        f"Bedeutung: {meaning}\n"
        f"Nächster Schritt: {next_step}\n"
        f"GitHub-Meldung: {raw}"
    )


def list_rulesets() -> list:
    result = run(["gh", "api", f"repos/{REPO}/rulesets"], check=False)
    if result.returncode != 0:
        raise RuntimeError(describe_failure("Rulesets lesen", result.stderr))
    return parse_json_list(result.stdout, "Rulesets lesen")


def admin_preflight() -> bool:
    print("\n=== ADMIN-FÄHIGKEITS-PRÜFUNG ===")

    repo_result = run(["gh", "api", f"repos/{REPO}"], check=False)
    if repo_result.returncode != 0:
        print("[BLOCKED] Repository-Metadaten nicht lesbar.")
        print(describe_failure("Repository-Prüfung", repo_result.stderr))
        print("GITHUB_ADMIN_PREFLIGHT: BLOCKED")
        return False

    try:
        repo_data = parse_json_output(repo_result.stdout, "Repository-Prüfung")
    except RuntimeError as exc:
        print(f"[BLOCKED] {exc}")
        print("GITHUB_ADMIN_PREFLIGHT: BLOCKED")
        return False

    admin_ok, detail = repo_admin_capability(repo_data)
    print(f"[{'PASS' if admin_ok else 'BLOCKED'}] Konto/Rechte: {detail}")
    print(f"[INFO] Sichtbarkeit: {repo_data.get('visibility', 'unbekannt')}")
    print(f"[INFO] Default-Branch: {repo_data.get('default_branch', 'unbekannt')}")

    branch_result = run(["gh", "api", f"repos/{REPO}/branches/{BRANCH}"], check=False)
    if branch_result.returncode != 0:
        print("[BLOCKED] Zielbranch nicht lesbar.")
        print(describe_failure("Branch-Prüfung", branch_result.stderr))
        print("GITHUB_ADMIN_PREFLIGHT: BLOCKED")
        return False

    try:
        branch_data = parse_json_output(branch_result.stdout, "Branch-Prüfung")
    except RuntimeError as exc:
        print(f"[BLOCKED] {exc}")
        print("GITHUB_ADMIN_PREFLIGHT: BLOCKED")
        return False

    if branch_data.get("name") != BRANCH:
        print(f"[BLOCKED] Erwarteter Branch {BRANCH!r} wurde nicht bestätigt.")
        print("GITHUB_ADMIN_PREFLIGHT: BLOCKED")
        return False

    protected = branch_data.get("protected") is True
    print(f"[INFO] GitHub-Server meldet {BRANCH}.protected={'true' if protected else 'false'}")

    try:
        rulesets = list_rulesets()
        named = [item for item in rulesets if isinstance(item, dict) and item.get("name") == RULESET_NAME]
        print(f"[INFO] P0-Rulesets mit Sollname: {len(named)}")
        if len(named) > 1:
            print("[BLOCKED] Mehrere gleichnamige P0-Rulesets gefunden; zuerst Duplikate manuell bereinigen.")
            print("GITHUB_ADMIN_PREFLIGHT: BLOCKED")
            return False
    except RuntimeError as exc:
        print(f"[BLOCKED] {exc}")
        print("GITHUB_ADMIN_PREFLIGHT: BLOCKED")
        return False

    if not admin_ok:
        print("GITHUB_ADMIN_PREFLIGHT: BLOCKED")
        return False

    print("[PASS] Repository, Branch, Ruleset-Lesepfad und Repository-Adminrecht bestätigt.")
    print("GITHUB_ADMIN_PREFLIGHT: PASS")
    return True


def protection_payload() -> dict:
    return {
        "required_status_checks": {
            "strict": True,
            "contexts": list(REQUIRED_CHECKS),
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
    print("\nEmpfohlen: evidence-freundliches Repository Ruleset")
    print(f"- Name: {RULESET_NAME}")
    print("- Pull Request vor Integration")
    print("- Branch muss vor Merge aktuell sein")
    for check in REQUIRED_CHECKS:
        print(f"- Required Check: {check}")
    print("- keine Bypass-Akteure")
    print("- offene Review-Diskussionen blockieren")
    print("- Force-Push gesperrt")
    print("- Branch-Löschen gesperrt")
    print("\nAlternative/Legacy: klassische Branch Protection über --apply")
    print("Nicht global required: cp1-runtime")
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
        raise RuntimeError(describe_failure("Branch-Schutz setzen", result.stderr))
    print("[PASS] Klassische Branch Protection wurde von GitHub angenommen.")


def apply_ruleset() -> dict:
    items = list_rulesets()
    duplicates = [item for item in items if isinstance(item, dict) and item.get("name") == RULESET_NAME]
    if len(duplicates) > 1:
        raise RuntimeError("Mehrere gleichnamige P0-Rulesets gefunden; automatisches Upsert bleibt aus Sicherheitsgründen gesperrt.")

    current = find_named_ruleset(items)
    ruleset_id = current.get("id") if isinstance(current, dict) else None
    method = "PUT" if isinstance(ruleset_id, int) else "POST"
    endpoint = f"repos/{REPO}/rulesets/{ruleset_id}" if isinstance(ruleset_id, int) else f"repos/{REPO}/rulesets"
    action = "Ruleset aktualisieren" if method == "PUT" else "Ruleset anlegen"

    result = run(
        ["gh", "api", "--method", method, endpoint, "--input", "-"],
        input_text=json.dumps(ruleset_payload()),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(describe_failure(action, result.stderr))

    data = parse_json_output(result.stdout, action)
    ok, failures = evaluate_ruleset(data)
    if not ok:
        raise RuntimeError("GitHub nahm das Ruleset an, aber die Antwort erfüllt den P0-Vertrag nicht: " + "; ".join(failures))

    print(f"[PASS] {action}: {RULESET_NAME}")
    print(f"[PASS] Ruleset-ID: {data.get('id', 'unbekannt')}")
    return data


def verify_ruleset() -> bool:
    try:
        items = list_rulesets()
    except RuntimeError as exc:
        print(f"[FAIL] {exc}")
        return False

    current = find_named_ruleset(items)
    if not isinstance(current, dict) or not isinstance(current.get("id"), int):
        print(f"[FAIL] Ruleset {RULESET_NAME!r} nicht eindeutig gefunden.")
        return False

    result = run(["gh", "api", f"repos/{REPO}/rulesets/{current['id']}"], check=False)
    if result.returncode != 0:
        print("[FAIL] Ruleset konnte nicht serverseitig zurückgelesen werden.")
        print(describe_failure("Ruleset nachprüfen", result.stderr))
        return False

    try:
        data = parse_json_output(result.stdout, "Ruleset nachprüfen")
    except RuntimeError as exc:
        print(f"[FAIL] {exc}")
        return False

    ok, failures = evaluate_ruleset(data)
    print("\n=== RULESET-NACHPRÜFUNG ===")
    print(f"Name:        {'PASS' if data.get('name') == RULESET_NAME else 'FAIL'}")
    print(f"Enforcement: {'PASS' if data.get('enforcement') == 'active' else 'FAIL'}")
    for check in REQUIRED_CHECKS:
        print(f"Required Check {check}: {'PASS' if not any(check in item for item in failures) else 'FAIL'}")
    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
    print(f"GITHUB_P0_RULESET_GATE: {'PASS' if ok else 'FAIL'}")
    return ok


def verify() -> bool:
    result = run(["gh", "api", f"repos/{REPO}/branches/{BRANCH}/protection"], check=False)
    if result.returncode != 0:
        print("[FAIL] Branch-Schutz konnte nach dem Schreiben nicht detailliert gelesen werden.")
        print(describe_failure("Branch-Schutz nachprüfen", result.stderr))
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

    print("\n=== CLASSIC-NACHPRÜFUNG ===")
    print(f"Pull-Request-Gate:       {'PASS' if pr_gate else 'FAIL'}")
    print(f"Required Checks aktuell: {'PASS' if strict else 'FAIL'}")
    print(f"Admins geschützt:        {'PASS' if admins else 'FAIL'}")
    print(f"Force-Push gesperrt:     {'PASS' if not force else 'FAIL'}")
    print(f"Branch-Löschen gesperrt: {'PASS' if not delete else 'FAIL'}")
    for name in REQUIRED_CHECKS:
        print(f"Check {name}: {'PASS' if name in checks else 'FAIL'}")

    ok = pr_gate and strict and admins and not force and not delete and not missing
    print(f"GITHUB_P0_BRANCH_GATE: {'PASS' if ok else 'FAIL'}")
    return ok


def validate_fresh_readiness(report_path: Path = READINESS_REPORT) -> tuple[bool, str]:
    if not report_path.is_file():
        return False, f"Readiness-Evidence fehlt: {report_path}"
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"Readiness-Evidence ist ungültig: {exc}"

    repository, repository_detail = current_repository_identity(ROOT)
    if repository != EXPECTED_REPOSITORY:
        return False, f"aktueller Checkout ist nicht {EXPECTED_REPOSITORY}: {repository_detail}"

    head, head_detail = current_git_head(ROOT)
    if head is None:
        return False, f"aktueller Git-HEAD ist nicht bindbar: {head_detail}"

    fingerprint, fingerprint_detail = machine_fingerprint()
    if fingerprint is None:
        return False, f"aktuelle Maschine ist nicht bindbar: {fingerprint_detail}"

    clean, clean_detail = git_worktree_clean(ROOT)
    if not clean:
        return False, f"aktueller Git-Arbeitsstand ist nicht sauber: {clean_detail}"

    ok, detail = validate_readiness_report(
        data,
        expected_repository=repository,
        expected_head=head,
        expected_machine_fingerprint=fingerprint,
    )
    if not ok:
        return False, detail

    return True, detail + "; aktueller Worktree erneut sauber bestätigt"


def set_runner_variable() -> None:
    ready, detail = validate_fresh_readiness()
    if not ready:
        raise RuntimeError(
            "UE58_RUNNER_ENABLED bleibt gesperrt. " + detail +
            "\nZuerst auf derselben UE-Maschine und demselben sauberen Checkout `python3 Scripts/runner_readiness.py` erfolgreich ausführen."
        )
    print(f"[PASS] {detail}")
    result = run(
        ["gh", "variable", "set", "UE58_RUNNER_ENABLED", "--repo", REPO, "--body", "true"],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(describe_failure("Repository-Variable setzen", result.stderr))
    print("[PASS] UE58_RUNNER_ENABLED=true gesetzt.")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="klassische Branch Protection wirklich setzen")
    group.add_argument("--apply-ruleset", action="store_true", help="empfohlenes evidence-freundliches P0 Ruleset anlegen/aktualisieren")
    parser.add_argument("--doctor", action="store_true", help="nur GitHub-/Admin-Fähigkeit diagnostizieren; niemals schreiben")
    parser.add_argument(
        "--enable-runner-variable",
        action="store_true",
        help="UE58_RUNNER_ENABLED=true setzen; verlangt frische, checkout- und maschinengebundene RUNNER_READINESS: PASS Evidence",
    )
    args = parser.parse_args()

    show_plan()
    try:
        require_gh()
    except RuntimeError as exc:
        print(f"\n[BLOCKED] {exc}")
        return 3

    if args.doctor:
        return 0 if admin_preflight() else 3

    if not args.apply and not args.apply_ruleset:
        print("\nKeine Änderung durchgeführt.")
        print("Empfohlen: python3 Scripts/github_p0_admin.py --doctor")
        print("Danach:    python3 Scripts/github_p0_admin.py --apply-ruleset")
        return 0

    if not admin_preflight():
        print("[BLOCKED] Schreibvorgang wurde vor dem ersten GitHub-Write gestoppt.")
        return 3

    try:
        if args.apply_ruleset:
            apply_ruleset()
            ok = verify_ruleset()
        else:
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
