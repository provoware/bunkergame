from pathlib import Path
import queue
import sys
import threading
import traceback
import tkinter as tk
from tkinter import ttk

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Launcher/core"))

from assistant import EnvironmentAssistant
from environment_contract import normalize_result_payload


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BUNKER BEATS — Environment Doctor")
        self.geometry("1180x760")
        self.minsize(960, 650)
        self.q = queue.Queue()
        self.running = False
        self.build()
        self.after(100, self.poll)
        self.run(False)

    def build(self):
        head = ttk.Frame(self, padding=14)
        head.pack(fill="x")
        ttk.Label(head, text="BUNKER BEATS", font=("TkDefaultFont", 22, "bold")).pack(anchor="w")
        ttk.Label(
            head,
            text="Environment Doctor • Vorprüfung • sichere Reparatur • Nachvalidierung",
        ).pack(anchor="w")

        bar = ttk.Frame(self, padding=(14, 0, 14, 8))
        bar.pack(fill="x")
        self.check_button = ttk.Button(bar, text="① Prüfen", command=lambda: self.run(False))
        self.check_button.pack(side="left", padx=4)
        self.repair_button = ttk.Button(
            bar,
            text="② Sicher reparieren",
            command=lambda: self.run(True),
        )
        self.repair_button.pack(side="left", padx=4)

        pan = ttk.PanedWindow(self, orient="horizontal")
        pan.pack(fill="both", expand=True, padx=14, pady=8)
        left = ttk.Frame(pan, padding=8)
        right = ttk.Frame(pan, padding=8)
        pan.add(left, weight=1)
        pan.add(right, weight=2)

        ttk.Label(left, text="Anforderungen / Ampel", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        self.tree = ttk.Treeview(
            left,
            columns=("status", "area", "message"),
            show="headings",
        )
        for col, title, width in [
            ("status", "Status", 90),
            ("area", "Bereich", 150),
            ("message", "Einfache Erklärung", 430),
        ]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width)
        self.tree.pack(fill="both", expand=True)

        ttk.Label(
            right,
            text="Detailereignisse / Debugging",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w")
        self.output = tk.Text(right, wrap="word", state="disabled")
        self.output.pack(fill="both", expand=True)
        self.status = tk.StringVar(value="Prüfung läuft …")
        ttk.Label(
            right,
            textvariable=self.status,
            font=("TkDefaultFont", 13, "bold"),
        ).pack(anchor="w", pady=6)

    def _set_busy(self, busy: bool, text: str | None = None):
        self.running = busy
        state = "disabled" if busy else "normal"
        self.check_button.configure(state=state)
        self.repair_button.configure(state=state)
        if text:
            self.status.set(text)

    def _append_output(self, message: str):
        self.output.configure(state="normal")
        self.output.insert("end", str(message) + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def log(self, msg):
        self.q.put(("log", msg))

    def run(self, repair):
        if self.running:
            self._append_output("[INFO] Eine Prüfung läuft bereits. Bitte den Abschluss abwarten.")
            return

        self._set_busy(
            True,
            "Sichere Reparatur + Nachvalidierung läuft …" if repair else "Vor- und Nachprüfung läuft …",
        )

        def worker():
            try:
                result = EnvironmentAssistant(console=self.log).run(repair=repair)
            except Exception as exc:  # GUI must survive all worker failures
                self.q.put(
                    (
                        "error",
                        {
                            "message": f"Die Startroutine wurde unerwartet abgebrochen: {exc}",
                            "traceback": traceback.format_exc(),
                        },
                    )
                )
                return
            self.q.put(("result", result))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_result(self, payload):
        view = normalize_result_payload(payload)
        self.status.set(view["label"])
        self.tree.delete(*self.tree.get_children())

        for row in view["rows"]:
            self.tree.insert(
                "",
                "end",
                values=(row["status"], row["id"], row["message"]),
            )

        if not view["rows"]:
            self.tree.insert(
                "",
                "end",
                values=("RED", "ERGEBNIS", "Keine auswertbaren Prüfdaten vorhanden."),
            )

        phase_text = {
            "after": "Nachvalidierung angezeigt.",
            "before": "Nur Vorprüfung verfügbar; Nachvalidierung fehlt.",
            "issues": "Nur bekannte Restprobleme verfügbar.",
            "none": "Keine vollständigen Prüfdaten verfügbar.",
        }[view["phase"]]
        self._append_output(f"[INFO] {phase_text}")
        for warning in view["warnings"]:
            self._append_output(f"[WARNING] {warning}")

        self._set_busy(False)

    def _apply_error(self, payload):
        message = "Unbekannter Fehler in der Startroutine."
        detail = ""
        if isinstance(payload, dict):
            message = str(payload.get("message") or message)
            detail = str(payload.get("traceback") or "")

        self.status.set("🔴 STARTROUTINE ABGEBROCHEN")
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", "end", values=("RED", "START", message))
        self._append_output(f"[ERROR] {message}")
        if detail:
            self._append_output(detail)
        self._set_busy(False)

    def poll(self):
        try:
            while True:
                typ, payload = self.q.get_nowait()
                try:
                    if typ == "log":
                        self._append_output(str(payload))
                    elif typ == "result":
                        self._apply_result(payload)
                    elif typ == "error":
                        self._apply_error(payload)
                    else:
                        self._append_output(f"[WARNING] Unbekanntes GUI-Ereignis: {typ}")
                except Exception:
                    # A malformed single event must never kill Tk's polling callback.
                    self.status.set("🔴 DARSTELLUNGSFEHLER")
                    self._append_output("[ERROR] Ergebnis konnte nicht dargestellt werden.")
                    self._append_output(traceback.format_exc())
                    self._set_busy(False)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.poll)


if __name__ == "__main__":
    App().mainloop()
