#!/usr/bin/env python3
"""One-command, read-only P0 preflight for BUNKER BEATS."""

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
    Step("branch", "Branch-Lifecycle", (sys.executable, "Scripts/branch_lifecycle_guard.py")),
    Step("static", "Statische Projektprüfung", (sys.executable, "Scripts/ci_verify.py")),
    Step("quality", "Repository-Qualität", (sys.executable, "Scripts/repo_quality.py")),
    Step("github", "GitHub P0 Ruleset Live-Beweis", (sys.executable, "Scripts/github_p0_public_verify.py")),
)
BOOTSTRAP_STEP = Step(
    "bootstrap",
    "UE-5.8 Runner-Bootstrap Serverbeweis",
    (sys.executable, "Scripts/github_runner_bootstrap_public_verify.py"),
)
READINESS_STEP = Step(
    "readiness",
    "Lokale UE-5.8 Runner-Bereitschaft",
    (sys.executable, "Scripts/runner_readiness.py"),
)


def run_step(step: Step) -> StepResult:
    print(f"\n=== {step.title} ===")
    result = subprocess.run(step.command, cwd=ROOT, check=False)
    return StepResult(step, result.returncode)


def failed(results: list[StepResult], key: str) -> bool:
    item = next((result for result in results if result.step.key == key), None)
    return item is None or not item.passed


def next_action(results: list[StepResult], include_readiness: bool) -> str:
    if failed(results, "branch"):
        return "Neuen Arbeitsbranch vom aktuellen main erstellen; gemergten Feature-Branch nicht weiterverwenden."
    if failed(results, "static"):
        return "Statische Fehler zuerst beheben: python3 Scripts/ci_verify.py"
    if failed(results, "quality"):
        return "Quality Guard zuerst reparieren: python3 Scripts/repo_quality.py"
    if failed(results, "github"):
        return (
            "GitHub-Adminfähigkeit zuerst read-only prüfen: "
            "python3 Scripts/github_p0_admin.py --doctor; erst nach PASS das unabhängig lesbare Ruleset mit "
            "python3 Scripts/github_p0_admin.py --apply-ruleset anwenden."
        )
    if not include_readiness:
        return (
            "Self-hosted Runner registrieren; danach GitHub Actions → `UE 5.8 Runner Bootstrap Acceptance` "
            "auf main manuell ausführen und anschließend python3 Scripts/p0_preflight.py --full starten."
        )
    if failed(results, "bootstrap"):
        return (
            "GitHub Actions → `UE 5.8 Runner Bootstrap Acceptance` auf main manuell ausführen. "
            "Erst ein frischer UE58_RUNNER_BOOTSTRAP: PASS darf die Runner-Aktivierung freigeben."
        )
    if failed(results, "readiness"):
        return "Lokale UE-Maschine reparieren und Readiness erneut ausführen."
    return (
        "Alle Vorbedingungen sind PASS. Runner jetzt nur über "
        "python3 Scripts/github_p0_admin.py --apply-ruleset --enable-runner-variable freigeben; "
        "danach CP1 UE 5.8 Runtime ausführen."
    )


def summary(results: list[StepResult], include_readiness: bool) -> int:
    print("\n=== P0 GESAMTSTATUS ===")
    for item in results:
        print(f"[{'PASS' if item.passed else 'FAIL'}] {item.step.title}")

    failures = [item for item in results if item.step.required and not item.passed]
    print(f"\nNÄCHSTER SCHRITT: {next_action(results, include_readiness)}")
    state = "PASS" if not failures else "INCOMPLETE"
    print(f"P0_PREFLIGHT: {state}")
    print("Hinweis: P0_PREFLIGHT: PASS ist kein CP1-Runtime-PASS.")
    return 0 if not failures else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Gesamtprüfung vor Aktivierung des echten UE-5.8-CP1-Laufs."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="zusätzlich öffentlichen Runner-Bootstrap-Beweis und lokale UE-5.8-Readiness prüfen",
    )
    args = parser.parse_args()

    print("=== BUNKER BEATS P0 PREFLIGHT ===")
    print("Modus: READ-ONLY — dieses Skript ändert keine GitHub-Einstellungen.")
    print("GitHub-Schutzbeweis: öffentliches Ruleset direkt von api.github.com, ohne Token.")
    if args.full:
        print("Runner-Beweis: öffentlicher GitHub Workflow-/Job-Status + lokale Readiness v3.")

    steps = list(BASE_STEPS)
    if args.full:
        steps.extend((BOOTSTRAP_STEP, READINESS_STEP))

    return summary([run_step(step) for step in steps], args.full)


if __name__ == "__main__":
    raise SystemExit(main())
