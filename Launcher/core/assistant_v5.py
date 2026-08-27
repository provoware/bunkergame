
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from diagnostics_v5 import EventLogger
from toolchain_v5 import inspect,evaluate
from repair_recipes_v5 import RECIPES
from regression_rules_v5 import record,compile_rules

class ToolchainAssistant:
    def __init__(self,console=None): self.logger=EventLogger(console=console)
    def run(self,repair=False):
        self.logger.emit("BOOT-TOOLCHAIN-001","INFO","BOOT","Toolchain-Doctor gestartet",
                         "Ich prüfe Unreal, Compiler, SDK-nahe Voraussetzungen und Projektpfade.",
                         status="STARTED")
        data=inspect(); findings=evaluate(data); issues=[]; repairs=[]
        for f in findings:
            st=f["status"]
            self.logger.emit(f["code"],"INFO" if st=="GREEN" else ("WARNING" if st=="YELLOW" else "ERROR"),
                             "DIAGNOSE",f["area"],f["message"],
                             cause="Versionierte UE-5.8-Anforderung",
                             action=f.get("repair",""),status=st,detail=f["evidence"])
            if st!="GREEN":
                issues.append({"code":f["code"],"status":st,"message":f["message"]})
                if repair:
                    recipe=RECIPES.get(f.get("repair"))
                    if recipe:
                        repairs.append({"id":f["repair"],"mode":recipe["mode"],"safe":recipe["safe"],
                                         "steps":recipe["steps"]})
                        self.logger.emit("REPAIR-"+f["repair"],"WARNING" if not recipe["safe"] else "INFO",
                                         "REPAIR",f["area"],
                                         ("Reparatur benötigt bewusstes Eingreifen." if not recipe["safe"]
                                          else "Sichere read-only Prüfung vorbereitet."),
                                         status="ASSISTED" if not recipe["safe"] else "READY",
                                         detail={"steps":recipe["steps"]})
        overall="RED" if any(f["status"]=="RED" for f in findings) else ("YELLOW" if any(f["status"]=="YELLOW" for f in findings) else "GREEN")
        summary={"overall":overall,"issues":issues,"repairs":repairs,
                 "unreal_ready":data["ue"]["available"],"platform":data["os"]}
        self.logger.emit("GATE-TOOLCHAIN-001","INFO" if overall=="GREEN" else "WARNING",
                         "GATE","Toolchain-Gate",
                         {"GREEN":"Alle geprüften Anforderungen erfüllt.",
                          "YELLOW":"Projekt teilweise bereit; mindestens eine Voraussetzung fehlt.",
                          "RED":"Kritische Toolchain-Anforderung nicht erfüllt."}[overall],
                         status=overall,detail=summary)
        report=self.logger.report(summary)
        record(self.logger.run_id,issues); compile_rules()
        return {"run_id":self.logger.run_id,"summary":summary,"report":str(report)}
