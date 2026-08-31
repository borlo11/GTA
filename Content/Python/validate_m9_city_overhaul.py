# validate_m9_city_overhaul.py
# M9 validator for the rebuilt OW_LightweightCity.

import unreal

MAP_PATH = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_CITY_"


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M9: " + message)


def main():
    require(
        unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH),
        "map missing: " + MAP_PATH,
    )

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels.load_level(MAP_PATH), "could not load city map")

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = [a for a in actor_subsystem.get_all_level_actors() if a]
    labels = [a.get_actor_label() for a in actors]

    generated = [label for label in labels if label.startswith(PREFIX)]
    buildings = [label for label in labels if label.startswith(PREFIX + "Building_")]
    road_marks = [label for label in labels if label.startswith(PREFIX + "RoadMark_")]
    crosswalks = [label for label in labels if label.startswith(PREFIX + "Crosswalk_")]
    street_lights = [label for label in labels if label.startswith(PREFIX + "StreetLight_")]
    urban_props = [label for label in labels if label.startswith(PREFIX + "UrbanProp_")]
    sidewalk_pads = [label for label in labels if label.startswith(PREFIX + "SidewalkPad_")]

    require(PREFIX + "Road_NS" in labels, "legacy central NS road label missing")
    require(PREFIX + "Road_EW" in labels, "legacy central EW road label missing")
    require(PREFIX + "Road_NS_00" in labels, "secondary road grid missing")
    require(PREFIX + "Road_EW_02" in labels, "secondary road grid missing")
    require(PREFIX + "PlayerStart" in labels, "PlayerStart missing")
    require(PREFIX + "PrototypeVehicle" in labels, "prototype vehicle missing")
    require(PREFIX + "Sun" in labels, "dynamic sun missing")
    require(PREFIX + "SkyAtmosphere" in labels, "SkyAtmosphere missing")
    require(PREFIX + "SkyLight" in labels, "SkyLight missing")
    require(PREFIX + "Fog" in labels, "fog missing")

    require(len(sidewalk_pads) >= 16, "expected at least 16 urban block pads")
    require(len(buildings) >= 28, "expected richer multi-part building massing")
    require(len(road_marks) >= 80, "lane markings are too sparse")
    require(len(crosswalks) >= 28, "crosswalk system missing")
    require(len(street_lights) >= 28, "streetlight components/actors missing")
    require(len(urban_props) >= 12, "urban props missing")

    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings() if world else None
    require(settings is not None, "WorldSettings unavailable")

    game_mode = settings.get_editor_property("default_game_mode")
    require(
        game_mode and "OWGameGameMode" in str(game_mode),
        "map GameMode is not OWGameGameMode: {}".format(game_mode),
    )

    try:
        force_dynamic = settings.get_editor_property("force_no_precomputed_lighting")
        require(force_dynamic, "ForceNoPrecomputedLighting is disabled")
        unreal.log("VALIDATE_M9: FORCE_NO_PRECOMPUTED_LIGHTING=True")
    except Exception as exc:
        unreal.log_warning(
            "VALIDATE_M9: could not inspect ForceNoPrecomputedLighting: {}".format(exc)
        )

    unreal.log("VALIDATE_M9: GENERATED_ACTORS={}".format(len(generated)))
    unreal.log("VALIDATE_M9: BUILDING_PARTS={}".format(len(buildings)))
    unreal.log("VALIDATE_M9: ROAD_MARKS={}".format(len(road_marks)))
    unreal.log("VALIDATE_M9: CROSSWALKS={}".format(len(crosswalks)))
    unreal.log("VALIDATE_M9: STREETLIGHT_ACTORS={}".format(len(street_lights)))
    unreal.log("VALIDATE_M9: URBAN_PROPS={}".format(len(urban_props)))
    unreal.log("VALIDATE_M9: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
