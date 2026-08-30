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
#include "InputCoreTypes.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "UObject/ConstructorHelpers.h"
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

    // Resolve the standard Milestone 1 input assets so the native pawn works
    // without requiring manual Blueprint assignment. Properties remain
    // EditDefaultsOnly so a Blueprint subclass can still override them.
    static ConstructorHelpers::FObjectFinder<UInputMappingContext> DefaultContextFinder(TEXT("/Game/Input/IMC_Default"));
    static ConstructorHelpers::FObjectFinder<UInputAction> MoveActionFinder(TEXT("/Game/Input/IA_Move"));
    static ConstructorHelpers::FObjectFinder<UInputAction> LookActionFinder(TEXT("/Game/Input/IA_Look"));
    static ConstructorHelpers::FObjectFinder<UInputAction> JumpActionFinder(TEXT("/Game/Input/IA_Jump"));
    static ConstructorHelpers::FObjectFinder<UInputAction> InteractActionFinder(TEXT("/Game/Input/IA_Interact"));

    if (DefaultContextFinder.Succeeded())
    {
        DefaultMappingContext = DefaultContextFinder.Object;
    }
    if (MoveActionFinder.Succeeded())
    {
        MoveAction = MoveActionFinder.Object;
    }
    if (LookActionFinder.Succeeded())
    {
        LookAction = LookActionFinder.Object;
    }
    if (JumpActionFinder.Succeeded())
    {
        JumpAction = JumpActionFinder.Object;
    }
    if (InteractActionFinder.Succeeded())
    {
        InteractAction = InteractActionFinder.Object;
    }
}

void AOWGameCharacter::ActivateOnFootInput()
{
    ActivateOnFootInput();
}

void AOWGameCharacter::BeginPlay()
{
    Super::BeginPlay();

    CameraBoom->TargetArmLength = CameraDistance;
    ResolveInputAssets();
    BuildRuntimeMappingContext();
    ApplyDefaultMappingContext();
}

void AOWGameCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // Resolve again at runtime so PIE remains robust even when constructor-time
    // asset lookup did not bind an editor-created input asset.
    ActivateOnFootInput();

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

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("Input assets on %s: Context=%s Move=%s Look=%s Jump=%s Interact=%s"),
        *GetName(),
        DefaultMappingContext ? TEXT("OK") : TEXT("MISSING"),
        MoveAction ? TEXT("OK") : TEXT("MISSING"),
        LookAction ? TEXT("OK") : TEXT("MISSING"),
        JumpAction ? TEXT("OK") : TEXT("MISSING"),
        InteractAction ? TEXT("OK") : TEXT("MISSING"));
}

void AOWGameCharacter::BuildRuntimeMappingContext()
{
    if (RuntimeDefaultMappingContext || !MoveAction || !LookAction || !JumpAction || !InteractAction)
    {
        return;
    }

    RuntimeDefaultMappingContext = NewObject<UInputMappingContext>(this, TEXT("RuntimeDefaultMappingContext"));
    if (!RuntimeDefaultMappingContext)
    {
        UE_LOG(LogOWGame, Error, TEXT("Failed to create runtime input mapping context for %s."), *GetName());
        return;
    }

    auto AddNegate = [this](FEnhancedActionKeyMapping& Mapping)
    {
        Mapping.Modifiers.Add(NewObject<UInputModifierNegate>(RuntimeDefaultMappingContext));
    };

    auto AddSwizzleToY = [this](FEnhancedActionKeyMapping& Mapping)
    {
        UInputModifierSwizzleAxis* Swizzle =
            NewObject<UInputModifierSwizzleAxis>(RuntimeDefaultMappingContext);
        Swizzle->Order = EInputAxisSwizzle::YXZ;
        Mapping.Modifiers.Add(Swizzle);
    };

    FEnhancedActionKeyMapping& MoveW = RuntimeDefaultMappingContext->MapKey(MoveAction, EKeys::W);
    AddSwizzleToY(MoveW);

    FEnhancedActionKeyMapping& MoveS = RuntimeDefaultMappingContext->MapKey(MoveAction, EKeys::S);
    AddNegate(MoveS);
    AddSwizzleToY(MoveS);

    FEnhancedActionKeyMapping& MoveA = RuntimeDefaultMappingContext->MapKey(MoveAction, EKeys::A);
    AddNegate(MoveA);

    RuntimeDefaultMappingContext->MapKey(MoveAction, EKeys::D);

    RuntimeDefaultMappingContext->MapKey(LookAction, EKeys::MouseX);

    FEnhancedActionKeyMapping& LookY = RuntimeDefaultMappingContext->MapKey(LookAction, EKeys::MouseY);
    AddSwizzleToY(LookY);
    AddNegate(LookY);

    RuntimeDefaultMappingContext->MapKey(JumpAction, EKeys::SpaceBar);
    RuntimeDefaultMappingContext->MapKey(InteractAction, EKeys::E);

    UE_LOG(LogOWGame, Log, TEXT("Built runtime Enhanced Input mappings for %s."), *GetName());
}

void AOWGameCharacter::ApplyDefaultMappingContext()
{
    APlayerController* PC = Cast<APlayerController>(GetController());
    if (!PC)
    {
        return;
    }

    ULocalPlayer* LocalPlayer = PC->GetLocalPlayer();
    if (!LocalPlayer)
    {
        return;
    }

    UEnhancedInputLocalPlayerSubsystem* Subsystem =
        LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>();
    if (!Subsystem)
    {
        return;
    }

    if (DefaultMappingContext)
    {
        Subsystem->RemoveMappingContext(DefaultMappingContext);
    }

    if (RuntimeDefaultMappingContext)
    {
        Subsystem->RemoveMappingContext(RuntimeDefaultMappingContext);
        Subsystem->AddMappingContext(RuntimeDefaultMappingContext, 0);
        UE_LOG(
            LogOWGame,
            Log,
            TEXT("Applied runtime input mapping context to %s (Controller=%s)."),
            *GetName(),
            *GetNameSafe(GetController()));
    }
    else
    {
        UE_LOG(LogOWGame, Error, TEXT("Runtime input mapping context is missing on %s."), *GetName());
    }
}

void AOWGameCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D MovementVector = Value.Get<FVector2D>();

    static bool bLoggedMoveInput = false;
    if (!bLoggedMoveInput && !MovementVector.IsNearlyZero())
    {
        bLoggedMoveInput = true;
        UE_LOG(LogOWGame, Log, TEXT("MOVE INPUT RECEIVED: X=%.3f Y=%.3f"), MovementVector.X, MovementVector.Y);
    }
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

    static bool bLoggedLookInput = false;
    if (!bLoggedLookInput && !LookAxis.IsNearlyZero())
    {
        bLoggedLookInput = true;
        UE_LOG(LogOWGame, Log, TEXT("LOOK INPUT RECEIVED: X=%.3f Y=%.3f"), LookAxis.X, LookAxis.Y);
    }
    AddControllerYawInput(LookAxis.X * LookSensitivity);
    AddControllerPitchInput(LookAxis.Y * LookSensitivity);
}

void AOWGameCharacter::StartJump()
{
    UE_LOG(LogOWGame, Log, TEXT("JUMP INPUT RECEIVED"));
    Jump();
}

void AOWGameCharacter::StopJump()
{
    StopJumping();
}

void AOWGameCharacter::TryInteract()
{
    UE_LOG(LogOWGame, Log, TEXT("INTERACT INPUT RECEIVED"));

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
