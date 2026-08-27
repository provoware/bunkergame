
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from preflight_clean import evaluate

def main():
    p=ROOT/"Config/generated_preflight_rules.json"
    p.write_text(json.dumps({"rules":[
      {"rule_id":"REG-A","source_code":"A","priority":"P0","observed_runs":2},
      {"rule_id":"REG-B","source_code":"B","priority":"P1","observed_runs":2}
    ]}),encoding="utf-8")
    a=evaluate([{"code":"A","status":"RED"},{"code":"B","status":"GREEN"}])
    b=evaluate([{"code":"A","status":"GREEN"},{"code":"B","status":"YELLOW"}])
    c=evaluate([{"code":"A","status":"GREEN"},{"code":"B","status":"GREEN"}])
    r=[a["status"]=="RED",b["status"]=="YELLOW",c["status"]=="GREEN"]
    print(json.dumps({"P0_RED":r[0],"P1_YELLOW":r[1],"ALL_GREEN":r[2]},indent=2))
    return 0 if all(r) else 1
if __name__=="__main__": raise SystemExit(main())
