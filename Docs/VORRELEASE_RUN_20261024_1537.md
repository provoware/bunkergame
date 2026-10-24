# Vorrelease-Nachweis – CP1-JSON-Rekursion (24.10.2026)

- Repository: `provoware/bunkergame`
- Hauptzweig `main` beim Start: `9f2f4db4689291295938bce9e245590eb525bc8c`.
- Gestapelte Ausgangsbasis: PR #18, `ade1f8e5f1a1e8f3895cf1e5b3a3b86f9845c5ca`.
- Entwicklungszweig: `fix/cp1-json-recursion-20261024-1537`; [Entwurfs-PR #19](https://github.com/provoware/bunkergame/pull/19).
- **Befund:** 20.000 verschachtelte Arrays oder Objekte verursachen beim Python-JSON-Parser `RecursionError`, obwohl die Dateien kleiner als 4 MiB sind.
- **Umsetzung:** Fehler wird kontrolliert in `load_json_file` behandelt. Zwei negative Teilfälle ergänzen die bereits verdrahteten CP1-Regressionen.
- **Lokale Reproduktion:** Python 3.13.5, `json.loads` auf beiden Testeingaben → `RecursionError`. Dies ist keine Ausführung des vollständigen Projekt-Testprogramms.
- **Code-/Doku-HEAD der ersten CI:** `2a35870e998911d9c3cb6b73f2f80c10cdfd5f66`.
- **PASS:** [GitHub Validate #40099100013](https://github.com/provoware/bunkergame/actions/runs/40099100013): `CI_VERIFY: PASS`, `VORRELEASE_MATRIX: PASS`, CP1-Loader 12/12.
- **PASS:** [GitHub Quality Guard #40099100020](https://github.com/provoware/bunkergame/actions/runs/40099100020): 149/149 Python-Tests, neuer Tiefentest einschließlich zwei Grenzfällen, `QUALITY_GUARD: PASS`, `ITERATION_GUARD: PASS`.
- **SKIPPED:** [UE-5.8-CP1-Runtime #40099100001](https://github.com/provoware/bunkergame/actions/runs/40099100001); keine Engine-Ausführung.
- **FAIL / Infrastruktur:** [P0 Infrastructure Observer #40082770442](https://github.com/provoware/bunkergame/actions/runs/40082770442) auf `main`: erwartetes aktives Ruleset `BUNKER BEATS P0 main gate` nicht vorhanden (0 gefunden). Keine Schutzumgehung.
- **Dieser Nachtrag erzeugt einen neuen Dokumentations-HEAD; dessen GitHub-CI muss gesondert geprüft werden.**
- **Pflichtmatrix:** 0/40 vollständig freigegeben. `P0_RULESET` und `P0_RUNNER` BLOCKED; CP1-Runtime und vollständige Spielverläufe UNOBSERVED/PLANNED.
- **Nächste Pflichtarbeit:** aktives Ruleset, vertrauenswürdigen UE-5.8-Runner und echten Build/Spawn/Movement/Telemetrie/Gate nachweisen.
- **Grenzen:** keine Gameplay- oder Engine-Ausführung; kein Merge, kein Release, keine persönliche Endabnahme.
