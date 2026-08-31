#include "OWMissionComponent.h"

#include "OWMissionMarker.h"
#include "OWMissionSaveGame.h"
#include "../OWGame.h"
#include "../OWGamePlayerController.h"
#include "../Crime/OWWantedComponent.h"

#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"

UOWMissionComponent::UOWMissionComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UOWMissionComponent::BeginPlay()
{
    Super::BeginPlay();

    BuildPrototypeMission();
    LoadMissionProgress();

    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(
            ObjectiveTimer,
            this,
            &UOWMissionComponent::EvaluateCurrentObjective,
            ObjectiveUpdateInterval,
            true,
            ObjectiveUpdateInterval);
    }

    if (MissionState == EOWMissionState::Active)
    {
        OnObjectiveStarted();
    }
}

void UOWMissionComponent::BuildPrototypeMission()
{
    Objectives.Reset();

    FOWMissionObjectiveSpec ReachVehicle;
    ReachVehicle.Type = EOWMissionObjectiveType::ReachVehicle;
    ReachVehicle.Description = FText::FromString(TEXT("Raggiungi il veicolo"));
    ReachVehicle.AcceptanceRadius = 320.0f;
    Objectives.Add(ReachVehicle);

    FOWMissionObjectiveSpec EnterVehicle;
    EnterVehicle.Type = EOWMissionObjectiveType::EnterVehicle;
    EnterVehicle.Description = FText::FromString(TEXT("Entra nel veicolo"));
    EnterVehicle.AcceptanceRadius = 320.0f;
    Objectives.Add(EnterVehicle);

    FOWMissionObjectiveSpec DriveCheckpoint;
    DriveCheckpoint.Type = EOWMissionObjectiveType::ReachLocation;
    DriveCheckpoint.Description = FText::FromString(TEXT("Guida fino al checkpoint"));
    DriveCheckpoint.TargetLocation = FVector(0.0f, 4200.0f, 120.0f);
    DriveCheckpoint.AcceptanceRadius = 420.0f;
    Objectives.Add(DriveCheckpoint);

    FOWMissionObjectiveSpec LoseWanted;
    LoseWanted.Type = EOWMissionObjectiveType::LoseWanted;
    LoseWanted.Description = FText::FromString(TEXT("Semina la polizia"));
    LoseWanted.AcceptanceRadius = 0.0f;
    Objectives.Add(LoseWanted);
}

void UOWMissionComponent::StartPrototypeMission()
{
    if (Objectives.IsEmpty())
    {
        BuildPrototypeMission();
    }

    if (MissionState == EOWMissionState::Active)
    {
        return;
    }

    ResetMission(true);

    MissionState = EOWMissionState::Active;
    CurrentObjectiveIndex = 0;
    FailureReason = FText::GetEmpty();

    UE_LOG(LogOWGame, Log, TEXT("Mission %s started."), *MissionId.ToString());

    OnObjectiveStarted();
    SaveMissionProgress();
}

void UOWMissionComponent::ResetMission(bool bDeleteSave)
{
    MissionState = EOWMissionState::Inactive;
    CurrentObjectiveIndex = INDEX_NONE;
    FailureReason = FText::GetEmpty();
    CachedObjectiveDistance = -1.0f;
    CompletionBannerEndWorldTime = -1.0;

    DestroyMarker();

    if (bDeleteSave && UGameplayStatics::DoesSaveGameExist(SaveSlotName, 0))
    {
        UGameplayStatics::DeleteGameInSlot(SaveSlotName, 0);
    }

    UE_LOG(LogOWGame, Log, TEXT("Mission state reset."));
}

void UOWMissionComponent::FailMission(const FText& Reason)
{
    if (MissionState != EOWMissionState::Active)
    {
        return;
    }

    MissionState = EOWMissionState::Failed;
    FailureReason = Reason;
    CachedObjectiveDistance = -1.0f;
    CompletionBannerEndWorldTime = -1.0;
    DestroyMarker();
    SaveMissionProgress();

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("Mission %s failed: %s"),
        *MissionId.ToString(),
        *Reason.ToString());
}

FText UOWMissionComponent::GetMissionTitle() const
{
    return FText::FromString(TEXT("Hot Run"));
}

FText UOWMissionComponent::GetCurrentObjectiveText() const
{
    if (MissionState == EOWMissionState::Completed)
    {
        return FText::FromString(TEXT("Missione completata"));
    }

    if (MissionState == EOWMissionState::Failed)
    {
        return FailureReason.IsEmpty()
            ? FText::FromString(TEXT("Missione fallita"))
            : FailureReason;
    }

    if (MissionState != EOWMissionState::Active ||
        !Objectives.IsValidIndex(CurrentObjectiveIndex))
    {
        return FText::GetEmpty();
    }

    return Objectives[CurrentObjectiveIndex].Description;
}

APawn* UOWMissionComponent::FindMissionVehicle() const
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return nullptr;
    }

    const AOWGamePlayerController* PlayerController =
        Cast<AOWGamePlayerController>(GetOwner());
    const APawn* PlayerPawn = PlayerController ? PlayerController->GetPawn() : nullptr;
    const FVector ReferenceLocation =
        PlayerPawn ? PlayerPawn->GetActorLocation() : FVector::ZeroVector;

    APawn* BestVehicle = nullptr;
    float BestDistanceSquared = TNumericLimits<float>::Max();

    for (TActorIterator<APawn> It(World); It; ++It)
    {
        APawn* Vehicle = *It;
        if (!IsValid(Vehicle) ||
            !Vehicle->ActorHasTag(TEXT("OWMissionVehicle")))
        {
            continue;
        }

        const float DistanceSquared =
            FVector::DistSquared(ReferenceLocation, Vehicle->GetActorLocation());

        if (DistanceSquared < BestDistanceSquared)
        {
            BestDistanceSquared = DistanceSquared;
            BestVehicle = Vehicle;
        }
    }

    return BestVehicle;
}

FVector UOWMissionComponent::ResolveCurrentObjectiveLocation(bool& bHasLocation) const
{
    bHasLocation = false;

    if (MissionState != EOWMissionState::Active ||
        !Objectives.IsValidIndex(CurrentObjectiveIndex))
    {
        return FVector::ZeroVector;
    }

    const FOWMissionObjectiveSpec& Objective = Objectives[CurrentObjectiveIndex];

    if (Objective.Type == EOWMissionObjectiveType::ReachVehicle ||
        Objective.Type == EOWMissionObjectiveType::EnterVehicle)
    {
        if (const APawn* Vehicle = FindMissionVehicle())
        {
            bHasLocation = true;
            return Vehicle->GetActorLocation() + FVector(0.0f, 0.0f, 120.0f);
        }
    }
    else if (Objective.Type == EOWMissionObjectiveType::ReachLocation)
    {
        bHasLocation = true;
        return Objective.TargetLocation;
    }

    return FVector::ZeroVector;
}

void UOWMissionComponent::EvaluateCurrentObjective()
{
    if (MissionState != EOWMissionState::Active ||
        !Objectives.IsValidIndex(CurrentObjectiveIndex))
    {
        return;
    }

    AOWGamePlayerController* PlayerController =
        Cast<AOWGamePlayerController>(GetOwner());
    APawn* PlayerPawn = PlayerController ? PlayerController->GetPawn() : nullptr;
    if (!PlayerController || !PlayerPawn)
    {
        return;
    }

    UpdateMarker();

    const FOWMissionObjectiveSpec& Objective = Objectives[CurrentObjectiveIndex];

    switch (Objective.Type)
    {
    case EOWMissionObjectiveType::ReachVehicle:
        if (APawn* Vehicle = FindMissionVehicle())
        {
            if (FVector::Dist2D(
                PlayerPawn->GetActorLocation(),
                Vehicle->GetActorLocation()) <= Objective.AcceptanceRadius)
            {
                AdvanceObjective();
            }
        }
        break;

    case EOWMissionObjectiveType::EnterVehicle:
        if (PlayerController->IsDrivingMissionVehicle())
        {
            AdvanceObjective();
        }
        break;

    case EOWMissionObjectiveType::ReachLocation:
        if (PlayerController->IsDrivingMissionVehicle() &&
            FVector::Dist2D(
                PlayerPawn->GetActorLocation(),
                Objective.TargetLocation) <= Objective.AcceptanceRadius)
        {
            AdvanceObjective();
        }
        break;

    case EOWMissionObjectiveType::LoseWanted:
        if (UOWWantedComponent* Wanted = PlayerController->GetWantedComponent())
        {
            if (Wanted->GetWantedLevel() <= 0)
            {
                AdvanceObjective();
            }
        }
        break;

    default:
        break;
    }
}

void UOWMissionComponent::AdvanceObjective()
{
    if (MissionState != EOWMissionState::Active)
    {
        return;
    }

    ++CurrentObjectiveIndex;

    if (!Objectives.IsValidIndex(CurrentObjectiveIndex))
    {
        CompleteMission();
        return;
    }

    OnObjectiveStarted();
    SaveMissionProgress();

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("Mission %s advanced to objective %d: %s"),
        *MissionId.ToString(),
        CurrentObjectiveIndex,
        *Objectives[CurrentObjectiveIndex].Description.ToString());
}

void UOWMissionComponent::CompleteMission()
{
    MissionState = EOWMissionState::Completed;
    CurrentObjectiveIndex = Objectives.Num();
    CachedObjectiveDistance = -1.0f;

    if (const UWorld* World = GetWorld())
    {
        CompletionBannerEndWorldTime =
            World->GetTimeSeconds() + CompletionBannerSeconds;
    }

    DestroyMarker();
    SaveMissionProgress();

    UE_LOG(LogOWGame, Log, TEXT("Mission %s completed."), *MissionId.ToString());
}

void UOWMissionComponent::OnObjectiveStarted()
{
    if (MissionState != EOWMissionState::Active ||
        !Objectives.IsValidIndex(CurrentObjectiveIndex))
    {
        return;
    }

    const FOWMissionObjectiveSpec& Objective = Objectives[CurrentObjectiveIndex];

    if (Objective.Type == EOWMissionObjectiveType::LoseWanted)
    {
        if (AOWGamePlayerController* PlayerController =
            Cast<AOWGamePlayerController>(GetOwner()))
        {
            if (UOWWantedComponent* Wanted = PlayerController->GetWantedComponent())
            {
                const int32 NeededSeverity =
                    FMath::Max(0, 2 - Wanted->GetWantedLevel());

                if (NeededSeverity > 0)
                {
                    PlayerController->ReportPrototypeCrime(NeededSeverity);
                }
            }
        }
    }

    UpdateMarker();
}

void UOWMissionComponent::EnsureMarker()
{
    if (IsValid(MissionMarker))
    {
        return;
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    FActorSpawnParameters SpawnParameters;
    SpawnParameters.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    MissionMarker = World->SpawnActor<AOWMissionMarker>(
        AOWMissionMarker::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParameters);
}

void UOWMissionComponent::UpdateMarker()
{
    bool bHasLocation = false;
    const FVector TargetLocation = ResolveCurrentObjectiveLocation(bHasLocation);

    if (!bHasLocation)
    {
        CachedObjectiveDistance = -1.0f;
        DestroyMarker();
        return;
    }

    if (const AOWGamePlayerController* PlayerController =
        Cast<AOWGamePlayerController>(GetOwner()))
    {
        if (const APawn* PlayerPawn = PlayerController->GetPawn())
        {
            CachedObjectiveDistance =
                FVector::Dist2D(PlayerPawn->GetActorLocation(), TargetLocation);
        }
        else
        {
            CachedObjectiveDistance = -1.0f;
        }
    }
    else
    {
        CachedObjectiveDistance = -1.0f;
    }

    EnsureMarker();

    if (MissionMarker)
    {
        MissionMarker->SetMarkerLocation(TargetLocation);
        MissionMarker->SetMarkerText(FText::FromString(TEXT("MISSIONE")));
    }
}

void UOWMissionComponent::DestroyMarker()
{
    if (IsValid(MissionMarker))
    {
        MissionMarker->Destroy();
    }

    MissionMarker = nullptr;
}

void UOWMissionComponent::SaveMissionProgress() const
{
    UOWMissionSaveGame* SaveGame =
        Cast<UOWMissionSaveGame>(
            UGameplayStatics::CreateSaveGameObject(
                UOWMissionSaveGame::StaticClass()));

    if (!SaveGame)
    {
        return;
    }

    SaveGame->MissionId = MissionId;
    SaveGame->MissionState = MissionState;
    SaveGame->ObjectiveIndex = CurrentObjectiveIndex;

    if (!UGameplayStatics::SaveGameToSlot(SaveGame, SaveSlotName, 0))
    {
        UE_LOG(
            LogOWGame,
            Warning,
            TEXT("Failed to save mission progress to %s."),
            *SaveSlotName);
    }
}

void UOWMissionComponent::LoadMissionProgress()
{
    if (!UGameplayStatics::DoesSaveGameExist(SaveSlotName, 0))
    {
        return;
    }

    UOWMissionSaveGame* SaveGame =
        Cast<UOWMissionSaveGame>(
            UGameplayStatics::LoadGameFromSlot(SaveSlotName, 0));

    if (!SaveGame || SaveGame->MissionId != MissionId)
    {
        return;
    }

    MissionState = SaveGame->MissionState;
    CurrentObjectiveIndex = SaveGame->ObjectiveIndex;

    if (MissionState == EOWMissionState::Active &&
        !Objectives.IsValidIndex(CurrentObjectiveIndex))
    {
        MissionState = EOWMissionState::Inactive;
        CurrentObjectiveIndex = INDEX_NONE;
    }

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("Loaded mission %s state=%d objective=%d."),
        *MissionId.ToString(),
        static_cast<int32>(MissionState),
        CurrentObjectiveIndex);
}


bool UOWMissionComponent::ShouldShowCompletionBanner() const
{
    const UWorld* World = GetWorld();

    return MissionState == EOWMissionState::Completed &&
        World &&
        CompletionBannerEndWorldTime >= 0.0 &&
        World->GetTimeSeconds() <= CompletionBannerEndWorldTime;
}
