
from __future__ import annotations
from pathlib import Path
import json,time
from attribution import collect
from test_impact import map_tests,associate_failure

ROOT=Path(__file__).resolve().parents[2]
REG=ROOT/"Diagnostics/Regression"; ATTR=ROOT/"Diagnostics/Attribution"
REG.mkdir(parents=True,exist_ok=True); ATTR.mkdir(parents=True,exist_ok=True)
HISTORY=REG/"knowledge_v6.jsonl"
ATTR_HISTORY=ATTR/"attribution_history.jsonl"

def record_failure(run_id, failure, context, test_ids=None):
    test_ids=test_ids or []
    files=context.get("changed_files",{}).get("files",[])
    impacts=map_tests(files,test_ids)
    ranked=associate_failure(failure,files,impacts)
    top=ranked[0] if ranked else None

    if top and top["score"]>=60: confidence="HIGH"
    elif top and top["score"]>=30: confidence="MEDIUM"
    elif top: confidence="LOW"
    else: confidence="NONE"

    row={
        "schema":"regression.attribution.v1",
        "run_id":run_id,
        "timestamp_utc":context.get("local",{}).get("timestamp_utc"),
        "failure":failure,
        "context":context,
        "test_impacts":impacts,
        "candidate_files":ranked,
        "attribution":{
            "confidence":confidence,
            "candidate_file":top["path"] if top else None,
            "candidate_score":top["score"] if top else 0,
            "causal_status":"HYPOTHESIS_ONLY" if confidence!="HIGH" else "HIGH_CONFIDENCE_CANDIDATE"
        }
    }
    with ATTR_HISTORY.open("a",encoding="utf-8") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row

def regression_entry(run_id,issues,context):
    row={"schema":"regression.v6.contextual",
         "run_id":run_id,
         "timestamp_utc":context.get("local",{}).get("timestamp_utc"),
         "context":context,
         "issues":issues}
    with HISTORY.open("a",encoding="utf-8") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row

def summarize():
    rows=[]
    if ATTR_HISTORY.exists():
        for line in ATTR_HISTORY.read_text(encoding="utf-8").splitlines():
            try: rows.append(json.loads(line))
            except json.JSONDecodeError: pass
    by_file={}
    by_code={}
    for r in rows:
        a=r.get("attribution",{})
        p=a.get("candidate_file")
        c=r.get("failure",{}).get("code")
        if p: by_file[p]=by_file.get(p,0)+1
        if c: by_code[c]=by_code.get(c,0)+1
    report={
        "runs_with_attribution":len(rows),
        "top_candidate_files":sorted(by_file.items(),key=lambda x:-x[1])[:20],
        "top_failure_codes":sorted(by_code.items(),key=lambda x:-x[1])[:20],
    }
    (ATTR/"ATTRIBUTION_SUMMARY.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report
