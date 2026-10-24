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

---

## CQ-2026-08-27-009 — Sicherheits-Evidence gegen Kontext-Reuse absichern

**Iteration:** Runner Evidence Binding  
**Kategorie:** Evidence Integrity / Runner Security / Fail-Closed Validation  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reale UE-5.8-Maschinen-Evidence weiterhin offen  
**Aufwand:** 4/10  
**Risiko:** 2/10

### Verbesserungsvorschlag

Readiness-Evidence nicht nur auf Freshness und einzelne positive Checks prüfen, sondern sie an den **konkreten Ausführungskontext** binden und diesen Kontext unmittelbar vor dem sicherheitsrelevanten Zustandsübergang erneut bestimmen.

### Grund

Eine noch frische Readiness-Datei kann ihre Aussagekraft verlieren, wenn sie aus einem anderen Checkout oder von einer anderen Maschine stammt. Zusätzlich reicht ein Git-HEAD allein nicht aus: Uncommittete Änderungen können den Arbeitsstand verändern, ohne den SHA zu ändern. Ein offener Check-Satz birgt außerdem das Risiko, dass eine verkürzte Evidence nur die gerade vorhandenen `true`-Werte enthält und trotzdem akzeptiert wird.

### Wirkung

- kopierte Evidence aus anderem Checkout wird blockiert
- Evidence von einer anderen Maschine wird blockiert
- geänderter Git-HEAD wird blockiert
- nach Readiness verschmutzter Worktree wird blockiert
- fehlende Pflichtchecks werden blockiert
- unbekannte Zusatzchecks werden blockiert
- alte Schema-v2-Evidence wird bewusst nicht mehr zur Runner-Freigabe akzeptiert
- Collector und Admin-Gate verwenden denselben zentralen Readiness-Vertrag
- weniger Drift zwischen Erzeugung und Verbrauch der Evidence

### Technischer Effekt

Neu sind `Scripts/runner_identity.py` und `Scripts/runner_readiness_contract.py`. Das Readiness-Schema v3 enthält Repository, vollständigen Git-HEAD und einen pseudonymen Maschinenfingerprint. Der Pflichtcheck-Satz ist exakt definiert.

Vor `UE58_RUNNER_ENABLED=true` liest `github_p0_admin.py` den aktuellen Kontext erneut:

```text
origin → erwartetes Repository
HEAD → exakt Evidence-HEAD
Maschinenfingerprint → exakt Evidence-Fingerprint
Worktree → weiterhin sauber
Schema v3 → vollständig
Freshness → ≤ 30 Minuten
UE Build.version → exakt 5.8
```

Erst danach kann die Repository-Variable gesetzt werden.

Der Maschinenfingerprint ist ein SHA-256 aus Hostname, Betriebssystem und Architektur. Er ist bewusst **keine Hardware-Attestation** und kein Identitätsnachweis; er reduziert Kontext-Reuse und versehentliche Evidence-Verwechslung, ohne Hardware-Seriennummern zu speichern.

Die separate Testdatei `Scripts/tests/test_runner_evidence_binding.py` prüft Repository-Normalisierung, HEAD-/Maschinen-Reuse, exakten Check-Satz, Bool-/Integer-Kanten, Freshness, Worktree-Drift und die reale Admin-Validator-Verknüpfung.

### Erwarteter Nutzen

**Evidence-Integrität:** sehr hoch  
**Runner-Sicherheit:** sehr hoch  
**Fehlbedienungsschutz:** sehr hoch  
**Codequalität:** sehr hoch  
**Wartbarkeit:** hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-010 — Runtime-GREEN gegen stale, kopierte und manipulierte Evidence absichern

**Iteration:** CP1 Runtime Evidence Contract v3  
**Kategorie:** Runtime Evidence / No-Fake-Success / Regression Prevention  
**Priorität:** P0  
**Status:** 🟡 IMPLEMENTIERT — Hosted-Abnahme und echter UE-5.8-Lauf noch offen  
**Aufwand:** 5/10  
**Risiko:** 3/10

### Verbesserungsvorschlag

CP1-Runtime-GREEN nicht mehr aus einem einzelnen Evidence-JSON und einigen eingebetteten Telemetriekennzahlen ableiten. Stattdessen muss das Gate eine **frische, laufgebundene Beweiskette** aus aktuellem Checkout, Maschine, Unreal-Lauf und tatsächlich vorhandener Telemetrie-Datei erneut validieren.

### Grund

Runtime-GREEN ist fachlich stärker als Readiness. Ein altes `CP1_runtime_evidence.json`, ein gemeinsam kopiertes Evidence-/Telemetry-Paar oder eine nachträglich veränderte Telemetrie darf deshalb keinen aktuellen CP1-Erfolg vortäuschen. Freshness und Datei-Hash allein reichen nicht vollständig aus, weil ein kopiertes Paar vom selben Commit innerhalb des Zeitfensters weiterhin plausibel aussehen könnte.

Die zusätzliche `run_id` löst diesen Restfall: Sie wird vor dem Lauf von Python erzeugt, als Command-Line-Challenge an Unreal übergeben und vom C++-Automationstest selbst in die erzeugte Telemetrie zurückgeschrieben.

### Wirkung

- alte Runtime-Evidence wird vor jedem neuen Versuch entfernt
- alte Telemetrie und alte Automation-Reports werden ebenfalls entfernt
- Abbruch vor einem neuen Evidence-Write kann kein vorheriges GREEN liegen lassen
- Runtime-Evidence wird an Repository, Git-HEAD und Maschine gebunden
- Unreal-Telemetrie wird an genau denselben Lauf gebunden
- kopierte Telemetrie eines anderen Laufs wird über `run_id` abgelehnt
- veränderte Telemetrie wird über SHA-256 erkannt
- eingebettete und echte Telemetrie müssen übereinstimmen
- Gate prüft Freshness, Schema, Schritte, Typen und aktuellen Kontext erneut
- manuelle Gate-Aufrufe können kein altes GREEN übernehmen

### Technischer Effekt

Neu ist `Scripts/cp1_runtime_evidence_contract.py` als zentrale reine Vertragslogik. Telemetrie v3 enthält `run_id`; Runtime-Evidence v3 enthält dieselbe `run_id`, den Telemetrie-SHA-256 sowie Repo-/HEAD-/Maschinenbindung.

Die reale Kette lautet:

```text
purge stale artifacts
→ generate run_id
→ verify repo/head/machine/worktree
→ exact UE 5.8 build
→ launch Unreal with -CP1EvidenceRunId
→ C++ writes telemetry v3 + run_id
→ validate telemetry
→ hash actual telemetry file
→ seal Runtime Evidence v3
→ gate reads current context + actual telemetry again
→ validate run_id + hash + content + freshness
→ CP1_GATE GREEN / RED / BLOCKED
```

`Scripts/run_cp1_ue58.py` ist die kanonische Ein-Befehl-Reihenfolge Readiness → Preflight → Runtime → Gate. Der GitHub-Runtime-Workflow verwendet denselben Orchestrator und listet die Contract-/Gate-Dateien explizit als Triggerpfade.

Die separate Testdatei `Scripts/tests/test_cp1_runtime_evidence_contract.py` prüft unter anderem Schema-v2-Rejection, HEAD-/Maschinen-Drift, stale/future Evidence, Step-Duplikate, Bool-Returncodes, falsche Telemetrie-Schemata, Run-ID-Mismatch, Digest-/Content-Drift, Evidence-Manipulation, Positions-/Displacement-Konsistenz und das sichere Löschen alter Runtime-Artefakte.

### Erwarteter Nutzen

**Runtime-Evidence-Integrität:** sehr hoch  
**No-Fake-Success:** sehr hoch  
**Regressionserkennung:** sehr hoch  
**Diagnosefähigkeit:** sehr hoch  
**Codequalität:** sehr hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-011 — Runner-Registrierung durch serververmittelten Bootstrap beweisen

**Iteration:** UE 5.8 Runner Bootstrap Acceptance  
**Kategorie:** Self-hosted Runner / Server Evidence / Fail-Closed Activation  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — realer Bootstrap-Lauf weiterhin extern offen  
**Aufwand:** 4/10  
**Risiko:** 2/10

### Verbesserungsvorschlag

Die Freigabe des Self-hosted UE-5.8-Runners nicht länger primär aus einer lokalen Readiness-Datei ableiten. Stattdessen soll GitHub selbst beweisen, dass ein Job mit den Pflichtlabels tatsächlich an einen Runner zugestellt wurde und dort die Readiness erfolgreich ausgeführt hat.

### Grund

Eine lokale Readiness-Evidence kann die Maschine und den Checkout sehr streng beschreiben, beweist aber nicht, dass GitHub den Runner registriert hat, ihn erreichen kann oder die erwarteten Scheduler-Labels tatsächlich auf dem zugewiesenen Job vorhanden waren. Außerdem koppelte die bisherige Aktivierung Admin-Terminal und Runner-Workspace unnötig eng.

Der serververmittelte Bootstrap löst diese Lücke: GitHub muss einen Job auf `[self-hosted, unreal, ue-5.8]` wirklich zustellen. Danach lassen sich Run, Job, Runnername, Job-Labels und erfolgreiche Pflichtschritte erneut über die öffentliche GitHub-API prüfen.

### Wirkung

- Runner-Registrierung wird durch reale Jobzustellung statt lokale Annahme bewiesen
- Runnername und Pflichtlabels stammen aus GitHubs Jobdaten
- Bootstrap ist an den aktuellen `main`-SHA gebunden
- nur der neueste passende Bootstrap auf diesem SHA zählt
- ein neuerer Fehllauf kann einen älteren Erfolg nicht verdecken
- Bootstrap-PASS ist nur 30 Minuten als Aktivierungsbeweis gültig
- Admin-Checkout muss exakt auf aktuellem `main` stehen und sauber sein
- lokale `runner_readiness.json` bleibt Diagnose-/Artifact-Evidence, ist aber nicht mehr alleinige Aktivierungsautorität
- Aktivierung über den Helper ist nur noch zusammen mit dem Ruleset-Pfad möglich
- Bootstrap führt niemals CP1 oder einen Repository-Variablen-Write aus

### Technischer Effekt

Neu sind:

```text
.github/workflows/ue58-runner-bootstrap.yml
Scripts/runner_bootstrap_contract.py
Scripts/runner_bootstrap_evidence.py
Scripts/github_runner_bootstrap_public_verify.py
Scripts/tests/test_runner_bootstrap_acceptance.py
```

Die Kette lautet:

```text
workflow_dispatch auf main
→ runs-on [self-hosted, unreal, ue-5.8]
→ runner_readiness.py Schema v3
→ runner_bootstrap_evidence.json
→ Artifact auch bei FAIL
→ Public Verifier liest aktuellen main
→ neuesten passenden Workflow-Run
→ genau einen Bootstrap-Job
→ runner_name + Labels + Pflichtschritte
→ Freshness ≤ 30 Minuten
→ UE58_RUNNER_BOOTSTRAP: PASS / INCOMPLETE
```

`github_p0_admin.py --apply-ruleset --enable-runner-variable` verlangt danach diesen öffentlichen Server-PASS und zusätzlich einen sauberen Admin-Checkout auf exakt demselben aktuellen `main`-SHA. Ein lokales Readiness-JSON allein kann den Variablen-Write damit nicht mehr auslösen.

### Erwarteter Nutzen

**Runner-Evidence-Integrität:** sehr hoch  
**Infrastruktur-Beweisbarkeit:** sehr hoch  
**Fehlbedienungsschutz:** sehr hoch  
**Laienfreundlichkeit:** hoch  
**Codequalität:** sehr hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-012 — GUI und Diagnose-Core über einen versionierten Vor-/Nachvalidierungsvertrag koppeln

**Iteration:** Environment Doctor Pre/Post Contract Hardening  
**Kategorie:** Launcher / GUI / Datenvertrag / Fail-Safe UX  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — Hosted-CI-Abnahme dieser Iteration steht noch aus  
**Aufwand:** 4/10  
**Risiko:** 2/10

### Verbesserungsvorschlag

GUI und Reparatur-Core dürfen keine impliziten oder nur durch Konvention angenommenen Payload-Felder verwenden. Vorprüfung, Reparaturaktion und Nachvalidierung werden als expliziter, versionierter Datenvertrag modelliert und über eine reine Normalisierungsschicht an die Oberfläche übergeben.

### Grund

Der reale Fehler `KeyError: 'after'` zeigte eine klassische Contract-Drift: `repair_gui.py` erwartete `summary.after`, während `EnvironmentAssistant.run()` dieses Feld nicht erzeugte. Eine solche Abweichung darf in einem Diagnosewerkzeug nicht erst im Tkinter-Callback auffallen.

Außerdem erzeugten `diagnostics.py` und `regression_knowledge.py` bereits beim Import Verzeichnisse im Projekt. Solche Import-Seiteneffekte erschweren reproduzierbare Tests und Paketierung.

### Wirkung

- `before` und `after` sind explizite technische Phasen statt nur textliche Absicht
- Gesamtstatus wird aus der Nachvalidierung bestimmt
- Legacy- und Teil-Payloads werden kontrolliert dargestellt
- fehlende Felder führen zu Warn-/Fehlerzuständen statt Callback-Absturz
- Worker-Ausnahmen werden sichtbar an die GUI zurückgegeben
- Tkinter-Polling bleibt nach einzelnen fehlerhaften Events aktiv
- parallele Mehrfachstarts werden während eines laufenden Jobs verhindert
- reine Modulimporte verändern den Projektordner nicht mehr durch Diagnose-/Regression-Ordner
- der konkrete Produktionsfehler ist als Regressionstest konserviert

### Technischer Effekt

Neu ist `Launcher/core/environment_contract.py` mit Schema-Version 2 und reinen Funktionen für Finding-Normalisierung, Statusableitung und fail-safe Payload-Auswertung. `EnvironmentAssistant` serialisiert beide Scan-Phasen; `repair_gui.py` konsumiert ausschließlich die Normalisierungsschicht statt direkt verschachtelte Dictionary-Pfade zu dereferenzieren.

`Scripts/tests/test_environment_gui_contract.py` prüft unter anderem:

- aktuelle `after`-Phase wird bevorzugt
- Legacy-Tupel bleiben kompatibel
- fehlendes `after` fällt auf `before` zurück
- fehlende Vor-/Nachvalidierung fällt kontrolliert auf Restprobleme zurück
- fehlende `summary` ergibt fail-safe RED
- fehlerhafte Einzelzeilen werden übersprungen statt die Darstellung zu zerstören
- ungültiger Gesamtstatus wird aus Findings abgeleitet
- Assistant liefert bei Prüflauf und Reparaturlauf immer zwei Scans
- Reparaturaktionen werden protokolliert und anschließend erneut validiert

Der Repository Quality Guard schützt Contract, Assistant, GUI und Regressionstest als Pflichtdateien.

### Erwarteter Nutzen

**Robustheit:** sehr hoch  
**Laienfreundlichkeit:** sehr hoch  
**Diagnosefähigkeit:** sehr hoch  
**Regressionserkennung:** sehr hoch  
**Wartbarkeit:** sehr hoch  
**Gameplay-Risiko:** keines

---

## CQ-2026-08-27-013 — Dateirechte als testbaren Bestandteil des Portable-Release-Vertrags behandeln

**Iteration:** Linux Click-&-Start Executable Mode  
**Kategorie:** Portabilität / Release Integrity / Linux  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — Hosted-/Release-Abnahme noch offen  
**Aufwand:** 2/10  
**Risiko:** 1/10

### Verbesserungsvorschlag

Unix-Dateimodi dürfen bei portablen Startskripten nicht als nebensächliche Metadaten behandelt werden. Zentrale `.sh`-Einstiege werden als `100755` versioniert und der Package-Integrity-Test prüft die Execute-Bits automatisch.

### Grund

Der Release-Smoke nach dem Environment-Doctor-Fix zeigte, dass `START_BUNKER_BEATS_INTELLIGENT.sh` und `START_BUNKER_BEATS_ALL.sh` zwar per `bash datei.sh` funktionierten, aber nicht als echte Klick-&-Start-Dateien ausgeliefert wurden. Eine nachträgliche Paketkorrektur mit `chmod` würde außerdem den Release-Inhalt von der tatsächlichen `main`-Basis entkoppeln.

### Wirkung

- Git-Checkout und Release-ZIP erhalten dieselben ausführbaren Einstiegspunkte
- kein manuelles `chmod +x` für Laien erforderlich
- Start-/Smoke-/CP1-Shellpfade werden konsistent
- Dateimodus-Regressionen brechen die bestehende CI frühzeitig
- Paketierung bleibt reproduzierbar und muss keine Rechte erfinden

### Technischer Effekt

`Tests/test_cp1_package_integrity.py` prüft für `START_BUNKER_BEATS_INTELLIGENT.sh`, `START_BUNKER_BEATS_ALL.sh`, `RUN_CP1_UE58_ALL.sh` und `Build/Scripts/run_cp1_smoke.sh` Existenz und Unix-Execute-Bits. Die entsprechenden Git-Tree-Einträge werden auf `100755` gesetzt.

### Erwarteter Nutzen

**Portabilität:** sehr hoch  
**Laienfreundlichkeit:** sehr hoch  
**Release-Integrität:** sehr hoch  
**Regressionserkennung:** hoch  
**Gameplay-Risiko:** keines


---

## CQ-2026-10-23-014 — Vorrelease-Pflichten als festen CI-Vertrag absichern

**Iteration:** Vorrelease CI Wiring · **Kategorie:** P0 / Regression / Release-Integrität
**Status:** Implementiert; GitHub-Prüfungen noch zu bestätigen.

### Beobachtung
Eine dokumentierte Vorrelease-Pflichtmatrix reicht nicht aus, wenn der zentrale Validate-Aufruf ihre Prüfung überspringt. Dadurch kann die normale CI grün sein, obwohl Release-Pflichten nicht geprüft wurden.

### Verbesserung
Den vorhandenen Matrix-Vertrag und alle zugehörigen Regressionstests in `Scripts/ci_verify.py` ausführen. Ein eigener Test liest die tatsächliche Python-Befehlsliste, verlangt jeden Pflichtaufruf exakt einmal und prüft den Aufruf des zentralen Prüfers durch `validate.yml`.

### Wirkung
Ausgelassene, doppelte oder versehentlich abgekoppelte Vorrelease-Tests führen künftig zu einem reproduzierbaren Fehler. Die CI deckt damit die Vollständigkeit der **Prüfverkabelung** ab, nicht die fertige Unreal-Runtime.

### Technischer Effekt
`Validate → ci_verify.py → prerelease_gate.py + drei Regressionstests`; echte UE-5.8-Tests, Spielverläufe und Branchschutz bleiben eigenständige Pflichtprüfungen.

---

## CQ-2026-10-23-015 — Ungültige UE-Build.version ohne Absturz abweisen

**Iteration:** Runner Version Shape Guard · **Kategorie:** P0 / Runner-Readiness / Fail-Closed  
**Status:** Implementiert; GitHub-Prüfung noch ausstehend.

### Beobachtung
Gültiges JSON muss nicht zwingend ein Objekt sein. Bei `Build.version` mit JSON-Array oder Skalar führte `data.get()` in der Readiness-Erkennung zu einer unbehandelten Ausnahme. Die bisherige Testdatei war nicht Teil des zentralen Validate-Kommandos.

### Verbesserungsvorschlag
Die äußere Form von `Build.version` vor jedem Feldzugriff prüfen und die bestehenden Runner-Bindungstests samt sechs neuen Nicht-Objekt-Negativfällen als verbindlichen CI-Bestandteil ausführen.

### Grund
Ein ungültiges Maschinenprofil muss geordnet scheitern und darf keine unklare Ausnahme statt eines prüfbaren Readiness-Ergebnisses auslösen. Tests müssen im tatsächlichen CI-Pfad liegen.

### Wirkung
Frühzeitiger, reproduzierbarer Fehlerbericht für ungültige UE-Versiondateien; bessere Erkennung von Regressionen bei Runner-Identität und Readiness-Verträgen. Kein Runtime-PASS und keine Veränderung an Schutzregeln.

### Technischer Effekt
`runner_readiness.py` prüft `isinstance(data, dict)`; `test_runner_evidence_binding.py` prüft sechs JSON-Nicht-Objekte; `ci_verify.py` ruft die Testdatei auf; `test_prerelease_ci_wiring.py` kontrolliert die Einbindung.

### Nachträglicher technischer Nachweis (23.10.2026)

**Geprüfter GitHub-HEAD:** `40f94213d732cf5349fd8c97096a2e8d6a193d5b`. **Validate:** PASS ([Lauf 39954719607](https://github.com/provoware/bunkergame/actions/runs/39954719607)); **Quality Guard:** PASS ([Lauf 39954719562](https://github.com/provoware/bunkergame/actions/runs/39954719562)). In der zentralen CI wurden 22 Runner-Bindungs-Regressionstests ausgeführt; die Qualitätsprüfung führte insgesamt 132 Tests erfolgreich aus. Der neue Negativtest prüft sechs Nicht-Objekt-Varianten. `cp1-runtime` wurde **SKIPPED**; echte UE-5.8-Runtime bleibt BLOCKED/UNOBSERVED.

---

## CQ-2026-10-23-016 — Build.version eindeutig und UTF-8-sicher auswerten

**Iteration:** Runner-Versiondatei-Integrität · **Kategorie:** P0 / Sicherheit / Fail-Closed  
**Status:** IMPLEMENTED; vollständige GitHub-CI auf dem neuen HEAD noch zu prüfen.

### Beobachtung
Die UE-Readiness brach bei ungültigen UTF-8-Bytes mit unbehandeltem UnicodeDecodeError ab. Doppelte JSON-Schlüssel konnten widersprüchliche MajorVersion-Angaben durch den letzten Wert still überschreiben und so 5.8 melden, obwohl die Datei mehrdeutig war. Beide Fehler wurden mit isolierten lokalen Negativfällen reproduziert.

### Verbesserungsvorschlag
JSON-Duplikate beim Einlesen ausdrücklich zurückweisen und Dekodierfehler als kontrolliertes FAIL melden. Regressionen für ungültiges UTF-8, doppelte Schlüssel (auch verschachtelt) und eine weiterhin gültige 5.8-Version in der bereits verpflichtend eingebundenen Runner-Testdatei ergänzen.

### Grund
Maschinenidentität und Engine-Version dürfen nicht aus mehrdeutigen oder unlesbaren Daten bestätigt werden. Eine geordnete Ablehnung ist überprüfbar und schützt die nachfolgenden Runtime-Gates vor falschen Voraussetzungen.

### Wirkung
Malformed-Versiondateien werden ohne Ausnahme abgelehnt. Gültige eindeutige 5.8-Versionen bleiben akzeptiert. Kein echter UE-Build, kein CP1-Runtime-PASS, keine Änderung der Runner-Sicherheitsbedingungen oder des Hauptzweigs.

### Technischer Effekt
`Scripts/runner_readiness.py`: strikter JSON-Objektschlüssel-Parser und UnicodeError-Behandlung. `Scripts/tests/test_runner_evidence_binding.py`: drei neue Testmethoden mit vier negativen und einem positiven Teilfall. CI-Einbindung über vorhandenes `Scripts/ci_verify.py`.


---

## CQ-2026-10-24-017 — Strikte JSON-Zahlen im UE-Runner-Readiness-Vertrag

**Iteration:** Runner-JSON-Konformität · **Kategorie:** P0 / Integrität / Fail-Closed  
**Status:** IMPLEMENTED auf `fix/runner-json-nonfinite-20261024-0038`; lokale isolierte Parser-Prüfung 7/7 PASS, vollständige GitHub-CI noch separat zu prüfen.  
**Ausgangs-HEAD:** `a2d13d5d953bf88644e9b5ef8d922f18978216da` (PR #15, gestapelt; `main` unverändert).

### Beobachtung
`json.loads` akzeptiert standardmäßig `NaN`, `Infinity` und `-Infinity`, obwohl diese Konstanten kein gültiges JSON sind. Die bisherige `read_engine_version`-Prüfung kontrollierte Versionstypen und doppelte Schlüssel, konnte aber ungültige Metadaten still tolerieren.

### Verbesserungsvorschlag
Den vorhandenen Parser mit `parse_constant` auf strikt endliche JSON-Werte beschränken. Nicht normgerechte Konstanten als `ValueError` an die bereits vorhandene kontrollierte FAIL-Behandlung übergeben. Vier negative Teilfälle und einen positiven Metadatenfall in die bestehende CI-verdrahtete Testdatei aufnehmen.

### Grund
Eine Runner-Bereitschaft darf nur auf gültigen, eindeutigen Maschinendaten beruhen. Eine ungültige Versiondatei darf keinen Readiness-PASS ermöglichen, auch wenn Major/Minor zufällig 5.8 ergeben.

### Wirkung
Der Parser meldet bei nicht endlichen Konstanten ein kontrolliertes FAIL. Die vorherige Duplikat-, Unicode- und Formprüfung bleibt erhalten. Kein echter UE-5.8-Lauf, kein Gameplay-Nachweis, keine Änderung an Runner-Labels, Branchschutz, Secrets oder `main`.

### Technischer Effekt
`Scripts/runner_readiness.py`: `parse_constant`-Ablehnung. `Scripts/tests/test_runner_evidence_binding.py`: zwei neue Testmethoden mit vier negativen und einem positiven Fall. Die Tests sind bereits durch `Scripts/ci_verify.py` und `Scripts/tests/test_prerelease_ci_wiring.py` in der Validate-Pflichtprüfung verankert. Lokale isolierte Parser-Reproduktion: 7/7 PASS; Repository-Gesamtprüfung wird über GitHub Actions nachgeholt.


### Nachträglicher GitHub-CI-Nachweis zu CQ-2026-10-24-017 (24.10.2026)

**Geprüfter Code-/Dokumentations-HEAD:** `4f70738799bc75431af5ff19ad70a065f47d5caa`. **Validate:** PASS ([Lauf 40035142309](https://github.com/provoware/bunkergame/actions/runs/40035142309)), `CI_VERIFY: PASS` mit 27 Runner-Bindungs-Tests. **Quality Guard:** PASS ([Lauf 40035142335](https://github.com/provoware/bunkergame/actions/runs/40035142335)), 137 Python-Tests und `ITERATION_GUARD: PASS`. **UE-5.8-CP1:** SKIPPED ([Lauf 40035142370](https://github.com/provoware/bunkergame/actions/runs/40035142370)); kein Runtime-PASS. Dieser append-only Nachtrag liegt in einem späteren Dokumentations-Commit; dessen CI muss erneut separat geprüft werden.


---

## CQ-2026-10-24-018 — CP1-Gate liest Laufzeitnachweise fail-closed

**Iteration:** CP1-Runtime-JSON-Integrität · **Kategorie:** P0 / Sicherheit / Evidence  
**Status:** IMPLEMENTED auf `fix/cp1-evidence-json-strict-20261024-0536`; GitHub-CI und echter UE-5.8-Lauf noch zu beobachten.  
**Ausgangs-HEAD:** `91a822830bcec14d8ab1c3c13128eb2c3d6fc044` (gestapelter Entwurfs-PR #16; `main` unverändert).

### Beobachtung
Der CP1-Gate-Lesepfad verwendete `json.loads` ohne Duplikatschlüssel- und Nichtendlichkeitsprüfung. Ein synthetisches JSON `{"status":"RED","status":"GREEN"}` wird von Python standardmäßig zu `{"status":"GREEN"}` reduziert. Zudem fehlten Größenbegrenzung und Symlink-Sperre. Das ist ein konkretes Integritätsrisiko für Runtime-Evidence und Telemetrie.

### Verbesserungsvorschlag
Beide Dateien vor dem eigentlichen CP1-Vertrag strikt laden: eindeutige JSON-Schlüssel, endliche JSON-Konstanten, UTF-8, kein Symlink, maximal 4 MiB; Rohbytes für den SHA-256-Abgleich erhalten. Acht Regressionstestmethoden verbindlich in Validate aufnehmen.

### Grund
Widersprüchliche oder unkontrollierte Eingabedateien dürfen niemals Grundlage einer technischen CP1-Freigabe sein. Die Prüfung bleibt rein lesend und verändert keine Laufzeitdateien.

### Wirkung und Risiko
Ungültige Eingaben liefern kontrolliert BLOCKED. Der gültige Normalfall bleibt unverändert. Die 4-MiB-Grenze ist bewusst konservativ und muss bei realen, nachweislich größeren Telemetriedateien fachlich begründet angepasst werden. Symlink-Prüfung verhindert übliche Umleitungen, ist keine vollständige Absicherung gegen zeitgleiche Dateiaustausch-Angriffe.

### Technischer Effekt
`Scripts/cp1_gate_runtime.py`, `Scripts/tests/test_cp1_gate_runtime_loader.py`, `Scripts/ci_verify.py`, `Scripts/tests/test_prerelease_ci_wiring.py`; Pflichtmatrix, Runtime-Dokumentation, TODO, CHANGELOG und README synchronisiert. Synthetische Regressionstests beweisen **keinen** Unreal-5.8-Lauf; CP1 bleibt BLOCKED/UNOBSERVED.


---

## CQ-2026-10-24-019 — CP1-Dateideskriptor statt Vorab-Dateipfad vertrauen

**Iteration:** CP1-Evidence-Dateiaustausch · **Kategorie:** P0 / Evidence / Integrität
**Status:** IMPLEMENTED auf `fix/cp1-evidence-file-race-20261024-1038`; GitHub-CI und UE-Runtime noch getrennt zu belegen.
**Ausgangs-HEAD:** `c2335035ef91cc4721e40c12c2de14145e40ee0a` (gestapelter Entwurfs-PR #17; `main` unverändert).

### Beobachtung
`Path.is_symlink()`, `is_file()` und `stat()` vor `Path.open()` schützen nicht gegen einen Austausch der Datei zwischen Prüfung und Öffnen (TOCTOU). Eine kurzfristig ersetzte FIFO-Datei könnte zudem den Gate-Lesepfad blockieren.

### Verbesserungsvorschlag
Mit `os.open` und verfügbaren `O_NOFOLLOW`-/`O_NONBLOCK`-Flags öffnen; die wirklich geöffnete Datei mit `os.fstat` und `stat.S_ISREG` prüfen, dann erst begrenzt lesen. Drei gezielte Regressionstestmethoden für Symlink-Austausch, FIFO-Austausch und Verzeichnisablehnung ergänzen.

### Grund
Nur der bereits geöffnete Deskriptor ist die verlässliche Grundlage für Größen- und Dateitypprüfung. Die vorhandene Integritätsprüfung der unveränderten Rohbytes bleibt maßgeblich.

### Wirkung
Auf Unix wird ein letzter Symlink-Austausch kontrolliert abgewiesen, ein FIFO blockiert den Test nicht. Auf Plattformen ohne `O_NOFOLLOW` ist kein vollständiger Schutz gegen zeitgleichen Symlink-Austausch behauptet. Kein UE-5.8-Runtime-Nachweis und keine Änderung an Runner-Rechten, Branchschutz oder Gameplay.

### Technischer Effekt
`Scripts/cp1_gate_runtime.py` und `Scripts/tests/test_cp1_gate_runtime_loader.py`. Die Testdatei wird bereits durch `Scripts/ci_verify.py` verpflichtend ausgeführt. CI-Nachweis am finalen HEAD bleibt gesondert auszuweisen.


### Nachträglicher GitHub-CI-Nachweis zu CQ-2026-10-24-019 (24.10.2026)

**Geprüfter Code-/Doku-HEAD:** `6e56fd6d7648e3e07367c6c525ff17bdb1a36a12`. **PASS:** [Validate #40078953659](https://github.com/provoware/bunkergame/actions/runs/40078953659), 11 CP1-Loader-Tests; **PASS:** [Quality Guard #40078953654](https://github.com/provoware/bunkergame/actions/runs/40078953654), 148 Python-Tests und Iteration Guard; **SKIPPED:** [UE-5.8-Runtime #40078953633](https://github.com/provoware/bunkergame/actions/runs/40078953633). Späterer Dokumentations-HEAD braucht eigene CI-Evidence; kein CP1-Runtime-PASS.
