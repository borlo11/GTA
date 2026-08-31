#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "OWGamePlayerController.generated.h"

class AOWGameCharacter;
class UChaosWheeledVehicleMovementComponent;
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

    UFUNCTION(BlueprintCallable, Category="Vehicle")
    bool EnterChaosVehicle(APawn* VehiclePawn, AOWGameCharacter* DriverCharacter);

    UFUNCTION(BlueprintCallable, Category="Vehicle")
    void ExitChaosVehicle();

    UFUNCTION(BlueprintPure, Category="Vehicle")
    bool IsDrivingChaosVehicle() const;

    UFUNCTION(BlueprintPure, Category="Vehicle")
    bool IsDrivingMissionVehicle() const;

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

    UChaosWheeledVehicleMovementComponent* GetActiveChaosMovement() const;
    void WakeActiveChaosVehicle();
    void UpdateSteeringInput();

    void VehicleForwardPressed();
    void VehicleForwardReleased();
    void VehicleReversePressed();
    void VehicleReverseReleased();
    void VehicleSteerLeftPressed();
    void VehicleSteerLeftReleased();
    void VehicleSteerRightPressed();
    void VehicleSteerRightReleased();
    void VehicleHandbrakePressed();
    void VehicleHandbrakeReleased();
    void VehicleResetPressed();
    void VehicleExitPressed();
    void VehicleLookYaw(float Value);
    void VehicleLookPitch(float Value);

    UPROPERTY(VisibleAnywhere, Category="Crime")
    TObjectPtr<UOWWantedComponent> WantedComponent;

    UPROPERTY(VisibleAnywhere, Category="Mission")
    TObjectPtr<UOWMissionComponent> MissionComponent;

    UPROPERTY(Transient)
    TObjectPtr<AOWGameCharacter> VehicleDriverCharacter;

    UPROPERTY(Transient)
    TObjectPtr<APawn> ActiveVehiclePawn;

    UPROPERTY(EditDefaultsOnly, Category="Vehicle")
    FVector VehicleExitOffset = FVector(0.0f, 230.0f, 95.0f);

    UPROPERTY(Transient)
    bool bShowPerformanceOverlay = false;

    bool bVehicleSteerLeftHeld = false;
    bool bVehicleSteerRightHeld = false;
};
