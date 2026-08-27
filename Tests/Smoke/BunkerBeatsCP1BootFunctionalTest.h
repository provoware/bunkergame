#pragma once

#include "CoreMinimal.h"
#include "FunctionalTest.h"
#include "BunkerBeatsCP1BootFunctionalTest.generated.h"

UCLASS()
class BUNKERBEATS_API ABunkerBeatsCP1BootFunctionalTest : public AFunctionalTest
{
    GENERATED_BODY()

public:
    ABunkerBeatsCP1BootFunctionalTest();

    virtual void PrepareTest() override;
    virtual bool RunTest() override;
};
