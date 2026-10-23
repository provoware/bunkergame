# BUNKER BEATS — Vorrelease-Prüfkette, 23.10.2026

**Repository:** provoware/bunkergame  
**Beobachteter main-HEAD:** `9f2f4db4689291295938bce9e245590eb525bc8c`  
**Entwicklungszweig:** `fix/prerelease-ci-wiring-20261023-0934`  
**Paket:** P0 — vorhandene Vorrelease-Verträge in Validate aufnehmen.

## Soll / Ist / Evidenz / Status

| Bereich | Soll | Ist | Evidenz / Status |
|---|---|---|---|
| Pflichtmatrix | 40 Anforderungen, inklusive einzelner Spielelemente und Gates | `Docs/VORRELEASE_PFLICHTMATRIX.json` und `Docs/VORRELEASE_SPIELELEMENTE.md` | Vorhanden; Validierung in CI neu angebunden; **IMPLEMENTED** bis CI-PASS |
| Matrix-Integrität | Schema, Pflichtkennungen, Bereiche, Referenzen, Status, Nachweise prüfen | `Scripts/prerelease_gate.py` | **IMPLEMENTED**, Runtime-PASS ausdrücklich nicht behauptet |
| Regression | Matrix- und Katalogabdeckung dauerhaft prüfen | `Scripts/tests/test_prerelease_matrix.py`, `test_prerelease_elements.py` | **IMPLEMENTED**, CI-Ergebnis separat nachführen |
| CI-Einbindung | Alle drei Prüfungen plus Verdrahtungstest genau einmal ausführen | `Scripts/ci_verify.py` und `test_prerelease_ci_wiring.py` | **IMPLEMENTED**, CI-Ergebnis separat nachführen |
| GitHub-Schutz | Required Checks, Ruleset und PR-Pflicht auf main | Hauptzweig ungeschützt laut GitHub-Branch-Abfrage | **BLOCKED**; keine Umgehung |
| UE 5.8 | echter Build, Spawn, Bewegung, Telemetrie und CP1 GREEN | kein verifizierter echter Lauf | **BLOCKED/UNOBSERVED** |
| Spielbarkeit | Interaction → Task → Ability → XP → vollständige Partien | aktueller vertikaler Schnitt noch nicht runtime-bewiesen | **PLANNED/UNOBSERVED** |
| Speicher-/Fehlerfälle | atomare Spielstände, Wiederherstellung, Migration, Korruption | laut Matrix nicht fertig bewiesen | **PLANNED/UNOBSERVED** |
| Oberfläche | 800×600, 200 % Skalierung, Tastatur, Fokus, Grafik | kein echter UE-Nachweis | **UNOBSERVED** |
| Leistung/Balance | 60 FPS auf definierter Hardware, deterministische Balance-Batches | kein Runtime-/Batch-Nachweis | **UNOBSERVED** |
| Installation/Release | Linux/Windows-Paket, Volltests, Regression, Doku, Freeze | keine Gesamtfreigabe | **BLOCKED** |

## Testplan und Grenzen

1. Statischer Negativtest: Entfernen/Duplizieren jedes CI-Pflichtaufrufs muss fehlschlagen.
2. Vorhandene Matrix- und Spielelementtests sowie vollständiges `python3 Scripts/ci_verify.py` müssen auf dem tatsächlichen Repository laufen.
3. `python3 Scripts/repo_quality.py` und PR-Iteration-Guard prüfen Dokumentation, Hygiene und Änderungsverlauf.
4. GitHub-Validate und Quality Guard müssen für den exakten PR-HEAD erfolgreich sein.
5. UE-5.8-Runtime, Spielverläufe, Speicherung, 800×600 und Nutzerabnahme bleiben separate Gates.

**Risiko:** Bestehende Matrix-Tests könnten nach CI-Anbindung bisher unerkannte Fehler melden; solche Fehler werden behoben, nicht umgangen.  
**Rollback:** Nur diesen Entwicklungszweig/PR zurücknehmen, main unverändert lassen.  
**Nächste konkrete Implementierung:** Nach grünen CI-Gates P0-Branchschutz/Runner-Bootstrap regelkonform nachweisen; danach CP1-UE-5.8-Lauf und Interaction-Vertikalschnitt.  
**Release:** gesperrt. **Merge:** nur nach erfolgreichen Pflichtprüfungen. **Persönliche Endabnahme:** zurückgestellt.

## Nachträglich auf GitHub bestätigte technische Evidenz

**Geprüfter Entwicklungs-HEAD:** `3c6aeaac6d627515607ecebaaa8159e15e40eb0a`  
**Entwurfs-PR:** https://github.com/provoware/bunkergame/pull/13

| Prüfkette | Ergebnis | Konkreter Nachweis |
|---|---|---|
| Validate / static-and-contract | **PASS** | https://github.com/provoware/bunkergame/actions/runs/39919004091 |
| Quality Guard / repository-quality | **PASS** | https://github.com/provoware/bunkergame/actions/runs/39919004128 |
| P0-Control-Plane-Regression | **PASS** | Quality Guard, gleicher Lauf |
| PR-Iteration-Guard | **PASS** | Quality Guard, gleicher Lauf |
| Git-Patch-Leerraumprüfung | **PASS** | Quality Guard, gleicher Lauf |
| Vorrelease-Matrix-Gate | **PASS (Struktur, nicht Release)** | Validate-Protokoll `VORRELEASE_MATRIX: PASS` |
| Tatsächliche UE-5.8-Runtime | **BLOCKED/UNOBSERVED** | kein passender Runtime-Nachweis |
| Schutzregelsatz auf main | **BLOCKED** | unverändert; kein Schutz umgangen |

Vor dem erfolgreichen Qualitätslauf wurde eine unvollständige `WICHTIG.md`-Abschnittsstruktur im ersten PR-Prüflauf erkannt (**FAIL**, https://github.com/provoware/bunkergame/actions/runs/39918938320) und durch Wiederherstellung der geforderten Begriffe **Verbesserungsvorschlag, Grund, Wirkung** behoben. Die Folgeprüfung war grün.

**Hinweis:** Diese Dokumentationsaktualisierung erzeugt selbst einen neuen Commit; dessen GitHub-Prüfungen sind erneut separat zu kontrollieren. Die obigen PASS-Nachweise beziehen sich ausdrücklich auf den angegebenen SHA.
