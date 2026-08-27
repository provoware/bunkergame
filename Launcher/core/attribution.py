
from __future__ import annotations
from pathlib import Path
import os, platform, subprocess, json, hashlib, re, time

ROOT=Path(__file__).resolve().parents[2]

def run_git(args):
    try:
        p=subprocess.run(["git",*args],cwd=ROOT,text=True,capture_output=True,timeout=20)
        return p.returncode,p.stdout.strip(),p.stderr.strip()
    except Exception as exc:
        return 1,"",str(exc)

def git_context():
    rc,b,err=run_git(["rev-parse","--abbrev-ref","HEAD"])
    rc2,c,err2=run_git(["rev-parse","HEAD"])
    rc3,status,_=run_git(["status","--porcelain"])
    return {
        "available":rc==0 and rc2==0,
        "branch":b if rc==0 else None,
        "commit":c if rc2==0 else None,
        "dirty":bool(status) if rc3==0 else None,
        "git_error":err or err2 or None,
    }

def commit_meta(commit="HEAD"):
    rc,body,err=run_git(["show","-s","--format=%H%x1f%an%x1f%ae%x1f%aI%x1f%s",commit])
    if rc!=0:return None
    parts=body.split("\x1f")
    if len(parts)!=5:return None
    return {"commit":parts[0],"author":parts[1],"author_email":parts[2],
            "author_time":parts[3],"subject":parts[4]}

def changed_files(base_commit, head_commit="HEAD"):
    rc,body,err=run_git(["diff","--name-status",base_commit,head_commit])
    if rc!=0:return {"available":False,"error":err,"files":[]}
    files=[]
    for line in body.splitlines():
        parts=line.split("\t")
        if len(parts)>=2:
            files.append({"status":parts[0],"path":parts[-1]})
    return {"available":True,"files":files}

def diff_stats(base_commit,head_commit="HEAD"):
    rc,body,err=run_git(["diff","--numstat",base_commit,head_commit])
    if rc!=0:return {"available":False,"error":err}
    total_add=total_del=0
    by_file={}
    for line in body.splitlines():
        parts=line.split("\t")
        if len(parts)!=3:continue
        a,d,p=parts
        aa=int(a) if a.isdigit() else 0
        dd=int(d) if d.isdigit() else 0
        total_add+=aa; total_del+=dd
        by_file[p]={"additions":aa,"deletions":dd}
    return {"available":True,"additions":total_add,"deletions":total_del,"by_file":by_file}

def patch_hash(base_commit,head_commit="HEAD"):
    rc,body,err=run_git(["diff","--binary",base_commit,head_commit])
    if rc!=0:return None
    return hashlib.sha256(body.encode()).hexdigest()

def local_context():
    return {
        "timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "platform":platform.platform(),
        "os":platform.system(),
        "release":platform.release(),
        "machine":platform.machine(),
        "python":platform.python_version(),
        "cwd":str(ROOT),
        "env":{k:os.environ.get(k) for k in
               ["UE_ROOT","CI","GITHUB_ACTIONS","BUILD_ID","BUILD_NUMBER"] if os.environ.get(k)}
    }

def collect(base_commit=None):
    git=git_context()
    base=base_commit
    if base is None:
        _,merge_base,_=run_git(["merge-base","HEAD","HEAD~1"])
        base=merge_base if merge_base else "HEAD~1"
    return {
        "local":local_context(),
        "git":git,
        "head_commit_meta":commit_meta("HEAD") if git["available"] else None,
        "base_commit":base,
        "base_commit_meta":commit_meta(base) if git["available"] else None,
        "changed_files":changed_files(base) if git["available"] else {"available":False,"files":[]},
        "diff_stats":diff_stats(base) if git["available"] else {"available":False},
        "patch_sha256":patch_hash(base) if git["available"] else None,
    }
