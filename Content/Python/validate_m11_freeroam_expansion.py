# validate_m11_freeroam_expansion.py
# Structural validator for M11 Phase B free-roam expansion.

import unreal

TARGET_MAP = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_M11_"


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M11: " + message)


def actor_subsystem():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def level_subsystem():
    return unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def main():
    require(
        unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP),
        "target map missing",
    )
    require(level_subsystem().load_level(TARGET_MAP), "could not load target map")

    actors = [a for a in actor_subsystem().get_all_level_actors() if a]
    labels = [a.get_actor_label() for a in actors]
    m11 = [a for a in actors if a.get_actor_label().startswith(PREFIX)]

    roads = [a for a in m11 if "_Road_" in a.get_actor_label()]
    pads = [a for a in m11 if "_Pad_" in a.get_actor_label()]
    hero_prefabs = [
        a for a in m11
        if hasattr(unreal, "LevelInstance") and isinstance(a, unreal.LevelInstance)
    ]
    background_buildings = [
        a for a in m11 if "_Background_" in a.get_actor_label()
    ]
    lane_graphics = [
        a for a in m11
        if "Lane_" in a.get_actor_label() or "Crosswalk_" in a.get_actor_label()
    ]
    parking_marks = [
        a for a in m11 if "ParkingMark_" in a.get_actor_label()
    ]
    streetlights = [
        a for a in m11 if "StreetLight_" in a.get_actor_label()
    ]

    require(len(m11) >= 250, "expected substantial additive world expansion")
    require(len(roads) >= 14, "expected at least fourteen expanded roads")
    require(len(pads) >= 28, "expected outer district block pads")
    require(len(hero_prefabs) >= 4, "expected four authored outer hero prefabs")
    require(len(background_buildings) >= 15, "expected lightweight district buildings")
    require(len(lane_graphics) >= 150, "expected expanded road graphics")
    require(len(parking_marks) >= 18, "expected visible parking detail")
    require(len(streetlights) >= 40, "expected sparse outer street-light dressing")

    require(
        "OW_M10_SportsCar" in labels,
        "M10 SportsCar was not preserved",
    )
    require(
        "OW_M10_SportsCarInteraction" in labels,
        "M10 SportsCar interaction proxy was not preserved",
    )

    player_starts = [a for a in actors if isinstance(a, unreal.PlayerStart)]
    require(len(player_starts) == 1, "expected exactly one deterministic PlayerStart")

    districts = ("Residential", "Modern", "Industrial", "ParkEdge")
    for district in districts:
        require(
            any(district in label for label in labels if label.startswith(PREFIX)),
            "district missing: {}".format(district),
        )

    unreal.log("VALIDATE_M11: expansion_actors={}".format(len(m11)))
    unreal.log("VALIDATE_M11: roads={}".format(len(roads)))
    unreal.log("VALIDATE_M11: district_pads={}".format(len(pads)))
    unreal.log("VALIDATE_M11: hero_prefabs={}".format(len(hero_prefabs)))
    unreal.log("VALIDATE_M11: background_buildings={}".format(len(background_buildings)))
    unreal.log("VALIDATE_M11: road_graphics={}".format(len(lane_graphics)))
    unreal.log("VALIDATE_M11: parking_marks={}".format(len(parking_marks)))
    unreal.log("VALIDATE_M11: streetlight_parts={}".format(len(streetlights)))
    unreal.log("VALIDATE_M11: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
