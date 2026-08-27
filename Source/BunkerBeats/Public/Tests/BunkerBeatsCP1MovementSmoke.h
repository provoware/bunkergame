
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Tests/BunkerBeatsCP1MovementSmoke.generated.h"

/**
 * Minimal real runtime character used only by CP1 smoke automation.
 *
 * The class deliberately uses ACharacter + UCharacterMovementComponent
 * so CP1 exercises the same engine movement pipeline as gameplay.
 * It is test infrastructure, not a player-facing gameplay character.
 */
UCLASS()
class BUNKERBEATS_API ABunkerBeatsCP1MovementSmokeCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ABunkerBeatsCP1MovementSmokeCharacter();

    /** Marks the test character with an identifiable runtime tag. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="BunkerBeats|Smoke")
    bool bCP1SmokeCharacter = true;
};
