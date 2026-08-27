from __future__ import annotations
import json, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/"Diagnostics/Reports"
TESTS=ROOT/"Diagnostics/TestRuns"
REPORTS.mkdir(parents=True,exist_ok=True)

def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def run():
    env=read_json(REPORTS/"environment_report.json",{})
    quality=read_json(REPORTS/"quality_checks.json",{})
    test=read_json(TESTS/"latest_testrun.json",{})
    payload={
        "timestamp":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status":"GREEN",
        "inputs":{
            "environment":bool(env),
            "quality":bool(quality),
            "tests":bool(test),
        },
        "metrics":{
            "tests_passed":test.get("summary",{}).get("passed",0),
            "tests_failed":test.get("summary",{}).get("failed",0),
            "formatted_files":len(quality.get("formatted_files",[])),
        },
        "environment":env,
        "quality":quality,
        "tests":test
    }
    if not env or env.get("git_ok") is False or quality.get("status")=="FAIL" or test.get("status")=="FAIL":
        payload["status"]="RED"
    elif not test or test.get("status")=="YELLOW":
        payload["status"]="YELLOW"
    (REPORTS/"result_collector.json").write_text(
        json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return payload

if __name__=="__main__":
    p=run()
    print(json.dumps(p,ensure_ascii=False,indent=2))
    raise SystemExit(0 if p["status"]=="GREEN" else 1)
