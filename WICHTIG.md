# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-010 — Runtime-Evidence an realen Lauf und Telemetrie-Datei binden

**Kategorie:** CP1 Runtime / Evidence Integrity / No-Fake-Success  
**Priorität:** P0  
**Status:** 🟡 IMPLEMENTIERT — Hosted-Abnahme und echter UE-5.8-Lauf noch offen  
**Nutzen:** 10/10  
**Aufwand:** 5/10  
**Risiko der Umsetzung:** 3/10

### Beobachtung

Die bisherige CP1-Runtime-Evidence v2 löschte zwar alte Telemetrie vor einem Lauf, war aber selbst noch nicht ausreichend gegen Wiederverwendung abgesichert. `CP1_runtime_evidence.json` war nicht an Repository, Git-HEAD oder Maschine gebunden. Das Gate prüfte weder Freshness noch Runtime-/Telemetrie-Schema und verglich die eingebettete Telemetrie nicht mit der tatsächlich auf der Platte liegenden Unreal-Datei.

Zusätzlich konnte ein altes GREEN-Evidence-JSON liegen bleiben, wenn ein neuer Collector-Versuch vor dem abschließenden Überschreiben abbrach.

### Verbesserungsvorschlag

Runtime-GREEN als **laufgebundene Beweiskette** behandeln:

```text
vor dem Lauf
→ altes Runtime-JSON löschen
→ alte Telemetrie löschen
→ alten Automation-Report löschen
→ Repository + HEAD + Maschine + sauberer Worktree prüfen
→ zufällige run_id erzeugen

UE-Lauf
→ run_id als -CP1EvidenceRunId an Unreal übergeben
→ C++-Automationstest verlangt run_id
→ Unreal schreibt dieselbe run_id in Telemetrie v3

Collector
→ Telemetrie v3 fail-closed validieren
→ Datei-SHA-256 bilden
→ Repo + HEAD + Maschine + run_id + Telemetrie einbetten
→ Runtime-Evidence Schema v3 versiegeln

Gate
→ aktuellen Repo-/HEAD-/Maschinenkontext erneut lesen
→ aktuellen Worktree erneut prüfen
→ echte Telemetrie-Datei neu lesen
→ Datei-Hash + run_id + Inhalt + Schema + Freshness erneut prüfen
→ nur dann CP1_GATE: GREEN
```

### Grund

Ein Runtime-PASS ist der stärkste technische Status im aktuellen CP1. Deshalb darf er nicht aus einem alten JSON, einer kopierten Telemetrie oder einer nur formal plausiblen Testdatei entstehen. Die Evidence muss zeigen, dass **dieser konkrete Unreal-Lauf in diesem Checkout auf dieser Maschine genau diese Telemetrie erzeugt hat**.

Eine zufällige Lauf-ID ist hier entscheidend: Selbst ein gemeinsam kopiertes Evidence-/Telemetry-Paar vom gleichen Commit verliert seine Aussagekraft, wenn es nicht zur aktuellen Ausführungskette gehört. SHA-256 dient zusätzlich der Integrität der realen Telemetrie-Datei; er ist keine Signatur oder Hardware-Attestation.

### Umgesetzt

- `Scripts/cp1_runtime_evidence_contract.py` als zentrale fail-closed Runtime-/Telemetry-Vertragslogik ergänzt.
- Runtime-Evidence auf Schema v3 / Typ `CP1_RUNTIME_EVIDENCE` angehoben.
- Telemetrie auf `bunkerbeats.cp1.movement.telemetry.v3` angehoben.
- C++-Automationstest verlangt `-CP1EvidenceRunId=<run-id>`.
- Unreal schreibt die `run_id` selbst in `CP1_RuntimeTelemetry.json` zurück.
- Collector erzeugt pro Versuch eine neue zufällige 32-stellige Hex-`run_id`.
- alter Runtime-Report, alte Telemetrie und alter Automation-Report werden vor einem neuen Versuch entfernt.
- Fehlschlag beim Stale-Cleanup blockiert den neuen Lauf.
- Runtime-Collector bindet Evidence an Repository, vollständigen Git-HEAD und pseudonymen Maschinenfingerprint.
- ein unsauberer Worktree blockiert bereits vor dem UE-Lauf.
- UE `Build.version` wird über die bestehende Readiness-Logik exakt auf 5.8 geprüft.
- Prozessstart-/Timeout-Fehler werden als strukturierte Step-Evidence gespeichert.
- `runtime_executed` wird nur gesetzt, wenn der Unreal-Prozess tatsächlich gestartet wurde.
- `cp1_pass` wird nur im vollständigen GREEN-Fall gesetzt.
- Telemetrie-Datei wird zentral validiert und per SHA-256 gebunden.
- eingebettete Telemetrie und echte Telemetrie-Datei müssen identisch sein.
- Telemetrie prüft echte Zahlentypen, Vektoren, Frame-Werte, MovementComponent und Positions-/Displacement-Konsistenz.
- `cp1_gate_runtime.py` liest aktuellen Repo-/HEAD-/Maschinenkontext und Worktree erneut.
- Gate akzeptiert nur frische Runtime-Evidence (maximal 30 Minuten).
- Gate prüft tatsächliche Telemetrie-Datei, Hash, `run_id`, Schema und Evidence-Integrität erneut.
- `Scripts/run_cp1_ue58.py` ist jetzt die kanonische Sequenz Readiness → Preflight → Runtime → Gate.
- GitHub-Workflow verwendet denselben Orchestrator und reagiert auch auf reine Contract-/Gate-Änderungen.
- `Scripts/tests/test_cp1_runtime_evidence_contract.py` deckt stale/kopierte/manipulierte Evidence, Telemetrie-Drift, Typkanten und C++↔Python-Run-ID-Wiring ab.

### Erwartete Wirkung

- kein CP1-GREEN aus einem liegen gebliebenen alten Evidence-JSON
- kein CP1-GREEN aus kopierter Telemetrie eines anderen Laufs
- kein CP1-GREEN nach Checkout-/HEAD-/Maschinenwechsel
- Telemetrie-Datei und eingebettete Evidence können nicht unbemerkt auseinanderlaufen
- manuelle Gate-Aufrufe sind genauso streng wie der Orchestrator
- Collector, Gate und Tests verwenden denselben zentralen Vertrag
- bessere Diagnose bei Timeout, Buildfehler, UE-Testfehler und Evidence-Drift
- deutlich höhere Wartbarkeit durch eine kanonische Ausführungsreihenfolge

### Technischer Effekt

```text
RUN-ID CHALLENGE
Python run_id
→ Unreal command line
→ C++ Automation Test
→ Telemetry v3 run_id
→ telemetry SHA-256
→ Runtime Evidence v3
→ live Gate Revalidation
```

### Aktueller belegter Zustand

- PR #6 Runner Evidence Binding: gemergt
- `main` danach: `367efbd72d4918f6acb3c2a291e9493b507f7344`
- Runtime Contract v3: implementiert
- Telemetrie run_id v3: implementiert
- Collector-Stale-Cleanup: implementiert
- Live Runtime Gate: implementiert
- Runtime-Contract-Regressionstests: implementiert
- Hosted-Abnahme dieses neuen Branches: noch offen
- reales GitHub-P0-Ruleset: weiterhin nicht aktiv nachgewiesen
- realer Self-hosted UE-5.8-Runner: weiterhin nicht nachgewiesen
- echter CP1 Runtime-Lauf: weiterhin `UNOBSERVED/BLOCKED`

### Fertig, wenn

- Hosted `static-and-contract` PASS ist
- Hosted `repository-quality` inklusive Runtime-Contract-Regressionen PASS ist
- C++-/Python-Run-ID-Vertrag statisch konsistent ist
- `cp1-runtime` ohne realen Runner weiterhin nur SKIPPED/BLOCKED bleibt
- auf der echten UE-5.8-Maschine Build + Automation + Telemetrie v3 real erzeugt werden
- das neue Live-Gate dieselbe Evidence anschließend als GREEN bestätigt

### Detailanleitung

Der reale Ablauf bleibt `RUN_CP1_UE58_ALL.sh` / `RUN_CP1_UE58_ALL.bat` beziehungsweise `python3 Scripts/run_cp1_ue58.py`. Ein Hosted-Test-PASS beweist nur die Vertragslogik, niemals den Unreal-Runtime-Erfolg.
