# CHANGELOG

## 2026-08-27 — GitHub CP1 Control Plane
- Repository-Baseline aus v8.3-Paket bereinigt; generierte Logs/Caches ausgeschlossen.
- Unreal Game-/Editor-Targets und Primary Game Module ergänzt.
- CP1 Movement-Evidence um Frame-Time, Position, Velocity, Displacement und MovementComponent erweitert.
- Stale-Evidence-Schutz und striktes Runtime-Gate ergänzt.
- GitHub Actions für schnelle Validierung und optionalen Self-hosted UE-5.8-Lauf ergänzt.
- CODEOWNERS, PR-/Issue-Templates, Dependabot, Root-AGENTS und Contribution-Workflow ergänzt.

## 0.3.0-concept — 2026-08-27

### Added
- professional Game Design Bible
- quantified prototype balance data
- data dictionary
- prototype JSON seed data
- QA and Auto Playtester specification
- expanded project scope model
- expanded README
- expanded TODO
- project-specific AGENTS rules
- expanded living player guide
- explicit KPI hypotheses
- explicit balance-testing targets

### Changed
- project progress updated to ~23% planning/production readiness
- Technical Boot remains next implementation gate
- engine candidate assessment aligned with current Unreal Engine 5.8 tooling

### Not Validated
- runtime project
- engine boot
- 3D movement
- abilities
- crowd
- rivals
- auto playtesting
- save/load
- packaged build

## Validation update — 2026-08-27

### Added
- deterministic documentation/data consistency validation report
- verification of 20 abilities and 190 2-of-20 combinations
- verification of equal starting skill profiles
- cross-document player-guide synchronization checks

### Confirmed Not Validated
- runtime
- packaged build
- crowd/rival simulation
- auto playtester


## 0.3.1-alpha-prep — 2026-08-27

### Added
- CP1 Unreal project bootstrap
- GameMode and Character source foundation
- Enhanced Input wiring
- CP1 environment/validation report

### Changed
- project status advanced to bootstrap-prepared
- CP1 remains unpassed until Unreal compilation/editor execution is available

### Validation
- static bootstrap: PASS
- Unreal runtime: BLOCKED by unavailable toolchain

## 0.4.2-alpha-prep — 2026-08-27

### Added
- dependency manifest
- dependency doctor
- remediation plan
- startup integration
- AutoStart README

### Validation
- local dependency tooling: PASS
- Unreal runtime: still BLOCKED in current environment

## 0.6.0-alpha-prep — 2026-08-27

### Added
- intelligent regression analysis
- baseline/current comparison
- Green/Yellow/Red classification
- evidence-based optimization recommendations
- candidate optimization planner
- regression/optimization specification

### Validation
- offline analyzer: PASS
- offline optimizer: PASS
- Unreal runtime integration: not validated

## 0.6.1-alpha-prep — 2026-08-27

### Added
- regression analyzer
- optimization planner
- Pareto-frontier analysis
- offline validation fixtures
- documented separation between regression and optimization

### Validation
- known synthetic regression detected correctly
- optimization planner completed successfully

## 0.7.1-alpha-prep — 2026-08-27
- Orchestrator in-process umgestellt
- Autoformatter auf AST statt subprocess umgestellt
- vollständiger Offline-Quality-Pfad ergänzt

## 0.7.2-alpha-prep — 2026-08-27
- Orchestrator gegen Prozess-/Import-Kaskaden gehärtet
- CP Gate konservativer gestaltet
- Offline-Selbsttest ergänzt

## 1.1.0-runtime-adapter — 2026-08-27
- Character Runtime Adapter scaffold ergänzt
- Transportvalidierung und Diagnostik ergänzt
- Unreal Runtime weiterhin nicht validiert

## 1.4.0-ability-task-effects — 2026-08-27
- Ability→Task Effekte ergänzt
- Risiko-/Progress-Modifikatoren ergänzt
- 190er Testmatrix ausgeführt

## 8.3.0-cp1-runtime-evidence — 2026-08-27
- CP1 Target-Machine Runner ergänzt
- Build/Automation/Report/Gate integriert
- No-Fake-Success Runtime-Evidence erweitert
