
from __future__ import annotations
from pathlib import Path
import os, platform, subprocess, hashlib, json

ROOT=Path(__file__).resolve().parents[2]

def cmd(*args):
    try:
        p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=15)
        return p.stdout.strip(),p.stderr.strip(),p.returncode
    except Exception as e:
        return "",str(e),-1

def git_context():
    branch,_,rb=cmd("git","rev-parse","--abbrev-ref","HEAD")
    commit,_,rc=cmd("git","rev-parse","HEAD")
    status,_,rs=cmd("git","status","--porcelain")
    return {
        "repository_present": rb==0 and rc==0,
        "branch": branch if rb==0 else None,
        "commit": commit if rc==0 else None,
        "working_tree_dirty": bool(status.strip()) if rs==0 else None,
    }

def project_context():
    p=ROOT/"BunkerBeats.uproject"
    return {
        "path":str(p),
        "exists":p.exists(),
        "size":p.stat().st_size if p.exists() else None,
        "mtime_ns":p.stat().st_mtime_ns if p.exists() else None,
    }

def runtime_context():
    keys=["UE_ROOT","UE_5_8_ROOT","UNREAL_ENGINE_ROOT","UNREAL_ROOT",
          "CI","GITHUB_ACTIONS","BUILD_NUMBER","BUILD_ID","RUN_ID"]
    return {k:os.environ.get(k) for k in keys if os.environ.get(k)}

def collect(toolchain_snapshot=None):
    ctx={
        "timestamp_utc":__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "platform":platform.platform(),
        "os":platform.system(),
        "release":platform.release(),
        "machine":platform.machine(),
        "python":platform.python_version(),
        "git":git_context(),
        "project":project_context(),
        "runtime_environment":runtime_context(),
    }
    if toolchain_snapshot is not None:
        raw=json.dumps(toolchain_snapshot,sort_keys=True,ensure_ascii=False).encode()
        ctx["toolchain_snapshot_sha256"]=hashlib.sha256(raw).hexdigest()
    return ctx
