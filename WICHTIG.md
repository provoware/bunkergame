# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-008 — Infrastruktur-Evidence an Live-`main` und Ruleset-Drift binden

**Kategorie:** Evidence Integrity / Drift Detection / GitHub Infrastructure  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reales Ruleset und damit echter PASS weiterhin offen  
**Nutzen:** 10/10  
**Aufwand:** 4/10  
**Risiko der Umsetzung:** 2/10

### Beobachtung

Ein tokenfreier Live-Check beweist den aktuellen GitHub-Zustand sehr gut, hinterlässt aber ohne zusätzliche Struktur nur eine Konsolenausgabe. Für spätere Fehleranalyse, Release-Abnahme und automatische Drift-Erkennung fehlt damit ein maschinenlesbarer Beleg, der eindeutig sagt, **welcher `main`-Commit**, **welches Ruleset** und **welcher Vertragszustand** tatsächlich beobachtet wurden.

Eine gespeicherte JSON-Datei allein wäre wiederum zu schwach: Sie könnte veraltet sein, nachträglich verändert werden oder nach einem neuen `main`-Commit weiter wie gültige Evidence aussehen.

### Verbesserungsvorschlag

Den öffentlichen Live-Beweis zu einer zweistufigen Evidence-Kette erweitern:

```text
LIVE GITHUB
→ main SHA lesen
→ Ruleset-ID + Detail lesen
→ P0-Contract validieren
→ JSON-Evidence erzeugen
→ Integritäts-Hash bilden

GESPEICHERTE EVIDENCE
→ Schema + Repository + Branch prüfen
→ Freshness prüfen
→ SHA-256-Integrität prüfen
→ GitHub erneut live lesen
→ main SHA muss noch identisch sein
→ Ruleset-ID muss noch identisch sein
→ Contract muss erneut PASS sein
→ erst dann GITHUB_P0_EVIDENCE: PASS
```

### Grund

Ein belastbarer Infrastrukturbeweis braucht sowohl **Nachvollziehbarkeit** als auch **Gegenwartsbezug**. Der gespeicherte Datensatz erklärt, was beobachtet wurde; die erneute Live-Abfrage verhindert, dass ein alter oder kopierter PASS als aktueller Serverzustand verwendet wird.

Der SHA-256-Hash ist dabei ausdrücklich nur eine lokale Integritätsprüfung gegen versehentliche Veränderung. Er ist **keine GitHub-Signatur** und ersetzt niemals die zweite Live-Abfrage.

### Umgesetzt

- `Scripts/github_p0_evidence.py` sammelt tokenfrei Live-Daten und schreibt ein versioniertes JSON-Bundle.
- Evidence enthält Repository, Branch, aktuellen `main`-SHA, Ruleset-ID, Enforcement, Contract-Status, Fehlerliste, Quellen und Beobachtungszeit.
- FAIL-Zustände werden ebenfalls als Diagnose-Bundle geschrieben.
- Evidence wird mit SHA-256 versiegelt; nachträgliche lokale Änderungen werden erkannt.
- `Scripts/github_p0_evidence_validate.py` prüft Schema, Typ, Repository, Branch, Freshness, Status, Quellendpunkte und Integritäts-Hash.
- gespeicherter PASS reicht technisch nicht: der Validator führt immer eine neue öffentliche GitHub-Abfrage aus.
- ein veränderter `main`-SHA invalidiert die vorhandene Evidence automatisch.
- geänderte Ruleset-ID oder Ruleset-Konfiguration werden als Drift erkannt.
- maximale Evidence-Altersgrenze: 36 Stunden.
- neue Regressionstests prüfen PASS-Bundle, fehlendes Ruleset, Manipulation, Stale-Evidence, falsches Repository, `main`-Drift, Ruleset-ID-Drift und Contract-Drift.
- `P0 Infrastructure Observer` lädt das JSON-Bundle auch bei FAIL als GitHub-Actions-Artefakt hoch und setzt den Job erst danach rot.
- `actions/upload-artifact` ist auf einen vollständigen Commit-SHA gepinnt.

### Erwartete Wirkung

- nachvollziehbare Infrastruktur-Evidence statt flüchtiger Terminalausgabe
- automatische Invalidierung alter Evidence nach Änderungen an `main`
- Drift-Erkennung bei Ruleset-Änderungen
- bessere Fehleranalyse durch gespeicherte FAIL-Bundles
- reproduzierbare Release-/P0-Abnahme
- klare Trennung zwischen Integritäts-Hash und echter Live-Authentizität
- deutlich geringeres Risiko eines versehentlich wiederverwendeten alten PASS

### Technischer Effekt

```text
COLLECT
→ live GitHub
→ evidence.json
→ SHA-256 seal

VALIDATE
→ stored contract
→ freshness
→ integrity
→ live GitHub re-check
→ main-SHA binding
→ ruleset binding
→ P0 contract re-check
→ PASS / DRIFT / FAIL
```

### Aktueller belegter Zustand

- PR #4 mit Ruleset-/Public-Verify-Schicht: gemergt
- `main` nach PR #4: `deba9c92f0ff7d36b1c62b420ef5c450b93157eb`
- Evidence-Collector: implementiert
- Evidence-Live-Validator: implementiert
- Observer-Artefaktpfad: implementiert
- Regressionstests: implementiert
- reales GitHub-P0-Ruleset: weiterhin noch nicht angewendet
- echter Infrastruktur-PASS: daher weiterhin offen
- Self-hosted UE-5.8 Runner: weiterhin offen
- CP1 Runtime: `UNOBSERVED/BLOCKED`

### Fertig, wenn

- Hosted `static-and-contract` PASS ist
- Hosted `repository-quality` inklusive neuer Evidence-Regressionstests PASS ist
- ein reales aktives P0-Ruleset auf GitHub vorhanden ist
- der Observer ein PASS-Bundle erzeugt und hochlädt
- `github_p0_evidence_validate.py` dasselbe Bundle gegen den weiterhin aktuellen Live-Serverzustand mit `GITHUB_P0_EVIDENCE: PASS` bestätigt

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md`, `Docs/PROJEKTSTATUS.md`, Issue #2 und das Evidence-Bundle aus `P0 Infrastructure Observer`.
