#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TimerManager.h"
#include "OWWantedComponent.generated.h"

UCLASS(ClassGroup=(OWGame), meta=(BlueprintSpawnableComponent))
class OWGAME_API UOWWantedComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UOWWantedComponent();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="Crime")
    void ReportCrime(int32 Severity = 1);

    void ReportCrimeAtLocation(int32 Severity, const FVector& WorldLocation);
    void MarkObserved(const FVector& WorldLocation);
    void ClearWanted();

    UFUNCTION(BlueprintPure, Category="Crime")
    int32 GetWantedLevel() const { return WantedLevel; }

    UFUNCTION(BlueprintPure, Category="Crime")
    int32 GetMaxWantedLevel() const { return MaxWantedLevel; }

    UFUNCTION(BlueprintPure, Category="Crime")
    float GetDecayDelaySeconds() const { return DecayDelaySeconds; }

    UFUNCTION(BlueprintPure, Category="Crime")
    FVector GetLastKnownLocation() const { return LastKnownLocation; }

    UFUNCTION(BlueprintPure, Category="Crime")
    bool HasLastKnownLocation() const { return bHasLastKnownLocation; }

protected:
    void EvaluateDeescalation();

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Crime")
    int32 WantedLevel = 0;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Crime", meta=(ClampMin="1", ClampMax="5"))
    int32 MaxWantedLevel = 3;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Crime", meta=(ClampMin="2.0", ClampMax="60.0"))
    float DecayDelaySeconds = 10.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Crime", meta=(ClampMin="0.25", ClampMax="5.0"))
    float DecayCheckInterval = 1.0f;

    FVector LastKnownLocation = FVector::ZeroVector;
    double LastObservedWorldTime = -1.0;
    bool bHasLastKnownLocation = false;

    FTimerHandle DecayTimer;
};
