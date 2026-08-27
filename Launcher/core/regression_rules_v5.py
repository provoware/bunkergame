
from pathlib import Path
import json,time
ROOT=Path(__file__).resolve().parents[2]
REG=ROOT/"Diagnostics/Regression"; REG.mkdir(parents=True,exist_ok=True)
HISTORY=REG/"knowledge_v5.jsonl"; RULES=ROOT/"Config/generated_preflight_rules.json"
def record(run_id,issues):
    with HISTORY.open("a",encoding="utf-8") as f:
        f.write(json.dumps({"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                            "run_id":run_id,"issues":issues},ensure_ascii=False)+"\n")
def compile_rules():
    counts={}
    if HISTORY.exists():
        for line in HISTORY.read_text(encoding="utf-8").splitlines():
            try: row=json.loads(line)
            except json.JSONDecodeError: continue
            for issue in row.get("issues",[]):
                c=issue.get("code","UNKNOWN"); counts[c]=counts.get(c,0)+1
    rules=[{"rule_id":"REG-"+c,"source_code":c,"observed_runs":n,
            "action":"CHECK_BEFORE_START","severity":"PRESTART"} for c,n in counts.items() if n>=2]
    RULES.write_text(json.dumps({"generated_from":str(HISTORY),"minimum_observations":2,
                                 "rules":rules},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    insights=["# Regression Insights","",f"Analysierte Läufe: {sum(1 for _ in HISTORY.open(encoding='utf-8')) if HISTORY.exists() else 0}","",
              "## Dauerhafte Preflight-Regeln"]
    if rules:
        insights += [f"- {r['rule_id']}: {r['observed_runs']} Beobachtungen → Vorabprüfung." for r in rules]
    else:
        insights.append("- Noch keine Regel erreicht die Schwelle von zwei Beobachtungen.")
    (REG/"REGRESSION_INSIGHTS.md").write_text("\n".join(insights)+"\n",encoding="utf-8")
    return rules
