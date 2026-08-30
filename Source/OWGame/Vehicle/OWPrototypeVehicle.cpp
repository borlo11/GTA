#include "OWPrototypeVehicle.h"

#include "../OWGame.h"
#include "../OWGameCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/FloatingPawnMovement.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputAction.h"
#include "InputActionValue.h"
#include "InputCoreTypes.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "UObject/UObjectGlobals.h"

namespace
{
UEnhancedInputLocalPlayerSubsystem* GetEnhancedInputSubsystem(AController* Controller)
{
    APlayerController* PlayerController = Cast<APlayerController>(Controller);
    if (!PlayerController)
    {
        return nullptr;
    }

    ULocalPlayer* LocalPlayer = PlayerController->GetLocalPlayer();
    return LocalPlayer ? LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
}
}

AOWPrototypeVehicle::AOWPrototypeVehicle()
{
    PrimaryActorTick.bCanEverTick = false;

    VehicleMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VehicleMesh"));
    SetRootComponent(VehicleMesh);
    VehicleMesh->SetCollisionProfileName(TEXT("BlockAll"));
    VehicleMesh->SetRelativeScale3D(FVector(2.5f, 1.3f, 0.6f));

    if (UStaticMesh* CubeMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")))
    {
        VehicleMesh->SetStaticMesh(CubeMesh);
    }

    VehicleMovement = CreateDefaultSubobject<UFloatingPawnMovement>(TEXT("VehicleMovement"));
    VehicleMovement->SetUpdatedComponent(VehicleMesh);
    VehicleMovement->MaxSpeed = 1800.0f;
    VehicleMovement->Acceleration = 4000.0f;
    VehicleMovement->Deceleration = 6000.0f;
    VehicleMovement->TurningBoost = 4.0f;

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(VehicleMesh);
    CameraBoom->TargetArmLength = 550.0f;
    CameraBoom->SetRelativeLocation(FVector(0.0f, 0.0f, 120.0f));
    CameraBoom->bUsePawnControlRotation = true;
    CameraBoom->bEnableCameraLag = true;
    CameraBoom->CameraLagSpeed = 8.0f;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;

    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;

}

void AOWPrototypeVehicle::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    ResolveInputAssets();
    BuildRuntimeVehicleMappingContext();

    UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent);
    if (!EnhancedInput)
    {
        UE_LOG(LogOWGame, Error, TEXT("Expected EnhancedInputComponent on vehicle %s."), *GetName());
        return;
    }

    if (ThrottleAction)
    {
        EnhancedInput->BindAction(ThrottleAction, ETriggerEvent::Triggered, this, &AOWPrototypeVehicle::Throttle);
    }
    if (SteerAction)
    {
        EnhancedInput->BindAction(SteerAction, ETriggerEvent::Triggered, this, &AOWPrototypeVehicle::Steer);
    }
    if (LookAction)
    {
        EnhancedInput->BindAction(LookAction, ETriggerEvent::Triggered, this, &AOWPrototypeVehicle::Look);
    }
    if (BrakeAction)
    {
        EnhancedInput->BindAction(BrakeAction, ETriggerEvent::Started, this, &AOWPrototypeVehicle::Brake);
    }
    if (ExitAction)
    {
        EnhancedInput->BindAction(ExitAction, ETriggerEvent::Started, this, &AOWPrototypeVehicle::ExitVehicle);
    }
}

void AOWPrototypeVehicle::PossessedBy(AController* NewController)
{
    Super::PossessedBy(NewController);
    ResolveInputAssets();
    BuildRuntimeVehicleMappingContext();
    AddVehicleMappingContext(NewController);
}

void AOWPrototypeVehicle::UnPossessed()
{
    AController* OldController = GetController();
    RemoveVehicleMappingContext(OldController);
    RestoreDriverCharacter();
    Super::UnPossessed();
}

UPawnMovementComponent* AOWPrototypeVehicle::GetMovementComponent() const
{
    return VehicleMovement;
}

bool AOWPrototypeVehicle::CanInteract_Implementation(AActor* Interactor) const
{
    const AOWGameCharacter* Character = Cast<AOWGameCharacter>(Interactor);
    return !IsOccupied() && IsValid(Character) && IsValid(Character->GetController());
}

void AOWPrototypeVehicle::Interact_Implementation(AActor* Interactor)
{
    AOWGameCharacter* Character = Cast<AOWGameCharacter>(Interactor);
    APlayerController* PlayerController = Character ? Cast<APlayerController>(Character->GetController()) : nullptr;
    if (!Character || !PlayerController || IsOccupied())
    {
        return;
    }

    DriverCharacter = Character;
    Character->SetActorHiddenInGame(true);
    Character->SetActorEnableCollision(false);

    if (UCharacterMovementComponent* CharacterMovement = Character->GetCharacterMovement())
    {
        CharacterMovement->DisableMovement();
    }

    Character->SetActorLocation(GetActorLocation());
    PlayerController->Possess(this);

    UE_LOG(LogOWGame, Log, TEXT("%s entered vehicle %s."), *Character->GetName(), *GetName());
}

bool AOWPrototypeVehicle::IsOccupied() const
{
    return IsValid(DriverCharacter);
}

float AOWPrototypeVehicle::GetConfiguredMaxSpeed() const
{
    return VehicleMovement ? VehicleMovement->MaxSpeed : 0.0f;
}

void AOWPrototypeVehicle::Throttle(const FInputActionValue& Value)
{
    const float ThrottleValue = FMath::Clamp(Value.Get<float>(), -1.0f, 1.0f);
    AddMovementInput(GetActorForwardVector(), ThrottleValue);
}

void AOWPrototypeVehicle::Steer(const FInputActionValue& Value)
{
    if (!VehicleMovement || !GetWorld())
    {
        return;
    }

    const float SteeringValue = FMath::Clamp(Value.Get<float>(), -1.0f, 1.0f);
    const float ForwardSpeed = FVector::DotProduct(VehicleMovement->Velocity, GetActorForwardVector());
    const float SpeedAlpha = FMath::Clamp(
        FMath::Abs(ForwardSpeed) / FMath::Max(VehicleMovement->MaxSpeed, 1.0f),
        0.0f,
        1.0f);

    if (SpeedAlpha <= KINDA_SMALL_NUMBER)
    {
        return;
    }

    const float TravelDirection = ForwardSpeed >= 0.0f ? 1.0f : -1.0f;
    const float DeltaYaw =
        SteeringValue *
        TravelDirection *
        SteeringRateDegreesPerSecond *
        SpeedAlpha *
        GetWorld()->GetDeltaSeconds();

    AddActorLocalRotation(FRotator(0.0f, DeltaYaw, 0.0f));
}

void AOWPrototypeVehicle::Look(const FInputActionValue& Value)
{
    const FVector2D LookAxis = Value.Get<FVector2D>();
    AddControllerYawInput(LookAxis.X);
    AddControllerPitchInput(LookAxis.Y);
}

void AOWPrototypeVehicle::Brake()
{
    if (VehicleMovement)
    {
        VehicleMovement->StopMovementImmediately();
    }
}

void AOWPrototypeVehicle::ExitVehicle()
{
    APlayerController* PlayerController = Cast<APlayerController>(GetController());
    AOWGameCharacter* Character = DriverCharacter;

    if (!PlayerController || !IsValid(Character))
    {
        return;
    }

    RemoveVehicleMappingContext(PlayerController);

    DriverCharacter = nullptr;
    const FVector ExitLocation = GetActorTransform().TransformPosition(ExitOffset);
    Character->SetActorLocationAndRotation(
        ExitLocation,
        FRotator(0.0f, GetActorRotation().Yaw, 0.0f),
        false,
        nullptr,
        ETeleportType::TeleportPhysics);
    Character->SetActorHiddenInGame(false);
    Character->SetActorEnableCollision(true);

    if (UCharacterMovementComponent* CharacterMovement = Character->GetCharacterMovement())
    {
        CharacterMovement->SetMovementMode(MOVE_Walking);
    }

    PlayerController->Possess(Character);
    Character->ActivateOnFootInput();

    UE_LOG(LogOWGame, Log, TEXT("%s exited vehicle %s."), *Character->GetName(), *GetName());
}

void AOWPrototypeVehicle::ResolveInputAssets()
{
    if (!VehicleMappingContext)
    {
        VehicleMappingContext = LoadObject<UInputMappingContext>(nullptr, TEXT("/Game/Input/IMC_Vehicle.IMC_Vehicle"));
    }
    if (!ThrottleAction)
    {
        ThrottleAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_VehicleThrottle.IA_VehicleThrottle"));
    }
    if (!SteerAction)
    {
        SteerAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_VehicleSteer.IA_VehicleSteer"));
    }
    if (!BrakeAction)
    {
        BrakeAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_VehicleBrake.IA_VehicleBrake"));
    }
    if (!ExitAction)
    {
        ExitAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_VehicleExit.IA_VehicleExit"));
    }
    if (!LookAction)
    {
        LookAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_Look.IA_Look"));
    }
}

void AOWPrototypeVehicle::BuildRuntimeVehicleMappingContext()
{
    if (RuntimeVehicleMappingContext || !ThrottleAction || !SteerAction || !BrakeAction || !ExitAction)
    {
        return;
    }

    RuntimeVehicleMappingContext = NewObject<UInputMappingContext>(this, TEXT("RuntimeVehicleMappingContext"));
    if (!RuntimeVehicleMappingContext)
    {
        UE_LOG(LogOWGame, Error, TEXT("Failed to create runtime vehicle mapping context for %s."), *GetName());
        return;
    }

    auto AddNegate = [this](FEnhancedActionKeyMapping& Mapping)
    {
        Mapping.Modifiers.Add(NewObject<UInputModifierNegate>(RuntimeVehicleMappingContext));
    };

    RuntimeVehicleMappingContext->MapKey(ThrottleAction, EKeys::W);

    FEnhancedActionKeyMapping& Reverse =
        RuntimeVehicleMappingContext->MapKey(ThrottleAction, EKeys::S);
    AddNegate(Reverse);

    FEnhancedActionKeyMapping& SteerLeft =
        RuntimeVehicleMappingContext->MapKey(SteerAction, EKeys::A);
    AddNegate(SteerLeft);

    RuntimeVehicleMappingContext->MapKey(SteerAction, EKeys::D);
    if (LookAction)
    {
        RuntimeVehicleMappingContext->MapKey(LookAction, EKeys::MouseX);

        FEnhancedActionKeyMapping& LookY =
            RuntimeVehicleMappingContext->MapKey(LookAction, EKeys::MouseY);
        UInputModifierSwizzleAxis* Swizzle =
            NewObject<UInputModifierSwizzleAxis>(RuntimeVehicleMappingContext);
        Swizzle->Order = EInputAxisSwizzle::YXZ;
        LookY.Modifiers.Add(Swizzle);
        LookY.Modifiers.Add(NewObject<UInputModifierNegate>(RuntimeVehicleMappingContext));
    }

    RuntimeVehicleMappingContext->MapKey(BrakeAction, EKeys::SpaceBar);
    RuntimeVehicleMappingContext->MapKey(ExitAction, EKeys::E);

    UE_LOG(LogOWGame, Log, TEXT("Built runtime vehicle Enhanced Input mappings for %s."), *GetName());
}

void AOWPrototypeVehicle::AddVehicleMappingContext(AController* InController)
{
    if (UEnhancedInputLocalPlayerSubsystem* Subsystem = GetEnhancedInputSubsystem(InController))
    {
        // M2 gives the vehicle exclusive ownership of gameplay keys while it is
        // possessed. This prevents the on-foot E/WASD mappings from competing
        // with vehicle actions.
        Subsystem->ClearAllMappings();

        if (RuntimeVehicleMappingContext)
        {
            Subsystem->AddMappingContext(RuntimeVehicleMappingContext, 10);
            UE_LOG(LogOWGame, Log, TEXT("Applied exclusive vehicle mapping context to %s."), *GetName());
        }
        else
        {
            UE_LOG(LogOWGame, Error, TEXT("Runtime vehicle mapping context missing on %s."), *GetName());
        }
    }
}

void AOWPrototypeVehicle::RemoveVehicleMappingContext(AController* InController)
{
    if (UEnhancedInputLocalPlayerSubsystem* Subsystem = GetEnhancedInputSubsystem(InController))
    {
        if (VehicleMappingContext)
        {
            Subsystem->RemoveMappingContext(VehicleMappingContext);
        }
        if (RuntimeVehicleMappingContext)
        {
            Subsystem->RemoveMappingContext(RuntimeVehicleMappingContext);
        }
    }
}

void AOWPrototypeVehicle::RestoreDriverCharacter()
{
    if (!IsOccupied())
    {
        DriverCharacter = nullptr;
        return;
    }

    AOWGameCharacter* Character = DriverCharacter;
    DriverCharacter = nullptr;

    const FVector ExitLocation = GetActorTransform().TransformPosition(ExitOffset);
    Character->SetActorLocationAndRotation(
        ExitLocation,
        FRotator(0.0f, GetActorRotation().Yaw, 0.0f),
        false,
        nullptr,
        ETeleportType::TeleportPhysics);
    Character->SetActorHiddenInGame(false);
    Character->SetActorEnableCollision(true);

    if (UCharacterMovementComponent* CharacterMovement = Character->GetCharacterMovement())
    {
        CharacterMovement->SetMovementMode(MOVE_Walking);
    }
}
