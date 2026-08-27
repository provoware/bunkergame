
from __future__ import annotations
from pathlib import Path
import os,platform,subprocess,json,hashlib,time
ROOT=Path(__file__).resolve().parents[2]

def git(*args):
    try:
        p=subprocess.run(["git",*args],cwd=ROOT,text=True,capture_output=True,timeout=20)
        return p.returncode,p.stdout.strip(),p.stderr.strip()
    except Exception as e:return 1,"",str(e)

def context():
    rc,b,_=git("rev-parse","--abbrev-ref","HEAD")
    rc2,c,_=git("rev-parse","HEAD")
    rc3,s,_=git("status","--porcelain")
    return {
        "local":{"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
                 "platform":platform.platform(),"os":platform.system(),
                 "release":platform.release(),"machine":platform.machine(),
                 "python":platform.python_version(),
                 "env":{k:os.environ.get(k) for k in ["UE_ROOT","CI","BUILD_ID","BUILD_NUMBER"] if os.environ.get(k)}},
        "git":{"available":rc==0 and rc2==0,
               "branch":b if rc==0 else None,"commit":c if rc2==0 else None,
               "dirty":bool(s) if rc3==0 else None}
    }

def diff_context(base_commit="HEAD~1"):
    rc,body,err=git("diff","--name-status",base_commit,"HEAD")
    files=[]
    if rc==0:
        for line in body.splitlines():
            parts=line.split("\t")
            if len(parts)>=2: files.append({"status":parts[0],"path":parts[-1]})
    rc2,num,_=git("diff","--numstat",base_commit,"HEAD")
    by={}
    if rc2==0:
        for line in num.splitlines():
            p=line.split("\t")
            if len(p)==3:
                by[p[2]]={"additions":int(p[0]) if p[0].isdigit() else 0,
                           "deletions":int(p[1]) if p[1].isdigit() else 0}
    return {"available":rc==0,"base_commit":base_commit,"files":files,"stats":by}

def build_context(base_commit=None):
    c=context()
    base=base_commit or "HEAD~1"
    d=diff_context(base)
    c["diff"]=d
    raw=json.dumps(c,sort_keys=True,ensure_ascii=False).encode()
    c["context_sha256"]=hashlib.sha256(raw).hexdigest()
    return c
