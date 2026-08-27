from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "Diagnostics/Runtime/CP1_runtime_evidence.json"

REQUIRED_METRICS = (
    "frame_samples",
    "frame_time_ms_avg",
    "position_before",
    "position_after",
    "velocity",
    "speed_cm_s",
    "displacement_cm",
    "movement_component",
)


def main() -> int:
    if not EVIDENCE.exists():
        print("CP1_GATE: BLOCKED - runtime evidence missing")
        return 3

    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    telemetry = data.get("telemetry") or {}
    missing = [key for key in REQUIRED_METRICS if key not in telemetry]

    checks = {
        "runtime_status_green": data.get("status") == "GREEN",
        "telemetry_complete": not missing,
        "frame_samples_positive": (telemetry.get("frame_samples") or 0) > 0,
        "frame_time_positive": (telemetry.get("frame_time_ms_avg") or 0) > 0,
        "displacement_positive": (telemetry.get("displacement_cm") or 0) > 0.01,
        "movement_component_valid": bool((telemetry.get("movement_component") or {}).get("valid")),
    }
    failed = [name for name, ok in checks.items() if not ok]
    result = {
        "checkpoint": "CP1",
        "status": "GREEN" if not failed else "RED",
        "checks": checks,
        "missing_metrics": missing,
        "failed": failed,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "GREEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
