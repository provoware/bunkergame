#!/usr/bin/env python3
"""Public, token-free verifier for the BUNKER BEATS P0 Ruleset.

This script never writes and never needs GitHub CLI credentials. It reads the
public repository Ruleset from api.github.com and validates it with the same
pure contract used by the admin tooling.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any

from github_p0_ruleset import REPO, RULESET_NAME, evaluate_ruleset, find_named_ruleset

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
TIMEOUT_SECONDS = 15


def github_get(path: str) -> tuple[bool, Any | None, str]:
    url = f"{API_ROOT}/{path.lstrip('/')}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "bunkergame-p0-public-verifier",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        return False, None, f"Netzwerkfehler: {exc.reason}"
    except TimeoutError:
        return False, None, "Zeitüberschreitung beim GitHub-Aufruf"

    try:
        return True, json.loads(raw), ""
    except json.JSONDecodeError as exc:
        return False, None, f"GitHub-Antwort ist kein gültiges JSON: {exc}"


def verify_public_ruleset() -> tuple[bool, str]:
    ok, items, error = github_get(f"repos/{REPO}/rulesets")
    if not ok or not isinstance(items, list):
        return False, f"Ruleset-Liste nicht öffentlich lesbar — {error}"

    matches = [item for item in items if isinstance(item, dict) and item.get("name") == RULESET_NAME]
    if len(matches) == 0:
        return False, f"Ruleset {RULESET_NAME!r} ist auf GitHub nicht vorhanden"
    if len(matches) > 1:
        return False, f"mehrere Rulesets mit Sollname gefunden ({len(matches)})"

    summary = find_named_ruleset(items)
    if not isinstance(summary, dict) or not isinstance(summary.get("id"), int):
        return False, "Ruleset-ID konnte nicht eindeutig bestimmt werden"

    ruleset_id = summary["id"]
    ok, detail, error = github_get(f"repos/{REPO}/rulesets/{ruleset_id}")
    if not ok or not isinstance(detail, dict):
        return False, f"Ruleset-Detail {ruleset_id} nicht öffentlich lesbar — {error}"

    valid, failures = evaluate_ruleset(detail)
    if not valid:
        return False, "; ".join(failures)

    return True, f"GitHub Ruleset {ruleset_id} ist aktiv und erfüllt den vollständigen P0-Vertrag"


def main() -> int:
    print("=== BUNKER BEATS PUBLIC P0 RULESET VERIFY ===")
    print("Modus: READ-ONLY / TOKEN-FREI / DIREKT VON GITHUB")
    ok, detail = verify_public_ruleset()
    print(f"[{'PASS' if ok else 'INCOMPLETE'}] {detail}")
    print(f"GITHUB_P0_PUBLIC_RULESET: {'PASS' if ok else 'INCOMPLETE'}")
    print("Hinweis: Dieser PASS beweist nur den GitHub-Schutz, niemals UE-Readiness oder CP1 Runtime.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
