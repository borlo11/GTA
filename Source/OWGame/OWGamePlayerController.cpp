#include "OWGamePlayerController.h"

#include "OWGame.h"
#include "OWGameCharacter.h"
#include "Crime/OWWantedComponent.h"
#include "Mission/OWMissionComponent.h"
#include "Vehicle/OWVehicleInteractionProxy.h"

#include "ChaosWheeledVehicleMovementComponent.h"
#include "EngineUtils.h"
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
        EKeys::X,
        IE_Pressed,
        this,
        &AOWGamePlayerController::VehicleResetPressed);
    FInputKeyBinding& VehicleExitBinding = InputComponent->BindKey(
        EKeys::E,
        IE_Pressed,
        this,
        &AOWGamePlayerController::VehicleExitPressed);

    // Do not consume E while the player is on foot. The character's
    // Enhanced Input IA_Interact also uses E to enter vehicles / interact
    // with world objects. Consuming it here made the enter interaction never
    // reach AOWGameCharacter::TryInteract().
    VehicleExitBinding.bConsumeInput = false;

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
    AOWGameCharacter* DriverCharacter)
{
    if (!IsValid(VehiclePawn) ||
        !IsValid(DriverCharacter) ||
        ActiveVehiclePawn)
    {
        return false;
    }

    // A migrated template pawn may arrive with a controller depending on its
    // Blueprint defaults. OWGame owns possession while driving, so release any
    // previous controller instead of treating that as a failed interaction.
    if (AController* ExistingController = VehiclePawn->GetController())
    {
        if (ExistingController != this)
        {
            ExistingController->UnPossess();
        }
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

    VehicleDriverCharacter = DriverCharacter;
    ActiveVehiclePawn = VehiclePawn;

    DriverCharacter->SetActorHiddenInGame(true);
    DriverCharacter->SetActorEnableCollision(false);

    if (UCharacterMovementComponent* CharacterMovement =
        DriverCharacter->GetCharacterMovement())
    {
        CharacterMovement->DisableMovement();
    }

    DriverCharacter->SetActorLocation(VehiclePawn->GetActorLocation());

    Possess(VehiclePawn);

    if (GetPawn() != VehiclePawn)
    {
        DriverCharacter->SetActorHiddenInGame(false);
        DriverCharacter->SetActorEnableCollision(true);

        if (UCharacterMovementComponent* CharacterMovement =
            DriverCharacter->GetCharacterMovement())
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
        *DriverCharacter->GetName(),
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

    AOWGameCharacter* DriverCharacter = VehicleDriverCharacter;
    APawn* VehiclePawn = ActiveVehiclePawn;

    const FVector ExitLocation =
        VehiclePawn->GetActorTransform().TransformPosition(VehicleExitOffset);

    DriverCharacter->SetActorLocationAndRotation(
        ExitLocation,
        FRotator(0.0f, VehiclePawn->GetActorRotation().Yaw, 0.0f),
        false,
        nullptr,
        ETeleportType::TeleportPhysics);
    DriverCharacter->SetActorHiddenInGame(false);
    DriverCharacter->SetActorEnableCollision(true);

    if (UCharacterMovementComponent* CharacterMovement =
        DriverCharacter->GetCharacterMovement())
    {
        CharacterMovement->SetMovementMode(MOVE_Walking);
    }

    Possess(DriverCharacter);

    if (GetPawn() != DriverCharacter)
    {
        UE_LOG(
            LogOWGame,
            Error,
            TEXT("Chaos vehicle exit failed: controller possesses %s instead of %s."),
            *GetNameSafe(GetPawn()),
            *GetNameSafe(DriverCharacter));
        return;
    }

    DriverCharacter->ActivateOnFootInput();

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
        *DriverCharacter->GetName(),
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

void AOWGamePlayerController::WakeActiveChaosVehicle()
{
    if (UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement())
    {
        Movement->SetSleeping(false);
        Movement->SetParked(false);
    }
}

void AOWGamePlayerController::UpdateSteeringInput()
{
    WakeActiveChaosVehicle();

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
    WakeActiveChaosVehicle();

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
    WakeActiveChaosVehicle();

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
    WakeActiveChaosVehicle();

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

void AOWGamePlayerController::VehicleResetPressed()
{
    if (!IsDrivingChaosVehicle() || !IsValid(ActiveVehiclePawn))
    {
        return;
    }

    UChaosWheeledVehicleMovementComponent* Movement =
        GetActiveChaosMovement();

    if (Movement)
    {
        Movement->SetThrottleInput(0.0f);
        Movement->SetBrakeInput(0.0f);
        Movement->SetSteeringInput(0.0f);
        Movement->SetHandbrakeInput(false);
        Movement->StopMovementImmediately();
    }

    // Lift the vehicle clear of curbs/geometry while preserving its current
    // heading. This is intentionally a gameplay recovery action rather than a
    // respawn so free-roam testing can continue immediately.
    const FVector ResetLocation =
        ActiveVehiclePawn->GetActorLocation() + FVector(0.0f, 0.0f, 140.0f);
    const FRotator ResetRotation(
        0.0f,
        ActiveVehiclePawn->GetActorRotation().Yaw,
        0.0f);

    ActiveVehiclePawn->SetActorLocationAndRotation(
        ResetLocation,
        ResetRotation,
        false,
        nullptr,
        ETeleportType::TeleportPhysics);

    bVehicleSteerLeftHeld = false;
    bVehicleSteerRightHeld = false;
    WakeActiveChaosVehicle();

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("Chaos vehicle reset at %s."),
        *ResetLocation.ToCompactString());
}

void AOWGamePlayerController::VehicleExitPressed()
{
    if (IsDrivingChaosVehicle())
    {
        ExitChaosVehicle();
        return;
    }

    // Robust on-foot vehicle entry: do not depend on the camera visibility
    // sweep hitting an invisible proxy before the SportsCar's own collision.
    // Pressing E near a vehicle always chooses the closest linked M10 proxy.
    AOWGameCharacter* DriverCharacter = Cast<AOWGameCharacter>(GetPawn());
    UWorld* World = GetWorld();
    if (!DriverCharacter || !World)
    {
        return;
    }

    constexpr float EnterRadius = 500.0f;
    const float EnterRadiusSq = FMath::Square(EnterRadius);

    AOWVehicleInteractionProxy* BestProxy = nullptr;
    float BestDistanceSq = EnterRadiusSq;

    for (TActorIterator<AOWVehicleInteractionProxy> It(World); It; ++It)
    {
        AOWVehicleInteractionProxy* Proxy = *It;
        if (!IsValid(Proxy) || !IsValid(Proxy->GetVehiclePawn()))
        {
            continue;
        }

        const float DistanceSq = FVector::DistSquared(
            DriverCharacter->GetActorLocation(),
            Proxy->GetVehiclePawn()->GetActorLocation());

        if (DistanceSq <= BestDistanceSq)
        {
            BestDistanceSq = DistanceSq;
            BestProxy = Proxy;
        }
    }

    if (!BestProxy)
    {
        UE_LOG(
            LogOWGame,
            Verbose,
            TEXT("Vehicle enter pressed but no Chaos vehicle was within %.0f cm."),
            EnterRadius);
        return;
    }

    if (!EnterChaosVehicle(BestProxy->GetVehiclePawn(), DriverCharacter))
    {
        UE_LOG(
            LogOWGame,
            Warning,
            TEXT("Direct proximity entry failed for Chaos vehicle %s."),
            *GetNameSafe(BestProxy->GetVehiclePawn()));
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
