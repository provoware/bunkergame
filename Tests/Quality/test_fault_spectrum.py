
import json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from solution_ranker import rank
from preflight_context import evaluate

def run():
    cases=[
      ("TOOLCHAIN-LINUX-CLANG-001","RED"),
      ("TOOLCHAIN-UE-001","YELLOW"),
      ("RUNTIME-CP1-BOOT-FAIL","RED"),
      ("BUILD-FAILED","RED"),
      ("DATA-SCHEMA-INVALID","YELLOW"),
      ("PIPELINE-REPORT-MISSING","YELLOW"),
      ("GIT-DIRTY","YELLOW"),
      ("TEST-ASSERTION-FAILED","YELLOW"),
    ]
    results=[]
    for code,status in cases:
        solutions=rank(code)
        results.append({
            "code":code,
            "input_status":status,
            "solutions_present":len(solutions)>=2,
            "rank_monotonic":all(
                (solutions[i].evidence*4+solutions[i].reversibility*3-solutions[i].risk*3-solutions[i].effort*2)
                >=
                (solutions[i+1].evidence*4+solutions[i+1].reversibility*3-solutions[i+1].risk*3-solutions[i+1].effort*2)
                for i in range(len(solutions)-1)
            )
        })
    # Gate semantics: use an isolated temporary rules file and the normalized schema.
    rules_path = ROOT/"Config/generated_preflight_rules.json"
    previous = rules_path.read_text(encoding="utf-8") if rules_path.exists() else None
    rules_path.write_text(json.dumps({"rules":[
        {"rule_id":"REG-A","source_code":"A","priority":"P0","observed_independent_runs":2},
        {"rule_id":"REG-B","source_code":"B","priority":"P1","observed_independent_runs":2}
    ]}), encoding="utf-8")
    r1=evaluate([{"code":"A","status":"RED"}], {})
    r2=evaluate([{"code":"A","status":"GREEN"}], {})
    results += [
      {"code":"GATE-RED","pass":r1["status"]=="RED"},
      {"code":"GATE-P1-UNOBSERVED","pass":r2["status"]=="YELLOW"}
    ]
    if previous is None:
        rules_path.unlink(missing_ok=True)
    else:
        rules_path.write_text(previous, encoding="utf-8")
    return results

if __name__=="__main__":
    out=run(); print(json.dumps(out,ensure_ascii=False,indent=2))
    raise SystemExit(0 if all(x.get("solutions_present",x.get("pass",False)) and
                               x.get("rank_monotonic",True) for x in out) else 1)
