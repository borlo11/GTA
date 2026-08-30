#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "OWInteractable.generated.h"

UINTERFACE(BlueprintType)
class OWGAME_API UOWInteractable : public UInterface
{
    GENERATED_BODY()
};

class OWGAME_API IOWInteractable
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Interaction")
    bool CanInteract(AActor* Interactor) const;

    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Interaction")
    FText GetInteractionPrompt(AActor* Interactor) const;

    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Interaction")
    void Interact(AActor* Interactor);
};
