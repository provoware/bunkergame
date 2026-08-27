
from __future__ import annotations
from pathlib import Path
import json,time,hashlib

ROOT=Path(__file__).resolve().parents[2]
KB=ROOT/"Diagnostics/Knowledge"; KB.mkdir(parents=True,exist_ok=True)
HISTORY=KB/"knowledge.jsonl"
INSIGHTS=KB/"KNOWLEDGE_INSIGHTS.md"

def fingerprint(code,context):
    branch=context.get("git",{}).get("branch")
    platform=context.get("local",{}).get("platform")
    return hashlib.sha256(f"{code}|{branch}|{platform}".encode()).hexdigest()[:16]

def record(entry):
    with HISTORY.open("a",encoding="utf-8") as f:
        f.write(json.dumps(entry,ensure_ascii=False)+"\n")
    return entry

def learn():
    rows=[]
    if HISTORY.exists():
        for line in HISTORY.read_text(encoding="utf-8").splitlines():
            try: rows.append(json.loads(line))
            except json.JSONDecodeError: continue
    by_code={}
    for r in rows:
        for failure in r.get("failures",[]):
            code=failure.get("code","UNKNOWN")
            b=by_code.setdefault(code,{"runs":set(),"solutions":{}, "last":None})
            b["runs"].add(r.get("run_id"))
            b["last"]=r
            for sol in failure.get("solutions",[]):
                sid=sol.get("id")
                if sid:
                    b["solutions"].setdefault(sid,{"attempts":0,"success":0})
                    b["solutions"][sid]["attempts"]+=1
                    if sol.get("outcome")=="SUCCESS": b["solutions"][sid]["success"]+=1

    rules=[]
    insights=["# Knowledge Insights","",
              "Die Wissensbasis wird aus realen Laufnachweisen erzeugt.",""]
    for code,b in sorted(by_code.items()):
        run_count=len({r for r in b["runs"] if r})
        if run_count>=2:
            priority="P0" if code in {"BUILD-FAILED","RUNTIME-CP1-CRASH","RUNTIME-CP1-BOOT-FAIL"} else (
                      "P1" if code.startswith("TOOLCHAIN-") or code.startswith("ENV-") else "P2")
            rules.append({
                "rule_id":"KNOW-"+code,
                "source_code":code,
                "priority":priority,
                "observed_runs":run_count,
                "action":"CHECK_BEFORE_START",
                "learned":"true"
            })
            insights.append(
                f"- **{code}**: {run_count} unabhängige Läufe → {priority}-Preflight; "
                f"Lösungsversuche: {len(b['solutions'])}"
            )
    (ROOT/"Config/learned_preflight_rules.json").write_text(
        json.dumps({"schema":"preflight.learned.v1","generated_at":time.time(),"rules":rules},
                   ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    insights += [
        "",
        "## Präventionsregel",
        "Jeder wiederkehrende Fehler erzeugt eine dauerhafte Preflight-Erkennung.",
        "Eine Lösung zählt erst als erfolgreich, wenn nach ihrer Anwendung eine relevante Re-Validation bestanden wurde."
    ]
    INSIGHTS.write_text("\n".join(insights)+"\n",encoding="utf-8")
    return rules


def stats_json():
    """Return solution history with string fields so it is always JSON-safe."""
    out=[]
    for (failure_code, solution_id), data in stats().items():
        out.append({
            "failure_code":failure_code,
            "solution_id":solution_id,
            **data,
        })
    out.sort(key=lambda x:(x["failure_code"],x["solution_id"]))
    return out
