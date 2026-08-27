# CP1 Runtime Execution — UE 5.8

## Zweck
Dieser Lauf erzeugt den ersten echten Engine-Nachweis für CP1. Statische Tests dürfen diesen Nachweis nicht ersetzen.

## Ablauf
`Repository Preflight → UE Build → temporäre Game-Testwelt → Character Spawn → CharacterMovement → Telemetrie → CP1 Gate`

## Start auf der UE-5.8-Maschine
```bash
./RUN_CP1_UE58_ALL.sh
```

Windows:
```bat
RUN_CP1_UE58_ALL.bat
```

Optional kann `UE_ROOT` auf die Engine-Wurzel zeigen.

## Erforderliche Evidence
- Test wurde gestartet.
- Character wurde real erzeugt.
- `UCharacterMovementComponent` existiert und ist aktiv.
- Position vor/nach Movement ist dokumentiert.
- Velocity und Speed sind dokumentiert.
- Displacement > 0.01 cm.
- Frame-Samples sowie min/avg/max Frame-Time sind dokumentiert.
- Laufzeit-Evidence stammt aus dem aktuellen Lauf; eine alte Telemetriedatei wird vor dem Test gelöscht.
- Automation-Report wurde exportiert.

## Dateien
- `Saved/Automation/CP1_RuntimeTelemetry.json` — direkte UE-Movement-Telemetrie, absichtlich nicht in Git.
- `Diagnostics/Runtime/CP1_runtime_evidence.json` — zusammengefasste Runner-Evidence, absichtlich nicht in Git.

## Statussemantik
- `GREEN`: Build, Runtime-Test und Telemetrie vollständig bestanden.
- `RED`: Build/Test/Evidence technisch fehlgeschlagen.
- `BLOCKED`: UE 5.8 oder Projektvoraussetzung fehlt. BLOCKED ist niemals PASS.

## Testwelt
Der Smoke-Test nutzt UE 5.8 `FTestWorldWrapper`, startet `BeginPlay` in einer temporären `Game`-Welt und tickt diese explizit. Dadurch ist kein bereits geöffneter PIE-Level als versteckte Voraussetzung nötig.

## Buildstrategie
Der Runner baut gezielt `BunkerBeatsEditor` in `Development` über das UE-Batch-Buildskript. Das ist für einen Editor-Automationstest präziser und günstiger als einen vollständigen Cook/Stage/Package-Lauf zu erzwingen.
