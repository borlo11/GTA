#include "OWVehicleInteractionProxy.h"

#include "../OWGame.h"
#include "../OWGameCharacter.h"
#include "../OWGamePlayerController.h"

#include "Components/BoxComponent.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"

AOWVehicleInteractionProxy::AOWVehicleInteractionProxy()
{
    PrimaryActorTick.bCanEverTick = false;

    InteractionCollision = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractionCollision"));
    SetRootComponent(InteractionCollision);

    InteractionCollision->SetBoxExtent(FVector(245.0f, 125.0f, 85.0f));
    InteractionCollision->SetRelativeLocation(FVector(0.0f, 0.0f, 75.0f));
    InteractionCollision->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    InteractionCollision->SetCollisionResponseToAllChannels(ECR_Ignore);
    InteractionCollision->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    InteractionCollision->SetGenerateOverlapEvents(false);
}

void AOWVehicleInteractionProxy::InitializeVehicle(APawn* InVehiclePawn)
{
    VehiclePawn = InVehiclePawn;

    if (!IsValid(VehiclePawn))
    {
        UE_LOG(LogOWGame, Error, TEXT("Chaos vehicle proxy initialized without a valid vehicle pawn."));
        return;
    }

    SetActorLocationAndRotation(
        VehiclePawn->GetActorLocation(),
        VehiclePawn->GetActorRotation(),
        false,
        nullptr,
        ETeleportType::TeleportPhysics);

    AttachToActor(
        VehiclePawn,
        FAttachmentTransformRules::KeepWorldTransform);
}

bool AOWVehicleInteractionProxy::CanInteract_Implementation(AActor* Interactor) const
{
    const AOWGameCharacter* Character = Cast<AOWGameCharacter>(Interactor);

    return IsValid(Character) &&
        IsValid(Character->GetController()) &&
        IsValid(VehiclePawn);
}

FText AOWVehicleInteractionProxy::GetInteractionPrompt_Implementation(AActor* Interactor) const
{
    return CanInteract_Implementation(Interactor)
        ? NSLOCTEXT("OWGame", "EnterChaosVehiclePrompt", "Entra nel veicolo")
        : FText::GetEmpty();
}

void AOWVehicleInteractionProxy::Interact_Implementation(AActor* Interactor)
{
    AOWGameCharacter* Character = Cast<AOWGameCharacter>(Interactor);
    AOWGamePlayerController* PlayerController =
        Character ? Cast<AOWGamePlayerController>(Character->GetController()) : nullptr;

    if (!Character || !PlayerController || !CanInteract_Implementation(Interactor))
    {
        return;
    }

    if (!PlayerController->EnterChaosVehicle(VehiclePawn, Character))
    {
        UE_LOG(
            LogOWGame,
            Warning,
            TEXT("Failed to enter Chaos vehicle %s through %s."),
            *GetNameSafe(VehiclePawn),
            *GetName());
    }
}
