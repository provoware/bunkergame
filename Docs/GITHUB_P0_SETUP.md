# BUNKER BEATS — GITHUB P0 SETUP

> Ziel: `main` absichern, Required Checks verbindlich machen und den UE-5.8-Self-hosted-Runner kontrolliert aktivieren.

---

## 1. REIHENFOLGE

Nicht alles gleichzeitig aktivieren.

```text
Quality Guard grün
   ↓
Branch Ruleset für main
   ↓
Required Checks setzen
   ↓
Self-hosted Runner registrieren
   ↓
Runner Readiness PASS
   ↓
UE58_RUNNER_ENABLED=true
   ↓
CP1 Runtime ausführen
```

### Empfohlener Ein-Befehl-Einstieg

Auf dem Admin-/Entwicklungsrechner:

```bash
python3 Scripts/p0_preflight.py
```

Auf der echten UE-5.8-Maschine:

```bash
python3 Scripts/p0_preflight.py --full
```

Der Preflight ist **read-only**. Er verändert keine GitHub-Einstellung, führt die vorhandenen Gates in definierter Reihenfolge aus und nennt den ersten sinnvollen nächsten Schritt.

`P0_PREFLIGHT: PASS` ist **kein** CP1-Runtime-PASS.

---

## 2. BRANCH-PROTECTION / RULESET FÜR `main`

### Empfohlener Weg

GitHub:

`Repository → Settings → Rules → Rulesets → New branch ruleset`

### Zielbranch

Default branch / `main`.

### Empfohlene Regeln

- Pull Request vor Merge erforderlich
- Required status checks vor Merge erforderlich
- Branch vor Merge auf aktuellem Stand halten
- Force-Push blockieren
- Branch-Löschen blockieren
- direkte Änderungen an `main` vermeiden

### Required Checks

Die tatsächlich erzeugten Check-Namen sind:

```text
static-and-contract
repository-quality
```

Bedeutung:

- `static-and-contract` = Workflow `Validate`
- `repository-quality` = Workflow `Quality Guard`

> Nicht nur nach dem Workflow-Namen suchen. GitHub Branch Protection arbeitet mit den erzeugten Status-/Job-Checks.

### Review-Anforderung

Bei einem Solo-Repository **nicht vorschnell eine zwingende fremde Approval-Anforderung aktivieren**, wenn kein zweiter Reviewer verfügbar ist. Sonst kann sich der Repository-Eigentümer selbst blockieren.

Wenn später ein zweiter Maintainer vorhanden ist:

- mindestens 1 Approval erwägen
- CODEOWNERS-Review für kritische Bereiche erwägen
- alte Approvals bei neuen Commits verwerfen

### CP1 noch nicht global Required

`cp1-runtime` erst dann als verpflichtendes Runtime-Gate verwenden, wenn:

- der Self-hosted Runner dauerhaft erreichbar ist,
- UE 5.8 sauber erkannt wird,
- Readiness mehrfach stabil PASS war,
- reine Doku-/Headless-PRs nicht unnötig blockiert werden.

---

## 3. SELF-HOSTED RUNNER ANLEGEN

GitHub:

`Repository → Settings → Actions → Runners → New self-hosted runner`

GitHub erzeugt dort **plattform- und versionsaktuelle Download-/Konfigurationsbefehle**. Diese Befehle verwenden; keine Runner-Version dauerhaft in dieser Projektdoku festschreiben.

### Benutzerdefinierte Labels bei Erstkonfiguration

Zusätzlich zu den automatischen Standardlabels:

```text
unreal
ue-5.8
```

GitHub setzt `self-hosted` automatisch.

Bei der Erstkonfiguration können mehrere Custom Labels übergeben werden, z. B.:

```bash
./config.sh --url <REPOSITORY_URL> --token <TEMPORARY_REGISTRATION_TOKEN> --labels unreal,ue-5.8
```

**Wichtig:** Den echten Registrierungs-Token niemals in Git, Logs, Markdown oder Screenshots speichern.

---

## 4. RUNNER-MASCHINE VORBEREITEN

Vor Aktivierung prüfen:

- Unreal Engine 5.8 installiert
- UE-Editor-Binary vorhanden
- UE-Build-Skript vorhanden
- C++-Toolchain installiert
- Python verfügbar
- Git verfügbar
- ausreichend freier Speicher
- Repository-Arbeitsordner beschreibbar
- Runner kann GitHub erreichen

### Empfohlene Umgebungsvariable

Wenn UE nicht an einem automatisch erkannten Standardpfad liegt:

```text
UE58_ROOT=/pfad/zur/UE_5.8
```

Alternativ:

```text
UE58_EDITOR_CMD=/voller/pfad/zu/UnrealEditor
```

---

## 5. AUTOMATISCHE READINESS-PRÜFUNG

Der Runtime-Workflow führt vor dem eigentlichen UE-Test aus:

```bash
python3 Scripts/runner_readiness.py
```

Geprüft werden unter anderem:

- Projektdatei
- Editor-Target
- erkannter UE-5.8-Pfad
- UnrealEditor
- Build-Skript
- echte Engine-Version aus `Engine/Build/Build.version`
- `MajorVersion=5` und `MinorVersion=8`
- Python
- Schreibrechte
- mindestens 5 GB freier Speicher
- sauberer Git-Arbeitsstand vor Runtime

Ausgabe:

```text
Diagnostics/Runtime/runner_readiness.json
```

Die Evidence verwendet Schema v2 und enthält einen UTC-Zeitstempel. Für die Freigabe der Runner-Variable akzeptiert der Admin-Assistent nur eine **frische PASS-Evidence**, die höchstens 30 Minuten alt ist.

> `RUNNER_READINESS: PASS` bedeutet nur: **Maschine bereit.** Es bedeutet ausdrücklich nicht `CP1 PASS`.

---

## 6. RUNNER IN GITHUB PRÜFEN

GitHub:

`Settings → Actions → Runners`

Der Runner soll anzeigen:

```text
Status: Idle
Labels: self-hosted, ..., unreal, ue-5.8
```

Mögliche Zustände:

- `Idle` = verbunden und bereit
- `Active` = arbeitet
- `Offline` = nicht verbunden / Runner-Dienst läuft nicht / Netzwerkproblem

---

## 7. ERST JETZT RUNTIME AKTIVIEREN

Repository-Variable setzen:

`Settings → Secrets and variables → Actions → Variables`

Name:

```text
UE58_RUNNER_ENABLED
```

Wert:

```text
true
```

Bevorzugt nicht manuell setzen, sondern nach frischem Readiness-PASS über:

```bash
python3 Scripts/github_p0_admin.py --apply --enable-runner-variable
```

Das Skript validiert unmittelbar vorher die lokale Readiness-Evidence. Fehlende, alte, falsche oder nicht exakt zu UE 5.8 gehörende Evidence blockiert die Freigabe.

---

## 8. ERSTER ECHTER CP1-LAUF

Workflow:

`Actions → CP1 UE 5.8 Runtime → Run workflow`

Erwartete Reihenfolge:

```text
Checkout
→ Runner Readiness
→ Repository Preflight
→ UE 5.8 Build
→ Character Spawn
→ Movement
→ Telemetrie
→ CP1 Gate
→ Artifact Upload
```

### Artifact prüfen

Mindestens:

- Readiness-Report
- Runtime-Evidence
- CP1-Telemetrie, falls erzeugt

---

## 9. SICHERHEIT BEI ÖFFENTLICHEM REPOSITORY

Self-hosted Runner sind bei öffentlichen Repositories besonders sensibel, weil fremde Pull Requests potenziell Code einschleusen können.

Der vorhandene Workflow verhindert deshalb den automatischen Runtime-Lauf für Fork-PRs.

Zusätzlich:

- keine persönlichen Dateien im Runner-Workspace
- keine unnötigen Secrets auf der Maschine
- minimale GitHub-Token-Rechte
- Runner möglichst dediziert für dieses Projekt
- Workspace regelmäßig bereinigen
- keine dauerhaften Zugangstoken in Scripts

---

## 10. ABNAHME-CHECKLISTE

- [ ] `repository-quality` ist grün
- [ ] `static-and-contract` ist grün
- [ ] `python3 Scripts/p0_preflight.py` zeigt den erwarteten ersten Engpass
- [ ] `main` Ruleset aktiv
- [ ] Pull Request erforderlich
- [ ] Force-Push gesperrt
- [ ] Löschen von `main` gesperrt
- [ ] beide Required Checks eingetragen
- [ ] Self-hosted Runner registriert
- [ ] Labels `unreal` und `ue-5.8` vorhanden
- [ ] Runner Status `Idle`
- [ ] `python3 Scripts/p0_preflight.py --full` auf UE-Maschine ausgeführt
- [ ] `runner_readiness.py` PASS
- [ ] Readiness-Evidence höchstens 30 Minuten alt
- [ ] `UE58_RUNNER_ENABLED=true` erst nach Evidence-Gate
- [ ] erster CP1-Lauf ausgeführt
- [ ] Runtime-Evidence geprüft

---

## 11. SICHERER ADMIN-ASSISTENT

Damit die Branch-Protection nicht ausschließlich per Hand konfiguriert werden muss, gibt es zwei Hilfsskripte.

### Nur Vorschau

```bash
python3 Scripts/github_p0_admin.py
```

Das Skript zeigt die geplante Konfiguration und ändert **nichts**.

### Branch-Schutz anwenden

```bash
python3 Scripts/github_p0_admin.py --apply
```

Voraussetzungen:

- GitHub CLI `gh` installiert
- `gh auth login` abgeschlossen
- verwendetes Konto besitzt Repository-Adminrechte

Nach dem Schreiben liest das Skript die GitHub-Konfiguration erneut. Zielausgabe:

```text
GITHUB_P0_BRANCH_GATE: PASS
```

### Jederzeit read-only prüfen

```bash
python3 Scripts/github_p0_status.py
```

Dieser Prüfer verändert nichts und kontrolliert:

- Branch-Protection auf `main`
- Required Check `static-and-contract`
- Required Check `repository-quality`
- Status von `UE58_RUNNER_ENABLED`
- passende Self-hosted Runner mit Labels `self-hosted`, `unreal`, `ue-5.8`

---

## Referenzen

- GitHub Protected Branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub Self-hosted Runner hinzufügen: https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners
- GitHub Runner Labels: https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/apply-labels
- GitHub Runner Monitoring: https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/monitor-and-troubleshoot
