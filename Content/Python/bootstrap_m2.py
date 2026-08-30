# bootstrap_m2.py
# Milestone 2 editor bootstrap for OWGame (Unreal Engine 5.8).
# Idempotent. Safe to run multiple times. Never deletes user content.

import unreal

INPUT_DIR = "/Game/Input"
MAP_PATH = "/Game/Maps/M1_TestMap"
VEHICLE_LABEL = "OW_M2_Vehicle"
VEHICLE_LOCATION = unreal.Vector(550.0, -50.0, 140.0)
VEHICLE_ROTATION = unreal.Rotator(0.0, 0.0, 0.0)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
log = unreal.log


def make_factory(asset_class):
    dedicated = getattr(unreal, asset_class.__name__ + "Factory", None)
    if dedicated is not None:
        return dedicated()
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", asset_class)
    return factory


def ensure_asset(name, asset_class):
    object_path = "{}/{}".format(INPUT_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(object_path):
        asset = unreal.EditorAssetLibrary.load_asset(object_path)
        if asset is None or not isinstance(asset, asset_class):
            raise RuntimeError(
                "Asset {} exists but is not a {}".format(object_path, asset_class.__name__)
            )
        return asset

    asset = asset_tools.create_asset(name, INPUT_DIR, asset_class, make_factory(asset_class))
    if asset is None:
        raise RuntimeError("Failed to create {}".format(object_path))
    log("bootstrap_m2: created {}".format(object_path))
    return asset


def ensure_input_action(name, value_type):
    action = ensure_asset(name, unreal.InputAction)
    if action.get_editor_property("value_type") != value_type:
        action.set_editor_property("value_type", value_type)
        unreal.EditorAssetLibrary.save_loaded_asset(action)
    return action


def make_modifier(imc, modifier_class):
    return unreal.new_object(modifier_class, outer=imc)


def ensure_mapping(imc, action, key_name, modifier_classes):
    key = unreal.Key()
    key.set_editor_property("key_name", key_name)

    mappings = list(imc.get_editor_property("mappings"))
    for mapping in mappings:
        if (
            mapping.get_editor_property("action") == action
            and str(mapping.get_editor_property("key").get_editor_property("key_name")) == key_name
        ):
            return False

    mapping = unreal.EnhancedActionKeyMapping()
    mapping.set_editor_property("action", action)
    mapping.set_editor_property("key", key)
    mapping.set_editor_property(
        "modifiers",
        [make_modifier(imc, modifier_class) for modifier_class in modifier_classes],
    )
    mappings.append(mapping)
    imc.set_editor_property("mappings", mappings)
    log("bootstrap_m2: mapped {} -> {}".format(key_name, action.get_name()))
    return True


def setup_vehicle_input():
    if not unreal.EditorAssetLibrary.does_directory_exist(INPUT_DIR):
        unreal.EditorAssetLibrary.make_directory(INPUT_DIR)

    throttle = ensure_input_action("IA_VehicleThrottle", unreal.InputActionValueType.AXIS1D)
    steer = ensure_input_action("IA_VehicleSteer", unreal.InputActionValueType.AXIS1D)
    brake = ensure_input_action("IA_VehicleBrake", unreal.InputActionValueType.BOOLEAN)
    exit_action = ensure_input_action("IA_VehicleExit", unreal.InputActionValueType.BOOLEAN)

    look = unreal.EditorAssetLibrary.load_asset("{}/IA_Look".format(INPUT_DIR))
    if look is None:
        raise RuntimeError("Missing /Game/Input/IA_Look. Run bootstrap_m1.py first.")

    imc = ensure_asset("IMC_Vehicle", unreal.InputMappingContext)

    changed = False
    changed |= ensure_mapping(imc, throttle, "W", [])
    changed |= ensure_mapping(imc, throttle, "S", [unreal.InputModifierNegate])
    changed |= ensure_mapping(imc, steer, "A", [unreal.InputModifierNegate])
    changed |= ensure_mapping(imc, steer, "D", [])
    changed |= ensure_mapping(imc, look, "MouseX", [])
    changed |= ensure_mapping(imc, look, "MouseY", [unreal.InputModifierNegate])
    changed |= ensure_mapping(imc, brake, "SpaceBar", [])
    changed |= ensure_mapping(imc, exit_action, "E", [])

    if changed:
        unreal.EditorAssetLibrary.save_loaded_asset(imc)
    log("bootstrap_m2: vehicle input OK")


def find_actor_by_label(actor_subsystem, label):
    for actor in actor_subsystem.get_all_level_actors():
        if actor and actor.get_actor_label() == label:
            return actor
    return None


def mark_always_loaded(actor):
    try:
        actor.set_editor_property("is_spatially_loaded", False)
    except Exception:
        pass


def setup_vehicle_actor():
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        raise RuntimeError("Required map {} does not exist".format(MAP_PATH))

    unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    vehicle = find_actor_by_label(actor_subsystem, VEHICLE_LABEL)
    if vehicle is not None:
        log("bootstrap_m2: vehicle already present")
        return

    vehicle_class = unreal.load_class(None, "/Script/OWGame.OWPrototypeVehicle")
    if vehicle_class is None:
        raise RuntimeError(
            "Could not load /Script/OWGame.OWPrototypeVehicle; build OWGameEditor first."
        )

    vehicle = actor_subsystem.spawn_actor_from_class(
        vehicle_class, VEHICLE_LOCATION, VEHICLE_ROTATION
    )
    if vehicle is None:
        raise RuntimeError("Failed to spawn OWPrototypeVehicle")

    vehicle.set_actor_label(VEHICLE_LABEL)
    mark_always_loaded(vehicle)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("bootstrap_m2: spawned and saved {}".format(VEHICLE_LABEL))


def main():
    setup_vehicle_input()
    setup_vehicle_actor()
    log("bootstrap_m2: DONE")


if __name__ == "__main__":
    main()
