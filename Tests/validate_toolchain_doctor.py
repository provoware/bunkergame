
from pathlib import Path
import ast,json,sys
ROOT=Path(__file__).resolve().parents[1]
for p in ROOT.rglob("*.py"):
    ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
sys.path.insert(0,str(ROOT/"Launcher/core"))
from assistant_v5 import ToolchainAssistant
logs=[]
res=ToolchainAssistant(console=logs.append).run(repair=True)
checks={
 "assistant_execution":True,
 "report_exists":Path(res["report"]).exists(),
 "event_log_exists":(ROOT/"Diagnostics/Events/events.jsonl").exists(),
 "regression_history":(ROOT/"Diagnostics/Regression/knowledge_v5.jsonl").exists(),
 "preflight_rules":(ROOT/"Config/generated_preflight_rules.json").exists(),
 "regression_insights":(ROOT/"Diagnostics/Regression/REGRESSION_INSIGHTS.md").exists(),
 "current_status_is_explicit":res["summary"]["overall"] in {"GREEN","YELLOW","RED"},
}
print(json.dumps({"checks":checks,"result":res["summary"],"logs":logs},ensure_ascii=False,indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
