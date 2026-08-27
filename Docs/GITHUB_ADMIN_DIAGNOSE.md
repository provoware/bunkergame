# GITHUB-ADMIN-DIAGNOSE — P0 RULESET / BRANCH-SCHUTZ

> Zweck: herausfinden, warum `main` noch nicht geschützt ist, den Schutz sicher anwenden und ihn danach **ohne Admin-Token unabhängig beweisen**.

## 1. SICHERER ERSTER BEFEHL

```bash
python3 Scripts/github_p0_admin.py --doctor
```

Dieser Modus ist read-only. Er verändert weder Rulesets, Branch Protection noch Repository-Variablen.

Ziel:

```text
GITHUB_ADMIN_PREFLIGHT: PASS
```

Erst danach darf geschrieben werden.

---

## 2. WAS PRÜFT DER DOCTOR?

In Reihenfolge:

1. GitHub CLI `gh` vorhanden
2. GitHub-Anmeldung aktiv
3. Repository exakt `provoware/bunkergame`
4. Repository nicht archiviert
5. Konto besitzt `permissions.admin == true`
6. Branch `main` existiert
7. aktueller `main.protected`-Hinweis
8. Ruleset-Liste ist lesbar
9. höchstens ein Ruleset mit P0-Sollname vorhanden

Push- oder Maintain-Recht allein reicht nicht als Adminrecht.

---

## 3. EMPFOHLENER APPLY-WEG

Nach Doctor-PASS:

```bash
python3 Scripts/github_p0_admin.py --apply-ruleset
```

Warum Ruleset?

- Schutz lässt sich mit Adminrecht schreiben.
- Vollständiges Ruleset kann danach bereits mit Repository-Lesezugriff gelesen werden.
- Dadurch ist die Nachprüfung nicht an denselben privilegierten Token gebunden.

Das Tool führt ein sicheres Upsert aus:

```text
kein Soll-Ruleset → Create
exactly one      → Update
mehrere          → BLOCKED
```

Ziel:

```text
GITHUB_P0_RULESET_GATE: PASS
```

Klassische Branch Protection bleibt als Fallback verfügbar:

```bash
python3 Scripts/github_p0_admin.py --apply
```

---

## 4. TOKENFREIER LIVE-BEWEIS

Nach `--apply-ruleset` auf irgendeinem Rechner mit Python:

```bash
python3 Scripts/github_p0_public_verify.py
```

Dieser Prüfer:

- braucht kein `gh`
- braucht keine Anmeldung
- braucht keinen Token
- verändert nichts
- liest GitHub direkt über die öffentliche REST-API
- nutzt denselben zentralen Contract wie das Admin-Tool

Ziel:

```text
GITHUB_P0_PUBLIC_RULESET: PASS
```

PASS bedeutet ausschließlich: Das aktive GitHub-Ruleset erfüllt live den P0-Schutzvertrag.

Es beweist **nicht** UE-Readiness und **nicht** CP1 Runtime.

---

## 5. AUTOMATISCHER ZWEITER BEWEIS

GitHub Workflow:

```text
P0 Infrastructure Observer
```

Datei:

```text
.github/workflows/p0-infrastructure-observer.yml
```

Er läuft täglich und manuell auf einem GitHub-hosted Runner und verwendet ebenfalls den tokenfreien Live-Verifier.

Damit existieren nach dem Ruleset-Apply zwei getrennte Nachweise:

```text
lokaler/UE-Rechner → github_p0_public_verify.py
GitHub-hosted      → p0-infrastructure-evidence
```

Beide lesen den echten Serverzustand. Keine Testfixture kann diesen PASS ersetzen.

---

## 6. FEHLERCODES DES ADMIN-TOOLS

### `AUTHORIZATION_403`

GitHub verweigert die Administrationsaktion.

Typische Ursachen:

- falsches GitHub-Konto
- Konto ohne Repository-Adminrecht
- Fine-grained Token ohne `Repository Administration: Read and write`
- GitHub-App ohne nötige Administration-Schreibberechtigung

Prüfen:

```bash
gh auth status
gh repo view provoware/bunkergame
python3 Scripts/github_p0_admin.py --doctor
```

### `RESOURCE_404`

Repository, Branch oder Ruleset-/Protection-Ressource ist nicht sichtbar bzw. wurde nicht gefunden.

```bash
gh repo view provoware/bunkergame
gh api repos/provoware/bunkergame/branches/main
gh api repos/provoware/bunkergame/rulesets
```

### `VALIDATION_422`

GitHub lehnt die Konfiguration ab. Schutzregeln nicht blind abschwächen. Den unveränderten GitHub-Fehlertext prüfen.

### `UNKNOWN_GITHUB_ERROR`

Keine sichere Zuordnung möglich. Nicht raten; Originalmeldung verwenden.

---

## 7. WAS DER RULESET-CONTRACT ABSICHTLICH BLOCKIERT

Der Validator ist fail-closed. Unter anderem führen zu FAIL:

- `enforcement=evaluate`
- anderer Zielbranch oder zusätzlicher Branchbereich
- Branch-Ausnahmen
- Bypass-Akteure
- doppelte Rule-Typen
- unerwartete Zusatzregeln
- fehlende Pull-Request-Regel
- fremde Approval-Pflicht im Solo-Repository
- fehlende Review-Thread-Auflösung
- fehlender oder zusätzlicher Required Check
- Strictness aus
- Delete-Sperre fehlt
- Force-Push-Sperre fehlt

Der kanonische Sollvertrag liegt in:

```text
Scripts/github_p0_ruleset.py
```

---

## 8. ERWEITERTER AUTHENTIFIZIERTER STATUS

```bash
python3 Scripts/github_p0_status.py
```

Dieser Prüfer arbeitet:

```text
Ruleset zuerst
→ falls kein PASS: klassische Branch Protection als Fallback
→ zusätzlich Runner-Variable und Runner-Liste
```

Bevorzugtes Ergebnis:

```text
GITHUB_P0_EVIDENCE_PATH: RULESET
GITHUB_P0_BRANCH_GATE: PASS
```

---

## 9. ERST NACH GITHUB-PASS ZUR UE-MASCHINE

```bash
python3 Scripts/p0_preflight.py --full
```

Auf `main` wird der GitHub-Schutz im Preflight tokenfrei über das öffentliche Ruleset bewiesen.

`P0_PREFLIGHT: PASS` und `RUNNER_READINESS: PASS` bleiben Vorbedingungen, kein Runtime-Beweis.

Der echte CP1-Beweis bleibt:

```text
UE 5.8 Build
→ Character Spawn
→ Movement
→ Telemetrie
→ CP1 Gate
```
