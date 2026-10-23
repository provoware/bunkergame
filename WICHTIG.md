# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Vorschlag. Historische Vorschläge stehen append-only in `CODEQUALITÄT.md`.

## W-2026-10-23-015 — UE-5.8-Runner-Readiness bei fehlerhafter Build.version kontrolliert sperren

**Kategorie:** P0 / Runner / Sicherheit / Regression  
**Priorität:** P0  
**Status:** IMPLEMENTIERT; GitHub-Validate und Quality Guard auf geprüftem HEAD `40f94213d732cf5349fd8c97096a2e8d6a193d5b` PASS  
**Nutzen:** 9/10 · **Änderungsrisiko:** niedrig

### Beobachtung
`Scripts/runner_readiness.py` las `Build.version` als JSON und verwendete anschließend `.get()` ohne Prüfung des äußeren Datentyps. Gültiges JSON mit Array, Zahl, Text, Boolean oder null löste dadurch einen unbehandelten Fehler aus, statt die Maschinenbereitschaft geordnet abzulehnen.

### Verbesserungsvorschlag
Vor dem Zugriff auf Versionsfelder ausdrücklich ein JSON-Objekt verlangen. Sechs Negativfälle als Regressionstest ergänzen und die gesamte Runner-Bindungs-Testdatei verbindlich in `Scripts/ci_verify.py` aufnehmen; den CI-Aufruf durch einen Verdrahtungsvertrag schützen.

### Grund und Nachweisgrenzen
Der Readiness-Fehler darf nicht mit einem CP1-Gameplay-Fehler verwechselt werden. Auch nach erfolgreichem statischem Test bleiben der echte UE-5.8-Runner, CP1-Runtime, Main-Branchschutz und persönliche Endabnahme unabhängig und offen.

### Wirkung und Fertig, wenn
- Nicht-Objekt-`Build.version` ergibt `FAIL` ohne Ausnahme
- sechs neue Negativfälle und vorhandene Runner-Bindungstests bestehen
- `ci_verify.py`, `repository-quality` und Iteration Guard auf dem geprüften HEAD PASS: [Validate](https://github.com/provoware/bunkergame/actions/runs/39954719607), [Quality Guard](https://github.com/provoware/bunkergame/actions/runs/39954719562)
- ein echter UE-5.8-Lauf wird erst mit eigener Runtime-Evidence bewertet
