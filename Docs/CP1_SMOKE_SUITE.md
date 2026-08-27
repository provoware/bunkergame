# BunkerBeats.Smoke — CP1 Automation Suite

## Fast smoke layer

`BunkerBeats.Smoke.CP1.BuildIdentity`
- proves the project automation test executes.

`BunkerBeats.Smoke.CP1.InputContract`
- proves the runtime adapter contract is reachable.
- keeps canonical gameplay rules outside the test/presentation layer.

These are intentionally fast. Unreal Engine 5.8 classifies Smoke tests as speed-oriented checks intended to run frequently; Epic states they are expected to finish within about one second. citeturn449081search0

## CP1 boot layer

`BunkerBeats CP1 Boot` is a Functional Test and verifies:
- `UWorld` exists
- a non-empty map name is available
- a clear success/failure message is emitted.

This remains separate from the ultra-fast smoke tests so the suite can grow without turning every smoke test into a long session test.

## Command line

UE 5.8 supports:
`-ExecCmds="Automation RunTest BunkerBeats.Smoke;Quit"`

and:
`-ReportExportPath="<path>"`

for machine-readable Automation results. citeturn449081search5

## UAT / Gauntlet

The wrapper uses `UE.EditorAutomation` through RunUAT for editor-session automation. Epic documents this Gauntlet test path for running C++ and functional tests from build automation. citeturn449081search1

Gauntlet is appropriate as the higher-level session orchestrator; it is not required for the fast test definitions themselves. citeturn449081search3

## CP1 Gate

GREEN requires:
1. Unreal 5.8 toolchain discovered.
2. Editor target build succeeds.
3. `BunkerBeats.Smoke` executes.
4. all selected smoke tests pass.
5. CP1 Boot Functional Test succeeds.
6. report is exported.
7. no blocking crash/error evidence is present.

Process exit code alone does not pass CP1.

## Current environment

Runtime execution remains **NOT VALIDATED** until an actual Unreal 5.8 installation is available.

## Package precondition
`BunkerBeats.uproject` must be present at the package root. The AutoStart preflight treats its absence as a blocking packaging defect.
