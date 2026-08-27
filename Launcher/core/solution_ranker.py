
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from solution_outcomes import score as historical_score

ROOT=Path(__file__).resolve().parents[2]
KB_POLICY=json.loads((ROOT/"Config/knowledge_policy.json").read_text(encoding="utf-8"))

@dataclass
class Solution:
    id:str
    title:str
    type:str
    risk:int
    reversibility:int
    effort:int
    evidence:int
    description:str
    action:str
    requires_confirmation:bool

def catalog_for_failure(code):
    if code.startswith("TOOLCHAIN-LINUX-CLANG"):
        return [
            Solution("CLANG-VERIFY","Compiler-Pfad und Version erneut prüfen","diagnose",1,5,1,5,
                     "Prüft PATH, clang-20 und reale Version ohne Systemänderung.",
                     "doctor --deep-clang",False),
            Solution("CLANG-UE-NATIVE","UE-eigene Linux-Toolchain verwenden","repair",2,4,2,5,
                     "Bevorzugter Weg nach installierter UE: native Toolchain des Projekts nutzen.",
                     "SetupToolchain.sh + Re-Scan",True),
            Solution("CLANG-APT","Clang 20 über Distribution bereitstellen","repair",4,4,3,4,
                     "Systemweite Paketinstallation; nur explizit autorisiert.",
                     "apt-get install clang-20 lld-20",True),
        ]
    if code=="TOOLCHAIN-UE-001":
        return [
            Solution("UE-ROOT","Vorhandene UE-5.8-Installation über UE_ROOT registrieren","configuration",1,5,1,5,
                     "Keine Installation; nur eindeutige vorhandene Engine referenzieren.",
                     "export UE_ROOT=<UE_5.8>",True),
            Solution("UE-INSTALL","Verifizierte UE-5.8-Installation bereitstellen","repair",5,2,5,4,
                     "Externe Installation; nur assistiert.",
                     "Installationsanleitung + Verify",True),
        ]
    if code.startswith("RUNTIME-CP1"):
        return [
            Solution("CP1-LOG-TRIAGE","Crash-/Automation-Report analysieren","diagnose",1,5,1,5,
                     "Niedrigstes Risiko, erste Maßnahme.", "collect CP1 evidence",False),
            Solution("CP1-BISECT","Änderung per Git-Bisect eingrenzen","diagnose",2,3,3,5,
                     "Revisionsbezogene Ursache ermitteln.", "git bisect run <test>",True),
            Solution("CP1-ROLLBACK-CANDIDATE","Gezielte Änderung rückgängig machen","repair",4,3,2,3,
                     "Nur als Kandidat; nicht automatisch ausführen.", "review candidate diff",True),
        ]
    if code=="BUILD-FAILED":
        return [
            Solution("BUILD-EVIDENCE","Compiler-/Buildreport analysieren","diagnose",1,5,1,5,
                     "Erstursache vor Änderungen ermitteln.", "collect build evidence",False),
            Solution("BUILD-ATTRIBUTION","Diff-/Commit-Kandidat prüfen","diagnose",1,5,2,4,
                     "Betroffene Änderung identifizieren.", "review attributed commit",False),
        ]
    return [
        Solution("GENERAL-DIAGNOSE","Detaildiagnose ausführen","diagnose",1,5,1,4,
                 "Sichere Erstmaßnahme.", "collect detailed evidence",False),
        Solution("GENERAL_TEST","Gezielten Regressionstest ausführen","diagnose",1,5,2,4,
                 "Fehler reproduzierbar machen.", "run impacted test",False),
    ]

def rank(code):
    sols=catalog_for_failure(code)
    # Higher evidence/reversibility, lower risk/effort.
    scored=[]
    for s in sols:
        base_score=(s.evidence*4)+(s.reversibility*3)-(s.risk*3)-(s.effort*2)
        learned_score,history=historical_score(s.id,code,base_score)
        # Keep the score transparent: base heuristics + historical outcome signal.
        s._learned_score=learned_score
        s._history=history
        scored.append((learned_score,s))
    scored.sort(key=lambda x:(-x[0],x[1].id))
    return [s for _,s in scored]

if __name__=="__main__":
    for s in rank("TOOLCHAIN-LINUX-CLANG-001"):
        print(asdict(s))
