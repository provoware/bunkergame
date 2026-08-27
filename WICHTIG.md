# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-011 — Self-hosted Runner durch echten GitHub-Job beweisen

**Kategorie:** Self-hosted Runner / Infrastructure Evidence / No-Fake-Success  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — realer Bootstrap-Lauf weiterhin extern offen  
**Nutzen:** 10/10  
**Aufwand:** 4/10  
**Risiko der Umsetzung:** 2/10

### Beobachtung

Bisher konnte die lokale Readiness sehr genau beweisen, dass **eine Maschine** für UE 5.8 vorbereitet ist. Sie beweist aber nicht serverseitig, dass GitHub diese Maschine tatsächlich als Self-hosted Runner mit den benötigten Labels registriert hat, einen Job an sie zustellen kann und der Job auf dem aktuellen `main` erfolgreich ausgeführt wurde.

Der bisherige Aktivierungspfad hing deshalb noch zu stark an einer lokalen `runner_readiness.json`. Das war technisch streng, aber betrieblich unnötig fragil: Admin-Terminal, Projektcheckout und GitHub-Runner-Workspace mussten praktisch eng gekoppelt bleiben.

### Verbesserungsvorschlag

Runner-Registrierung und Runner-Readiness als **serververmittelte Bootstrap-Acceptance** beweisen:

```text
GitHub workflow_dispatch auf main
→ Job verlangt [self-hosted, unreal, ue-5.8]
→ GitHub muss passenden Runner tatsächlich zuweisen
→ Runner checkt exakt den Dispatch-SHA aus
→ runner_readiness.py erzeugt Schema-v3-Evidence
→ Bootstrap-Evidence bindet GitHub-Run + Runner + Checkout + Readiness
→ Artifact wird auch bei Fehlern hochgeladen
→ öffentlicher Verifier liest aktuellen main-SHA
→ liest neuesten Bootstrap-Run auf genau diesem SHA
→ liest dessen Job + runner_name + tatsächliche Job-Labels + Pflichtschritte
→ nur bei frischem vollständigem Erfolg UE58_RUNNER_BOOTSTRAP: PASS
```

### Grund

Ein registrierter Runner ist eine **GitHub-Infrastruktur-Eigenschaft**, keine rein lokale Eigenschaft. Der stärkere Beweis muss daher von GitHub selbst kommen: Ein Job, der ausdrücklich die Labels `self-hosted`, `unreal`, `ue-5.8` verlangt, kann nur erfolgreich werden, wenn GitHub einen passenden Runner tatsächlich findet, den Job zustellt und die Readiness-Schritte dort erfolgreich abschließt.

Das trennt außerdem Admin- und Runner-Arbeitsverzeichnis. Die spätere Aktivierung von `UE58_RUNNER_ENABLED=true` benötigt nicht mehr dieselbe lokale Readiness-Datei im Admin-Checkout, sondern einen frischen serverseitigen Bootstrap-PASS auf dem aktuellen `main`.

### Umgesetzt

- `.github/workflows/ue58-runner-bootstrap.yml` als manueller Bootstrap-Acceptance-Workflow ergänzt.
- Workflow besitzt ausschließlich `workflow_dispatch`; kein PR-, Push- oder Schedule-Trigger.
- Job läuft ausschließlich auf `[self-hosted, unreal, ue-5.8]`.
- Workflow besitzt nur `contents: read`.
- kein UE-Build, kein CP1-Lauf und kein Schreiben von Repository-Variablen im Bootstrap-Workflow.
- `Scripts/runner_bootstrap_evidence.py` erzeugt ein maschinenlesbares Bootstrap-Bundle.
- Bundle bindet Repository, `main`-Ref, GitHub-SHA, Workflow, Job, Run-ID, Run-Attempt, Runnername, OS/Architektur, Maschinenfingerprint und Readiness-SHA-256.
- `runtime_executed=false` und `cp1_pass=false` sind im Bootstrap-Beweis fest getrennt.
- `Scripts/runner_bootstrap_contract.py` zentralisiert Labels, Workflow-/Jobnamen, Pflichtschritte und 30-Minuten-Freshness.
- `Scripts/github_runner_bootstrap_public_verify.py` liest GitHub ohne Token live zurück.
- nur der **neueste** passende Bootstrap-Lauf auf dem aktuellen `main` zählt; ein neuerer Fehllauf kann nicht durch einen älteren Erfolg verdeckt werden.
- Public Verifier verlangt `workflow_dispatch`, aktuellen `main`-SHA, erfolgreichen Job, echten `runner_name`, alle Pflichtlabels und erfolgreiche Pflichtschritte.
- `github_p0_admin.py --enable-runner-variable` akzeptiert lokale Readiness nicht mehr als alleinige Aktivierungsautorität.
- Aktivierung verlangt jetzt frischen öffentlichen Bootstrap-PASS und einen sauberen Admin-Checkout exakt auf demselben aktuellen `main`-SHA.
- Aktivierung ist nur noch zusammen mit `--apply-ruleset` erlaubt.
- `p0_preflight.py --full` prüft den öffentlichen Bootstrap-Beweis zusätzlich zur lokalen Readiness.
- separate Regressionstests decken stale/falsche Runs, fehlende Labels/Schritte, fehlenden Runnernamen, Public-Verify und den Variablen-Write-Guard ab.

### Erwartete Wirkung

- GitHub-Runner-Registrierung wird tatsächlich durch einen zugestellten Job bewiesen
- keine Runner-Aktivierung nur aufgrund einer lokalen JSON-Datei
- Admin-Terminal muss nicht mehr identisch mit dem Runner-Workspace sein
- Runnername und Scheduler-Labels werden aus GitHub-Jobdaten beweisbar
- alter Bootstrap eines früheren `main`-SHA wird automatisch ungültig
- neuerer fehlgeschlagener Bootstrap kann nicht von älterem PASS überdeckt werden
- deutlich bessere Diagnose zwischen „Runner fehlt“, „Runner nicht erreichbar“ und „Readiness auf Runner fehlgeschlagen“
- CP1 bleibt weiterhin strikt von Bootstrap/Readiness getrennt

### Technischer Effekt

```text
REGISTERED RUNNER PROOF
workflow_dispatch
→ runs-on [self-hosted, unreal, ue-5.8]
→ GitHub scheduler
→ real runner_name
→ Readiness v3
→ bootstrap artifact
→ public GitHub run/job re-read
→ UE58_RUNNER_BOOTSTRAP: PASS

ACTIVATION
active P0 ruleset
+ fresh public bootstrap PASS
+ admin checkout == current main
+ clean worktree
→ UE58_RUNNER_ENABLED=true
```

### Aktueller belegter Zustand

- PR #7 CP1 Runtime Evidence Contract v3: gemergt
- `main` danach: `b6109c60d544a55091bcfcb8ef106eeeb5f012c8`
- Bootstrap-Workflow: implementiert
- Bootstrap-Evidence-Script: implementiert
- öffentlicher Bootstrap-Verifier: implementiert
- Aktivierungsgate auf Serverbeweis umgestellt: implementiert
- Bootstrap-/Activation-Regressionstests: implementiert
- reales GitHub-P0-Ruleset: weiterhin nicht aktiv nachgewiesen
- realer Self-hosted UE-5.8-Runner: weiterhin nicht nachgewiesen
- echter `UE58_RUNNER_BOOTSTRAP: PASS`: weiterhin offen
- echter CP1 Runtime-Lauf: weiterhin `UNOBSERVED/BLOCKED`

### Fertig, wenn

- Hosted `static-and-contract` PASS ist
- Hosted `repository-quality` inklusive Bootstrap-Regressionen PASS ist
- Bootstrap-Workflow auf `main` manuell gestartet wird
- GitHub einen Runner mit `self-hosted`, `unreal`, `ue-5.8` tatsächlich zuweist
- Readiness v3 im Bootstrap-Job PASS ist
- Artifact `runner_readiness.json` + `runner_bootstrap_evidence.json` erzeugt wird
- `github_runner_bootstrap_public_verify.py` denselben Lauf serverseitig als `UE58_RUNNER_BOOTSTRAP: PASS` bestätigt
- erst danach `UE58_RUNNER_ENABLED=true` freigegeben wird

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md` und Issue #2. Ein Bootstrap-PASS beweist Runner-Registrierung und Readiness, aber ausdrücklich **keinen UE-Build und keinen CP1-Runtime-PASS**.
