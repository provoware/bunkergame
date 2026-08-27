# CONTRIBUTING — BUNKER BEATS

> Ziel: Änderungen sollen **klein, beweisbar, rückbaubar und für den nächsten Entwickler verständlich** sein.

---

## 1. SCHNELLSTER SICHERER ABLAUF

1. `README.md` für den aktuellen Gesamtstand lesen.
2. `WICHTIG.md` lesen — dort steht der aktuelle Verbesserungsfokus.
3. `Docs/TODO.md` prüfen — nur eine Aufgabe wählen, die den aktuellen Engpass reduziert.
4. Branch vom aktuellen `main` erstellen.
5. Ursache nachvollziehen und kleinste sinnvolle Änderung umsetzen.
6. lokale Prüfungen ausführen.
7. Dokumentation synchronisieren.
8. `WICHTIG.md` mit **genau einem neuen aktuellen Verbesserungsvorschlag** für die Iteration ersetzen/aktualisieren.
9. in `CODEQUALITÄT.md` **genau einen neuen Eintrag anhängen** — niemals alte Einträge löschen oder umschreiben.
10. PR mit Evidence, Risiko, Rollback und nächstem Gate öffnen/aktualisieren.
11. Required Checks abwarten.
12. nur nach erfüllter Definition of Done mergen.

---

## 2. BRANCH-NAMEN

| Typ | Muster | Beispiel |
|---|---|---|
| Fehler | `fix/...` | `fix/cp1-stale-evidence` |
| Feature | `feat/...` | `feat/interaction-core` |
| Infrastruktur | `infra/...` | `infra/quality-guard` |
| Dokumentation | `docs/...` | `docs/project-status` |
| Refactor | `refactor/...` | `refactor/runtime-gate` |
| Test | `test/...` | `test/cp1-boundaries` |

Ein Branch soll möglichst **einen logischen Zweck** haben.

---

## 3. COMMIT-STIL

Kurzer, eindeutiger Imperativ mit Scope:

```text
cp1: export movement telemetry
quality: reject broken local links
docs: align project status
```

Vermeiden:

```text
update
fix stuff
new version
changes
```

---

## 4. LOKALE PRÜFUNGEN

### Pflicht vor jedem PR-Update

```bash
python3 Scripts/ci_verify.py
python3 Scripts/repo_quality.py
```

### Bei UE-Runtime-Änderungen zusätzlich

Linux:

```bash
./RUN_CP1_UE58_ALL.sh
```

Windows:

```bat
RUN_CP1_UE58_ALL.bat
```

Fehlt UE 5.8, wird Runtime **BLOCKED/UNBEOBACHTET**, niemals PASS.

---

## 5. DOKUMENTATIONSPFLICHT PRO ITERATION

Nach jeder fachlichen Iteration müssen die betroffenen Wahrheitsquellen synchron sein.

### Immer prüfen

- `WICHTIG.md`
- `CODEQUALITÄT.md`
- `Docs/TODO.md`
- `Docs/PROJEKTSTATUS.md`
- `Docs/CHANGELOG.md`

### Nur bei Bedarf

- `README.md` — wenn Einstieg, Status oder Schnellstart betroffen ist
- `ANLEITUNG.md` — wenn Nutzerablauf, Start, Fehlerhilfe oder Bedienung betroffen ist
- `AGENTS.md` — wenn Entwicklungsregeln oder Gates geändert werden

### WICHTIG-Regel

`WICHTIG.md` enthält **einen aktuell priorisierten** Vorschlag aus mindestens einer Kategorie:

- Schwachstelle
- Optimierung
- Verbesserung
- Erweiterung
- Automatisierung
- Risikoabbau

Der Eintrag enthält mindestens:
- Problem/Beobachtung
- Vorschlag
- Grund
- erwartete Wirkung
- Aufwand
- Risiko
- Priorität
- Status

### CODEQUALITÄT-Regel

`CODEQUALITÄT.md` ist **append-only**.

Jeder neue Eintrag enthält:
- eindeutige ID
- Datum/Iteration
- Verbesserungsvorschlag
- Grund
- Wirkung
- technischer Effekt
- Aufwand
- Risiko
- Status

Alte Einträge bleiben als Entwicklungsgedächtnis erhalten.

---

## 6. PR-MINDESTINHALT

Jeder PR beantwortet:

- **Ziel:** Welcher Engpass wird reduziert?
- **Scope:** Was wurde geändert?
- **Nicht geändert:** Was blieb absichtlich draußen?
- **Evidence:** Welche Tests/Checks beweisen den Stand?
- **Runtime-Evidence:** vorhanden / BLOCKED / nicht relevant
- **Risiko:** Was könnte kaputtgehen?
- **Rollback:** Wie wird zurückgerollt?
- **Doku:** Welche Wahrheitsquellen wurden aktualisiert?
- **Nächstes Gate:** Was muss danach bewiesen werden?

---

## 7. GITHUB-CHECKS

### Immer erforderlich

- `Validate`
- `Quality Guard`

### UE-spezifisch

`CP1 UE 5.8 Runtime` läuft auf einem Self-hosted Runner.

Solange der Runner nicht dauerhaft verfügbar ist, darf der Runtime-Job **nicht** als künstlich grüner Ersatzcheck behandelt werden.

Sobald Runner und Toolchain stabil betrieben werden, soll CP1 für runtime-relevante Änderungen zum Merge-Gate werden.

---

## 8. SELF-HOSTED UE-5.8-RUNNER

Benötigte Runner-Labels:

- `self-hosted`
- `unreal`
- `ue-5.8`

Benötigte Repository-Variable:

```text
UE58_RUNNER_ENABLED=true
```

Der Runner darf keine ungeprüften Fork-PRs automatisch ausführen.

---

## 9. NICHT COMMITTEN

- `Saved/`
- `Intermediate/`
- `Binaries/`
- `DerivedDataCache/`
- `Diagnostics/`
- `__pycache__/`
- `*.pyc`
- lokale IDE-/Editor-Dateien
- temporäre Reports
- echte Runtime-Evidence, sofern sie als CI-Artifact vorgesehen ist

---

## 10. DEFINITION OF DONE

Eine Iteration ist erst fertig, wenn:

- Änderung technisch vollständig ist
- relevante Tests grün sind
- kein Test abgeschwächt wurde, um GREEN zu erzeugen
- Evidence korrekt klassifiziert ist
- generierte Dateien nicht versehentlich im Commit sind
- `WICHTIG.md` für diese Iteration aktualisiert ist
- genau ein neuer Qualitätsvorschlag in `CODEQUALITÄT.md` angehängt wurde
- TODO/Projektstatus/Changelog synchron sind
- PR Risiko und Rollback nennt
- der nächste logische Schritt eindeutig ist
