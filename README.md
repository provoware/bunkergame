# BUNKER BEATS

**UE 5.8 · Social-Rivalry / Management / Simulation / Progression · provoware**

## Status

| Bereich | Status | Nachweis |
|---|---|---|
| Headless Core | 🟢 validiert | deterministische Tests im Paket |
| Repository/CI | 🟢 vorbereitet | `.github/workflows/validate.yml` |
| UE 5.8 Build | 🟡 ausstehend | benötigt echte UE-5.8-Maschine |
| CP1 Spawn + Movement | 🟡 ausstehend | `cp1-ue58.yml` + Runtime-Evidence |
| CP1 Telemetrie | 🟢 implementiert | Frame-Time, Position, Velocity, MovementComponent |
| Next Vertical Slice | 🔵 geplant | Character → Interaction → Task → Ability → XP |

> **Evidence-Regel:** Unausgeführte Unreal-Tests sind niemals PASS. Ohne echte UE-5.8-Ausführung bleibt CP1 `BLOCKED/AUSSTEHEND`.

## 1-Klick-Entwicklungsfluss

### Ohne Unreal Engine
```bash
python3 Scripts/ci_verify.py
```

### Auf der UE-5.8-Maschine
```bash
./RUN_CP1_UE58_ALL.sh
```

Windows:
```bat
RUN_CP1_UE58_ALL.bat
```

Der Runner führt **Build → Character Spawn → Movement → Telemetrie → CP1 Gate** aus und schreibt maschinenlesbare Evidence unter `Diagnostics/Runtime/`.

## GitHub-Automation
- `Validate`: schneller Python-/JSON-/Contract-Check auf jedem PR.
- `CP1 UE 5.8 Runtime`: echter Runtime-Lauf auf einem Self-hosted UE-5.8-Runner.
- Dependabot hält verwendete GitHub Actions wöchentlich aktuell.
- CODEOWNERS, Issue-Formulare und PR-Template reduzieren manuelle Repo-Arbeit.

## Projektstruktur
- `Source/` Unreal-C++ und CP1-Smoke-Test
- `Launcher/` Diagnose, Repair, Learning und Runtime-Orchestrierung
- `Scripts/` Gates, CI, Runner und Reports
- `Config/` deklarative Policies/Manifeste
- `Tests/` Headless-/Contract-/Quality-Tests
- `Docs/` ausführliche Projekt-, Gameplay- und Entwicklerdokumentation

## Dokumentation
- [Projektregeln](AGENTS.md)
- [Beitragen / GitHub-Workflow](CONTRIBUTING.md)
- [Detail-README](Docs/README.md)
- [Projektstatus](Docs/PROJEKTSTATUS.md)
- [CP1 Runtime](Docs/CP1_RUNTIME_EXECUTION.md)
- [Gameplay Guide](Docs/GAMEPLAY_GUIDE.md)

## Aktueller P0
**Ein echter UE-5.8-Lauf auf der Zielmaschine.** Erst dessen Evidence entscheidet, ob CP1 grün ist.
