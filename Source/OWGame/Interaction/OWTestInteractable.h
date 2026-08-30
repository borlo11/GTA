#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OWInteractable.h"
#include "OWTestInteractable.generated.h"

class USceneComponent;
class UStaticMeshComponent;

UCLASS()
class OWGAME_API AOWTestInteractable : public AActor, public IOWInteractable
{
    GENERATED_BODY()

public:
    AOWTestInteractable();

    virtual bool CanInteract_Implementation(AActor* Interactor) const override;
    virtual FText GetInteractionPrompt_Implementation(AActor* Interactor) const override;
    virtual void Interact_Implementation(AActor* Interactor) override;

private:
    UPROPERTY(VisibleAnywhere, Category="Interaction")
    TObjectPtr<USceneComponent> SceneRoot;

    UPROPERTY(VisibleAnywhere, Category="Interaction")
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(VisibleInstanceOnly, Category="Interaction")
    bool bHasBeenInteractedWith = false;
};
