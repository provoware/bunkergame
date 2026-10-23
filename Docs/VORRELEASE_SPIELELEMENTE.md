# BUNKER BEATS — Vorrelease-Pflichtmatrix

**Beobachteter Ausgangsstand:** `main` `43842eb30739a45f3fae1cfa2b7b7c950961e9d8` (21.10.2026).  
**Status:** Kein Vorrelease-Kandidat. **Kein Release.**

## Prüfmodell

Die maschinenlesbare Liste steht in [VORRELEASE_PFLICHTMATRIX.json](VORRELEASE_PFLICHTMATRIX.json). Jede Pflicht besitzt eine stabile ID, einen Bereich, einen Status, eine Quellreferenz und eine nächste Prüfhandlung.

- **PLANNED:** geplant, noch nicht vollständig umgesetzt.
- **IMPLEMENTED:** Code oder Vertrag vorhanden; ein aktueller Funktionsnachweis steht aus.
- **UNOBSERVED:** notwendiger Test wurde noch nicht beobachtet.
- **BLOCKED:** externe Voraussetzung fehlt.
- **FAIL:** tatsächlicher Test fehlgeschlagen.
- **PASS:** passender Test erfolgreich und mit Commit-SHA, Test-ID und GitHub-Lauf verknüpft.

`python3 Scripts/prerelease_gate.py` prüft nur die **Integrität der Pflichtliste**. Das ist ausdrücklich kein Gameplay-PASS. `python3 Scripts/prerelease_gate.py --release-ready` muss bis zur vollständigen Abnahme `BLOCKED` ergeben.

## Konkreter Spielelemente-Katalog

**Figuren:** Pppoppi Poppsen von Bückstücken; Atze. Gleiche Startskills. Unterschiedliche Identität, Dialoge und genau zwei ausgewählte Fähigkeiten.

**20 Fähigkeiten:** 01 Kabelmagnet; 02 Improvisationskönig; 03 Bass-Geflüster; 04 Menschenkenntnis; 05 Trash-Magnet; 06 Deadline-Dämon; 07 Ersatzteil-Orakel; 08 Crowd-Flüsterer; 09 Bühnenbastler; 10 Risiko-Rocker; 11 Notfallknopf; 12 Gerüchteküche; 13 Sound-Sommelier; 14 Bunkerkarte im Kopf; 15 Rivalen-Stichelei; 16 Crowd-Bait; 17 Silent Operator; 18 Charmeoffensive; 19 Fehlerfinder; 20 Letzte-Platte-Prinzip.

**Sechs Interaktionspunkte und Aufgaben:**

| Interaktion | Aufgabe | Nachweis |
|---|---|---|
| `INT_POWER` | `TASK_POWER` | Stromkasten: Start, Fortschritt, Abschluss, Fehler |
| `INT_SETUP` | `TASK_SETUP` | Licht-Rig: Aufbau, Skill, Abschluss |
| `INT_TIMED` | `TASK_TIMED` | Kabelweg: Zeitdruck, Erfolg/Misserfolg |
| `INT_RESOURCE` | `TASK_RESOURCE` | Ersatzteile: Ressourceneffekt |
| `INT_SOCIAL` | `TASK_SOCIAL` | Türpolitik: soziale Entscheidung |
| `INT_RISK` | `TASK_RISK` | Notstrom: Risiko und Belohnung |

Die Definitionen im Headless-Core sind **nicht** mit spielbaren Unreal-Funktionen gleichzusetzen. Jede Fähigkeit und jeder Task benötigt später eigene Runtime- und Balancenachweise. Nach CP1 ist die Reihenfolge **Interaction → erster Task → Ability-Effekt → XP** verbindlich.

## Weitere verpflichtende Gates

**Spiel:** Eventkonfiguration und -ausgang, Crowd-Reaktionen, Rivalen, Geheimnisse, mehrere tragfähige Strategien, deterministische Wiederholung, komplette Spielverläufe und Fehlversuche.

**Daten:** versionierte Spielstände, atomare Speicherung, Roundtrip, Migration, Sicherung, Wiederherstellung und beschädigte Eingaben.

**Bedienung:** 800×600, 175–200 % Skalierung, Tastatur, sichtbarer Fokus, Kontrast, gut lesbare Beschriftungen, keine verdeckten Elemente.

**Technik:** Unreal 5.8 Build/Editor, Character Spawn/Movement/Telemetrie, 60 FPS mit Median/p95, Dauerlauf, Linux/Windows/Offline-Start, automatisierte Negativ- und Regressionstests, vollständiges Release-Paket, Hash und Dokumentation.

## Aktuell bekannte Blockaden

1. GitHub-`main`-Rulesets sind laut Live-Abfrage leer (`[]`); der P0 Observer ist deshalb rot. Keine stillschweigende Änderung von Schutzregeln.
2. Kein nachgewiesener UE-5.8-Runner und kein echter CP1-Lauf. Deshalb **Runtime BLOCKED/UNOBSERVED**, auch wenn statische Tests grün sind.
3. Gameplay, Save/Load, 800×600/200 %, echte Leistungsmessungen und Langzeitpartien bleiben offen.

**Nächster technischer Engpass:** GitHub-Schutz nach gesonderter Freigabe herstellen, UE-5.8-Runner nachweisen und CP1 komplett ausführen. Unabhängige Matrix- und Regressionstests dürfen bereits jetzt weiterlaufen.

**Endabnahme:** Benutzer-Sichtprüfung, persönlicher Kubuntu-Praxistest und Release-Freigabe erst **nach** sämtlichen eigenständig möglichen technischen Prüfungen und eingefrorenem Kandidaten. Keine automatische Veröffentlichung.
