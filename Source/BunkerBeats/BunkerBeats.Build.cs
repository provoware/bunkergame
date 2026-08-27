using UnrealBuildTool;

public class BunkerBeats : ModuleRules
{
    public BunkerBeats(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core","CoreUObject","Engine","InputCore","EnhancedInput","FunctionalTesting"
        });
    }
}
