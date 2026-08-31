#include "OWPopulationManager.h"

#include "OWPopulationNPC.h"

#include "Engine/World.h"
#include "GameFramework/PlayerController.h"

AOWPopulationManager::AOWPopulationManager()
{
    PrimaryActorTick.bCanEverTick = false;

    NPCClass = AOWPopulationNPC::StaticClass();
    SpawnRandomStream.Initialize(20260830);
}

void AOWPopulationManager::BeginPlay()
{
    Super::BeginPlay();

    GetWorldTimerManager().SetTimer(
        PopulationTimer,
        this,
        &AOWPopulationManager::UpdatePopulation,
        PopulationUpdateInterval,
        true,
        0.25f);
}

bool AOWPopulationManager::FindGroundedSpawnLocation(
    const FVector& Candidate,
    FVector& OutLocation) const
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return false;
    }

    FHitResult GroundHit;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(OWPopulationGround), false, this);
    for (const AOWPopulationNPC* NPC : Population)
    {
        if (IsValid(NPC))
        {
            QueryParams.AddIgnoredActor(NPC);
        }
    }

    const FVector TraceStart(Candidate.X, Candidate.Y, Candidate.Z + 1200.0f);
    const FVector TraceEnd(Candidate.X, Candidate.Y, Candidate.Z - 2200.0f);

    if (!World->LineTraceSingleByChannel(
        GroundHit,
        TraceStart,
        TraceEnd,
        ECC_Visibility,
        QueryParams))
    {
        return false;
    }

    if (const AActor* GroundActor = GroundHit.GetActor())
    {
        if (GroundActor->ActorHasTag(TEXT("OWNoPopulationSpawn")))
        {
            return false;
        }

#if WITH_EDITOR
        if (GroundActor->GetActorLabel().Contains(TEXT("Building")))
        {
            return false;
        }
#endif
    }

    OutLocation = GroundHit.ImpactPoint + FVector(0.0f, 0.0f, 96.0f);
    return true;
}

bool AOWPopulationManager::SpawnOneNear(const FVector& PlayerLocation)
{
    UWorld* World = GetWorld();
    if (!World || !NPCClass)
    {
        return false;
    }

    for (int32 Attempt = 0; Attempt < 10; ++Attempt)
    {
        const float Angle = SpawnRandomStream.FRandRange(0.0f, 2.0f * PI);
        const float Radius = SpawnRandomStream.FRandRange(MinimumSpawnRadius, MaximumSpawnRadius);

        const FVector Candidate =
            PlayerLocation +
            FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, 0.0f);

        FVector SpawnLocation;
        if (!FindGroundedSpawnLocation(Candidate, SpawnLocation))
        {
            continue;
        }

        FActorSpawnParameters SpawnParameters;
        SpawnParameters.SpawnCollisionHandlingOverride =
            ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

        AOWPopulationNPC* NPC = World->SpawnActor<AOWPopulationNPC>(
            NPCClass,
            SpawnLocation,
            FRotator(0.0f, SpawnRandomStream.FRandRange(-180.0f, 180.0f), 0.0f),
            SpawnParameters);

        if (!NPC)
        {
            continue;
        }

        NPC->InitializePopulationMember(NextNPCSeed++, SpawnLocation);
        Population.Add(NPC);
        return true;
    }

    return false;
}

void AOWPopulationManager::UpdatePopulation()
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    APlayerController* PlayerController = World->GetFirstPlayerController();
    APawn* PlayerPawn = PlayerController ? PlayerController->GetPawn() : nullptr;
    if (!PlayerPawn)
    {
        return;
    }

    const FVector PlayerLocation = PlayerPawn->GetActorLocation();

    for (int32 Index = Population.Num() - 1; Index >= 0; --Index)
    {
        AOWPopulationNPC* NPC = Population[Index];
        if (!IsValid(NPC) || NPC->IsDead())
        {
            Population.RemoveAtSwap(Index);
            continue;
        }

        const float Distance = FVector::Dist2D(PlayerLocation, NPC->GetActorLocation());

        if (Distance > DespawnDistance)
        {
            NPC->Destroy();
            Population.RemoveAtSwap(Index);
            continue;
        }

        if (Distance <= HighDetailDistance)
        {
            NPC->SetSimulationTier(EOWPopulationSimulationTier::High);
        }
        else if (Distance <= MediumDetailDistance)
        {
            NPC->SetSimulationTier(EOWPopulationSimulationTier::Medium);
        }
        else if (Distance <= LowDetailDistance)
        {
            NPC->SetSimulationTier(EOWPopulationSimulationTier::Low);
        }
        else
        {
            NPC->SetSimulationTier(EOWPopulationSimulationTier::Dormant);
        }
    }

    int32 SpawnAttempts = 0;
    while (Population.Num() < TargetPopulation && SpawnAttempts < TargetPopulation * 3)
    {
        ++SpawnAttempts;
        if (!SpawnOneNear(PlayerLocation))
        {
            break;
        }
    }
}
