#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "OWGamePlayerController.generated.h"

class UOWWantedComponent;

UCLASS()
class OWGAME_API AOWGamePlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    AOWGamePlayerController();

    UFUNCTION(BlueprintPure, Category="Crime")
    UOWWantedComponent* GetWantedComponent() const { return WantedComponent; }

    UFUNCTION(BlueprintCallable, Category="Crime")
    void ReportPrototypeCrime(int32 Severity = 1);

protected:
    virtual void BeginPlay() override;
    virtual void OnPossess(APawn* InPawn) override;
    virtual void SetupInputComponent() override;

private:
    void ApplyGameplayInputMode();
    void DebugReportCrime();

    UPROPERTY(VisibleAnywhere, Category="Crime")
    TObjectPtr<UOWWantedComponent> WantedComponent;
};
