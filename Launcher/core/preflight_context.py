
from __future__ import annotations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
RULES=ROOT/"Config/generated_preflight_rules.json"

def load_rules():
    if not RULES.exists():
        return []
    try:
        raw=json.loads(RULES.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    rules=raw.get("rules",[])
    normalized=[]
    for r in rules:
        if not isinstance(r,dict) or not r.get("source_code"):
            continue
        normalized.append({
            "rule_id":r.get("rule_id","REG-"+r["source_code"]),
            "source_code":r["source_code"],
            "priority":r.get("priority","P2"),
            "observed_independent_runs":r.get(
                "observed_independent_runs",
                r.get("observed_runs",0)
            )
        })
    return normalized

def evaluate(current_findings, context=None):
    rules=load_rules()
    fmap={f["code"]:f for f in current_findings}
    blocking=[]; warnings=[]; passed=[]
    for r in rules:
        f=fmap.get(r["source_code"])
        current=f.get("status") if f else "NOT_OBSERVED"
        ok=current=="GREEN"
        item={
            "rule_id":r["rule_id"],
            "priority":r["priority"],
            "observed_independent_runs":r["observed_independent_runs"],
            "current_status":current,
            "passed":ok,
            "context_at_check":context or {}
        }
        if ok:
            passed.append(item)
        elif r["priority"]=="P0":
            blocking.append(item)
        elif r["priority"]=="P1":
            warnings.append(item)
    return {
        "status":"RED" if blocking else "YELLOW" if warnings else "GREEN",
        "blocking":blocking,
        "warnings":warnings,
        "passed":passed
    }
