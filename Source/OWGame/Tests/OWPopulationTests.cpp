#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../Population/OWPopulationManager.h"
#include "../Population/OWPopulationNPC.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FOWPopulationDefaultsTest,
    "OWGame.Population.Defaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOWPopulationDefaultsTest::RunTest(const FString& Parameters)
{
    const AOWPopulationNPC* NPCCDO = GetDefault<AOWPopulationNPC>();
    const AOWPopulationManager* ManagerCDO = GetDefault<AOWPopulationManager>();

    TestNotNull(TEXT("Population NPC CDO exists"), NPCCDO);
    if (NPCCDO)
    {
        TestNotNull(TEXT("Population NPC movement component exists"), NPCCDO->GetMovementComponent());
        TestTrue(TEXT("Population NPC walk speed is positive"), NPCCDO->GetConfiguredWalkSpeed() > 0.0f);
        TestTrue(TEXT("Population NPC wander radius is positive"), NPCCDO->GetWanderRadius() > 0.0f);
        TestTrue(
            TEXT("Simulation intervals become cheaper with distance"),
            NPCCDO->GetHighSimulationInterval() < NPCCDO->GetMediumSimulationInterval() &&
            NPCCDO->GetMediumSimulationInterval() < NPCCDO->GetLowSimulationInterval());
    }

    TestNotNull(TEXT("Population manager CDO exists"), ManagerCDO);
    if (ManagerCDO)
    {
        TestTrue(TEXT("Target population is positive"), ManagerCDO->GetTargetPopulation() > 0);
        TestTrue(
            TEXT("Population LOD distances are ordered"),
            ManagerCDO->GetHighDetailDistance() < ManagerCDO->GetMediumDetailDistance() &&
            ManagerCDO->GetMediumDetailDistance() < ManagerCDO->GetLowDetailDistance() &&
            ManagerCDO->GetLowDetailDistance() < ManagerCDO->GetDespawnDistance());
    }

    return true;
}

#endif
