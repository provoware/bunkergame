#!/usr/bin/env python3
"""Self-hosted UE 5.8 runner readiness check.

This proves machine readiness only. It never upgrades CP1 runtime status to PASS.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "Diagnostics" / "Runtime" / "runner_readiness.json"


def command_exists(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def candidate_roots() -> list[Path]:
    candidates: list[Path] = []
    for key in ("UE58_ROOT", "UE_ROOT", "UNREAL_ENGINE_ROOT"):
        value = os.environ.get(key)
        if value:
            candidates.append(Path(value).expanduser())

    home = Path.home()
    system = platform.system().lower()
    if system == "linux":
        candidates.extend(
            [
                Path("/opt/UnrealEngine/UE_5.8"),
                Path("/opt/UnrealEngine-5.8"),
                home / "UnrealEngine" / "UE_5.8",
                home / "UnrealEngine-5.8",
            ]
        )
    elif system == "windows":
        for base in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)")):
            if base:
                candidates.append(Path(base) / "Epic Games" / "UE_5.8")
    elif system == "darwin":
        candidates.append(Path("/Users/Shared/Epic Games/UE_5.8"))

    result: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            result.append(candidate)
    return result


def locate_engine() -> tuple[Path | None, Path | None, Path | None]:
    explicit_editor = os.environ.get("UE58_EDITOR_CMD")
    if explicit_editor:
        editor = Path(explicit_editor).expanduser()
        if editor.is_file():
            return editor.parents[3] if len(editor.parents) >= 4 else editor.parent, editor, None

    system = platform.system().lower()
    for root in candidate_roots():
        if system == "windows":
            editor = root / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
            build = root / "Engine" / "Build" / "BatchFiles" / "Build.bat"
        elif system == "darwin":
            editor = root / "Engine" / "Binaries" / "Mac" / "UnrealEditor.app"
            build = root / "Engine" / "Build" / "BatchFiles" / "Mac" / "Build.sh"
        else:
            editor = root / "Engine" / "Binaries" / "Linux" / "UnrealEditor"
            build = root / "Engine" / "Build" / "BatchFiles" / "Linux" / "Build.sh"

        if editor.exists():
            return root, editor, build if build.exists() else None

    return None, None, None


def git_clean() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as exc:
        return False, f"git status unavailable: {exc}"
    dirty = [line for line in result.stdout.splitlines() if line.strip()]
    return not dirty, "clean" if not dirty else f"{len(dirty)} changed/untracked path(s)"


def main() -> int:
    engine_root, editor, build_script = locate_engine()
    disk = shutil.disk_usage(ROOT)
    free_gb = disk.free / (1024**3)
    clean, clean_detail = git_clean()

    compiler = command_exists("clang++", "g++", "cl.exe", "cl")
    python_cmd = command_exists("python3", "python")

    checks = {
        "project_file": (ROOT / "BunkerBeats.uproject").is_file(),
        "editor_target": (ROOT / "Source" / "BunkerBeatsEditor.Target.cs").is_file(),
        "engine_root_detected": engine_root is not None,
        "unreal_editor_detected": editor is not None,
        "engine_build_script_detected": build_script is not None,
        "python_available": python_cmd is not None,
        "repo_writable": os.access(ROOT, os.W_OK),
        "free_disk_gt_5gb": free_gb >= 5.0,
        "git_worktree_clean_before_runtime": clean,
    }

    required_pass = all(checks.values())
    report = {
        "schema_version": 1,
        "kind": "UE58_RUNNER_READINESS",
        "runtime_executed": False,
        "cp1_pass": False,
        "status": "PASS" if required_pass else "FAIL",
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "engine_root": str(engine_root) if engine_root else None,
        "editor": str(editor) if editor else None,
        "build_script": str(build_script) if build_script else None,
        "compiler_hint": compiler,
        "free_disk_gb": round(free_gb, 2),
        "git_worktree": clean_detail,
        "checks": checks,
        "note": "Readiness PASS proves machine prerequisites only; it is not CP1 runtime evidence.",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if not compiler:
        print("[WARN] No compiler executable found on PATH. Unreal may still locate its toolchain independently.")

    if required_pass:
        print("RUNNER_READINESS: PASS")
        return 0

    print("RUNNER_READINESS: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
