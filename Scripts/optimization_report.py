from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Diagnostics/Optimization"; OUT.mkdir(parents=True,exist_ok=True)
def run():
    p=ROOT/"Config/optimization_sample.json"
    if not p.exists():
        result={"status":"YELLOW","reason":"No optimization input configured."}
    else:
        d=json.loads(p.read_text(encoding="utf-8"))
        base=d["baseline"]; dirs=d.get("directions",{}); weights=d.get("weights",{})
        ranked=[]
        for c in d["candidates"]:
            score=0.0
            for m,w in weights.items():
                if m not in c["metrics"]: continue
                b=base[m]; v=c["metrics"][m]
                g=(b-v)/max(abs(b),1e-9) if dirs.get(m)=="lower_better" else (v-b)/max(abs(b),1e-9)
                score += w*g
            ranked.append({"id":c["id"],"score":score,"metrics":c["metrics"]})
        result={"status":"PASS","ranked":sorted(ranked,key=lambda x:x["score"],reverse=True)}
    (OUT/"latest_optimization_report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
