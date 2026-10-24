# Vorrelease-Nachweis – CP1-Dateideskriptor-Härtung (24.10.2026)

## Ausgangszustand
- Repository: `provoware/bunkergame`, Hauptzweig `main` HEAD `9f2f4db4689291295938bce9e245590eb525bc8c` (vor Iteration beobachtet).
- Gestapelte PR-Basis: [#17](https://github.com/provoware/bunkergame/pull/17), HEAD `c2335035ef91cc4721e40c12c2de14145e40ee0a`.
- Entwicklungs-PR: [#18](https://github.com/provoware/bunkergame/pull/18), **Entwurf**; kein Merge.
- Geprüfter Code-/Doku-HEAD vor diesem Nachweis: `6e56fd6d7648e3e07367c6c525ff17bdb1a36a12`.

## Reproduzierbarer Befund und Korrektur
Vorher: getrennte `is_symlink()`-/`is_file()`-/`stat()`-Vorprüfung und `open()` konnten bei Dateiaustausch auseinanderlaufen. Nachher: `os.open` mit verfügbaren `O_NOFOLLOW`-/`O_NONBLOCK`-Flags, danach `os.fstat` und `stat.S_ISREG` auf demselben Deskriptor, begrenztes Lesen. Gültige JSON-Rohbytes bleiben für die bestehende Hashprüfung erhalten. Auf Systemen ohne `O_NOFOLLOW` ist kein atomarer Symlink-Schutz behauptet.

## Tatsächliche Prüfungen am Code-/Doku-HEAD
- **PASS:** [Validate / static-and-contract #40078953659](https://github.com/provoware/bunkergame/actions/runs/40078953659), `CI_VERIFY: PASS`, CP1-Loader 11 Tests, `VORRELEASE_MATRIX: PASS`.
- **PASS:** [Quality Guard / repository-quality #40078953654](https://github.com/provoware/bunkergame/actions/runs/40078953654), 148 Python-Tests einschließlich drei neuer Datei-Austausch-Regressionen; `QUALITY_GUARD: PASS`, `ITERATION_GUARD: PASS`.
- **SKIPPED:** [CP1 UE-5.8 Runtime #40078953633](https://github.com/provoware/bunkergame/actions/runs/40078953633); keine echte Engine-Ausführung, kein Runtime-PASS.
- Diese Nachweisdatei selbst ist ein **späterer Dokumentations-Commit**; CI des endgültigen HEAD ist gesondert im PR nachzuweisen.

## Pflichtmatrix / Restarbeiten
- [Vorrelease-Pflichtmatrix](VORRELEASE_PFLICHTMATRIX.json): **0/40 vollständig freigegeben**; die statische Matrixprüfung ist nicht die Spielabnahme.
- BLOCKED: aktives P0-Ruleset auf `main`, vertrauenswürdiger UE-5.8-Runner, CP1-Gesamtfreigabe.
- UNOBSERVED/PLANNED: echter Build/Spawn/Movement/Telemetrie, Gameplay-Vertikalschnitt, vollständige Partien, Speichern/Wiederherstellen, 800×600/Skalierung, Tastatur, Leistung, Grafik, Installations-/Paketprüfung.
- Persönliche Sicht- und Kubuntu-Endabnahme bleibt ausdrücklich zurückgestellt.

## Nächste konkrete Implementierung
P0-Ruleset mit echten erforderlichen Prüfungen nachweisen; UE-5.8-Runner sicher bereitstellen und Bootstrap belegen; dann CP1-Build, Spawn, Movement und Telemetrie in **einem frischen echten Lauf** ausführen. Bei externer Blockade nur unabhängige, reproduzierbare P0-Funde bearbeiten. **Kein Merge, kein Release ohne ausdrückliche Nutzerfreigabe.**
