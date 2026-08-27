
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from rt_diag import EventLogger
from doctor_clean import inspect,evaluate
from regression_context import record,compile_rules
from preflight_context import evaluate as preflight_evaluate

def main():
    logger=EventLogger()
    env=inspect()
    findings=evaluate(env)
    context={
        "platform":env.get("os"),
        "runtime":env,
        "git":{},
    }
    try:
        from build_context import git_context, collect
        context.update(collect(toolchain_snapshot=env.get("toolchain")))
    except Exception:
        pass

    rules=compile_rules()
    gate=preflight_evaluate(findings,context)
    issues=[{"code":f["code"],"status":f["status"],"message":f["message"]} for f in findings if f["status"]!="GREEN"]
    record(logger.run_id,issues,context)
    compile_rules()

    if any(f["status"]=="RED" for f in findings):
        result={"status":"RED","phase":"TOOLCHAIN","reason":"Kritische Toolchain-Anforderung fehlt.",
                "findings":findings,"preflight":gate,"context":context}
    elif gate["status"]=="RED":
        result={"status":"RED","phase":"REGRESSION","reason":"P0-Preflight-Regel blockiert.",
                "findings":findings,"preflight":gate,"context":context}
    elif gate["status"]=="YELLOW":
        result={"status":"YELLOW","phase":"REGRESSION","reason":"P1-Preflight-Regel blockiert Runtime.",
                "findings":findings,"preflight":gate,"context":context}
    else:
        result={"status":"READY_FOR_RUNTIME","phase":"RUNTIME","findings":findings,"preflight":gate,"context":context}
    logger.report(result)
    print(json.dumps({"overall":result["status"],"result":result},ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
