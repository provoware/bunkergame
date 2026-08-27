# AGENTS.md — BUNKER BEATS REPOSITORY CONTROL PLANE

> Diese Datei definiert die **verbindlichen Arbeitsregeln** für Menschen, KI-Agenten, Automatisierungen und Code-Assistenten im Repository.

---

# 1. AUTHORITY ORDER

Bei Widersprüchen gilt diese Reihenfolge:

1. **Sicherheits-, Evidence- und Gate-Regeln dieser Root-`AGENTS.md`**
2. `Docs/AGENTS.md` für Gameplay-, Architektur- und Projektdetails
3. konkrete Issue-/PR-Anforderung
4. lokale Implementierungsentscheidung

Eine niedrigere Ebene darf den Scope enger machen, aber niemals:

- Evidence-Anforderungen abschwächen,
- Tests umgehen,
- Sicherheitsgrenzen entfernen,
- einen unbeobachteten Runtime-Zustand zu PASS erklären.

---

# 2. MISSION

Die Entwicklungsarbeit soll nicht möglichst viel Code erzeugen, sondern **den nächsten belegbaren Engpass mit minimalem Risiko schließen**.

Aktuelle Hauptreihenfolge:

```text
CP1 Runtime
   ↓
Interaction
   ↓
erster Task
   ↓
Ability-Effekt
   ↓
XP
```

Crowd, Rival, Event, große Präsentationsarbeit oder zusätzliche Systeme werden nicht vorgezogen, solange sie keine echte Abhängigkeit dieses Pfades sind.

---

# 3. FIRST 90 SECONDS — VOR JEDER ÄNDERUNG

Jeder Agent prüft zuerst:

1. `README.md`
2. `Docs/TODO.md`
3. diese `AGENTS.md`
4. relevante Detaildokumente
5. betroffene Tests
6. aktuellen Git-/PR-Status

Danach muss intern klar sein:

- Was ist der **aktuelle belegte Zustand**?
- Was ist der **eine konkrete Engpass**?
- Welche Dateien sind wirklich betroffen?
- Welcher Test beweist die Änderung?
- Welche Evidence darf danach entstehen?
- Welche Dokumente müssen synchronisiert werden?

Nicht mit Code beginnen, wenn diese Fragen nicht beantwortbar sind.

---

# 4. NON-NEGOTIABLE WORKFLOW

Verbindlicher Ablauf:

```text
Observe
→ Reproduce
→ Classify
→ Find source
→ Smallest safe change
→ Local validation
→ Regression check
→ Evidence
→ Documentation sync
→ Commit
→ Pull Request
→ CI
→ Runtime gate if required
→ Review
→ Merge
```

### Bedeutungen

**Observe**  
Aktuellen Zustand lesen statt vermuten.

**Reproduce**  
Fehler nach Möglichkeit reproduzieren. Nicht aus Fehlermeldungen allein eine Ursache erfinden.

**Classify**  
Fehlerklasse, Priorität, Gate und betroffene Schicht bestimmen.

**Find source**  
Ersten echten Fehler suchen, nicht nur Folgefehler behandeln.

**Smallest safe change**  
Kleinste Änderung mit vollständigem Nutzen bevorzugen.

**Regression check**  
Sicherstellen, dass bestehende Funktionen nicht still beschädigt werden.

---

# 5. EVIDENCE STATE MACHINE

Erlaubte Zustände:

| Zustand | Bedeutung |
|---|---|
| `PLANNED` | vorgesehen, noch nicht implementiert |
| `IMPLEMENTED` | Code vorhanden, aber nicht ausreichend bewiesen |
| `UNOBSERVED` | Test existiert, wurde aber nicht ausgeführt |
| `BLOCKED` | Test kann wegen externer Voraussetzung nicht ausgeführt werden |
| `PASS` | passende Prüfung tatsächlich erfolgreich ausgeführt |
| `FAIL` | passende Prüfung tatsächlich ausgeführt und fehlgeschlagen |

### Verbotene Abkürzungen

```text
IMPLEMENTED ≠ PASS
STATIC_PASS ≠ RUNTIME_PASS
NO_RUN ≠ PASS
SKIPPED ≠ PASS
BLOCKED ≠ PASS
```

Ein Agent darf einen Status nur verbessern, wenn neue Evidence das rechtfertigt.

---

# 6. RUNTIME-EVIDENCE RULE

**Unreal-Runtime-Verhalten darf niemals aus statischer Inspektion als PASS markiert werden.**

Für Runtime-Claims ist maschinell erzeugte Evidence aus Unreal Engine 5.8 erforderlich.

Wenn keine passende UE-5.8-Maschine verfügbar ist:

```text
Status = BLOCKED oder UNOBSERVED
```

niemals:

```text
Status = PASS
```

### Freshness

Veraltete Evidence darf keinen neuen Gate-Lauf bestehen lassen.

Vor einem Runtime-Test muss alte für den Gate relevante Evidence:

- gelöscht,
- eindeutig versioniert,
- oder durch Run-ID/Zeitstempel sicher vom aktuellen Lauf getrennt werden.

---

# 7. CP1 ACCEPTANCE CONTRACT

CP1 ist nur GREEN, wenn **alle** folgenden Aussagen aus demselben gültigen Lauf bewiesen sind:

- [ ] Projekt wurde mit UE 5.8 gebaut.
- [ ] Editor-/Test-Target ist erfolgreich.
- [ ] CP1-Test wurde tatsächlich ausgeführt.
- [ ] Test-Character wurde erzeugt.
- [ ] `CharacterMovementComponent` ist vorhanden.
- [ ] Movement Component ist aktiv/verwendbar.
- [ ] Bewegungsinput wurde angewendet.
- [ ] Testwelt wurde kontrolliert weitergetickt.
- [ ] messbares Displacement wurde erzeugt.
- [ ] Startposition ist dokumentiert.
- [ ] Endposition ist dokumentiert.
- [ ] Velocity ist dokumentiert.
- [ ] Speed ist dokumentiert.
- [ ] Frame-Time ist dokumentiert.
- [ ] Evidence ist frisch und dem Run eindeutig zugeordnet.
- [ ] CP1-Gate meldet PASS.

Fehlt ein notwendiger Punkt, bleibt CP1 nicht grün.

---

# 8. TEST POLICY

## 8.1 Vor einer Änderung

Bestehende relevante Tests identifizieren.

## 8.2 Während der Änderung

Bei Bugfixes bevorzugt zuerst einen reproduzierenden Test bzw. Contract ergänzen.

## 8.3 Nach der Änderung

Mindestens ausführen:

```bash
python3 Scripts/ci_verify.py
```

Bei Runtime-relevanten Änderungen zusätzlich den passenden UE-Test.

## 8.4 Nicht erlaubt

- fehlschlagenden Test löschen, um GREEN zu erhalten
- Assertion abschwächen ohne belegten Grund
- Timeout künstlich erhöhen, ohne Ursache zu untersuchen
- Evidence-Datei manuell so verändern, dass ein Gate besteht
- Runtime-Test durch statischen Mock ersetzen und anschließend denselben Evidence-Status verwenden
- bekannte Regression als „Flaky“ deklarieren ohne Nachweis

---

# 9. CHANGE CLASSES

Jede Änderung gehört mindestens einer Klasse an.

## P0 — Gate / Integrität / Sicherheit

Beispiele:

- Build blockiert
- Evidence falsch
- Gate unzuverlässig
- Datenverlust
- Self-hosted-Runner-Sicherheitsproblem

**Regel:** kleinster möglicher Scope, höchste Prüfstrenge.

## P1 — aktueller Gameplay-Pfad

Beispiele:

- Interaction
- erster Task
- Ability-Effekt
- XP

## P2 — Architektur / Wartbarkeit

Nur priorisieren, wenn:

- aktueller P0/P1-Pfad davon profitiert,
- konkretes Risiko reduziert wird,
- oder wiederholte Fehler dadurch entfallen.

## P3+ — spätere Erweiterungen

Nicht in aktive P0/P1-PRs mischen.

---

# 10. CHANGE BUDGET

Ein Pull Request soll **eine logische Veränderung** enthalten.

### Bevorzugt

```text
1 Ursache
→ 1 Fix
→ passende Tests
→ passende Doku
```

### Vermeiden

```text
Bugfix
+ großer Refactor
+ Gameplay-Feature
+ Formatierungswelle
+ neue Architekturidee
```

Refactors werden getrennt, außer sie sind für die Korrektheit zwingend erforderlich.

---

# 11. FILE HYGIENE

Nicht committen:

```text
Saved/
Intermediate/
Binaries/
DerivedDataCache/
Diagnostics/
__pycache__/
*.pyc
```

Laufzeitdaten, temporäre Reports und lokale Debugdateien bleiben lokal oder werden als CI-Artefakte gespeichert.

Keine großen Binärdateien hinzufügen, wenn kein bewusstes Asset-/LFS-Konzept existiert.

---

# 12. VERSIONING / MANIFEST RULE

Bei Änderungen an Projektstruktur, Runtime-Vertrag oder Release-relevantem Verhalten prüfen:

- `RELEASE_MANIFEST.json`
- relevante Config-/Schema-Version
- `Docs/CHANGELOG.md`
- Statusdokumente

Versionsangaben dürfen nicht widersprüchlich in mehreren Dateien unabhängig gepflegt werden, wenn eine kanonische Quelle möglich ist.

Neue Schemas brauchen:

- Versionsfeld
- Rückwärtskompatibilitätsentscheidung
- Migration oder bewusst dokumentierten Bruch
- Regressionstest

---

# 13. DOCUMENTATION SYNC MATRIX

| Änderung | Pflichtdokumente prüfen |
|---|---|
| Bedienung / Start | `README.md`, `ANLEITUNG.md` |
| Priorität / Roadmap | `Docs/TODO.md`, ggf. `Docs/PROJEKTSTATUS.md` |
| Runtime-/Gate-Verhalten | README, TODO, Runtime-Doku, AGENTS |
| Gameplay-Regel sichtbar geändert | `Docs/GAMEPLAY_GUIDE.md` |
| Entwicklerprozess geändert | `AGENTS.md`, `CONTRIBUTING.md` |
| Release-/Version geändert | Manifest, CHANGELOG, Status |

### Zuständigkeit der vier Kerndokumente

- `README.md` = **Was ist das Projekt und wo steht es?**
- `ANLEITUNG.md` = **Wie starte, prüfe und repariere ich es als Einsteiger?**
- `Docs/TODO.md` = **Was ist als Nächstes zu tun und warum?**
- `AGENTS.md` = **Nach welchen Regeln darf entwickelt und bewertet werden?**

Diese Verantwortungen nicht vermischen. Detailwissen gehört in `Docs/`, der schnelle Einstieg bleibt im Root.

Ein Agent darf eine technische Änderung nicht als vollständig erklären, wenn die dadurch falsch gewordene Doku ungeändert bleibt.

---

# 14. TODO DISCIPLINE

`Docs/TODO.md` ist kein Ideenspeicher ohne Reihenfolge, sondern das aktive Steuerungsboard.

Regeln:

1. `CURRENT TRUTH` zuerst korrekt halten.
2. Nur bewiesene Punkte abhaken.
3. Genau einen **NEXT BEST ACTION** als Hauptengpass führen.
4. Neue Aufgaben einem Gate und einer Priorität zuordnen.
5. Abhängigkeiten sichtbar machen.
6. Große Ideen in spätere Bereiche verschieben, wenn sie P0/P1 nicht helfen.
7. Kein Feature allein wegen Attraktivität vorziehen.

---

# 15. GITHUB WORKFLOW

## Branches

- nie direkt auf `main` entwickeln
- pro logischer Änderung eigener Branch
- Branchname beschreibt Zweck

Beispiele:

```text
fix/cp1-movement-evidence
feat/interaction-core
infra/ue58-runner-gate
```

## Pull Request muss enthalten

- Ziel
- Scope
- was bewusst nicht geändert wurde
- Tests / Evidence
- Runtime-Status
- Risiko
- Rollback
- nächstes Gate

## Merge

Bevorzugt **Squash Merge** für einen logischen Änderungssatz.

Nicht mergen, wenn:

- erforderliche CI rot ist
- Evidence fehlt
- Runtime-PASS behauptet wird, aber Runtime nicht lief
- offene P0-Regression existiert
- PR mehrere unabhängige Themen unkontrolliert vermischt

---

# 16. SELF-HOSTED RUNNER SECURITY

Ein Self-hosted Unreal-Runner ist ein echter Rechner mit lokal installierter Software und darf nicht wie ein beliebiger Hosted Runner behandelt werden.

### Verbindlich

- fremde Fork-PRs nicht automatisch ausführen
- minimale Token-Rechte
- keine Secrets in Logs
- keine unnötigen persistenten Zugangsdaten
- Workspace nach vertrauensunwürdigen Läufen bereinigen
- Runtime-Workflow nicht so verändern, dass Sicherheitsbedingungen still entfallen

Eine Änderung an Runner-Sicherheitsbedingungen ist mindestens **P0 Security**.

---

# 17. FAILURE HANDLING

Bei einem Fehler:

```text
erste echte Fehlermeldung
→ Fehlerklasse
→ betroffene Schicht
→ reproduzierbarer Minimalfall
→ kleinste Reparatur
→ Regressionstest
→ erneuter vollständiger Gate-Lauf
```

### Kein Shotgun Debugging

Nicht fünf unabhängige Reparaturen gleichzeitig anwenden.

Sonst ist nicht mehr beweisbar, welche Änderung den Fehler gelöst oder einen neuen erzeugt hat.

---

# 18. LEARNING / SELF-REPAIR POLICY

Das Projekt darf aus erfolgreichen und fehlgeschlagenen Reparaturen lernen.

Eine gelernte Regel muss Kontext besitzen, z. B.:

- Betriebssystem
- Unreal-Version
- Toolchain-Version
- Fehlercode
- Reparatur-ID
- Ergebnis
- Anzahl Versuche
- Erfolgsquote
- Zeitpunkt

### Promotion

Eine Reparatur darf nur höher priorisiert werden, wenn echte Ergebnisse dies stützen.

### Verboten

Self-Repair darf niemals:

- Tests abschwächen
- Gate-Schwellen heimlich verändern
- Evidence erzeugen, ohne den Test auszuführen
- unbekannte Systemänderungen ohne Protokoll durchführen

---

# 19. AUTONOMOUS AGENT RULES

Ein autonom arbeitender Agent darf ohne Rückfrage:

- relevante Dateien lesen
- bestehenden Status analysieren
- Tests ausführen
- kleine sichere Änderungen auf Arbeitsbranch vornehmen
- Dokumentation synchronisieren
- PR-Evidence sammeln

Ein Agent muss besonders vorsichtig sein bei:

- Löschen von Daten
- Änderung von Secrets / Zugangsdaten
- Runner-Sicherheitsregeln
- Branch-Protection
- Release/Deployment
- automatischen Systemreparaturen außerhalb des Projektordners

Keine Erfolgsbehauptung aus Tool-Absicht ableiten. Nur tatsächlich bestätigte Tool-Ergebnisse zählen.

---

# 20. ARCHITECTURE RULE

Headless-/Regellogik und Unreal-Darstellung sollen nicht unnötig doppelte Wahrheiten erzeugen.

Bevorzugtes Modell:

```text
Definition
→ Runtime State
→ Persistence State
→ Presentation State
```

Unreal soll vorhandene Regeln ausführen/darstellen und nicht unbemerkt parallele Regelwerke schaffen.

Neue Gameplay-Regeln brauchen möglichst:

- stabile ID
- deklarative Definition
- zentrale Validierung
- deterministischen Testpfad
- Runtime-Adapter
- nachvollziehbare Evidence

---

# 21. AFTER CP1

Wenn CP1 GREEN ist, lautet der nächste verbindliche Vertikalschnitt:

```text
Character
→ Interaction
→ erster Task
→ Ability-Effekt
→ XP
```

### Nicht vorher aufblasen

- Crowd-Runtime
- Rivalen-Runtime
- Event-Komplexität
- große Animation-/Grafikpolitur
- Multiplayer

Ausnahme: echte technische Abhängigkeit des Vertikalschnitts.

---

# 22. DEFINITION OF DONE

Eine Änderung ist erst **DONE**, wenn alle zutreffenden Punkte erfüllt sind:

- [ ] Ziel eindeutig
- [ ] Scope minimal und nachvollziehbar
- [ ] Ursache statt Symptom behandelt
- [ ] relevante Tests vorhanden
- [ ] lokale Validierung bestanden
- [ ] Regressionen geprüft
- [ ] Runtime-Evidence vorhanden, falls Runtime-Claim
- [ ] kein Fake-/stale-Evidence-Pfad
- [ ] Dokumentation synchron
- [ ] TODO-Status korrekt
- [ ] PR beschreibt Risiko und Rollback
- [ ] CI passend zum Scope grün
- [ ] nächstes Gate eindeutig

---

# 23. FINAL RULE

> **Nicht beweisen, dass der Code plausibel aussieht. Beweisen, dass der relevante Zustand tatsächlich funktioniert.**

Aktueller P0 bleibt daher: **echter UE-5.8-CP1-Lauf → Build → Character Spawn → Movement → Telemetrie → Gate.**
