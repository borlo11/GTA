#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TimerManager.h"
#include "OWPopulationManager.generated.h"

class AOWPopulationNPC;

UCLASS()
class OWGAME_API AOWPopulationManager : public AActor
{
    GENERATED_BODY()

public:
    AOWPopulationManager();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintPure, Category="Population")
    int32 GetTargetPopulation() const { return TargetPopulation; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetHighDetailDistance() const { return HighDetailDistance; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetMediumDetailDistance() const { return MediumDetailDistance; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetLowDetailDistance() const { return LowDetailDistance; }

    UFUNCTION(BlueprintPure, Category="Population")
    float GetDespawnDistance() const { return DespawnDistance; }

protected:
    void UpdatePopulation();
    bool SpawnOneNear(
        const FVector& PlayerLocation,
        APlayerController* PlayerController,
        APawn* PlayerPawn);
    bool FindGroundedSpawnLocation(const FVector& Candidate, FVector& OutLocation) const;
    bool IsSpawnHiddenFromPlayer(
        const FVector& SpawnLocation,
        APlayerController* PlayerController,
        APawn* PlayerPawn) const;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="1", ClampMax="64"))
    int32 TargetPopulation = 8;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="100.0", ClampMax="5000.0"))
    float MinimumSpawnRadius = 1800.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="200.0", ClampMax="8000.0"))
    float MaximumSpawnRadius = 3600.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="100.0", ClampMax="10000.0"))
    float HighDetailDistance = 1200.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="200.0", ClampMax="15000.0"))
    float MediumDetailDistance = 2200.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="300.0", ClampMax="20000.0"))
    float LowDetailDistance = 3500.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="500.0", ClampMax="30000.0"))
    float DespawnDistance = 5200.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="0.1", ClampMax="5.0"))
    float PopulationUpdateInterval = 0.5f;

    // At vehicle speed, never create pedestrians in the direction the player
    // is travelling. This prevents obvious "NPC popped into the road" moments.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|Spawning", meta=(ClampMin="0.0", ClampMax="5000.0"))
    float FastMovementThreshold = 500.0f;

    // Dot threshold for the camera-facing visibility gate. 0 = front
    // hemisphere; negative values make the protected view cone wider.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|Spawning", meta=(ClampMin="-1.0", ClampMax="1.0"))
    float VisibleSpawnDotThreshold = -0.15f;

    UPROPERTY(EditDefaultsOnly, Category="Population")
    TSubclassOf<AOWPopulationNPC> NPCClass;

    UPROPERTY(Transient)
    TArray<TObjectPtr<AOWPopulationNPC>> Population;

    FRandomStream SpawnRandomStream;
    FTimerHandle PopulationTimer;
    int32 NextNPCSeed = 1001;
};
