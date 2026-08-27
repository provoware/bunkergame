from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Diagnostics/Regression"; OUT.mkdir(parents=True,exist_ok=True)
def run():
    cfg=ROOT/"Config/regression_comparison.json"
    if not cfg.exists():
        result={"status":"YELLOW","reason":"No baseline/current comparison configured."}
    else:
        c=json.loads(cfg.read_text(encoding="utf-8"))
        b=json.loads(Path(c["baseline"]).read_text(encoding="utf-8"))
        cur=json.loads(Path(c["current"]).read_text(encoding="utf-8"))
        dirs=c.get("directions",{})
        thresholds=c.get("absolute_thresholds",{})
        regressions=[]
        for m,bv in b.get("metrics",{}).items():
            if m not in cur.get("metrics",{}): continue
            cv=cur["metrics"][m]
            gain=(cv-bv) if dirs.get(m,"higher_better")=="higher_better" else (bv-cv)
            thr=thresholds.get(m,abs(bv)*.05 if bv else 0)
            if gain < -thr:
                regressions.append({"metric":m,"baseline":bv,"current":cv,"degradation":-gain,"threshold":thr})
        result={"status":"RED" if regressions else "GREEN","regressions":regressions}
    (OUT/"latest_regression_gate.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
