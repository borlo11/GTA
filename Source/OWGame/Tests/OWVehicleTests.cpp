#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../Vehicle/OWPrototypeVehicle.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FOWVehicleDefaultsTest,
    "OWGame.Vehicle.PrototypeDefaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOWVehicleDefaultsTest::RunTest(const FString& Parameters)
{
    const AOWPrototypeVehicle* VehicleCDO = GetDefault<AOWPrototypeVehicle>();

    TestNotNull(TEXT("Vehicle CDO exists"), VehicleCDO);
    if (VehicleCDO)
    {
        TestNotNull(TEXT("Vehicle movement component exists"), VehicleCDO->GetMovementComponent());
        TestTrue(TEXT("Vehicle max speed is positive"), VehicleCDO->GetConfiguredMaxSpeed() > 0.0f);
        TestFalse(TEXT("Vehicle starts unoccupied"), VehicleCDO->IsOccupied());
    }

    return true;
}

#endif
