# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Genau ein priorisierter Verbesserungsvorschlag. Historische Einträge bleiben in `CODEQUALITÄT.md`.

## W-2026-10-21-014 — CP1-Diagnose auf kleinen Bildschirmen benutzbar halten

**Kategorie:** CP1-Diagnose / Oberfläche / Barrierefreiheit  
**Priorität:** P0 (Zugang zur Vorprüfung, nicht Runtime-Freigabe)  
**Status:** 🟡 IMPLEMENTIERT — echte GUI-Abnahme bei 800 × 600 ausstehend  
**Nutzen:** 8/10  
**Aufwand:** 3/10  
**Risiko:** 2/10

### Beobachtung

Das Environment-Doctor-Fenster verlangte mindestens 960 × 650 Pixel. Seine zwei festen horizontalen Bereiche und die 670 Pixel breiten Tabellenspalten konnten auf kleineren Displays wichtige Diagnosen abschneiden. Das erschwert den Zugang zur CP1-Vorprüfung.

### Verbesserungsvorschlag

Das Diagnosefenster auf 800 × 600 als Mindestgröße einstellen. Unter 1120 Pixel Fensterbreite die Ampel- und Detailbereiche untereinander anordnen; darüber nebeneinander. Die drei Tabellenspalten schmaler beginnen lassen, die Erklärungsspalte aber flexibel ausdehnen. Das Umschalten ohne laufende Prüfungen zu unterbrechen ermöglichen.

### Grund

Eine Vorprüfung muss auch dann bedienbar bleiben, wenn die Zielmaschine einen kleinen Bildschirm oder eine hohe Skalierung nutzt. Eine verdeckte Diagnosemeldung ist ein echtes Bedienrisiko.

### Wirkung

- Prüf- und Reparaturschaltflächen bleiben im Kopfbereich.
- Ampel und Detailausgabe nutzen bei 800 × 600 die volle Fensterbreite.
- Breite Fenster behalten die gleichzeitige Übersicht.
- Keine Änderung an Prüfentscheidungen, Runtime-Gates oder Spielständen.
- Reine Grenzwerttests schützen die Layoutentscheidung vor Regressionen.

### Technischer Effekt

`Launcher/core/viewport_layout.py` definiert die Mindestgröße und den Umschaltpunkt. `Launcher/gui/repair_gui.py` setzt die beiden Bereiche je nach Breite in ein ein- oder zweispaltiges Raster. `Scripts/tests/test_environment_gui_contract.py` prüft die Breiten 800, 960, 1024, 1119, 1120, 1180 und 1600.

### Nächster Nachweis

`static-and-contract` und `repository-quality` müssen auf dem PR-Commit grün sein. Danach muss ein echter Linux-Tkinter-Lauf bei 800 × 600 und hoher Skalierung prüfen, dass Texte, Status und Schaltflächen erreichbar sind. Unreal Engine 5.8, Ruleset und CP1-Runtime bleiben unabhängig davon weiterhin offen.
