#include "OWMissionMarker.h"

#include "Components/PointLightComponent.h"
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
    MarkerMesh->SetRelativeScale3D(FVector(1.25f, 1.25f, 0.10f));

    if (UStaticMesh* Cylinder =
        LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
    {
        MarkerMesh->SetStaticMesh(Cylinder);
    }

    MarkerText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("MarkerText"));
    MarkerText->SetupAttachment(RootComponent);
    MarkerText->SetRelativeLocation(FVector(0.0f, 0.0f, 95.0f));
    MarkerText->SetHorizontalAlignment(EHTA_Center);
    MarkerText->SetWorldSize(32.0f);
    MarkerText->SetTextRenderColor(FColor(255, 210, 40));
    MarkerText->SetText(FText::FromString(TEXT("MISSIONE")));

    MarkerLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("MarkerLight"));
    MarkerLight->SetupAttachment(RootComponent);
    MarkerLight->SetRelativeLocation(FVector(0.0f, 0.0f, 55.0f));
    MarkerLight->SetLightColor(FLinearColor(1.0f, 0.72f, 0.12f, 1.0f));
    MarkerLight->SetIntensity(650.0f);
    MarkerLight->SetAttenuationRadius(360.0f);
    MarkerLight->SetCastShadows(false);
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
