from __future__ import annotations
import argparse, importlib.util, json, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/"Diagnostics/Reports"
REPORTS.mkdir(parents=True,exist_ok=True)

def load(script):
    p=ROOT/"Scripts"/script
    if not p.exists():
        return {"script":script,"execution":"BLOCKED","reason":"Script missing"}
    spec=importlib.util.spec_from_file_location(
        f"bb_{p.stem}_{time.time_ns()}",p
    )
    if spec is None or spec.loader is None:
        return {"script":script,"execution":"FAIL","reason":"Module load failed"}
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn=getattr(mod,"run",None)
    if not callable(fn):
        return {"script":script,"execution":"FAIL","reason":"No run() function"}
    try:
        result=fn()
        domain=result.get("status") if isinstance(result,dict) else None
        return {"script":script,"execution":"PASS","domain_status":domain,"result":result}
    except Exception as exc:
        return {"script":script,"execution":"FAIL",
                "error":{"type":type(exc).__name__,"message":str(exc)}}

def unreal_stage(args):
    cmd=[sys.executable,str(ROOT/"Scripts/unreal_runner.py")]
    if args.unreal_build: cmd.append("--build")
    if args.unreal_pie:
        cmd.append("--pie")
        if args.automation_filter:
            cmd += ["--automation-filter",args.automation_filter]
    if args.unreal_package: cmd.append("--package")
    proc=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    try:
        result=json.loads(proc.stdout)
    except Exception:
        result={"status":"RED","raw_stdout":proc.stdout,"stderr":proc.stderr}
    return {
        "script":"unreal_runner.py",
        "execution":"PASS" if proc.returncode in (0,3) else "FAIL",
        "domain_status":result.get("status","RED"),
        "returncode":proc.returncode,
        "result":result,
        "stderr":proc.stderr[-5000:]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--format",action="store_true")
    ap.add_argument("--unreal-build",action="store_true")
    ap.add_argument("--unreal-pie",action="store_true")
    ap.add_argument("--unreal-package",action="store_true")
    ap.add_argument("--automation-filter",default="")
    args=ap.parse_args()

    stages=[]
    # Use the files actually present in the project.
    stages.append(load("environment_doctor.py"))
    if args.format:
        stages.append(load("quality_checks.py"))
    # Re-check after formatting/quality normalization.
    stages.append(load("environment_doctor.py"))
    stages.append(load("test_runner.py"))
    stages.append(load("result_collector.py"))

    # Stop before Unreal if project-side gates already failed.
    if any(s.get("execution")=="FAIL" or s.get("domain_status")=="RED" for s in stages):
        return finalize(stages)

    if args.unreal_build or args.unreal_pie or args.unreal_package:
        stages.append(unreal_stage(args))

    return finalize(stages)

def finalize(stages):
    red=any(s.get("execution")=="FAIL" or s.get("domain_status")=="RED" for s in stages)
    yellow=any(s.get("execution")=="BLOCKED" or s.get("domain_status") in ("YELLOW","BLOCKED") for s in stages)
    overall="RED" if red else ("YELLOW" if yellow else "GREEN")
    payload={
        "timestamp":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "overall":overall,
        "stages":stages,
        "semantic_rule":"execution success is distinct from domain/gate success"
    }
    (REPORTS/"orchestrator_report.json").write_text(
        json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,ensure_ascii=False,indent=2))
    return 0 if overall=="GREEN" else 1

if __name__=="__main__":
    raise SystemExit(main())
