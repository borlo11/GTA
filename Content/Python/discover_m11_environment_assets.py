# discover_m11_environment_assets.py
# Read-only inventory for M11 Environment & Free-Roam.
#
# Scans local /Game content and reports environment assets that could support
# distinct districts. It does not create, modify, save, or delete any asset.

import os
import unreal

ROOTS = (
    "/Game/Uniblocks",
    "/Game",
)

ENVIRONMENT_TERMS = (
    "building", "prefab", "house", "home", "villa", "cabin", "apartment",
    "office", "shop", "store", "industrial", "factory", "warehouse",
    "garage", "parking", "road", "street", "sidewalk", "pavement", "curb",
    "lamp", "light", "pole", "bollard", "barrier", "fence", "railing",
    "sign", "billboard", "bench", "trash", "bin", "planter", "flower",
    "tree", "bush", "grass", "plant", "park", "plaza", "garden",
    "concrete", "brick", "asphalt", "metal", "wall", "door", "window",
    "stairs", "stair", "gate", "pillar", "beam", "cladding", "perron",
)

DISTRICT_TERMS = {
    "residential": ("house", "home", "villa", "cabin", "garden", "flower", "fence"),
    "central": ("office", "shop", "store", "modern", "billboard", "plaza", "window"),
    "industrial": ("industrial", "factory", "warehouse", "garage", "metal", "gate", "barrier"),
    "waterfront": ("railing", "lamp", "bench", "plaza", "concrete", "bollard"),
    "park": ("tree", "bush", "grass", "plant", "garden", "flower", "bench", "planter"),
    "roads": ("road", "street", "asphalt", "sidewalk", "pavement", "curb", "parking", "sign"),
}

IGNORE_PATH_TERMS = (
    "/characters/",
    "/vehicles/",
    "/input/",
    "/ui/",
    "/audio/",
)

registry = unreal.AssetRegistryHelpers.get_asset_registry()

for root in ROOTS:
    try:
        registry.scan_paths_synchronous([root], True)
    except Exception as exc:
        unreal.log_warning(
            "M11_DISCOVERY: scan warning root={} error={}".format(root, exc)
        )

# Deduplicate because /Game/Uniblocks is contained by /Game.
all_assets = {}
for root in ROOTS:
    for data in registry.get_assets_by_path(root, recursive=True) or []:
        all_assets[str(data.package_name)] = data

assets = list(all_assets.values())

prefab_worlds = []
static_meshes = []
blueprints = []
materials = []
district_rows = {name: [] for name in DISTRICT_TERMS}

for data in assets:
    package = str(data.package_name)
    name = str(data.asset_name)
    class_path = str(data.asset_class_path)
    lower = (package + " " + name + " " + class_path).lower()

    if any(term in lower for term in IGNORE_PATH_TERMS):
        continue

    class_lower = class_path.lower()
    score = sum(2 for term in ENVIRONMENT_TERMS if term in lower)

    if "world" in class_lower:
        score += 12
    if "prefab" in lower:
        score += 12
    if "levelinstance" in lower:
        score += 10
    if "staticmesh" in class_lower:
        score += 5
    if "blueprint" in class_lower:
        score += 6
    if "materialinstance" in class_lower or "material" in class_lower:
        score += 2

    row = (score, package, name, class_path)

    if "world" in class_lower and ("prefab" in lower or "house" in lower or "building" in lower):
        prefab_worlds.append(row)

    if "staticmesh" in class_lower and score > 4:
        static_meshes.append(row)

    if "blueprint" in class_lower and score > 5:
        blueprints.append(row)

    if ("materialinstance" in class_lower or "material" in class_lower) and score > 1:
        materials.append(row)

    for district, terms in DISTRICT_TERMS.items():
        district_score = score + sum(5 for term in terms if term in lower)
        if district_score >= 10:
            district_rows[district].append(
                (district_score, package, name, class_path)
            )


def sorted_rows(rows):
    return sorted(rows, key=lambda item: (-item[0], item[1]))


prefab_worlds = sorted_rows(prefab_worlds)
static_meshes = sorted_rows(static_meshes)
blueprints = sorted_rows(blueprints)
materials = sorted_rows(materials)

lines = []
lines.append("M11_DISCOVERY: assets_scanned={}".format(len(assets)))
lines.append("M11_DISCOVERY: prefab_worlds={}".format(len(prefab_worlds)))
lines.append("M11_DISCOVERY: static_mesh_candidates={}".format(len(static_meshes)))
lines.append("M11_DISCOVERY: blueprint_candidates={}".format(len(blueprints)))
lines.append("M11_DISCOVERY: material_candidates={}".format(len(materials)))


def emit_section(title, prefix, rows, limit):
    lines.append("")
    lines.append("=== {} ===".format(title))
    for index, (score, package, name, class_path) in enumerate(rows[:limit]):
        lines.append(
            "{} {:03d} score={} class={} package={} name={}".format(
                prefix,
                index + 1,
                score,
                class_path,
                package,
                name,
            )
        )


emit_section("PREFAB WORLDS", "M11_PREFAB", prefab_worlds, 80)
emit_section("STATIC MESHES", "M11_MESH", static_meshes, 160)
emit_section("BLUEPRINT PROPS", "M11_BP", blueprints, 120)
emit_section("MATERIALS", "M11_MAT", materials, 100)

for district in ("residential", "central", "industrial", "waterfront", "park", "roads"):
    rows = sorted_rows(district_rows[district])
    emit_section(
        "DISTRICT {}".format(district.upper()),
        "M11_{}".format(district.upper()),
        rows,
        60,
    )

project_dir = unreal.Paths.project_dir()
saved_dir = os.path.join(project_dir, "Saved")
os.makedirs(saved_dir, exist_ok=True)
report_path = os.path.join(saved_dir, "M11_EnvironmentAssetInventory.txt")

with open(report_path, "w", encoding="utf-8") as report:
    report.write("\n".join(lines))
    report.write("\n")

# Console output stays concise; the full ranked inventory is in Saved/.
for line in lines:
    if (
        line.startswith("M11_DISCOVERY:")
        or line.startswith("M11_PREFAB ")
        or line.startswith("M11_RESIDENTIAL ")
        or line.startswith("M11_CENTRAL ")
        or line.startswith("M11_INDUSTRIAL ")
        or line.startswith("M11_WATERFRONT ")
        or line.startswith("M11_PARK ")
        or line.startswith("M11_ROADS ")
    ):
        unreal.log_warning(line)

unreal.log_warning("M11_DISCOVERY_REPORT={}".format(report_path))
unreal.log_warning("M11_DISCOVERY: DONE")
