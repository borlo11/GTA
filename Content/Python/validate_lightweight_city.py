# validate_lightweight_city.py
# M4.5 validator for /Game/Maps/OW_LightweightCity.

import unreal

MAP_PATH = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_CITY_"


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M4_5: " + message)


def main():
    require(
        unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH),
        "map missing: " + MAP_PATH,
    )

    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(subsystem.load_level(MAP_PATH), "could not load target map")

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = [a for a in actor_subsystem.get_all_level_actors() if a]

    labels = [a.get_actor_label() for a in actors]
    generated = [label for label in labels if label.startswith(PREFIX)]
    buildings = [label for label in labels if label.startswith(PREFIX + "Building_")]

    require(PREFIX + "Road_NS" in labels, "north/south road missing")
    require(PREFIX + "Road_EW" in labels, "east/west road missing")
    require(PREFIX + "PlayerStart" in labels, "PlayerStart missing")
    require(PREFIX + "PrototypeVehicle" in labels, "prototype vehicle missing")
    require(len(buildings) >= 8, "expected at least 8 generated buildings")

    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings() if world else None
    require(settings is not None, "WorldSettings unavailable")

    game_mode = settings.get_editor_property("default_game_mode")
    require(
        game_mode and "OWGameGameMode" in str(game_mode),
        "map GameMode is not OWGameGameMode: {}".format(game_mode),
    )

    unreal.log("VALIDATE_M4_5: GENERATED_ACTORS={}".format(len(generated)))
    unreal.log("VALIDATE_M4_5: BUILDINGS={}".format(len(buildings)))
    unreal.log("VALIDATE_M4_5: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
