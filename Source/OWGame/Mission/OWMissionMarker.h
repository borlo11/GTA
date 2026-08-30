#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OWMissionMarker.generated.h"

class UStaticMeshComponent;
class UTextRenderComponent;

UCLASS()
class OWGAME_API AOWMissionMarker : public AActor
{
    GENERATED_BODY()

public:
    AOWMissionMarker();

    void SetMarkerLocation(const FVector& WorldLocation);
    void SetMarkerText(const FText& Text);

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Mission")
    TObjectPtr<UStaticMeshComponent> MarkerMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Mission")
    TObjectPtr<UTextRenderComponent> MarkerText;
};
