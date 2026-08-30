#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "OWMissionTypes.h"
#include "OWMissionSaveGame.generated.h"

UCLASS()
class OWGAME_API UOWMissionSaveGame : public USaveGame
{
    GENERATED_BODY()

public:
    UPROPERTY(SaveGame)
    FName MissionId = NAME_None;

    UPROPERTY(SaveGame)
    EOWMissionState MissionState = EOWMissionState::Inactive;

    UPROPERTY(SaveGame)
    int32 ObjectiveIndex = INDEX_NONE;
};
