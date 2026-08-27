
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from test_impact import map_tests,associate_failure
from regression_attribution import record_failure
from attribution import collect

def main():
    changed=[
      {"status":"M","path":"Source/BunkerBeats/Character/Avatar.cpp"},
      {"status":"M","path":"Tests/Smoke/BunkerBeatsSmokeTests.cpp"},
      {"status":"M","path":"Launcher/core/runtime_clean.py"},
    ]
    impacts=map_tests(changed,["BunkerBeats.Smoke","CP1"])
    a=associate_failure({"code":"RUNTIME-CP1-BOOT-FAIL","message":"Smoke boot failed in Avatar"},changed,impacts)
    checks={
      "smoke_direct":impacts[0]["impact"]=="DIRECT",
      "cp1_direct":impacts[1]["impact"]=="DIRECT",
      "ranked_candidates":len(a)>=1,
      "confidence_is_bounded":all(x["score"]>=0 for x in a)
    }
    print(json.dumps(checks,ensure_ascii=False,indent=2))
    return 0 if all(checks.values()) else 1
if __name__=="__main__":raise SystemExit(main())
