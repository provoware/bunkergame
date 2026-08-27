
from pathlib import Path
import json,os,platform,re,shutil,subprocess

ROOT=Path(__file__).resolve().parents[2]
REQ=json.loads((ROOT/"Config/toolchain_requirements_ue58.json").read_text(encoding="utf-8"))

def ver(text):
    m=re.search(r"(\d+)\.(\d+)(?:\.(\d+))?(?:\.(\d+))?",str(text or ""))
    return tuple(int(x or 0) for x in m.groups()) if m else None
def ge(a,b):
    return a is not None and b is not None and tuple(a)>=tuple(b)

def cmd(name,*args):
    exe=shutil.which(name)
    if not exe:return None
    try:
        p=subprocess.run([exe,*args],text=True,capture_output=True,timeout=15)
        return {"path":exe,"returncode":p.returncode,"stdout":p.stdout[:5000],"stderr":p.stderr[:5000]}
    except Exception as e:return {"path":exe,"error":str(e)}

def find_ue():
    roots=[]
    if os.environ.get("UE_ROOT"): roots.append(Path(os.environ["UE_ROOT"]).expanduser())
    roots += [Path(r"C:\Program Files\Epic Games\UE_5.8"),Path(r"D:\Program Files\Epic Games\UE_5.8"),
              Path("/opt/UnrealEngine"),Path("/opt/Epic Games/UE_5.8"),Path.home()/".local/UnrealEngine"]
    for r in roots:
        if not r.exists():continue
        uat=[r/"Engine/Build/BatchFiles/RunUAT.sh",r/"Engine/Build/BatchFiles/RunUAT.bat"]
        ed=[r/"Engine/Binaries/Linux/UnrealEditor-Cmd",r/"Engine/Binaries/Win64/UnrealEditor-Cmd.exe"]
        if any(x.exists() for x in uat+ed):
            return {"available":True,"root":str(r),"runuat":next((str(x) for x in uat if x.exists()),None),
                    "editor":next((str(x) for x in ed if x.exists()),None)}
    return {"available":False}

def inspect():
    system=platform.system()
    if system=="Linux":
        c=cmd("clang","--version")
        try:
            p=subprocess.run(["ldd","--version"],text=True,capture_output=True,timeout=10)
            glibc_raw=((p.stdout or p.stderr).splitlines() or [""])[0]
        except Exception: glibc_raw=""
        tool={"clang_version":ver((c or {}).get("stdout","")),"glibc_version":ver(glibc_raw)}
    elif system=="Windows":
        v=cmd("vswhere","-latest","-products","*","-requires","Microsoft.VisualStudio.Component.VC.Tools.x86.x64","-property","installationVersion")
        tool={"vs_version":ver((v or {}).get("stdout","").strip())}
    else: tool={}
    return {"os":system,"toolchain":tool,"ue":find_ue()}

def evaluate(d):
    f=[]
    u=d["ue"]; f.append({"code":"TOOLCHAIN-UE-001","status":"GREEN" if u["available"] else "YELLOW",
        "message":"Unreal Engine 5.8 gefunden." if u["available"] else "Unreal Engine 5.8 wurde nicht gefunden.","evidence":u})
    if d["os"]=="Linux":
        c=d["toolchain"]["clang_version"]; ok=ge(c,ver(REQ["linux"]["compiler_min"]))
        f.append({"code":"TOOLCHAIN-LINUX-CLANG-001","status":"GREEN" if ok else "RED",
                   "message":"Clang erfüllt die Anforderung." if ok else "Clang 20.1.8 oder neuer wurde nicht nachgewiesen.",
                   "evidence":{"detected":c,"required":REQ["linux"]["compiler_min"]}})
        g=d["toolchain"]["glibc_version"]; ok=ge(g,ver(REQ["linux"]["glibc_min"]))
        f.append({"code":"TOOLCHAIN-LINUX-GLIBC-001","status":"GREEN" if ok else "RED",
                   "message":"glibc erfüllt das Minimum." if ok else "glibc 2.28 oder neuer wurde nicht nachgewiesen.",
                   "evidence":{"detected":g,"required":REQ["linux"]["glibc_min"]}})
    elif d["os"]=="Windows":
        v=d["toolchain"]["vs_version"]; ok=ge(v,ver(REQ["windows"]["visual_studio_min"]))
        f.append({"code":"TOOLCHAIN-WINDOWS-VS-001","status":"GREEN" if ok else "RED",
                   "message":"Visual Studio erfüllt die Anforderung." if ok else "Visual Studio 2022 17.14 oder neuer wurde nicht nachgewiesen.",
                   "evidence":{"detected":v,"required":REQ["windows"]["visual_studio_min"]}})
        f.append({"code":"TOOLCHAIN-WINDOWS-SDK-001","status":"YELLOW",
                  "message":"Windows SDK Tiefenprüfung offen.","evidence":{"required":REQ["windows"]["windows_sdk_min"]}})
    return f
