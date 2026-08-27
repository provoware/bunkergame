# BUNKER BEATS — MASTER TODO

**Arbeitsstand:** CP1 Runtime Integration  
**Steuerungsmodell:** P0–P6 + Gates + Evidence  
**Grundsatz:** Nicht möglichst viel anfangen, sondern den **nächsten Engpass vollständig beweisen**.

---

# 0. 🚦 CURRENT TRUTH

## 🟢 Bewiesen / vorhanden

- [x] Unreal-Projektstruktur vorhanden
- [x] UE-5.8-Engine-Association definiert
- [x] Game-Target vorhanden
- [x] Editor-Target vorhanden
- [x] primäres Game-Modul vorhanden
- [x] CP1 Character-Spawn-/Movement-Test implementiert
- [x] kontrollierte Testwelt für CP1 vorgesehen
- [x] Frame-Time-Evidence implementiert
- [x] Start-/Endposition-Evidence implementiert
- [x] Velocity-/Speed-Evidence implementiert
- [x] Movement-Component-Evidence implementiert
- [x] stale Evidence wird vor Runtime-Lauf entfernt
- [x] One-Command-Runner Linux/Windows vorhanden
- [x] `Scripts/ci_verify.py` vorhanden
- [x] statische GitHub-Validierung vorhanden
- [x] Runtime-Workflow für Self-hosted UE-5.8-Runner vorhanden
- [x] GitHub-Repository-Control-Plane vorhanden
- [x] 20 Spezialfähigkeiten definiert
- [x] 2-aus-20-Regel definiert
- [x] 190 Kombinationen im Headless-Modell abgedeckt
- [x] deterministische Headless-/Regression-Grundlage vorhanden

## 🟡 Vorbereitet, aber noch nicht Runtime-bewiesen

- [ ] UE-5.8-Projekt erfolgreich auf Zielmaschine kompilieren
- [ ] Editor-Target erfolgreich kompilieren
- [ ] CP1-Automation in echter UE-5.8-Runtime ausführen
- [ ] Character Spawn mit echter Runtime-Evidence bestätigen
- [ ] messbare Bewegung bestätigen
- [ ] Telemetrie aus echtem Lauf prüfen
- [ ] CP1 Gate auf echte Evidence anwenden

## 🔴 Darf aktuell NICHT als PASS gelten

- [ ] CP1 Runtime GREEN
- [ ] vollständige 3D-Interaktion
- [ ] Ability-Effekte in Unreal Runtime
- [ ] XP-/Progressionsfluss in Unreal Runtime
- [ ] Event-Runtime
- [ ] Crowd-Runtime
- [ ] Rivalen-Runtime
- [ ] Save/Load-Runtime
- [ ] Packaged Build

> **Evidence-Regel:** `nicht ausgeführt` = `UNOBSERVED/BLOCKED`, niemals `PASS`.

---

# 1. 🔥 JETZT — ACTIVE BOARD

## P0.1 — Echter UE-5.8-CP1-Lauf

**Priorität:** P0  
**Nutzen:** 10/10  
**Aufwand:** niedrig bis mittel  
**Risiko:** niedrig, wenn Evidence-Regeln eingehalten werden  
**Blockiert:** gesamter weitere Runtime-Pfad

### Ziel

Den ersten echten technischen Checkpoint auf einer Maschine mit Unreal Engine 5.8 beweisen.

### Aufgaben

- [ ] UE-5.8-Maschine bereitstellen
- [ ] C++-Toolchain prüfen
- [ ] Repository auf Zielmaschine auschecken
- [ ] `python3 Scripts/ci_verify.py` / Windows-Variante ausführen
- [ ] `RUN_CP1_UE58_ALL.sh` oder `.bat` starten
- [ ] Build-Ergebnis prüfen
- [ ] Character-Spawn-Evidence prüfen
- [ ] Movement-Evidence prüfen
- [ ] Frame-Time prüfen
- [ ] Position vorher/nachher prüfen
- [ ] Velocity/Speed prüfen
- [ ] Movement-Component-Status prüfen
- [ ] CP1 Gate ausführen
- [ ] Evidence als GitHub-Artifact sichern

### Definition of Done

CP1 ist nur abgeschlossen, wenn:

- [ ] UE 5.8 tatsächlich verwendet wurde
- [ ] Build PASS
- [ ] Character Spawn PASS
- [ ] Movement Component gültig/aktiv
- [ ] Displacement messbar > erforderlicher Grenzwert
- [ ] Position vorhanden
- [ ] Velocity vorhanden
- [ ] Frame-Time vorhanden
- [ ] Evidence stammt aus demselben Lauf
- [ ] keine alte Evidence kann PASS erzeugen
- [ ] CP1 Gate PASS

### Abbruchregel

Bei erstem echten Build-/Runtime-Fehler:

1. Fehler klassifizieren.
2. kleinste Ursache isolieren.
3. nur diese Ursache beheben.
4. passenden Regressionstest ergänzen.
5. CP1 erneut vollständig ausführen.

---

## P0.2 — GitHub Self-hosted UE-5.8-Runner

**Ziel:** CP1 wiederholbar über GitHub ausführen.

- [ ] Self-hosted Runner auf UE-5.8-Maschine installieren
- [ ] Label `self-hosted` prüfen
- [ ] Label `unreal` hinzufügen
- [ ] Label `ue-5.8` hinzufügen
- [ ] Repository-Variable `UE58_RUNNER_ENABLED=true` setzen
- [ ] Runner nur für vertrauenswürdigen Code zulassen
- [ ] ersten Workflow-Lauf starten
- [ ] Runtime-Evidence-Artifact prüfen
- [ ] Runner-Ausfall als `BLOCKED`, nicht als Gameplay-FAIL behandeln

**Gate:** Erst danach ist CP1 als wiederholbare CI-Prüfung etabliert.

---

## P0.3 — Repository-Gate härten

- [x] `.gitignore`
- [x] `.gitattributes`
- [x] `.editorconfig`
- [x] CODEOWNERS
- [x] PR-Template
- [x] Issue-Templates
- [x] Dependabot
- [x] `Validate`-Workflow
- [x] UE-5.8-Runtime-Workflow
- [ ] `Validate` als Required Check für `main`
- [ ] Branch-Protection / Ruleset für `main`
- [ ] direkte Pushes auf `main` verhindern
- [ ] Review-Anforderung festlegen
- [ ] Merge-Strategie final festlegen
- [ ] Release-/Tag-Regel definieren

---

# 2. 🟣 DIREKT NACH CP1 — ERSTER SPIELBARER VERTIKALSCHNITT

> **Reihenfolge bleibt verbindlich:** Character → Interaction → erster Task → Ability-Effekt → XP.

---

## P1.1 — Interaction Core

**Abhängigkeit:** CP1 PASS

### Ziel

Der Character erkennt genau ein interaktives Objekt und kann eine definierte Aktion auslösen.

### Aufgaben

- [ ] `IInteractable`-/Interaction-Vertrag festlegen
- [ ] Interaktionsziel erkennen
- [ ] verfügbar / nicht verfügbar unterscheiden
- [ ] verständlichen Grund bei Sperre liefern
- [ ] Interaktion ausführen
- [ ] Success-Feedback
- [ ] Failure-Feedback
- [ ] Diagnoseevent schreiben
- [ ] funktionalen Automation-Test ergänzen

### DoD

`Character → erkennt Objekt → Interaktion → bestätigtes Ergebnis → Evidence`

---

## P1.2 — Erster echter Task

**Abhängigkeit:** Interaction PASS

### Ziel

Eine kleine Aufgabe komplett vom Start bis zum Ergebnis spielen.

### Aufgaben

- [ ] TaskDefinition festlegen
- [ ] stabile Task-ID
- [ ] Voraussetzung
- [ ] Ziel
- [ ] erforderliche Aktion
- [ ] Fortschritt
- [ ] Erfolg
- [ ] Fehlschlag
- [ ] Reward
- [ ] Konsequenz
- [ ] Telemetrie
- [ ] deterministischen Test ergänzen

### Empfohlener erster Task

Ein klar begrenzter Bunker-Aufbau-/Reparaturtask mit genau einer Interaktion und überprüfbarem Ergebnis.

---

## P1.3 — Ability-Effekt im Task

**Abhängigkeit:** Task PASS

### Ziel

Mindestens eine Spezialfähigkeit verändert nachweisbar den Task-Ausgang.

- [ ] eine Ability auswählen
- [ ] Ability-ID stabil halten
- [ ] Ability auf Task anwenden
- [ ] Effekt vor/nach Anwendung messen
- [ ] Effektbegrenzung definieren
- [ ] kein versteckter Parallel-Regelpfad
- [ ] Regressionstest Ability an/aus
- [ ] Ergebnis für Spieler erklären

### DoD

Gleicher Task + gleiche Ausgangslage + Ability an/aus = **messbar unterschiedliches, erklärbares Ergebnis**.

---

## P1.4 — XP / Progression

**Abhängigkeit:** Task + Ability-Effekt PASS

- [ ] XP-Ereignis definieren
- [ ] XP nur bei bestätigtem Ergebnis vergeben
- [ ] zentrale Threshold-Tabelle
- [ ] Level 1–5
- [ ] Grenzwerttests
- [ ] doppelte XP-Vergabe verhindern
- [ ] Runtime-Evidence
- [ ] UI-/Feedback-Schnittstelle vorbereiten

### Prototypwerte

| Level | XP |
|---:|---:|
| 1 | 0 |
| 2 | 100 |
| 3 | 250 |
| 4 | 500 |
| 5 | 850 |

Diese Werte bleiben Prototypdaten, bis Playtests sie stützen.

---

# 3. 🟦 DANACH — CHARACTER / ABILITY SYSTEM

## Character Identity

- [ ] Pppoppi Runtime-Profil
- [ ] Atze Runtime-Profil
- [ ] gleiche Startwerte sicherstellen
- [ ] persistente Character-ID
- [ ] Bio-/Info-Daten anbinden
- [ ] Skill-Anzeige

## 2-aus-20 Ability Selection

- [ ] alle 20 Abilities als stabile Definitionen
- [ ] genau 2 auswählbar
- [ ] keine Duplikate
- [ ] 2/20-Zähler
- [ ] Auswahl bestätigen
- [ ] Auswahl persistent speichern
- [ ] Telemetrie schreiben
- [ ] ungültige Auswahl verständlich erklären
- [ ] 190-Kombinationsscan weiter als Headless-Regression verwenden

---

# 4. 🟠 PERSISTENCE — VOR ERSTEM RELEASE CANDIDATE

- [ ] `SaveSchemaVersion`
- [ ] stabile persistente IDs
- [ ] atomare Schreibvorgänge
- [ ] Backup vor Migration
- [ ] Recovery-Pfad
- [ ] Migrationstabelle
- [ ] beschädigten Save simulieren
- [ ] Migration Regression Tests
- [ ] Character-Auswahl speichern/laden
- [ ] Ability-Auswahl speichern/laden
- [ ] Task-/XP-Stand speichern/laden

**Release-Gate:** Kein Release Candidate ohne bewiesene Save-Integrität.

---

# 5. 🔵 SPÄTER — EVENT / CROWD / RIVAL / DISCOVERY

Diese Bereiche bleiben wichtig, sind aber **nicht der aktuelle Engpass**.

## Event

- [ ] EventDefinition
- [ ] Musikprofil
- [ ] Raum
- [ ] Bühne
- [ ] Licht
- [ ] Atmosphäre
- [ ] Performance
- [ ] EventBuilder
- [ ] EventEvaluator
- [ ] Outcome
- [ ] Event-Historie
- [ ] Ergebnis erklären

## Crowd

Archetypen:

- [ ] Basshead
- [ ] Dancer
- [ ] Visual Seeker
- [ ] Underground Purist
- [ ] Social Follower

States:

- [ ] ARRIVING
- [ ] WARMING_UP
- [ ] ENGAGED
- [ ] HYPED
- [ ] BORED
- [ ] LEAVING

Evidence:

- [ ] deterministischer Seed
- [ ] Gewichtungstest
- [ ] State-Transition-Test
- [ ] 100+ repräsentative Läufe
- [ ] Baseline-/Current-Vergleich

## Rival

- [ ] Rivalen-ID
- [ ] Ziel
- [ ] Strategie
- [ ] Skills
- [ ] Risikoneigung
- [ ] Aktionsauswahl
- [ ] Ergebnis
- [ ] Debug-Erklärung
- [ ] erster vollständig datengetriebener Rivale

## Discovery

- [ ] versteckter Ort
- [ ] Entdeckungsbedingung
- [ ] Hinweis
- [ ] Reward
- [ ] World Flag
- [ ] Story-Konsequenz
- [ ] Persistence

---

# 6. 🎛️ UX / SPIELERFÜHRUNG

## Character Creation

- [ ] Character-Auswahl
- [ ] Profilkarte
- [ ] Skills
- [ ] Ability Grid
- [ ] 2/20-Zähler
- [ ] klare Auswahlmarkierung
- [ ] Wirkung erklären
- [ ] Bestätigung
- [ ] ungültige Auswahl reparierbar machen

## Gameplay HUD

- [ ] aktuelles Ziel
- [ ] Interaktionshinweis
- [ ] Task-Status
- [ ] Skill-/Ability-Feedback
- [ ] XP-/Level-Feedback
- [ ] Event-Status
- [ ] Crowd-Status
- [ ] Rivalen-Status
- [ ] Konsequenzen erklären

## Hilfe

- [x] Root-`ANLEITUNG.md`
- [ ] First-Run-Guide im Spiel
- [ ] kontextbezogene Hilfe
- [ ] Ability-Glossar
- [ ] Fehlerhilfe
- [ ] Recovery-Hilfe
- [ ] aktuelle Steuerung automatisch dokumentieren

---

# 7. 🎨 PRESENTATION

Erst hochpriorisieren, wenn der passende Gameplay-Pfad bewiesen ist.

## Character

- [ ] Placeholder-Modell
- [ ] Pppoppi-Identität
- [ ] Atze-Identität
- [ ] Customization-Basis

## Animation

- [ ] Locomotion
- [ ] Interact
- [ ] Carry
- [ ] Repair
- [ ] Setup
- [ ] Performance
- [ ] Success
- [ ] Failure

## Audio

- [ ] Bunker-Ambience
- [ ] UI-Feedback
- [ ] Task-Feedback
- [ ] Event-Feedback
- [ ] Crowd-Feedback
- [ ] Rivalen-Cues

## Licht / VFX

- [ ] Bunker-Lesbarkeit
- [ ] Interaktionslesbarkeit
- [ ] Event-Atmosphäre
- [ ] Crowd-Lesbarkeit
- [ ] initiales Effektbudget begrenzen

---

# 8. 🧪 QUALITY / AUTOMATION

## Auto Playtester

- [ ] T01_BOOT
- [ ] T02_MOVEMENT
- [ ] T03_INTERACTION
- [ ] T04_TASK
- [ ] T05_CHARACTER_CREATION
- [ ] T06_ABILITY_SELECTION
- [ ] T07_ABILITY_EFFECT
- [ ] T08_XP_PROGRESSION
- [ ] T09_EVENT
- [ ] T10_CROWD
- [ ] T11_RIVAL
- [ ] T12_DISCOVERY
- [ ] T13_RECOVERY
- [ ] T14_REPEATABILITY
- [ ] T15_SAVE_LOAD
- [ ] T16_PACKAGED_BUILD

### Testmodi später

- [ ] Conservative
- [ ] Aggressive
- [ ] Explorer
- [ ] Improviser
- [ ] Completionist

---

## Regression

- [x] Baseline-/Current-Konzept
- [x] Severity-Grundlage
- [x] Threshold-Grundlage
- [x] First-Failure-Guidance
- [x] Solution-Learning-Grundlage
- [ ] echte Unreal-Evidence automatisch ingestieren
- [ ] historische Runtime-Baseline Registry
- [ ] Trend-Erkennung
- [ ] automatische Checkpoint-Gates
- [ ] Flaky-Test-Erkennung

### Ampelregel

- 🟢 **GREEN** = bewiesen, keine materielle Regression
- 🟡 **YELLOW** = Evidence fehlt oder Prüfung blockiert
- 🔴 **RED** = echter Fehler / materielle Regression

---

## Preflight / Format

- [x] Python-Syntaxprüfung
- [x] JSON-Prüfung
- [x] generierte UE-Ordner via `.gitignore` ausschließen
- [x] EditorConfig
- [x] Git Attributes
- [ ] C++-Formatter mit echter Toolchain integrieren
- [ ] Pre-Commit-Hook optional bereitstellen
- [ ] Workflow-Linting ergänzen
- [ ] Dokumentations-Linkprüfung ergänzen

---

# 9. 🧠 LEARNING / SELF-REPAIR

- [x] Fehler-Taxonomie vorhanden
- [x] Lösungsvorschläge vorhanden
- [x] Erfolgs-/Fehlversuche modellierbar
- [x] Ranking nach Ergebnissen möglich
- [x] Kontext für Toolchain-Reparaturen vorhanden
- [ ] echte UE-Reparaturergebnisse automatisch zurückspielen
- [ ] Erfolgsquoten nach OS trennen
- [ ] Erfolgsquoten nach UE-Version trennen
- [ ] Erfolgsquoten nach Fehlertyp trennen
- [ ] widersprüchliche Lernergebnisse erkennen
- [ ] veraltete Regeln ablaufen lassen
- [ ] menschliches Review für promotete Regeln

**Regel:** Self-Repair darf nie Evidence fälschen oder Tests abschwächen.

---

# 10. 🏁 GATES

## CP1 — Build + Spawn + Movement

- [ ] echter UE-5.8-Build
- [ ] Character Spawn
- [ ] Movement
- [ ] Runtime-Telemetrie
- [ ] Evidence frisch
- [ ] Gate PASS

## Vertical Slice 1

- [ ] CP1
- [ ] Interaction
- [ ] erster Task
- [ ] Ability-Effekt
- [ ] XP
- [ ] automatisierter End-to-End-Test

## Vertical Slice Core

- [ ] Start
- [ ] Movement
- [ ] Interaction
- [ ] Task
- [ ] Character-Auswahl
- [ ] 2/20 Ability-Auswahl
- [ ] Ability-Effekt
- [ ] XP / Progression
- [ ] Event
- [ ] Crowd
- [ ] Rival
- [ ] Discovery
- [ ] Save/Load
- [ ] deterministischer Replay-Nachweis
- [ ] Regression Gate
- [ ] Spielerhilfe aktuell

---

# 11. 🚫 NICHT JETZT

Bis CP1 + erster Vertikalschnitt bewiesen sind, nur bei zwingender Abhängigkeit beginnen:

- [ ] große Grafik-Politur
- [ ] umfangreiche Animationserweiterung
- [ ] Crowd-Komplexität
- [ ] mehrere Rivalen
- [ ] großes Event-Content-System
- [ ] Multiplayer
- [ ] tiefes Balancing ohne Runtime-Daten
- [ ] automatische Code-/Balance-Mutation ohne Review

---

# 12. 📍 NEXT BEST ACTION

## 🟢 Empfohlen

**Echten UE-5.8-CP1-Lauf auf der Zielmaschine ausführen.**

### Warum?

- Nutzen: **10/10**
- Erkenntnisgewinn: **10/10**
- zusätzliche Infrastruktur nötig: **gering**
- blockiert nächsten Gameplay-Slice: **ja**

### Direkt danach

Wenn CP1 GREEN:

```text
Interaction
→ erster Task
→ Ability-Effekt
→ XP
```

Wenn CP1 RED:

```text
ersten echten Fehler isolieren
→ kleinste Reparatur
→ Regressionstest
→ vollständigen CP1-Lauf wiederholen
```

---

# 13. ✅ TODO-PFLEGEREGELN

Bei jeder Entwicklungsiteration:

1. **CURRENT TRUTH** zuerst aktualisieren.
2. Nur tatsächlich bewiesene Punkte abhaken.
3. Blockierte Punkte gelb lassen, nicht grün umdeuten.
4. `NEXT BEST ACTION` auf genau einen Hauptengpass begrenzen.
5. Neue Aufgaben einer Priorität und einem Gate zuordnen.
6. Abhängigkeiten sichtbar machen.
7. Erledigte technische Arbeiten mit Test/Evidence verknüpfen.
8. README, ANLEITUNG und PROJEKTSTATUS synchron halten, wenn sich Bedienung oder Status ändert.
9. Große neue Ideen in den passenden späteren Bereich einordnen statt den aktiven P0-Pfad zu verwässern.
