from __future__ import annotations
import json, threading, queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

ROOT=Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0,str(ROOT/"Launcher/core"))
from diagnostic_engine import DiagnosticEngine
from pipeline import Pipeline

class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BUNKER BEATS — Intelligent Start")
        self.geometry("1080x720")
        self.minsize(900,620)
        self.engine=DiagnosticEngine(ROOT)
        self.q=queue.Queue()
        self.findings=[]
        self._build()
        self.after(100,self._poll)
        self.scan()

    def _build(self):
        top=ttk.Frame(self,padding=14); top.pack(fill="x")
        ttk.Label(top,text="BUNKER BEATS",font=("TkDefaultFont",22,"bold")).pack(anchor="w")
        ttk.Label(top,text="Intelligenter Start • Diagnose • Reparatur • Test • CP-Gates").pack(anchor="w")
        toolbar=ttk.Frame(self,padding=(14,0,14,8)); toolbar.pack(fill="x")
        ttk.Button(toolbar,text="① Umgebung prüfen",command=self.scan).pack(side="left",padx=4)
        ttk.Button(toolbar,text="② Core QA starten",command=lambda:self.run(["--core"])).pack(side="left",padx=4)
        ttk.Button(toolbar,text="③ Unreal CP1",command=lambda:self.run(["--unreal-build","--unreal-test"])).pack(side="left",padx=4)
        ttk.Button(toolbar,text="④ Full Validation",command=lambda:self.run(["--unreal-build","--unreal-test","--package"])).pack(side="left",padx=4)

        main=ttk.PanedWindow(self,orient="horizontal"); main.pack(fill="both",expand=True,padx=14,pady=6)
        left=ttk.Frame(main,padding=8); right=ttk.Frame(main,padding=8)
        main.add(left,weight=1); main.add(right,weight=2)
        ttk.Label(left,text="Ampel / Anforderungen",font=("TkDefaultFont",12,"bold")).pack(anchor="w")
        self.tree=ttk.Treeview(left,columns=("status","message"),show="headings",height=24)
        self.tree.heading("status",text="Status"); self.tree.heading("message",text="Einfache Erklärung")
        self.tree.column("status",width=80,anchor="center"); self.tree.column("message",width=390)
        self.tree.pack(fill="both",expand=True,pady=8)

        ttk.Label(right,text="Live-Ausgabe",font=("TkDefaultFont",12,"bold")).pack(anchor="w")
        self.output=tk.Text(right,wrap="word",state="disabled",height=30)
        self.output.pack(fill="both",expand=True)
        bottom=ttk.Frame(right,padding=(0,8,0,0)); bottom.pack(fill="x")
        self.gate_var=tk.StringVar(value="Noch nicht geprüft")
        ttk.Label(bottom,textvariable=self.gate_var,font=("TkDefaultFont",13,"bold")).pack(anchor="w")
        self.progress=ttk.Progressbar(bottom,mode="indeterminate"); self.progress.pack(fill="x",pady=6)

    def log(self,msg):
        self.q.put(("log",str(msg)))

    def scan(self):
        self.clear_output()
        self.log("Prüfung gestartet. Ich prüfe zuerst das Projekt, die Werkzeuge und die Smoke-Konfiguration.")
        findings=self.engine.scan()
        self.findings=findings
        for item in self.tree.get_children(): self.tree.delete(item)
        for f in findings:
            self.tree.insert("","end",values=(f.status,f"{f.title}: {f.message}"))
        overall=self.engine.overall(findings)
        self.gate_var.set(f"Gesamtstatus: {'🟢 BEREIT' if overall=='GREEN' else ('🟡 TEILWEISE BEREIT' if overall=='YELLOW' else '🔴 BLOCKIERT')}")
        data=self.engine.report(findings)
        self.log(f"Diagnose abgeschlossen: {overall}")
        for f in findings:
            self.log(f"[{f.status}] {f.title}: {f.message}")
        if overall=="YELLOW":
            self.log("Hinweis: Ein gelber Zustand wird niemals stillschweigend als Erfolg behandelt.")

    def clear_output(self):
        self.output.configure(state="normal"); self.output.delete("1.0","end"); self.output.configure(state="disabled")

    def run(self,args):
        self.progress.start(12)
        self.log("Startroutine läuft. Kein Ergebnis wird vor Abschluss des jeweiligen Gates als erfolgreich angezeigt.")
        def work():
            p=Pipeline(log_cb=self.log)
            result=p.run(args)
            self.q.put(("done",result))
        threading.Thread(target=work,daemon=True).start()

    def _poll(self):
        try:
            while True:
                typ,payload=self.q.get_nowait()
                if typ=="log":
                    self.output.configure(state="normal"); self.output.insert("end",payload+"\n"); self.output.see("end"); self.output.configure(state="disabled")
                elif typ=="done":
                    self.progress.stop()
                    status=payload["status"]
                    self.gate_var.set(f"Pipeline-Ergebnis: {'🟢 PASS' if status=='GREEN' else ('🟡 BLOCKED/INCOMPLETE' if status=='YELLOW' else '🔴 FAIL')}")
                    if status=="GREEN":
                        self.scan()
                    elif status=="RED":
                        messagebox.showerror("BUNKER BEATS", "Ein angeforderter Schritt ist fehlgeschlagen. Siehe Live-Ausgabe und Report.")
                    else:
                        messagebox.showwarning("BUNKER BEATS", "Die angeforderte Prüfung konnte nicht vollständig ausgeführt werden.")
        except queue.Empty:
            pass
        self.after(100,self._poll)

if __name__=="__main__":
    LauncherApp().mainloop()
