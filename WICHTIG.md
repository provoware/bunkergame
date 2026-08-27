# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-005 — Nach Merge nie still auf demselben Feature-Branch weiterentwickeln

**Kategorie:** Git-Workflow / Prozessintegrität / Fehlerprävention  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — als read-only Guard + Regressionstest  
**Nutzen:** 9/10  
**Aufwand:** 2/10  
**Risiko der Umsetzung:** 1/10

### Beobachtung

PR #1 wurde bereits gemergt, während danach noch weitere Änderungen auf demselben Feature-Branch entstanden. Diese Commits gehörten dadurch nicht mehr zum bereits abgeschlossenen PR und erhielten zunächst keinen neuen PR-/CI-Lifecycle.

Das ist kein Codefehler, aber eine relevante Prozessschwachstelle: Ein bereits gemergter Branch kann optisch wie ein weiterhin aktiver Arbeitszweig wirken, obwohl die neue Arbeit außerhalb des abgeschlossenen Review-Gates liegt.

### Verbesserungsvorschlag

Ein read-only Branch-Lifecycle-Gate vor die technische P0-Prüfung setzen:

```text
Arbeitsbranch bestimmen
→ GitHub nach bereits gemergten PRs dieses Branches fragen
→ Commits vor origin/main bestimmen
→ wenn bereits gemergt + neue Commits vorhanden:
   FAIL
   → neuen Branch vom aktuellen main verlangen
```

### Umgesetzt

- `Scripts/branch_lifecycle_guard.py` ergänzt.
- das Skript verändert weder Git noch GitHub.
- `main` wird nicht als Feature-Branch-Reuse gewertet.
- bereits gemergter Feature-Branch mit neuen Commits wird blockiert.
- noch nie gemergter oder aktuell offener Arbeitsbranch bleibt zulässig.
- fehlende GitHub-CLI-/Auth-Daten erzeugen `BLOCKED`, keinen erfundenen PASS.
- der Guard wurde als **erste Stufe** in `Scripts/p0_preflight.py` aufgenommen.
- Regressionstests decken main, merged+ahead, merged+0, nie gemergt und ungültige PR-Antwort ab.

### Grund

Ein Review-/CI-Prozess ist nur belastbar, wenn neue Arbeit nach einem Merge wieder einen neuen nachvollziehbaren Branch-/PR-Zyklus erhält. Sonst können Folgeänderungen versehentlich außerhalb des erwarteten Gate-Lebenszyklus landen.

### Erwartete Wirkung

- keine stillen Nacharbeiten auf bereits abgeschlossenen Feature-Branches
- sauberere PR-Historie
- jede Iteration erhält wieder einen eigenen prüfbaren Lifecycle
- weniger Verwechslung zwischen gemergtem Stand und neuer Arbeit
- bessere Grundlage für Branch Protection und Required Checks

### Technischer Effekt

Der P0-Preflight beginnt jetzt mit:

```text
BRANCH_LIFECYCLE
→ static
→ quality
→ GitHub branch gate
→ optional UE58 readiness
```

Ein Branch-Lifecycle-FAIL hat bewusst Vorrang vor allen nachfolgenden technischen Prüfungen.

### Aktueller belegter Zustand

- PR #1: gemergt
- Folgebranch: `infra/p0-postmerge-hardening`
- Branch-Lifecycle-Guard: implementiert
- Regressionstests: implementiert
- Branch Protection `main`: weiterhin extern offen
- Self-hosted UE-5.8 Runner: weiterhin extern offen
- CP1 Runtime: weiterhin `UNOBSERVED/BLOCKED`

### Fertig, wenn

- Folge-PR gegen `main` offen ist
- `static-and-contract` PASS ist
- `repository-quality` PASS ist
- Iteration Guard den neuen W-/CQ-Eintrag akzeptiert
- die Nacharbeiten ausschließlich über den neuen Folge-PR integriert werden

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md` und Issue #2.
