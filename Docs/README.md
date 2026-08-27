# BUNKER BEATS

## Professioneller Projektstatus

**Genre:** 3D Social-Rivalry / Management / Simulation / Progression
**Stil:** trashig, HardTechno-inspiriert, absurd, ironisch, kreativ
**Projektphase:** Pre-Production → Technical/Core Integration
**Dokumentationsstand:** `1.0` dieser Baseline
**Aktueller Fokus:** Headless Core → Runtime Integration
**Unreal Runtime:** NICHT VALIDiert
**Headless Core:** VALIDIERT

> **Wichtig:** Eine Designdefinition ist kein Runtime-Nachweis.
> Dieses README unterscheidet deshalb strikt zwischen **definiert**, **vorbereitet**, **validiert**, **blockiert** und **nicht überprüfbar**.

---

# 1. Spielziel

Der Spieler entwickelt einen individuellen Charakter im und um einen verlassenen Bunker.

Der zentrale Ablauf ist:

`Erkunden`
→ `Interagieren`
→ `Aufgaben erledigen`
→ `Skills verbessern`
→ `Spezialfähigkeiten einsetzen`
→ `eigenes Eventkonzept bauen`
→ `Event durchführen`
→ `Crowd reagiert`
→ `Rivale konkurriert`
→ `Ergebnis / Progression`
→ `neuer Versuch mit anderer Strategie`

Die besondere Spielidee ist nicht eine einzige optimale Route, sondern:

> **Gleiche Ausgangsbasis + unterschiedliche Entscheidungen = unterschiedliche Spielverläufe.**

---

# 2. Startcharaktere

## Pppoppi Poppsen von Bückstücken

Chaotisch, neugierig, kreativ und überzeugt davon, dass ungeplante Fehler eigentlich innovative Features sind.

## Atze

Direkt, konkurrenzorientiert und überzeugt davon, dass jedes Event mindestens ein persönliches Finale verdient.

### Gemeinsame Startwerte

| Skill | Start |
|---|---:|
| TECH | 1 |
| CREATIVE | 1 |
| SOCIAL | 1 |
| PERFORMANCE | 1 |

Beide Charaktere starten bewusst **gleich stark**.

Danach wählt der Spieler:

**2 aus 20 Spezialfähigkeiten.**

Mathematisch entstehen dadurch:

**C(20,2) = 190 mögliche Kombinationen.**

---

# 3. Die 20 Spezialfähigkeiten

1. Kabelmagnet
2. Improvisationskönig
3. Bass-Geflüster
4. Menschenkenntnis
5. Trash-Magnet
6. Deadline-Dämon
7. Ersatzteil-Orakel
8. Crowd-Flüsterer
9. Bühnenbastler
10. Risiko-Rocker
11. Notfallknopf
12. Gerüchteküche
13. Sound-Sommelier
14. Bunkerkarte im Kopf
15. Rivalen-Stichelei
16. Crowd-Bait
17. Silent Operator
18. Charmeoffensive
19. Fehlerfinder
20. Letzte-Platte-Prinzip

Die Effekte sind als Daten-/Gameplaymodell spezifiziert. Die tatsächliche Unreal-Runtime-Wirkung gilt erst nach Implementierung und Test als validiert.

---

# 4. Technische Architektur

Die Kernsysteme sind bewusst getrennt:

```text
Definition
   ↓
Runtime State
   ↓
Persistence State
   ↓
Presentation State
```

Geplante Hauptschichten:

- Character
- World
- Gameplay
- Simulation
- Presentation
- Infrastructure

Der Headless Core testet Regeln ohne Abhängigkeit von Grafik oder Animation.

Die Unreal-Runtime soll diese Regeln darstellen und interaktiv bedienen, nicht neue parallele Spielregeln erfinden.

---

# 5. Headless Core

Der engineunabhängige Kern wurde bereits ausführbar überprüft.

### Aktueller Nachweis

**190 / 190 Kombinationen**

**570 deterministische Szenario-Checks**

**0 strukturelle/rangebezogene Fehler**

Status:

### 🟢 HEADLESS CORE VALIDiert

Das beweist:
- vollständige Kombinationserzeugung
- deterministische Ausführung
- Wertebereichskonsistenz
- grundsätzliche Regel-Ausführbarkeit.

Es beweist noch nicht:
- menschlichen Spielspaß
- finales Balancing
- Animation
- 3D-Interaktion
- Unreal Runtime.

---

# 6. Crowd- und Rivalensystem

Geplante Crowd-Archetypen:

- Basshead
- Dancer
- Visual Seeker
- Underground Purist
- Social Follower

Geplante Rivalenstruktur:

- Ziel
- Strategie
- Skills
- Risikoneigung
- Entscheidungen
- Ergebnis.

Diese Systeme existieren derzeit als Design-/Simulationsgrundlage und sind noch kein validierter 3D-Runtime-Stand.

---

# 7. Event-System

Ein Event setzt sich zusammen aus:

`Musik`
+
`Raum`
+
`Bühne`
+
`Licht`
+
`Atmosphäre`
+
`Performance`

Das System soll mehrere valide Strategien unterstützen.

Die erste Zielausprägung:

- Sound-Fokus
- Atmosphären-Fokus
- Performance-Fokus.

---

# 8. Qualitätssystem

Die Entwicklungs-Pipeline folgt:

`Preflight`
→ `Autoformat`
→ `Test Runner`
→ `Result Collector`
→ `Regression Gate`
→ `Optimization Report`
→ `Checkpoint Gate`

Zusätzlich existieren:

- Dependency Doctor
- Diagnostics / Logging
- Headless Core
- Balance-Matrix
- automatisierte Artefaktberichte.

Regression und Optimierung sind getrennte Entscheidungsstufen.

---

# 9. Debugging und Logging

Diagnose ist getrennt von Basis-/Authoring-Daten.

Zielstruktur:

```text
ProjectData/
Diagnostics/
├── Logs/
├── DebugSnapshots/
├── Regression/
├── Optimization/
├── TestRuns/
└── Reports/
```

Wichtige Ereignisse sollen enthalten:

- Event-ID
- Diagnosecode
- Session-ID
- Run-ID
- Seed
- verständliche Meldung
- technische Details
- Ergebnis.

Für Spieler:
**Was ist passiert? Was bedeutet es? Was kann ich tun?**

Für Entwickler:
**Welche technische Ursache, welcher Zustand und welcher reproduzierbare Kontext?**

---

# 10. Automatischer Start

Die Start-/Diagnoseroutine soll langfristig:

`Klick`
→ `Umgebung erkennen`
→ `Dependencies prüfen`
→ `Projekt vorbereiten`
→ `Build`
→ `Tests`
→ `Regression`
→ `Optimization`
→ `Checkpoint`

abwickeln.

Systemweite Komponenten werden nicht blind installiert. Fehlende Voraussetzungen werden stattdessen eindeutig klassifiziert.

---

# 11. Spielanleitung

`GAMEPLAY_GUIDE.md` ist die laufende Spieler-Dokumentation.

Bei Änderungen prüfen:

- Begriff
- Bedienung
- Voraussetzung
- Konsequenz
- Beispiel
- Fehlerhilfe.

Geplante Features werden nicht als bereits spielbar dargestellt.

---

# 12. Hauptdokumente

| Datei | Zweck |
|---|---|
| `README.md` | Einstieg / Projektwahrheit |
| `AGENTS.md` | verbindliche Entwicklungsregeln |
| `TODO.md` | priorisierter Arbeitsplan |
| `GAMEPLAY_GUIDE.md` | Spieleranleitung |
| `GAME_DESIGN_BIBLE.md` | Game Design |
| `ARCHITECTURE.md` | technische Grenzen |
| `DATA_DICTIONARY.md` | Datenverträge |
| `QA_AUTOPLAYTESTER_SPEC.md` | Teststrategie |
| `PROJECT_SCOPE_ANALYSIS.md` | Scope / Rückwärtsanalyse |
| `PROJEKTSTATUS.md` | belegbarer Projektstatus |
| `CHANGELOG.md` | relevante Änderungen |

---

# 13. Checkpoints

## CP0 — Vision Lock
🟢 abgeschlossen

## CP1 — Technical Boot
🟡 vorbereitet / Runtime blockiert

## CP2 — Movement
⚪ noch nicht validiert

## CP3 — Interaction
⚪ noch nicht validiert

## CP4 — Progression
⚪ Design vorhanden, Runtime nicht validiert

## CP5 — Event
⚪ Design vorhanden, Runtime nicht validiert

## CP6 — Crowd
⚪ Design/Headless-Grundlage vorhanden, Runtime nicht validiert

## CP7 — Rival
⚪ Design vorhanden, Runtime nicht validiert

## CP8 — Discovery
⚪ Design vorhanden, Runtime nicht validiert

## CP9 — Auto Playtester
⚪ Infrastruktur vorhanden, Runtime nicht validiert

## CP10 — Vertical Slice
⚪ noch nicht erreicht

---

# 14. Aktueller technischer Engpass

Der wichtigste offene Engpass ist:

**Unreal Engine + C++-Toolchain + tatsächlicher Runtime-Test.**

Ohne diesen Nachweis darf CP1 nicht auf Grün gesetzt werden.

Die vorhandene Headless-Validierung wird trotzdem weiterverwendet, weil sie unabhängig von der fehlenden Unreal-Umgebung produktiv Nutzen erzeugt.

---

# 15. Entwicklungsprinzipien

Das Projekt folgt der Primärgrundlage:

**Verstehen**
→ **strukturieren**
→ **Abhängigkeiten erkennen**
→ **Arbeit bündeln**
→ **kleinste nachhaltige Änderung**
→ **an der Ursache patchen**
→ **gezielt validieren**
→ **Dokumentation synchronisieren**
→ **Versionierung / Status**
→ **nächsten Engpass bestimmen**

Priorität wird nicht nach Umfang entschieden, sondern nach:

`(Spielnutzen + Risikoreduktion + Zukunftswert + Abhängigkeitsnutzen + Wartbarkeitsgewinn) / (Aufwand + Komplexität + Regressionsrisiko)`

---

# 16. Transparenzstatus

### 🟢 Validiert
- Design-/Datenkonsistenz der bisherigen Baseline
- 2-aus-20-Kombinationslogik
- 190 Kombinationen
- 570 Headless-Szenario-Checks
- 0 strukturelle/rangebezogene Fehler

### 🟡 Teilvalidiert
- Quality-Pipeline
- Diagnostics
- Automation
- Dependency-Orchestrierung

### 🔴 Blockiert / nicht überprüfbar
- Unreal Compilation
- Unreal Editor
- PIE
- 3D Movement
- Animation
- Unreal Crowd Runtime
- Unreal Rival Runtime
- Packaged Build

---

# 17. Übergabepunkt

Ein neuer Entwickler soll anhand dieses Repositories verstehen können:

1. was das Spiel ist,
2. was bereits bewiesen wurde,
3. was nur definiert ist,
4. was blockiert ist,
5. welches Gate als Nächstes erforderlich ist.

**Der nächste harte Gate-Punkt ist CP1 Runtime.**

## Runtime Adapter
A thin Unreal adapter boundary now connects Character/UI/Input concepts to the engine-independent Gameplay API without making Unreal the gameplay-rule owner.

## Ability-driven Task Effects 1.4.0
Spezialfähigkeiten beeinflussen den ersten Bunker-Task bereits über datengetriebene Task-Tags. Prototypwerte, noch nicht final gebalanced.

## CP1 Runtime Evidence 8.3
CP1 besitzt jetzt einen einzigen verifizierbaren Target-Machine-Runner für Build → CharacterSpawnMovement → Report → Gate.
