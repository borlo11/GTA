# discover_m10_vehicle_assets.py
# M10 vehicle-asset audit for Unreal Engine 5.8.
#
# This script does not modify project content. It inspects the mounted Asset
# Registry and reports every SkeletalMesh / PhysicsAsset plus only genuinely
# vehicle-like Blueprints. That keeps the audit useful even when the project
# contains many unrelated Blueprints.

import os
import unreal

REPORT_NAME = "M10_VehicleAssetCandidates.txt"

VEHICLE_TERMS = (
    "vehicle",
    "car",
    "sedan",
    "coupe",
    "sports",
    "sport",
    "supercar",
    "muscle",
    "suv",
    "truck",
    "pickup",
    "buggy",
    "hatch",
    "chassis",
    "wheel",
    "tire",
    "tyre",
)


def has_vehicle_term(*parts):
    haystack = " ".join(str(part) for part in parts).lower()
    return any(term in haystack for term in VEHICLE_TERMS)


def main():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_all_assets() or []

    skeletal_meshes = []
    physics_assets = []
    vehicle_blueprints = []

    for data in assets:
        package = str(data.package_name)
        name = str(data.asset_name)
        class_path = str(data.asset_class_path).lower()

        row = (package, name, str(data.asset_class_path))

        if "skeletalmesh" in class_path:
            skeletal_meshes.append(row)
            continue

        if "physicsasset" in class_path:
            physics_assets.append(row)
            continue

        if "blueprint" in class_path and has_vehicle_term(package, name):
            vehicle_blueprints.append(row)

    skeletal_meshes.sort(key=lambda row: row[0])
    physics_assets.sort(key=lambda row: row[0])
    vehicle_blueprints.sort(key=lambda row: row[0])

    lines = [
        "M10_DISCOVERY: asset_registry_total={}".format(len(assets)),
        "M10_DISCOVERY: skeletal_meshes={}".format(len(skeletal_meshes)),
        "M10_DISCOVERY: physics_assets={}".format(len(physics_assets)),
        "M10_DISCOVERY: vehicle_blueprints={}".format(len(vehicle_blueprints)),
        "",
        "=== ALL SKELETAL MESHES ===",
    ]

    for index, (package, name, class_path) in enumerate(skeletal_meshes, start=1):
        lines.append(
            "M10_SKELETAL {:03d} class={} package={} name={}".format(
                index,
                class_path,
                package,
                name,
            )
        )

    lines.append("")
    lines.append("=== ALL PHYSICS ASSETS ===")

    for index, (package, name, class_path) in enumerate(physics_assets, start=1):
        lines.append(
            "M10_PHYSICS {:03d} class={} package={} name={}".format(
                index,
                class_path,
                package,
                name,
            )
        )

    lines.append("")
    lines.append("=== VEHICLE-LIKE BLUEPRINTS ONLY ===")

    for index, (package, name, class_path) in enumerate(vehicle_blueprints, start=1):
        lines.append(
            "M10_VEHICLE_BP {:03d} class={} package={} name={}".format(
                index,
                class_path,
                package,
                name,
            )
        )

    usable_meshes = [
        row
        for row in skeletal_meshes
        if has_vehicle_term(row[0], row[1])
    ]
    usable_physics = [
        row
        for row in physics_assets
        if has_vehicle_term(row[0], row[1])
    ]

    lines.append("")
    lines.append(
        "M10_DISCOVERY: vehicle_skeletal_candidates={}".format(len(usable_meshes))
    )
    lines.append(
        "M10_DISCOVERY: vehicle_physics_candidates={}".format(len(usable_physics))
    )

    if not usable_meshes:
        lines.append("M10_DISCOVERY: NO_VEHICLE_SKELETAL_MESH_FOUND")

    if not usable_physics:
        lines.append("M10_DISCOVERY: NO_VEHICLE_PHYSICS_ASSET_FOUND")

    if not usable_meshes or not usable_physics:
        lines.append(
            "M10_DISCOVERY: a rigged four-wheel vehicle asset is still required for the final Chaos car"
        )

    report_path = os.path.join(unreal.Paths.project_saved_dir(), REPORT_NAME)
    with open(report_path, "w", encoding="utf-8") as report:
        report.write("\n".join(lines))
        report.write("\n")

    for line in lines:
        unreal.log_warning(line)

    unreal.log_warning("M10_DISCOVERY_REPORT={}".format(report_path))
    unreal.log_warning("M10_DISCOVERY: DONE")


if __name__ == "__main__":
    main()
