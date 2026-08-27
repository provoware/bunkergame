
from __future__ import annotations
import json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))

from intelligent_autostart import IntelligentAutoStart
from runtime_clean import execute

def main():
    pre=IntelligentAutoStart(console=None).run()
    status=pre["overall"]
    if status!="GREEN":
        return {"status":status,"runtime_started":False,
                "reason":pre["result"].get("explanation"),
                "preflight_report":pre["report"]}
    runtime=execute()
    return {"status":runtime["status"],
            "runtime_started":runtime.get("executed",False),
            "runtime":runtime,
            "preflight_report":pre["report"]}

if __name__=="__main__":
    print(json.dumps(main(),ensure_ascii=False,indent=2))
