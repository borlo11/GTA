# discover_m10_vehicle_assets.py
# M10 vehicle-asset audit for Unreal Engine 5.8.
#
# This script does not modify project content. It inspects the mounted Asset
# Registry and reports skeletal meshes / physics assets / likely vehicle
# blueprints that could support a Chaos Vehicles implementation.

import os
import unreal

REPORT_NAME = "M10_VehicleAssetCandidates.txt"

POSITIVE_TERMS = {
    "vehicle": 40,
    "car": 40,
    "sedan": 36,
    "coupe": 32,
    "sports": 24,
    "sport": 20,
    "supercar": 32,
    "muscle": 24,
    "suv": 26,
    "truck": 24,
    "pickup": 24,
    "buggy": 22,
    "hatch": 20,
    "chassis": 16,
    "wheel": 10,
    "tire": 8,
    "tyre": 8,
}

NEGATIVE_TERMS = (
    "manny",
    "quinn",
    "mannequin",
    "metahuman",
    "character",
    "humanoid",
)

CLASS_BONUS = {
    "skeletalmesh": 30,
    "physicsasset": 20,
    "blueprint": 8,
    "animblueprint": 5,
}


def score_asset(data):
    package = str(data.package_name)
    name = str(data.asset_name)
    class_path = str(data.asset_class_path)
    haystack = "{} {} {}".format(package, name, class_path).lower()

    if any(term in haystack for term in NEGATIVE_TERMS):
        return -1

    score = 0

    for term, points in POSITIVE_TERMS.items():
        if term in haystack:
            score += points

    class_lower = class_path.lower()
    for class_name, points in CLASS_BONUS.items():
        if class_name in class_lower:
            score += points
            break

    # Prefer project/plugin content over generic engine assets when two
    # candidates otherwise score similarly.
    if package.startswith("/Game/"):
        score += 16
    elif not package.startswith("/Engine/"):
        score += 8

    return score


def main():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()

    # get_all_assets is deliberate here: mounted Fab/plugin content can live
    # outside /Game, and M10 needs to know whether a usable car already exists.
    assets = registry.get_all_assets() or []

    candidates = []
    skeletal_meshes = 0
    physics_assets = 0

    for data in assets:
        class_path = str(data.asset_class_path).lower()

        if "skeletalmesh" in class_path:
            skeletal_meshes += 1
        elif "physicsasset" in class_path:
            physics_assets += 1
        elif "blueprint" not in class_path:
            continue

        score = score_asset(data)
        if score <= 0:
            continue

        candidates.append(
            (
                score,
                str(data.package_name),
                str(data.asset_name),
                str(data.asset_class_path),
            )
        )

    candidates.sort(key=lambda row: (-row[0], row[1]))

    lines = [
        "M10_DISCOVERY: asset_registry_total={}".format(len(assets)),
        "M10_DISCOVERY: skeletal_meshes={}".format(skeletal_meshes),
        "M10_DISCOVERY: physics_assets={}".format(physics_assets),
        "M10_DISCOVERY: scored_candidates={}".format(len(candidates)),
    ]

    for index, (score, package, name, class_path) in enumerate(candidates[:120]):
        lines.append(
            "M10_CANDIDATE {:03d} score={} class={} package={} name={}".format(
                index + 1,
                score,
                class_path,
                package,
                name,
            )
        )

    if not candidates:
        lines.append("M10_DISCOVERY: NO_VEHICLE_CANDIDATES_FOUND")
        lines.append(
            "M10_DISCOVERY: install/import a rigged four-wheel vehicle asset before final Chaos setup"
        )

    report_path = os.path.join(unreal.Paths.project_saved_dir(), REPORT_NAME)
    with open(report_path, "w", encoding="utf-8") as report:
        report.write("\n".join(lines))
        report.write("\n")

    for line in lines[:90]:
        unreal.log_warning(line)

    unreal.log_warning("M10_DISCOVERY_REPORT={}".format(report_path))
    unreal.log_warning("M10_DISCOVERY: DONE")


if __name__ == "__main__":
    main()
