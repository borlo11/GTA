#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../OWGamePlayerController.h"
#include "../Mission/OWMissionComponent.h"
#include "../Mission/OWMissionStartActor.h"
#include "../VerticalSlice/OWVerticalSliceDirector.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FOWVerticalSliceDefaultsTest,
    "OWGame.VerticalSlice.Defaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOWVerticalSliceDefaultsTest::RunTest(const FString& Parameters)
{
    const AOWVerticalSliceDirector* DirectorCDO =
        GetDefault<AOWVerticalSliceDirector>();
    const AOWMissionStartActor* StartCDO =
        GetDefault<AOWMissionStartActor>();
    const AOWGamePlayerController* ControllerCDO =
        GetDefault<AOWGamePlayerController>();

    TestNotNull(TEXT("Vertical slice director CDO exists"), DirectorCDO);
    if (DirectorCDO)
    {
        TestTrue(
            TEXT("Mission start creation is deferred, not per-frame"),
            DirectorCDO->GetStartActorSpawnDelay() >= 0.05f);
    }

    TestNotNull(TEXT("Mission start actor CDO exists"), StartCDO);
    if (StartCDO)
    {
        TestTrue(
            TEXT("Mission start interaction radius is positive"),
            StartCDO->GetInteractionRadius() > 0.0f);
    }

    TestNotNull(TEXT("PlayerController CDO exists"), ControllerCDO);
    if (ControllerCDO)
    {
        TestFalse(
            TEXT("Performance overlay starts hidden"),
            ControllerCDO->IsPerformanceOverlayVisible());

        const UOWMissionComponent* Mission =
            ControllerCDO->GetMissionComponent();

        TestNotNull(TEXT("M8 reuses persistent mission component"), Mission);
        if (Mission)
        {
            TestTrue(
                TEXT("Completion banner has a positive presentation duration"),
                Mission->GetCompletionBannerSeconds() > 0.0f);
        }
    }

    return true;
}

#endif
