
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum
from typing import FrozenSet, Mapping, Sequence

class ResultCode(str, Enum):
    OK="OK"; INVALID_ARGUMENT="INVALID_ARGUMENT"; NOT_FOUND="NOT_FOUND"; PRECONDITION_FAILED="PRECONDITION_FAILED"

@dataclass(frozen=True)
class SkillSet:
    tech:int=1; creative:int=1; social:int=1; performance:int=1

@dataclass(frozen=True)
class AbilityDefinition:
    ability_id:str
    name:str
    category:str
    task_tags:FrozenSet[str]
    progress_bonus:int=0
    risk_delta:int=0
    reward_bonus:int=0

@dataclass(frozen=True)
class CharacterDefinition:
    character_id:str; display_name:str; bio:str

@dataclass(frozen=True)
class CharacterState:
    definition_id:str
    selected_abilities:FrozenSet[str]
    skills:SkillSet=SkillSet()
    xp:int=0
    reputation:int=0

@dataclass(frozen=True)
class InteractionPoint:
    interaction_id:str
    name:str
    description:str
    task_id:str

@dataclass(frozen=True)
class TaskDefinition:
    task_id:str
    name:str
    description:str
    required_skill:str
    required_level:int
    base_progress:int
    reward_xp:int
    interaction_id:str
    tags:FrozenSet[str]
    base_risk:int=0

@dataclass(frozen=True)
class TaskState:
    task_id:str
    status:str="AVAILABLE"
    progress:int=0
    max_progress:int=1
    risk:int=0
    reward_xp:int=0

@dataclass(frozen=True)
class GameEvent:
    event_id:str
    message:str
    payload:Mapping[str,object]

@dataclass(frozen=True)
class CommandResult:
    code:ResultCode
    state:CharacterState|None=None
    task:TaskState|None=None
    events:tuple[GameEvent,...]=()
    reason:str=""

class GameplayAPI:
    def __init__(self,characters,abilities,interactions,tasks):
        self.characters=dict(characters)
        self.abilities=dict(abilities)
        self.interactions=dict(interactions)
        self.tasks=dict(tasks)

    def create_character_state(self,character_id,ability_ids)->CommandResult:
        if character_id not in self.characters:
            return CommandResult(ResultCode.NOT_FOUND,reason="Character ID not found.")
        selected=frozenset(ability_ids)
        if len(selected)!=2:
            return CommandResult(ResultCode.INVALID_ARGUMENT,
                reason="Exactly two different Special Abilities are required.")
        if any(a not in self.abilities for a in selected):
            return CommandResult(ResultCode.NOT_FOUND,reason="Unknown ability ID.")
        return CommandResult(ResultCode.OK,state=CharacterState(character_id,selected))

    def _modifiers(self,state,task):
        progress=0; risk=task.base_risk; reward=task.reward_xp; used=[]
        for aid in state.selected_abilities:
            a=self.abilities[aid]
            if task.tags & a.task_tags:
                progress += a.progress_bonus
                risk += a.risk_delta
                reward += a.reward_bonus
                used.append(aid)
        return progress,max(0,risk),max(0,reward),used

    def start_task(self,state,interaction_id)->CommandResult:
        interaction=self.interactions.get(interaction_id)
        if not interaction:
            return CommandResult(ResultCode.NOT_FOUND,state=state,reason="Interaktionspunkt nicht gefunden.")
        task=self.tasks.get(interaction.task_id)
        if not task:
            return CommandResult(ResultCode.NOT_FOUND,state=state,reason="Aufgabe nicht gefunden.")
        skill=getattr(state.skills,task.required_skill,None)
        if skill is None:
            return CommandResult(ResultCode.INVALID_ARGUMENT,state=state,reason="Unbekannter Skill.")
        if skill<task.required_level:
            return CommandResult(ResultCode.PRECONDITION_FAILED,state=state,
                reason=f"{task.required_skill} Stufe {task.required_level} benötigt.")
        progress,risk,reward,used=self._modifiers(state,task)
        return CommandResult(ResultCode.OK,state=state,
            task=TaskState(task.task_id,"ACTIVE",0,max(1,task.base_progress),risk,reward),
            events=(GameEvent("TASK.STARTED",f"„{task.name}“ gestartet.",
                {"task_id":task.task_id,"ability_effects":used,"risk":risk,"reward_xp":reward}),))

    def advance_task(self,state,task,base_progress=1)->CommandResult:
        if task.status!="ACTIVE":
            return CommandResult(ResultCode.PRECONDITION_FAILED,state=state,task=task,
                reason="Nur aktive Aufgaben können fortgeführt werden.")
        definition=self.tasks.get(task.task_id)
        if not definition:
            return CommandResult(ResultCode.NOT_FOUND,state=state,task=task,reason="Task nicht gefunden.")
        bonus,risk,reward,used=self._modifiers(state,definition)
        progress=min(task.max_progress,task.progress+max(1,base_progress+bonus))
        updated=replace(task,progress=progress,risk=risk,reward_xp=reward)
        event_id="TASK.PROGRESS.MAX" if progress>=task.max_progress else "TASK.PROGRESS.UPDATED"
        message=f"Aufgabe bei {progress}/{task.max_progress}."
        return CommandResult(ResultCode.OK,state=state,task=updated,
            events=(GameEvent(event_id,message,
                {"task_id":task.task_id,"progress":progress,"risk":risk,"ability_effects":used}),))

    def complete_task(self,state,task)->CommandResult:
        if task.status!="ACTIVE":
            return CommandResult(ResultCode.PRECONDITION_FAILED,state=state,task=task,
                reason="Nur aktive Aufgaben können abgeschlossen werden.")
        if task.progress<task.max_progress:
            return CommandResult(ResultCode.PRECONDITION_FAILED,state=state,task=task,
                reason=f"Aufgabe noch nicht fertig ({task.progress}/{task.max_progress}).")
        done=replace(task,status="COMPLETED")
        new=replace(state,xp=state.xp+task.reward_xp)
        return CommandResult(ResultCode.OK,state=new,task=done,events=(
            GameEvent("TASK.COMPLETED","Aufgabe abgeschlossen.",
                {"task_id":task.task_id,"reward_xp":task.reward_xp,"final_risk":task.risk}),))
