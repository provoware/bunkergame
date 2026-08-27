from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Diagnostics/Reports"; OUT.mkdir(parents=True,exist_ok=True)
def run():
    pre=json.loads((OUT/"environment_report.json").read_text(encoding="utf-8"))
    q=json.loads((OUT/"quality_checks.json").read_text(encoding="utf-8"))
    t=json.loads((ROOT/"Diagnostics/TestRuns/latest_testrun.json").read_text(encoding="utf-8"))
    r=json.loads((ROOT/"Diagnostics/Regression/latest_regression_gate.json").read_text(encoding="utf-8"))
    checks=[
        ("Environment basic",pre["python_ok"] and pre["git_ok"]),
        ("Quality checks",q["status"]=="PASS"),
        ("Tests",t["status"]=="PASS"),
        ("Regression",r["status"]=="GREEN"),
    ]
    status="GREEN" if all(x[1] for x in checks) else ("YELLOW" if all(x[1] for x in checks[:3]) else "RED")
    result={"checkpoint":"CP1","status":status,"checks":[{"name":n,"pass":ok} for n,ok in checks]}
    (OUT/"cp_gate.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
