# BUNKER BEATS

> **UE 5.8 · Social-Rivalry / Management / Simulation / Progression · provoware**

BUNKER BEATS wird als **beweisorientiertes Unreal-Engine-Projekt** entwickelt: Ein Punkt gilt erst dann als fertig, wenn der passende Test ihn tatsächlich bestätigt. Ein vorhandener Codepfad ist deshalb nicht automatisch ein bestandener Runtime-Test.

---

## 🚦 Projektstatus auf einen Blick

| Bereich | Ampel | Aktueller Stand | Nächster Beweis |
|---|:---:|---|---|
| Repository-Struktur | 🟢 | aufgebaut | PR-Checks dauerhaft grün halten |
| Headless Core | 🟢 | deterministisch validiert | Regressionen verhindern |
| GitHub CI | 🟢 | `Validate` eingerichtet | auf jedem PR ausführen |
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

### Nur Projekt prüfen – ohne Unreal Engine

Linux / macOS:

```bash
python3 Scripts/ci_verify.py
```

Windows:

```bat
python Scripts\ci_verify.py
```

**Erwartetes Ergebnis:**

```text
CI_VERIFY: PASS
```

Damit werden Projektstruktur, Python-Code, JSON-Dateien, CP1-Vertrag und die Regel gegen erfundene Runtime-Erfolge geprüft.

### CP1 wirklich ausführen – auf einer UE-5.8-Maschine

Linux:

```bash
./RUN_CP1_UE58_ALL.sh
```

Windows:

```bat
RUN_CP1_UE58_ALL.bat
```

Der Runner führt automatisch aus:

```text
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

## 🎯 Aktueller P0 – genau ein Engpass

Der wichtigste nächste Schritt ist der **erste echte CP1-Lauf auf einer Maschine mit Unreal Engine 5.8**.

### CP1 wird nur GREEN, wenn alles bewiesen ist

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

### `Validate`

Läuft auf Pull Requests und prüft den schnellen, engineunabhängigen Teil:

- Python-Syntax und Tests
- JSON-/Config-Verträge
- Repository-Struktur
- CP1-Runtime-Vertrag
- Failure-/Learning-Logik
- Schutz gegen Fake-Evidence

### `CP1 UE 5.8 Runtime`

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

Der Runtime-Workflow wird absichtlich nicht auf fremdem Fork-Code automatisch ausgeführt.

### Weitere Hilfen

- **Dependabot:** prüft GitHub-Action-Versionen regelmäßig.
- **CODEOWNERS:** ordnet kritische Bereiche zu.
- **Issue-Formulare:** vereinheitlichen Fehler- und Featuremeldungen.
- **PR-Template:** verlangt Ziel, Nachweis, Risiko und Rollback.
- **AGENTS.md:** verbindliche Arbeitsregeln für Entwickler und KI-Agenten.

---

## 🧱 Projektstruktur

| Ordner / Datei | Zweck |
|---|---|
| `Source/` | Unreal-C++ und Runtime-/Smoke-Tests |
| `Launcher/` | Diagnose, Reparatur, Lernlogik und Runtime-Orchestrierung |
| `Scripts/` | CI, Gates, Runner, Reports und Hilfswerkzeuge |
| `Config/` | Policies, Manifeste und Toolchain-Vorgaben |
| `Tests/` | Headless-, Contract-, Quality- und Regressionstests |
| `Docs/` | technische Projekt- und Gameplay-Dokumentation |
| `Diagnostics/` | lokale Laufdaten; bewusst nicht versioniert |
| `AGENTS.md` | verbindliche Entwicklungsregeln |
| `ANLEITUNG.md` | Laienanleitung von Start bis CP1 |
| `Docs/TODO.md` | priorisierte Entwicklungssteuerung |

---

## 🧭 Welche Datei brauche ich?

| Ich möchte … | Öffnen |
|---|---|
| das Projekt verstehen | `README.md` |
| das Projekt starten/testen | [ANLEITUNG.md](ANLEITUNG.md) |
| wissen, was als Nächstes kommt | [Docs/TODO.md](Docs/TODO.md) |
| Entwicklungsregeln verstehen | [AGENTS.md](AGENTS.md) |
| tiefer in die Architektur gehen | [Docs/README.md](Docs/README.md) |
| den aktuellen technischen Status lesen | [Docs/PROJEKTSTATUS.md](Docs/PROJEKTSTATUS.md) |
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
kleinste sinnvolle Änderung
   ↓
lokale Schnellprüfung
   ↓
passender Regressionstest
   ↓
Commit auf Arbeitsbranch
   ↓
Pull Request
   ↓
GitHub Validate
   ↓
bei Runtime-Themen: echter UE-5.8-Test
   ↓
Evidence prüfen
   ↓
Merge erst bei erfülltem Gate
```

---

## 📌 Aktueller Entwicklungsfokus

**P0:** echten UE-5.8-CP1-Lauf ausführen und beweisen.

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
- [Master TODO](Docs/TODO.md)
- [Repository-/Agentenregeln](AGENTS.md)
- [Beitragen / GitHub-Workflow](CONTRIBUTING.md)
- [Technische Projektdokumentation](Docs/README.md)
- [Projektstatus](Docs/PROJEKTSTATUS.md)
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
6. README/TODO/Anleitung bei sichtbaren Änderungen aktualisiert wurden,
7. der Pull Request den Nachweis nachvollziehbar enthält.

**Aktuelle Wahrheit:** Die Infrastruktur für CP1 steht. Der echte UE-5.8-Runtime-Beweis ist der nächste entscheidende Schritt.
