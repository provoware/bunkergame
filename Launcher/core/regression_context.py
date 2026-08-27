
from __future__ import annotations
from pathlib import Path
import json, time

ROOT=Path(__file__).resolve().parents[2]
REG=ROOT/"Diagnostics/Regression"; REG.mkdir(parents=True,exist_ok=True)
HISTORY=REG/"knowledge_v6.jsonl"
RULES=ROOT/"Config/generated_preflight_rules.json"
PRIORITY={
 "RUNTIME-CP1-CRASH":"P0","RUNTIME-CP1-BOOT-FAIL":"P0","BUILD-FAILED":"P0",
 "TOOLCHAIN-UE-001":"P1","TOOLCHAIN-LINUX-CLANG-001":"P1",
 "TOOLCHAIN-LINUX-GLIBC-001":"P1","TOOLCHAIN-WINDOWS-VS-001":"P1",
 "TOOLCHAIN-WINDOWS-SDK-001":"P1"
}

def record(run_id,issues,context):
    row={
        "schema":"regression.v6",
        "run_id":run_id,
        "timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "context":context,
        "issues":issues
    }
    with HISTORY.open("a",encoding="utf-8") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row

def compile_rules(min_runs=2):
    groups={}
    if HISTORY.exists():
        for line in HISTORY.read_text(encoding="utf-8").splitlines():
            try: row=json.loads(line)
            except json.JSONDecodeError: continue
            for issue in row.get("issues",[]):
                code=issue.get("code","UNKNOWN")
                ctx=row.get("context",{})
                # Independent observations are run IDs; context is retained for attribution.
                groups.setdefault(code,{"runs":set(),"platforms":set(),"branches":set(),"commits":set()})
                g=groups[code]; g["runs"].add(row.get("run_id"))
                if ctx.get("platform"): g["platforms"].add(ctx["platform"])
                git=ctx.get("git",{})
                if git.get("branch"): g["branches"].add(git["branch"])
                if git.get("commit"): g["commits"].add(git["commit"])

    rules=[]
    for code,g in groups.items():
        runs={x for x in g["runs"] if x}
        if len(runs)<min_runs: continue
        pr=PRIORITY.get(code,"P2")
        rules.append({
            "rule_id":"REG-"+code,
            "source_code":code,
            "priority":pr,
            "observed_independent_runs":len(runs),
            "platforms":sorted(g["platforms"]),
            "branches":sorted(g["branches"]),
            "commits":sorted(g["commits"]),
            "gate_action":"BLOCK_ALL" if pr=="P0" else "BLOCK_RUNTIME" if pr=="P1" else "WARN",
            "evidence_policy":"REQUIRE_FRESH_EVIDENCE"
        })

    rules.sort(key=lambda r:(r["priority"],r["rule_id"]))
    RULES.write_text(json.dumps({
        "schema":"preflight.rules.v6",
        "generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "minimum_independent_runs":min_runs,
        "rules":rules
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    md=["# Regression Insights v6","",
        f"Analysierte historische Einträge: {sum(1 for _ in HISTORY.open(encoding='utf-8')) if HISTORY.exists() else 0}",
        "",
        "## Persistente P0/P1-Preflight-Gates"]
    if not rules:
        md.append("- Keine Regel erreicht die Schwelle von zwei unabhängigen Läufen.")
    else:
        for r in rules:
            md.append(
                f"- **{r['rule_id']}** — {r['priority']} — {r['observed_independent_runs']} unabhängige Läufe — "
                f"Plattformen: {', '.join(r['platforms']) or 'unbekannt'} — "
                f"Gate: `{r['gate_action']}`"
            )
    md += [
        "",
        "## Attributionsregel",
        "Zeitstempel, Branch, Commit, Plattform und Toolchain-Snapshot bleiben Bestandteil jedes Laufnachweises.",
        "Dadurch kann ein wiederkehrender Fehler von einem einzelnen Code-Change unterschieden werden."
    ]
    (REG/"REGRESSION_INSIGHTS.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    return rules
