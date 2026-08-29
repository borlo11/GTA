#include "OWGameGameMode.h"
#include "OWGameCharacter.h"
#include "OWGamePlayerController.h"

AOWGameGameMode::AOWGameGameMode()
{
    DefaultPawnClass = AOWGameCharacter::StaticClass();
    PlayerControllerClass = AOWGamePlayerController::StaticClass();
}
