#include "OWPoliceDirector.h"

#include "OWPoliceOfficer.h"
#include "../OWGame.h"
#include "../OWGamePlayerController.h"
#include "../Crime/OWWantedComponent.h"

#include "Engine/World.h"
#include "GameFramework/PlayerController.h"

AOWPoliceDirector::AOWPoliceDirector()
{
    PrimaryActorTick.bCanEverTick = false;

    PoliceOfficerClass = AOWPoliceOfficer::StaticClass();
    SpawnRandom.Initialize(20260831);
}

void AOWPoliceDirector::BeginPlay()
{
    Super::BeginPlay();

    GetWorldTimerManager().SetTimer(
        ResponseTimer,
        this,
        &AOWPoliceDirector::UpdatePoliceResponse,
        ResponseUpdateInterval,
        true,
        0.35f);
}

int32 AOWPoliceDirector::GetDesiredOfficerCount(int32 WantedLevel) const
{
    if (WantedLevel <= 0)
    {
        return 0;
    }

    if (WantedLevel == 1)
    {
        return LevelOneResponseCount;
    }

    if (WantedLevel == 2)
    {
        return LevelTwoResponseCount;
    }

    return LevelThreeResponseCount;
}

bool AOWPoliceDirector::FindGroundedSpawnLocation(
    const FVector& Candidate,
    FVector& OutLocation) const
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return false;
    }

    FHitResult GroundHit;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(OWPoliceGround), false, this);

    for (const AOWPoliceOfficer* Officer : Officers)
    {
        if (IsValid(Officer))
        {
            QueryParams.AddIgnoredActor(Officer);
        }
    }

    const FVector TraceStart(Candidate.X, Candidate.Y, Candidate.Z + 1400.0f);
    const FVector TraceEnd(Candidate.X, Candidate.Y, Candidate.Z - 2600.0f);

    if (!World->LineTraceSingleByChannel(
        GroundHit,
        TraceStart,
        TraceEnd,
        ECC_Visibility,
        QueryParams))
    {
        return false;
    }

#if WITH_EDITOR
    if (const AActor* GroundActor = GroundHit.GetActor())
    {
        if (GroundActor->GetActorLabel().Contains(TEXT("Building")))
        {
            return false;
        }
    }
#endif

    OutLocation = GroundHit.ImpactPoint + FVector(0.0f, 0.0f, 96.0f);
    return true;
}

bool AOWPoliceDirector::SpawnOfficerNear(
    const FVector& SearchCenter,
    AOWGamePlayerController* PlayerController)
{
    UWorld* World = GetWorld();
    if (!World || !PoliceOfficerClass || !PlayerController)
    {
        return false;
    }

    for (int32 Attempt = 0; Attempt < 12; ++Attempt)
    {
        const float Angle = SpawnRandom.FRandRange(0.0f, 2.0f * PI);
        const float Radius = SpawnRandom.FRandRange(MinimumSpawnRadius, MaximumSpawnRadius);

        const FVector Candidate = SearchCenter + FVector(
            FMath::Cos(Angle) * Radius,
            FMath::Sin(Angle) * Radius,
            0.0f);

        FVector SpawnLocation;
        if (!FindGroundedSpawnLocation(Candidate, SpawnLocation))
        {
            continue;
        }

        FActorSpawnParameters SpawnParameters;
        SpawnParameters.SpawnCollisionHandlingOverride =
            ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

        AOWPoliceOfficer* Officer = World->SpawnActor<AOWPoliceOfficer>(
            PoliceOfficerClass,
            SpawnLocation,
            FRotator(0.0f, SpawnRandom.FRandRange(-180.0f, 180.0f), 0.0f),
            SpawnParameters);

        if (!Officer)
        {
            continue;
        }

        Officer->InitializePoliceTarget(PlayerController);
        Officers.Add(Officer);

        UE_LOG(LogOWGame, Log, TEXT("Police response spawned %s."), *Officer->GetName());
        return true;
    }

    return false;
}

void AOWPoliceDirector::ClearPoliceResponse()
{
    for (AOWPoliceOfficer* Officer : Officers)
    {
        if (IsValid(Officer))
        {
            Officer->Destroy();
        }
    }

    Officers.Reset();
}

void AOWPoliceDirector::UpdatePoliceResponse()
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    AOWGamePlayerController* PlayerController =
        Cast<AOWGamePlayerController>(World->GetFirstPlayerController());
    UOWWantedComponent* Wanted =
        PlayerController ? PlayerController->GetWantedComponent() : nullptr;

    if (!PlayerController || !Wanted)
    {
        return;
    }

    const int32 WantedLevel = Wanted->GetWantedLevel();
    if (WantedLevel <= 0)
    {
        if (!Officers.IsEmpty())
        {
            ClearPoliceResponse();
        }
        return;
    }

    const FVector SearchCenter =
        Wanted->HasLastKnownLocation()
        ? Wanted->GetLastKnownLocation()
        : (PlayerController->GetPawn()
            ? PlayerController->GetPawn()->GetActorLocation()
            : FVector::ZeroVector);

    for (int32 Index = Officers.Num() - 1; Index >= 0; --Index)
    {
        AOWPoliceOfficer* Officer = Officers[Index];
        if (!IsValid(Officer) || Officer->IsDead())
        {
            Officers.RemoveAtSwap(Index);
            continue;
        }

        if (FVector::DistSquared2D(Officer->GetActorLocation(), SearchCenter) >
            FMath::Square(OfficerDespawnDistance))
        {
            Officer->Destroy();
            Officers.RemoveAtSwap(Index);
        }
    }

    const int32 DesiredCount = GetDesiredOfficerCount(WantedLevel);
    int32 SpawnAttempts = 0;

    while (Officers.Num() < DesiredCount && SpawnAttempts < DesiredCount * 4)
    {
        ++SpawnAttempts;
        if (!SpawnOfficerNear(SearchCenter, PlayerController))
        {
            break;
        }
    }

    while (Officers.Num() > DesiredCount)
    {
        AOWPoliceOfficer* Officer = Officers.Pop(EAllowShrinking::No);
        if (IsValid(Officer))
        {
            Officer->Destroy();
        }
    }
}
