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
