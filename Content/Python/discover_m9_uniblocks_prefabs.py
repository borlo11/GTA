# discover_m9_uniblocks_prefabs.py
# Read-only discovery pass for UNIBLOCKS FREE v4 assets.
# Does not modify maps/assets. Forces an AssetRegistry scan, ranks likely
# authored building/prefab assets, logs them, and writes a text report under Saved/.

import os
import unreal

ROOT = "/Game/Uniblocks"

KEYWORDS = (
    "building",
    "prefab",
    "house",
    "office",
    "villa",
    "cabin",
    "apartment",
    "tower",
    "shop",
    "store",
    "hotel",
    "residential",
    "commercial",
    "industrial",
    "block",
)

EXCLUDE = (
    "material",
    "texture",
    "sound",
    "documentation",
    "buildkit",
)

registry = unreal.AssetRegistryHelpers.get_asset_registry()

# Commandlets can query before the local Fab content is fully indexed.
try:
    registry.scan_paths_synchronous([ROOT], True)
except Exception as exc:
    unreal.log_warning("M9_DISCOVERY: scan_paths_synchronous warning: {}".format(exc))

assets = registry.get_assets_by_path(ROOT, recursive=True)

rows = []
for data in assets:
    package = str(data.package_name)
    name = str(data.asset_name)
    class_path = str(data.asset_class_path)
    haystack = (package + " " + name + " " + class_path).lower()

    if any(term in haystack for term in EXCLUDE):
        continue

    score = 0
    for term in KEYWORDS:
        if term in haystack:
            score += 4

    class_lower = class_path.lower()
    package_lower = package.lower()

    if "blueprint" in class_lower:
        score += 10
    if "world" in class_lower:
        score += 8
    if "levelinstance" in class_lower:
        score += 10
    if "prefab" in haystack:
        score += 12
    if "/buildings/" in package_lower:
        score += 8
    if "/prefabs/" in package_lower:
        score += 10
    if "/blueprints/" in package_lower:
        score += 6

    if score > 0:
        rows.append((score, package, name, class_path))

rows.sort(key=lambda item: (-item[0], item[1]))

lines = []
lines.append("M9_DISCOVERY: root={}".format(ROOT))
lines.append("M9_DISCOVERY: assets_scanned={}".format(len(assets)))
lines.append("M9_DISCOVERY: candidates={}".format(len(rows)))

for index, (score, package, name, class_path) in enumerate(rows[:120]):
    lines.append(
        "M9_CANDIDATE {:03d} score={} class={} package={} name={}".format(
            index + 1,
            score,
            class_path,
            package,
            name,
        )
    )

if not rows:
    lines.append("M9_DISCOVERY: NO_CANDIDATES_FOUND")
    lines.append("M9_DISCOVERY: dumping first 120 non-excluded assets for inspection")

    dumped = 0
    for data in assets:
        package = str(data.package_name)
        name = str(data.asset_name)
        class_path = str(data.asset_class_path)
        haystack = (package + " " + name).lower()

        if any(term in haystack for term in EXCLUDE):
            continue

        lines.append(
            "M9_ASSET {:03d} class={} package={} name={}".format(
                dumped + 1,
                class_path,
                package,
                name,
            )
        )
        dumped += 1
        if dumped >= 120:
            break

project_dir = unreal.Paths.project_dir()
saved_dir = os.path.join(project_dir, "Saved")
os.makedirs(saved_dir, exist_ok=True)
report_path = os.path.join(saved_dir, "M9_UniblocksCandidates.txt")

with open(report_path, "w", encoding="utf-8") as report:
    report.write("\n".join(lines))
    report.write("\n")

for line in lines[:130]:
    unreal.log_warning(line)

unreal.log_warning("M9_DISCOVERY_REPORT={}".format(report_path))
unreal.log_warning("M9_DISCOVERY: DONE")
