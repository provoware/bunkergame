# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Vorschlag. Historische Vorschläge stehen append-only in `CODEQUALITÄT.md`.

## W-2026-10-24-018 — CP1-Laufzeitnachweise nur aus eindeutigem JSON einlesen

**Kategorie:** P0 / Runtime-Gate / Integrität  
**Priorität:** P0  
**Status:** IMPLEMENTED auf Entwicklungszweig; GitHub-Validate/Quality Guard und UE-Runtime noch getrennt zu prüfen.  
**Nutzen:** 8/10 · **Änderungsrisiko:** niedrig bis mittel

### Beobachtung
`Scripts/cp1_gate_runtime.py` las die beiden für das CP1-Gate entscheidenden JSON-Dateien mit Pythons tolerantem Standardparser. Doppelte Schlüssel konnten widersprüchliche Angaben überdecken; `NaN`/`Infinity` wurden trotz ungültigem JSON akzeptiert. Die Dateigröße war unbegrenzt und symbolische Links wurden verfolgt.

### Verbesserungsvorschlag
Laufzeitnachweis und Telemetrie bereits beim Einlesen strikt und einheitlich prüfen: doppelte Schlüssel, nicht endliche Zahlen, ungültiges UTF-8, symbolische Links und Dateien über 4 MiB kontrolliert abweisen. Den gültigen Objekt-Normalfall und acht Testmethoden in den verpflichtenden Validate-Lauf aufnehmen.

### Grund
Ein CP1-GREEN darf niemals aus mehrdeutigen oder unkontrolliert großen Eingabedaten entstehen. Diese Härtung betrifft ausschließlich den Nachweis-Lesepfad; sie erzeugt keinen Unreal-Runtime-Erfolg.

### Wirkung und Abnahmekriterien
- Ungültige CP1-Nachweis- und Telemetriedateien führen kontrolliert zu BLOCKED, ohne Ausnahme.
- Gültiges JSON bleibt mit unveränderten Rohbytes für die SHA-256-Prüfung lesbar.
- Acht Regressionstestmethoden laufen in Validate und Quality Guard.
- GitHub-CI am finalen PR-HEAD ist separat nachzuweisen; UE 5.8, CP1, Gameplay und Branchschutz bleiben offen.
