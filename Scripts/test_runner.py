from __future__ import annotations
import importlib.util, json, sys, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Diagnostics/TestRuns"; OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"Core")); sys.path.insert(0,str(ROOT/"Data"))
def load(path):
    spec=importlib.util.spec_from_file_location("bb_test_"+path.stem+"_"+str(id(path)),path)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod
def run():
    results=[]
    for p in sorted((ROOT/"Tests").glob("*.py")):
        if p.name in {"test_runner.py","run_all.py"}: continue
        try:
            mod=load(p)
            fn=getattr(mod,"run",None)
            if not callable(fn):
                continue
            out=fn()
            if isinstance(out,list):
                passed=sum(1 for x in out if isinstance(x,dict) and x.get("status")=="PASS")
                failed=sum(1 for x in out if isinstance(x,dict) and x.get("status")=="FAIL")
                results.append({"file":p.name,"status":"PASS" if failed==0 else "FAIL",
                                "passed":passed,"failed":failed,"details":out})
            else:
                results.append({"file":p.name,"status":"PASS"})
        except Exception as e:
            results.append({"file":p.name,"status":"FAIL","error":str(e),"traceback":traceback.format_exc()})
    passed=sum(x["status"]=="PASS" for x in results)
    failed=sum(x["status"]=="FAIL" for x in results)
    payload={"status":"PASS" if failed==0 and results else ("YELLOW" if not results else "FAIL"),
             "tests":results,"summary":{"test_files":len(results),"passed":passed,"failed":failed}}
    (OUT/"latest_testrun.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return payload
if __name__=="__main__":
    p=run(); print(json.dumps(p,ensure_ascii=False,indent=2)); raise SystemExit(0 if p["status"]=="PASS" else 1)
