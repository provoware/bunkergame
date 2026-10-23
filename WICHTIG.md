# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Vorschlag. Historische Vorschläge stehen append-only in `CODEQUALITÄT.md`.

## W-2026-10-23-015 — UE-5.8-Runner-Readiness bei fehlerhafter Build.version kontrolliert sperren

**Kategorie:** P0 / Runner / Sicherheit / Regression  
**Priorität:** P0  
**Status:** IMPLEMENTIERT; GitHub-Prüflauf auf dem Entwicklungszweig ausstehend  
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
- `ci_verify.py`, `repository-quality` und Iteration Guard auf dem tatsächlichen PR-HEAD PASS
- ein echter UE-5.8-Lauf wird erst mit eigener Runtime-Evidence bewertet
