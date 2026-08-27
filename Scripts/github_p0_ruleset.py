#!/usr/bin/env python3
"""Shared P0 GitHub Ruleset contract for BUNKER BEATS.

Pure helpers only: no network writes. Used by admin/status tooling and tests.
"""

from __future__ import annotations

from typing import Any

REPO = "provoware/bunkergame"
BRANCH = "main"
RULESET_NAME = "BUNKER BEATS P0 main gate"
REQUIRED_CHECKS = ("static-and-contract", "repository-quality")


def ruleset_payload() -> dict[str, Any]:
    """Return the canonical active Ruleset configuration for main."""
    return {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {
            "ref_name": {
                "include": [f"refs/heads/{BRANCH}"],
                "exclude": [],
            }
        },
        "rules": [
            {
                "type": "pull_request",
                "parameters": {
                    "allowed_merge_methods": ["merge", "squash", "rebase"],
                    "dismiss_stale_reviews_on_push": True,
                    "require_code_owner_review": False,
                    "require_last_push_approval": False,
                    "required_approving_review_count": 0,
                    "required_review_thread_resolution": True,
                },
            },
            {
                "type": "required_status_checks",
                "parameters": {
                    "do_not_enforce_on_create": False,
                    "required_status_checks": [
                        {"context": check} for check in REQUIRED_CHECKS
                    ],
                    "strict_required_status_checks_policy": True,
                },
            },
            {"type": "deletion"},
            {"type": "non_fast_forward"},
        ],
    }


def find_named_ruleset(items: object) -> dict[str, Any] | None:
    if not isinstance(items, list):
        return None
    matches = [item for item in items if isinstance(item, dict) and item.get("name") == RULESET_NAME]
    return matches[0] if len(matches) == 1 else None


def _rule_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for rule in data.get("rules", []):
        if isinstance(rule, dict) and isinstance(rule.get("type"), str):
            result[rule["type"]] = rule
    return result


def evaluate_ruleset(data: object) -> tuple[bool, list[str]]:
    """Validate server Ruleset against the exact P0 contract."""
    failures: list[str] = []
    if not isinstance(data, dict):
        return False, ["Ruleset-Antwort ist kein Objekt"]

    if data.get("name") != RULESET_NAME:
        failures.append("Ruleset-Name stimmt nicht")
    if data.get("target") != "branch":
        failures.append("Target ist nicht branch")
    if data.get("enforcement") != "active":
        failures.append("Ruleset ist nicht active")

    conditions = data.get("conditions", {})
    ref_name = conditions.get("ref_name", {}) if isinstance(conditions, dict) else {}
    includes = ref_name.get("include", []) if isinstance(ref_name, dict) else []
    if f"refs/heads/{BRANCH}" not in includes:
        failures.append("main wird nicht erfasst")

    bypass = data.get("bypass_actors", [])
    if bypass not in ([], None):
        failures.append("unerwartete Bypass-Akteure vorhanden")

    rules = _rule_map(data)
    pull_request = rules.get("pull_request")
    if not isinstance(pull_request, dict):
        failures.append("Pull-Request-Regel fehlt")
    else:
        params = pull_request.get("parameters", {})
        if not isinstance(params, dict):
            failures.append("Pull-Request-Parameter fehlen")
        else:
            if params.get("required_approving_review_count") != 0:
                failures.append("Approval-Anzahl ist nicht solo-repo-kompatibel 0")
            if params.get("required_review_thread_resolution") is not True:
                failures.append("Review-Diskussionen müssen nicht gelöst sein")
            if params.get("dismiss_stale_reviews_on_push") is not True:
                failures.append("alte Reviews werden nicht verworfen")

    status_rule = rules.get("required_status_checks")
    if not isinstance(status_rule, dict):
        failures.append("Required-Status-Checks-Regel fehlt")
    else:
        params = status_rule.get("parameters", {})
        required = params.get("required_status_checks", []) if isinstance(params, dict) else []
        contexts = {
            item.get("context")
            for item in required
            if isinstance(item, dict) and isinstance(item.get("context"), str)
        }
        for check in REQUIRED_CHECKS:
            if check not in contexts:
                failures.append(f"Required Check fehlt: {check}")
        if not isinstance(params, dict) or params.get("strict_required_status_checks_policy") is not True:
            failures.append("Branch muss vor Merge nicht aktuell sein")

    if "deletion" not in rules:
        failures.append("Branch-Löschen ist nicht gesperrt")
    if "non_fast_forward" not in rules:
        failures.append("Force-Push ist nicht gesperrt")

    return not failures, failures
