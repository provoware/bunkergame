
#include "Tests/BunkerBeatsCP1MovementSmoke.h"
#include "GameFramework/CharacterMovementComponent.h"

/*
 * CP1 test character:
 * - Uses ACharacter so the real CharacterMovementComponent is present.
 * - Does not introduce gameplay tuning; all movement values remain engine defaults.
 * - Keeps the smoke test deterministic and small.
 */
ABunkerBeatsCP1MovementSmokeCharacter::ABunkerBeatsCP1MovementSmokeCharacter()
{
    PrimaryActorTick.bCanEverTick = false;

    // Explicitly keep the default movement component active. The smoke test
    // verifies movement through the real CharacterMovementComponent path.
    if (GetCharacterMovement())
    {
        GetCharacterMovement()->bOrientRotationToMovement = false;
        GetCharacterMovement()->bRunPhysicsWithNoController = true;
    }
}
