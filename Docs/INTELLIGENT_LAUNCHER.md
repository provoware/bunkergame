# BUNKER BEATS — Intelligent Launcher 3.0

## Purpose

One-click developer launcher with:
- environment detection
- clear green/yellow/red status
- Core QA
- Unreal CP1 path
- full validation path
- human-readable live output
- machine-readable reports
- no-fake-success gate semantics.

## Modes

GUI:
`bash START_BUNKER_BEATS_INTELLIGENT.sh`

Core:
`python3 Launcher/gui/launcher_gui.py`

## Gate semantics

GREEN = requested operation executed and passed.

YELLOW = requested work was blocked or evidence is incomplete.

RED = requested operation executed and failed.

The launcher does not silently install Unreal Engine or mutate unknown project files.

## Safe automatic repair

Only known, deterministic repairs should be automatic.
Unknown or destructive repairs are surfaced to the user.

## Diagnostics

Launcher diagnostics:
`Diagnostics/Launcher/`

Runtime/test evidence:
`Diagnostics/Reports/`

The UI uses simple language; the JSON reports retain precise technical data.

## User feedback examples

Green:
"Alles bereit. Der nächste Schritt kann gestartet werden."

Yellow:
"Das Projekt ist grundsätzlich in Ordnung, aber Unreal 5.8 wurde nicht gefunden."

Red:
"Die angeforderte Prüfung ist fehlgeschlagen. Öffne den Report für die genaue Ursache."

## Future extension points

- dependency repair recipes
- Unreal installation discovery
- SDK/compiler diagnosis
- automatic environment variable setup
- real CP1 Automation report parser
- regression dashboard
- packaged build launch.
