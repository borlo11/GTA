# inspect_m10_template_vehicle.py
# Read-only inspection of the migrated UE 5.8 Vehicle Template assets.
#
# The goal is to discover the exact input mapping/action asset names and
# relevant Blueprint dependencies before OWGame integrates the SportsCar.

import unreal

SPORTS_CAR_BP = "/Game/VehicleTemplate/Blueprints/SportsCar/BP_VehicleAdvSportsCar"
BASE_BP = "/Game/VehicleTemplate/Blueprints/BP_VehicleAdvPawnBase"
INPUT_ROOT = "/Game/VehicleTemplate/Input"


def log(message):
    unreal.log_warning("M10_INSPECT: " + message)


def package_dependencies(package_name):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    options = unreal.AssetRegistryDependencyOptions(
        include_soft_package_references=True,
        include_hard_package_references=True,
        include_searchable_names=False,
        include_soft_management_references=True,
        include_hard_management_references=True,
    )
    try:
        deps = registry.get_dependencies(package_name, options) or []
    except Exception as exc:
        log("dependency lookup failed for {}: {}".format(package_name, exc))
        return []
    return sorted(str(dep) for dep in deps)


def dump_blueprint(label, path):
    asset = unreal.load_asset(path)
    if not asset:
        log("{} missing: {}".format(label, path))
        return

    log("{} asset={}".format(label, asset.get_path_name()))

    try:
        generated_class = asset.generated_class()
        log("{} generated_class={}".format(label, generated_class.get_path_name()))
    except Exception as exc:
        log("{} generated_class unavailable: {}".format(label, exc))

    for dep in package_dependencies(path):
        dep_lower = dep.lower()
        if (
            "vehicletemplate" in dep_lower
            or "/game/vehicles/" in dep_lower
            or "/game/input/" in dep_lower
            or "chaos" in dep_lower
        ):
            log("{} dependency={}".format(label, dep))


def main():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()

    log("=== INPUT ASSETS ===")
    input_assets = registry.get_assets_by_path(INPUT_ROOT, recursive=True) or []
    for data in sorted(input_assets, key=lambda d: str(d.package_name)):
        log(
            "INPUT class={} package={} name={}".format(
                data.asset_class_path,
                data.package_name,
                data.asset_name,
            )
        )

    log("=== SPORTS CAR BLUEPRINT ===")
    dump_blueprint("SPORTSCAR", SPORTS_CAR_BP)

    log("=== BASE VEHICLE BLUEPRINT ===")
    dump_blueprint("BASE", BASE_BP)

    log("DONE")


if __name__ == "__main__":
    main()
