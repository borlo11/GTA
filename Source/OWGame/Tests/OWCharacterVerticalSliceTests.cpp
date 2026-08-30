#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../OWGameCharacter.h"
#include "../OWGameGameMode.h"
#include "../UI/OWGameHUD.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FOWCharacterVerticalSliceDefaultsTest,
    "OWGame.Character.VerticalSliceDefaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOWCharacterVerticalSliceDefaultsTest::RunTest(const FString& Parameters)
{
    const AOWGameCharacter* CharacterCDO = GetDefault<AOWGameCharacter>();
    const AOWGameGameMode* GameModeCDO = GetDefault<AOWGameGameMode>();

    TestNotNull(TEXT("Character CDO exists"), CharacterCDO);
    if (CharacterCDO)
    {
        TestTrue(TEXT("Walk speed is positive"), CharacterCDO->GetWalkSpeed() > 0.0f);
        TestTrue(TEXT("Sprint speed exceeds walk speed"), CharacterCDO->GetSprintSpeed() > CharacterCDO->GetWalkSpeed());
        TestTrue(TEXT("Interaction assist radius is positive"), CharacterCDO->GetInteractionAssistRadius() > 0.0f);
    }

    TestNotNull(TEXT("GameMode CDO exists"), GameModeCDO);
    if (GameModeCDO)
    {
        TestEqual(TEXT("M3 HUD class is configured"), GameModeCDO->HUDClass, AOWGameHUD::StaticClass());
    }

    return true;
}

#endif
