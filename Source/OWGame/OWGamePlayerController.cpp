#include "OWGamePlayerController.h"

#include "OWGame.h"
#include "GameFramework/Pawn.h"

AOWGamePlayerController::AOWGamePlayerController()
{
    bShowMouseCursor = false;
    bEnableClickEvents = false;
    bEnableMouseOverEvents = false;
}

void AOWGamePlayerController::BeginPlay()
{
    Super::BeginPlay();
    ApplyGameplayInputMode();

}

void AOWGamePlayerController::OnPossess(APawn* InPawn)
{
    Super::OnPossess(InPawn);
    ApplyGameplayInputMode();

}

void AOWGamePlayerController::ApplyGameplayInputMode()
{
    if (!IsLocalController())
    {
        return;
    }

    FInputModeGameOnly InputMode;
    InputMode.SetConsumeCaptureMouseDown(true);
    SetInputMode(InputMode);

    SetIgnoreMoveInput(false);
    SetIgnoreLookInput(false);
    bShowMouseCursor = false;
}
