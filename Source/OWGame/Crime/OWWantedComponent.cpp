#include "OWWantedComponent.h"

#include "../OWGame.h"

#include "Engine/World.h"
#include "GameFramework/Controller.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"

UOWWantedComponent::UOWWantedComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UOWWantedComponent::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(
            DecayTimer,
            this,
            &UOWWantedComponent::EvaluateDeescalation,
            DecayCheckInterval,
            true,
            DecayCheckInterval);
    }
}

void UOWWantedComponent::ReportCrime(int32 Severity)
{
    FVector CrimeLocation = GetOwner() ? GetOwner()->GetActorLocation() : FVector::ZeroVector;

    if (const APlayerController* PlayerController = Cast<APlayerController>(GetOwner()))
    {
        if (const APawn* Pawn = PlayerController->GetPawn())
        {
            CrimeLocation = Pawn->GetActorLocation();
        }
    }

    ReportCrimeAtLocation(Severity, CrimeLocation);
}

void UOWWantedComponent::ReportCrimeAtLocation(int32 Severity, const FVector& WorldLocation)
{
    if (Severity <= 0)
    {
        return;
    }

    const int32 PreviousLevel = WantedLevel;
    WantedLevel = FMath::Clamp(WantedLevel + Severity, 0, MaxWantedLevel);
    LastKnownLocation = WorldLocation;
    bHasLastKnownLocation = true;

    if (const UWorld* World = GetWorld())
    {
        LastObservedWorldTime = World->GetTimeSeconds();
    }

    if (WantedLevel != PreviousLevel)
    {
        UE_LOG(
            LogOWGame,
            Log,
            TEXT("Wanted level increased %d -> %d at %s."),
            PreviousLevel,
            WantedLevel,
            *WorldLocation.ToCompactString());
    }
}

void UOWWantedComponent::MarkObserved(const FVector& WorldLocation)
{
    if (WantedLevel <= 0)
    {
        return;
    }

    LastKnownLocation = WorldLocation;
    bHasLastKnownLocation = true;

    if (const UWorld* World = GetWorld())
    {
        LastObservedWorldTime = World->GetTimeSeconds();
    }
}

void UOWWantedComponent::ClearWanted()
{
    if (WantedLevel > 0)
    {
        UE_LOG(LogOWGame, Log, TEXT("Wanted level cleared."));
    }

    WantedLevel = 0;
    LastKnownLocation = FVector::ZeroVector;
    LastObservedWorldTime = -1.0;
    bHasLastKnownLocation = false;
}

void UOWWantedComponent::EvaluateDeescalation()
{
    if (WantedLevel <= 0)
    {
        return;
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    const double Now = World->GetTimeSeconds();
    if (LastObservedWorldTime < 0.0)
    {
        LastObservedWorldTime = Now;
        return;
    }

    if ((Now - LastObservedWorldTime) < DecayDelaySeconds)
    {
        return;
    }

    const int32 PreviousLevel = WantedLevel;
    WantedLevel = FMath::Max(0, WantedLevel - 1);
    LastObservedWorldTime = Now;

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("Wanted level de-escalated %d -> %d after losing police observation."),
        PreviousLevel,
        WantedLevel);

    if (WantedLevel == 0)
    {
        LastKnownLocation = FVector::ZeroVector;
        bHasLastKnownLocation = false;
    }
}
