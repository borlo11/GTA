#include "OWGamePlayerController.h"

#include "OWGame.h"
#include "OWGameCharacter.h"
#include "Crime/OWWantedComponent.h"
#include "Mission/OWMissionComponent.h"

#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
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

    if (!InputComponent)
    {
        return;
    }

    // M10 vehicle controls intentionally live on the PlayerController.
    // The migrated SportsCar already owns its Chaos physics configuration;
    // these raw key bindings make it usable without adopting the template's
    // PlayerController/GameMode/Input Mapping Context architecture.
    InputComponent->BindKey(
        EKeys::W,
        IE_Pressed,
        this,
        &AOWGamePlayerController::VehicleForwardPressed);
    InputComponent->BindKey(
        EKeys::W,
        IE_Released,
        this,
        &AOWGamePlayerController::VehicleForwardReleased);
    InputComponent->BindKey(
        EKeys::S,
        IE_Pressed,
        this,
        &AOWGamePlayerController::VehicleReversePressed);
    InputComponent->BindKey(
        EKeys::S,
        IE_Released,
        this,
        &AOWGamePlayerController::VehicleReverseReleased);
    InputComponent->BindKey(
        EKeys::A,
        IE_Pressed,
        this,
        &AOWGamePlayerController::VehicleSteerLeftPressed);
    InputComponent->BindKey(
        EKeys::A,
        IE_Released,
        this,
        &AOWGamePlayerController::VehicleSteerLeftReleased);
    InputComponent->BindKey(
        EKeys::D,
        IE_Pressed,
        this,
        &AOWGamePlayerController::VehicleSteerRightPressed);
    InputComponent->BindKey(
        EKeys::D,
        IE_Released,
        this,
        &AOWGamePlayerController::VehicleSteerRightReleased);
    InputComponent->BindKey(
        EKeys::SpaceBar,
        IE_Pressed,
        this,
        &AOWGamePlayerController::VehicleHandbrakePressed);
    InputComponent->BindKey(
        EKeys::SpaceBar,
        IE_Released,
        this,
        &AOWGamePlayerController::VehicleHandbrakeReleased);
    InputComponent->BindKey(
        EKeys::E,
        IE_Pressed,
        this,
        &AOWGamePlayerController::VehicleExitPressed);

    InputComponent->BindAxisKey(
        EKeys::MouseX,
        this,
        &AOWGamePlayerController::VehicleLookYaw);
    InputComponent->BindAxisKey(
        EKeys::MouseY,
        this,
        &AOWGamePlayerController::VehicleLookPitch);

#if !UE_BUILD_SHIPPING
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

bool AOWGamePlayerController::EnterChaosVehicle(
    APawn* VehiclePawn,
    AOWGameCharacter* Character)
{
    if (!IsValid(VehiclePawn) ||
        !IsValid(Character) ||
        ActiveVehiclePawn ||
        VehiclePawn->GetController())
    {
        return false;
    }

    UChaosWheeledVehicleMovementComponent* Movement =
        VehiclePawn->FindComponentByClass<UChaosWheeledVehicleMovementComponent>();

    if (!Movement)
    {
        UE_LOG(
            LogOWGame,
            Error,
            TEXT("Vehicle %s has no Chaos wheeled movement component."),
            *GetNameSafe(VehiclePawn));
        return false;
    }

    VehicleDriverCharacter = Character;
    ActiveVehiclePawn = VehiclePawn;

    Character->SetActorHiddenInGame(true);
    Character->SetActorEnableCollision(false);

    if (UCharacterMovementComponent* CharacterMovement =
        Character->GetCharacterMovement())
    {
        CharacterMovement->DisableMovement();
    }

    Character->SetActorLocation(VehiclePawn->GetActorLocation());

    Possess(VehiclePawn);

    if (GetPawn() != VehiclePawn)
    {
        Character->SetActorHiddenInGame(false);
        Character->SetActorEnableCollision(true);

        if (UCharacterMovementComponent* CharacterMovement =
            Character->GetCharacterMovement())
        {
            CharacterMovement->SetMovementMode(MOVE_Walking);
        }

        VehicleDriverCharacter = nullptr;
        ActiveVehiclePawn = nullptr;

        UE_LOG(
            LogOWGame,
            Error,
            TEXT("Failed to possess Chaos vehicle %s."),
            *GetNameSafe(VehiclePawn));
        return false;
    }

    Movement->SetRequiresControllerForInputs(true);
    Movement->SetSleeping(false);
    Movement->SetParked(false);
    Movement->SetThrottleInput(0.0f);
    Movement->SetBrakeInput(0.0f);
    Movement->SetSteeringInput(0.0f);
    Movement->SetHandbrakeInput(false);

    bVehicleSteerLeftHeld = false;
    bVehicleSteerRightHeld = false;

    SetControlRotation(
        FRotator(0.0f, VehiclePawn->GetActorRotation().Yaw, 0.0f));

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("%s entered Chaos vehicle %s."),
        *Character->GetName(),
        *VehiclePawn->GetName());

    return true;
}

void AOWGamePlayerController::ExitChaosVehicle()
{
    if (!IsValid(ActiveVehiclePawn) ||
        !IsValid(VehicleDriverCharacter) ||
        GetPawn() != ActiveVehiclePawn)
    {
        return;
    }

    if (UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement())
    {
        Movement->SetThrottleInput(0.0f);
        Movement->SetBrakeInput(0.0f);
        Movement->SetSteeringInput(0.0f);
        Movement->SetHandbrakeInput(false);
    }

    AOWGameCharacter* Character = VehicleDriverCharacter;
    APawn* VehiclePawn = ActiveVehiclePawn;

    const FVector ExitLocation =
        VehiclePawn->GetActorTransform().TransformPosition(VehicleExitOffset);

    Character->SetActorLocationAndRotation(
        ExitLocation,
        FRotator(0.0f, VehiclePawn->GetActorRotation().Yaw, 0.0f),
        false,
        nullptr,
        ETeleportType::TeleportPhysics);
    Character->SetActorHiddenInGame(false);
    Character->SetActorEnableCollision(true);

    if (UCharacterMovementComponent* CharacterMovement =
        Character->GetCharacterMovement())
    {
        CharacterMovement->SetMovementMode(MOVE_Walking);
    }

    Possess(Character);

    if (GetPawn() != Character)
    {
        UE_LOG(
            LogOWGame,
            Error,
            TEXT("Chaos vehicle exit failed: controller possesses %s instead of %s."),
            *GetNameSafe(GetPawn()),
            *GetNameSafe(Character));
        return;
    }

    Character->ActivateOnFootInput();

    SetControlRotation(
        FRotator(0.0f, VehiclePawn->GetActorRotation().Yaw, 0.0f));

    VehicleDriverCharacter = nullptr;
    ActiveVehiclePawn = nullptr;
    bVehicleSteerLeftHeld = false;
    bVehicleSteerRightHeld = false;

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("%s exited Chaos vehicle %s."),
        *Character->GetName(),
        *VehiclePawn->GetName());
}

bool AOWGamePlayerController::IsDrivingChaosVehicle() const
{
    const APawn* CurrentPawn = GetPawn();

    return IsValid(CurrentPawn) &&
        CurrentPawn->FindComponentByClass<UChaosWheeledVehicleMovementComponent>() != nullptr;
}

bool AOWGamePlayerController::IsDrivingMissionVehicle() const
{
    const APawn* CurrentPawn = GetPawn();

    return IsDrivingChaosVehicle() &&
        CurrentPawn &&
        CurrentPawn->ActorHasTag(TEXT("OWMissionVehicle"));
}

UChaosWheeledVehicleMovementComponent*
AOWGamePlayerController::GetActiveChaosMovement() const
{
    APawn* CurrentPawn = GetPawn();

    return IsValid(CurrentPawn)
        ? CurrentPawn->FindComponentByClass<UChaosWheeledVehicleMovementComponent>()
        : nullptr;
}

void AOWGamePlayerController::UpdateSteeringInput()
{
    UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement();

    if (!Movement)
    {
        return;
    }

    const float Steering =
        (bVehicleSteerRightHeld ? 1.0f : 0.0f) -
        (bVehicleSteerLeftHeld ? 1.0f : 0.0f);

    Movement->SetSteeringInput(Steering);
}

void AOWGamePlayerController::VehicleForwardPressed()
{
    if (UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement())
    {
        Movement->SetBrakeInput(0.0f);
        Movement->SetThrottleInput(1.0f);
    }
}

void AOWGamePlayerController::VehicleForwardReleased()
{
    if (UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement())
    {
        Movement->SetThrottleInput(0.0f);
    }
}

void AOWGamePlayerController::VehicleReversePressed()
{
    if (UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement())
    {
        // The UE 5.8 Vehicle Template is configured for arcade-style
        // reverse-as-brake behavior. Holding S therefore brakes first and
        // transitions into reverse once the car is slow enough.
        Movement->SetThrottleInput(0.0f);
        Movement->SetBrakeInput(1.0f);
    }
}

void AOWGamePlayerController::VehicleReverseReleased()
{
    if (UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement())
    {
        Movement->SetBrakeInput(0.0f);
    }
}

void AOWGamePlayerController::VehicleSteerLeftPressed()
{
    if (!IsDrivingChaosVehicle())
    {
        return;
    }

    bVehicleSteerLeftHeld = true;
    UpdateSteeringInput();
}

void AOWGamePlayerController::VehicleSteerLeftReleased()
{
    bVehicleSteerLeftHeld = false;
    UpdateSteeringInput();
}

void AOWGamePlayerController::VehicleSteerRightPressed()
{
    if (!IsDrivingChaosVehicle())
    {
        return;
    }

    bVehicleSteerRightHeld = true;
    UpdateSteeringInput();
}

void AOWGamePlayerController::VehicleSteerRightReleased()
{
    bVehicleSteerRightHeld = false;
    UpdateSteeringInput();
}

void AOWGamePlayerController::VehicleHandbrakePressed()
{
    if (UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement())
    {
        Movement->SetHandbrakeInput(true);
    }
}

void AOWGamePlayerController::VehicleHandbrakeReleased()
{
    if (UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement())
    {
        Movement->SetHandbrakeInput(false);
    }
}

void AOWGamePlayerController::VehicleExitPressed()
{
    if (IsDrivingChaosVehicle())
    {
        ExitChaosVehicle();
    }
}

void AOWGamePlayerController::VehicleLookYaw(float Value)
{
    if (IsDrivingChaosVehicle() && !FMath::IsNearlyZero(Value))
    {
        AddYawInput(Value);
    }
}

void AOWGamePlayerController::VehicleLookPitch(float Value)
{
    if (IsDrivingChaosVehicle() && !FMath::IsNearlyZero(Value))
    {
        AddPitchInput(-Value);
    }
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
