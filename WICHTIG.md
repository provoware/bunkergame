# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-012 — Startroutine gegen unvollständige Diagnose-Payloads absichern

**Kategorie:** Launcher / GUI / Vorprüfung-Nachvalidierung / Fail-Safe UX  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — Hosted-CI-Abnahme dieser Iteration steht noch aus  
**Nutzen:** 10/10  
**Aufwand:** 4/10  
**Risiko der Umsetzung:** 2/10

### Beobachtung

Beim realen Start über `START_BUNKER_BEATS_INTELLIGENT.sh` trat nach erfolgreicher Grunddiagnose ein Tkinter-Callback-Absturz auf:

```text
KeyError: 'after'
```

Die GUI griff direkt auf `payload["summary"]["after"]` zu. Der Core `EnvironmentAssistant.run()` erzeugte jedoch bis dahin überhaupt kein Feld `after`. Dadurch bestand ein widersprüchlicher interner Vertrag: Die Oberfläche erwartete eine Nachvalidierung, die Datenquelle nicht bereitstellte.

Zusätzlich konnte jede unerwartete Worker- oder Darstellungs-Ausnahme den periodischen Tkinter-Polling-Callback beenden. Das erzeugt für Laien den Eindruck eines eingefrorenen oder defekten Tools.

### Verbesserungsvorschlag

Die Startroutine auf einen expliziten, versionierten und defensiv auswertbaren Ablauf umstellen:

```text
Vorprüfung
→ optional sichere Reparatur
→ vollständige Nachvalidierung
→ versionierter Summary-Contract
→ defensive GUI-Normalisierung
→ Status/Ampel
```

Keine GUI-Komponente darf ungeprüft voraussetzen, dass ein einzelnes Payload-Feld existiert. Fehlende, alte oder teilweise Ergebnisdaten müssen als verständlicher Diagnosezustand erscheinen und dürfen niemals den Tkinter-Callback abbrechen.

### Grund

Eine laienoptimierte Startroutine muss gerade bei Fehlern stabiler sein als der zu prüfende Zustand. Ein Diagnosewerkzeug, das durch ein fehlendes Diagnosefeld selbst abstürzt, verletzt das Fail-Safe-Prinzip und verhindert die eigentliche Fehlerbehandlung.

Vorprüfung und Nachvalidierung müssen außerdem **im Datenmodell selbst** vorhanden sein. Nur Textmeldungen wie „ich prüfe vorher/nachher“ reichen nicht als technischer Nachweis.

### Umgesetzt

- `Launcher/core/environment_contract.py` als zentrale reine Vertragslogik ergänzt.
- Summary-Schema auf Version 2 gesetzt.
- `EnvironmentAssistant.run()` liefert jetzt immer explizit `before` und `after`.
- Findings werden in ein stabiles JSON-fähiges Format normalisiert.
- Gesamtstatus wird aus der Nachvalidierung bestimmt.
- `repair_requested` dokumentiert, ob der Reparaturpfad angefordert wurde.
- GUI bevorzugt `after`, akzeptiert aber Legacy-Tupel und fällt kontrolliert auf `before` oder `issues` zurück.
- fehlende `summary`-, `before`- oder `after`-Daten erzeugen verständliche Warnungen statt `KeyError`.
- Worker-Ausnahmen werden in die GUI-Queue übertragen und als roter Startfehler angezeigt.
- einzelne fehlerhafte GUI-Ereignisse können den Polling-Callback nicht mehr dauerhaft beenden.
- parallele Mehrfachstarts über die beiden GUI-Schaltflächen werden während eines laufenden Jobs blockiert.
- Buttons werden nach Ergebnis oder Fehler wieder freigegeben.
- `diagnostics.py` und `regression_knowledge.py` erzeugen ihre `Diagnostics`-Ordner nicht mehr beim bloßen Import, sondern erst beim tatsächlichen Schreiben.
- `Scripts/tests/test_environment_gui_contract.py` deckt aktuelle Payloads, Legacy-Payloads, fehlende Nachvalidierung, fehlende Summary, ungültige Einträge, Statusableitung sowie explizite Vor-/Nachvalidierung des Assistants ab.
- Contract, GUI und Regressionstest wurden in den Repository Quality Guard als Pflichtdateien aufgenommen.

### Wirkung

- realer `KeyError: 'after'` wird strukturell verhindert
- Vorprüfung und Nachvalidierung sind jetzt technisch belegbare Datenphasen
- alte oder teilweise Payloads bleiben darstellbar
- GUI bleibt auch bei Worker-/Darstellungsfehlern bedienbar
- kein stiller Tkinter-Polling-Abbruch mehr durch ein einzelnes Event
- bessere Laienführung bei unvollständigen Ergebnissen
- weniger versteckte Dateisystemänderungen beim Import
- stabilere Packaging-/Testreihenfolge durch weniger Import-Seiteneffekte
- Regressionserkennung schützt den konkreten Produktionsfehler dauerhaft

### Technischer Effekt

```text
EnvironmentAssistant
→ scan() = before
→ safe_repair() optional
→ scan() = after
→ environment_contract schema v2
→ normalize_result_payload()
→ GUI zeigt bevorzugt after

Fehlerfall:
Worker exception / alte Payload / fehlendes Feld
→ Queue / Contract-Normalisierung
→ verständlicher RED-/WARNING-Zustand
→ Tkinter poll läuft weiter
```

### Aktueller belegter Zustand

- Fehlerursache anhand des ausgelieferten `main` reproduzierbar identifiziert
- Core-/GUI-Vertragslücke behoben
- defensive Payload-Normalisierung implementiert
- Import-Seiteneffekte für Diagnose-/Regression-Speicher reduziert
- Regressionstests implementiert
- Repository-Pflichtdateien erweitert
- Hosted-CI-Abnahme des neuen Branches noch offen
- echter UE-5.8-CP1-Runtime-Lauf weiterhin `UNOBSERVED/BLOCKED`

### Fertig, wenn

- `static-and-contract` PASS ist
- `repository-quality` PASS ist
- neue Environment-GUI-Contract-Regressionen PASS sind
- Iteration Guard W-012/CQ-012 akzeptiert
- PR konfliktfrei integriert ist
- anschließend ein neues vollständiges, sauberes Projekt-ZIP aus dem gefixten `main` erzeugt und erneut strukturell validiert wurde
