#include "OWVerticalSliceDirector.h"

#include "../OWGame.h"
#include "../Mission/OWMissionStartActor.h"

#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"

AOWVerticalSliceDirector::AOWVerticalSliceDirector()
{
    PrimaryActorTick.bCanEverTick = false;
    MissionStartClass = AOWMissionStartActor::StaticClass();
}

void AOWVerticalSliceDirector::BeginPlay()
{
    Super::BeginPlay();

    if (!IsVerticalSliceMap())
    {
        Destroy();
        return;
    }

    GetWorldTimerManager().SetTimer(
        SpawnRetryTimer,
        this,
        &AOWVerticalSliceDirector::TryCreateMissionStart,
        StartActorSpawnDelay,
        true,
        StartActorSpawnDelay);
}

bool AOWVerticalSliceDirector::IsVerticalSliceMap() const
{
    const UWorld* World = GetWorld();
    return World && World->GetMapName().Contains(TEXT("OW_LightweightCity"));
}

bool AOWVerticalSliceDirector::FindGroundedLocation(
    const FVector& Candidate,
    FVector& OutLocation) const
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return false;
    }

    FHitResult Hit;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(OWVerticalSliceGround), false, this);

    const FVector Start = Candidate + FVector(0.0f, 0.0f, 700.0f);
    const FVector End = Candidate - FVector(0.0f, 0.0f, 1200.0f);

    if (!World->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, QueryParams))
    {
        return false;
    }

    OutLocation = Hit.ImpactPoint + FVector(0.0f, 0.0f, 95.0f);
    return true;
}

void AOWVerticalSliceDirector::TryCreateMissionStart()
{
    if (IsValid(MissionStartActor))
    {
        GetWorldTimerManager().ClearTimer(SpawnRetryTimer);
        return;
    }

    UWorld* World = GetWorld();
    APlayerController* PlayerController = World ? World->GetFirstPlayerController() : nullptr;
    APawn* PlayerPawn = PlayerController ? PlayerController->GetPawn() : nullptr;

    if (!World || !PlayerPawn || !MissionStartClass)
    {
        return;
    }

    const FVector Candidate =
        PlayerPawn->GetActorLocation() +
        PlayerPawn->GetActorForwardVector() * StartActorForwardOffset +
        PlayerPawn->GetActorRightVector() * StartActorRightOffset;

    FVector SpawnLocation = Candidate;
    FindGroundedLocation(Candidate, SpawnLocation);

    FActorSpawnParameters SpawnParameters;
    SpawnParameters.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

    MissionStartActor = World->SpawnActor<AOWMissionStartActor>(
        MissionStartClass,
        SpawnLocation,
        FRotator::ZeroRotator,
        SpawnParameters);

    if (MissionStartActor)
    {
        GetWorldTimerManager().ClearTimer(SpawnRetryTimer);

        UE_LOG(
            LogOWGame,
            Log,
            TEXT("M8 vertical slice mission start created at %s."),
            *SpawnLocation.ToCompactString());
    }
}
