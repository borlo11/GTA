#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../OWGameCharacter.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FOWCharacterDefaultsTest,
    "OWGame.Foundation.CharacterDefaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOWCharacterDefaultsTest::RunTest(const FString& Parameters)
{
    const AOWGameCharacter* CharacterCDO = GetDefault<AOWGameCharacter>();

    TestNotNull(TEXT("Character CDO exists"), CharacterCDO);
    if (CharacterCDO)
    {
        TestTrue(TEXT("Interaction range is positive"), CharacterCDO->GetInteractionRange() > 0.0f);
    }

    return true;
}

#endif
