# BUNKER BEATS — Vorrelease-Nachweis 2026-10-24: JSON-Konstanten im UE-Runner

## GitHub-Stand und Scope
- Repository: `provoware/bunkergame`.
- Hauptzweig beim Beginn: `9f2f4db4689291295938bce9e245590eb525bc8c`; unverändert.
- Ausgangs-HEAD: `a2d13d5d953bf88644e9b5ef8d922f18978216da` (Entwurfs-PR #15).
- Entwicklungszweig: `fix/runner-json-nonfinite-20261024-0038`; auf PR #15 gestapelt, kein Merge.
- Geänderte Fachdateien: `Scripts/runner_readiness.py` und `Scripts/tests/test_runner_evidence_binding.py`.
- Dokumentationsdateien: `WICHTIG.md`, `CODEQUALITÄT.md` (append-only), `Docs/TODO.md`, `Docs/CHANGELOG.md`, dieser Bericht.
- Verbotener Scope: keine Gameplay-Änderung, keine Runner-Policy, keine Secrets, keine Schutzumgehung, kein Release.

## Reproduzierter Befund
Pythons `json.loads` akzeptierte bei sonst gültigem `Build.version` nicht normgerechte JSON-Konstanten `NaN`, `Infinity` und `-Infinity`. Auch verschachtelte Metadaten konnten dadurch eine gültige UE-5.8-Versionprüfung passieren. Ein Parser-Test mit der unveränderten Python-Standardbibliothek bestätigte diese Akzeptanz.

## Änderung und Evidenz
| Prüfpunkt | Status | Beleg |
|---|---|---|
| Nicht endliche JSON-Konstanten | IMPLEMENTED | `parse_constant` wirft `ValueError`; vorhandene Fehlerbehandlung liefert kontrolliertes FAIL. |
| Vier Negativfälle | IMPLEMENTED | `test_non_finite_json_constants_are_rejected`: NaN im Metadatenfeld, Infinity in Liste, -Infinity in verschachteltem Objekt, NaN als MajorVersion. |
| Gültige endliche Metadaten | IMPLEMENTED | `test_finite_json_metadata_still_passes`: 5.8 mit endlicher Dezimalzahl und JSON-Bool/Null. |
| Isolierte Parser-Reproduktion | PASS | 7/7 lokale `unittest`-Fälle einschließlich vorhandener Duplikat- und Formfälle, 24.10.2026; reproduzierte Parserlogik, **nicht** vollständiger Repository-Testlauf. |
| GitHub Validate | PASS (geprüfter HEAD) | [static-and-contract #40035142309](https://github.com/provoware/bunkergame/actions/runs/40035142309), `CI_VERIFY: PASS`, Runner-Bindung 27 Tests. |
| GitHub Quality Guard / Iteration Guard | PASS (geprüfter HEAD) | [repository-quality #40035142335](https://github.com/provoware/bunkergame/actions/runs/40035142335), 137 Python-Tests, Iteration Guard PASS. |
| Echte UE-5.8-Runtime | SKIPPED / BLOCKED | [CP1 #40035142370](https://github.com/provoware/bunkergame/actions/runs/40035142370) übersprungen; kein vertrauenswürdiger UE-5.8-Runner / keine frische CP1-Evidence. |
| Main-Branchschutz | BLOCKED | Adminschutz nicht verändert; API-Lesezugriff auf Branch-Protection meldete 403. |

## Vorrelease-Pflichtmatrix
`Docs/VORRELEASE_PFLICHTMATRIX.json` bleibt bewusst unverändert: 40 Anforderungen, davon 3 BLOCKED, 6 UNOBSERVED, 14 IMPLEMENTED und 17 PLANNED. **0/40 vollständig freigegeben.** `candidate_frozen=false`, persönliche Endabnahme nicht erfolgt, Release nicht genehmigt.

## Nächste konkrete Implementierung
Vertrauenswürdigen UE-5.8-Runner unter vorhandenen Sicherheitsbedingungen bereitstellen; Bootstrap-Readiness mit aktuellem SHA und Maschinenfingerprint prüfen; echten CP1-Build, Character Spawn, Bewegung, Telemetrie und Gate mit frischer Evidence ausführen. Wenn externe Bereitstellung weiter blockiert, nur weitere unabhängige P0-Pflichten mit reproduzierbarem Befund bearbeiten. Keine persönliche Sicht-/Kubuntu-Endabnahme vor vollständig technisch geprüftem und eingefrorenem Kandidaten.

**CI-Evidence:** Auf dem geprüften PR-HEAD `4f70738799bc75431af5ff19ad70a065f47d5caa` sind Validate und Quality Guard erfolgreich; der echte CP1-Workflow wurde übersprungen. Diese Dokumentation wird nach dem geprüften Code-HEAD aktualisiert. Der abschließende Dokumentations-HEAD erfordert einen eigenen CI-Lauf und darf erst danach als geprüft bezeichnet werden.
