# CHANGELOG

## 2026-08-27 — UE 5.8 Runner Bootstrap Acceptance

### Added
- `.github/workflows/ue58-runner-bootstrap.yml` als manueller, CP1-freier Self-hosted-Runner-Abnahmepfad.
- `Scripts/runner_bootstrap_contract.py` als fail-closed Vertrag für GitHub-Run, Job, Pflichtlabels, Pflichtschritte und Freshness.
- `Scripts/runner_bootstrap_evidence.py` für maschinenlesbare Bootstrap-Evidence aus GitHub-Jobkontext + Readiness v3.
- `Scripts/github_runner_bootstrap_public_verify.py` als tokenfreier Live-Verifier für aktuellen `main`, Workflow-Run, Runnername und Job-Labels.
- `Scripts/tests/test_runner_bootstrap_acceptance.py` für Scheduler-/Label-/Freshness-/Aktivierungs-Regressionen.

### Changed
- `github_p0_admin.py --enable-runner-variable` akzeptiert lokale Readiness nicht mehr als alleinige Aktivierungsautorität.
- Runner-Aktivierung verlangt einen frischen öffentlichen `UE58_RUNNER_BOOTSTRAP: PASS` auf dem aktuellen `main`.
- Runner-Aktivierung ist über den Helper nur noch zusammen mit `--apply-ruleset` möglich.
- Admin-Checkout muss unmittelbar vor dem Variablen-Write auf exakt aktuellem `main` stehen und sauber sein.
- `p0_preflight.py --full` prüft jetzt zusätzlich den öffentlichen Runner-Bootstrap-Serverbeweis.
- `WICHTIG.md` auf W-2026-08-27-011 aktualisiert.
- `CODEQUALITÄT.md` append-only um CQ-2026-08-27-011 erweitert.

### Evidence state
- Bootstrap-Architektur implementiert; echter GitHub-Job auf einem UE-5.8-Self-hosted-Runner noch nicht ausgeführt.
- kein `UE58_RUNNER_BOOTSTRAP: PASS` behauptet.
- reales P0-Ruleset weiterhin nicht nachgewiesen.
- CP1 Runtime weiterhin `UNOBSERVED/BLOCKED`.

---

## 2026-08-27 — CP1 Runtime Evidence Contract v3

### Added
- `Scripts/cp1_runtime_evidence_contract.py` als zentrale Runtime-/Telemetry-Vertragslogik.
- Runtime Evidence v3 mit Repository-, Git-HEAD-, Maschinen-, Freshness-, Run-ID- und Telemetrie-Dateibindung.
- Telemetrie v3 mit vom C++-Automationstest zurückgeschriebener `run_id`.
- separate Runtime-Evidence-Regressionstests inklusive stale/kopiert/manipuliert/Hash-/Run-ID-/Typ-Drift.

### Changed
- alte Runtime-Evidence, Telemetrie und Automation-Reports werden vor einem neuen Versuch entfernt.
- C++-Automation verlangt `-CP1EvidenceRunId` und schreibt dieselbe ID in die Telemetrie.
- `cp1_gate_runtime.py` validiert aktuellen Checkout, Maschine, Freshness und reale Telemetrie-Datei erneut.
- `Scripts/run_cp1_ue58.py` ist die kanonische Folge Readiness → Preflight → Runtime → Gate.

### Evidence state
- PR #7 Hosted `static-and-contract`: PASS.
- PR #7 Hosted `repository-quality`: PASS.
- `cp1-runtime`: SKIPPED ohne real freigegebenen UE-5.8-Runner.
- kein echter CP1-Runtime-PASS behauptet.

---

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
- code-seitige Ruleset-Evidence-Schicht ist implementiert.
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
- reale Branch-Protection-/Ruleset-Aktivierung weiterhin externe Adminaktion.
- CP1 Runtime weiterhin `UNOBSERVED/BLOCKED`.

---

## 2026-08-27 — P0 Operator Experience / One-Command Preflight

### Added
- `Scripts/p0_preflight.py` als read-only Ein-Befehl-Vorprüfung vor dem realen UE-Lauf.
- `--full`-Modus für die echte UE-5.8-Maschine inklusive Runner-Readiness.
- zusätzliche Regressionstests für die Next-Best-Action-Entscheidungslogik.

### Changed
- P0-Ablauf führt statische Prüfung → Repository Quality → GitHub Gate → optional UE-Readiness in fester Reihenfolge aus.
- bei Fehlern wird der erste sinnvolle Blocker priorisiert statt mehrere Reparaturpfade gleichzeitig vorzuschlagen.
- `Docs/GITHUB_P0_SETUP.md` auf den Ein-Befehl-Ablauf synchronisiert.

### Evidence state
- Hosted `static-and-contract`: PASS auf den abgenommenen Folgeiterationen.
- Hosted `repository-quality`: PASS auf den abgenommenen Folgeiterationen.
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
- `main` Ruleset aktivieren.
- `Validate` und `Quality Guard` als Required Checks setzen.
- Self-hosted UE-5.8-Runner registrieren und über Bootstrap prüfen.
- Runtime erst nach Bootstrap-PASS freigeben.

### Evidence state
- Headless/static verification: verfügbar
- GitHub Quality Guard: aktiv
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
