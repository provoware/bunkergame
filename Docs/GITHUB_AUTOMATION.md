# GitHub Automation — BUNKER BEATS

## Ziel
GitHub soll Routinearbeit übernehmen, ohne Runtime-Erfolg vorzutäuschen.

## Automatische Ebenen
1. **Validate (GitHub-hosted):** Python-Syntax, JSON, Paketintegrität und CP1-Verträge auf jedem PR.
2. **CP1 UE 5.8 (Self-hosted):** echter Build + Runtime-Smoke + Evidence + Gate.
3. **Dependabot:** wöchentliche Updates verwendeter GitHub Actions.
4. **CODEOWNERS / Templates:** konsistente Reviews, Issues und PR-Evidence.

## Self-hosted UE-5.8-Runner
Der Rechner mit Unreal Engine wird einmalig als GitHub Self-hosted Runner registriert und erhält die Labels:
`self-hosted`, `unreal`, `ue-5.8`.

Danach Repository-Variable setzen:
`UE58_RUNNER_ENABLED=true`

Solange die Variable nicht `true` ist, wird der teure UE-Job bewusst übersprungen, statt PRs endlos auf einen nicht vorhandenen Rechner warten zu lassen.

## Empfohlene Branch-Regel
Für `main` sollten mindestens diese Checks verpflichtend sein:
- `Validate / static-and-contract`
- nach Runner-Aktivierung: `CP1 UE 5.8 Runtime / cp1-runtime` für Runtime-relevante Änderungen

Die aktuelle Connector-Schnittstelle kann Branch-Protection/Rulesets lesen, aber nicht sicher schreiben; diese Repository-Einstellung muss daher einmalig in GitHub aktiviert werden.
