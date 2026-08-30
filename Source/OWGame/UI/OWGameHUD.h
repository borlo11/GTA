#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "OWGameHUD.generated.h"

UCLASS()
class OWGAME_API AOWGameHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;
};
