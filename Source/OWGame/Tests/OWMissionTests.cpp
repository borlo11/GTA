#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../OWGamePlayerController.h"
#include "../Mission/OWMissionComponent.h"
#include "../Mission/OWMissionSaveGame.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FOWMissionDefaultsTest,
    "OWGame.Mission.Defaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOWMissionDefaultsTest::RunTest(const FString& Parameters)
{
    const AOWGamePlayerController* ControllerCDO =
        GetDefault<AOWGamePlayerController>();

    TestNotNull(TEXT("PlayerController CDO exists"), ControllerCDO);
    if (ControllerCDO)
    {
        const UOWMissionComponent* Mission =
            ControllerCDO->GetMissionComponent();

        TestNotNull(TEXT("Mission component exists on player controller"), Mission);

        if (Mission)
        {
            TestEqual(
                TEXT("Mission starts inactive"),
                Mission->GetMissionState(),
                EOWMissionState::Inactive);

            TestEqual(
                TEXT("Prototype mission id is stable"),
                Mission->GetMissionId(),
                FName(TEXT("HotRun")));

            TestTrue(
                TEXT("Objective update cadence is not per-frame"),
                Mission->GetObjectiveUpdateInterval() >= 0.05f);
        }
    }

    const UOWMissionSaveGame* SaveCDO = GetDefault<UOWMissionSaveGame>();
    TestNotNull(TEXT("Mission SaveGame class exists"), SaveCDO);

    return true;
}

#endif
