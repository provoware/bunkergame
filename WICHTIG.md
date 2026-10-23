# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Vorschlag. Historische Vorschläge stehen append-only in `CODEQUALITÄT.md`.

## W-2026-10-23-016 — Mehrdeutige oder unlesbare UE-Versiondateien sicher ablehnen

**Kategorie:** P0 / Runner / Integrität / Regression  
**Priorität:** P0  
**Status:** IMPLEMENTED; GitHub-Validate und Quality Guard auf geprüftem Code-HEAD `d810e8abdb642d18d53ed2bfe4fc58450f21803d` PASS (23.10.2026)  
**Nutzen:** 9/10 · **Änderungsrisiko:** niedrig

### Beobachtung
Ein nicht UTF-8-kodiertes `Build.version` löste bisher eine unbehandelte Ausnahme aus. Doppelte JSON-Schlüssel überschrieben unbemerkt frühere Werte, sodass ein mehrdeutiges Versionsprofil als gültig gelten konnte.

### Verbesserungsvorschlag
Fehlerhafte UTF-8-Kodierung und doppelte JSON-Schlüssel in der Versionsdatei kontrolliert ablehnen; Regressionstests für beide Fehlerarten und den gültigen UE-5.8-Normalfall ausführen.

### Grund
Die Runner-Bereitschaft muss auf eindeutigen Daten beruhen; widersprüchliche Angaben dürfen niemals als verlässlicher Versionsnachweis gelten.

### Wirkung und Abnahmekriterien
- Ungültiges UTF-8 liefert ein geordnetes FAIL statt einer Ausnahme.
- Doppelte Versionsschlüssel und verschachtelte Duplikate liefern FAIL.
- Eindeutige UE-5.8-Version liefert weiterhin PASS in der isolierten Parserprüfung.
- `ci_verify.py`, `repo_quality.py` und Iteration Guard bestehen auf dem neuen GitHub-HEAD.
- UE-5.8-Runner, echter CP1-Lauf und Main-Branchschutz bleiben eigenständige offene Pflichten.
