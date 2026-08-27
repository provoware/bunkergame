# BUNKER BEATS — PROJEKTSTATUS

**Stand:** 2026-08-27  
**Phase:** Technical/Core Integration  
**Aktueller Checkpoint:** P0 Runner Bootstrap → CP1 Runtime  
**Arbeitszweig:** `infra/ue58-runner-bootstrap-acceptance`

> Dieses Dokument beantwortet nur: **Was ist aktuell bewiesen, was ist blockiert und was ist der nächste Engpass?**  
> Bedienung: `ANLEITUNG.md` · Aufgaben: `Docs/TODO.md` · Regeln: `AGENTS.md` · aktueller Verbesserungsfokus: `WICHTIG.md`

---

## 1. CURRENT TRUTH

| Bereich | Status | Nachweis / Bedeutung |
|---|---|---|
| Headless Core | 🟢 BEWIESEN | 190 Kombinationen, 570 deterministische Checks |
| Repository-Baseline | 🟢 BEWIESEN | vollständiger Projektbaum über PR-/CI-Pfad |
| Static/Contract CI | 🟢 BEWIESEN | PR #7 final Hosted-PASS vor Merge |
| Repository Quality | 🟢 BEWIESEN | PR #7 final Hosted-PASS inklusive Runtime-v3-Regressionen |
| P0 Ruleset Contract | 🟢 IMPLEMENTIERT | zentraler fail-closed Soll-/Ist-Vertrag |
| Public Ruleset Verify | 🟢 IMPLEMENTIERT | tokenfreie Live-Abfrage ohne Adminrecht |
| Infrastructure Evidence Bundle | 🟢 IMPLEMENTIERT | JSON + Freshness + SHA-256 + Live-Recheck |
| P0 Infrastructure Observer | 🟢 IMPLEMENTIERT | GitHub-hosted, täglich/manuell, Artifact auch bei FAIL |
| Runner Readiness Contract v3 | 🟢 IMPLEMENTIERT | Repo-/HEAD-/Maschinenbindung + exakter Check-Satz |
| CP1 Runtime Evidence Contract v3 | 🟢 IMPLEMENTIERT + HOSTED GEPRÜFT | Run-ID, Kontextbindung, Telemetrie-Datei, Hash, Freshness |
| Runner Bootstrap Acceptance | 🟢 IMPLEMENTIERT | manueller GitHub-Job + Readiness + Artifact; realer Lauf noch offen |
| Public Runner Bootstrap Verify | 🟢 IMPLEMENTIERT | GitHub Run/Job/Runner/Labels werden tokenfrei rückgelesen |
| Runner Enable Gate | 🟢 IMPLEMENTIERT | verlangt Ruleset + frischen öffentlichen Bootstrap-PASS + aktuellen sauberen Admin-Checkout |
| Reales P0-Ruleset | 🔴 OFFEN | letzte Live-Evidence vor dieser Iteration: Rulesets `[]` |
| Self-hosted UE-5.8-Runner | 🔴 OFFEN | noch kein realer Bootstrap-Job nachgewiesen |
| `UE58_RUNNER_BOOTSTRAP: PASS` | 🔴 OFFEN | Workflow noch nicht real auf Runner ausgeführt |
| UE 5.8 Build | 🟡 UNBEOBACHTET | echter Zielmaschinenlauf fehlt |
| Character Spawn + Movement | 🟡 UNBEOBACHTET | echter Runtime-Lauf fehlt |
| CP1 Gate | 🟡 BLOCKIERT | darf ausschließlich aus echter Runtime-v3-Evidence GREEN werden |

**Evidence-Regel:** `IMPLEMENTIERT`, `HOSTED GEPRÜFT`, `RUNNER_READINESS: PASS` und `UE58_RUNNER_BOOTSTRAP: PASS` sind unterschiedliche Evidenzstufen. Nur ein echter UE-5.8-Runtime-Lauf mit `CP1_GATE: GREEN` beweist CP1.

---

## 2. AKTUELLER REPOSITORY-STAND

PR #7 `infra: bind CP1 runtime GREEN to the real Unreal run` ist gemergt.

`main` danach:

```text
b6109c60d544a55091bcfcb8ef106eeeb5f012c8
```

Die laufende Iteration `infra/ue58-runner-bootstrap-acceptance` fügt **keine Gameplay-Funktion** hinzu. Sie schließt die Beweislücke zwischen „lokale Maschine ist bereit“ und „GitHub hat einen passenden Self-hosted Runner tatsächlich registriert, erreicht und für einen Job eingesetzt“.

---

## 3. BEREITS IMPLEMENTIERTE P0-SCHICHTEN

### GitHub-Schutz

- zentraler Ruleset-Vertrag
- sicherer Admin-Doctor
- Ruleset-Upsert mit Read-back
- tokenfreier Public Ruleset Verify
- Infrastructure Evidence Bundle + Live-Revalidation
- GitHub-hosted Infrastructure Observer

### Runner Readiness v3

- Repository exakt `provoware/bunkergame`
- vollständiger Git-HEAD
- sauberer Worktree
- pseudonymer Maschinenfingerprint
- exakter Pflichtcheck-Satz
- echte `Build.version` exakt 5.8
- Freshness ≤ 30 Minuten

### Runtime Evidence v3

```text
stale artifacts purge
→ repo/head/machine/worktree
→ random run_id
→ UE Build
→ run_id an Unreal
→ C++ schreibt run_id zurück
→ Telemetrie v3
→ Datei-SHA-256
→ Runtime Evidence v3
→ Gate revalidiert Kontext + echte Datei
```

Hosted Tests beweisen die Vertragslogik; der echte UE-Lauf bleibt offen.

---

## 4. NEU — SERVERVERMITTELTER RUNNER-BOOTSTRAP

### Warum diese Stufe nötig ist

Lokale Readiness kann beweisen, dass ein Checkout auf einer Maschine UE 5.8 bereitstellt. Sie beweist nicht, dass GitHub:

- diese Maschine als Runner kennt,
- sie aktuell erreichen kann,
- die Labels `self-hosted`, `unreal`, `ue-5.8` tatsächlich für die Jobzustellung verwendet,
- einen Job auf dem aktuellen `main` dorthin ausgeliefert hat.

Deshalb existiert jetzt ein eigener manueller Workflow:

```text
UE 5.8 Runner Bootstrap Acceptance
```

Datei:

```text
.github/workflows/ue58-runner-bootstrap.yml
```

Eigenschaften:

- nur `workflow_dispatch`
- `runs-on: [self-hosted, unreal, ue-5.8]`
- `contents: read`
- kein CP1
- kein UE-Projektbuild
- kein Variablen-Write
- Readiness v3
- Bootstrap-Evidence
- Artifact auch bei FAIL

---

## 5. BOOTSTRAP-EVIDENCE UND PUBLIC VERIFY

Lokales/Artifact-Bundle:

```text
Diagnostics/Runtime/runner_bootstrap_evidence.json
```

Erzeuger:

```bash
python3 Scripts/runner_bootstrap_evidence.py
```

Unabhängiger Serverbeweis:

```bash
python3 Scripts/github_runner_bootstrap_public_verify.py
```

Der Verifier liest GitHub live:

```text
aktueller main-SHA
→ neuester workflow_dispatch-Bootstrap auf genau diesem SHA
→ completed + success
→ runner-bootstrap-acceptance Job
→ echter runner_name
→ tatsächliche Job-Labels
→ Checkout-/Readiness-/Bind-/Upload-Schritte SUCCESS
→ Freshness ≤ 30 Minuten
```

Nur dann:

```text
UE58_RUNNER_BOOTSTRAP: PASS
```

Ein älterer PASS eines früheren `main`-SHA oder ein älterer Erfolg vor einem neueren Fehllauf zählt nicht als aktuelle Freigabe.

---

## 6. RUNNER-AKTIVIERUNG

Ein lokales `runner_readiness.json` ist **nicht mehr alleinige Aktivierungsautorität**.

Der sichere Pfad lautet:

```bash
python3 Scripts/github_p0_admin.py --apply-ruleset --enable-runner-variable
```

Vor dem Write verlangt der Helper:

```text
Ruleset anwenden + Read-back PASS
→ öffentlicher Runner-Bootstrap erneut live PASS
→ Bootstrap auf aktuellem main
→ Bootstrap frisch
→ Admin-Checkout Repository exakt
→ Admin-HEAD == aktueller main
→ Admin-Worktree sauber
→ erst dann UE58_RUNNER_ENABLED=true
```

`--enable-runner-variable` ohne `--apply-ruleset` wird blockiert.

---

## 7. WAS NOCH NICHT BEWIESEN IST

- reales aktives P0-Ruleset auf GitHub
- `GITHUB_P0_PUBLIC_RULESET: PASS`
- `GITHUB_P0_EVIDENCE: PASS`
- Self-hosted Runner real registriert/erreichbar
- realer GitHub-Job auf `[self-hosted, unreal, ue-5.8]`
- echter `RUNNER_READINESS: PASS` im Bootstrap
- echter `UE58_RUNNER_BOOTSTRAP: PASS`
- `UE58_RUNNER_ENABLED=true` nach Bootstrap-Proof
- UE-5.8-Projektbuild
- Unreal Editor Automation
- Character Spawn
- Movement
- Telemetrie v3 aus echtem Unreal
- `CP1_GATE: GREEN`
- Animation
- Runtime-Ability-Effekte
- Interaction → Task → Ability → XP Vertical Slice
- Save/Load
- Packaged Build

Diese Punkte bleiben **UNBEOBACHTET/BLOCKIERT**, bis die jeweilige reale Stufe tatsächlich ausgeführt wurde.

---

## 8. AKTUELLER P0-ENGPASS

### P0-A — reales Ruleset

Sollname:

```text
BUNKER BEATS P0 main gate
```

Letzter belegter externer Zustand vor W-011:

```text
Repository-Rulesets: []
main.protected=false
```

### P0-B — Runner registrieren und Bootstrap ausführen

Nach aktivem Ruleset:

1. Runner über GitHub `Settings → Actions → Runners` registrieren.
2. Labels `unreal`, `ue-5.8` ergänzen.
3. Workflow `UE 5.8 Runner Bootstrap Acceptance` auf `main` manuell starten.
4. `github_runner_bootstrap_public_verify.py` ausführen.
5. Nur bei `UE58_RUNNER_BOOTSTRAP: PASS` zur Aktivierung weitergehen.

### P0-C — CP1

Erst danach:

```bash
python3 Scripts/run_cp1_ue58.py
```

Nur der echte Runtime-v3-Gate-PASS darf CP1 GREEN machen.

---

## 9. AUTOMATISCHE QUALITÄT

1. **Validate** — CP1-/Contract-/Headless-Prüfungen.
2. **Quality Guard** — Repository-Hygiene und Dokumentintegrität.
3. **P0 Regression Tests** — Ruleset, Infrastructure Evidence, Runner Binding, Runtime v3 und Runner Bootstrap.
4. **Iteration Guard** — `WICHTIG.md` + append-only `CODEQUALITÄT.md`.
5. **P0 Infrastructure Observer** — externer GitHub-Schutzstatus.
6. **UE 5.8 Runner Bootstrap Acceptance** — manuelle, sichere Runner-Zustellung/Readiness; kein CP1.
7. **CP1 UE 5.8 Runtime** — erst nach realer Runner-Freigabe.

Bootstrap-Regressionen prüfen insbesondere:

- nicht-manueller Run blockiert
- falscher/alter `main`-SHA blockiert
- stale Bootstrap blockiert
- fehlendes `ue-5.8`-Label blockiert
- fehlender Readiness-Schritt blockiert
- fehlender Runnername blockiert
- neuer Fehllauf kann älteren Erfolg nicht verdecken
- Variable wird ohne Public Bootstrap nicht geschrieben
- Admin-Checkout muss aktuell und sauber sein
- Bootstrap-Workflow enthält weder CP1 noch Variablen-Write

---

## 10. NEXT BEST ACTION

1. W-011-Folge-PR über Hosted `Validate` + `Quality Guard` abnehmen.
2. Nur bei vollständigem PASS integrieren.
3. reales GitHub-P0-Ruleset anwenden.
4. Ruleset/Public Infrastructure Evidence als PASS beweisen.
5. Self-hosted UE-5.8-Runner registrieren.
6. `UE 5.8 Runner Bootstrap Acceptance` auf aktuellem `main` manuell ausführen.
7. `UE58_RUNNER_BOOTSTRAP: PASS` öffentlich nachweisen.
8. Runner-Variable über `--apply-ruleset --enable-runner-variable` freigeben.
9. echten CP1-v3-Lauf ausführen.
10. erst nach `CP1_GATE: GREEN` den Interaction-Vertical-Slice beginnen.

---

## 11. NÄCHSTER VERTIKALSCHNITT NACH CP1

Erst nach echtem CP1-PASS:

```text
Character → Interaction → erster Task → Ability-Effekt → XP
```

Crowd, Rival und größere Event-Runtime bleiben dahinter, solange sie keine direkte Abhängigkeit für diesen Slice sind.
