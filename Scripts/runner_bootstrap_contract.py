#!/usr/bin/env python3
"""Pure validation contract for server-mediated UE 5.8 runner bootstrap evidence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

EXPECTED_REPOSITORY = "provoware/bunkergame"
EXPECTED_BRANCH = "main"
EXPECTED_REF = "refs/heads/main"
WORKFLOW_FILE = "ue58-runner-bootstrap.yml"
WORKFLOW_PATH = f".github/workflows/{WORKFLOW_FILE}"
WORKFLOW_NAME = "UE 5.8 Runner Bootstrap Acceptance"
JOB_NAME = "runner-bootstrap-acceptance"
REQUIRED_LABELS = frozenset({"self-hosted", "unreal", "ue-5.8"})
REQUIRED_SUCCESS_STEPS = (
    "Checkout trusted main",
    "UE 5.8 runner readiness v3",
    "Bind runner bootstrap evidence",
    "Upload runner bootstrap evidence",
)
MAX_BOOTSTRAP_AGE_SECONDS = 30 * 60
MAX_FUTURE_SKEW_SECONDS = 5 * 60


def parse_utc(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return parsed.astimezone(timezone.utc)


def _positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def select_latest_current_main_run(runs: object, current_main_sha: str) -> tuple[dict[str, Any] | None, str]:
    if not isinstance(runs, list):
        return None, "Workflow-Run-Liste ist ungültig"
    candidates: list[dict[str, Any]] = []
    for item in runs:
        if not isinstance(item, dict):
            continue
        if item.get("event") != "workflow_dispatch":
            continue
        if item.get("head_branch") != EXPECTED_BRANCH:
            continue
        if item.get("head_sha") != current_main_sha:
            continue
        candidates.append(item)
    if not candidates:
        return None, "kein manueller Runner-Bootstrap für den aktuellen main-SHA gefunden"

    def key(item: dict[str, Any]) -> tuple[datetime, int]:
        stamp = item.get("created_at")
        try:
            when = parse_utc(stamp) if isinstance(stamp, str) else datetime.min.replace(tzinfo=timezone.utc)
        except ValueError:
            when = datetime.min.replace(tzinfo=timezone.utc)
        run_id = item.get("id") if _positive_int(item.get("id")) else 0
        return when, run_id

    return max(candidates, key=key), "aktueller main-Bootstrap gefunden"


def validate_workflow_run(run: object, current_main_sha: str, *, now: datetime | None = None) -> tuple[bool, str]:
    if not isinstance(run, dict):
        return False, "Workflow-Run fehlt"
    if not _positive_int(run.get("id")):
        return False, "Workflow-Run-ID ist ungültig"
    if run.get("event") != "workflow_dispatch":
        return False, "Runner-Bootstrap wurde nicht manuell per workflow_dispatch gestartet"
    if run.get("head_branch") != EXPECTED_BRANCH:
        return False, f"Runner-Bootstrap lief nicht auf {EXPECTED_BRANCH}"
    if run.get("head_sha") != current_main_sha:
        return False, "Runner-Bootstrap gehört nicht zum aktuellen main-SHA"
    if run.get("path") != WORKFLOW_PATH:
        return False, f"unerwarteter Workflow-Pfad: {run.get('path')!r}"
    repository = run.get("repository")
    if not isinstance(repository, dict) or repository.get("full_name") != EXPECTED_REPOSITORY:
        return False, "Workflow-Run gehört nicht zum erwarteten Repository"
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        return False, f"neuester Runner-Bootstrap ist nicht erfolgreich abgeschlossen: status={run.get('status')!r}, conclusion={run.get('conclusion')!r}"
    if not _positive_int(run.get("run_attempt")):
        return False, "Workflow-Run-Attempt ist ungültig"

    stamp = run.get("updated_at") or run.get("run_started_at") or run.get("created_at")
    if not isinstance(stamp, str):
        return False, "Workflow-Run besitzt keinen Freshness-Zeitstempel"
    try:
        observed = parse_utc(stamp)
    except (ValueError, TypeError) as exc:
        return False, f"Workflow-Zeitstempel ungültig: {exc}"
    reference = now or datetime.now(timezone.utc)
    age = (reference - observed).total_seconds()
    if age < -MAX_FUTURE_SKEW_SECONDS:
        return False, "Runner-Bootstrap liegt unplausibel in der Zukunft"
    if age > MAX_BOOTSTRAP_AGE_SECONDS:
        return False, f"Runner-Bootstrap ist zu alt ({int(age)} s > {MAX_BOOTSTRAP_AGE_SECONDS} s)"
    return True, f"frischer erfolgreicher Bootstrap-Run bestätigt ({int(max(age, 0))} s alt)"


def validate_runner_job(job: object) -> tuple[bool, str]:
    if not isinstance(job, dict):
        return False, "Runner-Bootstrap-Job fehlt"
    if job.get("name") != JOB_NAME:
        return False, f"unerwarteter Bootstrap-Job: {job.get('name')!r}"
    if job.get("status") != "completed" or job.get("conclusion") != "success":
        return False, "Runner-Bootstrap-Job ist nicht erfolgreich abgeschlossen"
    runner_name = job.get("runner_name")
    if not isinstance(runner_name, str) or not runner_name.strip():
        return False, "GitHub meldet keinen ausführenden Self-hosted Runner"

    labels = job.get("labels")
    if not isinstance(labels, list) or not all(isinstance(item, str) for item in labels):
        return False, "Runner-Labels sind nicht lesbar"
    missing_labels = sorted(REQUIRED_LABELS - set(labels))
    if missing_labels:
        return False, "Runner besitzt nicht alle Pflichtlabels: " + ", ".join(missing_labels)

    steps = job.get("steps")
    if not isinstance(steps, list):
        return False, "Workflow-Schritte sind nicht lesbar"
    by_name = {item.get("name"): item for item in steps if isinstance(item, dict) and isinstance(item.get("name"), str)}
    for required in REQUIRED_SUCCESS_STEPS:
        item = by_name.get(required)
        if not isinstance(item, dict):
            return False, f"Pflichtschritt fehlt: {required}"
        if item.get("status") != "completed" or item.get("conclusion") != "success":
            return False, f"Pflichtschritt ist nicht erfolgreich: {required}"

    return True, f"Self-hosted Runner {runner_name!r} mit Pflichtlabels und Readiness-Schritten bestätigt"
