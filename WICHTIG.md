# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-013 — Linux-Klick-&-Start durch echte Dateirechte garantieren

**Kategorie:** Portabilität / Launcher / Release-Qualität / Linux  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT + HOSTED GEPRÜFT — finaler Release-Neubau noch offen  
**Nutzen:** 9/10  
**Aufwand:** 2/10  
**Risiko der Umsetzung:** 1/10

### Beobachtung

Der Release-Smoke des nach PR #9 erzeugten vollständigen ZIPs bestätigte den Environment-Doctor-Fix: Schema v2, explizite Nachvalidierung und 10/10 Contract-Regressionstests waren grün. Dabei wurde jedoch ein weiterer Portabilitätsfehler sichtbar:

```text
START_BUNKER_BEATS_INTELLIGENT.sh executable=no
```

Der Git-Tree bestätigte, dass `START_BUNKER_BEATS_INTELLIGENT.sh`, `START_BUNKER_BEATS_ALL.sh` und der interne Shell-Smoke-Launcher mit Modus `100644` gespeichert waren. Nur `RUN_CP1_UE58_ALL.sh` war bereits `100755`.

### Verbesserungsvorschlag

Alle Linux-Startskripte, die als Start-/Smoke-Einstieg dienen, müssen im Repository selbst als ausführbar (`100755`) versioniert sein. Die Release-Pipeline darf die Rechte nicht künstlich beim Packen reparieren; sonst wäre das ZIP nicht mehr die unveränderte Projektbasis von `main`.

Zusätzlich muss der Package-Integrity-Test die Execute-Bits dauerhaft prüfen.

### Grund

`bash START_BUNKER_BEATS_INTELLIGENT.sh` funktioniert auch ohne Execute-Bit, aber ein echtes **Klick-&-Start**-Versprechen benötigt ausführbare Dateien. Dateirechte sind Teil des Release-Artefakts und dürfen nicht als implizite lokale Nacharbeit vorausgesetzt werden.

Ein Paket, dessen Inhalt korrekt ist, dessen Linux-Einstieg aber nach dem Entpacken nicht direkt ausführbar ist, ist für die angestrebte Laienbedienung nur teilweise portabel.

### Umgesetzt

- `Tests/test_cp1_package_integrity.py` prüft jetzt für alle zentralen Linux-Einstiege Existenz und Execute-Bit.
- folgende Git-Modi sind auf `100755` gehärtet:
  - `START_BUNKER_BEATS_INTELLIGENT.sh`
  - `START_BUNKER_BEATS_ALL.sh`
  - `RUN_CP1_UE58_ALL.sh`
  - `Build/Scripts/run_cp1_smoke.sh`
- die Prüfung läuft im bestehenden `ci_verify.py`-Pfad und wird damit bei Hosted Validate sowie vor Release-Paketierung erzwungen.

### Wirkung

- Linux-Klick-&-Start bleibt beim Checkout und im ZIP erhalten
- kein nachträgliches `chmod +x` als versteckte Benutzerpflicht
- Release-Paket entspricht weiterhin der tatsächlichen `main`-Projektbasis
- Regression bei Git-Dateimodi wird automatisch erkannt
- Start-, Smoke- und CP1-Einstiege verwenden konsistente Unix-Rechte
- bessere Portabilität und Laienfreundlichkeit

### Technischer Effekt

```text
Git tree mode 100755
→ checkout erhält Execute-Bit
→ rsync übernimmt Modus
→ ZIP speichert Unix-Modus
→ normaler Linux-Extractor stellt Execute-Bit wieder her
→ Package-Integrity-Test prüft denselben Vertrag
```

### Aktueller belegter Zustand

- Environment-Doctor-v2-Core-Smoke: PASS
- `summary.after` vorhanden
- fehlende UE 5.8 bleibt korrekt YELLOW
- Environment-GUI-Contract-Tests: 10/10 PASS
- Git-Modus-Fehler der Startskripte real im Release-Smoke gefunden
- Regressionstest für Execute-Bits implementiert
- Hosted `repository-quality`: PASS auf PR #10 inklusive Iteration Guard
- Hosted `static-and-contract`: PASS auf PR #10 inklusive Package-Integrity-Execute-Bit-Prüfung
- CP1 Runtime-Workflow weiterhin korrekt SKIPPED ohne reale UE-Freigabe
- finaler Release-Neubau aus dem gemergten `main` noch offen
- echter UE-5.8-CP1-Runtime-Lauf weiterhin `UNOBSERVED/BLOCKED`

### Fertig, wenn

- alle vier Linux-Einstiege im Git-Tree `100755` besitzen
- `static-and-contract` PASS ist
- `repository-quality` PASS ist
- Package-Integrity-Test Execute-Bits PASS meldet
- PR konfliktfrei integriert ist
- neues vollständiges ZIP aus dem daraus resultierenden `main` erzeugt wurde
- lokale ZIP-Struktur, SHA-256 und Execute-Bits erneut geprüft sind
