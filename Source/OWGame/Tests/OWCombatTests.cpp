#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../Combat/OWHealthComponent.h"
#include "../OWGameCharacter.h"
#include "../Population/OWPopulationNPC.h"
#include "../Police/OWPoliceOfficer.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FOWCombatDefaultsTest,
    "OWGame.Combat.Defaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOWCombatDefaultsTest::RunTest(const FString& Parameters)
{
    const UOWHealthComponent* HealthCDO = GetDefault<UOWHealthComponent>();
    const AOWGameCharacter* CharacterCDO = GetDefault<AOWGameCharacter>();
    const AOWPopulationNPC* PopulationCDO = GetDefault<AOWPopulationNPC>();
    const AOWPoliceOfficer* PoliceCDO = GetDefault<AOWPoliceOfficer>();

    TestNotNull(TEXT("Health component CDO exists"), HealthCDO);
    if (HealthCDO)
    {
        TestTrue(TEXT("Default max health is positive"), HealthCDO->GetMaxHealth() > 0.0f);
    }

    TestNotNull(TEXT("Character combat CDO exists"), CharacterCDO);
    if (CharacterCDO)
    {
        TestNotNull(TEXT("Player has health component"), CharacterCDO->GetHealthComponent());
        TestTrue(TEXT("Ranged damage is positive"), CharacterCDO->GetRangedDamage() > 0.0f);
        TestTrue(TEXT("Melee damage is positive"), CharacterCDO->GetMeleeDamage() > 0.0f);
        TestTrue(TEXT("Ranged range exceeds melee range"), CharacterCDO->GetRangedRange() > CharacterCDO->GetMeleeRange());
    }

    TestNotNull(TEXT("Population combat CDO exists"), PopulationCDO);
    if (PopulationCDO)
    {
        TestNotNull(TEXT("Population NPC has health component"), PopulationCDO->GetHealthComponent());
    }

    TestNotNull(TEXT("Police combat CDO exists"), PoliceCDO);
    if (PoliceCDO)
    {
        TestNotNull(TEXT("Police officer has health component"), PoliceCDO->GetHealthComponent());
    }

    return true;
}

#endif
