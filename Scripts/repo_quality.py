#!/usr/bin/env python3
"""Zero-dependency repository quality guard for BUNKER BEATS."""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "ANLEITUNG.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "WICHTIG.md",
    "CODEQUALITÄT.md",
    "Docs/TODO.md",
    "Docs/PROJEKTSTATUS.md",
    "Docs/CHANGELOG.md",
    "Launcher/core/environment_contract.py",
    "Launcher/core/assistant.py",
    "Launcher/gui/repair_gui.py",
    "Scripts/ci_verify.py",
    "Scripts/tests/test_environment_gui_contract.py",
)

COCKPIT_MARKDOWN = (
    "README.md",
    "ANLEITUNG.md",
    "CONTRIBUTING.md",
    "WICHTIG.md",
    "CODEQUALITÄT.md",
    "Docs/TODO.md",
    "Docs/PROJEKTSTATUS.md",
)

FORBIDDEN_DIR_NAMES = {
    "Binaries",
    "DerivedDataCache",
    "Diagnostics",
    "Intermediate",
    "Saved",
    "__pycache__",
}

ACTION_REF_RE = re.compile(r"^[0-9a-fA-F]{40}$")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CQ_ID_RE = re.compile(r"^## (CQ-[A-Za-z0-9._-]+)", re.MULTILINE)
W_ID_RE = re.compile(r"^## (W-[A-Za-z0-9._-]+)", re.MULTILINE)


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)
    print(f"[FAIL] {message}")


def check_required_files(errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.is_file():
            add_error(errors, f"required file missing: {rel}")


def check_forbidden_generated_paths(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_dir() and path.name in FORBIDDEN_DIR_NAMES:
            add_error(errors, f"forbidden generated directory is tracked/present: {path.relative_to(ROOT)}")
        if path.is_file() and (path.suffix == ".pyc" or path.name == ".DS_Store"):
            add_error(errors, f"forbidden generated file is tracked/present: {path.relative_to(ROOT)}")


def check_json(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:  # quality tool must report every malformed file
            add_error(errors, f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def check_python_syntax(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            add_error(errors, f"Python syntax error {path.relative_to(ROOT)}: {exc.msg}")


def check_conflict_markers(errors: list[str]) -> None:
    extensions = {".md", ".py", ".json", ".yml", ".yaml", ".sh", ".bat", ".ps1", ".ini", ".cs", ".cpp", ".h"}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in extensions or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "<<<<<<< " in text and "=======\n" in text and ">>>>>>> " in text:
            add_error(errors, f"merge conflict markers found: {path.relative_to(ROOT)}")


def normalize_link(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", 1)[0].split("?", 1)[0]
    return unquote(target)


def check_local_markdown_links(errors: list[str]) -> None:
    for rel in COCKPIT_MARKDOWN:
        source = ROOT / rel
        if not source.is_file():
            continue
        text = source.read_text(encoding="utf-8")
        for raw in MARKDOWN_LINK_RE.findall(text):
            lowered = raw.lower().strip()
            if lowered.startswith(("http://", "https://", "mailto:", "ftp://", "#")):
                continue
            target = normalize_link(raw)
            if not target:
                continue
            candidate = (source.parent / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                add_error(errors, f"local link escapes repository: {rel} -> {raw}")
                continue
            if not candidate.exists():
                add_error(errors, f"broken local link: {rel} -> {raw}")


def check_quality_memory(errors: list[str]) -> None:
    wichtig = ROOT / "WICHTIG.md"
    codeq = ROOT / "CODEQUALITÄT.md"

    if wichtig.is_file():
        text = wichtig.read_text(encoding="utf-8")
        ids = W_ID_RE.findall(text)
        if len(ids) != 1:
            add_error(errors, f"WICHTIG.md must contain exactly one current W-* focus, found {len(ids)}")
        for required in ("Verbesserungsvorschlag", "Grund", "Wirkung", "Priorität", "Status"):
            if required.lower() not in text.lower():
                add_error(errors, f"WICHTIG.md missing required concept: {required}")

    if codeq.is_file():
        text = codeq.read_text(encoding="utf-8")
        ids = CQ_ID_RE.findall(text)
        if not ids:
            add_error(errors, "CODEQUALITÄT.md needs at least one CQ-* entry")
        if len(ids) != len(set(ids)):
            add_error(errors, "CODEQUALITÄT.md contains duplicate CQ IDs")
        for required in ("Verbesserungsvorschlag", "Grund", "Wirkung", "technischer Effekt"):
            if required.lower() not in text.lower():
                add_error(errors, f"CODEQUALITÄT.md missing required concept: {required}")


def check_action_pinning(errors: list[str]) -> None:
    workflows = ROOT / ".github" / "workflows"
    if not workflows.is_dir():
        return
    for path in sorted(list(workflows.glob("*.yml")) + list(workflows.glob("*.yaml"))):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped.startswith("uses:"):
                continue
            value = stripped.split("uses:", 1)[1].strip().split("#", 1)[0].strip()
            if value.startswith("./"):
                continue
            if "@" not in value:
                add_error(errors, f"workflow action without ref: {path.relative_to(ROOT)}:{number}")
                continue
            _, ref = value.rsplit("@", 1)
            if not ACTION_REF_RE.fullmatch(ref):
                add_error(errors, f"workflow action not pinned to full commit SHA: {path.relative_to(ROOT)}:{number} -> {value}")


def main() -> int:
    errors: list[str] = []
    checks = (
        check_required_files,
        check_forbidden_generated_paths,
        check_json,
        check_python_syntax,
        check_conflict_markers,
        check_local_markdown_links,
        check_quality_memory,
        check_action_pinning,
    )

    print("=== BUNKER BEATS REPOSITORY QUALITY GUARD ===")
    for check in checks:
        print(f"[RUN ] {check.__name__}")
        check(errors)

    if errors:
        print(f"QUALITY_GUARD: FAIL ({len(errors)} issue(s))")
        return 1

    print("QUALITY_GUARD: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
