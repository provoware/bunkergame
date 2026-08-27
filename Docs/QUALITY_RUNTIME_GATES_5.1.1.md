# Quality Runtime Gates 5.1.1

## Persistent P0/P1 regression gates

- Two independent observations required.
- P0 blocks all dependent starts.
- P1 permits independent Core QA but blocks dependent Runtime/CP gates.
- P2 produces a warning.

## Automatic runtime sequence

When toolchain + persistent preflight gates are GREEN:

`Build → BunkerBeats.Smoke → CP1 → Report → Gate`

If any prerequisite is not satisfied, Runtime is not executed.

## Evidence rule

Execution status, domain status and gate status are separate.
No successful Runtime claim without actual execution and successful test evidence.
