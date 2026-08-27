# BUNKER BEATS — PROJEKTSTATUS

**Stand:** 2026-08-27  
**Phase:** Technical/Core Integration  
**Aktueller Checkpoint:** CP1 Runtime  
**Arbeitszweig:** `infra/cp1-github-control-plane`

> Dieses Dokument beantwortet nur: **Was ist aktuell bewiesen, was ist blockiert und was ist der nächste Engpass?**  
> Bedienung: `ANLEITUNG.md` · Aufgaben: `Docs/TODO.md` · Regeln: `AGENTS.md` · aktueller Verbesserungsfokus: `WICHTIG.md`

---

## 1. CURRENT TRUTH

| Bereich | Status | Nachweis / Bedeutung |
|---|---|---|
| Headless Core | 🟢 BEWIESEN | 190 Kombinationen, 570 deterministische Checks |
| Repository-Baseline | 🟢 BEWIESEN | vollständiger Projektbaum im PR-Branch |
| Static/Contract CI | 🟢 BEWIESEN | `Validate` lief auf GitHub erfolgreich |
| CP1 Telemetrie-Vertrag | 🟢 IMPLEMENTIERT | Frame-Time, Position, Velocity, Displacement, MovementComponent |
| UE 5.8 Build | 🟡 UNBEOBACHTET | echte UE-5.8-Maschine erforderlich |
| Character Spawn + Movement | 🟡 UNBEOBACHTET | echter Runtime-Lauf fehlt |
| CP1 Gate | 🟡 BLOCKIERT | darf ohne Runtime-Evidence nicht GREEN werden |
| `main` Branch-Schutz | 🔴 OFFEN | `main` ist aktuell nicht geschützt |
| Self-hosted UE-Runner | 🔴 OFFEN | Registrierung/Labels/Variable fehlen noch |

**Evidence-Regel:** `IMPLEMENTIERT` ist nicht automatisch `BEWIESEN`. Ein Runtime-Verhalten wird ausschließlich durch maschinell erzeugte UE-5.8-Evidence zu PASS.

---

## 2. WAS BEREITS FUNKTIONIERT

- Headless-Regelwerk und deterministische Tests
- 2-aus-20-Fähigkeitenmodell mit 190 Kombinationen
- Diagnose-, Repair-, Learning- und Attribution-Grundlagen
- CP1 Game-/Editor-Targets und Primary Game Module
- automatisierter CP1-Ablauf: Build → Spawn → Movement → Telemetrie → Gate
- Schutz gegen stale/falsche Runtime-Evidence
- GitHub `Validate` Workflow
- optionaler `CP1 UE 5.8 Runtime` Workflow
- CODEOWNERS, Dependabot, PR-/Issue-Templates
- getrenntes Dokumentations-Cockpit

---

## 3. WAS NOCH NICHT BEWIESEN IST

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

Diese Punkte bleiben **UNBEOBACHTET/BLOCKIERT**, bis ein passender Test sie tatsächlich ausgeführt hat.

---

## 4. AKTUELLER P0-ENGPASS

### P0-A — GitHub-Schutzschicht

`main` muss gegen versehentliche Direktänderungen und ungeprüfte Merges abgesichert werden.

**Sollzustand:**
- Pull Request erforderlich
- Required Check: `Validate`
- Required Check: `Quality Guard`
- kein Force-Push
- kein Branch-Löschen
- Branch muss vor Merge aktuell sein
- CP1-Runtime erst dann als Required Check erzwingen, wenn der UE-Runner zuverlässig verfügbar ist

### P0-B — Self-hosted UE-5.8-Runner

Benötigte Labels:
- `self-hosted`
- `unreal`
- `ue-5.8`

Danach Repository-Variable:

`UE58_RUNNER_ENABLED=true`

Erst dann kann CP1 nativ bewiesen werden.

---

## 5. AUTOMATISCHE QUALITÄT

Die Repository-Prüfung wird in zwei Ebenen getrennt:

1. **Validate** — bestehende CP1-/Contract-/Headless-Prüfungen.
2. **Quality Guard** — Repository-Hygiene und Dokumentintegrität.

Der Quality Guard prüft automatisch unter anderem:
- Python-Syntax
- JSON-Lesbarkeit
- kaputte lokale Markdown-Links
- vorgeschriebene Kern-Dokumente
- verbotene generierte Ordner/Dateien
- Textdateien ohne Abschluss-Zeilenumbruch
- offensichtliche Merge-Konfliktmarker
- Struktur von `WICHTIG.md` und `CODEQUALITÄT.md`

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

---

## 7. NÄCHSTER VERTIKALSCHNITT NACH CP1

Erst nach echtem CP1-PASS:

`Character → Interaction → erster Task → Ability-Effekt → XP`

Crowd, Rival und größere Event-Runtime bleiben dahinter, solange sie keine direkte Abhängigkeit für diesen Slice sind.

---

## 8. NEXT BEST ACTION

1. `Quality Guard` installieren und grün bekommen.
2. Branch-Protection/Ruleset für `main` aktivieren.
3. Self-hosted UE-5.8-Runner registrieren.
4. `UE58_RUNNER_ENABLED=true` setzen.
5. CP1 nativ ausführen.
6. Runtime-Evidence prüfen.
7. Erst danach CP1 auf GREEN setzen und den Interaction-Vertical-Slice beginnen.
