# WICHTIG — AKTUELLER VERBESSERUNGSFOKUS

> Diese Datei enthält **genau einen priorisierten Verbesserungsvorschlag der aktuellen Iteration**. In der nächsten Iteration wird der Fokus neu bewertet und diese Datei aktualisiert. Historische Qualitätsideen bleiben in `CODEQUALITÄT.md` erhalten.

## W-2026-08-27-009 — Runner-Readiness an Checkout und Maschine binden

**Kategorie:** Evidence Integrity / Self-hosted Runner / Kontextbindung  
**Priorität:** P0  
**Status:** 🟢 IMPLEMENTIERT — reale UE-5.8-Maschinen-Evidence weiterhin offen  
**Nutzen:** 10/10  
**Aufwand:** 4/10  
**Risiko der Umsetzung:** 2/10

### Beobachtung

Die bisherige Readiness-Evidence war frisch und prüfte UE 5.8 sowie mehrere Maschinen-Voraussetzungen, war aber noch nicht stark genug an **den konkreten Ausführungskontext** gebunden. Eine formal gültige und noch frische JSON-Datei hätte theoretisch aus einem anderen Checkout oder von einer anderen Maschine kopiert werden können. Außerdem verlangte die bisherige Admin-Prüfung zwar, dass alle vorhandenen Checks `true` sind, aber noch nicht den **exakt erwarteten vollständigen Check-Satz**.

Ein weiterer Randfall: Nach einem erfolgreichen Readiness-Lauf könnten lokale Dateien verändert werden, ohne dass sich der Git-Commit-SHA ändert. Eine reine HEAD-Bindung würde diese Veränderung nicht erkennen.

### Verbesserungsvorschlag

Readiness-Evidence als kontextgebundene Freigabe behandeln:

```text
RUNNER READINESS
→ Repository exakt provoware/bunkergame
→ vollständiger Git-HEAD
→ Worktree sauber
→ pseudonymer Maschinenfingerprint
→ exakt definierter Check-Satz
→ UE exakt 5.8
→ Evidence maximal 30 Minuten alt
→ Schema v3

VOR UE58_RUNNER_ENABLED=true
→ Repository erneut bestimmen
→ Git-HEAD erneut bestimmen
→ Maschinenfingerprint erneut bestimmen
→ Worktree erneut auf sauber prüfen
→ gespeicherte Evidence gegen genau diesen aktuellen Kontext prüfen
→ erst dann GitHub-Variable setzen
```

### Grund

Eine sicherheitsrelevante Evidence soll nicht nur sagen „irgendeine passende Maschine war vor kurzem bereit“, sondern „**dieser Checkout auf dieser Maschine in diesem Zustand** war bereit und ist vor der Freigabe noch derselbe“. Dadurch verliert kopierte, teilweise erzeugte oder nachträglich kontextfremde Evidence ihre Freigabewirkung.

Der Maschinenfingerprint ist bewusst **keine Hardware-Attestation**. Er ist ein pseudonymer SHA-256 aus Hostname, Betriebssystem und Architektur und dient dazu, versehentliche oder einfache Evidence-Wiederverwendung zwischen Maschinen zu verhindern. Er beweist keine physische Maschinenidentität und enthält keine Hardware-Seriennummer.

### Umgesetzt

- `Scripts/runner_identity.py` als gemeinsame, nicht geheime Identitätsschicht ergänzt.
- GitHub-Remote wird auf `owner/repo` normalisiert; rohe Remote-URLs oder Zugangsdaten werden nicht in die Evidence geschrieben.
- HTTPS-, SCP-SSH- und `ssh://`-GitHub-Remotes werden unterstützt.
- vollständiger 40-stelliger Git-HEAD wird ermittelt.
- Worktree-Sauberkeit wird zentral bestimmt.
- pseudonymer Maschinenfingerprint verwendet Schema `hostname-os-arch-sha256-v1`.
- `Scripts/runner_readiness_contract.py` zentralisiert Schema, Pflichtchecks, Freshness und Kontextbindung.
- Readiness-Schema von v2 auf **v3** angehoben.
- der vollständige Pflichtcheck-Satz ist jetzt exakt definiert; fehlende **und zusätzliche** Checks blockieren.
- Bool-Werte werden nicht als Integer-Schema-/Versionswerte akzeptiert.
- `runner_readiness.py` bindet Evidence an Repository, Git-HEAD und Maschinenfingerprint.
- `repository_identity_exact`, `git_head_bound` und `machine_identity_bound` sind neue Pflichtchecks.
- `github_p0_admin.py` verwendet denselben zentralen Contract statt einer separaten vereinfachten Readiness-Logik.
- unmittelbar vor `UE58_RUNNER_ENABLED=true` werden Repository, HEAD, Maschine und Worktree erneut live geprüft.
- ein nach Readiness verschmutzter Worktree blockiert die Freigabe selbst bei unverändertem HEAD.
- eine kopierte Evidence von anderer Maschine oder anderem Commit blockiert die Freigabe.
- neue separate Regressionstests decken Repository-Normalisierung, exakten Check-Satz, Schema v3, Head-/Maschinen-Reuse, Worktree-Drift, Engine-Typen und Freshness ab.

### Erwartete Wirkung

- deutlich geringeres Risiko kopierter Readiness-Evidence
- kein Runner-Enable aus einem anderen Checkout
- kein Runner-Enable nach uncommitteten Änderungen seit Readiness
- fehlende oder erfundene Checks werden fail-closed behandelt
- zentrale Contract-Logik reduziert Drift zwischen Collector und Admin-Gate
- bessere Nachvollziehbarkeit bei realen Runner-Fehlern
- höhere Codequalität durch getrennte Identity-, Contract- und Collector-Schichten

### Technischer Effekt

```text
READINESS SCHEMA v3
→ repo binding
→ HEAD binding
→ machine binding
→ exact checks
→ UE 5.8
→ freshness

ENABLE GATE
→ live repo re-check
→ live HEAD re-check
→ live machine re-check
→ live clean-worktree re-check
→ central contract
→ UE58_RUNNER_ENABLED=true / BLOCKED
```

### Aktueller belegter Zustand

- PR #4: gemergt
- PR #5 Infrastructure Evidence Bundle: gemergt
- `main` nach PR #5: `c0d26b925e39e119f22a04722a815e9c21c65b2b`
- Runner Identity Layer: implementiert
- Readiness Contract v3: implementiert
- Collector auf v3 umgestellt: implementiert
- Admin-Freigabegate auf Kontextbindung umgestellt: implementiert
- Runner-Bindungs-Regressionstests: implementiert
- reales GitHub-P0-Ruleset: weiterhin nicht nachgewiesen
- realer Self-hosted UE-5.8-Runner: weiterhin nicht nachgewiesen
- echter `RUNNER_READINESS: PASS`: weiterhin offen
- CP1 Runtime: `UNOBSERVED/BLOCKED`

### Fertig, wenn

- Hosted `static-and-contract` PASS ist
- Hosted `repository-quality` inklusive Runner-Bindungs-Regressionen PASS ist
- ein realer UE-5.8-Runner Schema-v3-Evidence mit `RUNNER_READINESS: PASS` erzeugt
- dieselbe Maschine im selben sauberen Checkout die Evidence innerhalb von 30 Minuten erneut validiert
- erst danach `UE58_RUNNER_ENABLED=true` technisch freigegeben werden kann

### Detailanleitung

Siehe `Docs/GITHUB_P0_SETUP.md`, `Docs/PROJEKTSTATUS.md` und Issue #2. Ein realer Readiness-PASS bleibt ausdrücklich getrennt vom späteren CP1-Runtime-PASS.
