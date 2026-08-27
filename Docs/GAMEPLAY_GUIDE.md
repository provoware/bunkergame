# BUNKER BEATS — SPIELANLEITUNG

Version: 0.3.0-concept
Status: Design- und Prototyp-Grundlage

> Diese Anleitung wird bei jeder relevanten Gameplayänderung aktualisiert. Sie unterscheidet zwischen festgelegtem Design und tatsächlich implementierten Funktionen.

---

# 1. Dein Ziel

Du entwickelst deinen eigenen Stil rund um einen verlassenen Bunker.

Du erkundest.
Du erledigst Aufgaben.
Du entwickelst deine Skills.
Du wählst Spezialfähigkeiten.
Du baust dein Event.
Die Crowd reagiert.
Rivalen versuchen, besser zu sein.

Der entscheidende Punkt:

**Dein Weg soll nicht genauso aussehen wie der Weg eines anderen Spielers.**

---

# 2. Pppoppi oder Atze?

## Pppoppi Poppsen von Bückstücken

Pppoppi ist der Improvisierer.

Zwischeninfo:
Er nennt Fehler „ungeplante Features“.

## Atze

Atze ist der Wettkämpfer.

Zwischeninfo:
Er nennt Niederlagen „vorläufige Beweisprobleme“.

### Wichtig

Beide beginnen mit denselben Skills:

TECH 1
CREATIVE 1
SOCIAL 1
PERFORMANCE 1

Es gibt keinen versteckten Startbonus.

---

# 3. Deine zwei Spezialfähigkeiten

Du wählst **genau 2 aus 20 Fähigkeiten**.

Die Wahl ist wichtig.

Eine Fähigkeit kann zum Beispiel:
- eine zusätzliche Aktion eröffnen
- Informationen liefern
- einen Fehler abfangen
- Crowd-Verhalten sichtbarer machen
- einen Rivalen beeinflussen
- Exploration verändern
- Eventaufbau verändern
- Risiko erhöhen
- einen Comeback-Versuch erlauben.

Du wählst damit einen Spielstil.

---

# 4. Die 20 Fähigkeiten

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

Die endgültige Wirkung einer Fähigkeit gilt im Spiel erst nach Runtime-Implementierung als aktiv.

---

# 5. Beispiel

### Pppoppi

Improvisationskönig + Trash-Magnet

Spielidee:
Fehler in neue Möglichkeiten umwandeln und ungewöhnliche Orte entdecken.

### Atze

Bass-Geflüster + Crowd-Bait

Spielidee:
Crowd besser einschätzen und bewusst Publikumsspitzen erzeugen.

Diese Kombinationen sind Beispiele, keine vorgeschriebenen Builds.

---

# 6. Skills

Vier Hauptgruppen:

TECH
CREATIVE
SOCIAL
PERFORMANCE

Start:
1

Prototyp-Ziel:
Level 1–5

Skills wachsen durch Handlungen und Training, nicht nur durch Menü-Käufe.

---

# 7. Aufgaben

Typische geplante Aufgaben:

- untersuchen
- tragen
- installieren
- reparieren
- konfigurieren
- vorbereiten.

Jede Aufgabe soll zeigen:
- was du tun musst
- ob es geht
- warum es nicht geht
- was danach passiert.

---

# 8. Dein Event

Du kombinierst:

Musik
+
Raum
+
Bühne
+
Licht
+
Atmosphäre
+
Performance

Dadurch entsteht dein Eventkonzept.

Mehrere Kombinationen sollen erfolgreich funktionieren.

---

# 9. Die Crowd

Geplante Crowdgruppen:

Basshead
Dancer
Visual Seeker
Underground Purist
Social Follower

Sie haben unterschiedliche Vorlieben.

Eine Gruppe kann dein Event lieben, während eine andere enttäuscht ist.

---

# 10. Was die Crowd macht

Die Crowd kann sich entwickeln:

ANKOMMEN
→ AUFWÄRMEN
→ ENGAGIERT
→ HYPED

oder:

ANKOMMEN
→ GELANGWEILT
→ GEHEN.

Damit wird sichtbar, ob dein Konzept funktioniert.

---

# 11. Rivalen

Rivalen spielen nicht einfach deine Strategie nach.

Sie haben:
- Ziele
- Skills
- Vorlieben
- Risiken
- eigene Entscheidungen.

Ein Rivale kann deshalb mit weniger Ressourcen trotzdem gewinnen, wenn sein Konzept besser zu seiner Strategie passt.

---

# 12. Geheimnisse

Versteckte Orte sollen nicht nur Sammelobjekte sein.

Sie können:
- neue Möglichkeiten
- Storyinformationen
- alternative Wege
- besondere Eventoptionen
- Fortschritt

geben.

---

# 13. Wichtiger Hinweis zum Prototyp

Viele der hier beschriebenen Systeme befinden sich aktuell noch im Designstadium.

Nicht alles ist bereits als spielbare Funktion vorhanden.

Aktueller Status:

Technical Boot: noch nicht validiert
3D-Bewegung: noch nicht validiert
Event: noch nicht validiert
Crowd: noch nicht validiert
Rivalen: noch nicht validiert
Auto Playtester: noch nicht validiert.

---

# 14. Auto-Testspieler

Später wird ein automatischer Testspieler verschiedene Wege ausprobieren.

Er bekommt reproduzierbare Szenarien und Seeds.

Er soll feststellen:
- ob Aufgaben lösbar sind
- ob Fähigkeiten wirken
- ob Events abgeschlossen werden
- ob Crowd reagiert
- ob Rivalen funktionieren
- ob Fehler reproduzierbar sind.

---

# 15. Wie du das Spiel „richtig“ spielst

Es gibt zunächst keine vorgeschriebene perfekte Strategie.

Das Ziel des Designs ist:

**Entscheiden → Konsequenz erleben → daraus lernen → nächsten Versuch anders spielen.**

---

# 16. Dokumentationsstand

Diese Anleitung wird gemeinsam mit dem Spiel weiterentwickelt.

Neue oder geänderte Gameplay-Regeln müssen hier nachvollziehbar ergänzt werden.

## 17. Spielstart / automatische Diagnose

Beim Start soll die Projekt-Routine zunächst die Entwicklungsumgebung prüfen.

Ampel:
- GRÜN = Voraussetzungen vorhanden und Stufe ausgeführt
- GELB = Teilzustand oder manuelle Voraussetzung
- ROT = kritischer Blocker oder ausgeführter Fehler

Die Startdiagnose erzeugt einen verständlichen Bericht. Ein nicht ausgeführter Unreal-Runtime-Test wird niemals als bestanden angezeigt.

## 18. Technische Diagnose

Für normale Spieler bleibt Debugging im Hintergrund.

Bei Problemen kann die Start-/Testumgebung einen verständlichen Diagnosebericht erzeugen. Die Diagnose unterscheidet zwischen:
- Problem erkannt
- automatischer Reparatur möglich
- manuelle Aktion erforderlich
- Test blockiert
- Test fehlgeschlagen.

Technische Diagnose-Dateien werden getrennt von den eigentlichen Spieldaten abgelegt.

## 19. Test- und Qualitätsstatus

Interne automatische Tests können feststellen, ob sich ein bereits funktionierender Ablauf verschlechtert hat.

Das ist kein Teil des normalen Spiels. Die Ergebnisse dienen der Entwicklung und Qualitätssicherung.

## 20. Qualitätsstatus

Automatische Regressionstests gehören zur internen Entwicklung und beeinflussen das normale Spielerlebnis nicht.
Wenn ein Entwicklungsstand schlechter als eine gültige Baseline wird, wird die Änderung zunächst untersucht, bevor weitere Optimierungen oder Content-Erweiterungen darauf aufbauen.

## 21. Qualitätsprüfung
Die Entwicklungs-Pipeline prüft intern Start, Tests und Regressionen. Das betrifft nicht den normalen Spielablauf.

## 23. Interne Pipeline
Die Entwicklungsroutine arbeitet intern mit voneinander getrennten Prüfungen. Ein unvollständiger Nachweis wird nicht als erfolgreicher Build gewertet.

## 25. Charakterlaufzeit
Die Charakteroberfläche verbindet die Eingaben des Spiels mit den zentralen Spielregeln. Gültige Charakterentscheidungen werden nicht von der Oberfläche allein bestimmt.

## 29. Spezialfähigkeiten wirken
Gewählte Spezialfähigkeiten können Aufgaben beschleunigen, absichern oder riskanter machen. Die Prototypeffekte werden während der Entwicklung weiter getestet.

## 34. Entwicklerdiagnose
Der Environment Doctor erklärt Startprobleme in einfacher Sprache und dokumentiert technische Details separat für Entwickler.
