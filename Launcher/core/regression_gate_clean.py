
from pathlib import Path
import json,time
ROOT=Path(__file__).resolve().parents[2]
REG=ROOT/"Diagnostics/Regression"; REG.mkdir(parents=True,exist_ok=True)
H=REG/"knowledge_v5.jsonl"; R=ROOT/"Config/generated_preflight_rules.json"

PRIO={"TOOLCHAIN-UE-001":"P1","TOOLCHAIN-LINUX-CLANG-001":"P1","TOOLCHAIN-LINUX-GLIBC-001":"P1",
      "TOOLCHAIN-WINDOWS-VS-001":"P1","TOOLCHAIN-WINDOWS-SDK-001":"P1",
      "RUNTIME-CP1-CRASH":"P0","RUNTIME-CP1-BOOT-FAIL":"P0","BUILD-FAILED":"P0"}

def record(run_id,issues):
    with H.open("a",encoding="utf-8") as f:
        f.write(json.dumps({"run_id":run_id,"timestamp":time.time(),"issues":issues},ensure_ascii=False)+"\n")

def compile(min_runs=2):
    buckets={}
    if H.exists():
        for line in H.read_text(encoding="utf-8").splitlines():
            try:r=json.loads(line)
            except json.JSONDecodeError:continue
            for issue in r.get("issues",[]):
                c=issue.get("code","UNKNOWN"); buckets.setdefault(c,set()).add(r.get("run_id"))
    rules=[]
    for code,runs in buckets.items():
        runs={r for r in runs if r}
        if len(runs)>=min_runs:
            p=PRIO.get(code,"P2")
            rules.append({"rule_id":"REG-"+code,"source_code":code,"priority":p,
                          "observed_runs":len(runs),
                          "gate_action":"BLOCK_ALL" if p=="P0" else "BLOCK_RUNTIME" if p=="P1" else "WARN"})
    rules.sort(key=lambda x:(x["priority"],x["rule_id"]))
    R.write_text(json.dumps({"generated_at":time.time(),"minimum_independent_runs":min_runs,"rules":rules},
                            ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return rules
