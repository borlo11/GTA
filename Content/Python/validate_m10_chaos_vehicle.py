# validate_m10_chaos_vehicle.py
# Non-destructive validation for M10's migrated Chaos SportsCar integration.

import unreal

TARGET_MAP = "/Game/Maps/OW_LightweightCity"

SPORTS_CAR_BP = (
    "/Game/VehicleTemplate/Blueprints/SportsCar/BP_VehicleAdvSportsCar"
)
SPORTS_CAR_MESH = "/Game/Vehicles/SportsCar/SKM_SportsCar"
SPORTS_CAR_PHYSICS = "/Game/Vehicles/SportsCar/PA_SportsCar"

VEHICLE_LABEL = "OW_M10_SportsCar"
PROXY_LABEL = "OW_M10_SportsCarInteraction"


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M10: " + message)


def main():
    require(
        unreal.EditorAssetLibrary.does_asset_exist(SPORTS_CAR_BP),
        "SportsCar Blueprint missing",
    )
    require(
        unreal.EditorAssetLibrary.does_asset_exist(SPORTS_CAR_MESH),
        "SportsCar skeletal mesh missing",
    )
    require(
        unreal.EditorAssetLibrary.does_asset_exist(SPORTS_CAR_PHYSICS),
        "SportsCar physics asset missing",
    )
    require(
        unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP),
        "OW_LightweightCity missing",
    )

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels.load_level(TARGET_MAP), "could not load city map")

    actors = [
        actor
        for actor in unreal.get_editor_subsystem(
            unreal.EditorActorSubsystem
        ).get_all_level_actors()
        if actor
    ]

    by_label = {actor.get_actor_label(): actor for actor in actors}

    require(
        "OW_CITY_PrototypeVehicle" not in by_label,
        "old prototype vehicle still exists in M10 city",
    )
    require(VEHICLE_LABEL in by_label, "M10 SportsCar actor missing")
    require(PROXY_LABEL in by_label, "M10 interaction proxy missing")

    vehicle = by_label[VEHICLE_LABEL]
    proxy = by_label[PROXY_LABEL]

    tags = {str(tag) for tag in vehicle.get_editor_property("tags")}
    require("OWMissionVehicle" in tags, "SportsCar mission tag missing")
    require(
        "OWNoPopulationSpawn" in tags,
        "SportsCar population exclusion tag missing",
    )

    movement_class = getattr(
        unreal,
        "ChaosWheeledVehicleMovementComponent",
        None,
    )
    require(
        movement_class is not None,
        "ChaosWheeledVehicleMovementComponent Python class unavailable",
    )

    movement = vehicle.get_component_by_class(movement_class)
    require(movement is not None, "SportsCar Chaos movement component missing")

    try:
        linked_vehicle = proxy.get_vehicle_pawn()
    except Exception as exc:
        raise RuntimeError(
            "VALIDATE_M10: interaction proxy getter failed: {}".format(exc)
        )

    require(
        linked_vehicle == vehicle,
        "interaction proxy is not linked to the SportsCar",
    )

    unreal.log(
        "VALIDATE_M10: VEHICLE_CLASS={}".format(
            vehicle.get_class().get_path_name()
        )
    )
    unreal.log(
        "VALIDATE_M10: MOVEMENT_CLASS={}".format(
            movement.get_class().get_path_name()
        )
    )
    unreal.log("VALIDATE_M10: MISSION_TAG=OWMissionVehicle")
    unreal.log("VALIDATE_M10: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
