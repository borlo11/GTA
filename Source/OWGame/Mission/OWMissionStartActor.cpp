#include "OWMissionStartActor.h"

#include "OWMissionComponent.h"
#include "../OWGameCharacter.h"
#include "../OWGamePlayerController.h"

#include "Components/CapsuleComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/UObjectGlobals.h"

AOWMissionStartActor::AOWMissionStartActor()
{
    PrimaryActorTick.bCanEverTick = false;

    InteractionCollision = CreateDefaultSubobject<UCapsuleComponent>(TEXT("InteractionCollision"));
    SetRootComponent(InteractionCollision);
    InteractionCollision->InitCapsuleSize(InteractionRadius, 90.0f);
    InteractionCollision->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    InteractionCollision->SetCollisionResponseToAllChannels(ECR_Ignore);
    InteractionCollision->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    InteractionCollision->SetGenerateOverlapEvents(false);

    MarkerMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MarkerMesh"));
    MarkerMesh->SetupAttachment(RootComponent);
    MarkerMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    MarkerMesh->SetGenerateOverlapEvents(false);
    MarkerMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -55.0f));
    MarkerMesh->SetRelativeScale3D(FVector(0.95f, 0.95f, 0.08f));

    if (UStaticMesh* Cylinder =
        LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
    {
        MarkerMesh->SetStaticMesh(Cylinder);
    }

    MarkerText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("MarkerText"));
    MarkerText->SetupAttachment(RootComponent);
    MarkerText->SetRelativeLocation(FVector(0.0f, 0.0f, 115.0f));
    MarkerText->SetHorizontalAlignment(EHTA_Center);
    MarkerText->SetWorldSize(36.0f);
    MarkerText->SetTextRenderColor(FColor(90, 255, 120));
    MarkerText->SetText(FText::FromString(TEXT("HOT RUN")));

    MarkerLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("MarkerLight"));
    MarkerLight->SetupAttachment(RootComponent);
    MarkerLight->SetRelativeLocation(FVector(0.0f, 0.0f, 45.0f));
    MarkerLight->SetLightColor(FLinearColor(0.18f, 1.0f, 0.28f, 1.0f));
    MarkerLight->SetIntensity(900.0f);
    MarkerLight->SetAttenuationRadius(420.0f);
    MarkerLight->SetCastShadows(false);
}

void AOWMissionStartActor::BeginPlay()
{
    Super::BeginPlay();

    RefreshAvailability();

    GetWorldTimerManager().SetTimer(
        AvailabilityTimer,
        this,
        &AOWMissionStartActor::RefreshAvailability,
        AvailabilityUpdateInterval,
        true,
        AvailabilityUpdateInterval);
}

bool AOWMissionStartActor::CanInteract_Implementation(AActor* Interactor) const
{
    const AOWGameCharacter* Character = Cast<AOWGameCharacter>(Interactor);
    const AOWGamePlayerController* PlayerController =
        Character ? Cast<AOWGamePlayerController>(Character->GetController()) : nullptr;
    const UOWMissionComponent* Mission =
        PlayerController ? PlayerController->GetMissionComponent() : nullptr;

    return Mission && !Mission->IsMissionActive();
}

FText AOWMissionStartActor::GetInteractionPrompt_Implementation(AActor* Interactor) const
{
    return CanInteract_Implementation(Interactor)
        ? FText::FromString(TEXT("Avvia Hot Run"))
        : FText::GetEmpty();
}

void AOWMissionStartActor::Interact_Implementation(AActor* Interactor)
{
    AOWGameCharacter* Character = Cast<AOWGameCharacter>(Interactor);
    AOWGamePlayerController* PlayerController =
        Character ? Cast<AOWGamePlayerController>(Character->GetController()) : nullptr;
    UOWMissionComponent* Mission =
        PlayerController ? PlayerController->GetMissionComponent() : nullptr;

    if (!Mission || Mission->IsMissionActive())
    {
        return;
    }

    Mission->StartPrototypeMission();
    RefreshAvailability();
}

void AOWMissionStartActor::RefreshAvailability()
{
    UWorld* World = GetWorld();
    AOWGamePlayerController* PlayerController =
        World ? Cast<AOWGamePlayerController>(World->GetFirstPlayerController()) : nullptr;
    UOWMissionComponent* Mission =
        PlayerController ? PlayerController->GetMissionComponent() : nullptr;

    const bool bAvailable = !Mission || !Mission->IsMissionActive();

    SetActorHiddenInGame(!bAvailable);

    if (InteractionCollision)
    {
        InteractionCollision->SetCollisionEnabled(
            bAvailable ? ECollisionEnabled::QueryOnly : ECollisionEnabled::NoCollision);
    }

    if (MarkerLight)
    {
        MarkerLight->SetVisibility(bAvailable);
    }
}
