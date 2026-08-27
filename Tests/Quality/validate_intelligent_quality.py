
import ast, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
errors=[]
for p in ROOT.rglob("*.py"):
    try: ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
    except SyntaxError as e: errors.append(str(e))

tests=[
 ("fault_spectrum",ROOT/"Tests/Quality/test_fault_spectrum.py"),
 ("regression_learning",ROOT/"Tests/Quality/test_regression_learning.py"),
 ("regression_attribution",ROOT/"Tests/test_regression_attribution.py"),
]
results={}
for name,path in tests:
    p=subprocess.run([sys.executable,str(path)],cwd=ROOT,text=True,capture_output=True,timeout=90)
    results[name]={"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}

a=subprocess.run([sys.executable,str(ROOT/"Launcher/core/intelligent_autostart.py"),"--quiet-json"],
                cwd=ROOT,text=True,capture_output=True,timeout=90)
results["autostart"]={"returncode":a.returncode,"stdout":a.stdout,"stderr":a.stderr}

report_dir=ROOT/"Diagnostics/Gates/intelligent_autostart_results"
reports=sorted(report_dir.glob("*.json"), key=lambda p:p.stat().st_mtime) if report_dir.exists() else []
machine_data={}
machine_ok=False
if reports:
    machine=reports[-1]
    try:
        machine_data=json.loads(machine.read_text(encoding="utf-8"))
        machine_ok=True
    except Exception as e:
        errors.append(f"machine report parse: {e}")

result=machine_data.get("result",{})
validation={
 "python_syntax":"PASS" if not errors else "FAIL",
 "fault_spectrum":"PASS" if results["fault_spectrum"]["returncode"]==0 else "FAIL",
 "learning_test":"PASS" if results["regression_learning"]["returncode"]==0 else "FAIL",
 "attribution_test":"PASS" if results["regression_attribution"]["returncode"]==0 else "FAIL",
 "autostart_process":"PASS" if results["autostart"]["returncode"]==0 else "FAIL",
 "machine_report":"PASS" if machine_ok else "FAIL",
 "attribution_in_autostart":bool(result.get("context")),
 "solutions_in_autostart":any(bool(f.get("solutions")) for f in result.get("failures",[])),
 "runtime_policy":result.get("runtime_policy"),
 "current_overall":machine_data.get("overall"),
 "runtime_actually_executed":False,
 "no_fake_success":result.get("runtime_policy")!="RUNTIME_EXECUTED",
}
(ROOT/"Diagnostics/Gates/FINAL_VALIDATION.json").write_text(
    json.dumps(validation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(validation,ensure_ascii=False,indent=2))
raise SystemExit(0 if all(v=="PASS" or v is True for k,v in validation.items()
                           if k not in {"runtime_policy","current_overall","runtime_actually_executed"}) else 1)
