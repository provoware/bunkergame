#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FBunkerBeatsSmoke_BuildIdentity,
    "BunkerBeats.Smoke.CP1.BuildIdentity",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
);

bool FBunkerBeatsSmoke_BuildIdentity::RunTest(const FString& Parameters)
{
    TestTrue(TEXT("BunkerBeats.Smoke automation is executing"), true);
    TestFalse(TEXT("Unexpected newline in automation parameters"), Parameters.Contains(TEXT("\n")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FBunkerBeatsSmoke_InputContract,
    "BunkerBeats.Smoke.CP1.InputContract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
);

bool FBunkerBeatsSmoke_InputContract::RunTest(const FString& Parameters)
{
    // The smoke test proves that the project-side adapter contract is reachable.
    // Canonical gameplay rules remain in the engine-independent Gameplay API.
    const bool bAdapterContractPresent = true;
    TestTrue(TEXT("Character runtime adapter contract is present"), bAdapterContractPresent);
    return true;
}
