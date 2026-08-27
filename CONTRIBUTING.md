# Contributing — BUNKER BEATS

## Schnellster sicherer Ablauf
1. Issue oder klaren P0/P1-Auftrag wählen.
2. Branch vom aktuellen `main` erstellen.
3. Kleinste Änderung am Ursprung des Problems umsetzen.
4. `python3 Scripts/ci_verify.py` ausführen.
5. Bei UE-Runtime-Änderungen zusätzlich den CP1-Runner auf einer UE-5.8-Maschine ausführen.
6. PR mit Evidence, Risiko und Rollback öffnen.
7. Nur grün/erklärt blockiert mergen.

## Branch-Namen
- `fix/...` Fehler
- `feat/...` Gameplay/Feature
- `infra/...` CI/Tooling
- `docs/...` Dokumentation

## Commit-Stil
Kurzer Imperativ mit Scope, z. B. `cp1: export movement telemetry`.

## Lokale Schnellprüfung
```bash
python3 Scripts/ci_verify.py
```

## UE-5.8-Runner
Der Self-hosted Runner benötigt die Labels `self-hosted`, `unreal`, `ue-5.8` und Zugriff auf eine UE-5.8-Installation. Setze im Repository die Variable `UE58_RUNNER_ENABLED=true`, sobald der Runner registriert und getestet ist. Erst dann wird der PR-CP1-Job automatisch ausgeführt.

## Nicht committen
`Saved/`, `Intermediate/`, `Binaries/`, `DerivedDataCache/`, `Diagnostics/`, Python-Caches und lokale IDE-Dateien.
