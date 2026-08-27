from __future__ import annotations
import ast, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Diagnostics/Reports"; OUT.mkdir(parents=True,exist_ok=True)
TEXT_EXT={".py",".json",".md",".txt",".ini",".cpp",".h",".bat",".sh"}
def run():
    formatted=[]; errors=[]; py_errors=[]; json_errors=[]
    for p in ROOT.rglob("*"):
        if not p.is_file() or "Diagnostics" in p.parts or p.suffix.lower() not in TEXT_EXT: continue
        try:
            old=p.read_text(encoding="utf-8")
            text=old.replace("\r\n","\n").replace("\r","\n")
            text="\n".join(line.rstrip() for line in text.split("\n")).rstrip("\n")+"\n"
            if p.suffix.lower()==".json":
                obj=json.loads(text)
                text=json.dumps(obj,ensure_ascii=False,indent=2)+"\n"
            if text!=old:
                p.write_text(text,encoding="utf-8"); formatted.append(str(p.relative_to(ROOT)))
        except Exception as e:
            errors.append({"file":str(p.relative_to(ROOT)),"error":str(e)})
    for p in ROOT.rglob("*.py"):
        if "Diagnostics" in p.parts: continue
        try: ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
        except SyntaxError as e: py_errors.append({"file":str(p.relative_to(ROOT)),"error":str(e)})
    for p in ROOT.rglob("*.json"):
        if "Diagnostics" in p.parts: continue
        try: json.loads(p.read_text(encoding="utf-8"))
        except Exception as e: json_errors.append({"file":str(p.relative_to(ROOT)),"error":str(e)})
    result={"status":"PASS" if not errors and not py_errors and not json_errors else "FAIL",
            "formatted_files":formatted,"format_errors":errors,
            "python_syntax":"PASS" if not py_errors else "FAIL","python_errors":py_errors,
            "json":"PASS" if not json_errors else "FAIL","json_errors":json_errors}
    (OUT/"quality_checks.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
