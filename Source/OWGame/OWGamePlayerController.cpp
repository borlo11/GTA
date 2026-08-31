#include "OWGamePlayerController.h"

#include "OWGame.h"
#include "Crime/OWWantedComponent.h"
#include "Mission/OWMissionComponent.h"

#include "Components/InputComponent.h"
#include "GameFramework/Pawn.h"
#include "InputCoreTypes.h"

AOWGamePlayerController::AOWGamePlayerController()
{
    bShowMouseCursor = false;
    bEnableClickEvents = false;
    bEnableMouseOverEvents = false;

    WantedComponent = CreateDefaultSubobject<UOWWantedComponent>(TEXT("WantedComponent"));
    MissionComponent = CreateDefaultSubobject<UOWMissionComponent>(TEXT("MissionComponent"));
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

void AOWGamePlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();

#if !UE_BUILD_SHIPPING
    if (InputComponent)
    {
        InputComponent->BindKey(
            EKeys::F,
            IE_Pressed,
            this,
            &AOWGamePlayerController::DebugReportCrime);

        InputComponent->BindKey(
            EKeys::R,
            IE_Pressed,
            this,
            &AOWGamePlayerController::DebugStartMission);

        InputComponent->BindKey(
            EKeys::T,
            IE_Pressed,
            this,
            &AOWGamePlayerController::DebugResetMission);

        InputComponent->BindKey(
            EKeys::F9,
            IE_Pressed,
            this,
            &AOWGamePlayerController::TogglePerformanceOverlay);
    }
#endif
}

void AOWGamePlayerController::ReportPrototypeCrime(int32 Severity)
{
    if (!WantedComponent || Severity <= 0)
    {
        return;
    }

    WantedComponent->ReportCrime(Severity);
}

void AOWGamePlayerController::DebugReportCrime()
{
    ReportPrototypeCrime(1);

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("Prototype crime trigger pressed. Wanted=%d."),
        WantedComponent ? WantedComponent->GetWantedLevel() : 0);
}

void AOWGamePlayerController::DebugStartMission()
{
    if (MissionComponent)
    {
        MissionComponent->StartPrototypeMission();
    }
}

void AOWGamePlayerController::DebugResetMission()
{
    if (MissionComponent)
    {
        MissionComponent->ResetMission(true);
    }
}

void AOWGamePlayerController::TogglePerformanceOverlay()
{
    bShowPerformanceOverlay = !bShowPerformanceOverlay;
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
