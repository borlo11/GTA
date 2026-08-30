#include "OWPopulationNPC.h"

#include "../OWGame.h"

#include "Animation/AnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/UObjectGlobals.h"

AOWPopulationNPC::AOWPopulationNPC()
{
    PrimaryActorTick.bCanEverTick = false;

    GetCapsuleComponent()->InitCapsuleSize(38.0f, 92.0f);

    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;

    UCharacterMovementComponent* Movement = GetCharacterMovement();
    Movement->bOrientRotationToMovement = false;
    Movement->bRunPhysicsWithNoController = true;
    Movement->bUseAccelerationForPaths = true;
    Movement->MaxWalkSpeed = WalkSpeed;
    Movement->MaxAcceleration = 900.0f;
    Movement->BrakingDecelerationWalking = 650.0f;
    Movement->GroundFriction = 4.0f;
}

void AOWPopulationNPC::BeginPlay()
{
    Super::BeginPlay();

    if (!bPopulationInitialized)
    {
        HomeLocation = GetActorLocation();
        VisualVariantSeed = static_cast<int32>(GetUniqueID());
        RandomStream.Initialize(VisualVariantSeed);
        bPopulationInitialized = true;
    }

    ApplyTemplateVisuals();

    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->SetMovementMode(MOVE_Walking);
    }

    PickNewDestination();
    ScheduleSimulationTimer();
}

void AOWPopulationNPC::InitializePopulationMember(int32 Seed, const FVector& InHomeLocation)
{
    HomeLocation = InHomeLocation;
    VisualVariantSeed = Seed;
    RandomStream.Initialize(Seed);
    bPopulationInitialized = true;
    bWaitingAtDestination = false;
    PickNewDestination();
}

void AOWPopulationNPC::ApplyTemplateVisuals()
{
    struct FVisualCandidate
    {
        const TCHAR* MeshPath;
        const TCHAR* AnimClassPath;
    };

    static const FVisualCandidate MannyCandidate =
    {
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"),
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C")
    };

    static const FVisualCandidate QuinnCandidate =
    {
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple"),
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C")
    };

    const FVisualCandidate& Candidate =
        (VisualVariantSeed & 1) == 0 ? MannyCandidate : QuinnCandidate;

    USkeletalMesh* SkeletalMesh = LoadObject<USkeletalMesh>(nullptr, Candidate.MeshPath);
    UClass* AnimClass = LoadClass<UAnimInstance>(nullptr, Candidate.AnimClassPath);
    USkeletalMeshComponent* CharacterMesh = GetMesh();

    if (!CharacterMesh || !SkeletalMesh || !AnimClass)
    {
        UE_LOG(LogOWGame, Warning, TEXT("Population NPC %s could not load mannequin visuals."), *GetName());
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

void AOWPopulationNPC::SetSimulationTier(EOWPopulationSimulationTier NewTier)
{
    if (SimulationTier == NewTier)
    {
        return;
    }

    SimulationTier = NewTier;

    if (SimulationTier == EOWPopulationSimulationTier::Dormant)
    {
        GetWorldTimerManager().ClearTimer(SimulationTimer);
        StopHorizontalMovement();

        if (UCharacterMovementComponent* Movement = GetCharacterMovement())
        {
            Movement->SetComponentTickEnabled(false);
        }

        if (USkeletalMeshComponent* CharacterMesh = GetMesh())
        {
            CharacterMesh->SetComponentTickEnabled(false);
        }

        return;
    }

    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->SetComponentTickEnabled(true);
    }

    if (USkeletalMeshComponent* CharacterMesh = GetMesh())
    {
        CharacterMesh->SetComponentTickEnabled(true);
    }

    ScheduleSimulationTimer();
}

void AOWPopulationNPC::ScheduleSimulationTimer()
{
    if (!GetWorld() || SimulationTier == EOWPopulationSimulationTier::Dormant)
    {
        return;
    }

    float Interval = HighSimulationInterval;
    switch (SimulationTier)
    {
    case EOWPopulationSimulationTier::Medium:
        Interval = MediumSimulationInterval;
        break;
    case EOWPopulationSimulationTier::Low:
        Interval = LowSimulationInterval;
        break;
    default:
        break;
    }

    GetWorldTimerManager().SetTimer(
        SimulationTimer,
        this,
        &AOWPopulationNPC::UpdateWander,
        Interval,
        true,
        RandomStream.FRandRange(0.0f, Interval));
}

void AOWPopulationNPC::PickNewDestination()
{
    const float Angle = RandomStream.FRandRange(0.0f, 2.0f * PI);
    const float Radius = RandomStream.FRandRange(WanderRadius * 0.25f, WanderRadius);

    WanderDestination = HomeLocation + FVector(
        FMath::Cos(Angle) * Radius,
        FMath::Sin(Angle) * Radius,
        0.0f);
}

void AOWPopulationNPC::StopHorizontalMovement()
{
    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->RequestDirectMove(FVector::ZeroVector, false);
        Movement->StopMovementImmediately();
    }
}

void AOWPopulationNPC::UpdateWander()
{
    UWorld* World = GetWorld();
    UCharacterMovementComponent* Movement = GetCharacterMovement();
    if (!World || !Movement || SimulationTier == EOWPopulationSimulationTier::Dormant)
    {
        return;
    }

    const float Now = World->GetTimeSeconds();

    if (bWaitingAtDestination)
    {
        StopHorizontalMovement();

        if (Now < IdleUntilWorldTime)
        {
            return;
        }

        bWaitingAtDestination = false;
        PickNewDestination();
    }

    FVector ToDestination = WanderDestination - GetActorLocation();
    ToDestination.Z = 0.0f;

    if (ToDestination.SizeSquared() < FMath::Square(80.0f))
    {
        StopHorizontalMovement();
        bWaitingAtDestination = true;
        IdleUntilWorldTime = Now + RandomStream.FRandRange(0.6f, 2.2f);
        return;
    }

    const FVector Direction = ToDestination.GetSafeNormal();
    const float TierSpeedScale =
        SimulationTier == EOWPopulationSimulationTier::Low ? 0.75f :
        SimulationTier == EOWPopulationSimulationTier::Medium ? 0.90f :
        1.0f;

    const float DesiredSpeed = WalkSpeed * TierSpeedScale;
    Movement->MaxWalkSpeed = DesiredSpeed;

    // Feed movement through CharacterMovement's requested-move path instead of
    // writing Velocity directly. ABP_Unarmed derives locomotion state from
    // movement acceleration, so direct Velocity writes made the capsule move
    // while the mannequin remained in its idle pose.
    Movement->RequestDirectMove(Direction * DesiredSpeed, false);

    const FRotator TargetRotation(0.0f, Direction.Rotation().Yaw, 0.0f);
    const float RotationStep =
        SimulationTier == EOWPopulationSimulationTier::High ? HighSimulationInterval :
        SimulationTier == EOWPopulationSimulationTier::Medium ? MediumSimulationInterval :
        LowSimulationInterval;

    SetActorRotation(FMath::RInterpTo(GetActorRotation(), TargetRotation, RotationStep, 5.0f));
}
