from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Launcher/core"))

from diagnostics import EventLogger
from environment_contract import SUMMARY_SCHEMA_VERSION, derive_overall, serialize_findings
from repair_engine import RepairEngine
import regression_knowledge


class EnvironmentAssistant:
    def __init__(self, console=None):
        self.logger = EventLogger(console=console)
        self.engine = RepairEngine(self.logger)

    def run(self, repair=True):
        self.logger.emit(
            "BOOT-001",
            "INFO",
            "BOOT",
            "Startroutine gestartet",
            "Ich prüfe zuerst Projekt, Werkzeuge und Abhängigkeiten.",
            status="STARTED",
        )

        before_raw = self.engine.scan()
        before = serialize_findings(before_raw)
        repairs = []

        for finding in before_raw:
            fid, status, message, detail = finding
            self.logger.emit(
                f"ENV-{fid}-001",
                "INFO" if status == "GREEN" else ("WARNING" if status == "YELLOW" else "ERROR"),
                "DIAGNOSE",
                fid,
                message,
                cause="Projekt-/Umgebungsprüfung",
                action="Sichere Reparatur prüfen.",
                status=status,
                detail=detail,
            )

            if repair and status != "GREEN":
                action = self.engine.safe_repair(finding)
                repairs.append(action.__dict__)
                if action.status == "REPAIRED":
                    self.logger.emit(
                        action.repair_id,
                        "INFO",
                        "REPAIR",
                        action.title,
                        action.explanation,
                        status="REPAIRED",
                        detail={"changed_paths": action.changed_paths},
                    )

        # Nach jeder Aktion wird vollständig neu geprüft. Auch ein reiner Prüflauf
        # besitzt dadurch eine echte, explizite Nachvalidierung.
        after_raw = self.engine.scan()
        after = serialize_findings(after_raw)
        remaining = [
            {
                "code": f"ENV-{row['id']}-001",
                "title": row["id"],
                "status": row["status"],
                "message": row["message"],
            }
            for row in after
            if row["status"] != "GREEN"
        ]
        overall = derive_overall(after)
        unreal_ready = next(
            (
                bool(row.get("detail", {}).get("available"))
                for row in after
                if row["id"] == "UNREAL"
            ),
            False,
        )

        summary = {
            "schema_version": SUMMARY_SCHEMA_VERSION,
            "overall": overall,
            "repair_requested": bool(repair),
            "before": before,
            "after": after,
            "issues": remaining,
            "repairs": repairs,
            "unreal_ready": unreal_ready,
        }

        self.logger.emit(
            "GATE-001",
            "INFO" if overall == "GREEN" else "WARNING",
            "GATE",
            "Gesamtstatus bestimmt",
            {
                "GREEN": "Alles bereit.",
                "YELLOW": "Das Projekt ist teilweise bereit; mindestens eine Voraussetzung fehlt.",
                "RED": "Ein kritischer Fehler verhindert den Start.",
            }[overall],
            status=overall,
            detail={"remaining": remaining},
        )

        report = self.logger.report(summary)
        regression_knowledge.record(self.logger.run_id, summary)
        regression_knowledge.derive()
        return {"run_id": self.logger.run_id, "summary": summary, "report": str(report)}


if __name__ == "__main__":
    import json

    print(json.dumps(EnvironmentAssistant(console=print).run(), ensure_ascii=False, indent=2))
