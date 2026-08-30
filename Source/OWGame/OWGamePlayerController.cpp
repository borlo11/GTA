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

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("PlayerController BeginPlay: %s Pawn=%s Local=%s"),
        *GetName(),
        *GetNameSafe(GetPawn()),
        IsLocalController() ? TEXT("true") : TEXT("false"));
}

void AOWGamePlayerController::OnPossess(APawn* InPawn)
{
    Super::OnPossess(InPawn);
    ApplyGameplayInputMode();

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("PlayerController possessed %s."),
        *GetNameSafe(InPawn));
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
