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
- [x] `Quality Guard` vorhanden und erfolgreich gelaufen
- [x] `Iteration Guard` vorhanden und erfolgreich gelaufen
- [x] `Scripts/github_p0_admin.py` als Dry-Run/Apply-Helfer vorhanden
- [x] `Scripts/github_p0_status.py` als read-only Nachprüfer vorhanden
- [x] 20 Spezialfähigkeiten definiert
- [x] 2-aus-20-Regel definiert
- [x] 190 Kombinationen im Headless-Modell abgedeckt
- [x] deterministische Headless-/Regression-Grundlage vorhanden

## 🟡 Vorbereitet, aber noch nicht Runtime-/Admin-bewiesen

- [ ] `main` Branch-Protection auf GitHub wirklich aktivieren
- [ ] `static-and-contract` wirklich als Required Check setzen
- [ ] `repository-quality` wirklich als Required Check setzen
- [ ] UE-5.8 Self-hosted Runner registrieren
- [ ] `runner_readiness.py` auf echter UE-Maschine PASS
- [ ] Repository-Variable `UE58_RUNNER_ENABLED=true` erst danach setzen
- [ ] UE-5.8-Projekt erfolgreich auf Zielmaschine kompilieren
- [ ] Editor-Target erfolgreich kompilieren
- [ ] CP1-Automation in echter UE-5.8-Runtime ausführen
- [ ] Character Spawn mit echter Runtime-Evidence bestätigen
- [ ] messbare Bewegung bestätigen
- [ ] Telemetrie aus echtem Lauf prüfen
- [ ] CP1 Gate auf echte Evidence anwenden

## 🔴 Darf aktuell NICHT als PASS gelten

- [ ] Branch-Schutz aktiv
- [ ] UE-Runner bereit
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

## P0.1 — GitHub `main` wirklich schützen

**Priorität:** P0  
**Nutzen:** 10/10  
**Aufwand:** niedrig  
**Risiko:** niedrig mit Dry-Run/Read-back  
**Blockiert:** verlässlichen Integrationsstand

### Schnellster sicherer Weg

1. `gh auth login` mit Repository-Adminrechten.
2. Nur Vorschau:

```bash
python3 Scripts/github_p0_admin.py
```

3. Anwenden:

```bash
python3 Scripts/github_p0_admin.py --apply
```

4. Unabhängig nachprüfen:

```bash
python3 Scripts/github_p0_status.py
```

### Definition of Done

- [ ] GitHub meldet `main` als geschützt
- [ ] Pull Request Gate aktiv
- [ ] `static-and-contract` required
- [ ] `repository-quality` required
- [ ] Branch muss vor Merge aktuell sein
- [ ] Force-Push gesperrt
- [ ] Branch-Löschen gesperrt
- [ ] `GITHUB_P0_BRANCH_GATE: PASS`

`cp1-runtime` bleibt noch nicht global required.

---

## P0.2 — GitHub Self-hosted UE-5.8-Runner

**Ziel:** CP1 wiederholbar über GitHub ausführen.

- [ ] Self-hosted Runner auf UE-5.8-Maschine installieren
- [ ] Label `self-hosted` prüfen
- [ ] Label `unreal` hinzufügen
- [ ] Label `ue-5.8` hinzufügen
- [ ] UE 5.8 vorhanden
- [ ] C++-Toolchain vorhanden
- [ ] `python3 Scripts/runner_readiness.py` real ausführen
- [ ] `RUNNER_READINESS: PASS`
- [ ] erst danach Repository-Variable `UE58_RUNNER_ENABLED=true` setzen
- [ ] ersten Workflow-Lauf starten
- [ ] Runtime-Evidence-Artifact prüfen
- [ ] Runner-Ausfall als `BLOCKED`, nicht als Gameplay-FAIL behandeln

**Gate:** Erst danach ist CP1 als wiederholbare CI-Prüfung etabliert.

---

## P0.3 — Echter UE-5.8-CP1-Lauf

**Priorität:** P0  
**Nutzen:** 10/10  
**Aufwand:** niedrig bis mittel  
**Risiko:** niedrig, wenn Evidence-Regeln eingehalten werden  
**Blockiert:** gesamten weiteren Runtime-Pfad

### Ziel

Den ersten echten technischen Checkpoint auf einer Maschine mit Unreal Engine 5.8 beweisen.

### Aufgaben

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

# 2. 🟣 DIREKT NACH CP1 — ERSTER SPIELBARER VERTIKALSCHNITT

> **Reihenfolge bleibt verbindlich:** Character → Interaction → erster Task → Ability-Effekt → XP.

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

# 3. 🧭 NEXT BEST ACTION

```text
1. main Branch-Schutz mit github_p0_admin.py --apply real setzen
2. github_p0_status.py muss Branch Gate PASS melden
3. UE-5.8 Self-hosted Runner registrieren
4. runner_readiness.py real PASS
5. UE58_RUNNER_ENABLED=true
6. echten CP1-Lauf ausführen
```

Bis Punkt 1–2 real serverseitig bestätigt sind, bleibt Branch Protection **OFFEN**. Bis Punkt 3–6 real ausgeführt sind, bleibt CP1 **UNOBSERVED/BLOCKED**.
