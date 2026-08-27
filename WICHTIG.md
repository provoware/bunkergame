# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-006 — Branch-Protection-Fehler selbst diagnostizieren statt nur abbrechen

**Kategorie:** GitHub-Administration / Diagnose / Laienführung  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reale Admin-Ausführung weiterhin extern erforderlich  
**Nutzen:** 10/10  
**Aufwand:** 3/10  
**Risiko der Umsetzung:** 1/10

### Beobachtung

GitHub meldete serverseitig weiterhin `main.protected=false`, obwohl der sichere Apply-Ablauf bereits vorbereitet war. Der bisherige Assistent prüfte vor dem Schreiben nur, ob `gh` installiert und angemeldet ist. Er prüfte noch nicht explizit, ob das angemeldete Konto für **genau `provoware/bunkergame`** tatsächlich Repository-Adminrechte besitzt.

Bei Fehlern wurden 403, 404 und 422 außerdem nur als allgemeines Scheitern ausgegeben. Für Laien war damit nicht klar, ob Berechtigung, falscher Repository-/Branch-Kontext oder eine ungültige GitHub-Konfiguration die Ursache war.

### Verbesserungsvorschlag

Vor jeder Adminänderung eine read-only Fähigkeitsprüfung ausführen:

```text
gh vorhanden
→ gh angemeldet
→ Repository exakt bestätigt
→ Repository nicht archiviert
→ permissions.admin == true
→ main existiert
→ aktuellen protected-Serverhinweis anzeigen
→ erst dann Apply erlauben
```

Fehler werden anschließend eindeutig klassifiziert:

```text
403 → Berechtigung / Token
404 → Repository / Branch / Ressource
422 → Konfiguration von GitHub abgelehnt
sonst → unbekannter GitHub-Fehler
```

### Umgesetzt

- `github_p0_admin.py --doctor` ergänzt.
- Repository-Adminrecht wird aus der authentifizierten Repository-Antwort geprüft.
- Maintain-/Push-Rechte werden ausdrücklich nicht als Adminrecht akzeptiert.
- falscher Repository-Kontext wird blockiert.
- archiviertes Repository wird blockiert.
- Zielbranch `main` wird vor dem Schreiben bestätigt.
- aktueller Serverhinweis `main.protected=true/false` wird angezeigt.
- 403/404/422 erhalten eigene Diagnosecodes und konkrete nächste Schritte.
- Apply und Runner-Variable verwenden dieselbe Fehlerklassifizierung.
- `github_p0_status.py` liest zuerst den normalen Branch-Endpunkt und meldet `protected=false` eindeutig ohne Detail-API.
- erst bei `protected=true` wird die vollständige Branch-Protection-Konfiguration als Beweis geprüft.
- neue Regressionstests decken Adminrecht, Maintain-only, falsches Repository, 403/404/422 und Protected-Hinweise ab.

### Erwartete Wirkung

- deutlich weniger Rätselraten bei GitHub-Adminfehlern
- keine Apply-Versuche mit nur Maintain-/Push-Rechten
- schneller Unterschied zwischen Rechteproblem und Payload-Problem
- unabhängigerer Servernachweis über `protected`
- bessere Laienführung ohne Abschwächung des Sicherheitsgates

### Technischer Effekt

```text
GITHUB_ADMIN_PREFLIGHT
→ capability PASS/BLOCKED
→ APPLY nur bei PASS
→ serverseitiges Read-back
→ GITHUB_P0_BRANCH_GATE PASS/FAIL
```

### Aktueller belegter Zustand

- PR #1: gemergt
- PR #3: gemergt
- `main`: serverseitig zuletzt `protected=false`
- Admin-Diagnose: implementiert
- neue Regressionstests: implementiert
- reale Admin-Ausführung: extern offen
- Self-hosted UE-5.8 Runner: extern offen
- CP1 Runtime: `UNOBSERVED/BLOCKED`

### Fertig, wenn

- Hosted `static-and-contract` PASS ist
- Hosted `repository-quality` PASS ist
- `python3 Scripts/github_p0_admin.py --doctor` auf dem Admin-Rechner `GITHUB_ADMIN_PREFLIGHT: PASS` meldet
- `--apply` erfolgreich schreibt
- `github_p0_status.py` anschließend `main.protected=true` und beide Required Checks bestätigt
- `GITHUB_P0_BRANCH_GATE: PASS` serverseitig erreicht ist

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md` und Issue #2.
