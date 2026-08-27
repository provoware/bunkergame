# GITHUB-ADMIN-DIAGNOSE — BRANCH PROTECTION

> Zweck: herausfinden, **warum `main` noch nicht geschützt ist**, ohne zuerst Änderungen an GitHub vorzunehmen.

## 1. SICHERER ERSTER BEFEHL

Im aktuellen Projektordner:

```bash
python3 Scripts/github_p0_admin.py --doctor
```

Dieser Modus ist **read-only**. Er verändert weder Branch Protection noch Repository-Variablen.

Ziel:

```text
GITHUB_ADMIN_PREFLIGHT: PASS
```

Erst danach ist ein Apply sinnvoll.

---

## 2. WAS WIRD GEPRÜFT?

Der Doctor kontrolliert in dieser Reihenfolge:

1. GitHub CLI `gh` vorhanden
2. GitHub-Anmeldung aktiv
3. Zielrepository exakt `provoware/bunkergame`
4. Repository nicht archiviert
5. angemeldetes Konto besitzt `admin=true`
6. Branch `main` existiert
7. aktueller Serverhinweis `main.protected=true/false`

Ein normales Push- oder Maintain-Recht reicht **nicht** als Repository-Adminrecht.

---

## 3. AMPELSYSTEM

### 🟢 `GITHUB_ADMIN_PREFLIGHT: PASS`

Repository, Branch und Repository-Adminrecht wurden bestätigt.

Danach:

```bash
python3 Scripts/github_p0_admin.py --apply
python3 Scripts/github_p0_status.py
```

Ziel:

```text
GITHUB_P0_BRANCH_GATE: PASS
```

### 🔴 `GITHUB_ADMIN_PREFLIGHT: BLOCKED`

Nicht weiter mit `--apply` experimentieren. Zuerst den angezeigten Grund beheben.

---

## 4. FEHLERCODES

### `AUTHORIZATION_403`

**Bedeutung:** GitHub verweigert die Administrationsaktion.

Typische Ursachen:

- falsches GitHub-Konto angemeldet
- Konto besitzt keine Repository-Adminrechte
- Fine-grained Token hat für `Repository Administration` nicht `Read and write`
- GitHub-App-/Integrations-Token besitzt nicht die nötige Administrationsberechtigung

Prüfen:

```bash
gh auth status
gh repo view provoware/bunkergame
python3 Scripts/github_p0_admin.py --doctor
```

### `RESOURCE_404`

**Bedeutung:** Repository, Branch oder Protection-Ressource ist für diese Anmeldung nicht auffindbar.

Prüfen:

```bash
gh repo view provoware/bunkergame
gh api repos/provoware/bunkergame/branches/main
```

### `VALIDATION_422`

**Bedeutung:** GitHub hat die Protection-Konfiguration abgelehnt.

Nicht einzelne Schutzregeln blind deaktivieren. Den vollständigen Fehlertext prüfen; mögliche Ursachen sind ein nicht akzeptiertes Feld oder ein ungültiger Required-Check-Kontext.

### `UNKNOWN_GITHUB_ERROR`

Der Fehler passt nicht sicher zu 403/404/422. Die unveränderte GitHub-Meldung verwenden und nicht raten.

---

## 5. SERVERSTATUS UNABHÄNGIG PRÜFEN

```bash
python3 Scripts/github_p0_status.py
```

Der Prüfer liest zuerst den normalen Branch-Endpunkt.

Wenn GitHub meldet:

```text
main.protected=false
```

ist eindeutig bewiesen, dass Branch Protection noch nicht aktiv ist.

Erst bei:

```text
main.protected=true
```

werden die Detailregeln geprüft:

- Pull Request erforderlich
- Branch vor Merge aktuell
- Admins geschützt
- Force-Push gesperrt
- Branch-Löschen gesperrt
- `static-and-contract` required
- `repository-quality` required

---

## 6. ERST NACH BRANCH-GATE-PASS

Danach auf der echten UE-5.8-Maschine:

```bash
python3 Scripts/p0_preflight.py --full
```

`P0_PREFLIGHT: PASS` und `RUNNER_READINESS: PASS` sind noch **kein CP1-Runtime-PASS**.

Der echte CP1-Beweis bleibt:

```text
UE 5.8 Build
→ Character Spawn
→ Movement
→ Telemetrie
→ CP1 Gate
```
