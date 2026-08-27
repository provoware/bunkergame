#!/usr/bin/env python3
"""One-command, read-only P0 preflight for BUNKER BEATS.

This orchestrator never changes GitHub settings and never claims CP1 runtime PASS.
It combines already-existing gates into one layperson-friendly status matrix.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Step:
    key: str
    title: str
    command: tuple[str, ...]
    required: bool = True


@dataclass(frozen=True)
class StepResult:
    step: Step
    returncode: int

    @property
    def passed(self) -> bool:
        return self.returncode == 0


BASE_STEPS = (
    Step("static", "Statische Projektprüfung", (sys.executable, "Scripts/ci_verify.py")),
    Step("quality", "Repository-Qualität", (sys.executable, "Scripts/repo_quality.py")),
    Step("github", "GitHub P0 Branch-Gate", (sys.executable, "Scripts/github_p0_status.py")),
)
READINESS_STEP = Step(
    "readiness",
    "UE-5.8 Runner-Bereitschaft",
    (sys.executable, "Scripts/runner_readiness.py"),
)


def run_step(step: Step) -> StepResult:
    print(f"\n=== {step.title} ===")
    result = subprocess.run(step.command, cwd=ROOT, check=False)
    return StepResult(step, result.returncode)


def next_action(results: list[StepResult], include_readiness: bool) -> str:
    by_key = {item.step.key: item for item in results}
    if not by_key.get("static", StepResult(BASE_STEPS[0], 1)).passed:
        return "Statische Fehler zuerst beheben: python3 Scripts/ci_verify.py"
    if not by_key.get("quality", StepResult(BASE_STEPS[1], 1)).passed:
        return "Quality Guard zuerst reparieren: python3 Scripts/repo_quality.py"
    if not by_key.get("github", StepResult(BASE_STEPS[2], 1)).passed:
        return "main schützen: python3 Scripts/github_p0_admin.py --apply"
    if not include_readiness:
        return "Auf der UE-5.8-Maschine fortsetzen: python3 Scripts/p0_preflight.py --full"
    readiness = by_key.get("readiness")
    if readiness is None or not readiness.passed:
        return "UE-Maschine reparieren und Readiness erneut ausführen."
    return (
        "Alle Vorbedingungen sind PASS. Frische Evidence jetzt mit "
        "python3 Scripts/github_p0_admin.py --apply --enable-runner-variable freigeben; "
        "danach CP1 UE 5.8 Runtime ausführen."
    )


def summary(results: list[StepResult], include_readiness: bool) -> int:
    print("\n=== P0 GESAMTSTATUS ===")
    for item in results:
        print(f"[{'PASS' if item.passed else 'FAIL'}] {item.step.title}")

    failed = [item for item in results if item.step.required and not item.passed]
    print(f"\nNÄCHSTER SCHRITT: {next_action(results, include_readiness)}")
    state = "PASS" if not failed else "INCOMPLETE"
    print(f"P0_PREFLIGHT: {state}")
    print("Hinweis: P0_PREFLIGHT: PASS ist kein CP1-Runtime-PASS.")
    return 0 if not failed else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Gesamtprüfung vor Aktivierung des echten UE-5.8-CP1-Laufs."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="zusätzlich lokale UE-5.8 Runner-Readiness prüfen; auf der UE-Maschine verwenden",
    )
    args = parser.parse_args()

    print("=== BUNKER BEATS P0 PREFLIGHT ===")
    print("Modus: READ-ONLY — dieses Skript ändert keine GitHub-Einstellungen.")

    steps = list(BASE_STEPS)
    if args.full:
        steps.append(READINESS_STEP)

    results = [run_step(step) for step in steps]
    return summary(results, args.full)


if __name__ == "__main__":
    raise SystemExit(main())
