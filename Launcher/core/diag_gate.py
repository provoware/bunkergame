
from pathlib import Path
from datetime import datetime, timezone
import json, uuid

ROOT=Path(__file__).resolve().parents[2]
EVENTS=ROOT/"Diagnostics/Events"; REPORTS=ROOT/"Diagnostics/Reports"
EVENTS.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)

class Logger:
    def __init__(self):
        self.run_id=str(uuid.uuid4()); self.events=[]
    def emit(self,code,severity,phase,title,message,status,detail=None):
        e={"event_id":str(uuid.uuid4()),"timestamp":datetime.now(timezone.utc).isoformat(),
           "run_id":self.run_id,"code":code,"severity":severity,"phase":phase,
           "title":title,"message":message,"status":status,"detail":detail or {}}
        self.events.append(e)
        with (EVENTS/"events.jsonl").open("a",encoding="utf-8") as f:
            f.write(json.dumps(e,ensure_ascii=False)+"\n")
        return e
    def report(self,result):
        p=REPORTS/f"quality_runtime_{self.run_id}.json"
        p.write_text(json.dumps({"run_id":self.run_id,"result":result,"events":self.events},
                                ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return p
