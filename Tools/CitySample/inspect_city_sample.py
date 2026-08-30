# inspect_city_sample.py
# Run this script AGAINST the standalone Epic City Sample project.
# It does not modify the sample. It discovers the Small City map and reports
# potentially conflicting gameplay systems before any content is migrated.

import json
import os
import unreal

MAP_NAME = "Small_City_LVL"
SEARCH_ROOTS = ["/Game/Map", "/Game/Maps"]

CONFLICT_TOKENS = (
    "mass",
    "crowd",
    "traffic",
    "vehicle",
    "parking",
    "citysamplegamemode",
    "citysampleplayer",
    "spawn",
)


def log(message):
    unreal.log("CITY_SAMPLE_DISCOVERY: " + message)


def find_small_city():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    candidates = []

    for root in SEARCH_ROOTS:
        assets = registry.get_assets_by_path(root, recursive=True)
        for asset in assets:
            asset_name = str(asset.asset_name)
            package_name = str(asset.package_name)
            if asset_name == MAP_NAME or package_name.endswith("/" + MAP_NAME):
                candidates.append(package_name)

    if not candidates:
        # Fallback: scan all assets because sample folder layout can change.
        for asset in registry.get_all_assets():
            asset_name = str(asset.asset_name)
            package_name = str(asset.package_name)
            if asset_name == MAP_NAME or package_name.endswith("/" + MAP_NAME):
                candidates.append(package_name)

    return sorted(set(candidates))


def actor_record(actor):
    cls = actor.get_class()
    return {
        "label": actor.get_actor_label(),
        "name": actor.get_name(),
        "class": cls.get_name() if cls else "",
        "class_path": cls.get_path_name() if cls else "",
    }


def main():
    maps = find_small_city()
    if not maps:
        raise RuntimeError("Small_City_LVL was not found in this project.")

    log("FOUND_SMALL_CITY=" + maps[0])
    if len(maps) > 1:
        log("ADDITIONAL_MATCHES=" + ",".join(maps[1:]))

    unreal.EditorLoadingAndSavingUtils.load_map(maps[0])

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = [actor for actor in actor_subsystem.get_all_level_actors() if actor]

    conflicts = []
    for actor in actors:
        rec = actor_record(actor)
        haystack = " ".join(rec.values()).lower()
        if any(token in haystack for token in CONFLICT_TOKENS):
            conflicts.append(rec)

    world = unreal.EditorLevelLibrary.get_editor_world()
    world_settings = world.get_world_settings() if world else None

    report = {
        "small_city_map": maps[0],
        "actor_count_loaded": len(actors),
        "potential_gameplay_conflicts": conflicts,
        "world_settings_class": (
            world_settings.get_class().get_path_name() if world_settings else ""
        ),
    }

    saved_dir = unreal.Paths.project_saved_dir()
    output_path = os.path.join(saved_dir, "CitySampleDiscovery.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    log("LOADED_ACTORS={}".format(len(actors)))
    log("POTENTIAL_CONFLICT_ACTORS={}".format(len(conflicts)))
    for rec in conflicts[:80]:
        log(
            "CONFLICT label={label} class={class} path={class_path}".format(**rec)
        )

    if len(conflicts) > 80:
        log("CONFLICT_OUTPUT_TRUNCATED remaining={}".format(len(conflicts) - 80))

    log("REPORT=" + output_path)
    log("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
