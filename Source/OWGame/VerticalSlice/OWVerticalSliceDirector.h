#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TimerManager.h"
#include "OWVerticalSliceDirector.generated.h"

class AOWMissionStartActor;

UCLASS()
class OWGAME_API AOWVerticalSliceDirector : public AActor
{
    GENERATED_BODY()

public:
    AOWVerticalSliceDirector();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintPure, Category="Vertical Slice")
    float GetStartActorSpawnDelay() const { return StartActorSpawnDelay; }

protected:
    void TryCreateMissionStart();
    bool IsVerticalSliceMap() const;
    bool FindGroundedLocation(const FVector& Candidate, FVector& OutLocation) const;

    UPROPERTY(EditDefaultsOnly, Category="Vertical Slice", meta=(ClampMin="0.05", ClampMax="2.0"))
    float StartActorSpawnDelay = 0.25f;

    UPROPERTY(EditDefaultsOnly, Category="Vertical Slice", meta=(ClampMin="100.0", ClampMax="800.0"))
    float StartActorForwardOffset = 260.0f;

    UPROPERTY(EditDefaultsOnly, Category="Vertical Slice", meta=(ClampMin="-800.0", ClampMax="800.0"))
    float StartActorRightOffset = 160.0f;

    UPROPERTY(EditDefaultsOnly, Category="Vertical Slice")
    TSubclassOf<AOWMissionStartActor> MissionStartClass;

    UPROPERTY(Transient)
    TObjectPtr<AOWMissionStartActor> MissionStartActor;

    FTimerHandle SpawnRetryTimer;
};
