#include "OWGameGameMode.h"
#include "OWGameCharacter.h"
#include "OWGamePlayerController.h"
#include "UI/OWGameHUD.h"

AOWGameGameMode::AOWGameGameMode()
{
    DefaultPawnClass = AOWGameCharacter::StaticClass();
    PlayerControllerClass = AOWGamePlayerController::StaticClass();
    HUDClass = AOWGameHUD::StaticClass();
}
