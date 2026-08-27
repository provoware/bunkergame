#!/usr/bin/env python3
"""Token-free live verifier for the UE 5.8 self-hosted runner bootstrap.

PASS can only come from current public GitHub workflow/job data. Local fixtures
can test the contract, but cannot create a production PASS.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from runner_bootstrap_contract import (
    EXPECTED_BRANCH,
    EXPECTED_REPOSITORY,
    JOB_NAME,
    WORKFLOW_FILE,
    select_latest_current_main_run,
    validate_runner_job,
    validate_workflow_run,
)

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"


def github_get(path: str) -> tuple[bool, object | None, str]:
    url = API_ROOT + path
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "bunkerbeats-runner-bootstrap-public-verifier/1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return False, None, f"GitHub HTTP {exc.code}: {exc.reason}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, None, f"GitHub nicht erreichbar: {exc}"
    try:
        return True, json.loads(payload), ""
    except json.JSONDecodeError as exc:
        return False, None, f"GitHub lieferte ungültiges JSON: {exc}"


def _main_sha(branch_data: object) -> tuple[str | None, str]:
    if not isinstance(branch_data, dict) or branch_data.get("name") != EXPECTED_BRANCH:
        return None, "main-Branch-Antwort ist ungültig"
    commit = branch_data.get("commit")
    sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(sha, str) or len(sha) != 40 or any(ch not in "0123456789abcdef" for ch in sha.lower()):
        return None, "aktueller main-SHA konnte nicht sicher bestimmt werden"
    return sha.lower(), "aktueller main-SHA bestätigt"


def verify_public_runner_bootstrap(*, now: datetime | None = None) -> tuple[bool, str, dict[str, Any] | None]:
    ok, branch_data, error = github_get(f"/repos/{EXPECTED_REPOSITORY}/branches/{EXPECTED_BRANCH}")
    if not ok:
        return False, error, None
    main_sha, detail = _main_sha(branch_data)
    if main_sha is None:
        return False, detail, None

    query = urllib.parse.urlencode(
        {
            "branch": EXPECTED_BRANCH,
            "event": "workflow_dispatch",
            "per_page": 20,
        }
    )
    ok, runs_data, error = github_get(
        f"/repos/{EXPECTED_REPOSITORY}/actions/workflows/{WORKFLOW_FILE}/runs?{query}"
    )
    if not ok:
        return False, error, None
    runs = runs_data.get("workflow_runs") if isinstance(runs_data, dict) else None
    run, detail = select_latest_current_main_run(runs, main_sha)
    if run is None:
        return False, detail, {"main_sha": main_sha}

    ok, detail = validate_workflow_run(run, main_sha, now=now)
    if not ok:
        return False, detail, {"main_sha": main_sha, "run_id": run.get("id")}

    run_id = run.get("id")
    ok_http, jobs_data, error = github_get(f"/repos/{EXPECTED_REPOSITORY}/actions/runs/{run_id}/jobs?per_page=100")
    if not ok_http:
        return False, error, {"main_sha": main_sha, "run_id": run_id}
    jobs = jobs_data.get("jobs") if isinstance(jobs_data, dict) else None
    if not isinstance(jobs, list):
        return False, "GitHub-Jobliste ist ungültig", {"main_sha": main_sha, "run_id": run_id}
    matches = [item for item in jobs if isinstance(item, dict) and item.get("name") == JOB_NAME]
    if len(matches) != 1:
        return False, f"erwartet genau einen {JOB_NAME!r}-Job, gefunden: {len(matches)}", {"main_sha": main_sha, "run_id": run_id}

    job = matches[0]
    ok, detail = validate_runner_job(job)
    if not ok:
        return False, detail, {"main_sha": main_sha, "run_id": run_id}

    proof = {
        "main_sha": main_sha,
        "run_id": run_id,
        "run_number": run.get("run_number"),
        "run_attempt": run.get("run_attempt"),
        "runner_name": job.get("runner_name"),
        "runner_group_name": job.get("runner_group_name"),
        "labels": job.get("labels"),
        "updated_at": run.get("updated_at"),
    }
    return True, f"GitHub bestätigt frischen UE-5.8-Runner-Bootstrap auf aktuellem main: run={run_id}, runner={job.get('runner_name')!r}", proof


def main() -> int:
    ok, detail, proof = verify_public_runner_bootstrap(now=datetime.now(timezone.utc))
    if proof:
        print(json.dumps(proof, ensure_ascii=False, indent=2))
    print(detail)
    print(f"UE58_RUNNER_BOOTSTRAP: {'PASS' if ok else 'INCOMPLETE'}")
    print("Hinweis: Dieser PASS beweist Runner-Registrierung + Readiness, aber keinen UE-Build/CP1-Runtime-PASS.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
