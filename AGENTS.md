# AGENTS.md — BUNKER BEATS Repository Control Plane

## Authority order
1. This root file controls repository/CI/PR behavior.
2. `Docs/AGENTS.md` controls gameplay and project-specific engineering rules.
3. A task/issue may narrow scope, but must not weaken safety, evidence, or gate requirements.

## Non-negotiable workflow
Observe → reproduce → identify source → smallest change → local validation → evidence → PR → CI → review → merge.

## Evidence rule
Never mark Unreal runtime behavior PASS from static inspection. Runtime claims require machine-produced evidence from UE 5.8. Missing UE is `BLOCKED`, never `PASS`.

## Change budget
- P0 gate fixes: minimal files needed to unblock the gate.
- Refactors must be separate from gameplay unless required for correctness.
- Generated folders (`Saved`, `Intermediate`, `Binaries`, `Diagnostics`) never belong in commits.

## GitHub rules
- Work on a branch; `main` is release-integrated state.
- Every PR states: goal, scope, evidence, risk, rollback, next gate.
- Prefer squash merge for one logical change.
- CI must be green before merge; UE-specific jobs may be explicitly `SKIPPED/BLOCKED` only when no UE runner is enabled.
- Do not silently weaken or delete a failing test to obtain green CI.

## CP1 acceptance
CP1 is GREEN only when all are true:
- project builds with UE 5.8,
- smoke character spawns,
- CharacterMovementComponent is valid and active,
- measurable displacement is produced by movement input,
- position, velocity, frame-time and movement-component telemetry are exported,
- stale evidence cannot satisfy the gate.

## After CP1
The next vertical slice is strictly:
Character → Interaction → first Task → Ability effect → XP.
Do not expand Crowd/Rival/Event runtime before this slice is proven unless needed as a dependency.
