
import itertools, json, sys, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Core")); sys.path.insert(0,str(ROOT/"Data"))
from catalog import create_api,ABILITIES,TASKS
from multitask_api import ResultCode

def run():
    api=create_api(); checks=[]; records=[]
    def ck(n,c,d=""): checks.append({"name":n,"status":"PASS" if c else "FAIL","detail":d})

    ck("20 abilities",len(ABILITIES)==20)
    ck("6 task archetypes",len(TASKS)==6)
    combos=list(itertools.combinations(ABILITIES,2))
    ck("190 combinations",len(combos)==190)

    # Verify every combination can enter every low-level task in the prototype.
    for idx,(a,b) in enumerate(combos):
        state=api.create_character_state("Pppoppi",[a,b]).state
        for tid,task in TASKS.items():
            s=api.start_task(state,task.interaction_id)
            if s.code is not ResultCode.OK:
                checks.append({"name":f"start {idx}/{tid}","status":"FAIL","detail":s.reason})
                continue
            first=api.advance_task(state,s.task)
            records.append({
                "combo_index":idx,"ability_a":a,"ability_b":b,
                "task_id":tid,"initial_risk":s.task.risk,
                "reward_xp":s.task.reward_xp,
                "first_progress":first.task.progress,
                "max_progress":first.task.max_progress
            })

    ck("1140 scenario starts",len(records)==1140,str(len(records)))
    ck("non-negative risk",all(r["initial_risk"]>=0 for r in records))
    ck("positive reward",all(r["reward_xp"]>0 for r in records))
    ck("progress bounded",all(0<=r["first_progress"]<=r["max_progress"] for r in records))

    return checks,records

if __name__=="__main__":
    c,r=run()
    print(json.dumps({"checks":c,"scenario_records":len(r)},ensure_ascii=False,indent=2))
    raise SystemExit(0 if all(x["status"]=="PASS" for x in c) else 1)
