
from pathlib import Path
import os,platform,subprocess
ROOT=Path(__file__).resolve().parents[2]
def locate():
    roots=[]
    if os.environ.get("UE_ROOT"): roots.append(Path(os.environ["UE_ROOT"]).expanduser())
    roots += [Path(r"C:\Program Files\Epic Games\UE_5.8"),Path(r"D:\Program Files\Epic Games\UE_5.8"),
              Path("/opt/UnrealEngine"),Path("/opt/Epic Games/UE_5.8"),Path.home()/".local/UnrealEngine"]
    for r in roots:
        if not r.exists():continue
        u=next((p for p in [r/"Engine/Build/BatchFiles/RunUAT.sh",r/"Engine/Build/BatchFiles/RunUAT.bat"] if p.exists()),None)
        e=next((p for p in [r/"Engine/Binaries/Linux/UnrealEditor-Cmd",r/"Engine/Binaries/Win64/UnrealEditor-Cmd.exe"] if p.exists()),None)
        if u or e:return u,e
    return None,None
def run(cmd,timeout):
    p=subprocess.run([str(x) for x in cmd],cwd=ROOT,text=True,capture_output=True,timeout=timeout)
    return {"returncode":p.returncode,"stdout":p.stdout[-20000:],"stderr":p.stderr[-20000:]}
def execute():
    uat,editor=locate()
    project=ROOT/"BunkerBeats.uproject"
    if not uat or not editor:return {"status":"BLOCKED","executed":False,"code":"TOOLCHAIN-UE-001","message":"Unreal 5.8 bzw. RunUAT/Editor nicht gefunden."}
    if not project.exists():return {"status":"BLOCKED","executed":False,"code":"RUNTIME-PROJECT-001","message":"BunkerBeats.uproject fehlt."}
    build=run([uat,"BuildCookRun",f"-project={project}","-platform="+("Win64" if platform.system()=="Windows" else "Linux"),"-clientconfig=Development","-build"],3600)
    if build["returncode"]!=0:return {"status":"RED","executed":True,"code":"BUILD-FAILED","message":"Unreal-Build fehlgeschlagen.","build":build}
    out=ROOT/"Diagnostics/Runtime/UnrealSmoke"; out.mkdir(parents=True,exist_ok=True)
    smoke=run([editor,project,"-unattended","-nop4","-nosplash",
               "-ExecCmds=Automation RunTest BunkerBeats.Smoke;Quit",
               f"-ReportExportPath={out}"],1800)
    return {"status":"GREEN" if smoke["returncode"]==0 else "RED","executed":True,
            "code":"RUNTIME-CP1-BOOT-FAIL" if smoke["returncode"] else "RUNTIME-CP1-OK",
            "message":"Build und BunkerBeats.Smoke erfolgreich." if smoke["returncode"]==0 else "Smoke/CP1 fehlgeschlagen.",
            "build":build,"smoke":smoke}
