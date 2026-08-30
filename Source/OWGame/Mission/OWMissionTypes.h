#pragma once

#include "CoreMinimal.h"
#include "OWMissionTypes.generated.h"

UENUM(BlueprintType)
enum class EOWMissionState : uint8
{
    Inactive,
    Active,
    Completed,
    Failed
};

UENUM(BlueprintType)
enum class EOWMissionObjectiveType : uint8
{
    ReachVehicle,
    EnterVehicle,
    ReachLocation,
    LoseWanted
};

USTRUCT(BlueprintType)
struct FOWMissionObjectiveSpec
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Mission")
    EOWMissionObjectiveType Type = EOWMissionObjectiveType::ReachLocation;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Mission")
    FText Description = FText::GetEmpty();

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Mission")
    FVector TargetLocation = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Mission", meta=(ClampMin="10.0", ClampMax="5000.0"))
    float AcceptanceRadius = 250.0f;
};
