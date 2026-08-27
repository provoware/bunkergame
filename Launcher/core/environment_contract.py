from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SUMMARY_SCHEMA_VERSION = 2
VALID_STATUSES = {"GREEN", "YELLOW", "RED"}
STATUS_LABELS = {
    "GREEN": "🟢 ALLES BEREIT",
    "YELLOW": "🟡 TEILWEISE / BLOCKIERT",
    "RED": "🔴 KRITISCHER FEHLER",
}


def normalize_finding(item: Any) -> dict[str, Any] | None:
    """Normalize one finding from the current or legacy payload shape."""
    if isinstance(item, Mapping):
        fid = item.get("id") or item.get("title") or item.get("code")
        status = item.get("status")
        message = item.get("message")
        detail = item.get("detail", {})
    elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)) and len(item) >= 3:
        fid = item[0]
        status = item[1]
        message = item[2]
        detail = item[3] if len(item) >= 4 else {}
    else:
        return None

    if not isinstance(fid, str) or not fid.strip():
        return None
    if status not in VALID_STATUSES:
        return None
    if not isinstance(message, str):
        message = str(message) if message is not None else "Keine Beschreibung verfügbar."
    if not isinstance(detail, Mapping):
        detail = {"raw": str(detail)}

    return {
        "id": fid.strip(),
        "status": status,
        "message": message,
        "detail": dict(detail),
    }


def serialize_findings(findings: Sequence[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in findings:
        normalized = normalize_finding(item)
        if normalized is None:
            raise ValueError(f"Ungültiger Environment-Finding-Eintrag: {item!r}")
        rows.append(normalized)
    return rows


def derive_overall(findings: Sequence[Any]) -> str:
    statuses: list[str] = []
    for item in findings:
        normalized = normalize_finding(item)
        if normalized is not None:
            statuses.append(normalized["status"])
    if "RED" in statuses:
        return "RED"
    if "YELLOW" in statuses:
        return "YELLOW"
    return "GREEN" if statuses else "RED"


def _issue_fallback(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    issues = summary.get("issues", [])
    if not isinstance(issues, Sequence) or isinstance(issues, (str, bytes)):
        return []
    rows: list[dict[str, Any]] = []
    for item in issues:
        normalized = normalize_finding(item)
        if normalized is not None:
            rows.append(normalized)
    return rows


def normalize_result_payload(payload: Any) -> dict[str, Any]:
    """Return a fail-safe presentation state for GUI/CLI consumers.

    New payloads prefer summary.after. For backwards compatibility, summary.before
    and finally summary.issues are accepted. Missing/malformed payloads never raise.
    """
    warnings: list[str] = []
    if not isinstance(payload, Mapping):
        return {
            "overall": "RED",
            "label": STATUS_LABELS["RED"],
            "phase": "none",
            "rows": [],
            "warnings": ["Ergebnisdaten fehlen oder haben ein ungültiges Format."],
        }

    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        return {
            "overall": "RED",
            "label": STATUS_LABELS["RED"],
            "phase": "none",
            "rows": [],
            "warnings": ["Die Ergebniszusammenfassung fehlt. Bitte Diagnosebericht prüfen."],
        }

    phase = "none"
    rows: list[dict[str, Any]] = []
    for candidate in ("after", "before"):
        raw = summary.get(candidate)
        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
            phase = candidate
            for item in raw:
                normalized = normalize_finding(item)
                if normalized is None:
                    warnings.append(f"Ungültiger Eintrag in summary.{candidate} wurde übersprungen.")
                else:
                    rows.append(normalized)
            break

    if phase == "none":
        fallback = _issue_fallback(summary)
        if fallback:
            phase = "issues"
            rows = fallback
            warnings.append("Nachvalidierung fehlt; es werden nur bekannte Restprobleme angezeigt.")
        else:
            warnings.append("Vor-/Nachvalidierungsdaten fehlen. Der Lauf ist nicht vollständig auswertbar.")

    overall = summary.get("overall")
    if overall not in VALID_STATUSES:
        overall = derive_overall(rows)
        warnings.append("Gesamtstatus fehlte oder war ungültig und wurde aus den Prüfdaten abgeleitet.")

    return {
        "overall": overall,
        "label": STATUS_LABELS[overall],
        "phase": phase,
        "rows": rows,
        "warnings": warnings,
    }
