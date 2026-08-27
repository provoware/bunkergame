#!/usr/bin/env python3
"""Self-hosted UE 5.8 runner readiness check.

This proves machine readiness only. It never upgrades CP1 runtime status to PASS.
Readiness evidence is bound to the current repository, exact Git HEAD and a
pseudonymous machine fingerprint so it cannot be casually reused elsewhere.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from runner_identity import (
    EXPECTED_REPOSITORY,
    MACHINE_IDENTITY_SCHEME,
    current_git_head,
    current_repository_identity,
    git_worktree_clean,
    machine_fingerprint,
)
from runner_readiness_contract import (
    EXPECTED_UE_MAJOR,
    EXPECTED_UE_MINOR,
    KIND,
    REQUIRED_CHECKS,
    SCHEMA_VERSION,
)

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
            root = editor.parents[3] if len(editor.parents) >= 4 else editor.parent
            return root, editor, locate_build_script(root)

    system = platform.system().lower()
    for root in candidate_roots():
        if system == "windows":
            editor = root / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
        elif system == "darwin":
            editor = root / "Engine" / "Binaries" / "Mac" / "UnrealEditor.app"
        else:
            editor = root / "Engine" / "Binaries" / "Linux" / "UnrealEditor"

        if editor.exists():
            return root, editor, locate_build_script(root)

    return None, None, None


def locate_build_script(root: Path) -> Path | None:
    system = platform.system().lower()
    if system == "windows":
        candidate = root / "Engine" / "Build" / "BatchFiles" / "Build.bat"
    elif system == "darwin":
        candidate = root / "Engine" / "Build" / "BatchFiles" / "Mac" / "Build.sh"
    else:
        candidate = root / "Engine" / "Build" / "BatchFiles" / "Linux" / "Build.sh"
    return candidate if candidate.exists() else None


def read_engine_version(root: Path | None) -> tuple[bool, dict | None, str]:
    if root is None:
        return False, None, "engine root unavailable"
    path = root / "Engine" / "Build" / "Build.version"
    if not path.is_file():
        return False, None, f"missing {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, None, f"invalid Build.version: {exc}"
    major = data.get("MajorVersion")
    minor = data.get("MinorVersion")
    ok = (
        type(major) is int
        and type(minor) is int
        and major == EXPECTED_UE_MAJOR
        and minor == EXPECTED_UE_MINOR
    )
    return ok, data, f"{major}.{minor}"


def main() -> int:
    engine_root, editor, build_script = locate_engine()
    version_ok, version_data, version_detail = read_engine_version(engine_root)
    disk = shutil.disk_usage(ROOT)
    free_gb = disk.free / (1024**3)

    clean, clean_detail = git_worktree_clean(ROOT)
    repository, repository_detail = current_repository_identity(ROOT)
    git_head, git_head_detail = current_git_head(ROOT)
    fingerprint, fingerprint_detail = machine_fingerprint()

    compiler = command_exists("clang++", "g++", "cl.exe", "cl")
    python_cmd = command_exists("python3", "python")

    checks = {
        "project_file": (ROOT / "BunkerBeats.uproject").is_file(),
        "editor_target": (ROOT / "Source" / "BunkerBeatsEditor.Target.cs").is_file(),
        "engine_root_detected": engine_root is not None,
        "unreal_editor_detected": editor is not None,
        "engine_build_script_detected": build_script is not None,
        "engine_version_exact_5_8": version_ok,
        "python_available": python_cmd is not None,
        "repo_writable": os.access(ROOT, os.W_OK),
        "free_disk_gt_5gb": free_gb >= 5.0,
        "git_worktree_clean_before_runtime": clean,
        "repository_identity_exact": repository == EXPECTED_REPOSITORY,
        "git_head_bound": git_head is not None,
        "machine_identity_bound": fingerprint is not None,
    }

    contract_shape_ok = set(checks) == REQUIRED_CHECKS
    required_pass = contract_shape_ok and all(value is True for value in checks.values())
    now = datetime.now(timezone.utc)
    report = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "runtime_executed": False,
        "cp1_pass": False,
        "status": "PASS" if required_pass else "FAIL",
        "repository": repository,
        "git_head_sha": git_head,
        "machine_fingerprint_sha256": fingerprint,
        "machine_identity_scheme": MACHINE_IDENTITY_SCHEME,
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "engine_root": str(engine_root) if engine_root else None,
        "engine_version": version_detail if version_data is not None else None,
        "engine_version_raw": version_data,
        "editor": str(editor) if editor else None,
        "build_script": str(build_script) if build_script else None,
        "compiler_hint": compiler,
        "free_disk_gb": round(free_gb, 2),
        "git_worktree": clean_detail,
        "identity_diagnostics": {
            "repository": repository_detail,
            "git_head": git_head_detail,
            "machine": fingerprint_detail,
        },
        "checks": checks,
        "note": "Readiness PASS proves machine prerequisites only; it is not CP1 runtime evidence.",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if not contract_shape_ok:
        print("[FAIL] Internal readiness check set does not match the central contract.")
    if not compiler:
        print("[WARN] No compiler executable found on PATH. Unreal may still locate its toolchain independently.")

    if required_pass:
        print("RUNNER_READINESS: PASS")
        return 0

    print("RUNNER_READINESS: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
