from pathlib import Path
import json, shutil, sys

ROOT=Path(__file__).resolve().parents[1]
required=[
"Scripts/orchestrator.py",
"Scripts/environment_doctor.py",
"Scripts/quality_checks.py",
"Scripts/test_runner.py",
"Scripts/result_collector.py",
"Scripts/unreal_runner.py",
"BunkerBeats.uproject",
"Config/cp1_smoke_manifest.json"
]
rows=[]
for rel in required:
    rows.append({"path":rel,"present":(ROOT/rel).exists()})
print(json.dumps({"all_present":all(x["present"] for x in rows),"files":rows},ensure_ascii=False,indent=2))
raise SystemExit(0 if all(x["present"] for x in rows) else 1)
