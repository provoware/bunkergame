# BUNKER BEATS — AUTOMATISCHE QUALITÄT

> Ziel: möglichst viele Fehler **vor** einem teuren UE-Runtime-Lauf automatisch erkennen, ohne fachliche PASS-Zustände zu erfinden.

## Bereits aktiv

### 1. Validate
- CP1-/Contract-Checks
- Headless-Tests
- Failure-/Learning-Logik
- Fake-Evidence-Schutz

### 2. Quality Guard
- Pflichtdateien
- JSON-Parsing
- Python-Syntax
- lokale Dokumentlinks
- Merge-Konfliktmarker
- generierte Pfade
- Action-SHA-Pinning
- Qualitätsgedächtnis

### 3. Iteration Guard
- `WICHTIG.md` muss im PR mitgeführt werden
- `CODEQUALITÄT.md` muss erweitert werden
- bestehende CODEQUALITÄT-Historie darf nicht umgeschrieben werden
- exakt ein neuer CQ-Eintrag je normaler PR-Iteration

### 4. Runner Readiness
- UE-Pfad
- UnrealEditor
- Build-Skript
- Python
- Schreibrechte
- Speicherplatz
- sauberer Arbeitsstand

## Sinnvolle nächste autonome Erweiterungen

### A. C++ Format Check — nach bestätigter UE-Toolchain
**Werkzeug:** `clang-format` im Check-Modus.  
**Nutzen:** einheitliche C++-Formatierung ohne manuelle Diskussionen.  
**Wichtig:** Version an die bestätigte UE-5.8-Toolchain koppeln; nicht blind irgendeine Systemversion verwenden.

### B. C++ Static Analysis
**Werkzeug:** `clang-tidy` oder UE-kompatibler statischer Analyzer.  
**Nutzen:** Nullpointer-, Lifetime-, Include- und API-Probleme früher erkennen.  
**Bedingung:** Compile-Commands/UE-Build-Kontext zuverlässig verfügbar.

### C. Markdown Link Check erweitert
Der aktuelle Guard prüft lokale Cockpit-Links ohne Netzwerk. Später optional zusätzlich externe Links in einem geplanten Nightly-Job prüfen, damit temporäre Netzausfälle normale PRs nicht blockieren.

### D. Config Schema Validation
Für zentrale JSON-Dateien formale Schemas einführen und automatisch prüfen. Das ist stärker als reines JSON-Parsing und erkennt fehlende/falsch typisierte Felder.

### E. Secret Scan
Vor Merge auf versehentlich eingecheckte Tokens, Schlüssel und Zugangsdaten prüfen. Bei Einführung sollte die False-Positive-Strategie dokumentiert werden.

### F. Dependency/Supply-Chain Guard
Dependabot beibehalten und zusätzlich prüfen:
- externe Actions nur SHA-gepinnt
- keine unkontrollierten neuen Drittanbieter-Actions
- neue Abhängigkeiten bewusst dokumentieren

### G. Test Impact Mapping
Geänderte Dateien automatisch auf minimale Pflicht-Testgruppen abbilden. Effekt: schnellere PRs, ohne relevante Tests auszulassen.

### H. Nightly Full Headless Regression
Ein geplanter Lauf kann größere deterministic matrices ausführen, die für jeden kleinen PR zu teuer wären.

### I. Runtime Evidence Schema Guard
Runtime-Artefakte nach einem UE-Lauf formal validieren:
- Run-ID
- Commit-SHA
- Engine-Version
- Zeitstempel
- Test-ID
- Position/Velocity/Frame-Time
- Gate-Ergebnis

So kann eine formal unvollständige Evidence nicht als gültiger Beweis weitergereicht werden.

### J. Runner Health Watch
Auf dem Self-hosted Runner vor jedem Runtime-Test:
- UE-Version
- Toolchain
- freier Speicher
- Git-Zustand
- Schreibrechte
- Prozessreste
- vorherige stale Evidence

Der erste Teil davon ist bereits in `Scripts/runner_readiness.py` umgesetzt.

## Nicht empfohlen

### Auto-Commit-Formatter auf jedem PR
Automatisches Umschreiben und Pushen durch CI erzeugt unnötige Commit-Schleifen und kann Entwickleränderungen verdecken.

Bevorzugt:

```text
Formatter lokal mit --write
CI-Formatter nur mit --check
```

### Auto-Fix von Runtime-Gates
Ein automatischer Reparaturmechanismus darf niemals Testschwellen verändern, Evidence fälschen oder Fehler durch Abschwächung des Gates „lösen“.

## Priorisierte Reihenfolge

1. Quality Guard stabil GREEN
2. Branch-Protection aktiv
3. Runner Readiness auf echter Maschine
4. CP1 Runtime
5. Runtime-Evidence Schema Guard
6. Config Schema Validation
7. C++ Format/Static Analysis mit bestätigter UE-Toolchain
8. Test Impact Mapping
9. Nightly Full Regression
