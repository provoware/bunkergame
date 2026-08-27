
from __future__ import annotations
from pathlib import Path
import json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))

from rt_diag import EventLogger
from doctor_clean import inspect,evaluate
from preflight_context import evaluate as preflight_evaluate
from regression_context import record,compile_rules
from regression_attribution import record_failure
from attribution_v7 import build_context
from solution_ranker import rank
from knowledge_store import record as kb_record,learn
from solution_outcomes import stats_json as solution_stats

class IntelligentAutoStart:
    """
    Single source of truth for pre-start quality decisions.

    Important:
    - Attribution is evidence, not proof of causality.
    - Suggested repairs are ranked; they are not silently executed.
    - Runtime is eligible only when all blocking gates are clear.
    """

    def __init__(self,console=None):
        self.log=EventLogger(console=console)

    def run(self):
        context=build_context()
        environment=inspect()
        findings=evaluate(environment)

        # Compile historical rules first, then evaluate the fresh environment
        # against those rules. This makes repeated failures preventive.
        compile_rules()
        preflight=preflight_evaluate(findings,context)

        failures=[]
        for finding in findings:
            if finding["status"] == "GREEN":
                continue

            code=finding["code"]
            failure={"code":code,"status":finding["status"],
                     "message":finding["message"],
                     "solutions":[
                         {
                             "id":s.id,
                             "title":s.title,
                             "type":s.type,
                             "risk":s.risk,
                             "reversibility":s.reversibility,
                             "effort":s.effort,
                             "evidence":s.evidence,
                             "action":s.action,
                             "requires_confirmation":s.requires_confirmation,
                             "learned_score":getattr(s,"_learned_score",None),
                             "history":getattr(s,"_history",{"history":"NONE"})
                         }
                         for s in rank(code)
                     ]}
            failures.append(failure)

            # Persist attribution evidence for future learning.
            record_failure(
                self.log.run_id,
                {"code":code,"message":finding["message"]},
                context,
                ["BunkerBeats.Smoke"]
            )

        # Persist the run and immediately compile what future preflight should know.
        kb_record({
            "schema":"knowledge.v1",
            "run_id":self.log.run_id,
            "timestamp_utc":context["local"]["timestamp_utc"],
            "context":context,
            "failures":failures
        })
        learn()
        record(
            self.log.run_id,
            [{"code":x["code"],"status":x["status"],"message":x["message"]} for x in failures],
            context
        )
        compile_rules()

        hard_toolchain_failure=any(f["status"]=="RED" for f in findings)
        p0_block=bool(preflight.get("blocking"))
        p1_block=bool(preflight.get("warnings"))

        if hard_toolchain_failure or p0_block:
            status="RED"
            runtime_policy="RUNTIME_NOT_STARTED"
            explanation="Kritischer Fehler erkannt; abhängige Runtime bleibt gesperrt."
        elif p1_block or any(f["status"]=="YELLOW" for f in findings):
            status="YELLOW"
            runtime_policy="RUNTIME_NOT_STARTED"
            explanation="Mindestens eine Voraussetzung/Evidenz fehlt; Runtime bleibt vorsichtshalber gesperrt."
        else:
            status="GREEN"
            runtime_policy="RUNTIME_ELIGIBLE"
            explanation="Alle aktuellen Preflight-Gates sind erfüllt."

        result={
            "status":status,
            "phase":"PRESTART",
            "context":context,
            "findings":findings,
            "preflight":preflight,
            "failures":failures,
            "runtime_policy":runtime_policy,
            "solution_history":solution_stats(),
            "explanation":explanation
        }

        self.log.emit(
            "AUTOSTART-GATE-001",
            "INFO" if status=="GREEN" else ("WARNING" if status=="YELLOW" else "ERROR"),
            "GATE",
            "Intelligent Preflight Gate",
            explanation,
            status=status,
            detail=result
        )

        report=self.log.report(result)
        machine_report_dir=ROOT/"Diagnostics/Gates/intelligent_autostart_results"
        machine_report_dir.mkdir(parents=True,exist_ok=True)
        machine_report=machine_report_dir/f"{self.log.run_id}.json"
        machine_report.write_text(
            json.dumps({"overall":status,"report":str(report),"result":result},
                       ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8"
        )
        return {"overall":status,"report":str(report),"result":result}

if __name__=="__main__":
    quiet="--quiet-json" in sys.argv
    logger=None if quiet else print
    result=IntelligentAutoStart(console=logger).run()
    print(json.dumps(result,ensure_ascii=False,indent=2))
