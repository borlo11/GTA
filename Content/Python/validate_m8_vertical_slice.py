# validate_m8_vertical_slice.py
# Non-destructive M8 validation / World Partition inspection for OW_LightweightCity.

import unreal

MAP_PATH = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_CITY_"


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M8: " + message)


def main():
    require(
        unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH),
        "vertical slice map missing: " + MAP_PATH,
    )

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels.load_level(MAP_PATH), "could not load vertical slice map")

    actors = [
        actor
        for actor in unreal.get_editor_subsystem(
            unreal.EditorActorSubsystem
        ).get_all_level_actors()
        if actor
    ]

    labels = [actor.get_actor_label() for actor in actors]
    buildings = [
        label for label in labels if label.startswith(PREFIX + "Building_")
    ]

    require(PREFIX + "PlayerStart" in labels, "PlayerStart missing")
    require(PREFIX + "PrototypeVehicle" in labels, "prototype vehicle missing")
    require(len(buildings) >= 12, "expected the 12-building compact district")

    for class_path in (
        "/Script/OWGame.OWGameGameMode",
        "/Script/OWGame.OWVerticalSliceDirector",
        "/Script/OWGame.OWMissionStartActor",
        "/Script/OWGame.OWMissionComponent",
    ):
        require(
            unreal.load_class(None, class_path) is not None,
            "runtime class unavailable: " + class_path,
        )

    world = unreal.EditorLevelLibrary.get_editor_world()
    require(world is not None, "editor world unavailable")

    world_partition_state = "unavailable"
    try:
        world_partition = world.get_editor_property("world_partition")
        world_partition_state = "present" if world_partition else "not-present"
    except Exception:
        try:
            world_partition = world.get_world_partition()
            world_partition_state = "present" if world_partition else "not-present"
        except Exception:
            pass

    xs = [actor.get_actor_location().x for actor in actors if actor.get_actor_label().startswith(PREFIX)]
    ys = [actor.get_actor_location().y for actor in actors if actor.get_actor_label().startswith(PREFIX)]

    if xs and ys:
        unreal.log(
            "VALIDATE_M8: GENERATED_BOUNDS_X={:.0f}..{:.0f} Y={:.0f}..{:.0f}".format(
                min(xs), max(xs), min(ys), max(ys)
            )
        )

    unreal.log("VALIDATE_M8: WORLD_PARTITION={}".format(world_partition_state))
    unreal.log("VALIDATE_M8: BUILDINGS={}".format(len(buildings)))
    unreal.log("VALIDATE_M8: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
