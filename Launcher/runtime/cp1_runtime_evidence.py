from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import platform
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from cp1_runtime_evidence_contract import (
    KIND,
    SCHEMA_VERSION,
    TELEMETRY_RELATIVE_PATH,
    seal_runtime_evidence,
    telemetry_digest,
    validate_telemetry,
)
from runner_identity import (
    EXPECTED_REPOSITORY,
    current_git_head,
    current_repository_identity,
    git_worktree_clean,
    machine_fingerprint,
)
from runner_readiness import locate_engine, read_engine_version

REPORT_DIR = ROOT / "Diagnostics" / "Runtime"
OUTPUT = REPORT_DIR / "CP1_runtime_evidence.json"
AUTOMATION_REPORT_DIR = REPORT_DIR / "CP1"
TELEMETRY = ROOT / TELEMETRY_RELATIVE_PATH


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd, cwd=ROOT, timeout=3600):
    argv = [str(x) for x in cmd]
    if argv and platform.system() == "Windows" and argv[0].lower().endswith((".bat", ".cmd")):
        argv = ["cmd.exe", "/d", "/s", "/c", *argv]
    try:
        proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout[-30000:],
            "stderr": proc.stderr[-30000:],
            "launched": True,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return {
            "returncode": 124,
            "stdout": stdout[-30000:],
            "stderr": (stderr + f"\nTIMEOUT after {timeout}s")[-30000:],
            "launched": True,
            "timed_out": True,
        }
    except OSError as exc:
        return {
            "returncode": 127,
            "stdout": "",
            "stderr": f"process launch failed: {exc}",
            "launched": False,
            "timed_out": False,
        }


def purge_stale_runtime_artifacts() -> tuple[bool, list[str]]:
    failures: list[str] = []
    for path in (OUTPUT, TELEMETRY):
        try:
            if path.exists():
                path.unlink()
        except OSError as exc:
            failures.append(f"stale artifact could not be removed: {path}: {exc}")
    try:
        if AUTOMATION_REPORT_DIR.exists():
            shutil.rmtree(AUTOMATION_REPORT_DIR)
    except OSError as exc:
        failures.append(f"stale automation report could not be removed: {AUTOMATION_REPORT_DIR}: {exc}")
    return not failures, failures


def discover_ue():
    engine_root, editor, build_script = locate_engine()
    version_ok, version_data, version_detail = read_engine_version(engine_root)
    if not version_ok or engine_root is None or editor is None or build_script is None:
        return None
    return {
        "root": str(engine_root),
        "editor": str(editor),
        "build": str(build_script),
        "version": version_detail,
        "version_raw": version_data,
    }


def toolchain_snapshot():
    clang = shutil.which("clang")
    clang20 = shutil.which("clang-20")
    data = {
        "os": platform.system(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "clang": clang,
        "clang20": clang20,
    }
    for name, path in (("clang", clang), ("clang20", clang20)):
        if path:
            result = run([path, "--version"], timeout=20)
            data[name + "_version_output"] = result["stdout"]
    try:
        result = subprocess.run(["ldd", "--version"], text=True, capture_output=True, timeout=10)
        data["glibc"] = ((result.stdout or result.stderr).splitlines() or [""])[0]
    except Exception:
        data["glibc"] = None
    return data


def load_telemetry(expected_run_id: str):
    if not TELEMETRY.is_file():
        return None, None, "telemetry file missing"
    try:
        raw = TELEMETRY.read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, None, f"telemetry file invalid: {exc}"

    valid, failures = validate_telemetry(data, expected_run_id=expected_run_id)
    if not valid:
        return None, raw, "; ".join(failures)
    return data, raw, None


def write_final(evidence: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    sealed = seal_runtime_evidence(evidence)
    OUTPUT.write_text(json.dumps(sealed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(sealed, ensure_ascii=False, indent=2))


def main():
    purge_ok, purge_failures = purge_stale_runtime_artifacts()
    started = now()
    run_id = uuid.uuid4().hex

    repository, repository_detail = current_repository_identity(ROOT)
    git_head, git_head_detail = current_git_head(ROOT)
    fingerprint, fingerprint_scheme = machine_fingerprint()
    clean, clean_detail = git_worktree_clean(ROOT)
    project = ROOT / "BunkerBeats.uproject"
    ue = discover_ue()

    evidence = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "started_at_utc": started,
        "finished_at_utc": None,
        "runtime_executed": False,
        "cp1_pass": False,
        "status": "BLOCKED",
        "code": "RUNTIME-NOT-STARTED",
        "message": "CP1 Runtime wurde noch nicht ausgeführt.",
        "run_id": run_id,
        "repository": repository,
        "repository_detail": repository_detail,
        "git_head_sha": git_head,
        "git_head_detail": git_head_detail,
        "machine_fingerprint_sha256": fingerprint,
        "machine_identity_scheme": fingerprint_scheme,
        "git_worktree": clean_detail,
        "host": {"os": platform.system(), "platform": platform.platform(), "machine": platform.machine()},
        "project": {"path": "BunkerBeats.uproject", "exists": project.is_file()},
        "ue": ue,
        "toolchain": toolchain_snapshot(),
        "steps": [],
        "telemetry": None,
        "telemetry_path": TELEMETRY_RELATIVE_PATH,
        "telemetry_sha256": None,
        "telemetry_error": None,
        "stale_cleanup": {"status": "PASS" if purge_ok else "FAIL", "failures": purge_failures},
        "integrity_note": "SHA-256 detects local modification; authenticity comes from context binding, run_id and gate revalidation.",
    }

    if not purge_ok:
        evidence.update(code="RUNTIME-STALE-CLEANUP-FAIL", message="Alte Runtime-Artefakte konnten nicht sicher entfernt werden.")
    elif repository != EXPECTED_REPOSITORY:
        evidence.update(code="RUNTIME-REPO-IDENTITY-FAIL", message=f"Checkout gehört nicht eindeutig zu {EXPECTED_REPOSITORY}: {repository_detail}")
    elif git_head is None:
        evidence.update(code="RUNTIME-GIT-HEAD-FAIL", message=f"Git-HEAD konnte nicht sicher bestimmt werden: {git_head_detail}")
    elif fingerprint is None:
        evidence.update(code="RUNTIME-MACHINE-IDENTITY-FAIL", message=f"Maschinenkontext konnte nicht sicher bestimmt werden: {fingerprint_scheme}")
    elif not clean:
        evidence.update(code="RUNTIME-WORKTREE-DIRTY", message=f"Git-Arbeitsstand ist vor Runtime nicht sauber: {clean_detail}")
    elif not project.is_file():
        evidence.update(code="RUNTIME-PROJECT-001", message="BunkerBeats.uproject wurde nicht gefunden.")
    elif platform.system() not in {"Windows", "Linux"}:
        evidence.update(code="RUNTIME-PLATFORM-001", message=f"CP1 Runtime unterstützt aktuell nur Windows/Linux, erkannt: {platform.system()}")
    elif not ue:
        evidence.update(code="TOOLCHAIN-UE-001", message="Unreal Engine exakt 5.8 mit Editor + Build-Skript wurde nicht gefunden.")
    else:
        platform_target = "Win64" if platform.system() == "Windows" else "Linux"
        build_command = [
            ue["build"],
            "BunkerBeatsEditor",
            platform_target,
            "Development",
            str(project),
            "-WaitMutex",
        ]
        build_result = run(build_command, timeout=3600)
        evidence["steps"].append(
            {
                "step": "build",
                "status": "GREEN" if build_result["returncode"] == 0 else "RED",
                "evidence": build_result,
            }
        )

        if build_result["returncode"] != 0:
            evidence.update(status="RED", code="BUILD-FAILED", message="Der UE-5.8-Build ist fehlgeschlagen.")
        else:
            AUTOMATION_REPORT_DIR.mkdir(parents=True, exist_ok=True)
            smoke = [
                ue["editor"],
                project,
                "-unattended",
                "-nop4",
                "-nosplash",
                "-NullRHI",
                f"-CP1EvidenceRunId={run_id}",
                "-ExecCmds=Automation RunTest BunkerBeats.CP1.CharacterSpawnMovement;Quit",
                f"-ReportExportPath={AUTOMATION_REPORT_DIR}",
            ]
            smoke_result = run(smoke, timeout=1800)
            evidence["runtime_executed"] = smoke_result.get("launched") is True

            telemetry, telemetry_raw, telemetry_error = load_telemetry(run_id)
            evidence["telemetry"] = telemetry
            evidence["telemetry_error"] = telemetry_error
            if telemetry is not None and telemetry_raw is not None:
                evidence["telemetry_sha256"] = telemetry_digest(telemetry_raw)

            evidence["steps"].append(
                {
                    "step": "cp1_character_movement",
                    "status": "GREEN" if smoke_result["returncode"] == 0 and telemetry is not None else "RED",
                    "evidence": smoke_result,
                    "report_path": "Diagnostics/Runtime/CP1",
                    "telemetry_path": TELEMETRY_RELATIVE_PATH,
                    "run_id": run_id,
                }
            )

            if smoke_result["returncode"] != 0:
                evidence.update(status="RED", code="RUNTIME-CP1-MOVEMENT-FAIL", message="CP1 Character Spawn + Movement ist fehlgeschlagen.")
            elif telemetry is None:
                evidence.update(status="RED", code="RUNTIME-CP1-EVIDENCE-FAIL", message=f"UE-Test meldete Erfolg, aber die laufgebundene Telemetrie ist ungültig: {telemetry_error}")
            else:
                evidence.update(
                    status="GREEN",
                    cp1_pass=True,
                    code="CP1-CHARACTER-MOVEMENT-OK",
                    message="CP1 Build + Character Spawn + Movement + laufgebundene technische Telemetrie wurden real ausgeführt.",
                )

    evidence["finished_at_utc"] = now()
    write_final(evidence)

    if evidence["status"] == "GREEN":
        return 0
    if evidence["status"] == "BLOCKED":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
