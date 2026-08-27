
import json,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from solution_outcomes import record,stats,score
def main():
    sid="TEST-SOLUTION-"+uuid.uuid4().hex[:8]
    code="TEST-LEARN-"+uuid.uuid4().hex[:8]
    for outcome in ("FAILURE","SUCCESS","SUCCESS"):
        record(sid,code,outcome,{"run":str(uuid.uuid4())})
    s=stats()[(code,sid)]
    scored,history=score(sid,code,10)
    r={"attempts":s["attempts"]==3,"successes":s["successes"]==2,
       "rate_positive":s["success_rate"]>0.5,"score_increased":scored>10,
       "history_known":history["history"]=="KNOWN"}
    print(json.dumps(r,ensure_ascii=False,indent=2))
    return 0 if all(r.values()) else 1
if __name__=="__main__":raise SystemExit(main())
