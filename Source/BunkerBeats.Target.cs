using UnrealBuildTool;
using System.Collections.Generic;

public class BunkerBeatsTarget : TargetRules
{
    public BunkerBeatsTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        ExtraModuleNames.Add("BunkerBeats");
    }
}
