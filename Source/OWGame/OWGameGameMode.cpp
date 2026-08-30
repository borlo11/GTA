#include "OWGameGameMode.h"
#include "OWGameCharacter.h"
#include "OWGamePlayerController.h"
#include "UI/OWGameHUD.h"
#include "Population/OWPopulationManager.h"
#include "Police/OWPoliceDirector.h"

#include "Engine/World.h"

AOWGameGameMode::AOWGameGameMode()
{
    DefaultPawnClass = AOWGameCharacter::StaticClass();
    PlayerControllerClass = AOWGamePlayerController::StaticClass();
    HUDClass = AOWGameHUD::StaticClass();
}


void AOWGameGameMode::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        FActorSpawnParameters SpawnParameters;
        SpawnParameters.SpawnCollisionHandlingOverride =
            ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

        World->SpawnActor<AOWPopulationManager>(
            AOWPopulationManager::StaticClass(),
            FVector::ZeroVector,
            FRotator::ZeroRotator,
            SpawnParameters);

        World->SpawnActor<AOWPoliceDirector>(
            AOWPoliceDirector::StaticClass(),
            FVector::ZeroVector,
            FRotator::ZeroRotator,
            SpawnParameters);
    }
}
