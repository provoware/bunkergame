using UnrealBuildTool;
using System.Collections.Generic;

public class BunkerBeatsEditorTarget : TargetRules
{
    public BunkerBeatsEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        ExtraModuleNames.Add("BunkerBeats");
    }
}
