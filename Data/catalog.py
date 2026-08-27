
from multitask_api import *
A=[
("Kabelmagnet","TECH",{"POWER","SETUP"},1,0,0),
("Improvisationskönig","RECOVERY",{"POWER","FAILURE"},1,0,5),
("Bass-Geflüster","CROWD",{"SOCIAL"},0,0,4),
("Menschenkenntnis","SOCIAL",{"SOCIAL"},1,-1,6),
("Trash-Magnet","DISCOVERY",{"DISCOVERY"},0,0,4),
("Deadline-Dämon","TIME",{"TIMED"},1,0,5),
("Ersatzteil-Orakel","RESOURCE",{"RESOURCE","POWER"},1,-1,8),
("Crowd-Flüsterer","CROWD",{"SOCIAL"},0,0,6),
("Bühnenbastler","CREATIVE",{"SETUP"},1,0,5),
("Risiko-Rocker","RISK",{"RISK","POWER"},2,3,10),
("Notfallknopf","RECOVERY",{"FAILURE","RISK"},1,-2,3),
("Gerüchteküche","SOCIAL_INTEL",{"SOCIAL"},1,0,5),
("Sound-Sommelier","MUSIC",{"TIMED"},1,0,5),
("Bunkerkarte im Kopf","EXPLORATION",{"DISCOVERY"},1,0,5),
("Rivalen-Stichelei","RIVAL",{"RIVAL"},0,1,8),
("Crowd-Bait","CROWD",{"SOCIAL","RISK"},0,1,8),
("Silent Operator","SETUP",{"SETUP"},1,-1,6),
("Charmeoffensive","SOCIAL",{"SOCIAL"},1,0,7),
("Fehlerfinder","DIAGNOSTIC",{"POWER","FAILURE"},1,-2,5),
("Letzte-Platte-Prinzip","PERFORMANCE",{"PERFORMANCE"},1,0,7),
]
ABILITIES={}
for i,(name,cat,tags,pb,rd,rb) in enumerate(A,1):
    aid=f"ABILITY_{i:02d}"
    ABILITIES[aid]=AbilityDefinition(aid,name,cat,frozenset(tags),pb,rd,rb)

CHARACTERS={
    "Pppoppi":CharacterDefinition("Pppoppi","Pppoppi Poppsen von Bückstücken","Improvisationsbeauftragter."),
    "Atze":CharacterDefinition("Atze","Atze","Selbsternannter Event-Qualitätsmanager.")
}

TASK_SPECS=[
("INT_POWER","Stromkasten","Bunker-Strom wiederbeleben","tech",1,3,50,{"POWER"},0),
("INT_SETUP","Licht-Rig","Licht-Rig aufbauen","creative",1,3,55,{"SETUP"},1),
("INT_TIMED","Kabelweg","Kabelweg unter Zeitdruck sichern","tech",1,4,45,{"TIMED"},4),
("INT_RESOURCE","Ersatzteile","Ersatzteilkiste sinnvoll vorbereiten","tech",1,3,40,{"RESOURCE"},2),
("INT_SOCIAL","Türpolitik","Einlass-Team koordinieren","social",1,3,60,{"SOCIAL"},3),
("INT_RISK","Notstrom","Notstromkreis unter Risiko testen","tech",1,4,70,{"RISK"},10),
]
INTERACTIONS={}
TASKS={}
for iid,name,tname,skill,level,progress,reward,tags,risk in TASK_SPECS:
    tid="TASK_"+iid[4:]
    INTERACTIONS[iid]=InteractionPoint(iid,name,f"{name}: {tname}.",tid)
    TASKS[tid]=TaskDefinition(tid,tname,tname,skill,level,progress,reward,iid,frozenset(tags),risk)

def create_api(): return GameplayAPI(CHARACTERS,ABILITIES,INTERACTIONS,TASKS)
