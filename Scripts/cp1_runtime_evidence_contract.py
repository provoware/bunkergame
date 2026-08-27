#!/usr/bin/env python3
"""Pure validation contract for real CP1 UE runtime evidence.

This module performs no GitHub or Unreal writes. GREEN is intentionally strict:
the stored runtime record, current checkout context and the actual Unreal
telemetry file must all describe the same fresh run.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from typing import Any

from runner_identity import (
    EXPECTED_REPOSITORY,
    MACHINE_IDENTITY_SCHEME,
    SHA40_RE,
    SHA256_RE,
)

SCHEMA_VERSION = 3
KIND = "CP1_RUNTIME_EVIDENCE"
TELEMETRY_SCHEMA = "bunkerbeats.cp1.movement.telemetry.v3"
TELEMETRY_RELATIVE_PATH = "Saved/Automation/CP1_RuntimeTelemetry.json"
MAX_EVIDENCE_AGE_SECONDS = 30 * 60
MAX_FUTURE_SKEW_SECONDS = 5 * 60
MAX_RUNTIME_DURATION_SECONDS = 2 * 60 * 60
EXPECTED_UE_MAJOR = 5
EXPECTED_UE_MINOR = 8
REQUIRED_STEPS = ("build", "cp1_character_movement")
RUN_ID_RE = re.compile(r"^[0-9a-f]{32}$")


def parse_utc(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return parsed.astimezone(timezone.utc)


def is_number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(float(value))


def is_positive_number(value: object) -> bool:
    return is_number(value) and float(value) > 0.0


def validate_vector(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or len(value) != 3:
        return [f"{label} must contain exactly three numeric coordinates"]
    failures: list[str] = []
    for index, item in enumerate(value):
        if not is_number(item):
            failures.append(f"{label}[{index}] is not a finite real number")
    return failures


def telemetry_digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_evidence_bytes(data: dict[str, Any]) -> bytes:
    payload = dict(data)
    payload.pop("evidence_integrity_sha256", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_evidence_integrity(data: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_evidence_bytes(data)).hexdigest()


def seal_runtime_evidence(data: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(data)
    sealed["evidence_integrity_sha256"] = compute_evidence_integrity(sealed)
    return sealed


def validate_telemetry(data: object, *, expected_run_id: str | None = None) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not isinstance(data, dict):
        return False, ["telemetry root is not an object"]

    if data.get("schema") != TELEMETRY_SCHEMA:
        failures.append(f"unexpected telemetry schema: {data.get('schema')!r}")

    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        failures.append("telemetry run_id is missing or malformed")
    elif expected_run_id is not None and run_id != expected_run_id:
        failures.append(f"telemetry run_id mismatch: expected={expected_run_id} actual={run_id}")

    frame_samples = data.get("frame_samples")
    if type(frame_samples) is not int or frame_samples <= 0:
        failures.append("frame_samples must be a positive integer")

    for key in (
        "frame_time_ms_avg",
        "frame_time_ms_min",
        "frame_time_ms_max",
        "speed_cm_s",
        "displacement_cm",
    ):
        if not is_positive_number(data.get(key)):
            failures.append(f"{key} must be a positive finite number")

    wall_avg = data.get("wall_frame_time_ms_avg")
    if not is_number(wall_avg) or float(wall_avg) < 0.0:
        failures.append("wall_frame_time_ms_avg must be a non-negative finite number")

    avg = data.get("frame_time_ms_avg")
    minimum = data.get("frame_time_ms_min")
    maximum = data.get("frame_time_ms_max")
    if all(is_number(value) for value in (minimum, avg, maximum)):
        if not float(minimum) <= float(avg) <= float(maximum):
            failures.append("frame timing ordering is inconsistent: min <= avg <= max is false")

    for key in ("position_before", "position_after", "velocity"):
        failures.extend(validate_vector(data.get(key), key))

    displacement = data.get("displacement_cm")
    before = data.get("position_before")
    after = data.get("position_after")
    if (
        is_number(displacement)
        and isinstance(before, list)
        and isinstance(after, list)
        and len(before) == len(after) == 3
        and all(is_number(item) for item in (*before, *after))
    ):
        calculated = math.dist([float(x) for x in before], [float(x) for x in after])
        tolerance = max(0.02, abs(calculated) * 0.01)
        if abs(float(displacement) - calculated) > tolerance:
            failures.append(
                f"displacement_cm is inconsistent with positions: reported={displacement} calculated={calculated:.6f}"
            )
    if is_number(displacement) and float(displacement) <= 0.01:
        failures.append("movement displacement is not above the CP1 threshold")

    movement = data.get("movement_component")
    if not isinstance(movement, dict):
        failures.append("movement_component is missing or not an object")
    else:
        for flag in ("valid", "active", "tick_enabled", "run_physics_without_controller"):
            if movement.get(flag) is not True:
                failures.append(f"movement_component.{flag} must be exactly true")
        for key in ("class", "movement_mode"):
            value = movement.get(key)
            if not isinstance(value, str) or not value.strip():
                failures.append(f"movement_component.{key} must be a non-empty string")
        if not is_positive_number(movement.get("max_walk_speed")):
            failures.append("movement_component.max_walk_speed must be a positive finite number")

    return not failures, failures


def validate_runtime_evidence(
    data: object,
    *,
    expected_repository: str,
    expected_head: str,
    expected_machine_fingerprint: str,
    telemetry_data: object,
    telemetry_raw: bytes,
    now: datetime | None = None,
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not isinstance(data, dict):
        return False, ["runtime evidence root is not an object"]

    schema = data.get("schema_version")
    if type(schema) is not int or schema != SCHEMA_VERSION:
        failures.append(f"unexpected runtime evidence schema_version: {schema!r}")
    if data.get("kind") != KIND:
        failures.append("wrong runtime evidence kind")
    if data.get("status") != "GREEN":
        failures.append(f"runtime status is not GREEN: {data.get('status')!r}")
    if data.get("runtime_executed") is not True:
        failures.append("runtime_executed must be exactly true")
    if data.get("cp1_pass") is not True:
        failures.append("cp1_pass must be exactly true")

    if expected_repository != EXPECTED_REPOSITORY:
        failures.append(f"current checkout is not {EXPECTED_REPOSITORY}: {expected_repository!r}")
    if data.get("repository") != EXPECTED_REPOSITORY:
        failures.append(f"runtime evidence belongs to a different repository: {data.get('repository')!r}")

    head = data.get("git_head_sha")
    if not isinstance(head, str) or not SHA40_RE.fullmatch(head):
        failures.append("runtime evidence contains no valid full git HEAD")
    if not isinstance(expected_head, str) or not SHA40_RE.fullmatch(expected_head):
        failures.append("current git HEAD could not be safely determined")
    elif head != expected_head:
        failures.append(f"runtime evidence git HEAD drift: evidence={head} current={expected_head}")

    fingerprint = data.get("machine_fingerprint_sha256")
    if not isinstance(fingerprint, str) or not SHA256_RE.fullmatch(fingerprint):
        failures.append("runtime evidence contains no valid machine fingerprint")
    if data.get("machine_identity_scheme") != MACHINE_IDENTITY_SCHEME:
        failures.append("runtime evidence uses an unknown machine identity scheme")
    if not isinstance(expected_machine_fingerprint, str) or not SHA256_RE.fullmatch(expected_machine_fingerprint):
        failures.append("current machine fingerprint could not be safely determined")
    elif fingerprint != expected_machine_fingerprint:
        failures.append("runtime evidence was produced on a different machine")

    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        failures.append("runtime evidence run_id is missing or malformed")

    ue = data.get("ue")
    if not isinstance(ue, dict):
        failures.append("UE evidence is missing")
    else:
        if ue.get("version") != "5.8":
            failures.append(f"runtime UE version is not exactly 5.8: {ue.get('version')!r}")
        raw_version = ue.get("version_raw")
        if not isinstance(raw_version, dict):
            failures.append("runtime UE Build.version evidence is missing")
        else:
            major = raw_version.get("MajorVersion")
            minor = raw_version.get("MinorVersion")
            if type(major) is not int or type(minor) is not int:
                failures.append("runtime UE MajorVersion/MinorVersion are not real integers")
            elif major != EXPECTED_UE_MAJOR or minor != EXPECTED_UE_MINOR:
                failures.append(f"runtime UE Build.version is not exactly {EXPECTED_UE_MAJOR}.{EXPECTED_UE_MINOR}")

    steps = data.get("steps")
    if not isinstance(steps, list):
        failures.append("runtime steps are missing")
    else:
        names = [item.get("step") for item in steps if isinstance(item, dict)]
        if len(names) != len(steps):
            failures.append("runtime steps contain a non-object entry")
        if names != list(REQUIRED_STEPS):
            failures.append(f"runtime step sequence differs from contract: {names!r}")
        if len(set(names)) != len(names):
            failures.append("runtime step sequence contains duplicates")
        for item in steps:
            if not isinstance(item, dict):
                continue
            name = item.get("step", "unknown")
            if item.get("status") != "GREEN":
                failures.append(f"runtime step {name!r} is not GREEN")
            step_evidence = item.get("evidence")
            returncode = step_evidence.get("returncode") if isinstance(step_evidence, dict) else None
            if type(returncode) is not int or returncode != 0:
                failures.append(f"runtime step {name!r} returncode is not integer 0")

    started_raw = data.get("started_at_utc")
    finished_raw = data.get("finished_at_utc")
    try:
        started = parse_utc(started_raw) if isinstance(started_raw, str) else None
    except (TypeError, ValueError) as exc:
        started = None
        failures.append(f"invalid started_at_utc: {exc}")
    if started is None and not isinstance(started_raw, str):
        failures.append("started_at_utc is missing")

    try:
        finished = parse_utc(finished_raw) if isinstance(finished_raw, str) else None
    except (TypeError, ValueError) as exc:
        finished = None
        failures.append(f"invalid finished_at_utc: {exc}")
    if finished is None and not isinstance(finished_raw, str):
        failures.append("finished_at_utc is missing")

    reference = now or datetime.now(timezone.utc)
    if started is not None and finished is not None:
        duration = (finished - started).total_seconds()
        if duration < 0:
            failures.append("runtime finished before it started")
        if duration > MAX_RUNTIME_DURATION_SECONDS:
            failures.append(f"runtime duration is implausibly long ({int(duration)}s)")
        age = (reference - finished).total_seconds()
        if age < -MAX_FUTURE_SKEW_SECONDS:
            failures.append("runtime evidence finish timestamp is implausibly in the future")
        if age > MAX_EVIDENCE_AGE_SECONDS:
            failures.append(f"runtime evidence is stale ({int(age)}s > {MAX_EVIDENCE_AGE_SECONDS}s)")

    telemetry_path = data.get("telemetry_path")
    if telemetry_path != TELEMETRY_RELATIVE_PATH:
        failures.append(f"unexpected telemetry_path: {telemetry_path!r}")

    digest = data.get("telemetry_sha256")
    actual_digest = telemetry_digest(telemetry_raw)
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        failures.append("telemetry_sha256 is missing or malformed")
    elif digest != actual_digest:
        failures.append(f"telemetry digest mismatch: evidence={digest} actual={actual_digest}")

    embedded = data.get("telemetry")
    telemetry_ok, telemetry_failures = validate_telemetry(telemetry_data, expected_run_id=run_id if isinstance(run_id, str) else None)
    if not telemetry_ok:
        failures.extend(f"telemetry: {item}" for item in telemetry_failures)
    if embedded != telemetry_data:
        failures.append("embedded telemetry differs from the actual telemetry file")

    integrity = data.get("evidence_integrity_sha256")
    if not isinstance(integrity, str) or not SHA256_RE.fullmatch(integrity):
        failures.append("evidence_integrity_sha256 is missing or malformed")
    elif integrity != compute_evidence_integrity(data):
        failures.append("runtime evidence integrity mismatch: record changed after sealing")

    return not failures, failures
