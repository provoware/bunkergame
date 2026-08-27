from __future__ import annotations
from pathlib import Path
import subprocess, sys, time, json, shlex

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"Diagnostics/Launcher/pipeline_run.json"

class Pipeline:
    def __init__(self, log_cb=None):
        self.log_cb=log_cb or (lambda msg: None)
        self.stages=[]

    def log(self,msg):
        self.log_cb(msg)

    def run(self, args):
        cmd=[sys.executable,str(ROOT/"Scripts/orchestrator.py")]+args
        self.log("Starte Qualitätspipeline: "+" ".join(shlex.quote(x) for x in cmd))
        p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
        for line in (p.stdout or "").splitlines():
            self.log(line)
        if p.stderr:
            self.log("FEHLER: "+p.stderr.strip())
        result={"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "command":cmd,"returncode":p.returncode,
                "status":"GREEN" if p.returncode==0 else ("YELLOW" if p.returncode==1 else "RED"),
                "stdout":p.stdout[-30000:],"stderr":p.stderr[-30000:]}
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return result
