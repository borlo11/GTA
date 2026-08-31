#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "../Interaction/OWInteractable.h"
#include "OWVehicleInteractionProxy.generated.h"

class APawn;
class UBoxComponent;

UCLASS()
class OWGAME_API AOWVehicleInteractionProxy : public AActor, public IOWInteractable
{
    GENERATED_BODY()

public:
    AOWVehicleInteractionProxy();

    UFUNCTION(BlueprintCallable, Category="Vehicle")
    void InitializeVehicle(APawn* InVehiclePawn);

    UFUNCTION(BlueprintPure, Category="Vehicle")
    APawn* GetVehiclePawn() const { return VehiclePawn; }

    virtual bool CanInteract_Implementation(AActor* Interactor) const override;
    virtual FText GetInteractionPrompt_Implementation(AActor* Interactor) const override;
    virtual void Interact_Implementation(AActor* Interactor) override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Vehicle")
    TObjectPtr<UBoxComponent> InteractionCollision;

    UPROPERTY(Transient)
    TObjectPtr<APawn> VehiclePawn;
};
