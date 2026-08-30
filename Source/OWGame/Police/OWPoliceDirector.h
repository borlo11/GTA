#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TimerManager.h"
#include "OWPoliceDirector.generated.h"

class AOWGamePlayerController;
class AOWPoliceOfficer;

UCLASS()
class OWGAME_API AOWPoliceDirector : public AActor
{
    GENERATED_BODY()

public:
    AOWPoliceDirector();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintPure, Category="Police")
    int32 GetLevelOneResponseCount() const { return LevelOneResponseCount; }

    UFUNCTION(BlueprintPure, Category="Police")
    int32 GetLevelTwoResponseCount() const { return LevelTwoResponseCount; }

    UFUNCTION(BlueprintPure, Category="Police")
    int32 GetLevelThreeResponseCount() const { return LevelThreeResponseCount; }

    UFUNCTION(BlueprintPure, Category="Police")
    float GetResponseUpdateInterval() const { return ResponseUpdateInterval; }

protected:
    void UpdatePoliceResponse();
    int32 GetDesiredOfficerCount(int32 WantedLevel) const;
    bool SpawnOfficerNear(const FVector& SearchCenter, AOWGamePlayerController* PlayerController);
    bool FindGroundedSpawnLocation(const FVector& Candidate, FVector& OutLocation) const;
    void ClearPoliceResponse();

    UPROPERTY(EditDefaultsOnly, Category="Police", meta=(ClampMin="1", ClampMax="8"))
    int32 LevelOneResponseCount = 1;

    UPROPERTY(EditDefaultsOnly, Category="Police", meta=(ClampMin="1", ClampMax="8"))
    int32 LevelTwoResponseCount = 2;

    UPROPERTY(EditDefaultsOnly, Category="Police", meta=(ClampMin="1", ClampMax="8"))
    int32 LevelThreeResponseCount = 3;

    UPROPERTY(EditDefaultsOnly, Category="Police", meta=(ClampMin="300.0", ClampMax="5000.0"))
    float MinimumSpawnRadius = 850.0f;

    UPROPERTY(EditDefaultsOnly, Category="Police", meta=(ClampMin="500.0", ClampMax="7000.0"))
    float MaximumSpawnRadius = 1450.0f;

    UPROPERTY(EditDefaultsOnly, Category="Police", meta=(ClampMin="1000.0", ClampMax="12000.0"))
    float OfficerDespawnDistance = 5000.0f;

    UPROPERTY(EditDefaultsOnly, Category="Police", meta=(ClampMin="0.1", ClampMax="3.0"))
    float ResponseUpdateInterval = 0.5f;

    UPROPERTY(EditDefaultsOnly, Category="Police")
    TSubclassOf<AOWPoliceOfficer> PoliceOfficerClass;

    UPROPERTY(Transient)
    TArray<TObjectPtr<AOWPoliceOfficer>> Officers;

    FRandomStream SpawnRandom;
    FTimerHandle ResponseTimer;
};
