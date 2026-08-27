from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
EVENT_DIR = ROOT / "Diagnostics/Events"
REPORT_DIR = ROOT / "Diagnostics/Launcher"


def _ensure_event_storage():
    EVENT_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_report_storage():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class DiagnosticEvent:
    event_id: str
    timestamp: str
    run_id: str
    code: str
    severity: str
    phase: str
    title: str
    message: str
    cause: str
    action: str
    status: str
    detail: dict


class EventLogger:
    def __init__(self, run_id=None, console=None):
        self.run_id = run_id or str(uuid.uuid4())
        self.console = console or (lambda _: None)
        self.events = []

    def emit(
        self,
        code,
        severity,
        phase,
        title,
        message,
        cause="",
        action="",
        status="INFO",
        detail=None,
    ):
        event = DiagnosticEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            run_id=self.run_id,
            code=code,
            severity=severity,
            phase=phase,
            title=title,
            message=message,
            cause=cause,
            action=action,
            status=status,
            detail=detail or {},
        )
        self.events.append(event)
        self.console(f"[{severity}] [{code}] {title}: {message}")
        _ensure_event_storage()
        with (EVENT_DIR / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
        return event

    def report(self, summary):
        _ensure_report_storage()
        path = REPORT_DIR / f"run_{self.run_id}.json"
        path.write_text(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "summary": summary,
                    "events": [asdict(event) for event in self.events],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return path

    def exception(self, code, phase, title, exc, action=""):
        return self.emit(
            code,
            "ERROR",
            phase,
            title,
            str(exc),
            cause=f"{type(exc).__name__}: {exc}",
            action=action,
            status="ERROR",
            detail={"traceback": traceback.format_exc()},
        )
