# CHANGELOG

## 2026-08-27 — P0 Independently Verifiable Ruleset Evidence

### Added
- `Scripts/github_p0_ruleset.py` als zentrale, fail-closed Vertragslogik für den GitHub-P0-Schutz.
- `Scripts/github_p0_public_verify.py` als tokenfreier Live-Verifier direkt gegen die öffentliche GitHub-REST-API.
- `.github/workflows/p0-infrastructure-observer.yml` als täglicher/manueller GitHub-hosted Infrastruktur-Observer ohne Self-hosted Runner und ohne Admin-Secret.
- Regressionstests für Ruleset-Enforcement, Required Checks, Strictness, Bypass, Delete-/Force-Push-Sperren und öffentlichen Live-Verifier.

### Changed
- `github_p0_admin.py` unterstützt `--apply-ruleset` als sicheres Create-or-Update mit Duplikat-Sperre und serverseitigem Read-back.
- `github_p0_status.py` arbeitet Ruleset-first und nutzt klassische Branch Protection nur noch als Fallback.
- `p0_preflight.py` beweist den GitHub-Schutz über `github_p0_public_verify.py` ohne GitHub-Login oder Token.
- Ruleset-Payload, Statusprüfung und Tests verwenden denselben zentralen Contract, um Soll-/Ist-Drift zu vermeiden.
- `WICHTIG.md` auf W-2026-08-27-007 aktualisiert und `CODEQUALITÄT.md` append-only um CQ-2026-08-27-007 erweitert.

### Evidence state
- GitHub-Ruleset-Liste meldete vor dem realen Apply weiterhin `[]`; daher noch kein Infrastruktur-PASS.
- `main` meldete zuletzt weiterhin `protected=false`; klassische Branch Protection bleibt nur Fallback.
- code-seitige Ruleset-Evidence-Schicht ist implementiert; neuester PR-Head wird erneut über Hosted CI abgenommen.
- Self-hosted UE-5.8 Runner weiterhin nicht real nachgewiesen.
- CP1 Runtime weiterhin `UNOBSERVED/BLOCKED`; kein Runtime-PASS behauptet.

---

## 2026-08-27 — P0 Admin Diagnostics

### Added
- `github_p0_admin.py --doctor` als read-only Administrations-Fähigkeitsprüfung.
- explizite Prüfung von Repository-Adminrechten für `provoware/bunkergame`.
- Fehlerklassifikation für GitHub 403, 404, 422 und unbekannte Fehler.
- `Docs/GITHUB_ADMIN_DIAGNOSE.md` als Laienanleitung für Branch-Protection-Fehler.
- zusätzliche Hosted-Regressionstests für Rechte-, Serverstatus- und Fehlerklassifikation.

### Changed
- Branch Protection wird nur noch nach bestätigtem Repository-Adminrecht angewendet.
- `github_p0_status.py` liest zuerst `main.protected` über den normalen Branch-Endpunkt.
- eine vollständige Protection-Detailprüfung erfolgt erst, wenn GitHub `protected=true` meldet.
- Maintain-/Push-Rechte werden ausdrücklich nicht mit Repository-Administration verwechselt.

### Evidence state
- `main` meldete vor dieser Iteration serverseitig weiterhin `protected=false`.
- neue Diagnose- und Regressionsebene implementiert; aktueller PR-Head wird über Hosted CI abgenommen.
- reale Branch-Protection-Aktivierung weiterhin externe Adminaktion.
- CP1 Runtime weiterhin `UNOBSERVED/BLOCKED`.

---

## 2026-08-27 — P0 Operator Experience / One-Command Preflight

### Added
- `Scripts/p0_preflight.py` als read-only Ein-Befehl-Vorprüfung vor dem realen UE-Lauf.
- `--full`-Modus für die echte UE-5.8-Maschine inklusive Runner-Readiness.
- zusätzliche Regressionstests für die Next-Best-Action-Entscheidungslogik.

### Changed
- P0-Ablauf führt jetzt statische Prüfung → Repository Quality → GitHub Branch Gate → optional UE-Readiness in fester Reihenfolge aus.
- bei Fehlern wird der erste sinnvolle Blocker priorisiert statt mehrere Reparaturpfade gleichzeitig vorzuschlagen.
- `Docs/GITHUB_P0_SETUP.md` auf den neuen Ein-Befehl-Ablauf synchronisiert.
- Readiness-Dokumentation auf Schema v2, echte `Build.version`-Prüfung und 30-Minuten-Freshness-Gate aktualisiert.

### Evidence state
- Hosted `static-and-contract`: auf vorheriger P0-Härtungsiteration PASS.
- Hosted `repository-quality`: auf vorheriger P0-Härtungsiteration PASS.
- neuer P0-Preflight: implementiert; aktueller Head wird erneut über CI abgenommen.
- Branch Protection: weiterhin externe Adminausführung erforderlich.
- Self-hosted UE-5.8 Runner: weiterhin externe Maschinenarbeit erforderlich.
- CP1 Runtime: weiterhin `UNOBSERVED/BLOCKED`.

---

## 2026-08-27 — Dokumentations-/GitHub-Control-Plane Iteration 2

### Added
- `WICHTIG.md` als jeweils aktueller, genau einpunktiger Verbesserungsfokus.
- `CODEQUALITÄT.md` als append-only Qualitätsjournal mit Grund, Wirkung und technischem Effekt.
- `Scripts/repo_quality.py` als UE-unabhängiger autonomer Repository Quality Guard.
- `Scripts/iteration_guard.py` zur technischen Durchsetzung der Iterations-Lernschleife.
- `.github/workflows/quality-guard.yml` für PRs, `main`, manuelle Läufe und wöchentliche Vollprüfung.

### Changed
- `Docs/PROJEKTSTATUS.md` auf CURRENT-TRUTH-/P0-/Evidence-Schema synchronisiert.
- `CONTRIBUTING.md` auf denselben Entwicklungsvertrag ausgerichtet.
- Dokumentrollen, Definition of Done und GitHub-Gates klarer getrennt.

### Automatic checks added
- erforderliche Kern-Dokumente vorhanden
- JSON-Dateien parsebar
- Python-Dateien syntaktisch gültig
- lokale Links im Dokumentations-Cockpit gültig
- keine offensichtlichen Merge-Konfliktmarker
- keine verbotenen generierten Ordner/Dateien
- externe GitHub Actions nur mit vollständigem Commit-SHA
- `WICHTIG.md` enthält genau einen aktuellen Fokus
- `CODEQUALITÄT.md` enthält eindeutige CQ-IDs
- bei normalen PR-Iterationen müssen `WICHTIG.md` und `CODEQUALITÄT.md` geändert werden
- bestehender Inhalt von `CODEQUALITÄT.md` darf nur erweitert, nicht umgeschrieben werden

### Current P0
- `main` Branch-Protection/Ruleset aktivieren.
- `Validate` und `Quality Guard` als Required Checks setzen.
- Self-hosted UE-5.8-Runner registrieren und prüfen.
- `UE58_RUNNER_ENABLED=true` erst nach erfolgreicher Runner-Bereitschaft setzen.

### Evidence state
- Headless/static verification: verfügbar
- GitHub Quality Guard: neu integriert, CI-Nachweis steht für den aktuellen Head aus
- UE-5.8 Runtime: weiterhin `UNOBSERVED/BLOCKED`
- kein Runtime-PASS behauptet

---

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