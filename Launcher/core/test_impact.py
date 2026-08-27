
from __future__ import annotations
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[2]

RULES={
    "BunkerBeats.Smoke": ["Source/","Tests/Smoke/","Config/DefaultEngine.ini","Config/cp1_smoke_manifest.json"],
    "CP1": ["Source/","Tests/Smoke/","Config/","Build/"],
    "Core": ["Core/","Data/","Tests/"],
    "Toolchain": ["Launcher/","Scripts/","Config/"],
}

def normalized(p): return p.replace("\\","/").lstrip("./")

def paths_for_test(test_id):
    return RULES.get(test_id,["Source/","Tests/"])

def relevance(test_id,changed_path):
    cp=normalized(changed_path)
    for prefix in paths_for_test(test_id):
        if cp.startswith(prefix):
            return "DIRECT"
    # generic semantic path hints
    if "Smoke" in test_id and ("Tests/Smoke" in cp or "DefaultEngine.ini" in cp):
        return "DIRECT"
    return "INDIRECT"

def map_tests(changed_files,test_ids):
    out=[]
    for tid in test_ids:
        direct=[f["path"] for f in changed_files if relevance(tid,f["path"])=="DIRECT"]
        out.append({"test_id":tid,"directly_impacted_files":direct,
                    "impact":"DIRECT" if direct else "INDIRECT"})
    return out

def associate_failure(failure,changed_files,test_impacts):
    text=(failure.get("message","")+" "+failure.get("code","")).lower()
    candidates=[]
    for f in changed_files:
        p=normalized(f["path"])
        score=0
        if any(part.lower() in text for part in Path(p).parts if len(part)>3):
            score+=30
        if p.startswith("Source/"): score+=20
        if "Tests/Smoke" in p and "smoke" in text: score+=35
        if "toolchain" in text and ("Launcher/" in p or "Scripts/" in p): score+=35
        for t in test_impacts:
            if p in t["directly_impacted_files"]:
                score+=15
        candidates.append({"path":p,"score":score})
    candidates.sort(key=lambda x:-x["score"])
    return candidates[:10]
