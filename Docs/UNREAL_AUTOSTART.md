# Unreal 5.8 AutoStart Integration

## Core-only

`python Scripts/orchestrator.py --format`

## Unreal Build

`python Scripts/orchestrator.py --format --unreal-build`

Uses Unreal Automation Tool `RunUAT` with `BuildCookRun -build`.

## Unreal Automation / PIE validation

`python Scripts/orchestrator.py --format --unreal-build --unreal-pie --automation-filter BunkerBeats.Smoke`

The filter is intentionally required. Opening the editor alone is not considered a successful runtime test.

The automation path exports results under:
`Diagnostics/TestRuns/UnrealAutomation/`

## Packaging

`python Scripts/orchestrator.py --format --unreal-build --unreal-package`

Uses `RunUAT BuildCookRun` with build/cook/stage/pak.

## Gate semantics

- GREEN: requested operation executed and passed.
- YELLOW: requested operation is blocked or evidence is incomplete.
- RED: requested operation executed and failed.

Unreal is never installed or silently configured by the script.

## Package precondition
`BunkerBeats.uproject` must be present at the package root. The AutoStart preflight treats its absence as a blocking packaging defect.
