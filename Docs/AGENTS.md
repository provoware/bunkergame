# AGENTS.md — BUNKER BEATS PROJECT RULES

## 0. Authority

The uploaded `ROLLENPROMPT_GAMEDESIGNER_AGENTS.md` is the primary process authority.

This document adds project-specific implementation rules.

---

# 1. PRODUCT IDENTITY

BUNKER BEATS is a 3D social-rivalry / management / simulation / progression game.

North Star:
> The player builds a distinctive event identity, sees the world react, and can win through different strategies.

---

# 2. DESIGN NON-NEGOTIABLES

1. Multiple viable strategies.
2. Character identity must affect gameplay.
3. Crowd response must be explainable.
4. Rivals must have goals and personalities.
5. Secrets must have systemic value.
6. Humor is part of presentation, never a substitute for clear UX.

---

# 3. PROCESS

Always:
Observe
-> Model
-> Prioritize
-> Minimize Change Budget
-> Implement at Source
-> Validate
-> Document
-> Version
-> Assess next bottleneck

Do not begin implementation solely because a feature sounds exciting.

---

# 4. PHASE GATES

CP0 Vision Lock
CP1 Technical Boot
CP2 Movement
CP3 Interaction
CP4 Progression
CP5 Event
CP6 Crowd
CP7 Rival
CP8 Discovery
CP9 Auto Playtester
CP10 Vertical Slice

Do not aggressively expand beyond a gate whose dependency is not proven.

---

# 5. CHARACTER RULE

Pppoppi and Atze:
- identical starting base skills
- exactly two Special Abilities selected from 20
- no hidden starting stat advantage

Differentiation is created through:
- personality
- bio
- dialogue
- selected abilities
- player behavior

---

# 6. ABILITY RULE

Each ability requires:
- stable ID
- clear trigger
- gameplay effect
- precondition
- explanation
- telemetry key
- balance tags

An ability must change a decision, option, information state or outcome.

Do not implement +5% bonuses without a demonstrated design reason.

---

# 7. DATA-FIRST

Prefer data definitions over scattered implementation.

Required conceptual separation:
Definition
Runtime State
Persistence State
Presentation State

Stable IDs are persistence contracts.

---

# 8. GAMEPLAY SYSTEM BOUNDARIES

### Character
Identity, progression, skill state.

### Interaction
What the player can do to an object.

### Task
Why/when an action matters.

### Event
How event configuration is evaluated.

### Crowd
How audience state responds.

### Rival
How competitor decisions are made.

### Presentation
How state is shown.

### Infrastructure
Saving, telemetry, tests, diagnostics, build.

Do not put core simulation rules in widgets/UI-only code.

---

# 9. SIMULATION

Crowd and rival logic must be:
- deterministic where practical
- seedable
- testable
- measurable
- independent from rendering.

A visual crowd agent is not automatically a simulation agent.

Use aggregation before high-frequency per-agent complexity.

---

# 10. PERFORMANCE

Prototype target:
60 FPS on declared hardware.

Do not optimize from assumptions.

Process:
Measure
-> locate bottleneck
-> change
-> remeasure.

Record median/p95 where useful.

---

# 11. ENGINE RULES

Current preferred candidate:
Unreal Engine 5.8.

Reason:
Epic currently documents Enhanced Input for contextual/dynamic input, Motion Matching through Pose Search, and Automation/Gauntlet test tooling suitable to the project.

Engine lock requires Technical Boot evidence.

---

# 12. AUTOMATION

Auto Playtester must not invent hidden gameplay rules.

It uses:
- defined actions
- defined scenarios
- known seeds
- known start states
- known acceptance criteria.

Status:
PASS / PARTIAL / FAIL / BLOCKED.

Unexecuted tests are NOT PASS.

---

# 13. TEST PYRAMID

Formula:
Unit -> Integration -> Functional -> Smoke -> End-to-End / Build -> Balance / Performance

Use only tests that answer a concrete question.

---

# 14. TELEMETRY

Important gameplay transitions should have stable telemetry keys.

Minimum useful metrics:
- task completion
- ability use
- event outcome
- crowd response
- rival outcome
- discovery
- errors
- performance
- test scenario result

Do not log every frame by default.

---

# 15. PLAYER GUIDE RULE

`GAMEPLAY_GUIDE.md` is the authoritative player-facing guide for implemented/officially confirmed gameplay.

Whenever gameplay changes:
- check terminology
- check control explanation
- check requirements
- check consequences
- check examples
- update only affected sections.

Never document planned mechanics as already available.

---

# 16. DOCUMENTATION MATRIX

Gameplay:
GAME_DESIGN_BIBLE
GAMEPLAY_GUIDE
TODO
PROJEKTSTATUS

Architecture:
ARCHITECTURE
AGENTS

Data:
DATA_DICTIONARY

Testing:
QA_AUTOPLAYTESTER_SPEC

Project state:
README
PROJEKTSTATUS
CHANGELOG

---

# 17. SAVE RULES

Later implementation must support:
- schema version
- persistent IDs
- atomic write
- backup
- recovery
- migration
- validation.

A save schema change requires migration design.

---

# 18. BALANCE

Balance is empirical.

For meaningful ability balance:
- run deterministic batches
- compare to baseline
- measure utility
- check scenario coverage
- look for dominance
- look for dead choices.

Do not auto-patch based on one result.

---

# 19. UX

Every major screen answers:
1. Where am I?
2. What is my state?
3. What can I do?
4. Why would I do it?
5. What happens next?

---

# 20. STYLE / NARRATIVE

Desired tone:
- trashy
- hard-techno-inspired
- absurd
- ironic
- exaggerated
- creative

Safety boundary:
The fiction does not become real-world operational guidance for dangerous or illegal activities.

---

# 21. SCOPE RULE

Before starting a feature:
- value
- dependencies
- risk
- change budget
- negative scope
- validation
- documentation impact

must be understood.

No mass content before CP10.

---

# 22. MULTIPLAYER RULE

No real multiplayer before the single-player simulation loop is proven.

Possible progression:
single-player
-> simulated rivals
-> optional asynchronous competition
-> optional networked multiplayer.

Each stage requires its own architecture decision.

---

# 23. GIT RULES

Before changes:
- inspect branch
- inspect working tree
- inspect relevant diff

After changes:
- inspect diff
- run relevant tests
- update docs
- commit coherently
- verify status

Never discard unrelated user work.

---

# 24. DEFINITION OF READY

Goal
+ Non-goal
+ Data
+ Dependencies
+ Acceptance
+ Validation

must be known.

---

# 25. DEFINITION OF DONE

Implementation
+ relevant validation
+ documentation
+ status
+ diff review
+ risk statement
+ next bottleneck

must be complete.

---

# 26. ITERATION REPORT

Always include:
- current state
- implemented
- rationale
- impact
- validation
- documentation
- version/release
- Git/GitHub
- residual risk
- progress
- exactly three next options
- one binding recommendation.

## DEBUG / LOGGING

Diagnostics are observational and must not own gameplay rules.

Every important event should support:
- stable event ID
- stable diagnostic code
- human-readable message
- machine-readable representation
- session correlation.

Diagnostics live outside project/base data.

Runtime target:
`Saved/BunkerBeats/Diagnostics/`

Do not log credentials, secrets or arbitrary full environment variables.

Human-facing messages explain:
1. what happened
2. what it means
3. what to do next

Technical details belong in structured context.

Unexecuted tests must not be logged as PASS merely because the test was planned.

## REGRESSION / OPTIMIZATION

Regression analysis is a release-quality gate.

Rules:
- compare only compatible baselines
- preserve seeds
- distinguish insufficient evidence from pass
- distinguish regression detection from optimization
- never suppress a failed test to make a build green
- add a regression test for fixed P0/P1 faults
- optimize only within correctness constraints
- preserve evidence before source modification

Optimization output is advisory until validated.

## REGRESSION GATE

A change is not "optimized" merely because one metric improves.

Required flow:
1. compare against compatible baseline
2. detect regressions
3. preserve evidence
4. isolate first reproducible failure
5. add/retain regression coverage
6. only then compare optimization candidates

No source mutation may be justified solely by the optimizer score.

## QUALITY PIPELINE
Use the orchestrated flow Preflight -> Format -> Tests -> Collection -> Regression -> Optimization -> CP Gate. Never turn missing evidence into GREEN.

## ORCHESTRATOR HARDENING
Prefer in-process deterministic stage execution for local quality orchestration. External processes are reserved for the tool actually under test (e.g. Unreal/UAT). Evidence states must remain conservative.

## RUNTIME ADAPTER RULE
Unreal Character/Controller/UI code is an adapter/presentation layer. Canonical gameplay invariants remain in the engine-independent Gameplay API. Do not duplicate ability-selection rules in UI or actors.

## ABILITY / TASK CONTRACT
Ability-Einflüsse möglichst datengetrieben und kontextgebunden modellieren. Keine verstreuten Switch-/Sonderfallketten als Standardlösung.

## CP1 RUNTIME EVIDENCE RULE
CP1 GREEN ist nur erlaubt, wenn UE wirklich ausgeführt wurde, Build und der Test `BunkerBeats.CP1.CharacterSpawnMovement` erfolgreich waren und ein Report vorliegt.
