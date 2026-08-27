# BUNKER BEATS — ANLEITUNG

> **Für Einsteiger:** Diese Anleitung führt vom heruntergeladenen Projekt bis zur ersten gültigen CP1-Prüfung. Du musst nicht wissen, wie Unreal Engine intern funktioniert.

> **Dokumentrolle:** Diese Datei erklärt ausschließlich **wie** das Projekt gestartet, geprüft und bei typischen Problemen behandelt wird. Projektstatus steht in `README.md`, Prioritäten in `Docs/TODO.md`, Entwicklungsregeln in `AGENTS.md`.

---

## 1. Was ist das Ziel?

Der aktuelle technische Meilenstein heißt **CP1**.

CP1 beantwortet nur diese Frage:

> **Kann das Projekt mit Unreal Engine 5.8 wirklich gebaut werden, einen Character erzeugen, ihn bewegen und die Bewegung technisch nachweisen?**

Der Ablauf ist:

```text
Projekt prüfen
   ↓
Unreal Engine 5.8 finden
   ↓
Projekt bauen
   ↓
Character erzeugen
   ↓
Character bewegen
   ↓
Messwerte speichern
   ↓
CP1 bewerten
```

---

## 2. Ampelsystem

| Ampel | Bedeutung | Was tun? |
|:---:|---|---|
| 🟢 | Prüfung bestanden | weiter zum nächsten Schritt |
| 🟡 | noch nicht geprüft / Voraussetzung fehlt | Hinweis lesen und Voraussetzung herstellen |
| 🔴 | echte Prüfung fehlgeschlagen | Fehlertext sichern und Ursache beheben |
| 🔵 | später geplant | jetzt nicht bearbeiten |

> [!IMPORTANT]
> **Gelb ist kein Fehler.** Wenn Unreal Engine 5.8 auf dem Computer nicht vorhanden ist, darf der Runtime-Test nicht grün werden.

---

## 3. Was wird benötigt?

### Für die einfache Projektprüfung

- das BUNKER-BEATS-Projekt
- Python 3

### Für den echten CP1-Lauf zusätzlich

- Unreal Engine **5.8**
- passende C++-Entwicklungswerkzeuge
- ausreichend freier Speicherplatz
- Schreibrechte im Projektordner

---

## 4. Projekt herunterladen

GitHub-Projekt:

```text
provoware/bunkergame
```

Empfohlen ist Git:

```bash
git clone https://github.com/provoware/bunkergame.git
cd bunkergame
```

Wenn du mit einem Arbeitsbranch arbeitest:

```bash
git switch infra/cp1-github-control-plane
```

Alternativ kann das Projekt über GitHub als ZIP geladen und entpackt werden.

---

## 5. Erste Prüfung ohne Unreal Engine

Diese Prüfung verändert das System nicht und startet Unreal nicht.

### Linux

Im Projektordner ein Terminal öffnen und ausführen:

```bash
python3 Scripts/ci_verify.py
```

### Windows

Eingabeaufforderung oder PowerShell im Projektordner öffnen:

```bat
python Scripts\ci_verify.py
```

### Richtiges Ergebnis

Am Ende muss stehen:

```text
CI_VERIFY: PASS
```

### Was wird dabei geprüft?

- wichtige Dateien vorhanden
- Unreal-Projektversion korrekt
- Game- und Editor-Target vorhanden
- Hauptmodul vorhanden
- Python-Dateien syntaktisch gültig
- JSON-/Konfigurationsdateien gültig
- CP1-Testvertrag vollständig
- Fehlerbehandlung vorhanden
- Lern-/Ranking-Logik konsistent
- kein erfundener Runtime-Erfolg

---

## 6. Wenn `CI_VERIFY` nicht PASS meldet

### 🔴 Nicht einfach weitermachen

1. Die letzte Fehlermeldung lesen.
2. Den vollständigen Fehlertext kopieren.
3. Keine Testdatei löschen, nur damit die Prüfung grün wird.
4. Keine Statusdatei manuell auf PASS setzen.
5. Erst die Ursache beheben.
6. `ci_verify.py` erneut ausführen.

Für Entwickler gilt zusätzlich: Der erste fehlschlagende Test ist wichtiger als spätere Folgefehler.

---

# TEIL B — ECHTER CP1-LAUF

## 7. Vor dem Start

Prüfe:

- [ ] Unreal Engine 5.8 ist installiert.
- [ ] Das Projekt liegt lokal auf der Festplatte.
- [ ] Im Projektordner darf geschrieben werden.
- [ ] `python3 Scripts/ci_verify.py` bzw. die Windows-Variante meldet PASS.
- [ ] Keine alte Runtime-Evidence wird als aktueller Test verwendet.

---

## 8. CP1 mit einem Befehl starten

### Linux

```bash
./RUN_CP1_UE58_ALL.sh
```

Falls die Datei noch nicht ausführbar ist:

```bash
chmod +x RUN_CP1_UE58_ALL.sh
./RUN_CP1_UE58_ALL.sh
```

### Windows

Doppelklick auf:

```text
RUN_CP1_UE58_ALL.bat
```

oder in der Eingabeaufforderung:

```bat
RUN_CP1_UE58_ALL.bat
```

---

## 9. Was macht der Runner automatisch?

Der Runner versucht nicht nur, irgendeine Anwendung zu öffnen. Er führt eine definierte Prüfkette aus:

### Schritt 1 — Vorprüfung

Prüft Projekt, Umgebung und benötigte Dateien.

### Schritt 2 — Build

Versucht das UE-5.8-Projekt bzw. Editor-Target wirklich zu kompilieren.

### Schritt 3 — Testwelt

Erzeugt eine kontrollierte temporäre Unreal-Testwelt.

### Schritt 4 — Character Spawn

Erzeugt den Test-Character.

### Schritt 5 — Movement

Gibt kontrollierten Bewegungsinput und lässt die Testwelt weiterlaufen.

### Schritt 6 — Telemetrie

Speichert technische Messwerte:

- Frame-Time
- Startposition
- Endposition
- Positionsänderung
- Velocity
- Speed
- Zustand der Movement Component

### Schritt 7 — CP1 Gate

Entscheidet anhand der echten Evidence, ob CP1 bestanden wurde.

---

## 10. Wo finde ich das Ergebnis?

Lokale Runtime-Ausgaben werden unter folgendem Bereich abgelegt:

```text
Diagnostics/Runtime/
```

Diese Dateien dienen als **Nachweis des konkreten Laufs**.

Sie gehören normalerweise **nicht in einen Git-Commit**, weil sie maschinen- und laufabhängig sind.

---

## 11. Wann ist CP1 wirklich grün?

Alle Punkte müssen erfüllt sein:

- [ ] Unreal Engine 5.8 wurde tatsächlich verwendet.
- [ ] Projekt wurde erfolgreich gebaut.
- [ ] Test wurde tatsächlich gestartet.
- [ ] Character wurde erfolgreich erzeugt.
- [ ] Movement Component ist gültig und aktiv.
- [ ] Character hat sich messbar bewegt.
- [ ] Start- und Endposition sind vorhanden.
- [ ] Velocity wurde erfasst.
- [ ] Frame-Time wurde erfasst.
- [ ] Evidence stammt aus diesem Lauf.
- [ ] CP1 Gate meldet PASS.

Fehlt nur ein notwendiger Punkt, bleibt CP1 **nicht grün**.

---

# TEIL C — GITHUB-AUTOMATION

## 12. Was GitHub automatisch prüft

Bei einem Pull Request läuft der Workflow:

```text
Validate
```

Er prüft den schnellen Teil ohne Unreal Engine.

Der echte Unreal-Lauf heißt:

```text
CP1 UE 5.8 Runtime
```

Dieser benötigt eine eigene Maschine, auf der Unreal Engine 5.8 installiert ist.

---

## 13. Self-hosted Runner für Unreal Engine 5.8

Ein **Self-hosted Runner** bedeutet einfach:

> Dein eigener Rechner führt einen GitHub-Test aus.

Der Runner muss in GitHub mit folgenden Labels registriert sein:

```text
self-hosted
unreal
ue-5.8
```

Danach wird im Repository die Variable gesetzt:

```text
UE58_RUNNER_ENABLED=true
```

Solange das nicht eingerichtet ist, darf der Runtime-Workflow übersprungen werden.

Das ist **BLOCKED**, nicht PASS.

---

## 14. Sicherheitsregel für den eigenen Runner

Der UE-Rechner darf **keinen beliebigen Code fremder Fork-Pull-Requests automatisch ausführen**.

Der Workflow ist deshalb so ausgelegt, dass dieser Fall abgefangen wird.

Vor Änderungen an dieser Regel immer `AGENTS.md` lesen.

---

# TEIL D — FEHLERHILFE

## 15. Unreal Engine wird nicht gefunden

**Ampel:** 🟡 oder 🔴 je nach ausgeführtem Schritt.

Prüfen:

1. Ist wirklich Unreal Engine 5.8 installiert?
2. Stimmt der Installationspfad?
3. Sind die Build-Werkzeuge installiert?
4. Wird die Installation von der Projektkonfiguration erkannt?

Nicht tun:

- Engine-Version im Projekt nur ändern, damit der Fehler verschwindet.
- Runtime-Test manuell als bestanden markieren.

---

## 16. Build schlägt fehl

1. Erste echte Compiler-Fehlermeldung suchen.
2. Nicht nur die letzten Folgefehler betrachten.
3. Fehlertext sichern.
4. Ursache beheben.
5. Schnellprüfung ausführen.
6. Build erneut starten.

Hilfreiche Dokumentation:

- `Docs/ENVIRONMENT_REPAIR_DEBUGGING.md`
- `Docs/TOOLCHAIN_DOCTOR_5.0.2.md`

---

## 17. Character spawnt, bewegt sich aber nicht

Prüfen:

- Movement Component vorhanden?
- Movement Component aktiv?
- Movement Mode gültig?
- Input tatsächlich angewendet?
- Testwelt wird getickt?
- Position vor und nach dem Test unterschiedlich?
- Velocity plausibel?

Genau dafür enthält CP1 die zusätzliche Telemetrie.

---

## 18. Alte Evidence liegt noch im Ordner

Der Runner muss verhindern, dass alte Daten einen neuen Lauf fälschlich bestehen lassen.

Wenn Zweifel bestehen:

1. Lauf abbrechen.
2. `Diagnostics/Runtime/` sichern, wenn der Fehler untersucht werden soll.
3. neuen CP1-Lauf starten.
4. prüfen, ob neue Zeit-/Laufdaten erzeugt wurden.

---

# TEIL E — ENTWICKELN

## 19. Einfacher Entwicklungsablauf

```text
1. Aufgabe auswählen
2. aktuellen Status prüfen
3. kleinste sinnvolle Änderung umsetzen
4. passenden Test ergänzen oder aktualisieren
5. python3 Scripts/ci_verify.py
6. Commit auf Arbeitsbranch
7. Pull Request
8. GitHub Validate prüfen
9. bei Runtime-Änderung echten UE-Test ausführen
10. Evidence prüfen
11. erst dann mergen
```

---

## 20. Was nach CP1 kommt

Nicht gleichzeitig zehn Systeme anfangen.

Der nächste spielbare Pfad ist:

```text
Character
   ↓
Interaction
   ↓
erster Task
   ↓
Ability-Effekt
   ↓
XP
```

Erst wenn dieser Vertikalschnitt technisch funktioniert, werden größere Crowd-, Rivalen-, Event- und Präsentationssysteme wieder P0/P1-relevant.

---

## 21. Die wichtigsten Dateien

| Datei | Für wen? | Zweck |
|---|---|---|
| `README.md` | alle | Projektübersicht und Status |
| `ANLEITUNG.md` | Einsteiger | Start-, Test- und Fehleranleitung |
| `Docs/TODO.md` | Entwickler | priorisierte nächste Arbeiten |
| `AGENTS.md` | Entwickler/KI | verbindliche Arbeitsregeln |
| `CONTRIBUTING.md` | Entwickler | GitHub-Arbeitsweise |
| `Docs/PROJEKTSTATUS.md` | alle | detaillierter Status |
| `Docs/CP1_RUNTIME_EXECUTION.md` | Entwickler | technische CP1-Ausführung |
| `Docs/GAMEPLAY_GUIDE.md` | Design/Gameplay | Spielsystem und Ablauf |

---

## 22. Die wichtigste Regel

> **Nicht behaupten, dass etwas funktioniert — es ausführen, messen und beweisen.**

### Aktueller nächster Schritt

**Auf einer echten UE-5.8-Maschine `RUN_CP1_UE58_ALL` ausführen und die erzeugte Evidence prüfen.**
