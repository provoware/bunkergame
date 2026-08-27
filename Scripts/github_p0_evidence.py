#!/usr/bin/env python3
"""Collect machine-readable live GitHub P0 infrastructure evidence.

The collector is token-free and read-only. It always writes a bundle when it
can execute, including FAIL bundles. A SHA-256 digest detects accidental local
changes; authenticity comes from the validator's independent live re-check,
not from the digest itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from github_p0_public_verify import API_ROOT, API_VERSION, github_get
from github_p0_ruleset import BRANCH, REPO, RULESET_NAME, evaluate_ruleset

SCHEMA_VERSION = 1
KIND = "GITHUB_P0_INFRASTRUCTURE_EVIDENCE"
DEFAULT_OUTPUT = Path("Diagnostics/Infrastructure/github_p0_evidence.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
Getter = Callable[[str], tuple[bool, Any | None, str]]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_bytes(data: dict[str, Any]) -> bytes:
    payload = dict(data)
    payload.pop("integrity_sha256", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_integrity(data: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


def seal_evidence(data: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(data)
    sealed["integrity_sha256"] = compute_integrity(sealed)
    return sealed


def _source(path: str) -> str:
    return f"{API_ROOT}/{path.lstrip('/')}"


def collect_evidence(*, getter: Getter = github_get, now: datetime | None = None) -> dict[str, Any]:
    observed = now or utc_now()
    branch_path = f"repos/{REPO}/branches/{BRANCH}"
    rulesets_path = f"repos/{REPO}/rulesets"

    evidence: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "observed_at_utc": iso_utc(observed),
        "live_observed": True,
        "synthetic": False,
        "source": "github-public-rest",
        "github_api_version": API_VERSION,
        "repository": REPO,
        "branch": BRANCH,
        "main_sha": None,
        "ruleset_id": None,
        "ruleset_name": RULESET_NAME,
        "ruleset_enforcement": None,
        "contract_status": "FAIL",
        "status": "FAIL",
        "failures": [],
        "sources": {
            "branch": _source(branch_path),
            "rulesets": _source(rulesets_path),
            "ruleset_detail": None,
        },
        "integrity_note": "SHA-256 detects local modification; it is not a GitHub server signature.",
    }

    failures: list[str] = evidence["failures"]

    ok, branch_data, error = getter(branch_path)
    if not ok or not isinstance(branch_data, dict):
        failures.append(f"main branch live read failed: {error or 'invalid response'}")
    else:
        sha = branch_data.get("commit", {}).get("sha") if isinstance(branch_data.get("commit"), dict) else None
        if isinstance(sha, str) and SHA_RE.fullmatch(sha):
            evidence["main_sha"] = sha
        else:
            failures.append("main branch live response contains no valid 40-character commit SHA")

    ok, items, error = getter(rulesets_path)
    if not ok or not isinstance(items, list):
        failures.append(f"ruleset list live read failed: {error or 'invalid response'}")
        return seal_evidence(evidence)

    matches = [item for item in items if isinstance(item, dict) and item.get("name") == RULESET_NAME]
    if len(matches) != 1:
        failures.append(f"expected exactly one ruleset named {RULESET_NAME!r}, found {len(matches)}")
        return seal_evidence(evidence)

    ruleset_id = matches[0].get("id")
    if not isinstance(ruleset_id, int) or ruleset_id <= 0:
        failures.append("ruleset summary contains no valid positive integer id")
        return seal_evidence(evidence)

    evidence["ruleset_id"] = ruleset_id
    detail_path = f"repos/{REPO}/rulesets/{ruleset_id}"
    evidence["sources"]["ruleset_detail"] = _source(detail_path)

    ok, detail, error = getter(detail_path)
    if not ok or not isinstance(detail, dict):
        failures.append(f"ruleset detail live read failed: {error or 'invalid response'}")
        return seal_evidence(evidence)

    evidence["ruleset_enforcement"] = detail.get("enforcement")
    valid, contract_failures = evaluate_ruleset(detail)
    if not valid:
        failures.extend(f"contract: {item}" for item in contract_failures)
        return seal_evidence(evidence)

    evidence["contract_status"] = "PASS"
    if evidence["main_sha"] is not None and not failures:
        evidence["status"] = "PASS"

    return seal_evidence(evidence)


def write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect token-free live GitHub P0 evidence as JSON.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="output JSON path")
    args = parser.parse_args()

    evidence = collect_evidence()
    write_evidence(args.output, evidence)

    print("=== BUNKER BEATS P0 INFRASTRUCTURE EVIDENCE ===")
    print(f"Output: {args.output}")
    print(f"Repository: {evidence['repository']} @ {evidence['main_sha'] or 'UNKNOWN'}")
    print(f"Ruleset: {evidence['ruleset_id'] or 'MISSING'} / {evidence['ruleset_enforcement'] or 'UNKNOWN'}")
    for failure in evidence["failures"]:
        print(f"[FAIL] {failure}")
    print(f"GITHUB_P0_EVIDENCE_COLLECT: {evidence['status']}")
    print("Hinweis: Das Bundle ist erst nach unabhängiger Live-Revalidierung belastbare Evidence.")
    return 0 if evidence["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
