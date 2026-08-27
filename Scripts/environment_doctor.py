from __future__ import annotations
import json, os, platform, shutil, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Diagnostics/Reports"
OUT.mkdir(parents=True,exist_ok=True)

def find_ue():
    candidates=[]
    if os.environ.get("UE_ROOT"): candidates.append(Path(os.environ["UE_ROOT"]))
    candidates += [
        Path(r"C:\Program Files\Epic Games\UE_5.8"),
        Path(r"C:\Program Files\Epic Games\UE_5.7"),
        Path("/opt/UnrealEngine"),
        Path.home()/".local/UnrealEngine",
    ]
    for p in candidates:
        if (p/"Engine").exists():
            return str(p)
    return None

def run():
    ue=find_ue()
    editor=None
    buildtool=None
    if ue:
        for rel in [
            "Engine/Binaries/Win64/UnrealEditor-Cmd.exe",
            "Engine/Binaries/Linux/UnrealEditor-Cmd",
            "Engine/Binaries/Mac/UnrealEditor-Cmd"
        ]:
            p=Path(ue)/rel
            if p.exists(): editor=str(p); break
        for rel in [
            "Engine/Binaries/DotNET/UnrealBuildTool.exe",
            "Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll"
        ]:
            p=Path(ue)/rel
            if p.exists(): buildtool=str(p); break
    result={
        "platform":platform.platform(),
        "python":sys.executable,
        "git":shutil.which("git"),
        "ue_root":ue,
        "unreal_editor_cmd":editor,
        "unreal_build_tool":buildtool,
        "python_ok":True,
        "git_ok":bool(shutil.which("git")),
        "unreal_available":bool(editor and buildtool),
    }
    (OUT/"environment_report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
