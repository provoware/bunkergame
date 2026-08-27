# BUNKER BEATS — PROJEKTSTATUS

**Stand:** 2026-08-27  
**Phase:** Technical/Core Integration  
**Aktueller Checkpoint:** CP1 Runtime  
**Arbeitszweig:** `infra/p0-evidence-bundle`

> Dieses Dokument beantwortet nur: **Was ist aktuell bewiesen, was ist blockiert und was ist der nächste Engpass?**  
> Bedienung: `ANLEITUNG.md` · Aufgaben: `Docs/TODO.md` · Regeln: `AGENTS.md` · aktueller Verbesserungsfokus: `WICHTIG.md`

---

## 1. CURRENT TRUTH

| Bereich | Status | Nachweis / Bedeutung |
|---|---|---|
| Headless Core | 🟢 BEWIESEN | 190 Kombinationen, 570 deterministische Checks |
| Repository-Baseline | 🟢 BEWIESEN | vollständiger Projektbaum über PR-/CI-Pfad |
| Static/Contract CI | 🟢 BEWIESEN | `static-and-contract` lief auf GitHub erfolgreich |
| Repository Quality | 🟢 BEWIESEN | `repository-quality` inklusive P0-Regressionen erfolgreich |
| P0 Ruleset Contract | 🟢 IMPLEMENTIERT | zentraler fail-closed Soll-/Ist-Vertrag |
| Public Ruleset Verify | 🟢 IMPLEMENTIERT | tokenfreie Live-Abfrage ohne Adminrecht |
| Infrastructure Evidence Bundle | 🟢 IMPLEMENTIERT | JSON + Freshness + SHA-256 + Live-Recheck |
| P0 Infrastructure Observer | 🟢 IMPLEMENTIERT | GitHub-hosted, täglich/manuell, Artifact auch bei FAIL |
| Reales P0-Ruleset auf GitHub | 🔴 OFFEN | letzte Live-Abfrage: Ruleset-Liste `[]` |
| CP1 Telemetrie-Vertrag | 🟢 IMPLEMENTIERT | Frame-Time, Position, Velocity, Displacement, MovementComponent |
| UE 5.8 Build | 🟡 UNBEOBACHTET | echte UE-5.8-Maschine erforderlich |
| Character Spawn + Movement | 🟡 UNBEOBACHTET | echter Runtime-Lauf fehlt |
| CP1 Gate | 🟡 BLOCKIERT | darf ohne Runtime-Evidence nicht GREEN werden |
| Self-hosted UE-Runner | 🔴 OFFEN | Registrierung/Labels/Readiness noch nicht real bewiesen |

**Evidence-Regel:** `IMPLEMENTIERT` ist nicht automatisch `BEWIESEN`. Ein Infrastruktur-PASS entsteht nur aus aktuellen GitHub-Live-Daten; Runtime-Verhalten ausschließlich aus echter UE-5.8-Evidence.

---

## 2. AKTUELLER REPOSITORY-STAND

PR #4 `infra: make GitHub P0 protection independently verifiable` ist gemergt.

`main` danach:

```text
deba9c92f0ff7d36b1c62b420ef5c450b93157eb
```

Die laufende Folgeiteration `infra/p0-evidence-bundle` ergänzt keine Gameplay-Funktion, sondern verbessert ausschließlich Infrastruktur-Evidence, Drift-Erkennung, Diagnose und Codequalität.

---

## 3. WAS BEREITS FUNKTIONIERT

- Headless-Regelwerk und deterministische Tests
- 2-aus-20-Fähigkeitenmodell mit 190 Kombinationen
- Diagnose-, Repair-, Learning- und Attribution-Grundlagen
- CP1 Game-/Editor-Targets und Primary Game Module
- automatisierter CP1-Ablauf: Build → Spawn → Movement → Telemetrie → Gate
- Schutz gegen stale/falsche Runtime-Evidence
- GitHub `Validate` Workflow
- `Quality Guard` mit Iteration Guard
- optionaler `CP1 UE 5.8 Runtime` Workflow
- zentraler GitHub-P0-Ruleset-Vertrag
- sicherer Ruleset-Upsert über Admin-Assistent
- tokenfreier öffentlicher Ruleset-Live-Verifier
- täglicher GitHub-hosted Infrastructure Observer
- maschinenlesbares GitHub-P0-Evidence-Bundle
- Live-Revalidator mit Bindung an aktuellen `main`-SHA und Ruleset-ID
- CODEOWNERS, Dependabot, PR-/Issue-Templates
- getrenntes Dokumentations-Cockpit

---

## 4. INFRASTRUKTUR-EVIDENCE

### Collector

```bash
python3 Scripts/github_p0_evidence.py
```

Erzeugt:

```text
Diagnostics/Infrastructure/github_p0_evidence.json
```

Enthalten sind unter anderem:

- Beobachtungszeit
- Repository und Branch
- aktueller Live-`main`-SHA
- Ruleset-ID und Enforcement
- P0-Contract-Status
- Fehlerliste
- abgefragte GitHub-Endpunkte
- SHA-256-Integritätswert

Der Hash erkennt lokale Veränderung, ist aber **keine GitHub-Signatur**.

### Validator

```bash
python3 Scripts/github_p0_evidence_validate.py
```

Der Validator akzeptiert gespeicherte PASS-Evidence niemals allein. Er prüft:

```text
Schema
→ Repository/Branch
→ Freshness ≤ 36 h
→ Integrität
→ neue GitHub-Live-Abfrage
→ main SHA identisch
→ Ruleset-ID identisch
→ P0-Contract erneut PASS
```

Nur danach:

```text
GITHUB_P0_EVIDENCE: PASS
```

Bei geändertem Live-Zustand:

```text
GITHUB_P0_EVIDENCE: DRIFT
```

Detailanleitung: `Docs/P0_INFRASTRUCTURE_EVIDENCE.md`.

---

## 5. WAS NOCH NICHT BEWIESEN IST

- echtes aktives P0-Ruleset auf GitHub
- `GITHUB_P0_PUBLIC_RULESET: PASS`
- `GITHUB_P0_EVIDENCE: PASS` aus realem Ruleset
- Self-hosted UE-5.8-Runner online und korrekt gelabelt
- UE-5.8-Kompilierung auf Zielmaschine
- Unreal Editor Boot / PIE
- echter Character Spawn
- echte 3D-Bewegung
- Animation
- Runtime-Ability-Effekte
- Interaction → Task → Ability → XP Vertical Slice
- Save/Load
- Event-, Crowd- und Rival-Runtime
- Packaged Build

Diese Punkte bleiben **UNBEOBACHTET/BLOCKIERT**, bis ein passender realer Test sie tatsächlich ausgeführt hat.

---

## 6. AKTUELLER P0-ENGPASS

### P0-A — reales GitHub-Ruleset

Sollname:

```text
BUNKER BEATS P0 main gate
```

Sollzustand:

- `enforcement=active`
- ausschließlich `refs/heads/main`
- keine Bypass-Akteure
- Pull Request erforderlich
- Required Check `static-and-contract`
- Required Check `repository-quality`
- Branch vor Merge aktuell
- Force-Push blockiert
- Löschen von `main` blockiert
- `cp1-runtime` noch nicht global required

Letzte Live-Evidence:

```text
Repository-Rulesets: []
```

Damit ist das Beweissystem vorhanden, aber der reale Schutz noch nicht aktiv.

### P0-B — Self-hosted UE-5.8-Runner

Benötigte Labels:

- `self-hosted`
- `unreal`
- `ue-5.8`

Danach Readiness-Evidence und erst dann:

```text
UE58_RUNNER_ENABLED=true
```

---

## 7. AUTOMATISCHE QUALITÄT

Die Repository-Prüfung ist mehrschichtig:

1. **Validate** — CP1-/Contract-/Headless-Prüfungen.
2. **Quality Guard** — Repository-Hygiene und Dokumentintegrität.
3. **P0 Regression Tests** — Control Plane, Ruleset und Evidence-Logik.
4. **Iteration Guard** — `WICHTIG.md` + append-only `CODEQUALITÄT.md`.
5. **P0 Infrastructure Observer** — echter externer GitHub-Live-Zustand.

Die Evidence-Regressionen prüfen zusätzlich:

- fehlendes Ruleset
- manipuliertes JSON
- zu alte Evidence
- falsches Repository
- `main`-SHA-Drift
- Ruleset-ID-Drift
- Ruleset-Contract-Drift
- Vorhandensein aller kritischen Evidence-Dateien

---

## 8. DOKUMENTATIONS-ROLLEN

| Datei | Aufgabe |
|---|---|
| `README.md` | Einstieg, Ampelstatus, Schnellstart |
| `ANLEITUNG.md` | Laien-Schrittfolge und Fehlerhilfe |
| `Docs/PROJEKTSTATUS.md` | aktueller belegter Zustand |
| `Docs/TODO.md` | priorisierte Arbeitssteuerung |
| `Docs/GITHUB_P0_SETUP.md` | GitHub-Schutz und Runner-Setup |
| `Docs/P0_INFRASTRUCTURE_EVIDENCE.md` | JSON-Evidence, Live-Recheck und Drift-Hilfe |
| `AGENTS.md` | verbindliche Entwicklungs-/Agentenregeln |
| `WICHTIG.md` | genau ein aktueller Verbesserungsfokus pro Iteration |
| `CODEQUALITÄT.md` | append-only Qualitätsjournal mit Grund/Wirkung/Effekt |
| `Docs/CHANGELOG.md` | tatsächlich umgesetzte Änderungen |

---

## 9. NEXT BEST ACTION

1. aktuelle Evidence-Bundle-Iteration über Hosted CI vollständig grün bekommen.
2. Folge-PR integrieren.
3. auf einem Admin-Rechner `python3 Scripts/github_p0_admin.py --doctor` ausführen.
4. reales Ruleset mit `python3 Scripts/github_p0_admin.py --apply-ruleset` setzen.
5. tokenfreien Live-PASS mit `github_p0_public_verify.py` beweisen.
6. JSON-Evidence sammeln und mit `github_p0_evidence_validate.py` live revalidieren.
7. Self-hosted UE-5.8-Runner registrieren.
8. `RUNNER_READINESS: PASS` real erzeugen.
9. Runner-Variable erst nach frischer Evidence freigeben.
10. CP1 nativ ausführen und Runtime-Evidence prüfen.
11. Erst nach echtem CP1-PASS den Interaction-Vertical-Slice beginnen.

---

## 10. NÄCHSTER VERTIKALSCHNITT NACH CP1

Erst nach echtem CP1-PASS:

```text
Character → Interaction → erster Task → Ability-Effekt → XP
```

Crowd, Rival und größere Event-Runtime bleiben dahinter, solange sie keine direkte Abhängigkeit für diesen Slice sind.
