from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
CPP = ROOT / "Source/BunkerBeats/Private/Tests/BunkerBeatsCP1MovementSmokeTest.cpp"
CHARACTER = ROOT / "Source/BunkerBeats/Private/Tests/BunkerBeatsCP1MovementSmoke.cpp"
RUNNER = ROOT / "Launcher/runtime/cp1_runtime_evidence.py"
GATE = ROOT / "Scripts/cp1_gate_runtime.py"
CONTRACT = ROOT / "Scripts/cp1_runtime_evidence_contract.py"
ORCHESTRATOR = ROOT / "Scripts/run_cp1_ue58.py"


def main():
    cpp = CPP.read_text(encoding="utf-8")
    character = CHARACTER.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")
    orchestrator = ORCHESTRATOR.read_text(encoding="utf-8")

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
        "stale_runtime_artifacts_purged": (
            "purge_stale_runtime_artifacts" in runner
            and "(OUTPUT, TELEMETRY)" in runner
            and "shutil.rmtree(AUTOMATION_REPORT_DIR)" in runner
        ),
        "automation_run": "Automation RunTest BunkerBeats.CP1.CharacterSpawnMovement" in runner,
        "report_export": "-ReportExportPath" in runner,
        "runtime_evidence_json": "CP1_runtime_evidence.json" in runner,
        "runtime_contract_v3": "SCHEMA_VERSION = 3" in contract and 'KIND = "CP1_RUNTIME_EVIDENCE"' in contract,
        "telemetry_schema_v3": "bunkerbeats.cp1.movement.telemetry.v3" in cpp and "TELEMETRY_SCHEMA" in contract,
        "run_id_challenge": (
            "CP1EvidenceRunId=" in cpp
            and "-CP1EvidenceRunId={run_id}" in runner
            and '\\"run_id\\"' in cpp
        ),
        "telemetry_file_hash_bound": "telemetry_sha256" in runner and "telemetry_digest" in contract,
        "gate_live_revalidation": (
            "validate_runtime_evidence" in gate
            and "current_repository_identity" in gate
            and "current_git_head" in gate
            and "machine_fingerprint" in gate
            and "git_worktree_clean" in gate
        ),
        "canonical_sequence": (
            "runner_readiness.py" in orchestrator
            and "ci_verify.py" in orchestrator
            and "cp1_runtime_evidence.py" in orchestrator
            and "cp1_gate_runtime.py" in orchestrator
        ),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
