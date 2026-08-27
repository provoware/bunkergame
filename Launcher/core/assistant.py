
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from diagnostics import EventLogger
from repair_engine import RepairEngine
import regression_knowledge

class EnvironmentAssistant:
    def __init__(self,console=None):
        self.logger=EventLogger(console=console)
        self.engine=RepairEngine(self.logger)

    def run(self,repair=True):
        self.logger.emit("BOOT-001","INFO","BOOT","Startroutine gestartet",
                         "Ich prüfe zuerst Projekt, Werkzeuge und Abhängigkeiten.",
                         status="STARTED")
        before=self.engine.scan()
        issues=[]
        repairs=[]
        for f in before:
            fid,status,message,detail=f
            if status!="GREEN":
                issues.append({"code":f"ENV-{fid}-001","title":fid,
                               "status":status,"message":message})
            self.logger.emit(f"ENV-{fid}-001",
                             "INFO" if status=="GREEN" else ("WARNING" if status=="YELLOW" else "ERROR"),
                             "DIAGNOSE",fid,message,
                             cause="Projekt-/Umgebungsprüfung",
                             action="Sichere Reparatur prüfen.",status=status,
                             detail=detail)
            if repair and status!="GREEN":
                a=self.engine.safe_repair(f)
                repairs.append(a.__dict__)
                if a.status=="REPAIRED":
                    self.logger.emit(a.repair_id,"INFO","REPAIR",a.title,a.explanation,
                                     status="REPAIRED",
                                     detail={"changed_paths":a.changed_paths})
        after=self.engine.scan()
        remaining=[{"code":f"ENV-{fid}-001","title":fid,"status":status,"message":message}
                   for fid,status,message,detail in after if status!="GREEN"]
        overall="RED" if any(x[1]=="RED" for x in after) else (
                "YELLOW" if any(x[1]=="YELLOW" for x in after) else "GREEN")
        summary={"overall":overall,"issues":remaining,"repairs":repairs,
                 "unreal_ready":next((d.get("available") for fid,_,_,d in after if fid=="UNREAL"),False)}
        self.logger.emit("GATE-001","INFO" if overall=="GREEN" else "WARNING","GATE",
                         "Gesamtstatus bestimmt",
                         {"GREEN":"Alles bereit.","YELLOW":"Das Projekt ist teilweise bereit; mindestens eine Voraussetzung fehlt.",
                          "RED":"Ein kritischer Fehler verhindert den Start."}[overall],
                         status=overall,detail={"remaining":remaining})
        report=self.logger.report(summary)
        regression_knowledge.record(self.logger.run_id,summary)
        regression_knowledge.derive()
        return {"run_id":self.logger.run_id,"summary":summary,"report":str(report)}

if __name__=="__main__":
    import json
    print(json.dumps(EnvironmentAssistant(console=print).run(),ensure_ascii=False,indent=2))
