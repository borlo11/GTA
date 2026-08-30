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
    bool SpawnOneNear(const FVector& PlayerLocation);
    bool FindGroundedSpawnLocation(const FVector& Candidate, FVector& OutLocation) const;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="1", ClampMax="64"))
    int32 TargetPopulation = 8;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="100.0", ClampMax="5000.0"))
    float MinimumSpawnRadius = 350.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="200.0", ClampMax="8000.0"))
    float MaximumSpawnRadius = 850.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="100.0", ClampMax="10000.0"))
    float HighDetailDistance = 900.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="200.0", ClampMax="15000.0"))
    float MediumDetailDistance = 1600.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="300.0", ClampMax="20000.0"))
    float LowDetailDistance = 2400.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population|LOD", meta=(ClampMin="500.0", ClampMax="30000.0"))
    float DespawnDistance = 3200.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Population", meta=(ClampMin="0.1", ClampMax="5.0"))
    float PopulationUpdateInterval = 0.5f;

    UPROPERTY(EditDefaultsOnly, Category="Population")
    TSubclassOf<AOWPopulationNPC> NPCClass;

    UPROPERTY(Transient)
    TArray<TObjectPtr<AOWPopulationNPC>> Population;

    FRandomStream SpawnRandomStream;
    FTimerHandle PopulationTimer;
    int32 NextNPCSeed = 1001;
};
