#!/usr/bin/env python3
"""Pure contract validation for UE 5.8 runner readiness evidence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from runner_identity import (
    EXPECTED_REPOSITORY,
    MACHINE_IDENTITY_SCHEME,
    SHA40_RE,
    SHA256_RE,
)

SCHEMA_VERSION = 3
KIND = "UE58_RUNNER_READINESS"
MAX_READINESS_AGE_SECONDS = 30 * 60
MAX_FUTURE_SKEW_SECONDS = 5 * 60
EXPECTED_UE_MAJOR = 5
EXPECTED_UE_MINOR = 8

REQUIRED_CHECKS = frozenset(
    {
        "project_file",
        "editor_target",
        "engine_root_detected",
        "unreal_editor_detected",
        "engine_build_script_detected",
        "engine_version_exact_5_8",
        "python_available",
        "repo_writable",
        "free_disk_gt_5gb",
        "git_worktree_clean_before_runtime",
        "repository_identity_exact",
        "git_head_bound",
        "machine_identity_bound",
    }
)


def parse_utc(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return parsed.astimezone(timezone.utc)


def validate_readiness_report(
    data: object,
    *,
    expected_repository: str,
    expected_head: str,
    expected_machine_fingerprint: str,
    now: datetime | None = None,
) -> tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "Readiness-Evidence ist kein JSON-Objekt"

    schema = data.get("schema_version")
    if type(schema) is not int or schema != SCHEMA_VERSION:
        return False, f"unerwartete Readiness-Schema-Version: {schema!r}"
    if data.get("kind") != KIND:
        return False, "falscher Evidence-Typ"
    if data.get("status") != "PASS":
        return False, f"Readiness-Status ist {data.get('status')!r}, nicht PASS"
    if data.get("runtime_executed") is not False or data.get("cp1_pass") is not False:
        return False, "Readiness-Evidence vermischt unzulässig Runtime-/CP1-Status"

    checks = data.get("checks")
    if not isinstance(checks, dict):
        return False, "Readiness-Checks fehlen"
    actual_check_names = set(checks)
    if actual_check_names != REQUIRED_CHECKS:
        missing = sorted(REQUIRED_CHECKS - actual_check_names)
        extra = sorted(actual_check_names - REQUIRED_CHECKS)
        parts: list[str] = []
        if missing:
            parts.append("fehlend: " + ", ".join(missing))
        if extra:
            parts.append("unerwartet: " + ", ".join(extra))
        return False, "Readiness-Check-Satz weicht vom Vertrag ab (" + "; ".join(parts) + ")"
    if not all(value is True for value in checks.values()):
        return False, "nicht alle Readiness-Checks sind exakt true"

    if expected_repository != EXPECTED_REPOSITORY:
        return False, f"aktueller Checkout gehört nicht zu {EXPECTED_REPOSITORY}: {expected_repository!r}"
    if data.get("repository") != EXPECTED_REPOSITORY:
        return False, f"Evidence gehört zum falschen Repository: {data.get('repository')!r}"

    head = data.get("git_head_sha")
    if not isinstance(head, str) or not SHA40_RE.fullmatch(head):
        return False, "Evidence enthält keinen gültigen vollständigen Git-HEAD"
    if not isinstance(expected_head, str) or not SHA40_RE.fullmatch(expected_head):
        return False, "aktueller Git-HEAD konnte nicht sicher bestimmt werden"
    if head != expected_head:
        return False, f"Evidence gehört zu anderem Git-HEAD: evidence={head}, aktuell={expected_head}"

    fingerprint = data.get("machine_fingerprint_sha256")
    if not isinstance(fingerprint, str) or not SHA256_RE.fullmatch(fingerprint):
        return False, "Evidence enthält keinen gültigen Maschinenfingerprint"
    if data.get("machine_identity_scheme") != MACHINE_IDENTITY_SCHEME:
        return False, "unbekanntes Maschinenfingerprint-Schema"
    if not isinstance(expected_machine_fingerprint, str) or not SHA256_RE.fullmatch(expected_machine_fingerprint):
        return False, "aktuelle Maschinenidentität konnte nicht sicher bestimmt werden"
    if fingerprint != expected_machine_fingerprint:
        return False, "Readiness-Evidence stammt nicht von dieser Maschine"

    if data.get("engine_version") != "5.8":
        return False, f"Evidence meldet unerwartete Engine-Version: {data.get('engine_version')!r}"
    raw_version = data.get("engine_version_raw")
    if not isinstance(raw_version, dict):
        return False, "Engine Build.version Evidence fehlt"
    major = raw_version.get("MajorVersion")
    minor = raw_version.get("MinorVersion")
    if type(major) is not int or type(minor) is not int:
        return False, "Engine Build.version Major/Minor sind nicht echte Integer"
    if major != EXPECTED_UE_MAJOR or minor != EXPECTED_UE_MINOR:
        return False, f"Engine Build.version ist nicht exakt {EXPECTED_UE_MAJOR}.{EXPECTED_UE_MINOR}"

    stamp = data.get("generated_at_utc")
    if not isinstance(stamp, str):
        return False, "Freshness-Zeitstempel fehlt"
    try:
        generated = parse_utc(stamp)
    except (ValueError, TypeError) as exc:
        return False, f"Freshness-Zeitstempel ungültig: {exc}"

    reference = now or datetime.now(timezone.utc)
    age = (reference - generated).total_seconds()
    if age < -MAX_FUTURE_SKEW_SECONDS:
        return False, "Readiness-Evidence liegt unplausibel in der Zukunft"
    if age > MAX_READINESS_AGE_SECONDS:
        return False, f"Readiness-Evidence ist zu alt ({int(age)} s > {MAX_READINESS_AGE_SECONDS} s)"

    return True, f"frische, checkout- und maschinengebundene Readiness-Evidence bestätigt ({int(max(age, 0))} s alt)"
