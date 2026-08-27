#!/usr/bin/env python3
"""Validate stored GitHub P0 evidence and independently re-check GitHub live.

A stored JSON file can never produce PASS by itself. Production PASS requires:
1) valid, fresh, untampered evidence structure, and
2) a new live GitHub read matching the bound main SHA and Ruleset contract.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from github_p0_evidence import (
    DEFAULT_OUTPUT,
    KIND,
    SCHEMA_VERSION,
    SHA_RE,
    compute_integrity,
)
from github_p0_public_verify import API_ROOT, API_VERSION, github_get
from github_p0_ruleset import BRANCH, REPO, RULESET_NAME, evaluate_ruleset

MAX_EVIDENCE_AGE_SECONDS = 36 * 60 * 60
MAX_FUTURE_SKEW_SECONDS = 5 * 60
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
Getter = Callable[[str], tuple[bool, Any | None, str]]


def parse_utc(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return parsed.astimezone(timezone.utc)


def validate_record(data: object, *, now: datetime | None = None) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not isinstance(data, dict):
        return False, ["evidence root is not an object"]

    if data.get("schema_version") != SCHEMA_VERSION:
        failures.append(f"unexpected schema_version: {data.get('schema_version')!r}")
    if data.get("kind") != KIND:
        failures.append("wrong evidence kind")
    if data.get("live_observed") is not True:
        failures.append("live_observed is not true")
    if data.get("synthetic") is not False:
        failures.append("synthetic evidence cannot pass")
    if data.get("source") != "github-public-rest":
        failures.append("evidence source is not github-public-rest")
    if data.get("github_api_version") != API_VERSION:
        failures.append("GitHub API version differs from current collector contract")
    if data.get("repository") != REPO:
        failures.append("evidence belongs to a different repository")
    if data.get("branch") != BRANCH:
        failures.append("evidence belongs to a different branch")

    main_sha = data.get("main_sha")
    if not isinstance(main_sha, str) or not SHA_RE.fullmatch(main_sha):
        failures.append("main_sha is not a valid 40-character SHA")
    ruleset_id = data.get("ruleset_id")
    if not isinstance(ruleset_id, int) or ruleset_id <= 0:
        failures.append("ruleset_id is not a positive integer")
    if data.get("ruleset_name") != RULESET_NAME:
        failures.append("ruleset_name differs from P0 contract")
    if data.get("ruleset_enforcement") != "active":
        failures.append("ruleset was not observed as active")
    if data.get("contract_status") != "PASS":
        failures.append("stored contract_status is not PASS")
    if data.get("status") != "PASS":
        failures.append("stored evidence status is not PASS")
    if data.get("failures") != []:
        failures.append("stored evidence contains failures")

    sources = data.get("sources")
    expected_branch = f"{API_ROOT}/repos/{REPO}/branches/{BRANCH}"
    expected_rulesets = f"{API_ROOT}/repos/{REPO}/rulesets"
    expected_detail = f"{API_ROOT}/repos/{REPO}/rulesets/{ruleset_id}" if isinstance(ruleset_id, int) else None
    if not isinstance(sources, dict):
        failures.append("source endpoint map is missing")
    else:
        if sources.get("branch") != expected_branch:
            failures.append("branch source endpoint differs from expected GitHub endpoint")
        if sources.get("rulesets") != expected_rulesets:
            failures.append("ruleset-list source endpoint differs from expected GitHub endpoint")
        if sources.get("ruleset_detail") != expected_detail:
            failures.append("ruleset-detail source endpoint differs from expected GitHub endpoint")

    observed_at = data.get("observed_at_utc")
    if not isinstance(observed_at, str):
        failures.append("observed_at_utc is missing")
    else:
        try:
            observed = parse_utc(observed_at)
            reference = now or datetime.now(timezone.utc)
            age = (reference - observed).total_seconds()
            if age < -MAX_FUTURE_SKEW_SECONDS:
                failures.append("evidence timestamp is implausibly in the future")
            if age > MAX_EVIDENCE_AGE_SECONDS:
                failures.append(
                    f"evidence is stale ({int(age)}s > {MAX_EVIDENCE_AGE_SECONDS}s)"
                )
        except (TypeError, ValueError) as exc:
            failures.append(f"invalid observed_at_utc: {exc}")

    digest = data.get("integrity_sha256")
    if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest):
        failures.append("integrity_sha256 is missing or malformed")
    elif digest != compute_integrity(data):
        failures.append("integrity_sha256 mismatch: evidence was modified after sealing")

    return not failures, failures


def live_recheck(data: dict[str, Any], *, getter: Getter = github_get) -> tuple[bool, list[str]]:
    failures: list[str] = []

    branch_path = f"repos/{REPO}/branches/{BRANCH}"
    ok, branch_data, error = getter(branch_path)
    if not ok or not isinstance(branch_data, dict):
        return False, [f"live branch re-check failed: {error or 'invalid response'}"]

    live_sha = branch_data.get("commit", {}).get("sha") if isinstance(branch_data.get("commit"), dict) else None
    if not isinstance(live_sha, str) or not SHA_RE.fullmatch(live_sha):
        failures.append("live main response contains no valid commit SHA")
    elif live_sha != data.get("main_sha"):
        failures.append(f"main SHA drift: evidence={data.get('main_sha')} live={live_sha}")

    rulesets_path = f"repos/{REPO}/rulesets"
    ok, items, error = getter(rulesets_path)
    if not ok or not isinstance(items, list):
        failures.append(f"live ruleset-list re-check failed: {error or 'invalid response'}")
        return False, failures

    matches = [item for item in items if isinstance(item, dict) and item.get("name") == RULESET_NAME]
    if len(matches) != 1:
        failures.append(f"live ruleset cardinality drift: expected 1, found {len(matches)}")
        return False, failures

    live_id = matches[0].get("id")
    if live_id != data.get("ruleset_id"):
        failures.append(f"ruleset id drift: evidence={data.get('ruleset_id')} live={live_id}")
        return False, failures

    detail_path = f"repos/{REPO}/rulesets/{live_id}"
    ok, detail, error = getter(detail_path)
    if not ok or not isinstance(detail, dict):
        failures.append(f"live ruleset-detail re-check failed: {error or 'invalid response'}")
        return False, failures

    valid, contract_failures = evaluate_ruleset(detail)
    if not valid:
        failures.extend(f"live contract drift: {item}" for item in contract_failures)

    return not failures, failures


def read_evidence(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"evidence file does not exist: {path}"
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"evidence file is unreadable: {exc}"
    if not isinstance(data, dict):
        return None, "evidence file root is not an object"
    return data, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate P0 evidence and re-check GitHub live.")
    parser.add_argument("--evidence", type=Path, default=DEFAULT_OUTPUT, help="evidence JSON path")
    args = parser.parse_args()

    print("=== BUNKER BEATS P0 EVIDENCE VALIDATOR ===")
    print("Modus: STORED-INTEGRITY + FRESHNESS + INDEPENDENT LIVE RE-CHECK")

    data, error = read_evidence(args.evidence)
    if data is None:
        print(f"[FAIL] {error}")
        print("GITHUB_P0_EVIDENCE: FAIL")
        return 2

    record_ok, record_failures = validate_record(data)
    for failure in record_failures:
        print(f"[FAIL] stored evidence: {failure}")
    if not record_ok:
        print("GITHUB_P0_EVIDENCE: FAIL")
        return 2

    live_ok, live_failures = live_recheck(data)
    for failure in live_failures:
        print(f"[FAIL] {failure}")
    if not live_ok:
        print("GITHUB_P0_EVIDENCE: DRIFT")
        return 2

    print(f"[PASS] Evidence is fresh, sealed, bound to main {data['main_sha']} and matches GitHub live.")
    print(f"[PASS] Ruleset {data['ruleset_id']} still satisfies the complete P0 contract.")
    print("GITHUB_P0_EVIDENCE: PASS")
    print("Hinweis: Dieser PASS beweist GitHub-Infrastruktur, nicht UE-Readiness oder CP1 Runtime.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
