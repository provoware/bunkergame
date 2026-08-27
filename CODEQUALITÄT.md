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
