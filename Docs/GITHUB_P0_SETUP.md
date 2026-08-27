# BUNKER BEATS — GITHUB P0 SETUP

> Ziel: `main` absichern, den Schutz **unabhängig beweisbar** machen und danach den UE-5.8-Self-hosted-Runner kontrolliert aktivieren.

---

## 1. EMPFOHLENE REIHENFOLGE

```text
Hosted Quality grün
   ↓
Admin-Doctor PASS
   ↓
aktives Repository Ruleset für main
   ↓
öffentlicher Ruleset-Live-Beweis PASS
   ↓
GitHub-Infrastruktur-Evidence PASS
   ↓
Self-hosted UE-5.8 Runner
   ↓
Runner Readiness Schema v3 PASS
   ↓
gleicher Checkout + gleiche Maschine + sauberer Worktree erneut bestätigt
   ↓
UE58_RUNNER_ENABLED=true
   ↓
echter CP1 Runtime-Lauf
```

### Ein-Befehl-Einstieg

```bash
python3 Scripts/p0_preflight.py
```

Auf der echten UE-5.8-Maschine:

```bash
python3 Scripts/p0_preflight.py --full
```

Der Preflight ist read-only. Sein GitHub-Schutzschritt verwendet `github_p0_public_verify.py` und liest das öffentliche Ruleset **ohne GitHub-Login oder Token** direkt von GitHub.

`P0_PREFLIGHT: PASS` ist niemals ein CP1-Runtime-PASS.

---

## 2. WARUM RULESET STATT NUR KLASSISCHER BRANCH PROTECTION?

Die klassische Branch-Protection bleibt unterstützt. Ihr Detail-Endpunkt kann für bestimmte GitHub-Apps oder Token jedoch mit 403 gesperrt sein. Dadurch kann eine zweite Stelle den vollständigen Schutz nicht immer unabhängig nachprüfen.

Repository Rulesets haben hier einen wichtigen Vorteil: GitHub erlaubt ihre Ansicht bereits mit Repository-Lesezugriff. Deshalb wird der P0-Schutz bevorzugt als Ruleset angelegt.

```text
privilegierter Schreibweg
→ GitHub speichert Ruleset

unabhängiger Lesepfad
→ Ruleset-Liste lesen
→ Ruleset-Detail lesen
→ denselben P0-Contract prüfen
```

Testdateien dürfen den Validator testen. Sie können aber keinen Live-Server-PASS erzeugen.

---

## 3. P0-RULESET-SOLL

Name:

```text
BUNKER BEATS P0 main gate
```

Ziel:

```text
refs/heads/main
```

Enforcement:

```text
active
```

Verbindliche Regeln:

- Pull Request vor Integration
- keine fremde Approval-Pflicht im Solo-Repository (`required_approving_review_count=0`)
- alte Reviews bei neuen Änderungen verwerfen
- offene Review-Diskussionen müssen gelöst sein
- `static-and-contract` required
- `repository-quality` required
- Branch vor Merge aktuell halten
- Force-Push sperren (`non_fast_forward`)
- Löschen von `main` sperren (`deletion`)
- keine Bypass-Akteure

`cp1-runtime` bleibt noch **nicht** global required, solange der echte UE-5.8-Runner nicht dauerhaft stabil verfügbar ist.

Der vollständige Sollvertrag liegt zentral in:

```text
Scripts/github_p0_ruleset.py
```

Admin-Tool, Status-Tool, öffentlicher Verifier und Regressionstests benutzen denselben Contract.

---

## 4. SICHERER ADMIN-ABLAUF

### Schritt 1 — nur diagnostizieren

```bash
python3 Scripts/github_p0_admin.py --doctor
```

Ziel:

```text
GITHUB_ADMIN_PREFLIGHT: PASS
```

Geprüft werden unter anderem:

- `gh` vorhanden
- `gh` angemeldet
- Repository exakt `provoware/bunkergame`
- Repository nicht archiviert
- `permissions.admin == true`
- `main` vorhanden
- Ruleset-Lesepfad erreichbar
- keine doppelten gleichnamigen P0-Rulesets

### Schritt 2 — empfohlenes Ruleset anwenden

```bash
python3 Scripts/github_p0_admin.py --apply-ruleset
```

Das ist ein sicheres Upsert:

```text
0 Rulesets mit Sollname → neu anlegen
1 Ruleset mit Sollname  → aktualisieren
>1 Rulesets             → BLOCKED, keine automatische Änderung
```

Nach dem Schreiben liest das Tool das Ruleset erneut von GitHub und validiert es mit demselben Contract.

Ziel:

```text
GITHUB_P0_RULESET_GATE: PASS
```

### Klassische Alternative

Nur falls Rulesets bewusst nicht verwendet werden sollen:

```bash
python3 Scripts/github_p0_admin.py --apply
```

Das setzt weiterhin die klassische Branch Protection.

---

## 5. UNABHÄNGIGER LIVE-BEWEIS — OHNE TOKEN

Auf **jedem** Rechner mit Python und Internetzugang:

```bash
python3 Scripts/github_p0_public_verify.py
```

Das Skript verwendet nur Python-Standardbibliothek und öffentliche GitHub-REST-Endpunkte.

Ziel:

```text
GITHUB_P0_PUBLIC_RULESET: PASS
```

PASS entsteht nur, wenn GitHub live ein Ruleset zurückliefert, das exakt den P0-Vertrag erfüllt.

Folgende Zustände bleiben INCOMPLETE:

- Ruleset fehlt
- Ruleset heißt falsch
- mehrere gleichnamige Rulesets
- `enforcement=evaluate`
- falscher Branchbereich
- Bypass-Akteur vorhanden
- Required Check fehlt oder zusätzlicher unerwarteter Check vorhanden
- Strictness aus
- Pull-Request-Regel unvollständig
- Force-Push-Sperre fehlt
- Delete-Sperre fehlt
- unerwartete Zusatzregel vorhanden

Damit kann eine lokale Testfixture keinen Live-PASS vortäuschen.

### Maschinenlesbares Infrastruktur-Bundle

Für archivierte Evidence zusätzlich:

```bash
python3 Scripts/github_p0_evidence.py
python3 Scripts/github_p0_evidence_validate.py
```

Der zweite Befehl akzeptiert den gespeicherten PASS niemals allein, sondern liest GitHub erneut und verlangt denselben aktuellen `main`-SHA sowie denselben vollständigen Ruleset-Vertrag.

Detailanleitung:

```text
Docs/P0_INFRASTRUCTURE_EVIDENCE.md
```

---

## 6. AUTOMATISCHER EXTERNER INFRASTRUKTUR-OBSERVER

Workflow:

```text
.github/workflows/p0-infrastructure-observer.yml
```

Er läuft:

- täglich geplant
- manuell über `workflow_dispatch`
- auf einem GitHub-hosted Runner
- ohne Self-hosted Runner
- ohne Admin-Secret
- ohne GitHub-CLI-Anmeldung

Jobname:

```text
p0-infrastructure-evidence
```

Der Observer sammelt ein JSON-Bundle, revalidiert es live und lädt es auch bei FAIL als Artifact hoch. Erst danach wird der Jobstatus erzwungen.

Bis das echte Ruleset aktiv ist, darf dieser Observer rot sein. Das ist kein Fehler der Testlogik, sondern wahrheitsgemäße Infrastruktur-Evidence.

Nach erfolgreichem Ruleset-Apply wird der Observer zum zweiten, externen PASS-Beweis.

---

## 7. ERWEITERTER AUTHENTIFIZIERTER STATUS

```bash
python3 Scripts/github_p0_status.py
```

Dieser read-only Prüfer arbeitet Ruleset-first und fällt bei Bedarf auf klassische Branch Protection zurück.

Zusätzlich versucht er zu lesen:

- `UE58_RUNNER_ENABLED`
- Self-hosted Runner mit `self-hosted`, `unreal`, `ue-5.8`

Mögliche Evidence-Pfade:

```text
GITHUB_P0_EVIDENCE_PATH: RULESET
GITHUB_P0_EVIDENCE_PATH: CLASSIC_PROTECTION
GITHUB_P0_EVIDENCE_PATH: NONE
```

Bevorzugtes Ziel:

```text
GITHUB_P0_EVIDENCE_PATH: RULESET
GITHUB_P0_BRANCH_GATE: PASS
```

---

## 8. SELF-HOSTED UE-5.8 RUNNER

GitHub:

`Repository → Settings → Actions → Runners → New self-hosted runner`

GitHubs aktuell erzeugte Setup-Befehle verwenden. Keine feste Runner-Version in die Projektdokumentation übernehmen.

Zusätzliche Labels:

```text
unreal
ue-5.8
```

GitHub setzt `self-hosted` automatisch.

Registrierungstoken niemals in Git, Issues, Markdown, Screenshots oder Logs speichern.

---

## 9. RUNNER-READINESS — SCHEMA v3

Auf der echten UE-Maschine und im **sauberen Projektcheckout**:

```bash
python3 Scripts/p0_preflight.py --full
```

Die Readiness prüft unter anderem:

- Projektdatei
- Editor-Target
- UE-Pfad
- UnrealEditor
- Build-Skript
- echte Version aus `Engine/Build/Build.version`
- exakt UE 5.8
- Python
- Schreibrechte
- mindestens 5 GB frei
- sauberer Git-Arbeitsstand
- Git-Remote gehört exakt zu `provoware/bunkergame`
- vollständiger aktueller Git-HEAD ist bestimmbar
- pseudonymer Maschinenfingerprint ist bestimmbar

Evidence:

```text
Diagnostics/Runtime/runner_readiness.json
```

Schema v3 bindet die Evidence an:

```text
repository
+ git_head_sha
+ machine_fingerprint_sha256
+ machine_identity_scheme
+ exakt definierter vollständiger Check-Satz
```

Der Maschinenfingerprint ist ein SHA-256 aus Hostname, Betriebssystem und Architektur. Er ist **keine Hardware-Attestation** und speichert keine Hardware-Seriennummer. Sein Zweck ist Kontextbindung und Vermeidung einfacher Evidence-Verwechslung zwischen Maschinen.

Der Pflichtcheck-Satz wird zentral in `Scripts/runner_readiness_contract.py` definiert. Fehlende oder zusätzliche Checks blockieren die Freigabe.

Nur frische PASS-Evidence, maximal 30 Minuten alt, darf die Runner-Freigabe ermöglichen.

`RUNNER_READINESS: PASS` beweist nur Maschinenbereitschaft. Es ist ausdrücklich noch kein UE-Build-/CP1-PASS.

---

## 10. RUNNER-VARIABLE FREIGEBEN — KONTEXT ERNEUT PRÜFEN

Bevorzugt auf **derselben UE-Maschine, demselben Checkout und direkt nach frischer Readiness**:

```bash
python3 Scripts/github_p0_admin.py --apply-ruleset --enable-runner-variable
```

Das Ruleset wird idempotent erneut geprüft/aktualisiert. Danach wird die lokale Readiness-Evidence nicht nur gelesen, sondern gegen den **jetzt aktuellen Kontext** geprüft:

```text
Repository jetzt
→ muss weiterhin provoware/bunkergame sein

Git-HEAD jetzt
→ muss exakt Evidence-HEAD sein

Maschinenfingerprint jetzt
→ muss exakt Evidence-Fingerprint sein

Worktree jetzt
→ muss erneut sauber sein

Evidence
→ Schema v3
→ vollständiger Check-Satz
→ UE exakt 5.8
→ maximal 30 Minuten alt
```

Erst danach wird gesetzt:

```text
UE58_RUNNER_ENABLED=true
```

Damit blockieren auch uncommittete Änderungen nach dem Readiness-Lauf die Freigabe, obwohl sich der Git-HEAD dabei nicht geändert hätte.

---

## 11. ERSTER ECHTER CP1-LAUF

Workflow:

```text
CP1 UE 5.8 Runtime
```

Beweiskette:

```text
Runner Readiness v3
→ Repository Preflight
→ UE 5.8 Build
→ Character Spawn
→ Movement
→ Telemetrie
→ CP1 Gate
→ Runtime Artifact
```

Erst dieser Lauf darf CP1 GREEN machen.

---

## 12. ABNAHME-CHECKLISTE

- [ ] `static-and-contract` PASS
- [ ] `repository-quality` PASS
- [ ] `GITHUB_ADMIN_PREFLIGHT: PASS`
- [ ] genau ein P0-Ruleset mit Sollname vorhanden
- [ ] Ruleset `active`
- [ ] nur `main` erfasst
- [ ] keine Bypass-Akteure
- [ ] Pull Request erforderlich
- [ ] Review-Diskussionen müssen gelöst sein
- [ ] `static-and-contract` required
- [ ] `repository-quality` required
- [ ] Branch vor Merge aktuell
- [ ] Force-Push gesperrt
- [ ] Löschen von `main` gesperrt
- [ ] `GITHUB_P0_PUBLIC_RULESET: PASS`
- [ ] `GITHUB_P0_EVIDENCE: PASS`
- [ ] Hosted `P0 Infrastructure Observer` PASS
- [ ] Self-hosted Runner registriert
- [ ] Labels `unreal`, `ue-5.8` vorhanden
- [ ] Runner online/idle
- [ ] Readiness-Schema v3 erzeugt
- [ ] Repository-Bindung korrekt
- [ ] Git-HEAD-Bindung korrekt
- [ ] Maschinenfingerprint vorhanden
- [ ] exakt vollständiger Pflichtcheck-Satz PASS
- [ ] `RUNNER_READINESS: PASS`
- [ ] Readiness-Evidence höchstens 30 Minuten alt
- [ ] Worktree unmittelbar vor Enable erneut sauber
- [ ] `UE58_RUNNER_ENABLED=true` erst danach
- [ ] echter CP1-Lauf ausgeführt
- [ ] Runtime-Evidence geprüft

---

## Referenzen

- GitHub Repository Rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- GitHub REST Rulesets: https://docs.github.com/en/rest/repos/rules
- GitHub Protected Branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub Self-hosted Runner: https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners
