#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "OWGamePlayerController.generated.h"

UCLASS()
class OWGAME_API AOWGamePlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    AOWGamePlayerController();

protected:
    virtual void BeginPlay() override;
    virtual void OnPossess(APawn* InPawn) override;

private:
    void ApplyGameplayInputMode();
};
