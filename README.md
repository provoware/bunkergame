# BUNKER BEATS

> **UE 5.8 · Social-Rivalry / Management / Simulation / Progression · provoware**

BUNKER BEATS wird als **beweisorientiertes Unreal-Engine-Projekt** entwickelt: Ein Punkt gilt erst dann als fertig, wenn der passende Test ihn tatsächlich bestätigt. Ein vorhandener Codepfad ist deshalb nicht automatisch ein bestandener Runtime-Test.

---

## 🚦 Projektstatus auf einen Blick

| Bereich | Ampel | Aktueller Stand | Nächster Beweis |
|---|:---:|---|---|
| Repository-Struktur | 🟢 | aufgebaut | PR-Checks dauerhaft grün halten |
| Headless Core | 🟢 | deterministisch validiert | Regressionen verhindern |
| GitHub Validate | 🟢 | eingerichtet | `static-and-contract` stabil halten |
| Quality Guard | 🟢 | eingerichtet | `repository-quality` stabil halten |
| `main` Branch-Schutz | 🔴 | noch nicht aktiv | Ruleset + Required Checks |
| UE-5.8-Build | 🟡 | vorbereitet | echter Build auf UE-5.8-Maschine |
| Character Spawn | 🟡 | Test implementiert | Runtime-Evidence erzeugen |
| Movement | 🟡 | Test implementiert | messbare Bewegung nachweisen |
| CP1-Telemetrie | 🟢 | implementiert | echte Werte aus Runtime erfassen |
| CP1 Gate | 🔴 | noch nicht bestanden | Build → Spawn → Movement → Evidence |
| Erster Gameplay-Slice | 🔵 | geplant | Interaction → Task → Ability → XP |

> [!IMPORTANT]
> **CP1 ist noch nicht GREEN.** Ohne echten Lauf mit Unreal Engine 5.8 bleibt der Runtime-Status `BLOCKED` bzw. `RUNTIME_NOT_STARTED`. Statische Tests dürfen diesen Zustand niemals zu PASS hochstufen.

---

## ▶️ Schnellstart

### Projekt vollständig prüfen – ohne Unreal Engine

Linux / macOS:

```bash
python3 Scripts/ci_verify.py
python3 Scripts/repo_quality.py
```

Windows:

```bat
python Scripts\ci_verify.py
python Scripts\repo_quality.py
```

**Erwartete Ergebnisse:**

```text
CI_VERIFY: PASS
QUALITY_GUARD: PASS
```

Damit werden neben den CP1-/Projektverträgen auch Dokumentlinks, JSON-Dateien, Python-Syntax, Repository-Hygiene, GitHub-Action-Pinning und die Verbesserungsdateien geprüft.

### CP1 wirklich ausführen – auf einer UE-5.8-Maschine

Linux:

```bash
./RUN_CP1_UE58_ALL.sh
```

Windows:

```bat
RUN_CP1_UE58_ALL.bat
```

Der automatisierte GitHub-Runtime-Pfad führt aus:

```text
Runner Readiness
   ↓
Vorprüfung
   ↓
UE-5.8-Build
   ↓
Character Spawn
   ↓
Movement
   ↓
Frame-Time + Position + Velocity
   ↓
CP1 Gate
   ↓
Runtime-Evidence
```

Die erzeugten Laufdaten liegen unter `Diagnostics/Runtime/` und werden **nicht** in Git eingecheckt.

➡️ Für eine genaue Schritt-für-Schritt-Erklärung: **[ANLEITUNG.md](ANLEITUNG.md)**

---

## 🎯 Aktueller P0

### P0-A — GitHub-Integrationspfad absichern

Der aktuelle organisatorische Bypass ist ein ungeschützter `main`-Branch.

Required Checks nach dem ersten stabilen Quality-Guard-Lauf:

```text
static-and-contract
repository-quality
```

Danach Force-Push und Branch-Löschen sperren und Pull Requests für `main` verpflichtend machen.

➡️ Exakte Einrichtung: **[Docs/GITHUB_P0_SETUP.md](Docs/GITHUB_P0_SETUP.md)**  
➡️ Aktuell wichtigster Verbesserungsvorschlag: **[WICHTIG.md](WICHTIG.md)**

### P0-B — erster echter UE-5.8-CP1-Lauf

CP1 wird nur GREEN, wenn alles bewiesen ist:

- [ ] Projekt kompiliert mit UE 5.8.
- [ ] Editor-/Test-Target startet korrekt.
- [ ] Test-Character wird erzeugt.
- [ ] `CharacterMovementComponent` ist vorhanden und aktiv.
- [ ] Movement-Input erzeugt messbare Positionsänderung.
- [ ] Position vor/nach dem Lauf wird gespeichert.
- [ ] Velocity und Speed werden gespeichert.
- [ ] Frame-Time wird gespeichert.
- [ ] Veraltete Evidence kann den Gate nicht fälschlich bestehen lassen.
- [ ] CP1-Gate meldet erst danach PASS.

**Danach:** `Character → Interaction → erster Task → Ability-Effekt → XP`.

---

## 🤖 GitHub-Automation

### `Validate` → Check `static-and-contract`

Prüft den schnellen, engineunabhängigen Fachpfad:

- Python-/Headless-Tests
- JSON-/Config-Verträge
- Repository-Struktur
- CP1-Runtime-Vertrag
- Failure-/Learning-Logik
- Schutz gegen Fake-Evidence

### `Quality Guard` → Check `repository-quality`

Läuft auf Pull Requests, `main`, manuell und zusätzlich wöchentlich.

Prüft autonom:

- Pflichtdateien
- JSON-Lesbarkeit
- Python-Syntax
- lokale Dokumentlinks
- Merge-Konfliktmarker
- verbotene generierte Pfade
- vollständiges Commit-SHA-Pinning externer GitHub Actions
- Struktur von `WICHTIG.md` und `CODEQUALITÄT.md`
- PR-Regel: `CODEQUALITÄT.md` bleibt append-only
- PR-Regel: Verbesserungsdateien werden je Iteration mitgeführt

### `CP1 UE 5.8 Runtime` → Check `cp1-runtime`

Ist für einen **Self-hosted Runner** mit echter Unreal-Engine-5.8-Installation vorgesehen.

Benötigte Runner-Labels:

```text
self-hosted
unreal
ue-5.8
```

Zusätzlich muss die Repository-Variable gesetzt sein:

```text
UE58_RUNNER_ENABLED=true
```

Vor Unreal selbst läuft `Scripts/runner_readiness.py`. Ein Readiness-PASS beweist nur die Maschinenbereitschaft und niemals CP1.

Der Runtime-Workflow wird absichtlich nicht auf fremdem Fork-Code automatisch ausgeführt.

### Weitere Hilfen

- **Dependabot:** prüft GitHub-Action-Versionen regelmäßig.
- **CODEOWNERS:** ordnet kritische Bereiche zu.
- **Issue-Formulare:** vereinheitlichen Fehler- und Featuremeldungen.
- **PR-Template:** verlangt Ziel, Nachweis, Risiko und Rollback.
- **AGENTS.md:** verbindliche Arbeitsregeln für Entwickler und KI-Agenten.

---

## 🔁 Eingebaute Verbesserungs-Schleife

### `WICHTIG.md`

Enthält **genau einen aktuell priorisierten** Vorschlag: Schwachstelle, Verbesserung, Optimierung, Erweiterung oder Risikoabbau.

### `CODEQUALITÄT.md`

Ist **append-only**. Pro Iteration kommt genau ein neuer Qualitätsvorschlag mit Grund, Wirkung und technischem Effekt hinzu. Alte Einträge bleiben als Entwicklungsgedächtnis erhalten.

Der `Iteration Guard` kontrolliert diese Regeln automatisch auf normalen Pull Requests.

---

## 🧱 Projektstruktur

| Ordner / Datei | Zweck |
|---|---|
| `Source/` | Unreal-C++ und Runtime-/Smoke-Tests |
| `Launcher/` | Diagnose, Reparatur, Lernlogik und Runtime-Orchestrierung |
| `Scripts/` | CI, Gates, Runner, Quality Guards, Reports und Hilfswerkzeuge |
| `Config/` | Policies, Manifeste und Toolchain-Vorgaben |
| `Tests/` | Headless-, Contract-, Quality- und Regressionstests |
| `Docs/` | technische Projekt- und Gameplay-Dokumentation |
| `Diagnostics/` | lokale Laufdaten; bewusst nicht versioniert |
| `AGENTS.md` | verbindliche Entwicklungsregeln |
| `ANLEITUNG.md` | Laienanleitung von Start bis CP1 |
| `WICHTIG.md` | aktueller Verbesserungsfokus |
| `CODEQUALITÄT.md` | append-only Qualitätsjournal |
| `Docs/TODO.md` | priorisierte Entwicklungssteuerung |

---

## 🧭 Welche Datei brauche ich?

| Ich möchte … | Öffnen |
|---|---|
| das Projekt verstehen | `README.md` |
| das Projekt starten/testen | [ANLEITUNG.md](ANLEITUNG.md) |
| den aktuell wichtigsten Verbesserungsfokus sehen | [WICHTIG.md](WICHTIG.md) |
| Qualitätsideen und ihre Wirkung nachvollziehen | [CODEQUALITÄT.md](CODEQUALITÄT.md) |
| wissen, was als Nächstes kommt | [Docs/TODO.md](Docs/TODO.md) |
| den aktuellen technischen Status lesen | [Docs/PROJEKTSTATUS.md](Docs/PROJEKTSTATUS.md) |
| GitHub-Schutz + UE-Runner einrichten | [Docs/GITHUB_P0_SETUP.md](Docs/GITHUB_P0_SETUP.md) |
| Entwicklungsregeln verstehen | [AGENTS.md](AGENTS.md) |
| tiefer in die Architektur gehen | [Docs/README.md](Docs/README.md) |
| CP1 technisch nachvollziehen | [Docs/CP1_RUNTIME_EXECUTION.md](Docs/CP1_RUNTIME_EXECUTION.md) |
| Gameplay und Spielidee lesen | [Docs/GAMEPLAY_GUIDE.md](Docs/GAMEPLAY_GUIDE.md) |

---

## 🧪 Evidence-Prinzip

BUNKER BEATS unterscheidet strikt zwischen:

| Zustand | Bedeutung |
|---|---|
| 🟢 **PASS** | tatsächlich geprüft und bestanden |
| 🟡 **BLOCKED / UNOBSERVED** | Prüfung ist vorbereitet, aber noch nicht ausführbar oder ausgeführt |
| 🔴 **FAIL** | Prüfung wurde ausgeführt und ist fehlgeschlagen |
| 🔵 **PLANNED** | geplant, aber noch nicht Teil des aktuellen Gates |

**Nicht erlaubt:** `nicht getestet → vermutlich okay → PASS`.

---

## 🔄 Empfohlener Entwicklungsfluss

```text
Problem / Ziel
   ↓
WICHTIG + TODO prüfen
   ↓
kleinste sinnvolle Änderung
   ↓
ci_verify + repo_quality
   ↓
passender Regressionstest
   ↓
WICHTIG aktualisieren
   ↓
CODEQUALITÄT anhängen
   ↓
Commit auf Arbeitsbranch
   ↓
Pull Request
   ↓
static-and-contract + repository-quality
   ↓
bei Runtime-Themen: echter UE-5.8-Test
   ↓
Evidence prüfen
   ↓
Merge erst bei erfülltem Gate
```

---

## 📌 Aktueller Entwicklungsfokus

**P0:** Repository-Gates verbindlich machen und danach den echten UE-5.8-CP1-Lauf ausführen und beweisen.

**P1 danach:** erster spielbarer Vertikalschnitt:

```text
Character
→ Interaction
→ erster Task
→ Ability-Effekt
→ XP
```

**Nicht priorisieren**, bevor dieser Pfad funktioniert: große Crowd-, Rivalen-, Event-, Grafik- oder Content-Erweiterungen ohne direkten Gate-Nutzen.

---

## 📚 Zentrale Dokumente

- [Laienanleitung](ANLEITUNG.md)
- [Aktueller Verbesserungsfokus](WICHTIG.md)
- [Codequalitäts-Journal](CODEQUALITÄT.md)
- [Master TODO](Docs/TODO.md)
- [Repository-/Agentenregeln](AGENTS.md)
- [Beitragen / GitHub-Workflow](CONTRIBUTING.md)
- [Technische Projektdokumentation](Docs/README.md)
- [Projektstatus](Docs/PROJEKTSTATUS.md)
- [GitHub-P0-Setup](Docs/GITHUB_P0_SETUP.md)
- [CP1 Runtime-Ausführung](Docs/CP1_RUNTIME_EXECUTION.md)
- [CP1 Smoke Suite](Docs/CP1_SMOKE_SUITE.md)
- [Gameplay Guide](Docs/GAMEPLAY_GUIDE.md)

---

## ✅ Definition von „fertig“

Eine Änderung ist erst fertig, wenn:

1. der Zweck eindeutig ist,
2. die kleinste sinnvolle Lösung umgesetzt wurde,
3. vorhandene Tests weiter bestehen,
4. neue Risiken durch passende Tests abgedeckt sind,
5. der Status nicht besser dargestellt wird als die Evidence erlaubt,
6. `WICHTIG.md` aktualisiert wurde,
7. genau ein neuer Eintrag in `CODEQUALITÄT.md` angehängt wurde,
8. TODO/Projektstatus/Changelog bei relevanten Änderungen synchron sind,
9. der Pull Request Risiko und Rollback nachvollziehbar enthält,
10. die Required Checks passend zum Scope grün sind.

**Aktuelle Wahrheit:** Die statische/automatische Control Plane steht. Branch-Schutz und der echte UE-5.8-Runtime-Beweis sind die nächsten entscheidenden P0-Schritte.
