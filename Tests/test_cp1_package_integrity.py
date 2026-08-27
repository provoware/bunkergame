from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def run():
    checks = []

    def ck(name, ok, detail=""):
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    uproject = ROOT / "BunkerBeats.uproject"
    ck("uproject present", uproject.exists())
    if uproject.exists():
        try:
            data = json.loads(uproject.read_text(encoding="utf-8"))
            ck("engine association 5.8", data.get("EngineAssociation") == "5.8", str(data.get("EngineAssociation")))
            ck("BunkerBeats module", any(m.get("Name") == "BunkerBeats" for m in data.get("Modules", [])))
        except Exception as exc:
            ck("uproject valid JSON", False, str(exc))

    ck("game target present", (ROOT / "Source/BunkerBeats.Target.cs").exists())
    ck("editor target present", (ROOT / "Source/BunkerBeatsEditor.Target.cs").exists())
    module_cpp = ROOT / "Source/BunkerBeats/Private/BunkerBeats.cpp"
    ck("primary game module present", module_cpp.exists())
    if module_cpp.exists():
        ck("primary game module macro", "IMPLEMENT_PRIMARY_GAME_MODULE" in module_cpp.read_text(encoding="utf-8"))

    manifest = ROOT / "Config/cp1_smoke_manifest.json"
    ck("smoke manifest present", manifest.exists())
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        ck("suite id", data.get("suite_id") == "BunkerBeats.Smoke", str(data.get("suite_id")))
        ck("checkpoint CP1", data.get("checkpoint") == "CP1", str(data.get("checkpoint")))

    return checks


if __name__ == "__main__":
    import sys

    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if all(item["status"] == "PASS" for item in result) else 1)
