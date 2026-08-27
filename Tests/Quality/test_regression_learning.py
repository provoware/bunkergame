
import json,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from knowledge_store import record,learn

def main():
    run1=str(uuid.uuid4()); run2=str(uuid.uuid4())
    ctx={"local":{"timestamp_utc":"2026-08-27T00:00:00Z","platform":"Linux"},
         "git":{"branch":"main","commit":"aaa"}}
    record({"run_id":run1,"context":ctx,"failures":[{"code":"TEST-REPEAT","status":"YELLOW","solutions":[{"id":"GENERAL_TEST","outcome":"SUCCESS"}]}]})
    record({"run_id":run2,"context":ctx,"failures":[{"code":"TEST-REPEAT","status":"YELLOW","solutions":[{"id":"GENERAL_TEST","outcome":"SUCCESS"}]}]})
    rules=learn()
    ok=any(r["source_code"]=="TEST-REPEAT" for r in rules)
    print(json.dumps({"promoted_rule":ok,"rule_count":len(rules)},ensure_ascii=False,indent=2))
    raise SystemExit(0 if ok else 1)

if __name__=="__main__": main()
