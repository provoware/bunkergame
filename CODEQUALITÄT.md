# CODEQUALITÄT — APPEND-ONLY QUALITÄTSJOURNAL

> Diese Datei ist ein **append-only Entwicklungsgedächtnis**. Pro Iteration wird genau ein neuer Verbesserungsvorschlag unten angehängt. Bestehende Einträge werden nicht gelöscht, umgeschrieben oder nachträglich „schöner“ gemacht. Wenn eine frühere Idee überholt ist, bekommt sie in einer späteren Iteration einen neuen Gegeneintrag.

---

## CQ-2026-08-27-001 — Autonomer Repository Quality Guard

**Iteration:** Dokumentations-/GitHub-Control-Plane 2  
**Kategorie:** Testautomatisierung / Wartbarkeit / Fehlerprävention  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT  
**Aufwand:** 3/10  
**Risiko:** 1/10

### Verbesserungsvorschlag

Einen vollständig autonomen, UE-unabhängigen `Quality Guard` einführen, der bei Pull Requests, Pushes und regelmäßig geplant ausgeführt wird und zentrale Repository-Invarianten prüft.

### Grund

`Scripts/ci_verify.py` prüft CP1- und Projektverträge sehr gut, deckt aber allgemeine Repository-Qualität wie kaputte lokale Dokumentlinks, Merge-Konfliktmarker, fehlende Kerndokumente oder ungültige JSON-Dateien nicht als eigene, leicht erweiterbare Schicht ab.

### Wirkung

- Dokumentationsfehler werden vor dem Merge sichtbar.
- ungültige JSON-Konfigurationen werden automatisch blockiert.
- Python-Syntaxfehler werden unabhängig vom fachlichen Testpfad erkannt.
- versehentlich eingecheckte generierte Ordner werden erkannt.
- Qualitätsregeln können zentral erweitert werden, ohne Gameplay-Gates aufzublähen.

### Technischer Effekt

Die CI wird von einem einzelnen fachlichen Gate zu einem **mehrschichtigen Kontrollsystem**:

```text
Validate
   ↓
Quality Guard
   ↓
Iteration Guard
   ↓
UE Runtime Gate, falls erforderlich
```

Dadurch lassen sich Fehlerklassen klarer zuordnen und Reparaturen bleiben kleiner.

### Zusatzeffekt

Der zugehörige `Iteration Guard` prüft zusätzlich, dass bei jeder PR-Iteration:

- `WICHTIG.md` aktualisiert wird,
- `CODEQUALITÄT.md` erweitert wird,
- historische CODEQUALITÄT-Einträge nur angehängt und nicht still überschrieben werden.

### Erwarteter Nutzen

**Robustheit:** hoch  
**Wartbarkeit:** sehr hoch  
**Entwicklerführung:** sehr hoch  
**Gameplay-Risiko:** keines
