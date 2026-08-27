# BUNKER BEATS — GITHUB P0 SETUP

> Ziel: `main` absichern, den Schutz unabhängig beweisen, einen echten UE-5.8-Self-hosted-Runner **durch GitHub selbst** abnehmen und erst danach CP1 freigeben.

---

## 1. EMPFOHLENE REIHENFOLGE

```text
Hosted Quality grün
   ↓
Admin-Doctor PASS
   ↓
aktives Repository Ruleset für main
   ↓
GITHUB_P0_PUBLIC_RULESET: PASS
   ↓
GITHUB_P0_EVIDENCE: PASS
   ↓
Self-hosted Runner registrieren
   ↓
manuellen "UE 5.8 Runner Bootstrap Acceptance" auf main starten
   ↓
GitHub weist [self-hosted, unreal, ue-5.8] tatsächlich zu
   ↓
Readiness Schema v3 läuft auf diesem Runner
   ↓
UE58_RUNNER_BOOTSTRAP: PASS
   ↓
Admin-Checkout = aktueller main + sauber
   ↓
UE58_RUNNER_ENABLED=true
   ↓
echter CP1 Runtime-Lauf
   ↓
CP1_GATE: GREEN
```

### Read-only Einstieg

```bash
python3 Scripts/p0_preflight.py
```

Vollprüfung nach einem Bootstrap-Lauf:

```bash
python3 Scripts/p0_preflight.py --full
```

`P0_PREFLIGHT: PASS`, `RUNNER_READINESS: PASS` und `UE58_RUNNER_BOOTSTRAP: PASS` sind ausdrücklich **keine CP1-Runtime-Pässe**.

---

## 2. P0-RULESET

Bevorzugter Schutz:

```text
BUNKER BEATS P0 main gate
```

Verbindlicher Vertrag:

- `enforcement=active`
- ausschließlich `refs/heads/main`
- Pull Request vor Integration
- `required_approving_review_count=0` für das Solo-Repository
- alte Reviews bei neuen Änderungen verwerfen
- offene Review-Diskussionen müssen gelöst sein
- Required Check `static-and-contract`
- Required Check `repository-quality`
- Branch vor Merge aktuell halten
- Force-Push sperren
- Löschen von `main` sperren
- keine Bypass-Akteure
- `cp1-runtime` noch nicht global required

Zentrale Vertragslogik:

```text
Scripts/github_p0_ruleset.py
```

### Sicher anwenden

```bash
python3 Scripts/github_p0_admin.py --doctor
```

Nur bei:

```text
GITHUB_ADMIN_PREFLIGHT: PASS
```

weiter:

```bash
python3 Scripts/github_p0_admin.py --apply-ruleset
```

Ziel:

```text
GITHUB_P0_RULESET_GATE: PASS
```

Das Ruleset wird als sicheres Upsert behandelt:

```text
0 Soll-Rulesets → Create
1 Soll-Ruleset  → Update
>1              → BLOCKED
```

Klassische Branch Protection bleibt mit `--apply` nur als Fallback erhalten.

---

## 3. UNABHÄNGIGER GITHUB-SCHUTZBEWEIS

Ohne GitHub-Login oder Admin-Token:

```bash
python3 Scripts/github_p0_public_verify.py
```

Ziel:

```text
GITHUB_P0_PUBLIC_RULESET: PASS
```

Archivierte Infrastruktur-Evidence:

```bash
python3 Scripts/github_p0_evidence.py
python3 Scripts/github_p0_evidence_validate.py
```

Ziel:

```text
GITHUB_P0_EVIDENCE: PASS
```

Der Validator akzeptiert gespeicherte Evidence niemals allein. Er liest GitHub erneut live und verlangt weiterhin denselben aktuellen `main`-SHA, dieselbe Ruleset-ID und denselben vollständigen Vertrag.

Detail: `Docs/P0_INFRASTRUCTURE_EVIDENCE.md`.

---

## 4. SELF-HOSTED UE-5.8-RUNNER REGISTRIEREN

GitHub:

`Repository → Settings → Actions → Runners → New self-hosted runner`

Die **von GitHub aktuell erzeugten** Installations-/Registrierungsbefehle verwenden. Keine alte Runner-Version aus einer Dokumentation kopieren.

Zusätzliche Labels:

```text
unreal
ue-5.8
```

GitHub ergänzt `self-hosted` automatisch.

Registrierungstoken niemals in Git, Markdown, Issues, Screenshots oder Logs speichern.

---

## 5. SERVERVERMITTELTE RUNNER-ABNAHME

Nach Registrierung wird **noch kein CP1 gestartet**.

Stattdessen in GitHub Actions manuell starten:

```text
UE 5.8 Runner Bootstrap Acceptance
```

Der Workflow liegt in:

```text
.github/workflows/ue58-runner-bootstrap.yml
```

Er besitzt bewusst nur:

```yaml
on:
  workflow_dispatch:
```

und der Job verlangt:

```text
[self-hosted, unreal, ue-5.8]
```

### Was GitHub damit beweisen muss

Ein erfolgreicher Lauf zeigt, dass GitHub:

1. das Repository und den aktuellen `main`-SHA kennt,
2. einen passenden Self-hosted Runner findet,
3. den Job tatsächlich an ihn zustellt,
4. einen echten `runner_name` zurückliefert,
5. die benötigten Job-Labels bestätigt,
6. `runner_readiness.py` dort erfolgreich ausführt,
7. die Bootstrap-Evidence erzeugt und als Artifact hochlädt.

### Was der Workflow ausdrücklich NICHT tut

- kein UE-Projektbuild
- kein Character Spawn
- kein Movement-Test
- kein CP1-Gate
- kein `UE58_RUNNER_ENABLED=true`
- keine GitHub-Adminänderung

Damit ist der Bootstrap eine eigene sichere Infrastruktur-Stufe.

---

## 6. RUNNER-READINESS — SCHEMA v3

Im Bootstrap läuft:

```bash
python3 Scripts/runner_readiness.py
```

Readiness prüft unter anderem:

- `BunkerBeats.uproject`
- Editor-Target
- UE-Root
- UnrealEditor
- UE-Build-Skript
- echte `Engine/Build/Build.version`
- exakt UE 5.8
- Python
- Schreibbarkeit des Repositories
- mindestens 5 GB freien Speicher
- sauberen Git-Arbeitsstand
- Repository exakt `provoware/bunkergame`
- vollständigen 40-stelligen Git-HEAD
- pseudonymen Maschinenfingerprint
- exakt definierten Pflichtcheck-Satz

Evidence:

```text
Diagnostics/Runtime/runner_readiness.json
```

Der Maschinenfingerprint ist SHA-256 aus Hostname, OS und Architektur. Er ist **keine Hardware-Attestation** und enthält keine Hardware-Seriennummer.

`RUNNER_READINESS: PASS` beweist Maschinenbereitschaft, nicht CP1.

---

## 7. BOOTSTRAP-EVIDENCE

Nach Readiness erzeugt der Workflow:

```text
Diagnostics/Runtime/runner_bootstrap_evidence.json
```

über:

```bash
python3 Scripts/runner_bootstrap_evidence.py
```

Das Bundle bindet unter anderem:

- Repository
- `refs/heads/main`
- GitHub-Dispatch-SHA
- lokalen Checkout-SHA
- Workflowname
- Jobname
- Run-ID
- Run-Attempt
- Runnername
- Runner-OS/-Architektur
- Maschinenfingerprint
- Readiness-Datei + SHA-256
- Readiness-v3-Validierung

und hält zwingend getrennt:

```text
runtime_executed=false
cp1_pass=false
```

Das Artifact wird auch bei Fehlern hochgeladen, damit Diagnose-Evidence nicht mit dem Fehlschlag verschwindet.

---

## 8. UNABHÄNGIGER RUNNER-SERVERBEWEIS

Nach dem manuellen Bootstrap:

```bash
python3 Scripts/github_runner_bootstrap_public_verify.py
```

Der Verifier benötigt keinen Admin-Token und liest GitHub live zurück:

```text
aktueller main-SHA
→ Workflow-Runs für UE 5.8 Runner Bootstrap Acceptance
→ nur workflow_dispatch
→ nur aktueller main-SHA
→ neuesten passenden Lauf wählen
→ completed + success
→ zugehörige Jobs lesen
→ genau runner-bootstrap-acceptance
→ runner_name vorhanden
→ Labels enthalten self-hosted + unreal + ue-5.8
→ Checkout/Readiness/Bind/Upload-Schritte erfolgreich
→ Freshness ≤ 30 Minuten
```

Nur dann:

```text
UE58_RUNNER_BOOTSTRAP: PASS
```

### Wichtige Fail-closed-Regel

Ein älterer erfolgreicher Lauf darf einen **neueren fehlgeschlagenen Lauf auf demselben aktuellen `main`** nicht verdecken. Der neueste passende Lauf ist maßgeblich.

Ein Bootstrap eines alten `main`-SHA verliert nach einem neuen Merge automatisch seine Aktivierungswirkung.

---

## 9. P0-PREFLIGHT --FULL

Nach dem Bootstrap:

```bash
python3 Scripts/p0_preflight.py --full
```

Reihenfolge:

```text
Branch Lifecycle
→ Static Contract
→ Repository Quality
→ Public Ruleset Live Verify
→ Public Runner Bootstrap Verify
→ lokale Runner Readiness v3
→ Next Best Action
```

Fehlt der Bootstrap-PASS, empfiehlt der Preflight **nicht** die Runner-Aktivierung, sondern zuerst den manuellen Bootstrap-Workflow.

---

## 10. RUNNER-VARIABLE FREIGEBEN

Der Aktivierungspfad wurde bewusst entkoppelt: Ein lokales `runner_readiness.json` ist **nicht mehr alleinige Aktivierungsautorität**.

Nach frischem `UE58_RUNNER_BOOTSTRAP: PASS` auf dem aktuellen `main`:

```bash
python3 Scripts/github_p0_admin.py --apply-ruleset --enable-runner-variable
```

Der Helper verlangt:

```text
Adminrecht
→ P0 Ruleset anwenden/rücklesen
→ Public Runner Bootstrap erneut live prüfen
→ Bootstrap muss auf aktuellem main liegen
→ Bootstrap ≤ 30 Minuten
→ Admin-Checkout Repository exakt
→ Admin-Checkout HEAD == aktueller main-SHA
→ Admin-Worktree sauber
→ erst dann UE58_RUNNER_ENABLED=true
```

`--enable-runner-variable` ohne `--apply-ruleset` wird blockiert.

Vorteil: Das Admin-Terminal muss nicht mehr im selben Runner-Workspace liegen. GitHub ist die Vermittlungs- und Beweisinstanz für die Runner-Abnahme.

---

## 11. ERSTER ECHTER CP1-LAUF

Erst nach Runner-Aktivierung:

```text
CP1 UE 5.8 Runtime
```

oder auf der Zielmaschine über den kanonischen Orchestrator:

```bash
python3 Scripts/run_cp1_ue58.py
```

Beweiskette Runtime v3:

```text
Readiness
→ Preflight
→ alte Runtime-Artefakte sicher entfernen
→ zufällige run_id
→ UE 5.8 Build
→ Unreal erhält run_id
→ Character Spawn + Movement
→ Unreal schreibt Telemetrie v3 + run_id
→ Telemetrie-Datei SHA-256
→ Runtime Evidence v3
→ Gate liest Kontext + reale Telemetrie erneut
→ CP1_GATE: GREEN / RED / BLOCKED
```

Nur `CP1_GATE: GREEN` aus dem echten Lauf darf CP1 auf GREEN setzen.

---

## 12. ABNAHME-CHECKLISTE

### GitHub-Schutz
- [ ] `static-and-contract` PASS
- [ ] `repository-quality` PASS
- [ ] `GITHUB_ADMIN_PREFLIGHT: PASS`
- [ ] genau ein P0-Ruleset vorhanden
- [ ] Ruleset `active`
- [ ] nur `main` erfasst
- [ ] keine Bypass-Akteure
- [ ] PR-Gate aktiv
- [ ] `static-and-contract` required
- [ ] `repository-quality` required
- [ ] Strictness aktiv
- [ ] Force-Push gesperrt
- [ ] Löschen von `main` gesperrt
- [ ] `GITHUB_P0_PUBLIC_RULESET: PASS`
- [ ] `GITHUB_P0_EVIDENCE: PASS`

### Runner-Bootstrap
- [ ] Self-hosted Runner registriert
- [ ] Labels `unreal`, `ue-5.8` gesetzt
- [ ] `UE 5.8 Runner Bootstrap Acceptance` auf `main` manuell gestartet
- [ ] GitHub weist echten `runner_name` aus
- [ ] Readiness Schema v3 PASS
- [ ] Bootstrap Artifact vorhanden
- [ ] `UE58_RUNNER_BOOTSTRAP: PASS`
- [ ] Bootstrap höchstens 30 Minuten alt
- [ ] Bootstrap gehört zum aktuellen `main`-SHA

### Aktivierung
- [ ] Admin-Checkout exakt `provoware/bunkergame`
- [ ] Admin-HEAD exakt aktueller `main`
- [ ] Admin-Worktree sauber
- [ ] `--apply-ruleset --enable-runner-variable` erfolgreich
- [ ] `UE58_RUNNER_ENABLED=true`

### CP1 Runtime
- [ ] echter UE-5.8-Build
- [ ] echter Character Spawn
- [ ] echte Bewegung
- [ ] Telemetrie v3
- [ ] Runtime Evidence v3
- [ ] `CP1_GATE: GREEN`

---

## Referenzen

- GitHub Repository Rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- GitHub REST Rulesets: https://docs.github.com/en/rest/repos/rules
- GitHub Protected Branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub Self-hosted Runner: https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners
