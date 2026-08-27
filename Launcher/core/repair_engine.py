
from dataclasses import dataclass
from pathlib import Path
import json, os, shutil

ROOT=Path(__file__).resolve().parents[2]

@dataclass
class RepairAction:
    repair_id:str
    title:str
    status:str
    safe:bool
    automatic:bool
    explanation:str
    changed_paths:list[str]

class RepairEngine:
    def __init__(self,logger):
        self.log=logger

    def scan(self):
        findings=[]
        project=ROOT/"BunkerBeats.uproject"
        smoke=ROOT/"Config/cp1_smoke_manifest.json"
        scripts=["environment_doctor.py","quality_checks.py","test_runner.py",
                 "result_collector.py","unreal_runner.py","orchestrator.py"]
        missing=[x for x in scripts if not (ROOT/"Scripts"/x).exists()]
        findings.append(("PROJECT","GREEN" if project.exists() else "RED",
                         "Projektdatei gefunden." if project.exists() else "Projektdatei fehlt.",
                         {"path":str(project)}))
        findings.append(("PIPELINE","GREEN" if not missing else "RED",
                         "Qualitätspipeline vollständig." if not missing else "Pipeline-Skripte fehlen.",
                         {"missing":missing}))
        findings.append(("SMOKE","GREEN" if smoke.exists() else "RED",
                         "CP1 Smoke-Konfiguration vorhanden." if smoke.exists() else "CP1 Smoke-Konfiguration fehlt.",
                         {}))
        findings.append(("UNREAL", "GREEN" if self.find_unreal().get("available") else "YELLOW",
                         "Unreal Engine 5.8 gefunden." if self.find_unreal().get("available") else
                         "Unreal Engine 5.8 wurde nicht gefunden.",
                         self.find_unreal()))
        return findings

    def find_unreal(self):
        candidates=[]
        if os.environ.get("UE_ROOT"):
            candidates.append(Path(os.environ["UE_ROOT"]).expanduser())
        candidates += [
            Path(r"C:\Program Files\Epic Games\UE_5.8"),
            Path(r"D:\Program Files\Epic Games\UE_5.8"),
            Path("/opt/UnrealEngine"),
            Path("/opt/Epic Games/UE_5.8"),
            Path.home()/".local/UnrealEngine",
        ]
        for r in candidates:
            if not r.exists():
                continue
            files=[
                r/"Engine/Build/BatchFiles/RunUAT.sh",
                r/"Engine/Build/BatchFiles/RunUAT.bat",
                r/"Engine/Binaries/Linux/UnrealEditor-Cmd",
                r/"Engine/Binaries/Win64/UnrealEditor-Cmd.exe",
            ]
            if any(p.exists() for p in files):
                return {"available":True,"root":str(r)}
        return {"available":False}

    def safe_repair(self,finding):
        fid,status,message,detail=finding
        if status=="GREEN":
            return RepairAction(f"REPAIR-{fid}-NOOP",fid,"NO_ACTION",True,False,
                                "Keine Reparatur erforderlich.",[])
        if fid=="UNREAL":
            return RepairAction("REPAIR-UE-001","Unreal Engine 5.8 bereitstellen","BLOCKED",
                                False,False,
                                "Keine heimliche Installation oder unbekannte Downloadquelle.",[])
        if fid=="PROJECT":
            return RepairAction("REPAIR-PROJECT-001","Projektdatei wiederherstellen","BLOCKED",
                                False,False,
                                "Ohne vertrauenswürdige Projektquelle keine automatische Rekonstruktion.",[])
        if fid=="SMOKE":
            return RepairAction("REPAIR-SMOKE-001","Smoke-Konfiguration herstellen","BLOCKED",
                                False,False,
                                "Ohne kanonische Testquelle keine automatische Rekonstruktion.",[])
        missing=detail.get("missing",[])
        target=ROOT/"Scripts/result_collector.py"
        if "result_collector.py" in missing and not target.exists():
            target.write_text(
                "from pathlib import Path\n"
                "import json\n"
                "ROOT=Path(__file__).resolve().parents[1]\n"
                "REPORTS=ROOT/'Diagnostics/Reports'\n"
                "REPORTS.mkdir(parents=True,exist_ok=True)\n"
                "def run():\n"
                " items=[]\n"
                " for p in sorted(REPORTS.glob('*.json')):\n"
                "  try: json.loads(p.read_text(encoding='utf-8')); items.append({'file':str(p),'status':'PASS'})\n"
                "  except Exception as e: items.append({'file':str(p),'status':'FAIL','error':str(e)})\n"
                " return {'status':'PASS' if all(x['status']=='PASS' for x in items) else 'FAIL','items':items}\n",
                encoding="utf-8")
            return RepairAction("REPAIR-PIPE-001","Fehlenden Result Collector ergänzt","REPAIRED",
                                True,True,
                                "Bekannte und nicht-destruktive Standardkomponente ergänzt.",
                                [str(target)])
        return RepairAction("REPAIR-PIPE-002","Pipeline reparieren","BLOCKED",False,False,
                            "Die fehlenden Komponenten sind nicht sicher rekonstruierbar.",[])
