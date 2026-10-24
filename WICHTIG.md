# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Vorschlag. Historische Vorschläge stehen append-only in `CODEQUALITÄT.md`.

## W-2026-10-24-019 — CP1-Evidence vor Dateiaustausch beim Öffnen schützen

**Kategorie:** P0 / Runtime-Gate / Dateiintegrität
**Priorität:** P0
**Status:** IMPLEMENTED auf Entwicklungszweig; GitHub-CI auf Code-HEAD 6e56fd6d7648e3e07367c6c525ff17bdb1a36a12 PASS (Validate #40078953659, Quality #40078953654); finaler Dokumentations-HEAD separat zu prüfen; Unreal-5.8-Runtime BLOCKED.
**Nutzen:** 8/10 · **Änderungsrisiko:** niedrig bis mittel

### Beobachtung
Die bisherige `is_symlink()`-/`is_file()`-/`stat()`-Vorprüfung erfolgte getrennt vom eigentlichen `open()`. Ein zeitgleicher Austausch der Datei zwischen Prüfung und Öffnen konnte unter Linux den Symlink-Schutz umgehen oder einen ersetzten FIFO-Lesepfad blockieren.

### Verbesserungsvorschlag
Den CP1-Nachweis auf Unix über `O_NOFOLLOW` und `O_NONBLOCK` öffnen; anschließend den tatsächlich geöffneten Dateideskriptor mit `fstat` als reguläre, höchstens 4 MiB große Datei prüfen. Die strikte JSON- und SHA-256-Prüfung beibehalten. Drei Regressionstestmethoden ergänzen.

### Grund
Ein CP1-Gate darf die vorab geprüfte Datei nicht mit einer nachträglich ausgetauschten Datei verwechseln. Es dürfen weder Umleitungen noch blockierende Sonderdateien einen Nachweis ersetzen.

### Wirkung und Abnahmekriterien
- Symlink-Austausch während des Öffnens wird auf Systemen mit `O_NOFOLLOW` kontrolliert abgewiesen.
- FIFO-Austausch blockiert nicht und führt zu BLOCKED.
- Gültige JSON-Rohbytes und bestehende Größen-, Duplikat- und Hashprüfungen bleiben unverändert.
- GitHub Validate/Quality Guard auf dem endgültigen HEAD nachweisen; keine Runtime-Freigabe ohne echten UE-5.8-Lauf.
- Plattformgrenze: Ohne `O_NOFOLLOW` ist die atomare Symlink-Sperre nicht nachgewiesen und muss separat auf der Zielplattform geprüft werden.
