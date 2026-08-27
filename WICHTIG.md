# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-004 — P0-Vorprüfung auf einen eindeutigen Ein-Befehl-Ablauf reduzieren

**Kategorie:** Bedienung / Fehlerprävention / P0 Control Plane  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — externe Admin-/UE-Ausführung weiterhin erforderlich  
**Nutzen:** 9/10  
**Aufwand:** 3/10  
**Risiko der Umsetzung:** 1/10

### Beobachtung

Vor dem ersten realen CP1-Lauf existieren mehrere korrekte Einzelprüfungen (`ci_verify.py`, `repo_quality.py`, `github_p0_status.py`, `runner_readiness.py`). Für Einsteiger bleibt jedoch die Gefahr, Prüfungen in falscher Reihenfolge auszuführen, einen späteren Fehler vor einem früheren Engpass zu untersuchen oder nach einem FAIL nicht zu wissen, welcher konkrete Schritt als Nächstes sinnvoll ist.

### Verbesserungsvorschlag

Einen vollständig read-only arbeitenden Orchestrator bereitstellen:

```text
python3 Scripts/p0_preflight.py
```

und auf der echten UE-5.8-Maschine:

```text
python3 Scripts/p0_preflight.py --full
```

Der Orchestrator führt die vorhandenen Gates in kontrollierter Reihenfolge aus, erzeugt eine kompakte Statusmatrix und nennt genau den ersten sinnvollen nächsten Schritt.

### Umgesetzt

- `Scripts/p0_preflight.py` ist read-only.
- statische Projektprüfung wird zuerst ausgeführt.
- Repository Quality Guard folgt als zweite Schicht.
- GitHub Branch-Gate wird danach geprüft.
- `--full` ergänzt die lokale UE-5.8-Readiness.
- kein PASS wird als CP1-Runtime-PASS interpretiert.
- bei Fehlern wird der erste echte Engpass priorisiert.
- Aktivierung der Runner-Variable wird nur empfohlen, wenn alle vorherigen Gates einschließlich Readiness PASS sind.
- die Entscheidungslogik ist in `Scripts/tests/test_p0_control_plane.py` regressionsgetestet.

### Grund

Mehrere gute Prüfskripte ergeben noch keinen guten Bedienprozess. Ein laienfreundlicher P0-Pfad braucht eine eindeutige Reihenfolge und eine einzelne Entscheidungsausgabe. Dadurch sinkt die Wahrscheinlichkeit von Shotgun-Debugging und Fehlbedienung.

### Erwartete Wirkung

- weniger manuelle Reihenfolgefehler
- schnelleres Erkennen des wirklichen Engpasses
- weniger unnötige Parallelreparaturen
- klare Trennung zwischen Hosted-Vorprüfung und echter UE-Maschine
- bessere Übergabe an andere Entwickler oder Agenten

### Technischer Effekt

```text
P0_PREFLIGHT
→ static
→ quality
→ GitHub branch gate
→ optional UE58 readiness
→ first failing gate
→ next best action
```

`P0_PREFLIGHT: PASS` bedeutet ausdrücklich nur, dass die Vorbedingungen erfüllt sind. Ein CP1-Runtime-PASS entsteht weiterhin ausschließlich durch den echten UE-5.8-Runtime-Workflow.

### Aktueller belegter Zustand

- Hosted `Validate`: PASS auf der vorherigen abgenommenen Iteration
- Hosted `Quality Guard`: PASS auf der vorherigen abgenommenen Iteration
- P0-Preflight-Orchestrator: implementiert
- zugehörige Entscheidungs-Regressionstests: implementiert
- Branch-Protection auf `main`: extern offen
- Self-hosted UE-5.8 Runner: extern offen
- reale Readiness-Evidence: noch nicht vorhanden
- CP1 Runtime: `UNOBSERVED/BLOCKED`

### Fertig, wenn

- neuer Head über `static-and-contract` und `repository-quality` PASS ist
- `python3 Scripts/p0_preflight.py` auf dem Admin-Rechner den korrekten GitHub-Engpass meldet
- nach Branch-Schutz der gleiche Befehl zum UE-Schritt weiterleitet
- `python3 Scripts/p0_preflight.py --full` auf der UE-Maschine nur bei echter Readiness PASS wird
- anschließend der reale CP1-Lauf gestartet wird

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md` und Issue #2.
