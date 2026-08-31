#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "../Interaction/OWInteractable.h"
#include "TimerManager.h"
#include "OWMissionStartActor.generated.h"

class UCapsuleComponent;
class UPointLightComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

UCLASS()
class OWGAME_API AOWMissionStartActor : public AActor, public IOWInteractable
{
    GENERATED_BODY()

public:
    AOWMissionStartActor();

    virtual void BeginPlay() override;

    virtual bool CanInteract_Implementation(AActor* Interactor) const override;
    virtual FText GetInteractionPrompt_Implementation(AActor* Interactor) const override;
    virtual void Interact_Implementation(AActor* Interactor) override;

    UFUNCTION(BlueprintPure, Category="Mission")
    float GetInteractionRadius() const { return InteractionRadius; }

protected:
    void RefreshAvailability();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Mission")
    TObjectPtr<UCapsuleComponent> InteractionCollision;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Mission")
    TObjectPtr<UStaticMeshComponent> MarkerMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Mission")
    TObjectPtr<UTextRenderComponent> MarkerText;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Mission")
    TObjectPtr<UPointLightComponent> MarkerLight;

    UPROPERTY(EditDefaultsOnly, Category="Mission", meta=(ClampMin="80.0", ClampMax="600.0"))
    float InteractionRadius = 180.0f;

    UPROPERTY(EditDefaultsOnly, Category="Mission", meta=(ClampMin="0.1", ClampMax="2.0"))
    float AvailabilityUpdateInterval = 0.5f;

    FTimerHandle AvailabilityTimer;
};
