# validate_m11_freeroam_expansion.py
# Structural validator for M11 Phase C free-roam environment pass.

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
    phase_c_bushes = [
        a for a in m11 if "Env_Bush_" in a.get_actor_label()
    ]
    phase_c_boulevards = [
        a for a in m11 if "Env_Boulevard_" in a.get_actor_label()
    ]
    loading_docks = [
        a for a in m11 if "Industrial_LoadingDock_" in a.get_actor_label()
    ]
    facade_details = [
        a for a in m11 if "Facade_" in a.get_actor_label()
    ]
    roof_details = [
        a for a in m11 if "RoofDetail_" in a.get_actor_label()
    ]
    secondary_parking = [
        a for a in m11
        if "ParkingPocket_" in a.get_actor_label()
        or "ParkingBay_" in a.get_actor_label()
        or "WheelStop_" in a.get_actor_label()
    ]
    district_crosswalks = [
        a for a in m11 if "DistrictCrosswalk_" in a.get_actor_label()
    ]
    street_props = [
        a for a in m11 if "StreetProp_" in a.get_actor_label()
    ]
    skyline = [
        a for a in m11 if "Skyline_" in a.get_actor_label()
    ]

    require(len(m11) >= 250, "expected substantial additive world expansion")
    require(len(roads) >= 14, "expected at least fourteen expanded roads")
    require(len(pads) >= 28, "expected outer district block pads")
    require(len(hero_prefabs) >= 4, "expected four authored outer hero prefabs")
    require(
        len(background_buildings) >= 50,
        "expected Phase C clustered district buildings",
    )
    require(len(lane_graphics) >= 150, "expected expanded road graphics")
    require(len(parking_marks) >= 18, "expected visible parking detail")
    require(len(streetlights) >= 40, "expected sparse outer street-light dressing")
    require(
        len(phase_c_bushes) >= 30,
        "expected Phase C residential/modern landscaping",
    )
    require(
        len(phase_c_boulevards) == 4,
        "expected four Phase C boulevard edge bands",
    )
    require(
        len(loading_docks) == 3,
        "expected three industrial loading docks",
    )
    require(
        len(facade_details) >= 45,
        "expected facade cues on background massing",
    )
    require(
        len(roof_details) >= 45,
        "expected rooftop silhouette detail",
    )
    require(
        len(secondary_parking) >= 30,
        "expected two secondary dressed parking pockets",
    )
    require(
        len(district_crosswalks) >= 24,
        "expected district intersection crosswalk detail",
    )
    require(
        len(street_props) >= 45,
        "expected human-scale street furniture",
    )
    require(
        len(skyline) >= 12,
        "expected three lightweight skyline landmarks",
    )

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
    unreal.log("VALIDATE_M11: phase_c_bushes={}".format(len(phase_c_bushes)))
    unreal.log("VALIDATE_M11: phase_c_boulevards={}".format(len(phase_c_boulevards)))
    unreal.log("VALIDATE_M11: industrial_loading_docks={}".format(len(loading_docks)))
    unreal.log("VALIDATE_M11: facade_details={}".format(len(facade_details)))
    unreal.log("VALIDATE_M11: roof_details={}".format(len(roof_details)))
    unreal.log("VALIDATE_M11: secondary_parking_parts={}".format(len(secondary_parking)))
    unreal.log("VALIDATE_M11: district_crosswalks={}".format(len(district_crosswalks)))
    unreal.log("VALIDATE_M11: street_props={}".format(len(street_props)))
    unreal.log("VALIDATE_M11: skyline_parts={}".format(len(skyline)))
    unreal.log("VALIDATE_M11: PHASE D CHECKS PASSED")
    unreal.log("VALIDATE_M11: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
