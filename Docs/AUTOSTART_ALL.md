# BUNKER BEATS — AutoStart All

## One-click

Windows:
`START_BUNKER_BEATS_ALL.bat`

Linux/macOS:
`START_BUNKER_BEATS_ALL.sh`

## What happens

1. Environment Doctor
2. Safe formatting + JSON/Python checks
3. All registered core tests
4. Regression Gate
5. Optimization Report
6. CP1 Gate
7. Human-readable report + machine-readable JSON

## Dependency behavior

The routine detects tools. It does not silently modify the operating system.

Unreal is optional at this stage:
- missing Unreal = runtime work is BLOCKED/NOT VALIDATED
- no baseline = regression evidence is YELLOW
- actual runtime success requires actual Unreal execution.

## Diagnostics

All generated evidence stays under `Diagnostics/`.
Project definitions and authoring data remain outside this diagnostics boundary.
