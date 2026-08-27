# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-003 — Runner-Freigabe nur mit frischer, exakt verifizierter UE-5.8-Evidence

**Kategorie:** Schwachstelle / Evidence / Self-hosted Runner / GitHub-Sicherheit  
**Priorität:** P0  
**Status:** 🟢 TECHNISCH GEHÄRTET — reale UE-Maschine weiterhin extern erforderlich  
**Nutzen:** 10/10  
**Aufwand:** 4/10  
**Risiko der Umsetzung:** 2/10

### Beobachtung

Der bisherige GitHub-P0-Assistent konnte `UE58_RUNNER_ENABLED=true` über einen expliziten Schalter setzen, obwohl nur ein Warnhinweis verlangte, vorher `RUNNER_READINESS: PASS` zu erzeugen. Außerdem erkannte `runner_readiness.py` zwar typische `UE_5.8`-Pfade, prüfte aber die tatsächliche Engine-Version aus `Engine/Build/Build.version` noch nicht und erzeugte keinen Freshness-Zeitstempel.

Damit bestand ein möglicher Bypass zwischen **Maschine sieht passend aus** und **Maschine ist frisch und exakt als UE 5.8 geprüft**.

### Verbesserungsvorschlag

Die Aktivierung der Repository-Variable wird an maschinell validierte Evidence gebunden:

```text
runner_readiness.py
→ Build.version lesen
→ exakt UE 5.8 bestätigen
→ alle Readiness-Checks PASS
→ UTC-Zeitstempel schreiben
→ Evidence höchstens 30 Minuten alt
→ github_p0_admin.py validiert Evidence erneut
→ erst dann UE58_RUNNER_ENABLED=true
```

### Umgesetzt

- `runner_readiness.json` verwendet Schema v2.
- `generated_at_utc` wird gespeichert.
- `Engine/Build/Build.version` wird gelesen.
- `MajorVersion == 5` und `MinorVersion == 8` sind zwingend.
- `engine_version_exact_5_8` ist ein Required Readiness Check.
- `github_p0_admin.py` akzeptiert nur Schema v2 und den korrekten Evidence-Typ.
- Status muss `PASS` sein.
- alle Readiness-Checks müssen `true` sein.
- Runtime-/CP1-Claims innerhalb der Readiness-Evidence werden als unzulässig blockiert.
- Evidence älter als 30 Minuten wird blockiert.
- deutlich in der Zukunft liegende Evidence wird blockiert.
- Regressionstests liegen unter `Scripts/tests/test_p0_control_plane.py`.
- `Quality Guard` führt diese Tests automatisch aus.

### Grund

Eine sicherheitsrelevante Freigabe darf nicht auf Erinnerung oder Bedienhinweis vertrauen. Der Übergang selbst muss die Evidence prüfen. Besonders bei Self-hosted Runnern kann veraltete oder falsch zugeordnete Readiness sonst einen Workflow auf einer inzwischen veränderten Maschine freischalten.

### Erwartete Wirkung

- kein versehentliches Aktivieren ohne aktuelle Readiness
- keine Freigabe für UE 5.7, UE 5.9 oder nur passend benannte Verzeichnisse
- weniger Stale-Evidence-Risiko
- klarere Trennung von Maschinenbereitschaft und Runtime-Erfolg
- Regressionen der Freigabelogik werden in Hosted CI erkannt

### Technischer Effekt

Die Freigabe wird zu einer echten Evidence-State-Machine:

```text
NO EVIDENCE / FAIL / STALE / WRONG UE
→ BLOCKED

FRESH UE58_RUNNER_READINESS PASS
→ Variable darf gesetzt werden

VARIABLE ENABLED
→ Runtime darf starten

RUNTIME PASS
→ erst dann CP1 GREEN
```

### Aktueller belegter Zustand

- Hosted `Validate`: PASS
- Hosted `Quality Guard`: PASS auf dem vorherigen abgenommenen Head
- Branch-Protection auf `main`: weiterhin extern offen
- Self-hosted UE-5.8 Runner: weiterhin extern offen
- reale Readiness-Evidence: noch nicht vorhanden
- CP1 Runtime: weiterhin `UNOBSERVED/BLOCKED`

### Fertig, wenn

- neue P0-Regressionstests auf GitHub PASS sind
- `main` Branch Gate real PASS ist
- Self-hosted Runner registriert ist
- `runner_readiness.py` auf dieser Maschine frisch PASS erzeugt
- `github_p0_admin.py --apply --enable-runner-variable` diese Evidence akzeptiert
- danach der echte CP1-Workflow läuft

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md` und Issue #2.
