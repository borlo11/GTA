# validate_m9_city_overhaul.py
# M9 validator for the authored-UNIBLOCKS prefab city pass.

import unreal

MAP_PATH = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_CITY_"


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M9: " + message)


def main():
    require(unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH), "map missing")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels.load_level(MAP_PATH), "could not load map")

    actors = [
        actor
        for actor in unreal.get_editor_subsystem(
            unreal.EditorActorSubsystem
        ).get_all_level_actors()
        if actor
    ]

    labels = [actor.get_actor_label() for actor in actors]

    buildings = [x for x in labels if x.startswith(PREFIX + "Building_")]
    road_marks = [x for x in labels if x.startswith(PREFIX + "RoadMark_")]
    crosswalks = [x for x in labels if x.startswith(PREFIX + "Crosswalk_")]
    lights = [x for x in labels if x.startswith(PREFIX + "StreetLight_")]
    pads = [x for x in labels if x.startswith(PREFIX + "SidewalkPad_")]

    require(PREFIX + "Road_NS" in labels, "central NS road missing")
    require(PREFIX + "Road_EW" in labels, "central EW road missing")
    require(PREFIX + "Road_NS_00" in labels, "road grid missing")
    require(PREFIX + "Road_EW_02" in labels, "road grid missing")
    require(PREFIX + "PlayerStart" in labels, "PlayerStart missing")
    require(PREFIX + "PrototypeVehicle" in labels, "vehicle missing")
    require(PREFIX + "Sun" in labels, "sun missing")
    require(PREFIX + "SkyAtmosphere" in labels, "atmosphere missing")
    require(PREFIX + "SkyLight" in labels, "skylight missing")
    require(PREFIX + "Fog" in labels, "fog missing")

    require(len(pads) >= 16, "urban block pads missing")
    require(len(buildings) >= 14, "expected hero prefabs plus background building masses")
    require(len(road_marks) >= 60, "lane markings too sparse")
    require(len(crosswalks) == 24, "expected four six-stripe crosswalks")
    require(len(lights) >= 20, "street-light geometry missing")

    prefab_instances = []
    if hasattr(unreal, "LevelInstance"):
        prefab_instances = [
            actor
            for actor in actors
            if isinstance(actor, unreal.LevelInstance)
            and actor.get_actor_label().startswith(PREFIX + "Building_")
        ]

    require(
        len(prefab_instances) >= 4,
        "expected four authored UNIBLOCKS hero LevelInstances: {}".format(
            len(prefab_instances)
        ),
    )

    world_assets = set()
    for instance in prefab_instances:
        try:
            world_asset = instance.get_world_asset()
            if world_asset:
                world_assets.add(world_asset.get_path_name())
        except Exception:
            pass

    require(
        len(world_assets) >= 2,
        "prefab variety too low: {}".format(sorted(world_assets)),
    )

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    settings = world.get_world_settings() if world else None
    require(settings is not None, "WorldSettings unavailable")

    game_mode = settings.get_editor_property("default_game_mode")
    require(
        game_mode and "OWGameGameMode" in str(game_mode),
        "wrong GameMode: {}".format(game_mode),
    )

    background_buildings = [
        label
        for label in labels
        if label.startswith(PREFIX + "Building_") and label.endswith("_Background")
    ]

    require(
        len(background_buildings) >= 8,
        "expected eight lightweight background building masses: {}".format(
            len(background_buildings)
        ),
    )

    unreal.log("VALIDATE_M9: HERO_PREFABS={}".format(len(prefab_instances)))
    unreal.log("VALIDATE_M9: PREFAB_VARIANTS={}".format(len(world_assets)))
    unreal.log("VALIDATE_M9: BACKGROUND_MASSES={}".format(len(background_buildings)))
    unreal.log("VALIDATE_M9: ROAD_MARKS={}".format(len(road_marks)))
    unreal.log("VALIDATE_M9: CROSSWALKS={}".format(len(crosswalks)))
    unreal.log("VALIDATE_M9: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
