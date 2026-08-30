#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "TimerManager.h"
#include "OWPopulationNPC.generated.h"

UENUM(BlueprintType)
enum class EOWPopulationSimulationTier : uint8
{
    High,
    Medium,
    Low,
    Dormant
};

UCLASS()
class OWGAME_API AOWPopulationNPC : public ACharacter
{
    GENERATED_BODY()

public:
    AOWPopulationNPC();

    virtual void BeginPlay() override;

    void InitializePopulationMember(int32 Seed, const FVector& InHomeLocation);
    void SetSimulationTier(EOWPopulationSimulationTier NewTier);

    UFUNCTION(BlueprintPure, Category="Population")
    EOWPopulationSimulationTier GetSimulationTier() const { return SimulationTier; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetWanderRadius() const { return WanderRadius; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetConfiguredWalkSpeed() const { return WalkSpeed; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetHighSimulationInterval() const { return HighSimulationInterval; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetMediumSimulationInterval() const { return MediumSimulationInterval; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetLowSimulationInterval() const { return LowSimulationInterval; }

protected:
    void ApplyTemplateVisuals();
    void ScheduleSimulationTimer();
    void UpdateWander();
    void PickNewDestination();
    void StopHorizontalMovement();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="50.0", ClampMax="1000.0"))
    float WanderRadius = 450.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="50.0", ClampMax="800.0"))
    float WalkSpeed = 190.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="0.02", ClampMax="0.20"))
    float HighSimulationInterval = 0.05f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="0.05", ClampMax="0.50"))
    float MediumSimulationInterval = 0.15f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="0.10", ClampMax="1.00"))
    float LowSimulationInterval = 0.45f;

    UPROPERTY(VisibleInstanceOnly, Category="Population")
    EOWPopulationSimulationTier SimulationTier = EOWPopulationSimulationTier::High;

    FVector HomeLocation = FVector::ZeroVector;
    FVector WanderDestination = FVector::ZeroVector;
    FRandomStream RandomStream;
    FTimerHandle SimulationTimer;

    float IdleUntilWorldTime = 0.0f;
    bool bPopulationInitialized = false;
    bool bWaitingAtDestination = false;
};
