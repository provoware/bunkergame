# BUNKER BEATS — Vorrelease-Nachweis 24.10.2026, CP1-JSON-Integrität

## Tatsächlich beobachteter GitHub-Stand
- Repository: `provoware/bunkergame`, `main` `9f2f4db4689291295938bce9e245590eb525bc8c`, Branchschutz bei API-Leseprüfung: `protected=false`.
- Ausgangs-HEAD: `91a822830bcec14d8ab1c3c13128eb2c3d6fc044` (Entwurfs-PR #16). Neuer separater Entwicklungszweig: `fix/cp1-evidence-json-strict-20261024-0536`.
- Neue Änderung wird auf PR #16 gestapelt; kein Push auf `main`, kein Merge und keine Release-Freigabe.
- Grundlage: Root-`AGENTS.md`, `Docs/AGENTS.md`, `README.md`, `Docs/TODO.md`, `Docs/VORRELEASE_PFLICHTMATRIX.json`, bestehende CP1-Tests und CI.

## Reproduzierter Fehler
`json.loads('{"status":"RED","status":"GREEN"}')` ergibt mit Pythons Standardparser `{"status":"GREEN"}`; `json.loads` akzeptiert zudem standardmäßig `NaN`. Das CP1-Gate verwendete bisher diesen toleranten Parser für Runtime-Evidence und Telemetrie, ohne Dateigrößenbegrenzung und ohne Symlink-Sperre.

## Implementierung
- `Scripts/cp1_gate_runtime.py`: JSON-Schlüssel müssen eindeutig sein, nicht endliche Konstanten werden abgelehnt, UTF-8-Fehler kontrolliert behandelt, Symlinks und Dateien > 4 MiB blockiert. Die originalen Rohbytes bleiben für die Telemetrie-Hashprüfung erhalten.
- `Scripts/tests/test_cp1_gate_runtime_loader.py`: acht Testmethoden für Normalfall, doppelte Schlüssel, nicht endliche Zahlen, UTF-8, Wurzeltyp, Größe, Symlink und fehlende Datei.
- `Scripts/ci_verify.py` und `Scripts/tests/test_prerelease_ci_wiring.py`: neue Tests verbindlich in Validate eingebunden.
- `Docs/VORRELEASE_PFLICHTMATRIX.json`: CP1-Evidence- und Regressionstest-Referenzen sowie nächste Prüfhandlungen präzisiert; Statuswerte bewusst nicht hochgestuft.
- WICHTIG, append-only CODEQUALITÄT, TODO, CHANGELOG, README und Runtime-Dokumentation synchronisiert.

## Prüfstatus
| Prüfung | Status | Evidenz |
|---|---|---|
| Python-Standardparser reproduziert Mehrdeutigkeit | PASS (isoliert) | Doppelschlüssel reduziert zu GREEN; NaN wird angenommen. Kein Repository-Test. |
| Acht neue Tests auf echtem Branch-Code | UNOBSERVED | GitHub Validate und Quality Guard nach PR-Erstellung prüfen. |
| CI-Verdrahtung und vollständige Regression | UNOBSERVED | GitHub-Workflow auf finalem PR-HEAD auswerten. |
| UE-5.8-Build, CP1 Spawn/Movement/Telemetry | BLOCKED | Kein vertrauenswürdiger UE-5.8-Runner; kein echter Runtime-Lauf. |
| GitHub-`main`-Ruleset | BLOCKED | Live-`main.protected=false`; keine Schutzumgehung. |
| Save/Restore, 800×600/200 %, Gameplay, Leistung | PLANNED/UNOBSERVED | Keine Laufzeit- oder Oberflächenabnahme. |

**Vorrelease-Pflichtmatrix:** 0/40 vollständig freigegeben; 3 BLOCKED, 6 UNOBSERVED, 14 IMPLEMENTED, 17 PLANNED. `candidate_frozen=false`; persönliche Abnahme und Release-Freigabe ausstehend.

## Nächste sichere Implementierung
Zuerst Hosted-CI auf dem neuen Entwurfs-PR auswerten und Fehler beheben. Anschließend echtes GitHub-P0-Ruleset mit unabhängiger Liveprüfung herstellen, vertrauenswürdigen UE-5.8-Runner bereitstellen und den vollständigen CP1-Lauf auf einem aktuellen, sauberen Checkout ausführen. Solange diese externen Schritte fehlen, weitere unabhängige P0-Arbeit nur mit reproduziertem Befund. **Kein Merge, kein Release, keine vorgezogene persönliche Endabnahme.**

**Finaler Branch-HEAD und GitHub-CI:** werden nach den tatsächlichen Läufen im Entwurfs-PR dokumentiert; keine vorweggenommene PASS-Behauptung.
