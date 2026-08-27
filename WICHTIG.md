# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-001 — `main` gegen ungeprüfte Änderungen schützen

**Kategorie:** Schwachstelle / GitHub-Sicherheit / Prozessqualität  
**Priorität:** P0  
**Status:** 🔴 OFFEN  
**Nutzen:** 10/10  
**Aufwand:** 2/10  
**Risiko der Umsetzung:** 2/10

### Beobachtung

Der Branch `main` ist aktuell nicht geschützt. Dadurch können Änderungen theoretisch ohne verpflichtende CI-Prüfung oder Pull-Request-Gate auf den Integrationsstand gelangen.

### Verbesserungsvorschlag

Nach erfolgreicher Einführung des `Quality Guard` einen Branch-Protection-Ruleset für `main` aktivieren:

- Pull Request vor Merge verpflichtend
- Check `static-and-contract` verpflichtend — Workflow `Validate`
- Check `repository-quality` verpflichtend — Workflow `Quality Guard`
- Branch vor Merge aktuell halten
- Force-Push sperren
- Löschen von `main` sperren
- direkte Pushes auf `main` vermeiden
- Squash Merge bevorzugen

`cp1-runtime` **noch nicht pauschal als Required Check** konfigurieren, solange der Self-hosted UE-Runner nicht dauerhaft verfügbar ist. Sonst könnten reine Doku-/Headless-Änderungen unnötig blockiert werden. Sobald der Runner stabil betrieben wird, wird ein pfad-/scope-gerechtes Runtime-Gate ergänzt.

### Grund

Die aktuelle technische Qualität kann sehr gut sein, aber ohne Schutz des Integrationsbranches bleibt ein organisatorischer Bypass offen. Ein versehentlicher Direkt-Push könnte die gesamte Evidence-/PR-Logik umgehen.

### Erwartete Wirkung

- weniger unbeabsichtigte Regressionen
- keine ungeprüften Merges
- CI wird verbindlicher Bestandteil des Entwicklungsprozesses
- klarer Unterschied zwischen Arbeitsstand und integriertem Stand
- bessere Nachvollziehbarkeit der Historie

### Technischer Effekt

`main` wird von einem normalen Git-Branch zu einem kontrollierten Integrations-Gate. Erst geprüfte Änderungen gelangen in den Referenzstand.

### Abhängigkeiten

1. `Quality Guard` muss im PR einmal erfolgreich laufen.
2. Check-Namen sind bestätigt: `static-and-contract` und `repository-quality`.
3. Self-hosted Runner wird separat eingerichtet.

### Fertig, wenn

- Branch-Schutz/Ruleset aktiv ist
- `static-and-contract` verpflichtend ist
- `repository-quality` verpflichtend ist
- Force-Push und Branch-Löschen blockiert sind
- ein Test-PR den Schutz praktisch bestätigt

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md`.
