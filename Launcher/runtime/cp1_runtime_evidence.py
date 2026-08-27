from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "Diagnostics/Runtime"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TELEMETRY = ROOT / "Saved/Automation/CP1_RuntimeTelemetry.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd, cwd=ROOT, timeout=3600):
    argv = [str(x) for x in cmd]
    if argv and platform.system() == "Windows" and argv[0].lower().endswith((".bat", ".cmd")):
        argv = ["cmd.exe", "/d", "/s", "/c", *argv]
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-30000:],
        "stderr": proc.stderr[-30000:],
    }


def discover_ue():
    roots = []
    env = os.environ.get("UE_ROOT")
    if env:
        roots.append(Path(env).expanduser())
    roots.extend(
        [
            Path(r"C:\Program Files\Epic Games\UE_5.8"),
            Path(r"D:\Program Files\Epic Games\UE_5.8"),
            Path("/opt/UnrealEngine"),
            Path("/opt/Epic Games/UE_5.8"),
            Path.home() / ".local/UnrealEngine",
        ]
    )
    for root in roots:
        if not root.exists():
            continue
        uat = next((p for p in [root / "Engine/Build/BatchFiles/RunUAT.sh", root / "Engine/Build/BatchFiles/RunUAT.bat"] if p.exists()), None)
        editor = next(
            (
                p
                for p in [
                    root / "Engine/Binaries/Linux/UnrealEditor-Cmd",
                    root / "Engine/Binaries/Linux/UnrealEditor",
                    root / "Engine/Binaries/Win64/UnrealEditor-Cmd.exe",
                    root / "Engine/Binaries/Win64/UnrealEditor.exe",
                ]
                if p.exists()
            ),
            None,
        )
        version_file = root / "Engine/Build/Build.version"
        version = None
        if version_file.exists():
            try:
                version_data = json.loads(version_file.read_text(encoding="utf-8"))
                version = f"{version_data.get('MajorVersion')}.{version_data.get('MinorVersion')}"
            except Exception:
                version = None
        build = next(
            (
                p
                for p in [
                    root / "Engine/Build/BatchFiles/Build.bat",
                    root / "Engine/Build/BatchFiles/Linux/Build.sh",
                ]
                if p.exists()
            ),
            None,
        )
        if uat and editor and build and version == "5.8":
            return {"root": str(root), "uat": str(uat), "editor": str(editor), "build": str(build), "version": version}
    return None


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
    for name, path in [("clang", clang), ("clang20", clang20)]:
        if path:
            result = run([path, "--version"], timeout=20)
            data[name + "_version_output"] = result["stdout"]
    try:
        result = subprocess.run(["ldd", "--version"], text=True, capture_output=True, timeout=10)
        data["glibc"] = ((result.stdout or result.stderr).splitlines() or [""])[0]
    except Exception:
        data["glibc"] = None
    return data


def load_telemetry():
    if not TELEMETRY.exists():
        return None, "telemetry file missing"
    try:
        data = json.loads(TELEMETRY.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"telemetry JSON invalid: {exc}"
    required = {
        "schema",
        "frame_samples",
        "frame_time_ms_avg",
        "position_before",
        "position_after",
        "velocity",
        "speed_cm_s",
        "displacement_cm",
        "movement_component",
    }
    missing = sorted(required - set(data))
    if missing:
        return None, f"telemetry fields missing: {', '.join(missing)}"
    if data.get("schema") != "bunkerbeats.cp1.movement.telemetry.v2":
        return None, f"unexpected telemetry schema: {data.get('schema')}"
    if (data.get("frame_samples") or 0) <= 0 or (data.get("frame_time_ms_avg") or 0) <= 0:
        return None, "frame telemetry is not positive"
    if (data.get("displacement_cm") or 0) <= 0.01:
        return None, "movement displacement is not above threshold"
    if not (data.get("movement_component") or {}).get("valid"):
        return None, "movement component evidence is invalid"
    return data, None


def main():
    project = ROOT / "BunkerBeats.uproject"
    ue = discover_ue()
    evidence = {
        "schema": "bunkerbeats.cp1.runtime.evidence.v2",
        "started_utc": now(),
        "host": {"os": platform.system(), "platform": platform.platform(), "machine": platform.machine()},
        "project": {"path": str(project), "exists": project.exists()},
        "ue": ue,
        "toolchain": toolchain_snapshot(),
        "steps": [],
        "telemetry": None,
    }

    # A stale telemetry file must never satisfy a new CP1 run.
    if TELEMETRY.exists():
        TELEMETRY.unlink()

    if not project.exists():
        evidence.update(status="BLOCKED", code="RUNTIME-PROJECT-001", message="BunkerBeats.uproject wurde nicht gefunden.")
    elif not ue:
        evidence.update(status="BLOCKED", code="TOOLCHAIN-UE-001", message="Unreal Engine 5.8 mit RunUAT + UnrealEditor wurde nicht gefunden.")
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
        evidence["steps"].append({"step": "build", "status": "GREEN" if build_result["returncode"] == 0 else "RED", "evidence": build_result})

        if build_result["returncode"] != 0:
            evidence.update(status="RED", code="BUILD-FAILED", message="Der UE-5.8-Build ist fehlgeschlagen.")
        else:
            report_path = REPORT_DIR / "CP1"
            report_path.mkdir(parents=True, exist_ok=True)
            smoke = [
                ue["editor"],
                project,
                "-unattended",
                "-nop4",
                "-nosplash",
                "-NullRHI",
                "-ExecCmds=Automation RunTest BunkerBeats.CP1.CharacterSpawnMovement;Quit",
                f"-ReportExportPath={report_path}",
            ]
            smoke_result = run(smoke, timeout=1800)
            telemetry, telemetry_error = load_telemetry()
            evidence["telemetry"] = telemetry
            evidence["telemetry_error"] = telemetry_error
            evidence["steps"].append(
                {
                    "step": "cp1_character_movement",
                    "status": "GREEN" if smoke_result["returncode"] == 0 and telemetry is not None else "RED",
                    "evidence": smoke_result,
                    "report_path": str(report_path),
                    "telemetry_path": str(TELEMETRY),
                }
            )

            if smoke_result["returncode"] != 0:
                evidence.update(status="RED", code="RUNTIME-CP1-MOVEMENT-FAIL", message="CP1 Character Spawn + Movement ist fehlgeschlagen.")
            elif telemetry is None:
                evidence.update(status="RED", code="RUNTIME-CP1-EVIDENCE-FAIL", message=f"UE-Test meldete Erfolg, aber technische Movement-Evidence ist unvollständig: {telemetry_error}")
            else:
                evidence.update(status="GREEN", code="CP1-CHARACTER-MOVEMENT-OK", message="CP1 Build + Character Spawn + Movement + technische Telemetrie wurden real ausgeführt.")

    evidence["finished_utc"] = now()
    out = REPORT_DIR / "CP1_runtime_evidence.json"
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    if evidence["status"] == "GREEN":
        return 0
    if evidence["status"] == "BLOCKED":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
