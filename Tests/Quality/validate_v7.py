
import ast, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

syntax_errors=[]
for p in ROOT.rglob("*.py"):
    try: ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
    except SyntaxError as e: syntax_errors.append(str(e))

tests=[
("fault_spectrum",ROOT/"Tests/Quality/test_fault_spectrum.py"),
("learning",ROOT/"Tests/Quality/test_regression_learning.py"),
("attribution",ROOT/"Tests/test_regression_attribution.py"),
]
results={}
for name,path in tests:
    p=subprocess.run([sys.executable,"-u",str(path)],cwd=ROOT,text=True,capture_output=True,timeout=90)
    results[name]={"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}

p=subprocess.run([sys.executable,"-u",str(ROOT/"Launcher/core/intelligent_autostart.py"),"--quiet-json"],
                cwd=ROOT,text=True,capture_output=True,timeout=90)
results["autostart"]={"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}

reports=sorted((ROOT/"Diagnostics/Gates/intelligent_autostart_results").glob("*.json"),
               key=lambda x:x.stat().st_mtime)
machine={}
if reports:
    machine=json.loads(reports[-1].read_text(encoding="utf-8"))

result=machine.get("result",{})
validation={
"status":"PASS" if (
    not syntax_errors and all(v["returncode"]==0 for v in results.values())
    and bool(result.get("context"))
    and any(bool(f.get("solutions")) for f in result.get("failures",[]))
) else "FAIL",
"python_syntax":"PASS" if not syntax_errors else "FAIL",
"fault_spectrum":"PASS" if results["fault_spectrum"]["returncode"]==0 else "FAIL",
"learning":"PASS" if results["learning"]["returncode"]==0 else "FAIL",
"attribution":"PASS" if results["attribution"]["returncode"]==0 else "FAIL",
"autostart":"PASS" if results["autostart"]["returncode"]==0 else "FAIL",
"attribution_in_autostart":bool(result.get("context")),
"solution_options_in_autostart":any(bool(f.get("solutions")) for f in result.get("failures",[])),
"runtime_policy":result.get("runtime_policy"),
"current_overall":machine.get("overall"),
"runtime_actually_executed":False,
"no_fake_success":result.get("runtime_policy")!="RUNTIME_EXECUTED",
"machine_reports":len(reports)
}
(ROOT/"Diagnostics/Gates/FINAL_VALIDATION.json").write_text(json.dumps(validation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(validation,ensure_ascii=False,indent=2))
raise SystemExit(0 if validation["status"]=="PASS" else 1)
