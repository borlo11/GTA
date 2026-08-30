#include "OWPoliceOfficer.h"

#include "../OWGame.h"
#include "../OWGamePlayerController.h"
#include "../Crime/OWWantedComponent.h"
#include "../Combat/OWHealthComponent.h"

#include "Animation/AnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "UObject/UObjectGlobals.h"

AOWPoliceOfficer::AOWPoliceOfficer()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bStartWithTickEnabled = true;

    GetCapsuleComponent()->InitCapsuleSize(38.0f, 92.0f);

    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;

    UCharacterMovementComponent* Movement = GetCharacterMovement();
    Movement->bOrientRotationToMovement = false;
    Movement->bRunPhysicsWithNoController = true;
    Movement->MaxWalkSpeed = ChaseSpeed;
    Movement->MaxAcceleration = 1400.0f;
    Movement->BrakingDecelerationWalking = 900.0f;
    Movement->GroundFriction = 5.0f;

    PoliceLabel = CreateDefaultSubobject<UTextRenderComponent>(TEXT("PoliceLabel"));
    PoliceLabel->SetupAttachment(RootComponent);
    PoliceLabel->SetRelativeLocation(FVector(0.0f, 0.0f, 120.0f));
    PoliceLabel->SetHorizontalAlignment(EHTA_Center);
    PoliceLabel->SetWorldSize(26.0f);
    PoliceLabel->SetTextRenderColor(FColor(50, 120, 255));
    PoliceLabel->SetText(FText::FromString(TEXT("POLICE")));

    HealthComponent = CreateDefaultSubobject<UOWHealthComponent>(TEXT("HealthComponent"));
}

void AOWPoliceOfficer::BeginPlay()
{
    Super::BeginPlay();

    SearchRandom.Initialize(static_cast<int32>(GetUniqueID()));
    ApplyPoliceVisuals();

    if (HealthComponent)
    {
        HealthComponent->OnDeath.AddDynamic(this, &AOWPoliceOfficer::HandleDeath);
    }

    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->SetMovementMode(MOVE_Walking);
    }
}

bool AOWPoliceOfficer::IsDead() const
{
    return HealthComponent && HealthComponent->IsDead();
}

void AOWPoliceOfficer::InitializePoliceTarget(AOWGamePlayerController* InTargetController)
{
    TargetController = InTargetController;
}

void AOWPoliceOfficer::ApplyPoliceVisuals()
{
    USkeletalMesh* SkeletalMesh = LoadObject<USkeletalMesh>(
        nullptr,
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"));
    UClass* AnimClass = LoadClass<UAnimInstance>(
        nullptr,
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C"));

    USkeletalMeshComponent* CharacterMesh = GetMesh();
    if (!CharacterMesh || !SkeletalMesh || !AnimClass)
    {
        UE_LOG(LogOWGame, Warning, TEXT("Police officer %s could not load mannequin visuals."), *GetName());
        return;
    }

    CharacterMesh->SetSkeletalMeshAsset(SkeletalMesh);
    CharacterMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -92.0f));
    CharacterMesh->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
    CharacterMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    CharacterMesh->SetGenerateOverlapEvents(false);
    CharacterMesh->SetAnimationMode(EAnimationMode::AnimationBlueprint);
    CharacterMesh->SetAnimInstanceClass(AnimClass);
    CharacterMesh->SetVisibility(true, true);
}

bool AOWPoliceOfficer::CanSeeTargetPawn(const APawn* TargetPawn) const
{
    const UWorld* World = GetWorld();
    if (!World || !TargetPawn)
    {
        return false;
    }

    const FVector Start = GetActorLocation() + FVector(0.0f, 0.0f, 70.0f);
    const FVector End = TargetPawn->GetActorLocation() + FVector(0.0f, 0.0f, 60.0f);

    if (FVector::DistSquared(Start, End) > FMath::Square(SightRange))
    {
        return false;
    }

    FHitResult Hit;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(OWPoliceSight), false, this);

    const bool bBlocked = World->LineTraceSingleByChannel(
        Hit,
        Start,
        End,
        ECC_Visibility,
        QueryParams);

    return !bBlocked || Hit.GetActor() == TargetPawn;
}

FVector AOWPoliceOfficer::GetSearchDestination(const FVector& LastKnownLocation)
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return LastKnownLocation;
    }

    const double Now = World->GetTimeSeconds();
    const bool bReachedSearchPoint =
        bHasSearchDestination &&
        FVector::DistSquared2D(GetActorLocation(), SearchDestination) < FMath::Square(100.0f);

    if (!bHasSearchDestination || bReachedSearchPoint || Now >= NextSearchRetargetWorldTime)
    {
        const float Angle = SearchRandom.FRandRange(0.0f, 2.0f * PI);
        const float Radius = SearchRandom.FRandRange(SearchRadius * 0.25f, SearchRadius);

        SearchDestination = LastKnownLocation + FVector(
            FMath::Cos(Angle) * Radius,
            FMath::Sin(Angle) * Radius,
            0.0f);

        bHasSearchDestination = true;
        NextSearchRetargetWorldTime = Now + SearchRetargetSeconds;
    }

    return SearchDestination;
}

void AOWPoliceOfficer::StopPursuitMovement()
{
    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->StopMovementImmediately();
    }
}

void AOWPoliceOfficer::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (IsDead())
    {
        return;
    }

    AOWGamePlayerController* PlayerController = TargetController.Get();
    UOWWantedComponent* Wanted = PlayerController ? PlayerController->GetWantedComponent() : nullptr;
    APawn* TargetPawn = PlayerController ? PlayerController->GetPawn() : nullptr;

    if (!Wanted || Wanted->GetWantedLevel() <= 0 || !TargetPawn)
    {
        StopPursuitMovement();
        return;
    }

    FVector Destination = GetActorLocation();
    bool bHasDestination = false;

    if (CanSeeTargetPawn(TargetPawn))
    {
        Destination = TargetPawn->GetActorLocation();
        bHasDestination = true;
        bHasSearchDestination = false;
        Wanted->MarkObserved(TargetPawn->GetActorLocation());
    }
    else if (Wanted->HasLastKnownLocation())
    {
        Destination = GetSearchDestination(Wanted->GetLastKnownLocation());
        bHasDestination = true;
    }

    if (!bHasDestination)
    {
        StopPursuitMovement();
        return;
    }

    FVector ToDestination = Destination - GetActorLocation();
    ToDestination.Z = 0.0f;

    if (ToDestination.SizeSquared() <= FMath::Square(StopDistance))
    {
        StopPursuitMovement();
        return;
    }

    const FVector Direction = ToDestination.GetSafeNormal();

    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->MaxWalkSpeed = ChaseSpeed;
    }

    AddMovementInput(Direction, 1.0f, true);

    const FRotator TargetRotation(0.0f, Direction.Rotation().Yaw, 0.0f);
    SetActorRotation(FMath::RInterpTo(GetActorRotation(), TargetRotation, DeltaSeconds, 7.0f));
}


void AOWPoliceOfficer::HandleDeath(AActor* DeadActor)
{
    StopPursuitMovement();
    SetActorTickEnabled(false);

    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->DisableMovement();
        Movement->SetComponentTickEnabled(false);
    }

    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    if (USkeletalMeshComponent* CharacterMesh = GetMesh())
    {
        CharacterMesh->SetComponentTickEnabled(false);
        CharacterMesh->bPauseAnims = true;
    }

    if (PoliceLabel)
    {
        PoliceLabel->SetVisibility(false);
    }

    SetLifeSpan(3.0f);

    UE_LOG(LogOWGame, Log, TEXT("Police officer %s died."), *GetName());
}
