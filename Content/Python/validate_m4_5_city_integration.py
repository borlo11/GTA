# validate_m4_5_city_integration.py
# Target-side validator for the curated OWGame City Sample integration map.
# This script becomes useful after the migration/preparation stage.

import unreal

TARGET_MAP = "/Game/Maps/OW_CitySample_Small"


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M4_5: " + message)


def main():
    require(
        unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP),
        "target integration map is missing: " + TARGET_MAP,
    )

    unreal.EditorLoadingAndSavingUtils.load_map(TARGET_MAP)

    world = unreal.EditorLevelLibrary.get_editor_world()
    require(world is not None, "could not obtain editor world")

    settings = world.get_world_settings()
    require(settings is not None, "world settings are missing")

    game_mode = settings.get_editor_property("default_game_mode")
    game_mode_text = str(game_mode) if game_mode else ""

    require(
        "OWGameGameMode" in game_mode_text,
        "target map does not override GameMode to OWGameGameMode; current={}".format(
            game_mode_text
        ),
    )

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = [actor for actor in actor_subsystem.get_all_level_actors() if actor]

    player_starts = [
        actor for actor in actors if isinstance(actor, unreal.PlayerStart)
    ]
    require(len(player_starts) >= 1, "target city map has no PlayerStart")

    unreal.log("VALIDATE_M4_5: MAP=" + TARGET_MAP)
    unreal.log("VALIDATE_M4_5: LOADED_ACTORS={}".format(len(actors)))
    unreal.log("VALIDATE_M4_5: PLAYER_STARTS={}".format(len(player_starts)))
    unreal.log("VALIDATE_M4_5: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
