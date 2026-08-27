
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from attribution import collect
from regression_attribution import regression_entry,summarize

def main(test_ids=None,base_commit=None,failure=None):
    ctx=collect(base_commit)
    issues=[failure] if failure else []
    from uuid import uuid4
    run_id=str(uuid4())
    regression_entry(run_id,issues,ctx)
    attribution=None
    if failure:
        from regression_attribution import record_failure
        attribution=record_failure(run_id,failure,ctx,test_ids or ["BunkerBeats.Smoke"])
    summary=summarize()
    result={"run_id":run_id,"context":ctx,"attribution":attribution,"summary":summary}
    out=ROOT/"Diagnostics/Attribution/latest_regression_doctor.json"
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    failure=None
    if "--failure-code" in sys.argv:
        i=sys.argv.index("--failure-code"); failure={"code":sys.argv[i+1],"message":"CLI supplied failure"}
    print(json.dumps(main(failure=failure),ensure_ascii=False,indent=2))
