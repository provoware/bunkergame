# BUNKER BEATS — Vorrelease-Nachweis 2026-10-23, Runner Build.version

## Scope und Git-Stand
- Repository: `provoware/bunkergame`.
- Ausgangs-HEAD / gestapelter Basis-PR #14: `a419999912a9b8118026e56c219d01d23b1d09fb`.
- Tatsächlich geprüfter Code-HEAD: `d810e8abdb642d18d53ed2bfe4fc58450f21803d`.
- Entwicklungszweig: `fix/runner-buildversion-strict-20261023-1929` (auf PR #14 gestapelt; Hauptzweig unverändert).
- PR: https://github.com/provoware/bunkergame/pull/15
- Hauptzweig beim Beginn der Arbeit: `9f2f4db4689291295938bce9e245590eb525bc8c`.

## Pflichtpaket und Ergebnis
| Bereich | Status | Nachweis / Begründung |
|---|---|---|
| Fehlendes UTF-8 in `Build.version` | PASS (isoliert + CI) | Kontrolliertes FAIL statt unbehandeltem UnicodeDecodeError; Regression `test_invalid_utf8_engine_version_fails_closed`. |
| Doppelte JSON-Schlüssel | PASS (isoliert + CI) | Haupt- und verschachtelte Duplikate werden abgewiesen; Regression `test_duplicate_version_keys_are_rejected`. |
| Eindeutige UE 5.8 | PASS (Parser) | Positiver Normalfall `test_valid_engine_version_still_passes`. Kein Runtime-PASS. |
| GitHub Validate / static-and-contract | PASS | https://github.com/provoware/bunkergame/actions/runs/39995769429 auf `d810e8abdb642d18d53ed2bfe4fc58450f21803d`; `CI_VERIFY: PASS`; Runner-Bindung 25 Tests. |
| GitHub Quality Guard / repository-quality | PASS | https://github.com/provoware/bunkergame/actions/runs/39995769898 auf `d810e8abdb642d18d53ed2bfe4fc58450f21803d`; 135 Python-Tests; `QUALITY_GUARD: PASS`, `ITERATION_GUARD: PASS`. |
| CP1 UE-5.8 Runtime | SKIPPED / BLOCKED | https://github.com/provoware/bunkergame/actions/runs/39995769449; keine UE-5.8-Maschine und keine frische CP1-Evidence. |
| P0 Main-Branchschutz | BLOCKED | Keine Änderung an GitHub-Adminschutz oder Required Checks. |
| Vorrelease-Pflichtmatrix | NICHT FREIGEGEBEN | 0/40 vollständig für Release nachgewiesen; `Docs/VORRELEASE_PFLICHTMATRIX.json` bleibt unverändert. |

## Weitere verbindliche Release-Pflichten
Echter UE-5.8-Build, Character Spawn und Bewegung samt Frame-Time/Position/Velocity, verifizierter Runner-Bootstrap, vollständige Spielverläufe, atomare Spielstände und Recovery, Gameplay/Balance, 800x600 und 200%-Skalierung, Tastatur/Fokus, Performance, Installation, Dokumentation und technischer Gesamtstatus. Persönliche Kubuntu-/Sichtabnahme erst nach vollständig geprüfter eingefrorener Vorrelease-Version.

## Nächste konkrete Implementierung
Auf einer vertrauenswürdigen UE-5.8-Maschine den Runner mit vorhandenen Sicherheitsregeln und Pflichtlabels bereitstellen, Bootstrap-Readiness an aktuellen Git-HEAD binden, danach `RUN_CP1_UE58_ALL.sh` ausführen und frische maschinenlesbare CP1-Evidence als GitHub-Artefakt auswerten. Bei Blockade unabhängige P0-Prüfungen desselben Spiels fortsetzen. Keine Gate-Umgehung, kein Merge, kein Release ohne ausdrückliche Nutzerfreigabe.

*Hinweis zur Evidence-Freshness:* Dieses Dokument wurde **nach** dem geprüften Code-HEAD hinzugefügt; die nachfolgende Dokumentations-Commit-SHA ist nicht identisch mit dem oben referenzierten Code-HEAD. Ein neuer CI-Lauf auf dem Dokumentations-HEAD ist separat auszuwerten.
