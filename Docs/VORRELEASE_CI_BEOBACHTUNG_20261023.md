# Vorrelease – CI-Beobachtung 23.10.2026

Basis: main 9f2f4db4689291295938bce9e245590eb525bc8c; Entwicklungsbasis 60227feb3d844ff8170ca3cecdbf3cdd8779b909.

Die vorhandene Vorrelease-Matrix ist noch nicht im zentralen Validate-Lauf eingebunden. Lokaler isolierter Reproduktionstest: vor der Korrektur 2/3 PASS, danach 3/3 PASS. Dies ist kein Unreal-Runtime-Nachweis.

P0: Die unveränderte Schutzregelprüfung meldet weiterhin FAIL; der Hauptzweig ist nicht geschützt. Keine Änderung an den Schutzregeln vorgenommen.

Nächste Implementierung: Scripts/ci_verify.py um Matrix-Gate und drei Regressionstests ergänzen; fehlende oder doppelte Aufrufe durch einen Negativtest abfangen. Anschließend vollständige CI und Qualitätsprüfung ausführen.

Unreal 5.8, Spielfunktionen, Speicherung, Oberflächen- und Release-Prüfungen bleiben offen. Persönliche Endabnahme und Release sind zurückgestellt.
