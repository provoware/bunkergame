
from pathlib import Path
import queue, threading, sys, tkinter as tk
from tkinter import ttk
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Launcher/core"))
from assistant import EnvironmentAssistant

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BUNKER BEATS — Environment Doctor")
        self.geometry("1180x760")
        self.minsize(960,650)
        self.q=queue.Queue()
        self.build()
        self.after(100,self.poll)
        self.run(False)

    def build(self):
        head=ttk.Frame(self,padding=14); head.pack(fill="x")
        ttk.Label(head,text="BUNKER BEATS",font=("TkDefaultFont",22,"bold")).pack(anchor="w")
        ttk.Label(head,text="Environment Doctor • Debugging • Repair • Regression-Erkenntnisse").pack(anchor="w")
        bar=ttk.Frame(self,padding=(14,0,14,8)); bar.pack(fill="x")
        ttk.Button(bar,text="① Prüfen",command=lambda:self.run(False)).pack(side="left",padx=4)
        ttk.Button(bar,text="② Sicher reparieren",command=lambda:self.run(True)).pack(side="left",padx=4)

        pan=ttk.PanedWindow(self,orient="horizontal"); pan.pack(fill="both",expand=True,padx=14,pady=8)
        left=ttk.Frame(pan,padding=8); right=ttk.Frame(pan,padding=8)
        pan.add(left,weight=1); pan.add(right,weight=2)
        ttk.Label(left,text="Anforderungen / Ampel",font=("TkDefaultFont",12,"bold")).pack(anchor="w")
        self.tree=ttk.Treeview(left,columns=("status","area","message"),show="headings")
        for col,title,w in [("status","Status",90),("area","Bereich",150),("message","Einfache Erklärung",430)]:
            self.tree.heading(col,text=title); self.tree.column(col,width=w)
        self.tree.pack(fill="both",expand=True)
        ttk.Label(right,text="Detailereignisse / Debugging",font=("TkDefaultFont",12,"bold")).pack(anchor="w")
        self.output=tk.Text(right,wrap="word",state="disabled")
        self.output.pack(fill="both",expand=True)
        self.status=tk.StringVar(value="Prüfung läuft …")
        ttk.Label(right,textvariable=self.status,font=("TkDefaultFont",13,"bold")).pack(anchor="w",pady=6)

    def log(self,msg):
        self.q.put(("log",msg))

    def run(self,repair):
        def worker():
            result=EnvironmentAssistant(console=self.log).run(repair=repair)
            self.q.put(("result",result))
        threading.Thread(target=worker,daemon=True).start()

    def poll(self):
        try:
            while True:
                typ,payload=self.q.get_nowait()
                if typ=="log":
                    self.output.configure(state="normal"); self.output.insert("end",str(payload)+"\n")
                    self.output.see("end"); self.output.configure(state="disabled")
                else:
                    overall=payload["summary"]["overall"]
                    self.status.set({"GREEN":"🟢 ALLES BEREIT","YELLOW":"🟡 TEILWEISE / BLOCKIERT","RED":"🔴 KRITISCHER FEHLER"}[overall])
                    self.tree.delete(*self.tree.get_children())
                    for fid,status,message,detail in payload["summary"]["after"]:
                        self.tree.insert("","end",values=(status,fid,message))
        except queue.Empty:
            pass
        self.after(100,self.poll)

if __name__=="__main__":
    App().mainloop()
