# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Vorschlag. Historische Vorschläge stehen append-only in `CODEQUALITÄT.md`.

## W-2026-10-24-020 — Tiefe CP1-JSON-Strukturen kontrolliert zurückweisen

**Kategorie:** P0 / Runtime-Gate / Robustheit der Nachweisprüfung
**Priorität:** P0
**Status:** IMPLEMENTED auf Entwicklungszweig; GitHub Validate #40099100013 und Quality Guard #40099100020 auf Code-HEAD `2a35870e998911d9c3cb6b73f2f80c10cdfd5f66` PASS; endgültiger Dokumentations-HEAD erneut zu prüfen; echter UE-5.8-Lauf BLOCKED.
**Nutzen:** 7/10 · **Änderungsrisiko:** niedrig

### Beobachtung
Auch bei maximal 4 MiB Eingabe können tief verschachtelte JSON-Arrays oder -Objekte `json.loads` zu `RecursionError` bringen. Der bisherige CP1-Loader fängt diese Ausnahme nicht ab: Das Gate bricht mit einem Python-Traceback ab, statt einen kontrollierten BLOCKED-Befund zu liefern.

### Verbesserungsvorschlag
`RecursionError` in der bestehenden fail-closed Fehlerbehandlung abfangen und für zwei reale Parser-Grenzfälle (20.000 verschachtelte Arrays und Objekte) Regressionen ergänzen. Keine Rekursionstiefe global verändern und keine zulässigen JSON-Inhalte umdeuten.

### Grund
Ungültige oder nicht verarbeitbare Nachweisdateien dürfen den Prüfer nicht unkontrolliert beenden. Der bestehende gültige Normalfall bleibt unverändert.

### Wirkung und Abnahmekriterien
- Tiefe JSON-Strukturen liefern einen kontrollierten Fehler mit `None` für Daten und Rohbytes.
- Vorhandene elf CP1-Ladertests bleiben grün, neuer Test mit zwei Teilfällen ebenfalls.
- Validate und Quality Guard am finalen HEAD nachweisen.
- **NEXT BEST ACTION:** echten P0-Ruleset-Schutz und vertrauenswürdigen UE-5.8-Runner nachweisen; CP1 Build/Spawn/Movement/Telemetrie anschließend in einem echten Lauf prüfen.
- Keine Runtime-Freigabe, kein Merge und kein Release ohne vollständige Gates.
