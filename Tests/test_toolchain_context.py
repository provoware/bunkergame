
import json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from regression_context import record,compile_rules
from preflight_context import evaluate

def main():
    # isolate evidence using current package store; test priority semantics.
    rules=ROOT/"Config/generated_preflight_rules.json"
    rules.write_text(json.dumps({"rules":[
      {"rule_id":"REG-RUNTIME-CP1-CRASH","source_code":"RUNTIME-CP1-CRASH","priority":"P0","observed_independent_runs":2},
      {"rule_id":"REG-TOOLCHAIN-UE-001","source_code":"TOOLCHAIN-UE-001","priority":"P1","observed_independent_runs":2}
    ]}),encoding="utf-8")
    ctx={"platform":"Linux","git":{"branch":"main","commit":"abc"}}
    a=evaluate([{"code":"RUNTIME-CP1-CRASH","status":"RED"},{"code":"TOOLCHAIN-UE-001","status":"GREEN"}],ctx)
    b=evaluate([{"code":"RUNTIME-CP1-CRASH","status":"GREEN"},{"code":"TOOLCHAIN-UE-001","status":"YELLOW"}],ctx)
    c=evaluate([{"code":"RUNTIME-CP1-CRASH","status":"GREEN"},{"code":"TOOLCHAIN-UE-001","status":"GREEN"}],ctx)
    ok=(a["status"]=="RED" and b["status"]=="YELLOW" and c["status"]=="GREEN")
    # Repair planner should never pretend it applied sudo.
    p=subprocess.run([sys.executable,str(ROOT/"Launcher/repair/toolchain_repair.py"),"--plan"],
                     cwd=ROOT,text=True,capture_output=True,timeout=30)
    plan=json.loads(p.stdout)
    safe_claim=all(x.get("status")!="PASS" for x in plan.get("apply",[]))
    result={"P0_RED":a["status"]=="RED","P1_YELLOW":b["status"]=="YELLOW",
            "ALL_GREEN":c["status"]=="GREEN","repair_plan_exposed":p.returncode==0}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if ok and p.returncode==0 else 1
if __name__=="__main__":raise SystemExit(main())
