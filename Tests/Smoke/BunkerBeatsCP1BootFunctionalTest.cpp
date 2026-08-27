#include "BunkerBeatsCP1BootFunctionalTest.h"

ABunkerBeatsCP1BootFunctionalTest::ABunkerBeatsCP1BootFunctionalTest()
{
    TestLabel = TEXT("BunkerBeats CP1 Boot");
    Author = TEXT("BUNKER BEATS QA");
    TimeLimit = 10.0f;
    bIsEnabled = true;
}

void ABunkerBeatsCP1BootFunctionalTest::PrepareTest()
{
    Super::PrepareTest();
}

bool ABunkerBeatsCP1BootFunctionalTest::RunTest()
{
    UWorld* World = GetWorld();
    if (World == nullptr)
    {
        FinishTest(
            EFunctionalTestResult::Failed,
            TEXT("CP1: Unreal World ist nicht verfügbar.")
        );
        return false;
    }

    const FString MapName = World->GetMapName();
    if (MapName.IsEmpty())
    {
        FinishTest(
            EFunctionalTestResult::Failed,
            TEXT("CP1: Keine gültige Test-Map geladen.")
        );
        return false;
    }

    FinishTest(
        EFunctionalTestResult::Succeeded,
        FString::Printf(TEXT("CP1 Boot OK: Map=%s"), *MapName)
    );
    return true;
}
