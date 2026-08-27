#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, platform, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/"Diagnostics/Reports"
REPORTS.mkdir(parents=True,exist_ok=True)

EXPECTED_ENGINE_PREFIX="5.8"

def roots():
    out=[]
    if os.environ.get("UE_ROOT"):
        out.append(Path(os.environ["UE_ROOT"]).expanduser())
    out += [
        Path(r"C:\Program Files\Epic Games\UE_5.8"),
        Path(r"D:\Program Files\Epic Games\UE_5.8"),
        Path("/opt/UnrealEngine"),
        Path("/opt/Epic Games/UE_5.8"),
        Path.home()/".local/UnrealEngine",
    ]
    return [p for p in out if p.exists()]

def discover():
    found=[]
    for r in roots():
        batch=r/"Engine/Build/BatchFiles"
        binaries=r/"Engine/Binaries"
        uat=[]
        for x in ["RunUAT.bat","RunUAT.sh"]:
            p=batch/x
            if p.exists(): uat.append(str(p))
        editors=[]
        for d in ["Win64","Linux","Mac"]:
            for x in ["UnrealEditor-Cmd.exe","UnrealEditor-Cmd","UnrealEditor.exe","UnrealEditor"]:
                p=binaries/d/x
                if p.exists():
                    editors.append(str(p))
        ubt=[]
        for d in ["Win64","Linux","Mac"]:
            for x in ["UnrealBuildTool.exe","UnrealBuildTool"]:
                p=binaries/d/x
                if p.exists(): ubt.append(str(p))
        found.append({"root":str(r),"uat":uat,"editors":editors,"ubt":ubt})
    return found

def write(name,payload):
    (REPORTS/name).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def invoke(cmd,timeout=3600):
    try:
        p=subprocess.run([str(x) for x in cmd],cwd=ROOT,text=True,capture_output=True,timeout=timeout)
        return {"returncode":p.returncode,"stdout":p.stdout[-30000:],"stderr":p.stderr[-30000:]}
    except subprocess.TimeoutExpired as e:
        return {"returncode":124,"stdout":str(e.stdout or "")[-10000:],"stderr":str(e.stderr or "")[-10000:],"timeout":True}

def ue_platform():
    s=platform.system().lower()
    return "Win64" if s=="windows" else ("Mac" if s=="darwin" else "Linux")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--build",action="store_true")
    ap.add_argument("--pie",action="store_true")
    ap.add_argument("--package",action="store_true")
    ap.add_argument("--automation-filter",default="")
    ap.add_argument("--map",default="")
    args=ap.parse_args()

    uproject=ROOT/"BunkerBeats.uproject"
    discovered=discover()
    d={"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
       "expected_engine":"5.8","uproject_exists":uproject.exists(),
       "platform":ue_platform(),"candidates":discovered}
    d["status"]="GREEN" if discovered and uproject.exists() else "BLOCKED"
    write("unreal_environment.json",d)

    if d["status"]=="BLOCKED":
        result={"status":"BLOCKED","executed":False,
                "runtime_success_claimed":False,
                "reason":"UE 5.8 RunUAT/Editor toolchain or uproject unavailable."}
        write("unreal_runtime_result.json",result)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 3

    sel=discovered[0]
    uat=Path(sel["uat"][0]) if sel["uat"] else None
    editor=Path(sel["editors"][0]) if sel["editors"] else None
    result={"status":"GREEN","executed":False,"steps":[]}

    # Build target: documented UAT BuildCookRun entry point.
    if args.build:
        if not uat:
            result["steps"].append({"step":"build","status":"BLOCKED","reason":"RunUAT unavailable"})
            result["status"]="BLOCKED"
        else:
            cmd=[uat,"BuildCookRun",
                 f"-project={uproject}",
                 f"-platform={ue_platform()}",
                 "-clientconfig=Development",
                 "-build"]
            build=invoke(cmd)
            result["executed"]=True
            result["steps"].append({"step":"build","status":"GREEN" if build["returncode"]==0 else "RED",
                                    "command":[str(x) for x in cmd],"execution":build})
            if build["returncode"]!=0: result["status"]="RED"

    # Packaging uses the same documented BuildCookRun pipeline.
    if args.package and result["status"] not in ("RED","BLOCKED"):
        if not uat:
            result["steps"].append({"step":"package","status":"BLOCKED","reason":"RunUAT unavailable"})
            result["status"]="BLOCKED"
        else:
            cmd=[uat,"BuildCookRun",
                 f"-project={uproject}",
                 f"-platform={ue_platform()}",
                 "-clientconfig=Development",
                 "-build","-cook","-stage","-pak"]
            pack=invoke(cmd)
            result["executed"]=True
            result["steps"].append({"step":"package","status":"GREEN" if pack["returncode"]==0 else "RED",
                                    "command":[str(x) for x in cmd],"execution":pack})
            if pack["returncode"]!=0: result["status"]="RED"

    # Real automation-test path. This is not merely opening the editor:
    # it runs an Automation test set and quits.
    if args.pie and result["status"] not in ("RED","BLOCKED"):
        if not editor:
            result["steps"].append({"step":"automation","status":"BLOCKED","reason":"UnrealEditor-Cmd unavailable"})
            result["status"]="BLOCKED"
        elif not args.automation_filter:
            result["steps"].append({
                "step":"automation","status":"BLOCKED",
                "reason":"No automation filter configured. Register a Smoke group/test path first."
            })
            result["status"]="BLOCKED"
        else:
            report_dir=ROOT/"Diagnostics/TestRuns/UnrealAutomation"
            report_dir.mkdir(parents=True,exist_ok=True)
            cmd=[editor,uproject,
                 "-unattended","-nop4","-nosplash",
                 f'-ExecCmds=Automation RunTest {args.automation_filter};Quit',
                 f"-ReportExportPath={report_dir}"]
            if args.map:
                cmd.insert(2,args.map)
            test=invoke(cmd,timeout=1800)
            result["executed"]=True
            result["steps"].append({"step":"automation","status":"GREEN" if test["returncode"]==0 else "RED",
                                    "command":[str(x) for x in cmd],"execution":test,
                                    "evidence_path":str(report_dir)})
            if test["returncode"]!=0: result["status"]="RED"

    write("unreal_runtime_result.json",result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="GREEN" else (3 if result["status"]=="BLOCKED" else 2)

if __name__=="__main__":
    raise SystemExit(main())
