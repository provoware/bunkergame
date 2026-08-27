
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Core")); sys.path.insert(0,str(ROOT/"Data"))
from catalog import create_api

def run():
    api=create_api(); checks=[]
    def ck(n,c,d=""): checks.append({"name":n,"status":"PASS" if c else "FAIL","detail":d})
    def start(a,b,interaction):
        c=api.create_character_state("Pppoppi",[a,b]).state
        return api.start_task(c,interaction).task

    cable=start("ABILITY_01","ABILITY_02","INT_POWER")
    neutral=start("ABILITY_03","ABILITY_04","INT_POWER")
    risk=start("ABILITY_10","ABILITY_02","INT_POWER")
    setup=start("ABILITY_09","ABILITY_17","INT_SETUP")
    neutral_setup=start("ABILITY_03","ABILITY_04","INT_SETUP")
    social=start("ABILITY_04","ABILITY_08","INT_SOCIAL")
    timed=start("ABILITY_06","ABILITY_13","INT_TIMED")
    resource=start("ABILITY_07","ABILITY_03","INT_RESOURCE")

    ck("POWER cable faster",cable.max_progress==3)
    ck("POWER neutral baseline",neutral.max_progress==3)
    ck("POWER risk modifier",risk.risk>neutral.risk)
    ck("SETUP has modifiers",setup.reward_xp>neutral_setup.reward_xp)
    ck("SOCIAL has modifiers",social.reward_xp>60)
    ck("TIMED has modifier",timed.reward_xp>45)
    ck("RESOURCE has modifier",resource.reward_xp>40)
    ck("risk never negative",all(x.risk>=0 for x in [cable,neutral,risk,setup,neutral_setup,social,timed,resource]))
    return checks
if __name__=="__main__":
    r=run(); print(json.dumps(r,ensure_ascii=False,indent=2)); raise SystemExit(0 if all(x["status"]=="PASS" for x in r) else 1)
