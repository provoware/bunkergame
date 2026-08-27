
from __future__ import annotations
from pathlib import Path
import json, time, math

ROOT=Path(__file__).resolve().parents[2]
KB=ROOT/"Diagnostics/Knowledge"
KB.mkdir(parents=True,exist_ok=True)
HISTORY=KB/"solution_outcomes.jsonl"

def record(solution_id, failure_code, outcome, context=None, evidence=None):
    row={
        "schema":"solution.outcome.v1",
        "timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "solution_id":solution_id,
        "failure_code":failure_code,
        "outcome":outcome,
        "context":context or {},
        "evidence":evidence or {}
    }
    with HISTORY.open("a",encoding="utf-8") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row

def stats():
    data={}
    if HISTORY.exists():
        for line in HISTORY.read_text(encoding="utf-8").splitlines():
            try:r=json.loads(line)
            except json.JSONDecodeError:continue
            key=(r.get("failure_code","UNKNOWN"),r.get("solution_id","UNKNOWN"))
            s=data.setdefault(key,{"attempts":0,"successes":0,"failures":0,"blocked":0})
            s["attempts"]+=1
            o=r.get("outcome")
            if o=="SUCCESS":s["successes"]+=1
            elif o=="FAILURE":s["failures"]+=1
            elif o=="BLOCKED":s["blocked"]+=1
    for s in data.values():
        # Bayesian-ish conservative success estimate with a Beta(1,1) prior.
        s["success_rate"]=(s["successes"]+1)/(s["attempts"]+2)
    return data

def score(solution_id,failure_code,base_score):
    s=stats().get((failure_code,solution_id))
    if not s:
        return base_score,{"history":"NONE","attempts":0}
    # Reward demonstrated success, penalize demonstrated failure.
    history_adjustment=(s["successes"]*8)-(s["failures"]*10)-(s["blocked"]*2)
    return base_score+history_adjustment,{"history":"KNOWN",**s}


def stats_json():
    """JSON-safe view of historical solution outcomes."""
    rows=[]
    for (failure_code, solution_id), data in stats().items():
        rows.append({
            "failure_code": failure_code,
            "solution_id": solution_id,
            **data,
        })
    rows.sort(key=lambda x:(x["failure_code"],x["solution_id"]))
    return rows
