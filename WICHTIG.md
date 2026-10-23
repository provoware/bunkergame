# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Vorschlag. Historische Vorschläge stehen append-only in `CODEQUALITÄT.md`.

## W-2026-10-24-017 — Ungültige JSON-Zahlen in UE-Versiondateien abweisen

**Kategorie:** P0 / Runner-Readiness / Evidence-Integrität  
**Priorität:** P0  
**Status:** IMPLEMENTED auf Entwicklungszweig; isolierter Parser-Negativ-/Positivtest 7/7 PASS (24.10.2026); GitHub-Gesamtprüfung und UE-5.8-Runtime separat nachzuweisen.  
**Nutzen:** 7/10 · **Änderungsrisiko:** niedrig

### Beobachtung
Pythons Standard-JSON-Parser akzeptiert die nicht normgerechten Werte `NaN`, `Infinity` und `-Infinity` auch in verschachtelten Metadaten. Die bisherige Runner-Versionprüfung konnte dadurch ein ungültiges `Build.version` als gültige UE-5.8-Readiness akzeptieren.

### Verbesserungsvorschlag
Nicht endliche JSON-Konstanten bereits beim Einlesen konsequent als kontrolliertes FAIL zurückweisen. Vier Negativfälle und einen gültigen Metadaten-Normalfall in die bereits verpflichtende Runner-Testdatei aufnehmen.

### Grund
Ein Maschinenprofil darf nur aus syntaktisch gültigem, eindeutigem JSON abgeleitet werden. Der Readiness-Status ist eine Vorbedingung für spätere Runtime-Prüfungen und darf ungültige Eingabedaten nicht still akzeptieren.

### Wirkung und Abnahmekriterien
- `NaN`, `Infinity` und `-Infinity` werden auch in verschachtelten Feldern ohne Absturz abgewiesen.
- Endliche numerische Metadaten sowie der UE-5.8-Normalfall bleiben akzeptiert.
- Zentrale Validate- und Quality-Guard-Prüfungen müssen am finalen GitHub-HEAD erfolgreich sein.
- CP1-Runtime, Spielverläufe und Main-Branchschutz bleiben ausdrücklich eigene offene Pflichtprüfungen.
