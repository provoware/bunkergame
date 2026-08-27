# CODEQUALITÄT — APPEND-ONLY QUALITÄTSJOURNAL

> Diese Datei ist ein **append-only Entwicklungsgedächtnis**. Pro Iteration wird genau ein neuer Verbesserungsvorschlag unten angehängt. Bestehende Einträge werden nicht gelöscht, umgeschrieben oder nachträglich „schöner“ gemacht. Wenn eine frühere Idee überholt ist, bekommt sie in einer späteren Iteration einen neuen Gegeneintrag.

---

## CQ-2026-08-27-001 — Autonomer Repository Quality Guard

**Iteration:** Dokumentations-/GitHub-Control-Plane 2  
**Kategorie:** Testautomatisierung / Wartbarkeit / Fehlerprävention  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT  
**Aufwand:** 3/10  
**Risiko:** 1/10

### Verbesserungsvorschlag

Einen vollständig autonomen, UE-unabhängigen `Quality Guard` einführen, der bei Pull Requests, Pushes und regelmäßig geplant ausgeführt wird und zentrale Repository-Invarianten prüft.

### Grund

`Scripts/ci_verify.py` prüft CP1- und Projektverträge sehr gut, deckt aber allgemeine Repository-Qualität wie kaputte lokale Dokumentlinks, Merge-Konfliktmarker, fehlende Kerndokumente oder ungültige JSON-Dateien nicht als eigene, leicht erweiterbare Schicht ab.

### Wirkung

- Dokumentationsfehler werden vor dem Merge sichtbar.
- ungültige JSON-Konfigurationen werden automatisch blockiert.
- Python-Syntaxfehler werden unabhängig vom fachlichen Testpfad erkannt.
- versehentlich eingecheckte generierte Ordner werden erkannt.
- Qualitätsregeln können zentral erweitert werden, ohne Gameplay-Gates aufzublähen.

### Technischer Effekt

Die CI wird von einem einzelnen fachlichen Gate zu einem **mehrschichtigen Kontrollsystem**:

```text
Validate
   ↓
Quality Guard
   ↓
Iteration Guard
   ↓
UE Runtime Gate, falls erforderlich
```

Dadurch lassen sich Fehlerklassen klarer zuordnen und Reparaturen bleiben kleiner.

### Zusatzeffekt

Der zugehörige `Iteration Guard` prüft zusätzlich, dass bei jeder PR-Iteration:

- `WICHTIG.md` aktualisiert wird,
- `CODEQUALITÄT.md` erweitert wird,
- historische CODEQUALITÄT-Einträge nur angehängt und nicht still überschrieben werden.

### Erwarteter Nutzen

**Robustheit:** hoch  
**Wartbarkeit:** sehr hoch  
**Entwicklerführung:** sehr hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-002 — Adminänderungen als Dry-Run + Read-back-Verifikation

**Iteration:** GitHub P0 Hardening  
**Kategorie:** GitHub-Administration / Safety by Design / Reproduzierbarkeit  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT, externe Ausführung noch offen  
**Aufwand:** 3/10  
**Risiko:** 2/10

### Verbesserungsvorschlag

Weitreichende GitHub-Adminänderungen nicht als unkontrollierte Einmalbefehle dokumentieren, sondern als sicheren Assistenten mit drei Stufen ausführen:

```text
Dry-Run
→ explizites Apply
→ serverseitiges Read-back
```

Dafür wurden `Scripts/github_p0_admin.py` und `Scripts/github_p0_status.py` eingeführt.

### Grund

Branch-Protection ist sicherheitsrelevant. Ein falsch gesetzter Check-Name kann entweder Schutzwirkung verlieren oder das Repository dauerhaft blockieren. Besonders kritisch wäre es, `cp1-runtime` global als Pflichtprüfung zu setzen, solange der Self-hosted UE-Runner nicht dauerhaft verfügbar ist.

### Wirkung

- Adminänderungen werden vor dem Schreiben sichtbar.
- Schreiboperationen benötigen eine explizite Benutzerentscheidung.
- GitHub wird nach der Änderung erneut abgefragt.
- Required Checks werden auf die tatsächlich stabilen Kontexte begrenzt.
- Branch-Schutz und UE-Runner-Freigabe bleiben getrennte Gates.
- die Konfiguration wird reproduzierbar statt nur als Klickfolge dokumentiert.

### Technischer Effekt

`github_p0_admin.py` setzt erst mit `--apply`:

- PR-Gate für `main`
- `static-and-contract` als Required Check
- `repository-quality` als Required Check
- `strict=true` für aktuellen Branch vor Merge
- Schutz auch für Admins
- Force-Push aus
- Branch-Löschen aus
- offene Review-Diskussionen als Merge-Blocker

Anschließend liest das Skript die Branch-Protection erneut und meldet `GITHUB_P0_BRANCH_GATE: PASS` nur, wenn die zentralen Sollwerte wirklich serverseitig sichtbar sind.

`github_p0_status.py` ist vollständig read-only und prüft zusätzlich, ob ein passender Self-hosted Runner sichtbar ist und ob `UE58_RUNNER_ENABLED` gesetzt wurde.

### Grund für die Trennung der Runner-Variable

`UE58_RUNNER_ENABLED=true` darf erst nach einem echten `RUNNER_READINESS: PASS` aktiviert werden. Dadurch kann eine bloße Runner-Registrierung nicht versehentlich den CP1-Workflow freischalten, bevor UE 5.8, Toolchain, Speicher und Schreibrechte real geprüft wurden.

### Erwarteter Nutzen

**Robustheit:** sehr hoch  
**Fehlkonfigurationsschutz:** sehr hoch  
**Nachvollziehbarkeit:** sehr hoch  
**Rollback-Fähigkeit:** hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-003 — Runner-Aktivierung an frische Evidence koppeln

**Iteration:** P0 Evidence Hardening  
**Kategorie:** Evidence Integrity / Self-hosted Runner / Regression Prevention  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reale Maschinen-Evidence weiterhin offen  
**Aufwand:** 4/10  
**Risiko:** 2/10

### Verbesserungsvorschlag

Sicherheitsrelevante Zustandsübergänge nicht nur dokumentarisch an Vorbedingungen binden, sondern die Vorbedingungen unmittelbar vor dem Übergang maschinell erneut validieren.

Für `UE58_RUNNER_ENABLED=true` bedeutet das:

```text
frische Readiness-Evidence
→ Schema prüfen
→ Evidence-Typ prüfen
→ Status PASS prüfen
→ alle Checks true
→ echte UE-Version exakt 5.8
→ Zeitstempel plausibel und höchstens 30 Minuten alt
→ erst dann Variable setzen
```

### Grund

Ein Warnhinweis wie „erst nach Readiness PASS verwenden“ ist kein technischer Schutz. Ein Nutzer, Agent oder späteres Skript könnte den Schalter trotzdem ausführen. Zusätzlich kann alte Evidence nach einer Maschinenänderung ihre Aussagekraft verlieren.

### Wirkung

- kein Runner-Enable ohne aktuelle maschinelle Evidence
- keine Freigabe bei falsch benanntem UE-Verzeichnis
- UE 5.7/5.9 werden nicht als 5.8 akzeptiert
- stale Evidence verliert automatisch ihre Freigabewirkung
- Zukunftszeitstempel werden als unplausibel erkannt
- Readiness kann keinen Runtime-/CP1-PASS vortäuschen
- die Sicherheitslogik wird in Hosted CI regressionsgetestet

### Technischer Effekt

`runner_readiness.py` erzeugt Schema v2 mit `generated_at_utc` und liest `Engine/Build/Build.version`. `github_p0_admin.py` besitzt einen eigenständigen Evidence-Validator und blockiert die Variable bei fehlender, alter, fehlerhafter oder nicht exakt zu UE 5.8 gehörender Evidence.

`Scripts/tests/test_p0_control_plane.py` prüft unter anderem:

- frische gültige Evidence → akzeptiert
- fehlende Evidence → blockiert
- FAIL → blockiert
- alte Evidence → blockiert
- unplausible Zukunft → blockiert
- falsches Schema → blockiert
- Runtime-Claim in Readiness → blockiert
- falsche Engine-Version → blockiert
- echte `Build.version` 5.8 → akzeptiert
- 5.7 → abgelehnt

Der `Quality Guard` führt diese Tests automatisch aus.

### Erwarteter Nutzen

**Evidence-Integrität:** sehr hoch  
**Fehlbedienungsschutz:** sehr hoch  
**Regressionserkennung:** sehr hoch  
**Self-hosted-Runner-Sicherheit:** hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-004 — Ein-Befehl-P0-Preflight mit Next-Best-Action

**Iteration:** P0 Operator Experience  
**Kategorie:** Bedienbarkeit / Diagnose / Fehlerprävention  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reale Admin-/UE-Ausführung noch offen  
**Aufwand:** 3/10  
**Risiko:** 1/10

### Verbesserungsvorschlag

Mehrere korrekte Einzelprüfungen zu einem read-only Orchestrator zusammenführen, der sie in einer festen Reihenfolge ausführt und bei Fehlern exakt den ersten sinnvollen nächsten Schritt nennt.

### Grund

Bei mehreren Gates kann ein Nutzer zwar jede Prüfung einzeln starten, aber dennoch am falschen Ende debuggen. Beispielsweise ist eine UE-Readiness-Reparatur nutzlos, wenn zuvor bereits der statische Projektvertrag gebrochen ist. Die Control Plane soll deshalb nicht nur prüfen, sondern auch die Reihenfolge der Problemlösung führen.

### Wirkung

- ein einziger Einstiegspunkt vor dem ersten Runtime-Lauf
- weniger Reihenfolgefehler
- weniger Shotgun-Debugging
- klare Unterscheidung zwischen Admin-Rechner und UE-Maschine
- sofort sichtbare Next-Best-Action
- bessere Übergabe an Laien, neue Entwickler und autonome Agenten

### Technischer Effekt

Neu ist `Scripts/p0_preflight.py`:

```text
python3 Scripts/p0_preflight.py
→ ci_verify
→ repo_quality
→ GitHub P0 status
→ Next Best Action

python3 Scripts/p0_preflight.py --full
→ alle obigen Prüfungen
→ UE58 runner_readiness
→ Next Best Action
```

Der Orchestrator verändert keine GitHub-Einstellung. `P0_PREFLIGHT: PASS` ist ausdrücklich kein CP1-Runtime-PASS.

Die Entscheidungslogik ist in `Scripts/tests/test_p0_control_plane.py` abgesichert: statischer Fehler hat Vorrang vor Quality, Quality vor GitHub, GitHub vor UE-Readiness; eine Runner-Freigabe wird nur nach vollständigem PASS empfohlen.

### Erwarteter Nutzen

**Laienfreundlichkeit:** sehr hoch  
**Diagnosegeschwindigkeit:** hoch  
**Fehlbedienungsschutz:** hoch  
**Wartbarkeit:** hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-005 — Branch-Lifecycle-Guard nach abgeschlossenem PR

**Iteration:** Post-Merge Workflow Hardening  
**Kategorie:** Git-Workflow / Prozessintegrität / Regression Prevention  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT  
**Aufwand:** 2/10  
**Risiko:** 1/10

### Verbesserungsvorschlag

Vor allen fachlichen Prüfungen sicherstellen, dass der aktuelle Arbeitsbranch nicht bereits über einen abgeschlossenen Pull Request gemergt wurde und anschließend neue Commits erhalten hat.

### Grund

Ein gemergter PR beendet seinen Review- und CI-Lifecycle. Werden danach auf demselben Feature-Branch weitere Commits erzeugt, gehören diese nicht mehr zum abgeschlossenen PR. Ohne neue Branch-/PR-Grenze kann dadurch der Eindruck entstehen, die Folgearbeit sei weiterhin Teil des bereits geprüften Änderungssatzes.

### Wirkung

- Folgearbeit erhält einen neuen Review-Lifecycle
- gemergte und noch offene Arbeit werden nicht vermischt
- bessere Nachvollziehbarkeit von CI-Evidence
- weniger Risiko für unbemerkte Nacharbeiten außerhalb eines PRs
- klarere Branch-Hygiene für Menschen und Agenten

### Technischer Effekt

`Scripts/branch_lifecycle_guard.py` prüft read-only:

```text
aktueller Feature-Branch
→ gemergte PRs mit demselben Head-Branch?
→ Commits vor origin/main?
→ merged + ahead > 0 = FAIL
```

Der Guard ist die erste Stufe von `Scripts/p0_preflight.py`. Die reine Entscheidungslogik wird in `Scripts/tests/test_p0_control_plane.py` regressionsgetestet.

### Erwarteter Nutzen

**Prozessintegrität:** sehr hoch  
**Review-Nachvollziehbarkeit:** sehr hoch  
**Fehlbedienungsschutz:** hoch  
**CI-Evidence-Zuordnung:** hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-006 — GitHub-Adminfähigkeit vor jeder Schutzänderung beweisen

**Iteration:** P0 Admin Diagnostics  
**Kategorie:** GitHub-Administration / Fehlerdiagnose / Safety by Design  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reale Serveranwendung weiterhin extern  
**Aufwand:** 3/10  
**Risiko:** 1/10

### Verbesserungsvorschlag

Vor einer Branch-Protection-Schreiboperation nicht nur `gh auth status`, sondern die **konkrete Administrationsfähigkeit für das Zielrepository** maschinell beweisen. Fehler der GitHub-API sollen außerdem in unterscheidbare, handlungsorientierte Kategorien übersetzt werden.

### Grund

Eine gültige GitHub-Anmeldung beweist nicht, dass das verwendete Konto bzw. Token `provoware/bunkergame` administrieren darf. Ein Nutzer kann korrekt angemeldet sein und trotzdem nur Push- oder Maintain-Rechte besitzen. Ohne vorgelagerte Fähigkeitsprüfung führt das zu unnötigen Apply-Versuchen und schwer verständlichen API-Fehlern.

### Wirkung

- kein Branch-Protection-Apply ohne bestätigtes Repository-Adminrecht
- 403, 404 und 422 führen zu unterschiedlichen Reparaturpfaden
- falscher Repository- oder Branch-Kontext wird früh erkannt
- Serverstatus `protected=false` kann ohne Detail-API eindeutig erkannt werden
- weniger Fehlversuche und weniger manuelle Interpretation von GitHub-Ausgaben

### Technischer Effekt

`github_p0_admin.py` besitzt jetzt `--doctor` und prüft read-only:

```text
gh installiert + angemeldet
→ repos/provoware/bunkergame
→ full_name korrekt
→ nicht archiviert
→ permissions.admin == true
→ main vorhanden
→ protected-Serverhinweis
→ GITHUB_ADMIN_PREFLIGHT: PASS/BLOCKED
```

Die API-Fehlerklassifikation unterscheidet:

- `AUTHORIZATION_403`
- `RESOURCE_404`
- `VALIDATION_422`
- `UNKNOWN_GITHUB_ERROR`

`github_p0_status.py` fragt zuerst den normalen Branch-Endpunkt ab. Bei `protected=false` ist der Branch-Gate-Fehler damit direkt bewiesen. Bei `protected=true` folgt erst die vollständige Detailprüfung der Schutzregeln und Required Checks.

Die Logik ist durch zusätzliche Hosted-Regressionstests abgesichert.

### Erwarteter Nutzen

**Diagnosequalität:** sehr hoch  
**Laienfreundlichkeit:** sehr hoch  
**Fehlbedienungsschutz:** sehr hoch  
**Admin-Sicherheit:** hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-007 — Schutzkonfiguration von privilegiertem Schreibweg entkoppeln

**Iteration:** P0 Independently Verifiable Ruleset Evidence  
**Kategorie:** Evidence Integrity / GitHub Rulesets / Wartbarkeit  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reales Ruleset serverseitig noch anzuwenden  
**Aufwand:** 4/10  
**Risiko:** 2/10

### Verbesserungsvorschlag

Den GitHub-P0-Schutz bevorzugt als Repository Ruleset statt ausschließlich als klassische Branch Protection abbilden und die komplette Soll-/Ist-Prüfung in ein gemeinsames, reines Contract-Modul auslagern.

### Grund

Die klassische Protection-Detail-API kann für bestimmte GitHub-Apps oder Token trotz sichtbarem Repositoryzustand mit 403 blockiert sein. Dann hängen Erzeugung und unabhängige Verifikation zu stark von derselben privilegierten Zugriffsschicht ab. Repository Rulesets sind dagegen bereits mit Repository-Lesezugriff sichtbar und eignen sich deshalb besser als unabhängig prüfbare Infrastruktur-Evidence.

### Wirkung

- Schutz kann nach dem Admin-Write durch eine zweite read-only Stelle vollständig geprüft werden
- Soll-Payload und Ist-Validator verwenden dieselben zentralen Konstanten
- weniger duplizierte GitHub-Regellogik
- Ruleset-Duplikate werden nicht still erzeugt
- Testfixtures validieren nur Logik und können keinen Live-PASS vortäuschen
- klassische Branch Protection bleibt als kompatibler Fallback erhalten

### Technischer Effekt

Neu ist `Scripts/github_p0_ruleset.py` als pure Contract-Schicht. Sie definiert zentral:

```text
Repository + main
→ Ruleset-Name
→ active enforcement
→ PR-Regel
→ static-and-contract
→ repository-quality
→ strict/up-to-date
→ deletion block
→ non-fast-forward block
→ keine Bypass-Akteure
```

`github_p0_admin.py --apply-ruleset` führt ein sicheres Create-or-Update aus und liest anschließend exakt dieses Ruleset zurück. `github_p0_status.py` bevorzugt den Ruleset-Lesepfad und nutzt klassische Branch Protection nur noch als Fallback.

Die Regressionstests lehnen insbesondere `enforcement=evaluate`, fehlende Required Checks, fehlende Strictness, Bypass-Akteure sowie fehlende Delete-/Force-Push-Sperren ab.

### Erwarteter Nutzen

**Evidence-Integrität:** sehr hoch  
**Robustheit:** sehr hoch  
**Codequalität:** sehr hoch  
**Wartbarkeit:** sehr hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-008 — Gespeicherte Infrastruktur-Evidence immer an Live-Zustand rückbinden

**Iteration:** P0 Infrastructure Evidence Bundle  
**Kategorie:** Evidence Integrity / Drift Detection / Reproduzierbarkeit  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — echter Server-PASS weiterhin vom realen Ruleset abhängig  
**Aufwand:** 4/10  
**Risiko:** 2/10

### Verbesserungsvorschlag

Den tokenfreien Live-Check um ein versioniertes, maschinenlesbares Evidence-Bundle erweitern und **gespeicherte PASS-Evidence niemals allein akzeptieren**. Jeder spätere PASS muss zusätzlich durch eine neue Live-Abfrage gegen GitHub bestätigt werden.

### Grund

Eine reine Terminalausgabe ist für spätere Abnahmen schlecht archivfähig. Eine reine JSON-Datei ist dagegen zu leicht veraltet: `main` kann weitergezogen, das Ruleset geändert oder die Datei lokal verändert worden sein. Der robuste Weg kombiniert daher gespeicherten Kontext mit erneuter Gegenwartsprüfung.

### Wirkung

- jeder Infrastruktur-Lauf hinterlässt nachvollziehbare PASS- oder FAIL-Evidence
- Evidence ist an den konkret beobachteten `main`-SHA gebunden
- alter PASS wird nach neuem `main` automatisch ungültig
- Ruleset-ID- und Contract-Drift werden erkannt
- versehentliche lokale Änderungen werden über SHA-256 sichtbar
- FAIL-Bundles bleiben als GitHub-Actions-Artefakt für Diagnose erhalten
- kein gespeichertes Testfixture kann ohne erneute Live-Prüfung einen Produktions-PASS liefern

### Technischer Effekt

`Scripts/github_p0_evidence.py` erzeugt:

```text
schema_version
kind
observed_at_utc
repository + branch
main_sha
ruleset_id + enforcement
contract_status
status
failures
source endpoints
integrity_sha256
```

`Scripts/github_p0_evidence_validate.py` prüft zuerst Struktur, Freshness und Integrität und liest danach GitHub **erneut live**. Nur wenn `main`-SHA, Ruleset-ID und vollständiger P0-Contract weiterhin übereinstimmen, entsteht `GITHUB_P0_EVIDENCE: PASS`.

Der SHA-256-Wert ist bewusst keine Server-Signatur. Er schützt nur die lokale Integrität; die Authentizität wird durch die erneute öffentliche GitHub-Abfrage hergestellt.

Der `P0 Infrastructure Observer` lädt das Bundle mit gepinntem `actions/upload-artifact` auch bei FAIL hoch und setzt den Workflow erst danach auf Fehler. Die neue Testdatei `Scripts/tests/test_p0_evidence_bundle.py` deckt Manipulation, Stale-Evidence, falsches Repository, `main`-Drift und Ruleset-Drift separat ab.

### Erwarteter Nutzen

**Evidence-Integrität:** sehr hoch  
**Drift-Erkennung:** sehr hoch  
**Diagnosefähigkeit:** sehr hoch  
**Reproduzierbarkeit:** sehr hoch  
**Codequalität:** hoch  
**Gameplay-Risiko:** keines