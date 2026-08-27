#!/usr/bin/env python3
"""Shared P0 GitHub Ruleset contract for BUNKER BEATS.

Pure helpers only: no network writes. Used by admin/status/public verification
and regression tests. The evaluator is deliberately fail-closed.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

REPO = "provoware/bunkergame"
BRANCH = "main"
RULESET_NAME = "BUNKER BEATS P0 main gate"
REQUIRED_CHECKS = ("static-and-contract", "repository-quality")
EXPECTED_RULE_TYPES = frozenset({"pull_request", "required_status_checks", "deletion", "non_fast_forward"})
EXPECTED_MERGE_METHODS = frozenset({"merge", "squash", "rebase"})


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
    rules = data.get("rules")
    if not isinstance(rules, list):
        return result
    for rule in rules:
        if isinstance(rule, dict) and isinstance(rule.get("type"), str):
            result[rule["type"]] = rule
    return result


def evaluate_ruleset(data: object) -> tuple[bool, list[str]]:
    """Validate a live server Ruleset against the exact P0 contract."""
    failures: list[str] = []
    if not isinstance(data, dict):
        return False, ["Ruleset-Antwort ist kein Objekt"]

    if data.get("name") != RULESET_NAME:
        failures.append("Ruleset-Name stimmt nicht")
    if data.get("target") != "branch":
        failures.append("Target ist nicht branch")
    if data.get("enforcement") != "active":
        failures.append("Ruleset ist nicht active")

    conditions = data.get("conditions")
    ref_name = conditions.get("ref_name") if isinstance(conditions, dict) else None
    includes = ref_name.get("include") if isinstance(ref_name, dict) else None
    excludes = ref_name.get("exclude") if isinstance(ref_name, dict) else None
    if includes != [f"refs/heads/{BRANCH}"]:
        failures.append("Ruleset muss ausschließlich refs/heads/main erfassen")
    if excludes not in ([], None):
        failures.append("Ruleset enthält unerwartete Branch-Ausnahmen")

    bypass = data.get("bypass_actors", [])
    if bypass not in ([], None):
        failures.append("unerwartete Bypass-Akteure vorhanden")

    raw_rules = data.get("rules")
    if not isinstance(raw_rules, list):
        failures.append("Rules-Liste fehlt")
        raw_rules = []

    rule_types = [
        rule.get("type")
        for rule in raw_rules
        if isinstance(rule, dict) and isinstance(rule.get("type"), str)
    ]
    counts = Counter(rule_types)
    duplicates = sorted(rule_type for rule_type, count in counts.items() if count > 1)
    if duplicates:
        failures.append("doppelte Ruleset-Regeln: " + ", ".join(duplicates))

    actual_types = set(rule_types)
    missing_types = sorted(EXPECTED_RULE_TYPES - actual_types)
    extra_types = sorted(actual_types - EXPECTED_RULE_TYPES)
    if missing_types:
        failures.append("Pflichtregeln fehlen: " + ", ".join(missing_types))
    if extra_types:
        failures.append("unerwartete Zusatzregeln: " + ", ".join(extra_types))

    rules = _rule_map(data)
    pull_request = rules.get("pull_request")
    if not isinstance(pull_request, dict):
        failures.append("Pull-Request-Regel fehlt")
    else:
        params = pull_request.get("parameters")
        if not isinstance(params, dict):
            failures.append("Pull-Request-Parameter fehlen")
        else:
            merge_methods = params.get("allowed_merge_methods")
            if not isinstance(merge_methods, list) or set(merge_methods) != EXPECTED_MERGE_METHODS:
                failures.append("erlaubte Merge-Methoden weichen vom Soll ab")
            if params.get("required_approving_review_count") != 0:
                failures.append("Approval-Anzahl ist nicht solo-repo-kompatibel 0")
            if params.get("required_review_thread_resolution") is not True:
                failures.append("Review-Diskussionen müssen nicht gelöst sein")
            if params.get("dismiss_stale_reviews_on_push") is not True:
                failures.append("alte Reviews werden nicht verworfen")
            if params.get("require_code_owner_review") is not False:
                failures.append("CODEOWNERS-Approval würde Solo-Repository unerwartet blockieren")
            if params.get("require_last_push_approval") is not False:
                failures.append("Last-Push-Approval würde Solo-Repository unerwartet blockieren")

    status_rule = rules.get("required_status_checks")
    if not isinstance(status_rule, dict):
        failures.append("Required-Status-Checks-Regel fehlt")
    else:
        params = status_rule.get("parameters")
        if not isinstance(params, dict):
            failures.append("Required-Status-Checks-Parameter fehlen")
        else:
            required = params.get("required_status_checks")
            if not isinstance(required, list):
                failures.append("Required-Checks-Liste fehlt")
                required = []
            contexts = {
                item.get("context")
                for item in required
                if isinstance(item, dict) and isinstance(item.get("context"), str)
            }
            if contexts != set(REQUIRED_CHECKS):
                missing = sorted(set(REQUIRED_CHECKS) - contexts)
                extra = sorted(contexts - set(REQUIRED_CHECKS))
                if missing:
                    failures.append("Required Checks fehlen: " + ", ".join(missing))
                if extra:
                    failures.append("unerwartete Required Checks: " + ", ".join(extra))
            if params.get("strict_required_status_checks_policy") is not True:
                failures.append("Branch muss vor Merge nicht aktuell sein")
            if params.get("do_not_enforce_on_create") is not False:
                failures.append("Status-Checks werden beim Erstellen unerwartet ausgenommen")

    return not failures, failures
