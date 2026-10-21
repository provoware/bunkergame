"""Validate BUNKER BEATS prerelease inventory; never infer runtime success."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "Docs/VORRELEASE_PFLICHTMATRIX.json"
STATES = {"PLANNED", "IMPLEMENTED", "UNOBSERVED", "BLOCKED", "PASS", "FAIL"}
AREAS = {"infrastructure", "engine", "movement", "characters", "abilities",
         "interaction", "tasks", "progression", "events", "crowd", "rivals",
         "discovery", "persistence", "security", "gameplay", "balance",
         "performance", "visuals", "accessibility", "installation", "tests",
         "documentation", "release"}
MANDATORY = {"P0_RULESET", "P0_RUNNER", "CP1_BUILD", "CP1_EDITOR", "CP1_SPAWN",
             "CP1_MOVEMENT", "CP1_TELEMETRY", "CP1_EVIDENCE", "GAME_END_TO_END",
             "SAVE_ATOMIC", "SAVE_RESTORE", "SAVE_MIGRATION", "SAVE_CORRUPTION",
             "INPUT_KEYBOARD", "UI_800X600", "UI_SCALING_200", "UI_FOCUS",
             "BALANCE_BATCH", "PERFORMANCE_60FPS", "INSTALL_LINUX",
             "INSTALL_WINDOWS", "RELEASE_PACKAGE", "RELEASE_NOTES",
             "RELEASE_FROZEN", "CI_STATIC", "CI_REGRESSION", "CI_UNREAL",
             "CI_FULL_GAME"}


def validate(data, root=ROOT):
    errors = []
    if not isinstance(data, dict):
        return ["root must be object"]
    if data.get("schema_version") != 1 or data.get("repository") != "provoware/bunkergame":
        errors.append("invalid schema or repository")
    if not re.fullmatch(r"[0-9a-f]{40}", str(data.get("observed_main_sha", ""))):
        errors.append("invalid observed SHA")
    rows = data.get("requirements")
    if not isinstance(rows, list) or not rows:
        return errors + ["requirements missing"]
    ids, areas = set(), set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append("invalid requirement object")
            continue
        rid, area, status = row.get("id"), row.get("area"), row.get("status")
        if not isinstance(rid, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]+", rid):
            errors.append("invalid requirement ID")
            continue
        if rid in ids:
            errors.append(f"{rid}: duplicate id")
        ids.add(rid)
        areas.add(area)
        if area not in AREAS or status not in STATES:
            errors.append(f"{rid}: invalid area or status")
        if not row.get("requirement") or not row.get("next_action"):
            errors.append(f"{rid}: missing description or next action")
        refs = row.get("source_refs", [])
        if not isinstance(refs, list):
            errors.append(f"{rid}: invalid source refs")
            continue
        if status in {"IMPLEMENTED", "PASS"} and not refs:
            errors.append(f"{rid}: missing implementation references")
        for ref in refs:
            if not isinstance(ref, str) or not ref:
                errors.append(f"{rid}: invalid source ref")
                continue
            path = (root / ref).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                errors.append(f"{rid}: invalid source path {ref}")
        proof = row.get("evidence")
        if status == "PASS":
            if not isinstance(proof, dict) or proof.get("result") != "PASS" or not re.fullmatch(r"[0-9a-f]{40}", str(proof.get("commit_sha", ""))) or not proof.get("test_id") or not str(proof.get("run_url", "")).startswith("https://github.com/provoware/bunkergame/actions/runs/"):
                errors.append(f"{rid}: PASS requires traceable test evidence")
        elif proof is not None:
            errors.append(f"{rid}: evidence is only allowed for PASS")
    errors += [f"missing area: {x}" for x in sorted(AREAS - areas)]
    errors += [f"missing requirement: {x}" for x in sorted(MANDATORY - ids)]
    return errors


def release_blockers(data):
    return [x["id"] for x in data["requirements"] if x["status"] != "PASS"] + [
        key for key in ("candidate_frozen", "personal_acceptance_complete",
                        "user_release_approved") if data.get(key) is not True]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-ready", action="store_true")
    args = parser.parse_args()
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    failures = validate(data)
    for failure in failures:
        print("FAIL:", failure)
    print("VORRELEASE_MATRIX:", "FAIL" if failures else "PASS")
    if failures:
        raise SystemExit(1)
    if args.release_ready and release_blockers(data):
        print("VORRELEASE_RELEASE: BLOCKED")
        raise SystemExit(2)
    if args.release_ready:
        print("VORRELEASE_RELEASE: PASS (documentation check only)")
