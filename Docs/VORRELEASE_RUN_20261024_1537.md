# Vorrelease-Nachweis – CP1-JSON-Rekursion (24.10.2026)

- Repository: `provoware/bunkergame`
- Hauptzweig `main` beim Start: `9f2f4db4689291295938bce9e245590eb525bc8c`.
- Gestapelte Ausgangsbasis: PR #18, `ade1f8e5f1a1e8f3895cf1e5b3a3b86f9845c5ca`.
- Entwicklungszweig: `fix/cp1-json-recursion-20261024-1537`; Entwurfs-PR noch zu erstellen.
- **Befund:** 20.000 verschachtelte Arrays oder Objekte verursachen beim Python-JSON-Parser `RecursionError`, obwohl die Dateien kleiner als 4 MiB sind.
- **Umsetzung:** Fehler wird kontrolliert in `load_json_file` behandelt. Zwei negative Teilfälle ergänzen die bereits verdrahteten CP1-Regressionen.
- **Lokale Reproduktion:** Python 3.13.5, `json.loads` auf beiden Testeingaben → `RecursionError`. Dies ist keine Ausführung des vollständigen Projekt-Testprogramms.
- **Projekt-/GitHub-Tests:** noch nicht ausgeführt; CI am finalen HEAD auswerten. Keine PASS-Behauptung vor tatsächlicher Prüfung.
- **Pflichtmatrix:** 0/40 vollständig freigegeben. `P0_RULESET` und `P0_RUNNER` BLOCKED; CP1-Runtime und vollständige Spielverläufe UNOBSERVED/PLANNED.
- **Nächste Pflichtarbeit:** aktives Ruleset, vertrauenswürdigen UE-5.8-Runner und echten Build/Spawn/Movement/Telemetrie/Gate nachweisen.
- **Grenzen:** keine Gameplay- oder Engine-Ausführung; kein Merge, kein Release, keine persönliche Endabnahme.
