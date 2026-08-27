from pathlib import Path
import json
import time

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "Diagnostics/Regression"
HISTORY = REG / "knowledge.jsonl"
INSIGHTS = REG / "REGRESSION_INSIGHTS.md"


def _ensure_storage():
    REG.mkdir(parents=True, exist_ok=True)


def record(run_id, summary):
    _ensure_storage()
    row = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "run_id": run_id,
        "summary": summary,
    }
    with HISTORY.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def derive():
    rows = []
    if HISTORY.exists():
        for line in HISTORY.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    counts = {}
    for row in rows:
        for issue in row.get("summary", {}).get("issues", []):
            code = issue.get("code", "UNKNOWN")
            counts[code] = counts.get(code, 0) + 1

    lines = [
        "# Regression Insights",
        "",
        f"Runs recorded: {len(rows)}",
        "",
        "## Wiederkehrende Erkenntnisse",
    ]
    if counts:
        for code, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- **{code}**: {count} Lauf/Läufe betroffen.")
    else:
        lines.append("- Noch keine wiederkehrenden Regressionserkenntnisse.")

    lines += [
        "",
        "## Präventionsregel",
        "Wiederkehrende Fehler müssen als dauerhafte Prävention in Preflight, Tests oder Architektur überführt werden.",
    ]
    _ensure_storage()
    INSIGHTS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return counts
