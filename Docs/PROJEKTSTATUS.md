# BUNKER BEATS — PROJEKTSTATUS

**Stand:** 2026-08-27  
**Phase:** Technical/Core Integration  
**Aktueller Checkpoint:** CP1 Runtime  
**Arbeitszweig:** `infra/cp1-runtime-evidence-contract`

> Dieses Dokument beantwortet nur: **Was ist aktuell bewiesen, was ist blockiert und was ist der nächste Engpass?**  
> Bedienung: `ANLEITUNG.md` · Aufgaben: `Docs/TODO.md` · Regeln: `AGENTS.md` · aktueller Verbesserungsfokus: `WICHTIG.md`

---

## 1. CURRENT TRUTH

| Bereich | Status | Nachweis / Bedeutung |
|---|---|---|
| Headless Core | 🟢 BEWIESEN | 190 Kombinationen, 570 deterministische Checks |
| Repository-Baseline | 🟢 BEWIESEN | vollständiger Projektbaum über PR-/CI-Pfad |
| Static/Contract CI | 🟢 BEWIESEN | aktueller Runtime-v3-Branch `static-and-contract` PASS |
| Repository Quality | 🟢 BEWIESEN | aktueller Runtime-v3-Branch `repository-quality` PASS |
| P0 Ruleset Contract | 🟢 IMPLEMENTIERT | zentraler fail-closed Soll-/Ist-Vertrag |
| Public Ruleset Verify | 🟢 IMPLEMENTIERT | tokenfreie Live-Abfrage ohne Adminrecht |
| Infrastructure Evidence Bundle | 🟢 IMPLEMENTIERT | JSON + Freshness + SHA-256 + Live-Recheck |
| P0 Infrastructure Observer | 🟢 IMPLEMENTIERT | GitHub-hosted, täglich/manuell, Artifact auch bei FAIL |
| Runner Readiness Contract v3 | 🟢 IMPLEMENTIERT | Repo-/HEAD-/Maschinenbindung + exakter Check-Satz |
| Runner Enable Gate | 🟢 IMPLEMENTIERT | Kontext und Worktree direkt vor Variable-Write erneut geprüft |
| Runtime Evidence Contract v3 | 🟢 IMPLEMENTIERT + HOSTED GEPRÜFT | Run-ID, Repo/HEAD/Maschine, Freshness, Telemetrie-Datei und Hash fail-closed |
| CP1 Telemetrie v3 | 🟢 IMPLEMENTIERT + HOSTED VERTRAG GEPRÜFT | Unreal schreibt laufgebundene `run_id`; echte UE-Erzeugung noch offen |
| Reales P0-Ruleset auf GitHub | 🔴 OFFEN | letzte Live-Abfrage: Ruleset-Liste `[]` |
| UE 5.8 Build | 🟡 UNBEOBACHTET | echte UE-5.8-Maschine erforderlich |
| Character Spawn + Movement | 🟡 UNBEOBACHTET | echter Runtime-Lauf fehlt |
| CP1 Gate | 🟡 BLOCKIERT | Vertrag gehärtet; darf ohne echte frische UE-Evidence nicht GREEN werden |
| Self-hosted UE-Runner | 🔴 OFFEN | Registrierung/Labels/Readiness noch nicht real bewiesen |

**Evidence-Regel:** `IMPLEMENTIERT` oder `HOSTED GEPRÜFT` ist nicht automatisch `RUNTIME BEWIESEN`. Hosted Tests beweisen die Ablehnungs-/Vertragslogik. Ein CP1-PASS entsteht ausschließlich durch den echten UE-5.8-Lauf mit laufgebundener Telemetrie und anschließendem Gate-PASS.

---

## 2. AKTUELLER REPOSITORY-STAND

PR #6 `infra: bind UE runner readiness evidence to checkout and machine` ist gemergt.

`main` danach:

```text
367efbd72d4918f6acb3c2a291e9493b507f7344
```

Aktuell offen: PR #7 `infra: bind CP1 runtime GREEN to the real Unreal run`.

Technischer Hosted-Head vor dieser Doku-Synchronisierung:

```text
a1870f7ff178649b91d84bf3aadec917c0eaf2a8
```

Abnahme dieses Heads:

- `static-and-contract`: PASS
- `repository-quality`: PASS
- neue Runtime-Evidence-v3-Regressionen: PASS
- statischer C++↔Python-v3-Contract: PASS
- Whitespace: PASS
- Iteration Guard: PASS
- `cp1-runtime`: SKIPPED — weiterhin kein echter UE-Runtime-PASS

---

## 3. WAS BEREITS FUNKTIONIERT

- Headless-Regelwerk und deterministische Tests
- 2-aus-20-Fähigkeitenmodell mit 190 Kombinationen
- Diagnose-, Repair-, Learning- und Attribution-Grundlagen
- CP1 Game-/Editor-Targets und Primary Game Module
- GitHub `Validate` Workflow
- `Quality Guard` mit Iteration Guard
- optionaler `CP1 UE 5.8 Runtime` Workflow
- zentraler GitHub-P0-Ruleset-Vertrag
- sicherer Ruleset-Upsert über Admin-Assistent
- tokenfreier öffentlicher Ruleset-Live-Verifier
- täglicher GitHub-hosted Infrastructure Observer
- maschinenlesbares GitHub-P0-Evidence-Bundle
- Live-Revalidator mit Bindung an aktuellen `main`-SHA und Ruleset-ID
- Runner-Identity-Schicht für Repository, HEAD, Worktree und pseudonymen Maschinenfingerprint
- Runner-Readiness-Contract Schema v3
- Admin-Freigabegate revalidiert Repo, HEAD, Maschine und Worktree vor `UE58_RUNNER_ENABLED=true`
- Runtime-Evidence-Contract Schema v3
- Telemetrie-Schema v3 mit Unreal-zurückgeschriebener `run_id`
- Stale-Purge für altes Runtime-JSON, alte Telemetrie und alten Automation-Report
- Runtime-Collector bindet Evidence an Repo, HEAD und Maschine
- tatsächliche Telemetrie-Datei wird SHA-256-gebunden
- Runtime-Gate liest aktuellen Kontext und reale Telemetrie erneut
- kanonischer CP1-Orchestrator: Readiness → Preflight → Runtime → Gate
- CODEOWNERS, Dependabot, PR-/Issue-Templates
- getrenntes Dokumentations-Cockpit

---

## 4. INFRASTRUKTUR-EVIDENCE

### Collector

```bash
python3 Scripts/github_p0_evidence.py
```

Erzeugt `Diagnostics/Infrastructure/github_p0_evidence.json` mit Live-`main`-SHA, Ruleset-ID/-Status, Quellen, Fehlern und Integritätswert.

### Validator

```bash
python3 Scripts/github_p0_evidence_validate.py
```

Gespeicherter PASS reicht nie allein. Der Validator prüft Freshness und Integrität und liest GitHub danach erneut live. Nur bei identischem `main`-SHA, identischer Ruleset-ID und erneut vollständigem P0-Contract entsteht:

```text
GITHUB_P0_EVIDENCE: PASS
```

Detailanleitung: `Docs/P0_INFRASTRUCTURE_EVIDENCE.md`.

---

## 5. RUNNER-READINESS — SCHEMA v3

Die lokale Runner-Evidence ist gebunden an:

```text
Repository exakt provoware/bunkergame
→ vollständiger Git-HEAD
→ Worktree sauber
→ pseudonymer Maschinenfingerprint
→ exakt definierter Pflichtcheck-Satz
→ UE Build.version exakt 5.8
→ Freshness ≤ 30 Minuten
```

Vor `UE58_RUNNER_ENABLED=true` wird derselbe Kontext erneut live bestimmt. Kopierte Evidence, anderer HEAD, andere Maschine, falsches Repository, ein nachträglich verschmutzter Worktree, alte Schema-v2-Evidence sowie fehlende/zusätzliche Checks blockieren.

`RUNNER_READINESS: PASS` beweist nur Maschinenbereitschaft, nicht CP1 Runtime.

---

## 6. CP1 RUNTIME-EVIDENCE — SCHEMA v3

Der neue Runtime-Vertrag behandelt GREEN als laufgebundene Kette:

```text
alte Runtime-Artefakte entfernen
→ Repo/HEAD/Maschine/Worktree vorprüfen
→ neue zufällige run_id
→ UE 5.8 Build
→ Unreal mit -CP1EvidenceRunId starten
→ C++-Test verlangt run_id
→ Unreal schreibt Telemetrie v3 + dieselbe run_id
→ Telemetrie fail-closed validieren
→ tatsächliche Datei hashen
→ Runtime Evidence v3 versiegeln
→ Gate liest aktuellen Kontext + reale Datei erneut
→ Freshness + run_id + Hash + Inhalt + Schritte prüfen
→ CP1_GATE GREEN / RED / BLOCKED
```

### No-Fake-Success-Invarianten

- alte Runtime-Evidence wird vor einem neuen Versuch gelöscht
- alte Telemetrie wird vor einem neuen Versuch gelöscht
- alter Automation-Report wird vor einem neuen Versuch gelöscht
- Cleanup-Fehler blockiert
- Runtime Evidence v2 wird nicht als GREEN akzeptiert
- Telemetrie v2 wird nicht als GREEN akzeptiert
- `runtime_executed` muss exakt `true` sein
- `cp1_pass` muss exakt `true` sein
- erforderliche Runtime-Schritte müssen exakt und in Reihenfolge GREEN sein
- Returncodes müssen echte Integer `0` sein; Bool zählt nicht
- Runtime-Evidence maximal 30 Minuten alt
- Evidence-HEAD muss aktuellem Checkout entsprechen
- Maschinenfingerprint muss aktuellem Host entsprechen
- Gate verlangt weiterhin sauberen Worktree
- Telemetrie-`run_id` muss Evidence-`run_id` entsprechen
- tatsächlicher Telemetrie-SHA-256 muss Evidence entsprechen
- eingebettete und tatsächliche Telemetrie müssen identisch sein
- Positions-/Displacement-Werte werden auf Konsistenz geprüft
- SHA-256 ist Integritätskontrolle, keine Signatur oder Hardware-Attestation

### Kanonischer Start

Linux/macOS-Shell:

```bash
./RUN_CP1_UE58_ALL.sh
```

Windows:

```text
RUN_CP1_UE58_ALL.bat
```

Direkt:

```bash
python3 Scripts/run_cp1_ue58.py
```

Der Orchestrator führt jetzt genau aus:

```text
Runner Readiness
→ Repository Preflight
→ UE Build + Character Spawn + Movement + bound Evidence
→ Live Runtime Gate
```

---

## 7. WAS NOCH NICHT BEWIESEN IST

- echtes aktives P0-Ruleset auf GitHub
- `GITHUB_P0_PUBLIC_RULESET: PASS`
- `GITHUB_P0_EVIDENCE: PASS` aus realem Ruleset
- Self-hosted UE-5.8-Runner online und korrekt gelabelt
- echter `RUNNER_READINESS: PASS` Schema v3 auf Zielmaschine
- UE-5.8-Kompilierung auf Zielmaschine
- Unreal Editor Boot / Automation
- echter Character Spawn
- echte 3D-Bewegung
- echte Telemetrie v3 aus Unreal
- echter `CP1_GATE: GREEN`
- Animation
- Runtime-Ability-Effekte
- Interaction → Task → Ability → XP Vertical Slice
- Save/Load
- Event-, Crowd- und Rival-Runtime
- Packaged Build

Diese Punkte bleiben **UNBEOBACHTET/BLOCKIERT**, bis ein passender realer Test sie tatsächlich ausgeführt hat.

---

## 8. AKTUELLER P0-ENGPASS

### P0-A — reales GitHub-Ruleset

Sollname: `BUNKER BEATS P0 main gate`

Pflicht:

- `enforcement=active`
- nur `refs/heads/main`
- keine Bypass-Akteure
- Pull Request erforderlich
- `static-and-contract` required
- `repository-quality` required
- Branch vor Merge aktuell
- Force-Push blockiert
- Löschen blockiert
- `cp1-runtime` noch nicht global required

Letzte echte Live-Evidence:

```text
Repository-Rulesets: []
main.protected=false
```

### P0-B — Self-hosted UE-5.8-Runner

Benötigte Labels:

- `self-hosted`
- `unreal`
- `ue-5.8`

Nach aktivem Ruleset und registriertem Runner:

```bash
python3 Scripts/p0_preflight.py --full
```

Erst nach realem Readiness-PASS und erneuter Kontextprüfung darf die Runner-Variable freigegeben werden.

### P0-C — erster echter CP1-v3-Lauf

Danach den kanonischen Orchestrator ausführen. Erst wenn Unreal selbst die passende `run_id` in Telemetrie v3 zurückschreibt und das Live-Gate anschließend GREEN liefert, ist CP1 fachlich bewiesen.

---

## 9. AUTOMATISCHE QUALITÄT

1. **Validate** — CP1-/Contract-/Headless-Prüfungen.
2. **Quality Guard** — Repository-Hygiene und Dokumentintegrität.
3. **P0 Regression Tests** — Control Plane, Ruleset, Infrastructure Evidence, Runner-Binding und Runtime-Evidence-v3.
4. **Iteration Guard** — `WICHTIG.md` + append-only `CODEQUALITÄT.md`.
5. **P0 Infrastructure Observer** — echter externer GitHub-Live-Zustand.
6. **CP1 UE 5.8 Runtime** — nur bei real freigeschaltetem Self-hosted Runner.

Runtime-Regressionen prüfen unter anderem:

- Schema-v2-Rejection
- stale/future Runtime-Evidence
- HEAD-/Maschinen-/Repository-Drift
- Step-Duplikate und falsche Reihenfolge
- Bool-Returncodes und Bool-Numerik
- Telemetrie-v2-Rejection
- Run-ID-Mismatch
- Datei-Hash-Drift
- eingebettete ≠ tatsächliche Telemetrie
- Evidence-Integritätsänderung
- Positions-/Displacement-Widerspruch
- Stale-Purge alter Runtime-Artefakte
- C++↔Python-Run-ID-Wiring

---

## 10. NEXT BEST ACTION

1. finalen PR-#7-Doku-Head erneut durch Validate + Quality Guard schicken.
2. PR #7 nur bei erneut vollständigem Hosted-PASS integrieren.
3. reales GitHub-P0-Ruleset auf dem Admin-Rechner anwenden.
4. Public Ruleset PASS + Infrastructure Evidence PASS unabhängig beweisen.
5. Self-hosted UE-5.8-Runner registrieren und Labels prüfen.
6. auf derselben Zielmaschine im sauberen `main`-Checkout `p0_preflight.py --full` ausführen.
7. Runner-Variable erst nach frischer Schema-v3-Readiness freigeben.
8. `Scripts/run_cp1_ue58.py` real ausführen.
9. Runtime Evidence v3, Telemetrie v3 und `CP1_GATE: GREEN` gemeinsam prüfen.
10. erst danach CP1 als GREEN markieren und den Interaction-Vertical-Slice beginnen.

---

## 11. NÄCHSTER VERTIKALSCHNITT NACH CP1

Erst nach echtem CP1-PASS:

```text
Character → Interaction → erster Task → Ability-Effekt → XP
```

Crowd, Rival und größere Event-Runtime bleiben dahinter, solange sie keine direkte Abhängigkeit für diesen Slice sind.
