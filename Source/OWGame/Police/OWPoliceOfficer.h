#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "OWPoliceOfficer.generated.h"

class AOWGamePlayerController;
class UTextRenderComponent;

UCLASS()
class OWGAME_API AOWPoliceOfficer : public ACharacter
{
    GENERATED_BODY()

public:
    AOWPoliceOfficer();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    void InitializePoliceTarget(AOWGamePlayerController* InTargetController);

    UFUNCTION(BlueprintPure, Category="Police")
    float GetChaseSpeed() const { return ChaseSpeed; }

    UFUNCTION(BlueprintPure, Category="Police")
    float GetSightRange() const { return SightRange; }

protected:
    void ApplyPoliceVisuals();
    bool CanSeeTargetPawn(const APawn* TargetPawn) const;
    FVector GetSearchDestination(const FVector& LastKnownLocation);
    void StopPursuitMovement();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Police")
    TObjectPtr<UTextRenderComponent> PoliceLabel;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Police", meta=(ClampMin="100.0", ClampMax="1200.0"))
    float ChaseSpeed = 620.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Police", meta=(ClampMin="300.0", ClampMax="6000.0"))
    float SightRange = 2600.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Police", meta=(ClampMin="50.0", ClampMax="800.0"))
    float StopDistance = 170.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Police|Search", meta=(ClampMin="100.0", ClampMax="1200.0"))
    float SearchRadius = 420.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Police|Search", meta=(ClampMin="0.5", ClampMax="10.0"))
    float SearchRetargetSeconds = 2.0f;

    TWeakObjectPtr<AOWGamePlayerController> TargetController;
    FVector SearchDestination = FVector::ZeroVector;
    double NextSearchRetargetWorldTime = 0.0;
    bool bHasSearchDestination = false;
    FRandomStream SearchRandom;
};
