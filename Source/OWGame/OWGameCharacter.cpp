#include "OWGameCharacter.h"
#include "OWGame.h"
#include "Interaction/OWInteractable.h"

#include "Animation/AnimInstance.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerController.h"
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

namespace
{
void ConfigurePrototypePart(
    UStaticMeshComponent* Component,
    UStaticMesh* Mesh,
    const FVector& Location,
    const FVector& Scale)
{
    if (!Component)
    {
        return;
    }

    Component->SetStaticMesh(Mesh);
    Component->SetRelativeLocation(Location);
    Component->SetRelativeScale3D(Scale);
    Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Component->SetGenerateOverlapEvents(false);
}
}

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
    Movement->MaxWalkSpeed = WalkSpeed;

    VisualRoot = CreateDefaultSubobject<USceneComponent>(TEXT("VisualRoot"));
    VisualRoot->SetupAttachment(RootComponent);

    TorsoMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("TorsoMesh"));
    TorsoMesh->SetupAttachment(VisualRoot);

    HeadMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HeadMesh"));
    HeadMesh->SetupAttachment(VisualRoot);

    LeftArmMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftArmMesh"));
    LeftArmMesh->SetupAttachment(VisualRoot);

    RightArmMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightArmMesh"));
    RightArmMesh->SetupAttachment(VisualRoot);

    LeftLegMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftLegMesh"));
    LeftLegMesh->SetupAttachment(VisualRoot);

    RightLegMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightLegMesh"));
    RightLegMesh->SetupAttachment(VisualRoot);

    UStaticMesh* CylinderMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    UStaticMesh* SphereMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));

    ConfigurePrototypePart(TorsoMesh, CylinderMesh, FVector(0.0f, 0.0f, 28.0f), FVector(0.36f, 0.28f, 0.62f));
    ConfigurePrototypePart(HeadMesh, SphereMesh, FVector(0.0f, 0.0f, 82.0f), FVector(0.30f, 0.30f, 0.30f));
    ConfigurePrototypePart(LeftArmMesh, CylinderMesh, FVector(0.0f, -34.0f, 24.0f), FVector(0.11f, 0.11f, 0.55f));
    ConfigurePrototypePart(RightArmMesh, CylinderMesh, FVector(0.0f, 34.0f, 24.0f), FVector(0.11f, 0.11f, 0.55f));
    ConfigurePrototypePart(LeftLegMesh, CylinderMesh, FVector(0.0f, -14.0f, -46.0f), FVector(0.14f, 0.14f, 0.62f));
    ConfigurePrototypePart(RightLegMesh, CylinderMesh, FVector(0.0f, 14.0f, -46.0f), FVector(0.14f, 0.14f, 0.62f));

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = CameraDistance;
    CameraBoom->TargetOffset = FVector(0.0f, 0.0f, 35.0f);
    CameraBoom->SocketOffset = FVector(0.0f, 55.0f, 35.0f);
    CameraBoom->bUsePawnControlRotation = true;
    CameraBoom->bDoCollisionTest = true;
    CameraBoom->bEnableCameraLag = true;
    CameraBoom->CameraLagSpeed = 12.0f;
    CameraBoom->bEnableCameraRotationLag = true;
    CameraBoom->CameraRotationLagSpeed = 18.0f;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;
    FollowCamera->SetFieldOfView(90.0f);

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

bool AOWGameCharacter::IsUsingTemplateSkeletalCharacter() const
{
    const USkeletalMeshComponent* CharacterMesh = GetMesh();
    return CharacterMesh &&
        CharacterMesh->GetSkeletalMeshAsset() != nullptr &&
        CharacterMesh->IsVisible();
}

void AOWGameCharacter::UsePrototypeVisualFallback()
{
    if (USkeletalMeshComponent* CharacterMesh = GetMesh())
    {
        CharacterMesh->SetSkeletalMeshAsset(nullptr);
        CharacterMesh->SetAnimInstanceClass(nullptr);
        CharacterMesh->SetVisibility(false, true);
    }

    if (VisualRoot)
    {
        VisualRoot->SetVisibility(true, true);
    }
}

bool AOWGameCharacter::TryApplyTemplateSkeletalCharacter()
{
    struct FTemplateCharacterCandidate
    {
        const TCHAR* MeshPath;
        const TCHAR* AnimClassPath;
        const TCHAR* Label;
    };

    static const FTemplateCharacterCandidate Candidates[] =
    {
        {
            TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"),
            TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C"),
            TEXT("Manny Simple / Unarmed")
        },
        {
            TEXT("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple"),
            TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C"),
            TEXT("Quinn Simple / Unarmed")
        },
        {
            TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny.SKM_Manny"),
            TEXT("/Game/Characters/Mannequins/Animations/ABP_Manny.ABP_Manny_C"),
            TEXT("Manny")
        },
        {
            TEXT("/Game/Characters/Mannequins/Meshes/SKM_Quinn.SKM_Quinn"),
            TEXT("/Game/Characters/Mannequins/Animations/ABP_Quinn.ABP_Quinn_C"),
            TEXT("Quinn")
        }
    };

    USkeletalMeshComponent* CharacterMesh = GetMesh();
    if (!CharacterMesh)
    {
        UsePrototypeVisualFallback();
        return false;
    }

    for (const FTemplateCharacterCandidate& Candidate : Candidates)
    {
        USkeletalMesh* SkeletalMesh = LoadObject<USkeletalMesh>(nullptr, Candidate.MeshPath);
        UClass* AnimClass = LoadClass<UAnimInstance>(nullptr, Candidate.AnimClassPath);
        if (!SkeletalMesh || !AnimClass)
        {
            continue;
        }

        CharacterMesh->SetSkeletalMeshAsset(SkeletalMesh);
        CharacterMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
        CharacterMesh->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
        CharacterMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        CharacterMesh->SetGenerateOverlapEvents(false);
        CharacterMesh->SetAnimationMode(EAnimationMode::AnimationBlueprint);
        CharacterMesh->SetAnimInstanceClass(AnimClass);
        CharacterMesh->SetVisibility(true, true);

        if (VisualRoot)
        {
            VisualRoot->SetVisibility(false, true);
        }

        UE_LOG(
            LogOWGame,
            Log,
            TEXT("Using UE Third Person template character %s on %s."),
            Candidate.Label,
            *GetName());
        return true;
    }

    UsePrototypeVisualFallback();
    UE_LOG(
        LogOWGame,
        Warning,
        TEXT("UE Third Person mannequin assets are not installed. Using M3 prototype visuals."));
    return false;
}

void AOWGameCharacter::ActivateOnFootInput()
{
    ResolveInputAssets();
    BuildRuntimeMappingContext();
    ApplyDefaultMappingContext();

    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->MaxWalkSpeed = WalkSpeed;
    }
}

void AOWGameCharacter::BeginPlay()
{
    Super::BeginPlay();

    CameraBoom->TargetArmLength = CameraDistance;
    TryApplyTemplateSkeletalCharacter();
    ActivateOnFootInput();

    GetWorldTimerManager().SetTimer(
        InteractionFocusTimer,
        this,
        &AOWGameCharacter::UpdateInteractionFocus,
        InteractionFocusInterval,
        true,
        0.0f);
}

void AOWGameCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

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

    PlayerInputComponent->BindKey(EKeys::LeftShift, IE_Pressed, this, &AOWGameCharacter::StartSprint);
    PlayerInputComponent->BindKey(EKeys::LeftShift, IE_Released, this, &AOWGameCharacter::StopSprint);
    PlayerInputComponent->BindKey(EKeys::RightShift, IE_Pressed, this, &AOWGameCharacter::StartSprint);
    PlayerInputComponent->BindKey(EKeys::RightShift, IE_Released, this, &AOWGameCharacter::StopSprint);
}

void AOWGameCharacter::ResolveInputAssets()
{
    if (!DefaultMappingContext)
    {
        DefaultMappingContext = LoadObject<UInputMappingContext>(nullptr, TEXT("/Game/Input/IMC_Default.IMC_Default"));
    }
    if (!MoveAction)
    {
        MoveAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_Move.IA_Move"));
    }
    if (!LookAction)
    {
        LookAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_Look.IA_Look"));
    }
    if (!JumpAction)
    {
        JumpAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_Jump.IA_Jump"));
    }
    if (!InteractAction)
    {
        InteractAction = LoadObject<UInputAction>(nullptr, TEXT("/Game/Input/IA_Interact.IA_Interact"));
    }
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
        UInputModifierSwizzleAxis* Swizzle = NewObject<UInputModifierSwizzleAxis>(RuntimeDefaultMappingContext);
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

    UEnhancedInputLocalPlayerSubsystem* Subsystem = LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>();
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
    }
    else
    {
        UE_LOG(LogOWGame, Error, TEXT("Runtime input mapping context is missing on %s."), *GetName());
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

void AOWGameCharacter::StartSprint()
{
    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->MaxWalkSpeed = SprintSpeed;
    }
}

void AOWGameCharacter::StopSprint()
{
    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->MaxWalkSpeed = WalkSpeed;
    }
}

AActor* AOWGameCharacter::FindInteractableInView()
{
    if (!FollowCamera || !GetWorld() || !Controller)
    {
        return nullptr;
    }

    const FVector Start = FollowCamera->GetComponentLocation();
    const FVector End = Start + (FollowCamera->GetForwardVector() * InteractionRange);

    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(OWInteractionFocus), false, this);
    TArray<FHitResult> Hits;

    GetWorld()->SweepMultiByChannel(
        Hits,
        Start,
        End,
        FQuat::Identity,
        ECC_Visibility,
        FCollisionShape::MakeSphere(InteractionAssistRadius),
        QueryParams);

#if !(UE_BUILD_SHIPPING || UE_BUILD_TEST)
    if (bDrawInteractionTrace)
    {
        DrawDebugLine(GetWorld(), Start, End, Hits.Num() > 0 ? FColor::Green : FColor::Red, false, InteractionFocusInterval, 0, 1.0f);
    }
#endif

    for (const FHitResult& Hit : Hits)
    {
        AActor* HitActor = Hit.GetActor();
        if (!IsValid(HitActor) || !HitActor->GetClass()->ImplementsInterface(UOWInteractable::StaticClass()))
        {
            continue;
        }

        if (IOWInteractable::Execute_CanInteract(HitActor, this))
        {
            return HitActor;
        }
    }

    return nullptr;
}

void AOWGameCharacter::UpdateInteractionFocus()
{
    if (!IsLocallyControlled())
    {
        FocusedInteractable.Reset();
        InteractionPrompt = FText::GetEmpty();
        return;
    }

    AActor* FocusedActor = FindInteractableInView();
    FocusedInteractable = FocusedActor;

    InteractionPrompt = FocusedActor
        ? IOWInteractable::Execute_GetInteractionPrompt(FocusedActor, this)
        : FText::GetEmpty();
}

void AOWGameCharacter::TryInteract()
{
    AActor* Interactable = FindInteractableInView();
    if (!Interactable)
    {
        return;
    }

    if (IOWInteractable::Execute_CanInteract(Interactable, this))
    {
        IOWInteractable::Execute_Interact(Interactable, this);
    }
}
