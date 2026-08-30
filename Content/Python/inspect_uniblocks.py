# inspect_uniblocks.py
# Read-only discovery for the locally imported UNIBLOCKS FREE content.
# Does not create, modify, rename, move, or save assets.

import json
import os
import unreal

ROOT = "/Game/Uniblocks"
INTERESTING_CLASSES = {
    "Blueprint",
    "StaticMesh",
    "World",
    "Material",
    "MaterialInstanceConstant",
    "Texture2D",
}


def log(message):
    unreal.log("UNIBLOCKS_DISCOVERY: " + message)


def main():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path(ROOT, recursive=True)

    if not assets:
        raise RuntimeError("No assets found under {}".format(ROOT))

    records = []
    class_counts = {}

    for asset in assets:
        asset_name = str(asset.asset_name)
        package_name = str(asset.package_name)
        class_path = str(asset.asset_class_path)
        class_name = class_path.split(".")[-1] if "." in class_path else class_path.split("/")[-1]

        class_counts[class_name] = class_counts.get(class_name, 0) + 1
        records.append(
            {
                "name": asset_name,
                "package": package_name,
                "class": class_name,
                "class_path": class_path,
            }
        )

    records.sort(key=lambda x: (x["class"], x["package"]))

    log("ROOT={}".format(ROOT))
    log("TOTAL_ASSETS={}".format(len(records)))
    for cls in sorted(class_counts):
        log("CLASS {}={}".format(cls, class_counts[cls]))

    priority = [
        r for r in records
        if r["class"] in INTERESTING_CLASSES
        and (
            "prefab" in r["name"].lower()
            or "building" in r["name"].lower()
            or "house" in r["name"].lower()
            or "block" in r["name"].lower()
            or "road" in r["name"].lower()
            or "street" in r["name"].lower()
            or "demo" in r["name"].lower()
            or r["class"] in {"Blueprint", "World"}
        )
    ]

    log("PRIORITY_ASSETS={}".format(len(priority)))
    for rec in priority[:120]:
        log(
            "ASSET class={class} name={name} package={package}".format(**rec)
        )

    if len(priority) > 120:
        log("PRIORITY_OUTPUT_TRUNCATED remaining={}".format(len(priority) - 120))

    output_path = os.path.join(
        unreal.Paths.project_saved_dir(),
        "UniblocksDiscovery.json",
    )

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "root": ROOT,
                "total_assets": len(records),
                "class_counts": class_counts,
                "priority_assets": priority,
                "all_assets": records,
            },
            handle,
            indent=2,
            ensure_ascii=False,
        )

    log("REPORT={}".format(output_path))
    log("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
