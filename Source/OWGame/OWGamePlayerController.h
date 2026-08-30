#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "OWGamePlayerController.generated.h"

class UOWMissionComponent;
class UOWWantedComponent;

UCLASS()
class OWGAME_API AOWGamePlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    AOWGamePlayerController();

    UFUNCTION(BlueprintPure, Category="Crime")
    UOWWantedComponent* GetWantedComponent() const { return WantedComponent; }

    UFUNCTION(BlueprintCallable, Category="Crime")
    void ReportPrototypeCrime(int32 Severity = 1);

    UFUNCTION(BlueprintPure, Category="Mission")
    UOWMissionComponent* GetMissionComponent() const { return MissionComponent; }

    UFUNCTION(BlueprintPure, Category="Debug")
    bool IsPerformanceOverlayVisible() const { return bShowPerformanceOverlay; }

protected:
    virtual void BeginPlay() override;
    virtual void OnPossess(APawn* InPawn) override;
    virtual void SetupInputComponent() override;

private:
    void ApplyGameplayInputMode();
    void DebugReportCrime();
    void DebugStartMission();
    void DebugResetMission();
    void TogglePerformanceOverlay();

    UPROPERTY(VisibleAnywhere, Category="Crime")
    TObjectPtr<UOWWantedComponent> WantedComponent;

    UPROPERTY(VisibleAnywhere, Category="Mission")
    TObjectPtr<UOWMissionComponent> MissionComponent;

    UPROPERTY(Transient)
    bool bShowPerformanceOverlay = false;
};
