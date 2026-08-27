
from __future__ import annotations
import json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))

from rt_diag import EventLogger
from doctor_clean import inspect,evaluate
from regression_gate_clean import record,compile
from preflight_clean import evaluate as preflight_evaluate
from runtime_clean import execute

def main():
    logger=EventLogger()
    logger.emit("ORCH-001","INFO","BOOT","Gesamtprüfung gestartet",
                "Toolchain, Regression-Gates und Unreal-Runtime werden geprüft.",
                status="STARTED")

    environment=inspect()
    findings=evaluate(environment)

    pre_rules=compile()
    gate=preflight_evaluate(findings)

    logger.emit(
        "PRESTART-001",
        "INFO" if gate["status"]=="GREEN" else "WARNING",
        "PRESTART",
        "Persistente Preflight-Gates",
        f"Preflight-Gate: {gate['status']}.",
        status=gate["status"],
        detail=gate
    )

    issues=[{"code":f["code"],"status":f["status"],"message":f["message"]}
            for f in findings if f["status"]!="GREEN"]
    record(logger.run_id,issues)
    compile()

    if any(f["status"]=="RED" for f in findings):
        result={"status":"RED","phase":"TOOLCHAIN",
                "reason":"Kritische Toolchain-Anforderung fehlt.",
                "findings":findings,"preflight":gate}
    elif gate["status"]=="RED":
        result={"status":"RED","phase":"REGRESSION",
                "reason":"P0-Preflight-Regel blockiert den Start.",
                "findings":findings,"preflight":gate}
    elif gate["status"]=="YELLOW":
        result={"status":"YELLOW","phase":"REGRESSION",
                "reason":"P1-Preflight-Regel blockiert die abhängige Runtime.",
                "findings":findings,"preflight":gate}
    else:
        runtime=execute()
        result={"status":runtime["status"],"phase":"RUNTIME",
                "findings":findings,"preflight":gate,"runtime":runtime}

    logger.emit(
        "FINAL-GATE-001",
        "INFO" if result["status"]=="GREEN" else
        "WARNING" if result["status"]=="YELLOW" else "ERROR",
        "GATE",
        "Gesamtergebnis",
        result.get("reason",result.get("runtime",{}).get("message","")),
        status=result["status"],
        detail=result
    )
    report=logger.report(result)
    print(json.dumps({"overall":result["status"],
                      "report":str(report),
                      "result":result},
                     ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
