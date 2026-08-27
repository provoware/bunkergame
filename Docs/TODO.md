# BUNKER BEATS — MASTER TODO

Version: 1.0 / aligned to current validated baseline
Method: P0–P6 + Feature Contracts + Checkpoint Gates
Current focus: CP1 Runtime / Core Integration

> **Arbeitsregel:** Keine Aufgabe wird wegen ihres Umfangs begonnen, sondern weil sie den nächsten Engpass nachweisbar reduziert.

---

# 0. CURRENT TRUTH

## Proven

- [x] Game vision documented
- [x] Character base model defined
- [x] 20 Special Abilities defined
- [x] 2-of-20 rule defined
- [x] 190 combinations enumerated
- [x] 570 headless deterministic scenario checks
- [x] 0 structural/range failures in current headless run
- [x] Regression analysis concept
- [x] Optimization analysis concept
- [x] Diagnostics / logging architecture
- [x] AutoStart / dependency architecture
- [x] Living player guide policy

## Not Proven

- [ ] Unreal Engine compile
- [ ] Unreal Editor boot
- [ ] PIE
- [ ] 3D movement
- [ ] animation
- [ ] runtime Character Creation
- [ ] runtime Ability Effects
- [ ] event runtime
- [ ] crowd runtime
- [ ] rival runtime
- [ ] save/load
- [ ] packaged build
- [ ] full Auto Playtester

---

# P0 — INTEGRITY / OPERATIONS

## P0.1 Repository Baseline

**Goal:** reproducible project state.

- [ ] repository root verify/create
- [ ] branch verify
- [ ] working tree verify
- [ ] canonical version source
- [ ] build identity
- [ ] engine version record
- [ ] platform target record

**DoD**
- reproducible project identity
- no ambiguous version source
- Git state reportable

**Risk:** HIGH if omitted before release.

---

## P0.2 Diagnostics

- [x] diagnostic categories defined
- [x] stable event IDs defined
- [x] diagnostic codes defined
- [x] session/run correlation defined
- [x] human-readable messages defined
- [x] JSONL structure defined
- [x] debug snapshots defined
- [ ] rotation verified at runtime
- [ ] sensitive-data redaction runtime-tested
- [ ] failure-report aggregation

---

## P0.3 Persistence

- [ ] SaveSchemaVersion
- [ ] stable persistent IDs
- [ ] atomic writes
- [ ] backup
- [ ] recovery
- [ ] migration table
- [ ] corrupt-save test
- [ ] migration regression tests

**Gate:** no release candidate before persistence integrity is proven.

---

# P1 — CORE GAME

## P1.1 CP1 Technical Boot

**Priority:** P1
**Current status:** 🟡 Bootstrap prepared / Runtime blocked

### Goal

Project starts in Unreal, compiles, loads a test map and exposes the first playable character.

### Dependencies

- Unreal 5.8
- C++ build toolchain
- project module
- input
- camera
- diagnostics

### Tasks

- [ ] detect real Unreal installation
- [ ] compile runtime module
- [ ] compile editor target
- [ ] create/verify test level
- [ ] spawn player
- [ ] initialize diagnostics session
- [ ] show build identity
- [ ] run boot smoke test

### Acceptance

`Boot → Map → Character → Diagnostics → no blocking error`

### Gate

**CP1 = GREEN only after actual execution.**

---

# P1.2 CP2 Movement

### Dependencies

CP1 PASS

### Tasks

- [ ] walk
- [ ] run
- [ ] turn
- [ ] collision
- [ ] camera
- [ ] controller/input
- [ ] locomotion animation
- [ ] evaluate Motion Matching fit
- [ ] movement regression case

### Acceptance

Character can move predictably with no blocking input/collision defect.

---

# P1.3 CP3 Interaction

### Dependencies

CP2

### Tasks

- [ ] IInteractable contract
- [ ] prompt
- [ ] availability state
- [ ] disabled reason
- [ ] execute
- [ ] success feedback
- [ ] failure feedback
- [ ] diagnostic event
- [ ] functional test

---

# P1.4 Character Identity

### Dependencies

CP3 data path + Character runtime

### Tasks

- [ ] Pppoppi
- [ ] Atze
- [ ] equal base skills
- [ ] profile
- [ ] bio
- [ ] funny info
- [ ] ability list
- [ ] exactly 2 selection
- [ ] duplicate rejection
- [ ] persistent IDs
- [ ] ability selection telemetry

### Acceptance

Two characters start equal and selection produces persistent differentiated state.

---

# P1.5 Tasks

- [ ] definition
- [ ] prerequisites
- [ ] target
- [ ] actions
- [ ] duration
- [ ] risk
- [ ] success
- [ ] failure
- [ ] rewards
- [ ] consequences
- [ ] telemetry
- [ ] deterministic replay support

---

# P1.6 CP4 Progression

### Tasks

- [ ] skill data
- [ ] XP
- [ ] levels 1–5
- [ ] centralized thresholds
- [ ] skill effects
- [ ] boundary tests
- [ ] UI
- [ ] save-state representation

### Initial design data

Level 1 = 0 XP
Level 2 = 100 XP
Level 3 = 250 XP
Level 4 = 500 XP
Level 5 = 850 XP

These values remain prototype data until playtest evidence supports them.

---

# P1.7 CP5 Event

### Tasks

- [ ] Music profile
- [ ] Room
- [ ] Stage
- [ ] Lighting
- [ ] Atmosphere
- [ ] Performance
- [ ] EventDefinition
- [ ] EventBuilder
- [ ] EventEvaluator
- [ ] Outcome object
- [ ] event history
- [ ] result explanation

### Initial valid strategy families

- Sound
- Atmosphere
- Performance

---

# P2 — SIMULATION

## P2.1 CP6 Crowd

### Target archetypes

- [ ] Basshead
- [ ] Dancer
- [ ] Visual Seeker
- [ ] Underground Purist
- [ ] Social Follower

### State model

- [ ] ARRIVING
- [ ] WARMING_UP
- [ ] ENGAGED
- [ ] HYPED
- [ ] BORED
- [ ] LEAVING

### Metrics

- [ ] attendance
- [ ] engagement
- [ ] retention
- [ ] satisfaction
- [ ] concept affinity
- [ ] peak crowd
- [ ] early exits

### Validation

- [ ] deterministic seed
- [ ] archetype weight test
- [ ] state transition test
- [ ] 100+ representative runs
- [ ] compare baseline/current

---

## P2.2 CP7 Rival

- [ ] identity
- [ ] goal
- [ ] strategy
- [ ] skills
- [ ] risk tolerance
- [ ] action selection
- [ ] result
- [ ] debug explanation

### First rival

One complete reusable data-driven rival.

---

## P2.3 CP8 Discovery

- [ ] hidden location
- [ ] discovery condition
- [ ] clue/hint
- [ ] reward
- [ ] world flag
- [ ] story consequence
- [ ] persistence

---

# P3 — UX

## P3.1 Character Creation

- [ ] character choice
- [ ] profile card
- [ ] skills
- [ ] 20 ability grid
- [ ] 2/20 counter
- [ ] selected state
- [ ] impact explanation
- [ ] confirmation
- [ ] recovery from invalid choice

## P3.2 Gameplay HUD

- [ ] objective
- [ ] interaction
- [ ] task state
- [ ] skill feedback
- [ ] event state
- [ ] crowd state
- [ ] rival state
- [ ] consequence feedback

## P3.3 Player Help

- [ ] first-run guide
- [ ] contextual help
- [ ] ability glossary
- [ ] error help
- [ ] recovery instructions
- [ ] current controls

---

# P4 — PRESENTATION

## Character

- [ ] placeholder model
- [ ] Pppoppi identity
- [ ] Atze identity
- [ ] avatar customization base

## Animation

- [ ] locomotion
- [ ] interact
- [ ] carry
- [ ] repair
- [ ] setup
- [ ] performance
- [ ] success
- [ ] failure

## Audio

- [ ] bunker ambience
- [ ] UI feedback
- [ ] event feedback
- [ ] crowd feedback
- [ ] rival cues

## VFX / Lighting

- [ ] bunker readability
- [ ] event atmosphere
- [ ] crowd readability
- [ ] restrained initial effect budget

---

# P5 — DATA / EXTENSIBILITY

## Definitions

- [ ] CharacterDefinition
- [ ] SkillDefinition
- [ ] AbilityDefinition
- [ ] TaskDefinition
- [ ] EventDefinition
- [ ] CrowdDefinition
- [ ] RivalDefinition
- [ ] SecretDefinition
- [ ] DialogueDefinition

## Validation

- [ ] stable IDs
- [ ] duplicate-ID scan
- [ ] missing-reference scan
- [ ] numeric-range scan
- [ ] schema versioning

---

# P6 — AUTOMATION / QUALITY

## P6.1 Auto Playtester

### Scenarios

- [ ] T01_BOOT
- [ ] T02_MOVEMENT
- [ ] T03_INTERACTION
- [ ] T04_TASK
- [ ] T05_CHARACTER_CREATION
- [ ] T06_ABILITY_SELECTION
- [ ] T07_ABILITY_EFFECT
- [ ] T08_EVENT
- [ ] T09_CROWD
- [ ] T10_RIVAL
- [ ] T11_DISCOVERY
- [ ] T12_RECOVERY
- [ ] T13_REPEATABILITY
- [ ] T14_SAVE_LOAD
- [ ] T15_PACKAGED_BUILD

### Modes

- [ ] Conservative
- [ ] Aggressive
- [ ] Explorer
- [ ] Improviser
- [ ] Completionist

---

## P6.2 Regression

- [x] baseline/current concept
- [x] metric direction handling
- [x] threshold model
- [x] severity model
- [x] first-failure guidance
- [ ] real Unreal test ingestion
- [ ] historical baseline registry
- [ ] trend detection
- [ ] checkpoint auto-gating

### Rule

Regression result:
- GREEN = no material regression
- YELLOW = evidence incomplete / blocked
- RED = material regression / failure

---

## P6.3 Optimization

- [x] candidate ranking concept
- [x] weighted objective model
- [x] Pareto concept
- [ ] live runtime metrics
- [ ] historical comparisons
- [ ] constrained candidate search
- [ ] human approval gate before source changes

**No automatic balance/code mutation.**

---

## P6.4 Autoformat / Preflight

- [x] JSON normalization
- [x] whitespace normalization
- [x] Python syntax checks
- [ ] C++ formatter integration after engine/toolchain is available
- [ ] pre-commit validation
- [ ] generated-file exclusion

---

# CP10 — VERTICAL SLICE GATE

All must be proven:

- [ ] start
- [ ] move
- [ ] interact
- [ ] task
- [ ] skill XP
- [ ] choose 2 of 20 abilities
- [ ] ability changes available play
- [ ] event build
- [ ] event execution
- [ ] crowd reaction
- [ ] rival competition
- [ ] secret
- [ ] progression
- [ ] deterministic replay
- [ ] automated test report
- [ ] regression gate
- [ ] player guide current

---

# CURRENT NEXT STEP

## 🟢 CP1 Runtime

**Objective:** Actual Unreal compile + boot + smoke test.

**Cause / bottleneck:** Runtime toolchain is the only critical proof gap remaining for the current core path.

**Dependencies:**
- Unreal Engine 5.8
- C++ toolchain
- project module
- test map
- character
- diagnostics

**Change class:** Technical Foundation / Runtime Integration

**Validation:** Boot Smoke + Build + Character Spawn + Diagnostics

**Documentation impact:**
- README
- TODO
- PROJEKTSTATUS
- GAMEPLAY_GUIDE only if visible controls/state change.

---

# NEXT-3 FORECAST

## Next iteration

CP1 Runtime.

## +3 iterations

Likely convergence:
Character → Interaction → Ability Selection.

## Next release candidate

First complete Vertical-Slice core:
Character + Task + Event + Crowd + Rival + Discovery + automated regression.

Only pursue deeper presentation/multiplayer after the core slice proves itself.

## Runtime Integration
- [x] thin Character Runtime Adapter scaffold
- [x] transport validation boundary
- [x] human-readable adapter diagnostics
- [x] adapter static checks
- [ ] bind adapter to actual Gameplay API runtime in Unreal
- [ ] compile with Unreal 5.8
- [ ] PIE validation

## Ability-driven Task Effects
- [x] Datenmodell für Task-Tags
- [x] Progress-/Risiko-Modifikatoren
- [x] 190er-Kombinationsscan
- [x] Regressionsevidenz für den ersten Task
- [ ] Szenario-Balance-Matrix erweitern

## CP1 Runtime Evidence 8.3
- [x] Target-machine runner
- [x] real Build step
- [x] exact CP1 CharacterSpawnMovement Automation test
- [x] evidence JSON
- [ ] successful execution on UE-5.8-equipped target machine
