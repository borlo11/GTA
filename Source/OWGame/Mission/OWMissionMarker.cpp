#include "OWMissionMarker.h"

#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/UObjectGlobals.h"

AOWMissionMarker::AOWMissionMarker()
{
    PrimaryActorTick.bCanEverTick = false;

    MarkerMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MarkerMesh"));
    SetRootComponent(MarkerMesh);
    MarkerMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    MarkerMesh->SetGenerateOverlapEvents(false);
    MarkerMesh->SetRelativeScale3D(FVector(0.34f, 0.34f, 0.34f));

    if (UStaticMesh* Sphere =
        LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")))
    {
        MarkerMesh->SetStaticMesh(Sphere);
    }

    MarkerText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("MarkerText"));
    MarkerText->SetupAttachment(RootComponent);
    MarkerText->SetRelativeLocation(FVector(0.0f, 0.0f, 95.0f));
    MarkerText->SetHorizontalAlignment(EHTA_Center);
    MarkerText->SetWorldSize(32.0f);
    MarkerText->SetTextRenderColor(FColor(255, 210, 40));
    MarkerText->SetText(FText::FromString(TEXT("MISSIONE")));
}

void AOWMissionMarker::SetMarkerLocation(const FVector& WorldLocation)
{
    SetActorLocation(WorldLocation);
}

void AOWMissionMarker::SetMarkerText(const FText& Text)
{
    if (MarkerText)
    {
        MarkerText->SetText(Text);
    }
}
