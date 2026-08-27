# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-007 — GitHub-Schutz über unabhängig lesbares Ruleset beweisen

**Kategorie:** Evidence Integrity / GitHub Rulesets / Robustheit / Codequalität  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reales Ruleset auf GitHub noch anzuwenden  
**Nutzen:** 10/10  
**Aufwand:** 4/10  
**Risiko der Umsetzung:** 2/10

### Beobachtung

Die klassische Branch-Protection kann korrekt funktionieren, ihr Detail-Endpunkt ist für manche GitHub-Integrationen aber nicht lesbar. Dadurch entsteht ein ungünstiger Zustand: Der Schutz kann auf dem Admin-Rechner gesetzt werden, während eine unabhängige zweite Stelle die vollständige Konfiguration wegen eines 403 nicht nachprüfen kann.

### Verbesserungsvorschlag

Den P0-Schutz bevorzugt als **Repository Ruleset** abbilden. Rulesets sind laut GitHub bereits mit Repository-Lesezugriff sichtbar. Dadurch kann der vollständige Serverzustand nach dem einmaligen Admin-Apply unabhängig nachgeprüft werden.

```text
Admin-Rechner
→ --doctor
→ --apply-ruleset
→ GitHub speichert aktives Ruleset

Unabhängige Prüfung
→ GET /repos/provoware/bunkergame/rulesets
→ Ruleset-ID bestimmen
→ vollständiges Ruleset lesen
→ gemeinsamer Contract-Validator
→ P0 PASS/FAIL
```

### Grund

Ein Beweis ist stärker, wenn seine Prüfung nicht dieselbe privilegierte Schnittstelle benötigt wie seine Erzeugung. Das Ruleset trennt daher **Schreiben mit Adminrecht** von **Lesen/Prüfen mit Read-Zugriff**. So wird die Infrastruktur-Evidence reproduzierbarer und weniger abhängig von einem einzelnen Token oder GitHub-App-Berechtigungsprofil.

### Umgesetzt

- `Scripts/github_p0_ruleset.py` als zentrale, reine Vertragslogik ergänzt.
- ein einziger kanonischer Ruleset-Payload verhindert Drift zwischen Admin-, Status- und Testlogik.
- Ruleset zielt ausschließlich auf `refs/heads/main`.
- Enforcement muss exakt `active` sein; `evaluate` zählt niemals als realer Schutz.
- Pull Request vor Integration ist verpflichtend.
- Solo-Repository bleibt mit `required_approving_review_count=0` bedienbar.
- offene Review-Diskussionen müssen gelöst sein.
- `static-and-contract` und `repository-quality` sind Required Checks.
- Branch muss vor Merge aktuell sein.
- `deletion` blockiert das Löschen von `main`.
- `non_fast_forward` blockiert Force-Push.
- unerwartete Bypass-Akteure führen zu FAIL.
- `cp1-runtime` bleibt bis zum stabilen echten UE-Runner bewusst nicht global required.
- `github_p0_admin.py --apply-ruleset` arbeitet als sicheres Upsert: vorhandenes Soll-Ruleset aktualisieren, sonst neu anlegen; Duplikate blockieren.
- nach jedem Write erfolgt serverseitiges Read-back mit demselben Contract-Validator.
- `github_p0_status.py` prüft Rulesets zuerst und fällt nur bei Bedarf auf klassische Branch Protection zurück.
- Hosted Regressionstests prüfen aktive/unechte Enforcement-Zustände, Required Checks, Strictness, Force-Push/Delete-Sperre, Bypass und Duplikate.

### Erwartete Wirkung

- unabhängigere und leichter reproduzierbare Infrastruktur-Evidence
- weniger Abhängigkeit vom klassischen Protection-Detail-Endpunkt
- kein Unterschied zwischen Soll-Payload und Prüfvertrag
- weniger duplizierte GitHub-Regellogik
- eindeutige Anti-Fake-Regeln für Testfixtures
- bessere Wartbarkeit durch zentrales Contract-Modul

### Technischer Effekt

```text
P0 RULESET CONTRACT
→ canonical payload
→ safe upsert
→ live server read-back
→ same evaluator
→ independent read-only verification
```

Testdateien dürfen den Evaluator prüfen, aber nie einen Live-Server-PASS ersetzen. Ein echtes P0-Ruleset-PASS entsteht nur aus einer von GitHub gelesenen aktiven Ruleset-Konfiguration.

### Aktueller belegter Zustand

- GitHub-Ruleset-Liste serverseitig aktuell leer (`[]`)
- `main` serverseitig weiterhin ungeschützt
- Repository-Rolle der verbundenen Identität: `admin=true`
- Ruleset-Contract und Apply-/Verify-Pfad: implementiert
- Anti-Fake-Regressionstests: implementiert
- reales Ruleset: noch nicht angewendet
- Self-hosted UE-5.8 Runner: weiterhin offen
- CP1 Runtime: `UNOBSERVED/BLOCKED`

### Fertig, wenn

- Hosted `static-and-contract` PASS ist
- Hosted `repository-quality` PASS ist
- `python3 Scripts/github_p0_admin.py --doctor` PASS meldet
- `python3 Scripts/github_p0_admin.py --apply-ruleset` das aktive Ruleset serverseitig anlegt
- der Ruleset-Endpunkt das vollständige Soll unabhängig lesbar zurückliefert
- `github_p0_status.py` `GITHUB_P0_EVIDENCE_PATH: RULESET` und `GITHUB_P0_BRANCH_GATE: PASS` meldet

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md`, `Docs/GITHUB_ADMIN_DIAGNOSE.md` und Issue #2.
