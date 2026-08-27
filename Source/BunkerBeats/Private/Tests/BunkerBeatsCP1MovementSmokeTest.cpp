#include "Misc/AutomationTest.h"
#include "Tests/BunkerBeatsCP1MovementSmoke.h"
#include "Tests/AutomationCommon.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/PlatformFileManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"

namespace BunkerBeatsCP1
{
constexpr double MinDisplacementCm = 0.01;
constexpr double MovementTimeoutSeconds = 3.0;
constexpr float TestDeltaSeconds = 1.0f / 60.0f;

static FString VectorJson(const FVector& Value)
{
    return FString::Printf(TEXT("[%.6f,%.6f,%.6f]"), Value.X, Value.Y, Value.Z);
}

static void WriteTelemetry(
    const FString& RunId,
    const FVector& Before,
    const FVector& After,
    const FVector& Velocity,
    const double Displacement,
    const int32 FrameSamples,
    const double FrameMsAverage,
    const double FrameMsMin,
    const double FrameMsMax,
    const double WallFrameMsAverage,
    const UCharacterMovementComponent* Movement)
{
    const FString OutputDirectory = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("Automation"));
    FPlatformFileManager::Get().GetPlatformFile().CreateDirectoryTree(*OutputDirectory);
    const FString OutputPath = FPaths::Combine(OutputDirectory, TEXT("CP1_RuntimeTelemetry.json"));

    const FString ComponentClass = Movement ? Movement->GetClass()->GetName() : TEXT("");
    const FString MovementMode = Movement ? UEnum::GetValueAsString(Movement->MovementMode) : TEXT("");
    const double Speed = Velocity.Size();

    const FString Payload = FString::Printf(
        TEXT("{\n")
        TEXT("  \"schema\": \"bunkerbeats.cp1.movement.telemetry.v3\",\n")
        TEXT("  \"run_id\": \"%s\",\n")
        TEXT("  \"frame_samples\": %d,\n")
        TEXT("  \"frame_time_ms_avg\": %.6f,\n")
        TEXT("  \"frame_time_ms_min\": %.6f,\n")
        TEXT("  \"frame_time_ms_max\": %.6f,\n")
        TEXT("  \"wall_frame_time_ms_avg\": %.6f,\n")
        TEXT("  \"position_before\": %s,\n")
        TEXT("  \"position_after\": %s,\n")
        TEXT("  \"velocity\": %s,\n")
        TEXT("  \"speed_cm_s\": %.6f,\n")
        TEXT("  \"displacement_cm\": %.6f,\n")
        TEXT("  \"movement_component\": {\n")
        TEXT("    \"valid\": %s,\n")
        TEXT("    \"active\": %s,\n")
        TEXT("    \"tick_enabled\": %s,\n")
        TEXT("    \"class\": \"%s\",\n")
        TEXT("    \"movement_mode\": \"%s\",\n")
        TEXT("    \"max_walk_speed\": %.6f,\n")
        TEXT("    \"run_physics_without_controller\": %s\n")
        TEXT("  }\n")
        TEXT("}\n"),
        *RunId,
        FrameSamples,
        FrameMsAverage,
        FrameMsMin,
        FrameMsMax,
        WallFrameMsAverage,
        *VectorJson(Before),
        *VectorJson(After),
        *VectorJson(Velocity),
        Speed,
        Displacement,
        Movement ? TEXT("true") : TEXT("false"),
        Movement && Movement->IsActive() ? TEXT("true") : TEXT("false"),
        Movement && Movement->IsComponentTickEnabled() ? TEXT("true") : TEXT("false"),
        *ComponentClass,
        *MovementMode,
        Movement ? Movement->MaxWalkSpeed : 0.0,
        Movement && Movement->bRunPhysicsWithNoController ? TEXT("true") : TEXT("false"));

    FFileHelper::SaveStringToFile(Payload, *OutputPath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
}

class FBunkerBeatsCP1MovementWait final : public IAutomationLatentCommand
{
public:
    FBunkerBeatsCP1MovementWait(
        FAutomationTestBase& InTest,
        TSharedRef<FTestWorldWrapper> InTestWorld,
        TWeakObjectPtr<ABunkerBeatsCP1MovementSmokeCharacter> InCharacter,
        const FVector& InBefore,
        const FString& InRunId)
        : Test(InTest)
        , TestWorld(MoveTemp(InTestWorld))
        , Character(InCharacter)
        , Before(InBefore)
        , RunId(InRunId)
        , StartedSeconds(FPlatformTime::Seconds())
        , LastUpdateSeconds(StartedSeconds)
    {
    }

    virtual bool Update() override
    {
        ABunkerBeatsCP1MovementSmokeCharacter* RuntimeCharacter = Character.Get();
        if (!RuntimeCharacter)
        {
            Test.AddError(TEXT("CP1 movement verification failed: runtime character disappeared before displacement was observed."));
            Cleanup();
            return true;
        }

        const double WallNowSeconds = FPlatformTime::Seconds();
        const double WallDeltaMs = (WallNowSeconds - LastUpdateSeconds) * 1000.0;
        LastUpdateSeconds = WallNowSeconds;

        if (!TestWorld->TickTestWorld(BunkerBeatsCP1::TestDeltaSeconds))
        {
            TestWorld->ForwardErrorMessages(&Test);
            Test.AddError(TEXT("CP1 movement verification failed: temporary test world could not be ticked."));
            Cleanup();
            return true;
        }

        UCharacterMovementComponent* Movement = RuntimeCharacter->GetCharacterMovement();
        const double FrameMs = static_cast<double>(BunkerBeatsCP1::TestDeltaSeconds) * 1000.0;
        ++FrameSamples;
        FrameMsSum += FrameMs;
        FrameMsMin = FMath::Min(FrameMsMin, FrameMs);
        FrameMsMax = FMath::Max(FrameMsMax, FrameMs);
        if (WallDeltaMs > 0.0)
        {
            WallFrameMsSum += WallDeltaMs;
            ++WallFrameSamples;
        }

        const FVector After = RuntimeCharacter->GetActorLocation();
        const FVector Velocity = RuntimeCharacter->GetVelocity();
        const double Distance = FVector::Dist(Before, After);
        const double ElapsedSeconds = WallNowSeconds - StartedSeconds;

        if (Distance > BunkerBeatsCP1::MinDisplacementCm)
        {
            const double AverageMs = FrameMsSum / static_cast<double>(FrameSamples);
            const double WallAverageMs = WallFrameSamples > 0 ? WallFrameMsSum / static_cast<double>(WallFrameSamples) : 0.0;

            BunkerBeatsCP1::WriteTelemetry(
                RunId,
                Before,
                After,
                Velocity,
                Distance,
                FrameSamples,
                AverageMs,
                FrameMsMin,
                FrameMsMax,
                WallAverageMs,
                Movement);

            Test.AddInfo(FString::Printf(
                TEXT("CP1 CharacterSpawnMovement PASS: run_id=%s displacement=%.3fcm speed=%.3fcm/s frames=%d avg_sim_frame=%.3fms component=%s."),
                *RunId,
                Distance,
                Velocity.Size(),
                FrameSamples,
                AverageMs,
                Movement ? *Movement->GetClass()->GetName() : TEXT("missing")));

            Cleanup();
            return true;
        }

        if (ElapsedSeconds >= BunkerBeatsCP1::MovementTimeoutSeconds)
        {
            Test.AddError(FString::Printf(
                TEXT("CP1 movement timeout after %.2fs: no displacement above %.3fcm. MovementComponent=%s Active=%s."),
                ElapsedSeconds,
                BunkerBeatsCP1::MinDisplacementCm,
                Movement ? TEXT("present") : TEXT("missing"),
                Movement && Movement->IsActive() ? TEXT("true") : TEXT("false")));
            Cleanup();
            return true;
        }

        return false;
    }

private:
    void Cleanup()
    {
        if (ABunkerBeatsCP1MovementSmokeCharacter* RuntimeCharacter = Character.Get())
        {
            if (UWorld* World = RuntimeCharacter->GetWorld())
            {
                World->DestroyActor(RuntimeCharacter);
            }
        }
        TestWorld->EndPlayInTestWorld();
        TestWorld->ForwardErrorMessages(&Test);
        TestWorld->DestroyTestWorld(false);
    }

    FAutomationTestBase& Test;
    TSharedRef<FTestWorldWrapper> TestWorld;
    TWeakObjectPtr<ABunkerBeatsCP1MovementSmokeCharacter> Character;
    FVector Before;
    FString RunId;
    double StartedSeconds = 0.0;
    double LastUpdateSeconds = 0.0;
    int32 FrameSamples = 0;
    double FrameMsSum = 0.0;
    double FrameMsMin = TNumericLimits<double>::Max();
    double FrameMsMax = 0.0;
    int32 WallFrameSamples = 0;
    double WallFrameMsSum = 0.0;
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FBunkerBeatsCP1MovementSmokeTest,
    "BunkerBeats.CP1.CharacterSpawnMovement",
    EAutomationTestFlags::EditorContext |
    EAutomationTestFlags::EngineFilter |
    EAutomationTestFlags::ProductFilter)

bool FBunkerBeatsCP1MovementSmokeTest::RunTest(const FString& Parameters)
{
    FString EvidenceRunId;
    if (!FParse::Value(FCommandLine::Get(), TEXT("CP1EvidenceRunId="), EvidenceRunId) || EvidenceRunId.IsEmpty())
    {
        AddError(TEXT("CP1 evidence binding failed: required -CP1EvidenceRunId=<run-id> is missing."));
        return false;
    }

    TSharedRef<FTestWorldWrapper> TestWorld = MakeShared<FTestWorldWrapper>();
    if (!TestWorld->CreateTestWorld(EWorldType::Game))
    {
        TestWorld->ForwardErrorMessages(this);
        AddError(TEXT("CP1 prerequisite failed: temporary Game test world could not be created."));
        return false;
    }
    if (!TestWorld->BeginPlayInTestWorld())
    {
        TestWorld->ForwardErrorMessages(this);
        TestWorld->DestroyTestWorld(false);
        AddError(TEXT("CP1 prerequisite failed: BeginPlay could not start in temporary test world."));
        return false;
    }

    UWorld* World = TestWorld->GetTestWorld();
    if (!World)
    {
        AddError(TEXT("CP1 prerequisite failed: FTestWorldWrapper returned no UWorld."));
        TestWorld->EndPlayInTestWorld();
        TestWorld->DestroyTestWorld(false);
        return false;
    }

    const FVector SpawnLocation(0.0f, 0.0f, 100.0f);
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    ABunkerBeatsCP1MovementSmokeCharacter* Character = World->SpawnActor<ABunkerBeatsCP1MovementSmokeCharacter>(
        ABunkerBeatsCP1MovementSmokeCharacter::StaticClass(),
        SpawnLocation,
        FRotator::ZeroRotator,
        SpawnParams);

    if (!Character)
    {
        AddError(TEXT("CP1 spawn failed: smoke character could not be spawned."));
        TestWorld->EndPlayInTestWorld();
        TestWorld->DestroyTestWorld(false);
        return false;
    }

    UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
    if (!Movement || !Movement->IsActive())
    {
        AddError(TEXT("CP1 movement prerequisite failed: CharacterMovementComponent missing or inactive."));
        World->DestroyActor(Character);
        TestWorld->EndPlayInTestWorld();
        TestWorld->DestroyTestWorld(false);
        return false;
    }

    Character->SetActorLocation(SpawnLocation, false, nullptr, ETeleportType::TeleportPhysics);
    const FVector Before = Character->GetActorLocation();
    Character->AddMovementInput(FVector::ForwardVector, 1.0f);

    ADD_LATENT_AUTOMATION_COMMAND(FBunkerBeatsCP1MovementWait(*this, TestWorld, Character, Before, EvidenceRunId));

    AddInfo(FString::Printf(
        TEXT("CP1 CharacterSpawnMovement START: run_id=%s temp_game_world=true position=%s component=%s active=true max_walk_speed=%.1f."),
        *EvidenceRunId,
        *Before.ToCompactString(),
        *Movement->GetClass()->GetName(),
        Movement->MaxWalkSpeed));

    return true;
}
