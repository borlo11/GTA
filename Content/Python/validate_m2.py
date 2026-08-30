# validate_m2.py
# Headless validation for the OWGame Milestone 2 vehicle prototype.

import unreal

INPUT_DIR = "/Game/Input"
MAP_PATH = "/Game/Maps/M1_TestMap"
VEHICLE_LABEL = "OW_M2_Vehicle"

log = unreal.log


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M2: " + message)


def load_required_asset(name, expected_class):
    path = "{}/{}".format(INPUT_DIR, name)
    require(unreal.EditorAssetLibrary.does_asset_exist(path), "missing {}".format(path))
    asset = unreal.EditorAssetLibrary.load_asset(path)
    require(asset is not None, "could not load {}".format(path))
    require(isinstance(asset, expected_class), "{} has wrong class".format(path))
    return asset


def validate_input():
    throttle = load_required_asset("IA_VehicleThrottle", unreal.InputAction)
    steer = load_required_asset("IA_VehicleSteer", unreal.InputAction)
    brake = load_required_asset("IA_VehicleBrake", unreal.InputAction)
    exit_action = load_required_asset("IA_VehicleExit", unreal.InputAction)
    load_required_asset("IA_Look", unreal.InputAction)
    imc = load_required_asset("IMC_Vehicle", unreal.InputMappingContext)

    require(
        throttle.get_editor_property("value_type") == unreal.InputActionValueType.AXIS1D,
        "IA_VehicleThrottle must be Axis1D",
    )
    require(
        steer.get_editor_property("value_type") == unreal.InputActionValueType.AXIS1D,
        "IA_VehicleSteer must be Axis1D",
    )
    require(
        brake.get_editor_property("value_type") == unreal.InputActionValueType.BOOLEAN,
        "IA_VehicleBrake must be Boolean",
    )
    require(
        exit_action.get_editor_property("value_type") == unreal.InputActionValueType.BOOLEAN,
        "IA_VehicleExit must be Boolean",
    )

    actual = set()
    for mapping in list(imc.get_editor_property("mappings")):
        action = mapping.get_editor_property("action")
        key = mapping.get_editor_property("key")
        if action is not None:
            actual.add(
                (
                    action.get_name(),
                    str(key.get_editor_property("key_name")),
                )
            )

    expected = {
        ("IA_VehicleThrottle", "W"),
        ("IA_VehicleThrottle", "S"),
        ("IA_VehicleSteer", "A"),
        ("IA_VehicleSteer", "D"),
        ("IA_VehicleBrake", "SpaceBar"),
        ("IA_VehicleExit", "E"),
    }

    missing = expected - actual
    require(not missing, "missing vehicle mappings: {}".format(sorted(missing)))
    log("VALIDATE_M2: input assets and mappings OK")


def validate_map():
    require(
        unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH),
        "missing map {}".format(MAP_PATH),
    )

    unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    vehicle = None
    for actor in actor_subsystem.get_all_level_actors():
        if actor and actor.get_actor_label() == VEHICLE_LABEL:
            vehicle = actor
            break

    require(vehicle is not None, "missing actor {}".format(VEHICLE_LABEL))

    vehicle_class = unreal.load_class(None, "/Script/OWGame.OWPrototypeVehicle")
    require(vehicle_class is not None, "OWPrototypeVehicle class is not loadable")
    require(
        vehicle.get_class() == vehicle_class,
        "{} has wrong class {}".format(VEHICLE_LABEL, vehicle.get_class().get_name()),
    )

    try:
        require(
            vehicle.get_editor_property("is_spatially_loaded") is False,
            "{} must be always loaded in World Partition".format(VEHICLE_LABEL),
        )
    except Exception:
        pass

    log("VALIDATE_M2: map and prototype vehicle OK")


def main():
    validate_input()
    validate_map()
    log("VALIDATE_M2: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
