from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, os, platform, shutil, subprocess, time

ROOT=Path(__file__).resolve().parents[2]
CFG=json.loads((ROOT/"Launcher/launcher_config.json").read_text(encoding="utf-8"))

@dataclass
class Finding:
    id:str
    title:str
    status:str
    message:str
    action:str
    automatic:bool
    detail:dict

class DiagnosticEngine:
    def __init__(self, root:Path=ROOT):
        self.root=root
    def emit(self,*args,**kwargs): pass

    def _finding(self,*args,**kwargs):
        return Finding(*args,**kwargs)

    def scan(self):
        findings=[]
        project=self.root/CFG["project_file"]
        findings.append(self._finding(
            "PROJECT.FILE", "Projektdatei",
            "GREEN" if project.exists() else "RED",
            "Die Unreal-Projektdatei wurde gefunden." if project.exists() else "Die Projektdatei fehlt.",
            "Projektdatei wiederherstellen oder korrektes Projektverzeichnis wählen.",
            False, {"path":str(project)}))

        py=shutil.which("python3") or shutil.which("python")
        findings.append(self._finding(
            "RUNTIME.PYTHON","Python",
            "GREEN" if py else "RED",
            f"Python ist verfügbar: {py}" if py else "Python wurde nicht gefunden.",
            "Python 3 installieren oder PATH korrigieren.",
            False, {"path":py}))

        git=shutil.which("git")
        findings.append(self._finding(
            "RUNTIME.GIT","Git",
            "GREEN" if git else "YELLOW",
            f"Git ist verfügbar: {git}" if git else "Git fehlt; Git-Funktionen bleiben eingeschränkt.",
            "Git installieren oder PATH korrigieren.",
            False, {"path":git}))

        scripts=["environment_doctor.py","quality_checks.py","test_runner.py","result_collector.py","unreal_runner.py","orchestrator.py"]
        missing=[x for x in scripts if not (self.root/"Scripts"/x).exists()]
        findings.append(self._finding(
            "PIPELINE.SCRIPTS","Qualitätspipeline",
            "GREEN" if not missing else "RED",
            "Alle Kernskripte vorhanden." if not missing else f"Fehlende Skripte: {', '.join(missing)}",
            "Pipeline-Reparatur ausführen.",
            True, {"missing":missing}))

        smoke=self.root/"Config/cp1_smoke_manifest.json"
        findings.append(self._finding(
            "CP1.SMOKE","CP1 Smoke Suite",
            "GREEN" if smoke.exists() else "RED",
            "Smoke-Konfiguration vorhanden." if smoke.exists() else "CP1 Smoke-Konfiguration fehlt.",
            "Smoke-Konfiguration wiederherstellen.",
            True, {}))

        ue=self._find_ue()
        findings.append(self._finding(
            "UNREAL.58","Unreal Engine 5.8",
            "GREEN" if ue["available"] else "YELLOW",
            ue["message"],
            "UE_ROOT setzen oder Unreal Engine 5.8 installieren.",
            False, ue))

        return findings

    def _find_ue(self):
        candidates=[]
        env=os.environ.get("UE_ROOT")
        if env: candidates.append(Path(env).expanduser())
        candidates += [
            Path(r"C:\Program Files\Epic Games\UE_5.8"),
            Path(r"D:\Program Files\Epic Games\UE_5.8"),
            Path("/opt/UnrealEngine"),
            Path("/opt/Epic Games/UE_5.8"),
            Path.home()/".local/UnrealEngine",
        ]
        for c in candidates:
            if not c.exists(): continue
            runuat_sh=c/"Engine/Build/BatchFiles/RunUAT.sh"
            editor=c/"Engine/Binaries/Linux/UnrealEditor-Cmd"
            if runuat_sh.exists() or editor.exists():
                return {"available":True,"root":str(c),
                        "runuat":str(runuat_sh) if runuat_sh.exists() else None,
                        "editor":str(editor) if editor.exists() else None,
                        "message":f"Unreal Engine 5.8 gefunden: {c}"}
        return {"available":False,"root":None,"runuat":None,"editor":None,
                "message":"Unreal Engine 5.8 wurde nicht gefunden."}

    def safe_repairs(self, findings):
        repairs=[]
        for f in findings:
            if f.id=="PIPELINE.SCRIPTS" and f.status=="RED" and f.automatic:
                # Never manufacture unknown logic; only report.
                repairs.append({"id":f.id,"status":"SKIPPED","reason":"Safe repair requires a known-good baseline source."})
        return repairs

    def overall(self, findings):
        statuses=[f.status for f in findings]
        if "RED" in statuses: return "RED"
        if "YELLOW" in statuses: return "YELLOW"
        return "GREEN"

    def report(self,findings,repairs=None):
        out={"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
             "overall":self.overall(findings),
             "findings":[f.__dict__ for f in findings],
             "repairs":repairs or []}
        p=self.root/CFG["directories"]["diagnostics"]/"launcher_diagnostics.json"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return out
