
from __future__ import annotations
from pathlib import Path
import argparse, json, os, platform, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
REQ=json.loads((ROOT/"Config/toolchain_requirements_ue58.json").read_text(encoding="utf-8"))

def run(cmd):
    return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)

def detect():
    os_name=platform.system()
    ue_root=os.environ.get("UE_ROOT")
    clang=shutil.which("clang") or shutil.which("clang-20")
    apt=shutil.which("apt-get")
    return {"os":os_name,"ue_root":ue_root,"clang":clang,"apt_get":apt}

def plan():
    d=detect()
    steps=[]
    if d["os"]=="Linux":
        if not d["ue_root"]:
            steps.append({
                "id":"UE_ROOT","mode":"ASSISTED","safe":False,
                "title":"Unreal Engine 5.8 bereitstellen",
                "reason":"Ohne UE_ROOT kann die projektgebundene Engine-Toolchain nicht aufgelöst werden.",
                "action":"UE 5.8 installieren/finden und UE_ROOT setzen."
            })
        if not d["clang"]:
            if d["apt_get"]:
                steps.append({
                    "id":"CLANG20","mode":"EXPLICIT_APPLY","safe":False,
                    "title":"Clang 20 bereitstellen",
                    "reason":"Aktueller Compiler ist nicht nachgewiesen.",
                    "action":"apt-get install clang-20 lld-20",
                    "requires_user_confirmation":True,
                    "sudo":True
                })
            else:
                steps.append({
                    "id":"CLANG20","mode":"ASSISTED","safe":False,
                    "title":"Clang 20 bereitstellen",
                    "reason":"Kein Paketmanagerpfad erkannt.",
                    "action":"Verifizierte Clang-20-Toolchain gemäß Epic/Distribution bereitstellen."
                })
    elif d["os"]=="Windows":
        steps.append({
            "id":"WINDOWS_TOOLCHAIN","mode":"ASSISTED","safe":False,
            "title":"Visual Studio / Windows SDK prüfen",
            "reason":"Installations- und Registryprüfung ist noch separat erforderlich.",
            "action":"Visual Studio C++ Toolchain und Windows SDK gemäß UE 5.8 Requirement bereitstellen."
        })
    return {"detected":d,"steps":steps}

def apply(plan_data,confirm=False):
    results=[]
    for s in plan_data["steps"]:
        if s["id"]=="CLANG20" and confirm and s.get("sudo"):
            if not shutil.which("apt-get"):
                results.append({"id":"CLANG20","status":"BLOCKED","reason":"apt-get fehlt."})
                continue
            # Explicit user-authorized action only.
            cmd=["sudo","apt-get","install","-y","clang-20","lld-20"]
            p=run(cmd)
            results.append({
                "id":"CLANG20",
                "status":"PASS" if p.returncode==0 else "FAIL",
                "returncode":p.returncode,
                "stdout":p.stdout[-8000:],
                "stderr":p.stderr[-8000:]
            })
        else:
            results.append({"id":s["id"],"status":"ASSISTED","action":s["action"]})
    return results

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--plan",action="store_true")
    ap.add_argument("--apply",action="store_true")
    ap.add_argument("--yes",action="store_true")
    a=ap.parse_args()
    p=plan()
    out={"plan":p}
    if a.apply:
        out["apply"]=apply(p,confirm=a.yes)
    print(json.dumps(out,ensure_ascii=False,indent=2))
