# BUNKER BEATS — PROJEKTSTATUS

**Stand:** 2026-08-27  
**Phase:** Technical/Core Integration  
**Aktueller Checkpoint:** CP1 Runtime  
**Arbeitszweig:** `infra/p0-admin-diagnostics`

> Dieses Dokument beantwortet nur: **Was ist aktuell bewiesen, was ist blockiert und was ist der nächste Engpass?**  
> Bedienung: `ANLEITUNG.md` · Aufgaben: `Docs/TODO.md` · Regeln: `AGENTS.md` · aktueller Verbesserungsfokus: `WICHTIG.md`

---

## 1. CURRENT TRUTH

| Bereich | Status | Nachweis / Bedeutung |
|---|---|---|
| Headless Core | 🟢 BEWIESEN | 190 Kombinationen, 570 deterministische Checks |
| Repository-Baseline | 🟢 BEWIESEN | Projektbasis auf `main`, Folgeänderungen über PR #4 |
| Static/Contract CI | 🟢 BEWIESEN | `static-and-contract` lief auf GitHub erfolgreich |
| Repository Quality CI | 🟡 IN ABNAHME | neuester Ruleset-Head wird erneut über `repository-quality` geprüft |
| P0 Ruleset Contract | 🟢 IMPLEMENTIERT | zentraler fail-closed Vertrag in `Scripts/github_p0_ruleset.py` |
| Tokenfreier GitHub-Live-Verifier | 🟢 IMPLEMENTIERT | `github_p0_public_verify.py`; PASS nur aus echtem GitHub-Ruleset |
| P0 Infrastructure Observer | 🟢 IMPLEMENTIERT | GitHub-hosted, täglich/manuell, ohne Admin-Secret |
| Reales P0-Ruleset auf GitHub | 🔴 OFFEN | Serverliste meldete zuletzt `[]`; noch kein Infrastruktur-PASS |
| Klassischer `main`-Schutz | 🔴 OFFEN/FALLBACK | `main.protected=false`; klassische Protection nur Fallback |
| CP1 Telemetrie-Vertrag | 🟢 IMPLEMENTIERT | Frame-Time, Position, Velocity, Displacement, MovementComponent |
| UE 5.8 Build | 🟡 UNBEOBACHTET | echte UE-5.8-Maschine erforderlich |
| Character Spawn + Movement | 🟡 UNBEOBACHTET | echter Runtime-Lauf fehlt |
| CP1 Gate | 🟡 BLOCKIERT | darf ohne Runtime-Evidence nicht GREEN werden |
| Self-hosted UE-Runner | 🔴 OFFEN | realer Runner/Readiness/Variable noch nicht nachgewiesen |

**Evidence-Regel:** `IMPLEMENTIERT` ist nicht automatisch `BEWIESEN`. Testfixtures beweisen Validatorlogik, aber niemals den Live-GitHub-Zustand. Ein GitHub-Schutz-PASS entsteht nur aus einer live gelesenen aktiven Serverkonfiguration. Runtime-Verhalten wird ausschließlich durch maschinell erzeugte UE-5.8-Evidence zu PASS.

---

## 2. WAS BEREITS FUNKTIONIERT

- Headless-Regelwerk und deterministische Tests
- 2-aus-20-Fähigkeitenmodell mit 190 Kombinationen
- Diagnose-, Repair-, Learning- und Attribution-Grundlagen
- CP1 Game-/Editor-Targets und Primary Game Module
- automatisierter CP1-Ablauf: Build → Spawn → Movement → Telemetrie → Gate
- Schutz gegen stale/falsche Runtime-Evidence
- GitHub `Validate` / Check `static-and-contract`
- GitHub `Quality Guard` / Check `repository-quality`
- optionaler `CP1 UE 5.8 Runtime` Workflow
- zentraler GitHub-P0-Ruleset-Contract
- Ruleset-Upsert mit Admin-Doctor und serverseitigem Read-back
- tokenfreier öffentlicher Ruleset-Live-Verifier
- GitHub-hosted `P0 Infrastructure Observer`
- klassische Branch Protection als kompatibler Fallback
- CODEOWNERS, Dependabot, PR-/Issue-Templates
- getrenntes Dokumentations-Cockpit

---

## 3. WAS NOCH NICHT BEWIESEN IST

### Infrastruktur

- aktives P0-Ruleset auf dem GitHub-Server
- `GITHUB_P0_PUBLIC_RULESET: PASS`
- `GITHUB_P0_EVIDENCE_PATH: RULESET`
- real registrierter und erreichbarer Self-hosted UE-5.8-Runner
- frische echte `RUNNER_READINESS: PASS` Evidence
- `UE58_RUNNER_ENABLED=true` nach Evidence-Gate

### Runtime

- UE-5.8-Kompilierung auf Zielmaschine
- Unreal Editor Boot / Automation
- echter Character Spawn
- echte 3D-Bewegung
- Animation
- Runtime-Ability-Effekte
- Interaction → Task → Ability → XP Vertical Slice
- Save/Load
- Event-, Crowd- und Rival-Runtime
- Packaged Build

Diese Punkte bleiben **UNBEOBACHTET/BLOCKIERT**, bis der jeweilige reale Test oder Server-Lesepfad sie tatsächlich beobachtet hat.

---

## 4. AKTUELLER P0-ENGPASS

### P0-A — unabhängig beweisbares GitHub Ruleset

Bevorzugter Sollzustand:

- Ruleset `BUNKER BEATS P0 main gate`
- `enforcement=active`
- ausschließlich `refs/heads/main`
- keine Bypass-Akteure
- Pull Request erforderlich
- offene Review-Diskussionen müssen gelöst sein
- Required Check `static-and-contract`
- Required Check `repository-quality`
- Branch vor Merge aktuell
- Force-Push gesperrt (`non_fast_forward`)
- Löschen von `main` gesperrt (`deletion`)
- `cp1-runtime` noch nicht global required

Der entscheidende Architekturpunkt: **Schreiben benötigt Adminrecht; der Beweis danach nicht.**

```text
Admin-Apply
→ GitHub Ruleset
→ tokenfreier Public Verify
→ GitHub-hosted Infrastructure Observer
```

### P0-B — Self-hosted UE-5.8-Runner

Benötigte Labels:

- `self-hosted`
- `unreal`
- `ue-5.8`

Danach frische Readiness-Evidence und erst dann:

```text
UE58_RUNNER_ENABLED=true
```

Erst anschließend kann CP1 nativ bewiesen werden.

---

## 5. AUTOMATISCHE QUALITÄT

Die Prüfung ist mehrschichtig:

1. **Validate / `static-and-contract`** — CP1-/Contract-/Headless-Prüfungen.
2. **Quality Guard / `repository-quality`** — Repository-Hygiene, Dokumentintegrität, P0-Regressionstests und Iteration Guard.
3. **P0 Infrastructure Observer** — echter öffentlicher GitHub-Ruleset-Zustand, GitHub-hosted und ohne Admin-Secret.
4. **CP1 UE 5.8 Runtime** — späterer echter Runtime-Beweis auf Self-hosted UE-Maschine.

Der Ruleset-Contract ist fail-closed. Unter anderem führen zu FAIL:

- `enforcement=evaluate`
- falscher/zusätzlicher Branchbereich
- Bypass-Akteure
- doppelte oder unerwartete Rule-Typen
- fehlende/zusätzliche Required Checks
- Strictness aus
- fehlende PR-Regel
- fehlende Delete-Sperre
- fehlende Force-Push-Sperre

---

## 6. DOKUMENTATIONS-ROLLEN

| Datei | Aufgabe |
|---|---|
| `README.md` | Einstieg, Ampelstatus, Schnellstart |
| `ANLEITUNG.md` | Laien-Schrittfolge und Fehlerhilfe |
| `Docs/PROJEKTSTATUS.md` | aktueller belegter Zustand |
| `Docs/TODO.md` | priorisierte Arbeitssteuerung |
| `AGENTS.md` | verbindliche Entwicklungs-/Agentenregeln |
| `WICHTIG.md` | genau ein aktueller Verbesserungsfokus pro Iteration |
| `CODEQUALITÄT.md` | append-only Qualitätsjournal mit Grund/Wirkung/Effekt |
| `Docs/CHANGELOG.md` | tatsächlich umgesetzte Änderungen |
| `Docs/GITHUB_P0_SETUP.md` | Ruleset-/Runner-Abnahme |
| `Docs/GITHUB_ADMIN_DIAGNOSE.md` | Admin- und Infrastrukturdiagnose |

---

## 7. NÄCHSTER VERTIKALSCHNITT NACH CP1

Erst nach echtem CP1-PASS:

`Character → Interaction → erster Task → Ability-Effekt → XP`

Crowd, Rival und größere Event-Runtime bleiben dahinter, solange sie keine direkte Abhängigkeit für diesen Slice sind.

---

## 8. NEXT BEST ACTION

1. aktuellen PR-Head über `static-and-contract` und `repository-quality` vollständig grün bekommen.
2. auf einem Admin-Rechner `python3 Scripts/github_p0_admin.py --doctor` ausführen.
3. `python3 Scripts/github_p0_admin.py --apply-ruleset` ausführen.
4. unabhängig `python3 Scripts/github_p0_public_verify.py` → `GITHUB_P0_PUBLIC_RULESET: PASS` beweisen.
5. `P0 Infrastructure Observer` manuell/automatisch als zweiten externen Live-Beweis prüfen.
6. Self-hosted UE-5.8-Runner registrieren.
7. `python3 Scripts/p0_preflight.py --full` auf der UE-Maschine ausführen.
8. erst nach frischer Readiness `UE58_RUNNER_ENABLED=true` freigeben.
9. CP1 nativ ausführen und Runtime-Evidence prüfen.
10. erst danach CP1 GREEN und Interaction-Vertical-Slice beginnen.
