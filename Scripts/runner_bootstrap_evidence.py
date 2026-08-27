#!/usr/bin/env python3
"""Create machine-readable evidence for a GitHub-dispatched UE 5.8 runner bootstrap.

This script intentionally proves runner/readiness context only. It never sets
runtime_executed or cp1_pass to true.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from runner_identity import (
    EXPECTED_REPOSITORY,
    current_git_head,
    current_repository_identity,
    git_worktree_clean,
    machine_fingerprint,
)
from runner_readiness_contract import validate_readiness_report

ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "Diagnostics" / "Runtime" / "runner_readiness.json"
OUT = ROOT / "Diagnostics" / "Runtime" / "runner_bootstrap_evidence.json"
SCHEMA_VERSION = 1
KIND = "UE58_RUNNER_BOOTSTRAP_ACCEPTANCE"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def positive_int_text(value: str | None) -> bool:
    if not isinstance(value, str) or not value.isdigit():
        return False
    return int(value) > 0


def main() -> int:
    failures: list[str] = []
    try:
        readiness_data = json.loads(READINESS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        readiness_data = None
        failures.append(f"Readiness-Evidence fehlt/ungültig: {exc}")

    repository, repository_detail = current_repository_identity(ROOT)
    head, head_detail = current_git_head(ROOT)
    fingerprint, fingerprint_scheme = machine_fingerprint()
    clean, clean_detail = git_worktree_clean(ROOT)

    if repository != EXPECTED_REPOSITORY:
        failures.append(f"Repository-Kontext falsch: {repository_detail}")
    if head is None:
        failures.append(f"Git-HEAD nicht bindbar: {head_detail}")
    if fingerprint is None:
        failures.append(f"Maschine nicht bindbar: {fingerprint_scheme}")
    if not clean:
        failures.append(f"Worktree nicht sauber: {clean_detail}")

    readiness_ok = False
    readiness_detail = "Readiness nicht validiert"
    if readiness_data is not None and repository == EXPECTED_REPOSITORY and head and fingerprint:
        readiness_ok, readiness_detail = validate_readiness_report(
            readiness_data,
            expected_repository=repository,
            expected_head=head,
            expected_machine_fingerprint=fingerprint,
        )
        if not readiness_ok:
            failures.append(readiness_detail)

    env = os.environ
    github_repository = env.get("GITHUB_REPOSITORY")
    github_ref = env.get("GITHUB_REF")
    github_sha = env.get("GITHUB_SHA")
    github_event = env.get("GITHUB_EVENT_NAME")
    github_workflow = env.get("GITHUB_WORKFLOW")
    github_job = env.get("GITHUB_JOB")
    github_run_id = env.get("GITHUB_RUN_ID")
    github_run_attempt = env.get("GITHUB_RUN_ATTEMPT")
    runner_name = env.get("RUNNER_NAME")
    runner_os = env.get("RUNNER_OS")
    runner_arch = env.get("RUNNER_ARCH")

    checks = {
        "repository_context_exact": github_repository == EXPECTED_REPOSITORY == repository,
        "main_ref_exact": github_ref == "refs/heads/main",
        "workflow_dispatch_exact": github_event == "workflow_dispatch",
        "workflow_name_exact": github_workflow == "UE 5.8 Runner Bootstrap Acceptance",
        "job_name_exact": github_job == "runner-bootstrap-acceptance",
        "github_sha_matches_checkout": isinstance(github_sha, str) and github_sha == head,
        "github_run_id_valid": positive_int_text(github_run_id),
        "github_run_attempt_valid": positive_int_text(github_run_attempt),
        "runner_name_present": isinstance(runner_name, str) and bool(runner_name.strip()),
        "runner_os_present": isinstance(runner_os, str) and bool(runner_os.strip()),
        "runner_arch_present": isinstance(runner_arch, str) and bool(runner_arch.strip()),
        "worktree_clean": clean,
        "readiness_v3_pass": readiness_ok,
    }
    for name, passed in checks.items():
        if passed is not True:
            failures.append(f"Bootstrap-Check fehlgeschlagen: {name}")

    status = "PASS" if not failures else "FAIL"
    report = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "generated_at_utc": now_utc(),
        "status": status,
        "runtime_executed": False,
        "cp1_pass": False,
        "repository": repository,
        "git_head_sha": head,
        "machine_fingerprint_sha256": fingerprint,
        "machine_identity_scheme": fingerprint_scheme,
        "github": {
            "repository": github_repository,
            "ref": github_ref,
            "sha": github_sha,
            "event_name": github_event,
            "workflow": github_workflow,
            "job": github_job,
            "run_id": int(github_run_id) if positive_int_text(github_run_id) else None,
            "run_attempt": int(github_run_attempt) if positive_int_text(github_run_attempt) else None,
        },
        "runner": {
            "name": runner_name,
            "os": runner_os,
            "arch": runner_arch,
        },
        "readiness": {
            "path": str(READINESS.relative_to(ROOT)),
            "sha256": sha256_file(READINESS),
            "validation": readiness_detail,
        },
        "checks": checks,
        "failures": failures,
        "note": "Bootstrap PASS proves a matching self-hosted runner executed readiness. It is not CP1 runtime evidence.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"RUNNER_BOOTSTRAP_EVIDENCE: {status}")
    return 0 if status == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
