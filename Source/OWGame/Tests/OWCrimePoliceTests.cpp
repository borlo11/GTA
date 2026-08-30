#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../OWGamePlayerController.h"
#include "../Crime/OWWantedComponent.h"
#include "../Police/OWPoliceDirector.h"
#include "../Police/OWPoliceOfficer.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FOWCrimePoliceDefaultsTest,
    "OWGame.CrimePolice.Defaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOWCrimePoliceDefaultsTest::RunTest(const FString& Parameters)
{
    const AOWGamePlayerController* ControllerCDO = GetDefault<AOWGamePlayerController>();
    const AOWPoliceDirector* DirectorCDO = GetDefault<AOWPoliceDirector>();
    const AOWPoliceOfficer* OfficerCDO = GetDefault<AOWPoliceOfficer>();

    TestNotNull(TEXT("PlayerController CDO exists"), ControllerCDO);
    if (ControllerCDO)
    {
        const UOWWantedComponent* Wanted = ControllerCDO->GetWantedComponent();
        TestNotNull(TEXT("Wanted component exists on player controller"), Wanted);
        if (Wanted)
        {
            TestEqual(TEXT("Wanted starts at zero"), Wanted->GetWantedLevel(), 0);
            TestEqual(TEXT("Prototype max wanted level is three"), Wanted->GetMaxWantedLevel(), 3);
            TestTrue(TEXT("Wanted decay delay is positive"), Wanted->GetDecayDelaySeconds() > 0.0f);
        }
    }

    TestNotNull(TEXT("Police director CDO exists"), DirectorCDO);
    if (DirectorCDO)
    {
        TestTrue(
            TEXT("Police response grows with wanted level"),
            DirectorCDO->GetLevelOneResponseCount() <
                DirectorCDO->GetLevelTwoResponseCount() &&
            DirectorCDO->GetLevelTwoResponseCount() <
                DirectorCDO->GetLevelThreeResponseCount());
        TestTrue(
            TEXT("Police response timer is low frequency"),
            DirectorCDO->GetResponseUpdateInterval() >= 0.1f);
    }

    TestNotNull(TEXT("Police officer CDO exists"), OfficerCDO);
    if (OfficerCDO)
    {
        TestTrue(TEXT("Police chase speed is positive"), OfficerCDO->GetChaseSpeed() > 0.0f);
        TestTrue(TEXT("Police sight range exceeds chase stop distance"), OfficerCDO->GetSightRange() > 500.0f);
    }

    return true;
}

#endif
