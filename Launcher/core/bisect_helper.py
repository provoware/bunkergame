
from __future__ import annotations
from pathlib import Path
import json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]

def git(args):
    p=subprocess.run(["git",*args],cwd=ROOT,text=True,capture_output=True,timeout=30)
    return p.returncode,p.stdout.strip(),p.stderr.strip()

def plan(good,bad,test_command):
    rc,out,err=git(["rev-list","--ancestry-path",f"{good}..{bad}","--reverse"])
    commits=out.splitlines() if rc==0 else []
    return {
        "good":good,"bad":bad,
        "candidate_commit_count":len(commits),
        "test_command":test_command,
        "automation":"git bisect run",
        "safe_policy":"PLAN_ONLY",
        "note":"Bisect changes repository state; this helper never starts or resets a bisect session automatically."
    }
