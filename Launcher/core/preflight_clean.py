
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/"Config/generated_preflight_rules.json"
def evaluate(findings):
    rules=json.loads(R.read_text(encoding="utf-8")).get("rules",[]) if R.exists() else []
    fmap={f["code"]:f for f in findings}
    blocking=[]; warn=[]; passed=[]
    for r in rules:
        cur=fmap.get(r["source_code"]); ok=cur is not None and cur["status"]=="GREEN"
        item={"rule_id":r["rule_id"],"source_code":r["source_code"],"priority":r["priority"],
              "observed_runs":r["observed_runs"],"current_status":cur["status"] if cur else "NOT_OBSERVED","passed":ok}
        (passed if ok else blocking if r["priority"]=="P0" else warn).append(item)
    return {"status":"RED" if blocking else "YELLOW" if warn else "GREEN",
            "blocking":blocking,"warnings":warn,"passed":passed}
