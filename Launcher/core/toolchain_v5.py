
from __future__ import annotations
from pathlib import Path
import json,os,platform,re,shutil,subprocess

ROOT=Path(__file__).resolve().parents[2]
REQ=json.loads((ROOT/"Config/toolchain_requirements_ue58.json").read_text(encoding="utf-8"))

def ver(text):
    m=re.search(r"(\d+)\.(\d+)(?:\.(\d+))?(?:\.(\d+))?",str(text or ""))
    return tuple(int(x or 0) for x in m.groups()) if m else None

def ge(a,b):
    a=ver(a) if not isinstance(a,tuple) else a
    b=ver(b) if not isinstance(b,tuple) else b
    return a is not None and b is not None and a>=b

def cmd(name,*args):
    exe=shutil.which(name)
    if not exe: return None
    try:
        p=subprocess.run([exe,*args],text=True,capture_output=True,timeout=15)
        return {"path":exe,"returncode":p.returncode,"stdout":p.stdout[:4000],"stderr":p.stderr[:4000]}
    except Exception as e: return {"path":exe,"error":str(e)}

def ue():
    roots=[]
    if os.environ.get("UE_ROOT"): roots.append(Path(os.environ["UE_ROOT"]).expanduser())
    roots += [Path(r"C:\Program Files\Epic Games\UE_5.8"),
              Path(r"D:\Program Files\Epic Games\UE_5.8"),
              Path("/opt/UnrealEngine"),Path("/opt/Epic Games/UE_5.8"),
              Path.home()/".local/UnrealEngine"]
    for r in roots:
        if not r.exists(): continue
        candidates=[
            r/"Engine/Build/BatchFiles/RunUAT.sh",
            r/"Engine/Build/BatchFiles/RunUAT.bat",
            r/"Engine/Binaries/Linux/UnrealEditor-Cmd",
            r/"Engine/Binaries/Win64/UnrealEditor-Cmd.exe"
        ]
        if any(x.exists() for x in candidates):
            return {"available":True,"root":str(r),"artifacts":[str(x) for x in candidates if x.exists()]}
    return {"available":False,"root":None,"artifacts":[]}

def inspect():
    system=platform.system()
    tool={}
    if system=="Linux":
        c=cmd("clang","--version")
        tool["clang_raw"]=(c or {}).get("stdout","")
        tool["clang_version"]=ver(tool["clang_raw"])
        try:
            p=subprocess.run(["ldd","--version"],text=True,capture_output=True,timeout=10)
            tool["glibc_raw"]=(p.stdout or p.stderr).splitlines()[0]
        except Exception: tool["glibc_raw"]=""
        tool["glibc_version"]=ver(tool["glibc_raw"])
        tool["dotnet"]=cmd("dotnet","--info")
    elif system=="Windows":
        v=cmd("vswhere","-latest","-products","*",
              "-requires","Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
              "-property","installationVersion")
        tool["vs_raw"]=(v or {}).get("stdout","").strip()
        tool["vs_version"]=ver(tool["vs_raw"])
        tool["cl"]=cmd("cl")
        tool["dotnet"]=cmd("dotnet","--info")
    return {"os":system,"machine":platform.machine(),"ue":ue(),"toolchain":tool}

def evaluate(data):
    out=[]
    u=data["ue"]
    out.append({"code":"TOOLCHAIN-UE-001","area":"Unreal Engine 5.8",
                "status":"GREEN" if u["available"] else "YELLOW",
                "message":"Unreal Engine 5.8 gefunden." if u["available"] else "Unreal Engine 5.8 wurde nicht gefunden.",
                "repair":"SET_UE_ROOT_OR_INSTALL","evidence":u})
    if data["os"]=="Linux":
        c=data["toolchain"]["clang_version"]
        ok=ge(c,REQ["linux"]["compiler_min"])
        out.append({"code":"TOOLCHAIN-LINUX-CLANG-001","area":"Clang",
                    "status":"GREEN" if ok else "RED",
                    "message":"Clang erfüllt die UE-5.8-Anforderung." if ok else
                             "Clang 20.1.8 oder neuer wurde nicht nachgewiesen.",
                    "repair":"INSTALL_VERIFIED_CLANG","evidence":{"detected":c,"required":REQ["linux"]["compiler_min"]}})
        g=data["toolchain"]["glibc_version"]
        ok=ge(g,REQ["linux"]["glibc_min"])
        out.append({"code":"TOOLCHAIN-LINUX-GLIBC-001","area":"glibc",
                    "status":"GREEN" if ok else "RED",
                    "message":"glibc erfüllt das UE-5.8-Minimum." if ok else
                             "glibc 2.28 oder neuer wurde nicht nachgewiesen.",
                    "repair":"UPGRADE_SUPPORTED_OS","evidence":{"detected":g,"required":REQ["linux"]["glibc_min"]}})
    elif data["os"]=="Windows":
        v=data["toolchain"]["vs_version"]
        ok=ge(v,REQ["windows"]["visual_studio_min"])
        out.append({"code":"TOOLCHAIN-WINDOWS-VS-001","area":"Visual Studio",
                    "status":"GREEN" if ok else "RED",
                    "message":"Visual Studio erfüllt die Mindestanforderung." if ok else
                             "Visual Studio 2022 17.14 oder neuer wurde nicht nachgewiesen.",
                    "repair":"INSTALL_VS_CPP_TOOLCHAIN","evidence":{"detected":v,"required":REQ["windows"]["visual_studio_min"]}})
        out.append({"code":"TOOLCHAIN-WINDOWS-SDK-001","area":"Windows SDK",
                    "status":"YELLOW","message":"SDK-Tiefenprüfung folgt in der Windows-Implementierung.",
                    "repair":"INSPECT_WINDOWS_SDK","evidence":{"required":REQ["windows"]["windows_sdk_min"]}})
    return out
