# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Vorschlag. Historische Vorschläge stehen append-only in `CODEQUALITÄT.md`.

## W-2026-10-23-014 — Vorrelease-Prüfungen dauerhaft in Validate ausführen

**Kategorie:** P0 / Prüfqualität / Vorrelease
**Priorität:** P0
**Status:** IMPLEMENTIERT; vollständiger GitHub-PR-Prüflauf noch zu bestätigen
**Nutzen:** 10/10 · **Änderungsrisiko:** niedrig

### Beobachtung
Die auf einem Entwicklungszweig vorhandene Vorrelease-Pflichtmatrix und ihre Regressionstests wurden von `Scripts/ci_verify.py` nicht ausgeführt. Ein grüner Standard-Validate-Lauf konnte daher die 40 Anforderungen unbeobachtet lassen.

### Verbesserungsvorschlag
`Scripts/ci_verify.py` ruft den Matrix-Vertrag und die drei zugehörigen Tests genau einmal auf. Ein neuer Negativtest erkennt fehlende oder doppelte Einträge und bestätigt den Aufruf durch den bestehenden Validate-Workflow.

### Grund und Nachweisgrenzen
Statische Vertragsprüfungen sind **kein** UE-5.8-Build, kein vollständiger Spielverlauf und kein Nachweis für eine persönliche Abnahme. P0-Branchschutz und Self-hosted-Runner bleiben getrennte offene Gates.

### Wirkung und Fertig, wenn
- neuer Negativtest und gesamte `Scripts/ci_verify.py`-Kette PASS
- `repository-quality` und Iteration Guard PASS
- GitHub-PR-Prüfungen auf genau dem neuen Commit erfolgreich
- nach erfolgreicher technischer Prüfung gesonderte, kontrollierte PR-Übernahme möglich (kein automatischer Merge)
