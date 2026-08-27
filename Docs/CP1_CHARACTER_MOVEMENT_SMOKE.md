# CP1 Character Spawn + Movement Smoke

## Runtime intent

The first real CP1 runtime test is `BunkerBeats.CP1.CharacterSpawnMovement`.

It:
1. requires a real PIE/Game world;
2. spawns a real `ACharacter`;
3. calls `AddMovementInput`;
4. waits for a real runtime tick;
5. verifies position displacement;
6. destroys the temporary character;
7. emits an explicit pass/failure event.

A mock transform change is never accepted as movement evidence.

## Why latent waiting?

Character movement is consumed during runtime ticks. The smoke test therefore waits for the engine rather than invoking protected movement internals.

Epic documents `ACharacter` movement through `MoveForward`/`MoveRight` and `AddMovementInput`, and its automation system supports latent/runtime test workflows. citeturn199315search4turn199315search2

## Runtime validation status

This package contains the test and wiring, but the actual UE 5.8 execution is not claimed as validated until the project is run with Unreal 5.8.
