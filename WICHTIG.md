# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-002 — GitHub-P0-Adminschritte fehlersicher und nachprüfbar machen

**Kategorie:** Schwachstelle / Bedienung / GitHub-Administration  
**Priorität:** P0  
**Status:** 🟡 VORBEREITET — externe Adminausführung erforderlich  
**Nutzen:** 10/10  
**Aufwand:** 3/10  
**Risiko der Umsetzung:** 2/10

### Beobachtung

`main` ist weiterhin ungeschützt und im Repository existiert noch kein Ruleset. Die GitHub-Verbindung dieser Entwicklungsumgebung kann Rulesets und Branch-Protection lesen, stellt aber keine Admin-Schreibaktion dafür bereit. Eine rein manuelle Einrichtung in der Weboberfläche ist möglich, aber anfällig für falsche Check-Namen, versehentlich aktivierte Runtime-Gates oder fehlende Nachkontrolle.

### Verbesserungsvorschlag

Die GitHub-P0-Einrichtung als **sicheren, lokalen Admin-Assistenten** im Repository bereitstellen:

- `Scripts/github_p0_admin.py` zeigt standardmäßig nur den geplanten Zustand an.
- Erst `--apply` darf Branch-Protection tatsächlich setzen.
- `static-and-contract` und `repository-quality` werden als Required Checks gesetzt.
- `cp1-runtime` bleibt bewusst noch nicht global required.
- Admins unterliegen dem Schutz.
- Force-Push und Branch-Löschen werden gesperrt.
- Nach dem Schreiben wird der GitHub-Zustand erneut gelesen und geprüft.
- `Scripts/github_p0_status.py` kann jederzeit ausschließlich lesend den P0-Zustand prüfen.
- `UE58_RUNNER_ENABLED=true` wird nicht automatisch zusammen mit Branch-Protection gesetzt; dafür ist ein eigener expliziter Schalter vorgesehen und darf erst nach realem `RUNNER_READINESS: PASS` verwendet werden.

### Grund

Ein Schutzmechanismus ist nur dann belastbar, wenn nicht nur seine Konfiguration, sondern auch seine **erfolgreiche serverseitige Wirkung** nachgeprüft wird. Gleichzeitig darf ein Hilfsskript keine weitreichende Adminänderung unbemerkt durchführen.

### Erwartete Wirkung

- weniger Fehlkonfigurationen bei Branch-Protection
- korrekte Required-Check-Namen
- reproduzierbare Einrichtung
- klarer Dry-Run vor jeder Änderung
- serverseitige Nachprüfung nach dem Schreiben
- Runner-Freigabe bleibt vom Branch-Schutz getrennt
- deutlich bessere Bedienbarkeit für Nicht-GitHub-Spezialisten

### Technischer Effekt

Der bisher rein manuelle P0-Adminschritt wird zu einem kontrollierten Ablauf:

```text
Dry-Run
→ gh-Authentifizierung prüfen
→ Branch-Protection setzen
→ GitHub erneut lesen
→ Required Checks verifizieren
→ PASS/FAIL ausgeben
```

Die UE-Runner-Freigabe bleibt ein separates Gate:

```text
Runner registrieren
→ runner_readiness.py real PASS
→ erst dann UE58_RUNNER_ENABLED=true
→ echter CP1-Lauf
```

### Aktueller belegter Zustand

- `static-and-contract`: PASS
- `repository-quality`: PASS
- GitHub-Rulesets: keine vorhanden
- `main` Branch-Protection: noch offen
- UE-5.8 Self-hosted Runner: noch extern einzurichten
- CP1 Runtime: weiterhin `UNOBSERVED/BLOCKED`

### Fertig, wenn

- `python3 Scripts/github_p0_admin.py --apply` auf einem mit Adminrechten angemeldeten Rechner erfolgreich ausgeführt wurde
- `python3 Scripts/github_p0_status.py` den Branch-Gate als PASS meldet
- GitHub `main` als geschützt ausweist
- `static-and-contract` required ist
- `repository-quality` required ist
- Force-Push und Löschen blockiert sind
- UE-Runner anschließend separat registriert und real geprüft wird

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md` und Issue #2.
