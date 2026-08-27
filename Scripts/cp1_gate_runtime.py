from __future__ import annotations

import json
from pathlib import Path

from cp1_runtime_evidence_contract import (
    TELEMETRY_RELATIVE_PATH,
    validate_runtime_evidence,
)
from runner_identity import (
    EXPECTED_REPOSITORY,
    current_git_head,
    current_repository_identity,
    git_worktree_clean,
    machine_fingerprint,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "Diagnostics/Runtime/CP1_runtime_evidence.json"
TELEMETRY = ROOT / TELEMETRY_RELATIVE_PATH


def load_json_file(path: Path) -> tuple[dict | None, bytes | None, str | None]:
    if not path.is_file():
        return None, None, f"missing file: {path.relative_to(ROOT)}"
    try:
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, None, f"invalid JSON file {path.relative_to(ROOT)}: {exc}"
    if not isinstance(data, dict):
        return None, raw, f"JSON root is not an object: {path.relative_to(ROOT)}"
    return data, raw, None


def main() -> int:
    evidence, _, evidence_error = load_json_file(EVIDENCE)
    if evidence is None:
        print(f"CP1_GATE: BLOCKED - {evidence_error}")
        return 3

    telemetry, telemetry_raw, telemetry_error = load_json_file(TELEMETRY)
    if telemetry is None or telemetry_raw is None:
        print(f"CP1_GATE: BLOCKED - {telemetry_error}")
        return 3

    repository, repository_detail = current_repository_identity(ROOT)
    head, head_detail = current_git_head(ROOT)
    fingerprint, fingerprint_detail = machine_fingerprint()
    clean, clean_detail = git_worktree_clean(ROOT)

    context_failures: list[str] = []
    if repository != EXPECTED_REPOSITORY:
        context_failures.append(f"current repository mismatch: {repository_detail}")
    if head is None:
        context_failures.append(f"current git HEAD unavailable: {head_detail}")
    if fingerprint is None:
        context_failures.append(f"current machine identity unavailable: {fingerprint_detail}")
    if not clean:
        context_failures.append(f"current worktree is not clean: {clean_detail}")

    if context_failures:
        print(json.dumps({"checkpoint": "CP1", "status": "BLOCKED", "failed": context_failures}, ensure_ascii=False, indent=2))
        print("CP1_GATE: BLOCKED")
        return 3

    valid, failures = validate_runtime_evidence(
        evidence,
        expected_repository=repository,
        expected_head=head,
        expected_machine_fingerprint=fingerprint,
        telemetry_data=telemetry,
        telemetry_raw=telemetry_raw,
    )

    result = {
        "checkpoint": "CP1",
        "status": "GREEN" if valid else "RED",
        "evidence_schema": evidence.get("schema_version"),
        "run_id": evidence.get("run_id"),
        "git_head_sha": evidence.get("git_head_sha"),
        "telemetry_path": TELEMETRY_RELATIVE_PATH,
        "failed": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if valid:
        print("CP1_GATE: GREEN")
        print("Hinweis: GREEN gilt nur für diese frische, laufgebundene UE-Evidence auf diesem Checkout und dieser Maschine.")
        return 0

    print("CP1_GATE: RED")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
