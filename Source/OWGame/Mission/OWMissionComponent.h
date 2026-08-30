#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TimerManager.h"
#include "OWMissionTypes.h"
#include "OWMissionComponent.generated.h"

class AOWMissionMarker;
class AOWPrototypeVehicle;

UCLASS(ClassGroup=(OWGame), meta=(BlueprintSpawnableComponent))
class OWGAME_API UOWMissionComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UOWMissionComponent();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="Mission")
    void StartPrototypeMission();

    UFUNCTION(BlueprintCallable, Category="Mission")
    void ResetMission(bool bDeleteSave);

    UFUNCTION(BlueprintCallable, Category="Mission")
    void FailMission(const FText& Reason);

    UFUNCTION(BlueprintPure, Category="Mission")
    EOWMissionState GetMissionState() const { return MissionState; }

    UFUNCTION(BlueprintPure, Category="Mission")
    int32 GetCurrentObjectiveIndex() const { return CurrentObjectiveIndex; }

    UFUNCTION(BlueprintPure, Category="Mission")
    int32 GetObjectiveCount() const { return Objectives.Num(); }

    UFUNCTION(BlueprintPure, Category="Mission")
    FText GetMissionTitle() const;

    UFUNCTION(BlueprintPure, Category="Mission")
    FText GetCurrentObjectiveText() const;

    UFUNCTION(BlueprintPure, Category="Mission")
    float GetCurrentObjectiveDistance() const { return CachedObjectiveDistance; }

    UFUNCTION(BlueprintPure, Category="Mission")
    float GetObjectiveUpdateInterval() const { return ObjectiveUpdateInterval; }

    UFUNCTION(BlueprintPure, Category="Mission")
    bool IsMissionActive() const { return MissionState == EOWMissionState::Active; }

    UFUNCTION(BlueprintPure, Category="Mission")
    FName GetMissionId() const { return MissionId; }

    UFUNCTION(BlueprintPure, Category="Mission")
    float GetCompletionBannerSeconds() const { return CompletionBannerSeconds; }

    UFUNCTION(BlueprintPure, Category="Mission")
    bool ShouldShowCompletionBanner() const;

protected:
    void BuildPrototypeMission();
    void EvaluateCurrentObjective();
    void AdvanceObjective();
    void CompleteMission();
    void OnObjectiveStarted();
    void SaveMissionProgress() const;
    void LoadMissionProgress();

    AOWPrototypeVehicle* FindPrototypeVehicle() const;
    FVector ResolveCurrentObjectiveLocation(bool& bHasLocation) const;

    void EnsureMarker();
    void UpdateMarker();
    void DestroyMarker();

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Mission")
    EOWMissionState MissionState = EOWMissionState::Inactive;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Mission")
    int32 CurrentObjectiveIndex = INDEX_NONE;

    UPROPERTY(Transient)
    TArray<FOWMissionObjectiveSpec> Objectives;

    UPROPERTY(Transient)
    TObjectPtr<AOWMissionMarker> MissionMarker;

    UPROPERTY(EditDefaultsOnly, Category="Mission", meta=(ClampMin="0.05", ClampMax="2.0"))
    float ObjectiveUpdateInterval = 0.2f;

    UPROPERTY(EditDefaultsOnly, Category="Mission")
    FName MissionId = FName(TEXT("HotRun"));

    UPROPERTY(EditDefaultsOnly, Category="Mission")
    FString SaveSlotName = TEXT("OWGame_MissionState_0");

    UPROPERTY(EditDefaultsOnly, Category="Mission|Presentation", meta=(ClampMin="1.0", ClampMax="10.0"))
    float CompletionBannerSeconds = 4.5f;

    FText FailureReason;
    float CachedObjectiveDistance = -1.0f;
    double CompletionBannerEndWorldTime = -1.0;
    FTimerHandle ObjectiveTimer;
};
