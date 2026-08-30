#include "OWTestInteractable.h"
#include "../OWGame.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"

AOWTestInteractable::AOWTestInteractable()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    SetRootComponent(SceneRoot);

    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(SceneRoot);
}

bool AOWTestInteractable::CanInteract_Implementation(AActor* Interactor) const
{
    return IsValid(Interactor);
}

FText AOWTestInteractable::GetInteractionPrompt_Implementation(AActor* Interactor) const
{
    return NSLOCTEXT("OWGame", "TestInteractablePrompt", "Interagisci");
}

void AOWTestInteractable::Interact_Implementation(AActor* Interactor)
{
    bHasBeenInteractedWith = !bHasBeenInteractedWith;
    UE_LOG(LogOWGame, Log, TEXT("Test interactable %s used by %s. State=%s"),
        *GetName(),
        IsValid(Interactor) ? *Interactor->GetName() : TEXT("None"),
        bHasBeenInteractedWith ? TEXT("On") : TEXT("Off"));
}
