#include "OWGameCharacter.h"
#include "OWGame.h"
#include "Interaction/OWInteractable.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "UObject/UObjectGlobals.h"

#if !(UE_BUILD_SHIPPING || UE_BUILD_TEST)
#include "DrawDebugHelpers.h"
#endif

AOWGameCharacter::AOWGameCharacter()
{
    PrimaryActorTick.bCanEverTick = false;

    GetCapsuleComponent()->InitCapsuleSize(42.0f, 96.0f);

    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;

    UCharacterMovementComponent* Movement = GetCharacterMovement();
    Movement->bOrientRotationToMovement = true;
    Movement->RotationRate = FRotator(0.0f, 500.0f, 0.0f);
    Movement->JumpZVelocity = 700.0f;
    Movement->AirControl = 0.35f;
    Movement->MaxWalkSpeed = 500.0f;

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = CameraDistance;
    CameraBoom->bUsePawnControlRotation = true;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;
}

void AOWGameCharacter::ResolveInputAssets()
{
    if (!DefaultMappingContext)
    {
        DefaultMappingContext = LoadObject<UInputMappingContext>(
            nullptr,
            TEXT("/Game/Input/IMC_Default.IMC_Default"));
    }

    if (!MoveAction)
    {
        MoveAction = LoadObject<UInputAction>(
            nullptr,
            TEXT("/Game/Input/IA_Move.IA_Move"));
    }

    if (!LookAction)
    {
        LookAction = LoadObject<UInputAction>(
            nullptr,
            TEXT("/Game/Input/IA_Look.IA_Look"));
    }

    if (!JumpAction)
    {
        JumpAction = LoadObject<UInputAction>(
            nullptr,
            TEXT("/Game/Input/IA_Jump.IA_Jump"));
    }

    if (!InteractAction)
    {
        InteractAction = LoadObject<UInputAction>(
            nullptr,
            TEXT("/Game/Input/IA_Interact.IA_Interact"));
    }
}

void AOWGameCharacter::BeginPlay()
{
    Super::BeginPlay();

    ResolveInputAssets();
    CameraBoom->TargetArmLength = CameraDistance;

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (ULocalPlayer* LocalPlayer = PC->GetLocalPlayer())
        {
            if (UEnhancedInputLocalPlayerSubsystem* Subsystem = LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            {
                if (DefaultMappingContext)
                {
                    Subsystem->AddMappingContext(DefaultMappingContext, 0);
                }
                else
                {
                    UE_LOG(LogOWGame, Warning, TEXT("No DefaultMappingContext found at /Game/Input/IMC_Default."));
                }
            }
        }
    }
}

void AOWGameCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    ResolveInputAssets();

    UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent);
    if (!EnhancedInput)
    {
        UE_LOG(LogOWGame, Error, TEXT("Expected EnhancedInputComponent on %s."), *GetName());
        return;
    }

    if (MoveAction)
    {
        EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AOWGameCharacter::Move);
    }

    if (LookAction)
    {
        EnhancedInput->BindAction(LookAction, ETriggerEvent::Triggered, this, &AOWGameCharacter::Look);
    }

    if (JumpAction)
    {
        EnhancedInput->BindAction(JumpAction, ETriggerEvent::Started, this, &AOWGameCharacter::StartJump);
        EnhancedInput->BindAction(JumpAction, ETriggerEvent::Completed, this, &AOWGameCharacter::StopJump);
    }

    if (InteractAction)
    {
        EnhancedInput->BindAction(InteractAction, ETriggerEvent::Started, this, &AOWGameCharacter::TryInteract);
    }
}

void AOWGameCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D MovementVector = Value.Get<FVector2D>();
    if (!Controller)
    {
        return;
    }

    const FRotator ControlRotation = Controller->GetControlRotation();
    const FRotator YawRotation(0.0f, ControlRotation.Yaw, 0.0f);

    const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
    const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

    AddMovementInput(ForwardDirection, MovementVector.Y);
    AddMovementInput(RightDirection, MovementVector.X);
}

void AOWGameCharacter::Look(const FInputActionValue& Value)
{
    const FVector2D LookAxis = Value.Get<FVector2D>();
    AddControllerYawInput(LookAxis.X * LookSensitivity);
    AddControllerPitchInput(LookAxis.Y * LookSensitivity);
}

void AOWGameCharacter::StartJump()
{
    Jump();
}

void AOWGameCharacter::StopJump()
{
    StopJumping();
}

void AOWGameCharacter::TryInteract()
{
    if (!FollowCamera || !GetWorld())
    {
        return;
    }

    const FVector Start = FollowCamera->GetComponentLocation();
    const FVector End = Start + (FollowCamera->GetForwardVector() * InteractionRange);

    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(OWInteractionTrace), false, this);
    FHitResult Hit;

    const bool bHit = GetWorld()->LineTraceSingleByChannel(
        Hit,
        Start,
        End,
        ECC_Visibility,
        QueryParams);

#if !(UE_BUILD_SHIPPING || UE_BUILD_TEST)
    if (bDrawInteractionTrace)
    {
        DrawDebugLine(
            GetWorld(),
            Start,
            End,
            bHit ? FColor::Green : FColor::Red,
            false,
            1.0f,
            0,
            1.0f);
    }
#endif

    AActor* HitActor = Hit.GetActor();
    if (!bHit || !IsValid(HitActor) || !HitActor->GetClass()->ImplementsInterface(UOWInteractable::StaticClass()))
    {
        return;
    }

    if (IOWInteractable::Execute_CanInteract(HitActor, this))
    {
        IOWInteractable::Execute_Interact(HitActor, this);
    }
}
