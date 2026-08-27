# P0 INFRASTRUCTURE EVIDENCE — LIVE-BEWEIS UND DRIFT-ERKENNUNG

> Zweck: GitHub-Schutz nicht nur als Terminalmeldung prüfen, sondern als nachvollziehbares JSON-Bundle archivieren und später **erneut gegen GitHub live** validieren.

---

## 1. KURZFASSUNG FÜR LAIEN

Es gibt zwei Schritte:

```text
1. Beweis aufnehmen
2. Beweis erneut gegen GitHub prüfen
```

Befehle:

```bash
python3 Scripts/github_p0_evidence.py
python3 Scripts/github_p0_evidence_validate.py
```

Ein echter Erfolg sieht so aus:

```text
GITHUB_P0_EVIDENCE_COLLECT: PASS
GITHUB_P0_EVIDENCE: PASS
```

**Wichtig:** Solange das echte P0-Ruleset auf GitHub fehlt, müssen diese Prüfungen FAIL/INCOMPLETE bleiben. Das ist korrekt und kein Programmfehler.

---

## 2. WAS WIRD BEWIESEN?

Das Bundle bezieht sich ausschließlich auf die GitHub-P0-Infrastruktur:

- Repository `provoware/bunkergame`
- Branch `main`
- aktuell beobachteter `main`-Commit-SHA
- P0-Ruleset `BUNKER BEATS P0 main gate`
- Ruleset-ID
- `enforcement=active`
- Pull-Request-Regel
- Required Check `static-and-contract`
- Required Check `repository-quality`
- Branch vor Merge aktuell
- Force-Push gesperrt
- Löschen von `main` gesperrt
- keine Bypass-Akteure

Es beweist **nicht**:

- Unreal Engine 5.8 verfügbar
- Runner bereit
- UE-Build erfolgreich
- Character Spawn
- Movement
- CP1 Runtime PASS

---

## 3. EVIDENCE AUFNEHMEN

Standard:

```bash
python3 Scripts/github_p0_evidence.py
```

Ausgabe-Datei:

```text
Diagnostics/Infrastructure/github_p0_evidence.json
```

Alternativer Zielpfad:

```bash
python3 Scripts/github_p0_evidence.py --output /pfad/evidence.json
```

`Diagnostics/` ist ein **generierter Diagnoseordner** und gehört nicht in Git.

Auch bei fehlendem oder falschem Ruleset versucht der Collector ein FAIL-Bundle zu schreiben. Dadurch bleibt die Fehlerursache erhalten.

---

## 4. WAS STEHT IM JSON-BUNDLE?

Wesentliche Felder:

```text
schema_version
kind
observed_at_utc
live_observed
synthetic
source
github_api_version
repository
branch
main_sha
ruleset_id
ruleset_name
ruleset_enforcement
contract_status
status
failures
sources
integrity_sha256
```

### `main_sha`

Bindet den Beweis an den konkret beobachteten Stand von `main`.

Wenn später ein neuer Commit auf `main` liegt, ist die alte Evidence absichtlich nicht mehr aktuell.

### `ruleset_id`

Bindet den Beweis an genau das beobachtete GitHub-Ruleset.

### `failures`

Enthält konkrete Gründe, wenn der Zustand nicht dem P0-Vertrag entspricht.

### `integrity_sha256`

Erkennt, ob das gespeicherte Bundle nach dem Erzeugen verändert wurde.

**Das ist keine GitHub-Signatur.** Ein SHA-256-Wert beweist nicht, dass GitHub die Datei signiert hat. Die Authentizität entsteht erst durch die erneute Live-Prüfung im nächsten Schritt.

---

## 5. EVIDENCE VALIDIEREN

Standard:

```bash
python3 Scripts/github_p0_evidence_validate.py
```

Andere Datei:

```bash
python3 Scripts/github_p0_evidence_validate.py --evidence /pfad/evidence.json
```

Der Validator prüft in zwei Ebenen.

### Ebene A — gespeicherter Datensatz

- richtiges Schema
- richtiger Evidence-Typ
- `live_observed=true`
- `synthetic=false`
- richtiges Repository
- Branch `main`
- gültiger 40-stelliger SHA
- gültige Ruleset-ID
- `enforcement=active`
- gespeicherter Contract-PASS
- keine gespeicherten Fehler
- korrekte GitHub-Quellendpunkte
- Evidence nicht älter als 36 Stunden
- Zeitstempel nicht unplausibel in der Zukunft
- SHA-256 stimmt noch

### Ebene B — neue Live-Abfrage

Danach liest der Validator GitHub **noch einmal neu**:

```text
aktueller main SHA
→ muss Evidence-SHA entsprechen

aktuelles P0-Ruleset
→ muss dieselbe Ruleset-ID besitzen

aktuelles Ruleset-Detail
→ muss den vollständigen P0-Vertrag weiterhin erfüllen
```

Nur danach:

```text
GITHUB_P0_EVIDENCE: PASS
```

---

## 6. STATUSBEDEUTUNG

### 🟢 `GITHUB_P0_EVIDENCE: PASS`

Gespeicherter Beweis ist frisch und unverändert **und** GitHub bestätigt denselben Zustand gerade erneut live.

### 🔴 `GITHUB_P0_EVIDENCE: FAIL`

Die gespeicherte Evidence selbst ist nicht gültig, zum Beispiel:

- falsches Schema
- falsches Repository
- zu alt
- Hash stimmt nicht mehr
- gespeicherter Zustand war bereits FAIL

### 🟡/🔴 `GITHUB_P0_EVIDENCE: DRIFT`

Die Datei war strukturell gültig, aber GitHub sieht inzwischen anders aus.

Typische Fälle:

- neuer `main`-Commit
- Ruleset ersetzt
- Ruleset deaktiviert
- Required Check entfernt
- Force-Push-Sperre entfernt
- Bypass hinzugefügt

Bei einem neuen legitimen `main`-Commit reicht normalerweise:

```bash
python3 Scripts/github_p0_evidence.py
python3 Scripts/github_p0_evidence_validate.py
```

Bei Ruleset-Drift zuerst die Ursache prüfen und nicht automatisch Schutzregeln abschwächen.

---

## 7. AUTOMATISCHER GITHUB-OBSERVER

Workflow:

```text
P0 Infrastructure Observer
```

Datei:

```text
.github/workflows/p0-infrastructure-observer.yml
```

Ablauf:

```text
Checkout
→ Python
→ Live-Evidence sammeln
→ Evidence erneut live validieren
→ JSON als Artifact hochladen
→ erst danach PASS/FAIL des Jobs erzwingen
```

Das Artifact heißt:

```text
p0-infrastructure-evidence
```

Aufbewahrung:

```text
14 Tage
```

Der Upload wird auch bei FAIL versucht. Dadurch bleibt die Diagnose erhalten.

---

## 8. WARUM ZWEI LIVE-ABFRAGEN?

Collector und Validator haben unterschiedliche Aufgaben:

```text
Collector
= Was habe ich beobachtet?

Validator
= Ist dieser gespeicherte Beweis noch gültig und sieht GitHub jetzt noch genauso aus?
```

Damit kann ein alter PASS nicht einfach als aktueller Zustand weiterverwendet werden.

---

## 9. REGRESSIONSTESTS

Separate Testdatei:

```text
Scripts/tests/test_p0_evidence_bundle.py
```

Geprüft werden unter anderem:

- vollständiger Live-Vertrag → PASS-Bundle
- fehlendes Ruleset → FAIL-Bundle
- frisches versiegeltes Bundle → strukturell gültig
- nachträgliche Änderung → Hash-FAIL
- Evidence älter als 36 Stunden → FAIL
- falsches Repository → FAIL, selbst nach neu berechnetem Hash
- anderer Live-`main`-SHA → DRIFT
- andere Ruleset-ID → DRIFT
- `enforcement=evaluate` oder anderer Contract-Drift → DRIFT
- kritische Evidence-Dateien fehlen → Regression FAIL

Diese Tests verwenden kontrollierte Testdaten und beweisen nur die Logik. Sie erzeugen keinen realen Infrastruktur-PASS.

---

## 10. EMPFOHLENER P0-ABLAUF

Nach realem Ruleset-Apply:

```bash
python3 Scripts/github_p0_admin.py --doctor
python3 Scripts/github_p0_admin.py --apply-ruleset
python3 Scripts/github_p0_public_verify.py
python3 Scripts/github_p0_evidence.py
python3 Scripts/github_p0_evidence_validate.py
```

Erwartete Kette:

```text
GITHUB_ADMIN_PREFLIGHT: PASS
GITHUB_P0_RULESET_GATE: PASS
GITHUB_P0_PUBLIC_RULESET: PASS
GITHUB_P0_EVIDENCE_COLLECT: PASS
GITHUB_P0_EVIDENCE: PASS
```

Danach erst auf der echten UE-5.8-Maschine:

```bash
python3 Scripts/p0_preflight.py --full
```

Und erst ein echter UE-Lauf darf später CP1 GREEN machen.
