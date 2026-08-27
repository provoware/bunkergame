# Environment Repair / Debugging

## Aufgaben

Diagnose → sichere Reparatur → erneute Diagnose → Gate → Report → Regressionserkenntnis.

## Sichere automatische Reparatur

Automatisch erlaubt sind nur deterministische, lokale und nicht-destruktive Korrekturen aus bekannten Projektquellen.

Nicht automatisch:
- Unreal Engine Installation
- systemweite SDK-/Compilerinstallation
- sudo/root
- unbekannte Downloads
- Löschen nicht regenerierbarer Nutzerdaten.

## Ereignisse

Jedes Ereignis enthält:
event_id, timestamp, run_id, code, severity, phase, title, message, cause, action, status und detail.

Speicher:
`Diagnostics/Events/events.jsonl`

Run-Reports:
`Diagnostics/Launcher/`

Regression:
`Diagnostics/Regression/knowledge.jsonl`
und
`Diagnostics/Regression/REGRESSION_INSIGHTS.md`

## Feedback

GREEN: Alles bereit.
YELLOW: Das Projekt ist teilweise bereit; eine Voraussetzung fehlt.
RED: Ein kritischer Fehler verhindert den angeforderten Schritt.

## Debugging-Regel

Ein Prozess-Exitcode ist keine Gameplay-Erfolgsgarantie. Domain-/Gate-Ergebnis und reine Prozessausführung werden getrennt protokolliert.
