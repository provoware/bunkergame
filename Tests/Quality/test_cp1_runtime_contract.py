from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
CPP = ROOT / "Source/BunkerBeats/Private/Tests/BunkerBeatsCP1MovementSmokeTest.cpp"
CHARACTER = ROOT / "Source/BunkerBeats/Private/Tests/BunkerBeatsCP1MovementSmoke.cpp"
RUNNER = ROOT / "Launcher/runtime/cp1_runtime_evidence.py"


def main():
    cpp = CPP.read_text(encoding="utf-8")
    character = CHARACTER.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    checks = {
        "test_world_wrapper": "FTestWorldWrapper" in cpp and "CreateTestWorld(EWorldType::Game)" in cpp and "TickTestWorld" in cpp,
        "spawn": "SpawnActor<ABunkerBeatsCP1MovementSmokeCharacter>" in cpp,
        "movement_input": "AddMovementInput" in cpp,
        "movement_component": "GetCharacterMovement" in cpp,
        "controllerless_physics": "bRunPhysicsWithNoController = true" in character,
        "bounded_timeout": "MovementTimeoutSeconds" in cpp,
        "frame_time": "frame_time_ms_avg" in cpp,
        "positions": "position_before" in cpp and "position_after" in cpp,
        "velocity": '\\"velocity\\"' in cpp,
        "displacement": "displacement_cm" in cpp,
        "telemetry_file": "CP1_RuntimeTelemetry.json" in cpp,
        "test_id": "BunkerBeats.CP1.CharacterSpawnMovement" in cpp,
        "editor_target_build": "BunkerBeatsEditor" in runner and 'ue["build"]' in runner,
        "stale_evidence_deleted": "TELEMETRY.unlink()" in runner,
        "automation_run": "Automation RunTest BunkerBeats.CP1.CharacterSpawnMovement" in runner,
        "report_export": "-ReportExportPath" in runner,
        "runtime_evidence_json": "CP1_runtime_evidence.json" in runner,
        "telemetry_schema_v2": "bunkerbeats.cp1.movement.telemetry.v2" in runner,
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
