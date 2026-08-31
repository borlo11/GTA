# discover_m9_uniblocks_prefabs.py
# Read-only discovery pass for UNIBLOCKS FREE v4 assets.
# It does NOT modify maps or assets. It prints a compact ranked list of
# building/prefab Blueprint/World candidates so M9 can use the pack's real
# authored architecture instead of stretching SM_UB_Block_scalable.

import unreal

ROOT = "/Game/Uniblocks"

KEYWORDS = (
    "building",
    "prefab",
    "house",
    "office",
    "villa",
    "cabin",
    "elevated",
    "hover",
    "apartment",
    "tower",
    "hall",
    "construction",
)

EXCLUDE = (
    "material",
    "texture",
    "sound",
    "demo_grid",
    "documentation",
    "buildkit",
)

registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = registry.get_assets_by_path(ROOT, recursive=True)

candidates = []

for data in assets:
    package = str(data.package_name)
    name = str(data.asset_name)
    class_path = str(data.asset_class_path)
    haystack = (package + " " + name).lower()

    if any(term in haystack for term in EXCLUDE):
        continue

    score = sum(4 for term in KEYWORDS if term in haystack)

    if "blueprint" in class_path.lower():
        score += 5
    if "world" in class_path.lower():
        score += 4
    if "levelinstance" in class_path.lower():
        score += 5
    if "prefab" in haystack:
        score += 8
    if "/buildings/" in package.lower() or "/prefabs/" in package.lower():
        score += 6

    if score > 0:
        candidates.append((score, package, name, class_path))

candidates.sort(key=lambda item: (-item[0], item[1]))

unreal.log("M9_DISCOVERY: UNIBLOCKS assets scanned={}".format(len(assets)))
unreal.log("M9_DISCOVERY: candidates={}".format(len(candidates)))

for index, (score, package, name, class_path) in enumerate(candidates[:80]):
    unreal.log(
        "M9_CANDIDATE {:02d} score={} class={} package={} name={}".format(
            index + 1,
            score,
            class_path,
            package,
            name,
        )
    )

unreal.log("M9_DISCOVERY: DONE")
