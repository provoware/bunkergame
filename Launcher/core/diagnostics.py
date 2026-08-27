
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json, uuid, traceback

ROOT=Path(__file__).resolve().parents[2]
EVENT_DIR=ROOT/"Diagnostics/Events"
REPORT_DIR=ROOT/"Diagnostics/Launcher"
EVENT_DIR.mkdir(parents=True,exist_ok=True)
REPORT_DIR.mkdir(parents=True,exist_ok=True)

@dataclass
class DiagnosticEvent:
    event_id:str
    timestamp:str
    run_id:str
    code:str
    severity:str
    phase:str
    title:str
    message:str
    cause:str
    action:str
    status:str
    detail:dict

class EventLogger:
    def __init__(self,run_id=None,console=None):
        self.run_id=run_id or str(uuid.uuid4())
        self.console=console or (lambda _:None)
        self.events=[]

    def emit(self,code,severity,phase,title,message,cause="",action="",status="INFO",detail=None):
        e=DiagnosticEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            run_id=self.run_id,
            code=code,
            severity=severity,
            phase=phase,
            title=title,
            message=message,
            cause=cause,
            action=action,
            status=status,
            detail=detail or {},
        )
        self.events.append(e)
        self.console(f"[{severity}] [{code}] {title}: {message}")
        with (EVENT_DIR/"events.jsonl").open("a",encoding="utf-8") as f:
            f.write(json.dumps(asdict(e),ensure_ascii=False)+"\n")
        return e

    def report(self,summary):
        p=REPORT_DIR/f"run_{self.run_id}.json"
        p.write_text(
            json.dumps({"run_id":self.run_id,"summary":summary,
                        "events":[asdict(e) for e in self.events]},
                       ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8")
        return p

    def exception(self,code,phase,title,exc,action=""):
        return self.emit(code,"ERROR",phase,title,str(exc),
                         cause=f"{type(exc).__name__}: {exc}",
                         action=action,status="ERROR",
                         detail={"traceback":traceback.format_exc()})
