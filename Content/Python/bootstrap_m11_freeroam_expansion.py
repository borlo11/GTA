# bootstrap_m11_freeroam_expansion.py
# M11 Phase B: additive free-roam expansion around the existing M9/M10 core.
#
# IMPORTANT:
# - preserves all M9/M10 gameplay actors and the current central district;
# - owns only actors whose label starts with OW_M11_;
# - expands the road network and adds four visually distinct outer districts;
# - uses a small number of authored UNIBLOCKS LevelInstances to protect FPS.

import unreal

TARGET_MAP = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_M11_"
UNIBLOCKS_ROOT = "/Game/Uniblocks"

CUBE = "/Engine/BasicShapes/Cube.Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder.Cylinder"

WORLD_SIZE = 96000.0
GROUND_TOP_Z = -10.0
ROAD_Z = 2.0
ROAD_HEIGHT = 12.0

ROAD_CENTERS = (-36000.0, -24000.0, -12000.0, 0.0, 12000.0, 24000.0, 36000.0)
BLOCK_CENTERS = (-30000.0, -18000.0, -6000.0, 6000.0, 18000.0, 30000.0)

PREFABS = {
    "classic": "/Game/Uniblocks/Maps/LI_prefab_Classic_house_v1",
    "modern": "/Game/Uniblocks/Maps/LI_prefab_Modern_house2_v1",
    "future": "/Game/Uniblocks/Maps/LI_prefab_Futuristic_cabin_v1",
    "art": "/Game/Uniblocks/Maps/LI_prefab_Art_house_elevated_v1",
}

# Phase E increases real authored architecture while keeping LevelInstance
# density deliberately modest for the project's 60 FPS target.
AUTHORED_PREFAB_SITES = (
    ("Residential_Hero_Classic", "classic", -30000.0, 30000.0, 0.0),
    ("Residential_Hero_Art", "art", -18000.0, 18000.0, 180.0),
    ("Modern_Hero_Modern", "modern", 18000.0, 30000.0, 180.0),
    ("Modern_Hero_Future", "future", 30000.0, 18000.0, 0.0),

    ("Residential_Infill_01", "classic", -30000.0, 18000.0, 90.0),
    ("Residential_Infill_02", "art", -18000.0, 30000.0, 270.0),
    ("Residential_Infill_03", "classic", -6000.0, 30000.0, 180.0),
    ("Residential_Infill_04", "art", -30000.0, 6000.0, 0.0),

    ("Modern_Infill_01", "modern", 30000.0, 30000.0, 90.0),
    ("Modern_Infill_02", "future", 18000.0, 18000.0, 270.0),
    ("Modern_Infill_03", "modern", 6000.0, 30000.0, 0.0),
    ("Modern_Infill_04", "future", 30000.0, 6000.0, 180.0),
)

# Exact visible (non-collider) assets confirmed by the user's local M11
# inventory. Optional loading keeps the bootstrap resilient to a modified
# local Fab installation.
AUTHORED_PARTS = {
    "door_swing": "/Game/Uniblocks/Meshes/Doors_swing/Parts/SM_UBP_DoorA_body_window_2",
    "door_slide": "/Game/Uniblocks/Meshes/Doors_slide/Parts/SM_UBP_DoorB_body_window_3",
    "window_big": "/Game/Uniblocks/Meshes/Gate/Parts_window/SM_UBP_Gate_sgmtWindowBig_03",
    "window_mid": "/Game/Uniblocks/Meshes/Gate/Parts_window/SM_UBP_Gate_sgmtWindowMid_04",
    "fence_big": "/Game/Uniblocks/Meshes/Gate/Parts_fence/SM_UBP_Gate_sgmtFenceBig_01",
    "flowerbed": "/Game/Uniblocks/Meshes/Garden/Parts/SM_UBP_Flowerbed_single_wall_top_t15",
    "lamp_head": "/Game/Uniblocks/Meshes/Lights/Parts/SM_UBP_Lamp_end_rectangular_middle",
}

ROAD_MATERIAL_NAMES = (
    "MI_UBT_concreteSmooth_dark",
    "MI_UBT_concreteAged_lines",
)
SIDEWALK_MATERIAL_NAMES = (
    "MI_UBT_concreteSmooth_gray",
    "MI_UBT_concreteRaw_gray_plain",
)
MARKING_MATERIAL_NAMES = (
    "MI_UBT_concreteRaw_white_plain",
    "MI_UBT_brickwork_white",
)
DARK_MATERIAL_NAMES = (
    "MI_UBT_concreteSmooth_dark",
    "MI_UBT_concreteRaw_gray_plain",
)
BACKGROUND_MATERIAL_NAMES = (
    "MI_UBT_brickwork_white",
    "MI_UBT_concreteSmooth_gray",
    "MI_UBT_concreteRaw_gray_plain",
)

log = unreal.log
warn = unreal.log_warning


def actor_subsystem():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def level_subsystem():
    return unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def find_asset(root, name):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    for data in registry.get_assets_by_path(root, recursive=True):
        if str(data.asset_name) == name:
            return unreal.EditorAssetLibrary.load_asset(str(data.package_name))
    return None


def first_asset(root, names):
    for name in names:
        asset = find_asset(root, name)
        if asset:
            return asset
    return None


def set_label(actor, label):
    actor.set_actor_label(label)
    return actor


def set_tags(actor, *tags):
    try:
        actor.set_editor_property("tags", [unreal.Name(tag) for tag in tags])
    except Exception:
        pass


def spawn_mesh(label, mesh_path, location, scale, material=None, collision=True, walkable=False, yaw=0.0):
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        raise RuntimeError("M11: missing mesh {}".format(mesh_path))

    actor = actor_subsystem().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    if not actor:
        raise RuntimeError("M11: failed spawning {}".format(label))

    set_label(actor, label)

    if walkable:
        set_tags(actor, "OWWalkableSpawn")
    elif collision:
        set_tags(actor, "OWNoPopulationSpawn")

    component = actor.static_mesh_component
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_static_mesh(mesh)
    component.set_collision_enabled(
        unreal.CollisionEnabled.QUERY_AND_PHYSICS
        if collision
        else unreal.CollisionEnabled.NO_COLLISION
    )

    if material:
        component.set_material(0, material)

    actor.set_actor_scale3d(scale)
    return actor


def cube(label, location, size, material=None, collision=True, walkable=False, yaw=0.0):
    return spawn_mesh(
        label,
        CUBE,
        location,
        unreal.Vector(size.x / 100.0, size.y / 100.0, size.z / 100.0),
        material,
        collision,
        walkable,
        yaw,
    )


def cylinder(label, location, diameter, height, material=None, collision=False):
    return spawn_mesh(
        label,
        CYLINDER,
        location,
        unreal.Vector(diameter / 100.0, diameter / 100.0, height / 100.0),
        material,
        collision,
        False,
    )


def mesh_dimensions(mesh):
    box = mesh.get_bounding_box()
    minimum = box.min
    maximum = box.max
    return unreal.Vector(
        max(1.0, maximum.x - minimum.x),
        max(1.0, maximum.y - minimum.y),
        max(1.0, maximum.z - minimum.z),
    )


def spawn_mesh_sized(label, mesh, location, target_size, material=None, collision=True, yaw=0.0):
    dims = mesh_dimensions(mesh)
    actor = actor_subsystem().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    if not actor:
        return None

    set_label(actor, label)
    set_tags(actor, "OWNoPopulationSpawn")

    component = actor.static_mesh_component
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_static_mesh(mesh)
    component.set_collision_enabled(
        unreal.CollisionEnabled.QUERY_AND_PHYSICS
        if collision
        else unreal.CollisionEnabled.NO_COLLISION
    )
    if material:
        component.set_material(0, material)

    actor.set_actor_scale3d(
        unreal.Vector(
            target_size.x / dims.x,
            target_size.y / dims.y,
            target_size.z / dims.z,
        )
    )
    return actor


def spawn_optional_visible_mesh(label, mesh_name, location, scale, yaw=0.0):
    """
    Spawn a confirmed visible UNIBLOCKS mesh by asset name.

    This helper is intentionally optional: dressing assets should never make
    the whole environment bootstrap fail if a specific Fab mesh is absent.
    """
    mesh = find_asset("/Game/Uniblocks/Meshes", mesh_name)
    if not mesh:
        warn("M11: optional visible mesh missing: {}".format(mesh_name))
        return None

    actor = actor_subsystem().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    if not actor:
        warn("M11: failed spawning optional visible mesh: {}".format(label))
        return None

    set_label(actor, label)
    set_tags(actor, "OWNoPopulationSpawn")

    component = actor.static_mesh_component
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_static_mesh(mesh)
    component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)

    actor.set_actor_scale3d(scale)
    return actor


def spawn_authored_part_sized(label, mesh_path, location, target_size, yaw=0.0, collision=False):
    """Spawn an inventory-confirmed UNIBLOCKS visible mesh at a controlled size."""
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        warn("M11: optional authored part missing: {}".format(mesh_path))
        return None

    return spawn_mesh_sized(
        label,
        mesh,
        location,
        target_size,
        None,
        collision,
        yaw,
    )


def load_materials():
    root = "/Game/Uniblocks/Materials"
    backgrounds = [
        find_asset(root, name)
        for name in BACKGROUND_MATERIAL_NAMES
    ]
    backgrounds = [m for m in backgrounds if m]

    return {
        "road": first_asset(root, ROAD_MATERIAL_NAMES),
        "sidewalk": first_asset(root, SIDEWALK_MATERIAL_NAMES),
        "marking": first_asset(root, MARKING_MATERIAL_NAMES),
        "dark": first_asset(root, DARK_MATERIAL_NAMES),
        "background": backgrounds,
    }


def clear_generated():
    removed = 0
    for actor in list(actor_subsystem().get_all_level_actors()):
        if actor and actor.get_actor_label().startswith(PREFIX):
            actor_subsystem().destroy_actor(actor)
            removed += 1
    log("M11: removed {} previous expansion actors".format(removed))


def ensure_dependencies():
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        raise RuntimeError("M11: target map missing: {}".format(TARGET_MAP))

    if not unreal.EditorAssetLibrary.does_directory_exist(UNIBLOCKS_ROOT):
        raise RuntimeError("M11: UNIBLOCKS FREE missing at /Game/Uniblocks")

    if not hasattr(unreal, "LevelInstance"):
        raise RuntimeError("M11: LevelInstance unavailable")

    for name, path in PREFABS.items():
        if not unreal.load_asset(path):
            raise RuntimeError("M11: missing prefab {} -> {}".format(name, path))


def build_world_base(mats):
    # Large low base under the existing M9 core. M9 geometry remains above it.
    cube(
        PREFIX + "WorldBase",
        unreal.Vector(0.0, 0.0, -90.0),
        unreal.Vector(WORLD_SIZE, WORLD_SIZE, 160.0),
        mats["sidewalk"],
        True,
        False,
    )

    road_count = 0
    for axis, centers in (("NS", ROAD_CENTERS), ("EW", ROAD_CENTERS)):
        for index, center in enumerate(centers):
            # Perimeter arterials are wider; central connector is widest.
            if abs(center) < 1.0:
                width = 1500.0
            elif abs(center) >= 35000.0:
                width = 1450.0
            else:
                width = 1050.0

            if axis == "NS":
                location = unreal.Vector(center, 0.0, ROAD_Z)
                size = unreal.Vector(width, WORLD_SIZE - 6000.0, ROAD_HEIGHT)
            else:
                location = unreal.Vector(0.0, center, ROAD_Z)
                size = unreal.Vector(WORLD_SIZE - 6000.0, width, ROAD_HEIGHT)

            road = cube(
                PREFIX + "Road_{}_{:02d}".format(axis, index),
                location,
                size,
                mats["road"],
                True,
                False,
            )
            set_tags(road, "OWRoadSurface", "OWNoPopulationSpawn")
            road_count += 1

    log("M11: expanded road network roads={}".format(road_count))


def add_lane_markings(mats):
    marking = mats["marking"] or mats["sidewalk"]
    count = 0

    # Long dashed center lanes. Skip the central 17k section where M9 already
    # provides its own road graphics so we do not create z-fighting.
    intervals = []
    for p in range(-43000, 43001, 3200):
        if -9500 < p < 9500:
            continue
        intervals.append(float(p))

    for center in ROAD_CENTERS:
        for p in intervals:
            cube(
                PREFIX + "Lane_NS_{:02d}".format(count),
                unreal.Vector(center, p, 9.0),
                unreal.Vector(16.0, 1450.0, 1.2),
                marking,
                False,
                False,
            )
            count += 1

            cube(
                PREFIX + "Lane_EW_{:02d}".format(count),
                unreal.Vector(p, center, 9.0),
                unreal.Vector(1450.0, 16.0, 1.2),
                marking,
                False,
                False,
            )
            count += 1

    # A few visible crosswalk clusters around the first outer intersections.
    stripe_count = 0
    for ix, iy in ((-12000.0, 0.0), (12000.0, 0.0), (0.0, -12000.0), (0.0, 12000.0)):
        for s in range(-4, 5):
            cube(
                PREFIX + "Crosswalk_{:02d}".format(stripe_count),
                unreal.Vector(ix + s * 85.0, iy + 620.0, 9.5),
                unreal.Vector(48.0, 380.0, 1.3),
                marking,
                False,
                False,
            )
            stripe_count += 1

    log("M11: road graphics lane_segments={} crosswalk_stripes={}".format(count, stripe_count))


def spawn_prefab(label, prefab_path, location, yaw):
    world_asset = unreal.load_asset(prefab_path)
    if not world_asset:
        raise RuntimeError("M11: missing prefab {}".format(prefab_path))

    instance = actor_subsystem().spawn_actor_from_class(
        unreal.LevelInstance,
        location,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    if not instance:
        raise RuntimeError("M11: failed to spawn prefab {}".format(label))

    set_label(instance, label)
    set_tags(instance, "OWNoPopulationSpawn")

    if not instance.set_world_asset(world_asset):
        actor_subsystem().destroy_actor(instance)
        raise RuntimeError("M11: LevelInstance rejected {}".format(prefab_path))

    try:
        instance.load_level_instance()
    except Exception as exc:
        warn("M11: prefab load warning {}: {}".format(label, exc))

    try:
        instance.set_actor_tick_enabled(False)
    except Exception:
        pass

    return instance


def district_for(x, y):
    if x < 0.0 and y > 0.0:
        return "Residential"
    if x > 0.0 and y > 0.0:
        return "Modern"
    if x < 0.0 and y < 0.0:
        return "Industrial"
    return "ParkEdge"


def build_district_pads(mats):
    count = 0
    for x in BLOCK_CENTERS:
        for y in BLOCK_CENTERS:
            # Keep the existing M9 central district untouched.
            if abs(x) < 10000.0 and abs(y) < 10000.0:
                continue

            district = district_for(x, y)

            if district == "ParkEdge" and x >= 18000.0 and y <= -18000.0:
                # Open green/plaza district: leave more road-to-road breathing room.
                size = 9300.0
            else:
                size = 10100.0

            cube(
                PREFIX + "{}_Pad_{:02d}".format(district, count),
                unreal.Vector(x, y, 5.0),
                unreal.Vector(size, size, 10.0),
                mats["sidewalk"],
                True,
                True,
            )
            count += 1

    log("M11: district pads={}".format(count))


def build_hero_prefabs():
    for label, prefab_key, x, y, yaw in AUTHORED_PREFAB_SITES:
        spawn_prefab(
            PREFIX + label,
            PREFABS[prefab_key],
            unreal.Vector(x, y, 18.0),
            yaw,
        )

    log("M11: authored outer hero/infill prefabs={}".format(len(AUTHORED_PREFAB_SITES)))


def add_authored_facade_detail(district, x, y, ox, oy, sx, sy, sz, yaw, index):
    """Place real UNIBLOCKS visible parts onto the cheap background masses."""
    base_z = 10.0
    rotated = int(round(yaw)) % 180 == 90

    if district == "Modern":
        mesh_path = (
            AUTHORED_PARTS["window_big"]
            if index % 2 == 0
            else AUTHORED_PARTS["window_mid"]
        )
        target = unreal.Vector(
            max(520.0, min(980.0, sx * 0.58)),
            48.0,
            max(220.0, min(430.0, sz * 0.33)),
        )
        z = base_z + sz * 0.56

        if rotated:
            location = unreal.Vector(x + ox + sy * 0.5 + 22.0, y + oy, z)
            part_yaw = 90.0
        else:
            location = unreal.Vector(x + ox, y + oy + sy * 0.5 + 22.0, z)
            part_yaw = 0.0

        spawn_authored_part_sized(
            PREFIX + "AuthoredFacade_Window_{:03d}".format(index),
            mesh_path,
            location,
            target,
            part_yaw,
            False,
        )

    elif district == "Residential":
        if index % 2 == 0:
            mesh_path = AUTHORED_PARTS["door_swing"]
            target = unreal.Vector(
                max(240.0, min(360.0, sx * 0.20)),
                50.0,
                max(280.0, min(390.0, sz * 0.58)),
            )
            z = base_z + target.z * 0.5
            label = PREFIX + "AuthoredFacade_Door_{:03d}".format(index)
        else:
            mesh_path = AUTHORED_PARTS["window_mid"]
            target = unreal.Vector(
                max(360.0, min(620.0, sx * 0.34)),
                45.0,
                max(190.0, min(300.0, sz * 0.36)),
            )
            z = base_z + sz * 0.58
            label = PREFIX + "AuthoredFacade_Window_{:03d}".format(index)

        if rotated:
            location = unreal.Vector(x + ox + sy * 0.5 + 20.0, y + oy, z)
            part_yaw = 90.0
        else:
            location = unreal.Vector(x + ox, y + oy + sy * 0.5 + 20.0, z)
            part_yaw = 0.0

        spawn_authored_part_sized(
            label,
            mesh_path,
            location,
            target,
            part_yaw,
            False,
        )

    elif district == "Industrial":
        target = unreal.Vector(
            max(720.0, min(1250.0, sx * 0.42)),
            58.0,
            max(300.0, min(470.0, sz * 0.66)),
        )
        z = base_z + target.z * 0.5

        if rotated:
            location = unreal.Vector(x + ox + sy * 0.5 + 24.0, y + oy, z)
            part_yaw = 90.0
        else:
            location = unreal.Vector(x + ox, y + oy + sy * 0.5 + 24.0, z)
            part_yaw = 0.0

        spawn_authored_part_sized(
            PREFIX + "AuthoredFacade_LoadingDoor_{:03d}".format(index),
            AUTHORED_PARTS["door_slide"],
            location,
            target,
            part_yaw,
            False,
        )


def dress_background_mass(mats, district, x, y, ox, oy, sx, sy, sz, yaw, index):
    """Add low-cost facade and rooftop cues so simple massing reads as architecture."""
    dark = mats["dark"] or mats["sidewalk"]
    base_z = 10.0

    # Rooftop service/crown volume breaks the pure-box silhouette at distance.
    cube(
        PREFIX + "RoofDetail_{:03d}".format(index),
        unreal.Vector(x + ox, y + oy, base_z + sz + 52.0),
        unreal.Vector(max(320.0, sx * 0.34), max(300.0, sy * 0.30), 104.0),
        dark,
        False,
        False,
        yaw,
    )

    rotated = int(round(yaw)) % 180 == 90

    if district == "Modern":
        # Two restrained dark facade bands suggest glazing without adding
        # expensive transparent materials or dozens of window meshes.
        for band_index, ratio in enumerate((0.42, 0.70)):
            if rotated:
                location = unreal.Vector(x + ox + sy * 0.5 + 8.0, y + oy, base_z + sz * ratio)
                size = unreal.Vector(16.0, max(520.0, sx * 0.72), 64.0)
            else:
                location = unreal.Vector(x + ox, y + oy + sy * 0.5 + 8.0, base_z + sz * ratio)
                size = unreal.Vector(max(520.0, sx * 0.72), 16.0, 64.0)

            cube(
                PREFIX + "Facade_Modern_{:03d}_{:02d}".format(index, band_index),
                location,
                size,
                dark,
                False,
                False,
                0.0,
            )

    elif district == "Industrial":
        # Large dark loading-door plane gives warehouses an obvious front.
        if rotated:
            location = unreal.Vector(x + ox + sy * 0.5 + 9.0, y + oy, base_z + min(250.0, sz * 0.45))
            size = unreal.Vector(18.0, max(760.0, sx * 0.42), min(360.0, sz * 0.62))
        else:
            location = unreal.Vector(x + ox, y + oy + sy * 0.5 + 9.0, base_z + min(250.0, sz * 0.45))
            size = unreal.Vector(max(760.0, sx * 0.42), 18.0, min(360.0, sz * 0.62))

        cube(
            PREFIX + "Facade_Industrial_{:03d}".format(index),
            location,
            size,
            dark,
            False,
            False,
            0.0,
        )

    else:
        # Small projecting awning/entry cue keeps residential masses from
        # reading as untouched cubes.
        if rotated:
            location = unreal.Vector(x + ox + sy * 0.5 + 70.0, y + oy, base_z + 225.0)
            size = unreal.Vector(150.0, min(650.0, sx * 0.48), 70.0)
        else:
            location = unreal.Vector(x + ox, y + oy + sy * 0.5 + 70.0, base_z + 225.0)
            size = unreal.Vector(min(650.0, sx * 0.48), 150.0, 70.0)

        cube(
            PREFIX + "Facade_Residential_{:03d}".format(index),
            location,
            size,
            dark,
            False,
            False,
            0.0,
        )

    add_authored_facade_detail(
        district,
        x,
        y,
        ox,
        oy,
        sx,
        sy,
        sz,
        yaw,
        index,
    )


def build_background_districts(mats):
    """
    Phase C.1 grounded massing pass.

    Do not use SM_UB_Block_scalable for district massing. Its authored pivot /
    bounds are not guaranteed to be centered, which can make scaled buildings
    appear as huge floating boxes in the free-roam map.

    Use the engine Cube for all cheap background architecture instead. Cube
    dimensions are deterministic, so every mass can be placed directly on the
    district pad with a known ground contact while the authored UNIBLOCKS
    LevelInstances remain the hero architecture.
    """
    backgrounds = mats["background"] or [mats["sidewalk"]]
    hero_lots = {
        (x, y)
        for _label, _prefab_key, x, y, _yaw in AUTHORED_PREFAB_SITES
    }

    count = 0
    pad_top_z = 10.0

    for x in BLOCK_CENTERS:
        for y in BLOCK_CENTERS:
            if abs(x) < 10000.0 and abs(y) < 10000.0:
                continue
            if (x, y) in hero_lots:
                continue

            district = district_for(x, y)

            # South-east stays intentionally open as park / civic / parking.
            if district == "ParkEdge":
                continue

            if district == "Residential":
                local = (
                    (-2200.0, -1650.0, 1900.0, 1500.0, 580.0, 0.0),
                    (1650.0, -850.0, 1650.0, 1400.0, 720.0, 90.0),
                    (250.0, 2050.0, 2050.0, 1400.0, 640.0, 0.0),
                )
            elif district == "Modern":
                local = (
                    (-1850.0, -1100.0, 1650.0, 1550.0, 1150.0, 0.0),
                    (1750.0, 1150.0, 1550.0, 1650.0, 1380.0, 90.0),
                    (-250.0, 2250.0, 2700.0, 950.0, 460.0, 0.0),
                )
            else:
                local = (
                    (-1850.0, -1500.0, 3300.0, 1950.0, 620.0, 0.0),
                    (1950.0, 1450.0, 3000.0, 1850.0, 700.0, 90.0),
                )

            for part_index, (ox, oy, sx, sy, sz, yaw) in enumerate(local):
                material = backgrounds[(count + part_index) % len(backgrounds)]

                # Engine Cube pivot is centered, so z = pad top + half height
                # guarantees that the building sits on the pad instead of
                # floating above it.
                actor = cube(
                    PREFIX + "{}_Background_{:03d}".format(district, count),
                    unreal.Vector(
                        x + ox,
                        y + oy,
                        pad_top_z + sz * 0.5,
                    ),
                    unreal.Vector(sx, sy, sz),
                    material,
                    True,
                    False,
                    yaw,
                )

                if not actor:
                    raise RuntimeError(
                        "M11: failed grounded background actor {}".format(count)
                    )

                dress_background_mass(
                    mats,
                    district,
                    x,
                    y,
                    ox,
                    oy,
                    sx,
                    sy,
                    sz,
                    yaw,
                    count,
                )

                count += 1

    log("M11: Phase C.1 grounded district buildings={}".format(count))

def build_phase_c_landscaping(mats):
    """
    Lightweight visual dressing using assets confirmed by the local inventory.
    Bushes are non-colliding and sparse so they improve scale/readability
    without turning the scene into a foliage benchmark.
    """
    bush_mesh = find_asset("/Game/Uniblocks/Meshes", "SM_UB_Bush_x150")
    if not bush_mesh:
        warn("M11: Phase C landscaping skipped; SM_UB_Bush_x150 unavailable")
        return

    positions = []

    # Residential front-garden rhythm.
    for x in (-33000.0, -30000.0, -27000.0, -21000.0, -18000.0, -15000.0):
        for y in (14500.0, 21500.0, 28500.0, 35500.0):
            positions.append((x, y, 0.70))

    # Modern district: fewer, more deliberate planted edges.
    for x, y in (
        (15000.0, 15500.0), (17500.0, 15500.0), (20500.0, 15500.0),
        (27500.0, 20500.0), (30500.0, 20500.0), (33500.0, 20500.0),
        (15500.0, 30500.0), (20500.0, 33500.0), (30500.0, 33500.0),
    ):
        positions.append((x, y, 0.62))

    count = 0
    for x, y, scale in positions:
        actor = actor_subsystem().spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(x, y, 82.0),
            unreal.Rotator(0.0, float((count * 47) % 360), 0.0),
        )

        if not actor:
            continue

        set_label(actor, PREFIX + "Env_Bush_{:03d}".format(count))
        set_tags(actor, "OWNoPopulationSpawn")

        component = actor.static_mesh_component
        component.set_static_mesh(bush_mesh)
        component.set_mobility(unreal.ComponentMobility.STATIC)
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        count += 1

    # Simple non-colliding curb/median bands make the main north/south and
    # east/west axes read like designed boulevards without affecting handling.
    curb_mat = mats["sidewalk"] or mats["marking"]
    for index, offset in enumerate((-760.0, 760.0)):
        cube(
            PREFIX + "Env_Boulevard_NS_{:02d}".format(index),
            unreal.Vector(offset, 0.0, 10.0),
            unreal.Vector(34.0, 84000.0, 8.0),
            curb_mat,
            False,
            False,
        )
        cube(
            PREFIX + "Env_Boulevard_EW_{:02d}".format(index),
            unreal.Vector(0.0, offset, 10.0),
            unreal.Vector(84000.0, 34.0, 8.0),
            curb_mat,
            False,
            False,
        )

    log("M11: Phase C landscaping bushes={}".format(count))



def build_industrial_dressing(mats):
    # Fence/gate parts are confirmed by the M11 inventory and come from visible
    # Parts/, not Colliders/.
    fence_mesh = unreal.load_asset(AUTHORED_PARTS["fence_big"])
    fence_count = 0

    for base_x, base_y, yaw in (
        (-33000.0, -18000.0, 0.0),
        (-27000.0, -18000.0, 0.0),
        (-21000.0, -30000.0, 90.0),
        (-21000.0, -24000.0, 90.0),
        (-33000.0, -30000.0, 0.0),
        (-27000.0, -30000.0, 0.0),
    ):
        if fence_mesh:
            actor = spawn_mesh_sized(
                PREFIX + "Industrial_Fence_{:02d}".format(fence_count),
                fence_mesh,
                unreal.Vector(base_x, base_y, 120.0),
                unreal.Vector(1500.0, 75.0, 240.0),
                None,
                True,
                yaw,
            )
        else:
            actor = None
        if actor:
            fence_count += 1

    # Loading bays / dock lips add silhouette and scale to warehouse fronts.
    dark = mats["dark"] or mats["sidewalk"]
    for i, x in enumerate((-31800.0, -29400.0, -27000.0)):
        cube(
            PREFIX + "Industrial_LoadingDock_{:02d}".format(i),
            unreal.Vector(x, -24600.0, 85.0),
            unreal.Vector(1500.0, 500.0, 150.0),
            dark,
            True,
            False,
        )

    log("M11: industrial visible fences={} loading_docks=3".format(fence_count))


def build_park_edge(mats):
    dark = mats["dark"] or mats["sidewalk"]

    # Main civic/park plaza.
    cube(
        PREFIX + "ParkEdge_Plaza",
        unreal.Vector(24000.0, -24000.0, 5.0),
        unreal.Vector(8500.0, 8500.0, 10.0),
        mats["sidewalk"],
        True,
        True,
    )

    # Low planters / seating bars.
    for i, (x, y, sx, sy) in enumerate((
        (21000.0, -24000.0, 1800.0, 220.0),
        (27000.0, -24000.0, 1800.0, 220.0),
        (24000.0, -21000.0, 220.0, 1800.0),
        (24000.0, -27000.0, 220.0, 1800.0),
    )):
        cube(
            PREFIX + "ParkEdge_Planter_{:02d}".format(i),
            unreal.Vector(x, y, 72.0),
            unreal.Vector(sx, sy, 110.0),
            dark,
            True,
            False,
        )

    bush_mesh = find_asset("/Game/Uniblocks/Meshes", "SM_UB_Bush_x150")
    bush_count = 0
    if bush_mesh:
        for x, y in (
            (21000.0, -23500.0), (21000.0, -24500.0),
            (27000.0, -23500.0), (27000.0, -24500.0),
            (23500.0, -21000.0), (24500.0, -21000.0),
            (23500.0, -27000.0), (24500.0, -27000.0),
        ):
            actor = actor_subsystem().spawn_actor_from_class(
                unreal.StaticMeshActor,
                unreal.Vector(x, y, 95.0),
                unreal.Rotator(0.0, float((bush_count * 37) % 360), 0.0),
            )
            if actor:
                set_label(actor, PREFIX + "ParkEdge_Bush_{:02d}".format(bush_count))
                set_tags(actor, "OWNoPopulationSpawn")
                actor.static_mesh_component.set_static_mesh(bush_mesh)
                actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
                actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                actor.set_actor_scale3d(unreal.Vector(0.75, 0.75, 0.75))
                bush_count += 1
    else:
        warn("M11: optional SM_UB_Bush_x150 not found; park remains hardscape")

    # Large parking area beside the plaza.
    parking_surface = cube(
        PREFIX + "ParkEdge_ParkingSurface",
        unreal.Vector(36000.0, -24000.0, 4.0),
        unreal.Vector(8800.0, 7600.0, 8.0),
        mats["road"],
        True,
        False,
    )
    set_tags(parking_surface, "OWRoadSurface", "OWNoPopulationSpawn")

    marking = mats["marking"] or mats["sidewalk"]
    marks = 0
    for row_y in (-26500.0, -24000.0, -21500.0):
        for x in range(33000, 39001, 1000):
            cube(
                PREFIX + "ParkingMark_{:03d}".format(marks),
                unreal.Vector(float(x), row_y, 8.8),
                unreal.Vector(14.0, 900.0, 1.0),
                marking,
                False,
                False,
            )
            marks += 1

    log("M11: park bushes={} parking_marks={}".format(bush_count, marks))



def build_secondary_parking(mats):
    """Add two smaller believable parking pockets outside the civic lot."""
    road = mats["road"]
    marking = mats["marking"] or mats["sidewalk"]
    dark = mats["dark"] or mats["sidewalk"]

    lots = (
        ("Industrial", -30000.0, -34000.0, 5600.0, 1700.0, 8),
        ("Modern", 30000.0, 9800.0, 5600.0, 1700.0, 8),
    )

    mark_count = 0
    stop_count = 0

    for lot_index, (district, x, y, sx, sy, spaces) in enumerate(lots):
        surface = cube(
            PREFIX + "ParkingPocket_{}_Surface".format(district),
            unreal.Vector(x, y, 12.0),
            unreal.Vector(sx, sy, 4.0),
            road,
            True,
            False,
        )
        set_tags(surface, "OWRoadSurface", "OWNoPopulationSpawn")

        start_x = x - (spaces - 1) * 620.0 * 0.5
        for i in range(spaces):
            px = start_x + i * 620.0
            cube(
                PREFIX + "ParkingBay_{:03d}".format(mark_count),
                unreal.Vector(px, y, 15.0),
                unreal.Vector(14.0, 1180.0, 1.2),
                marking,
                False,
                False,
            )
            mark_count += 1

            cube(
                PREFIX + "WheelStop_{:03d}".format(stop_count),
                unreal.Vector(px, y - 610.0, 27.0),
                unreal.Vector(360.0, 54.0, 24.0),
                dark,
                False,
                False,
            )
            stop_count += 1

    log("M11: secondary parking bays={} wheel_stops={}".format(mark_count, stop_count))


def build_road_detail_pass(mats):
    """Improve intersection readability without changing driving collision."""
    marking = mats["marking"] or mats["sidewalk"]
    crosswalk_count = 0
    stop_count = 0

    # Four district-defining outer intersections get compact crosswalk pairs.
    for ix, iy in (
        (-24000.0, 24000.0),
        (24000.0, 24000.0),
        (-24000.0, -24000.0),
        (24000.0, -24000.0),
    ):
        for s in range(-3, 4):
            cube(
                PREFIX + "DistrictCrosswalk_{:03d}".format(crosswalk_count),
                unreal.Vector(ix + s * 92.0, iy + 610.0, 9.6),
                unreal.Vector(52.0, 360.0, 1.3),
                marking,
                False,
                False,
            )
            crosswalk_count += 1

    # Stop bars on selected approaches visually break the endless-grid look.
    for x, y, sx, sy in (
        (-24000.0, 23380.0, 720.0, 28.0),
        (24000.0, 23380.0, 720.0, 28.0),
        (-24000.0, -23380.0, 720.0, 28.0),
        (24000.0, -23380.0, 720.0, 28.0),
        (-23380.0, 24000.0, 28.0, 720.0),
        (23380.0, 24000.0, 28.0, 720.0),
        (-23380.0, -24000.0, 28.0, 720.0),
        (23380.0, -24000.0, 28.0, 720.0),
    ):
        cube(
            PREFIX + "StopBar_{:02d}".format(stop_count),
            unreal.Vector(x, y, 9.7),
            unreal.Vector(sx, sy, 1.3),
            marking,
            False,
            False,
        )
        stop_count += 1

    log("M11: district crosswalks={} stop_bars={}".format(crosswalk_count, stop_count))


def build_street_furniture(mats):
    """Small props restore human scale to wide roads and plazas."""
    dark = mats["dark"] or mats["sidewalk"]
    sidewalk = mats["sidewalk"] or mats["dark"]

    prop_count = 0

    # Benches: seat + back, concentrated around the park/civic space.
    for i, (x, y, yaw) in enumerate((
        (21400.0, -22000.0, 0.0),
        (26600.0, -22000.0, 0.0),
        (21400.0, -26000.0, 180.0),
        (26600.0, -26000.0, 180.0),
        (22500.0, -20500.0, 90.0),
        (25500.0, -20500.0, 90.0),
    )):
        cube(
            PREFIX + "StreetProp_BenchSeat_{:02d}".format(i),
            unreal.Vector(x, y, 74.0),
            unreal.Vector(420.0, 85.0, 38.0),
            dark,
            False,
            False,
            yaw,
        )
        cube(
            PREFIX + "StreetProp_BenchBack_{:02d}".format(i),
            unreal.Vector(x, y + 42.0, 142.0),
            unreal.Vector(420.0, 28.0, 150.0),
            dark,
            False,
            False,
            yaw,
        )
        prop_count += 2

    # Bollard groups protect plaza and parking entrances.
    bollard_index = 0
    for x, y in (
        (31800.0, -27800.0), (32600.0, -27800.0), (33400.0, -27800.0),
        (34200.0, -27800.0), (35000.0, -27800.0),
        (18200.0, -19600.0), (18200.0, -20400.0), (18200.0, -21200.0),
    ):
        cylinder(
            PREFIX + "StreetProp_Bollard_{:02d}".format(bollard_index),
            unreal.Vector(x, y, 62.0),
            24.0,
            124.0,
            dark,
            False,
        )
        bollard_index += 1
        prop_count += 1

    # Simple litter bins at high-use corners.
    for i, (x, y) in enumerate((
        (20500.0, -20500.0),
        (27500.0, -20500.0),
        (20500.0, -27500.0),
        (27500.0, -27500.0),
        (-14500.0, 14500.0),
        (14500.0, 14500.0),
    )):
        cylinder(
            PREFIX + "StreetProp_Bin_{:02d}".format(i),
            unreal.Vector(x, y, 62.0),
            70.0,
            124.0,
            dark,
            False,
        )
        prop_count += 1

    # Eight traffic/street sign silhouettes at district gateways.
    for i, (x, y, yaw) in enumerate((
        (-24600.0, 24600.0, 0.0),
        (24600.0, 24600.0, 180.0),
        (-24600.0, -24600.0, 0.0),
        (24600.0, -24600.0, 180.0),
        (-12600.0, 24600.0, 0.0),
        (12600.0, 24600.0, 180.0),
        (-12600.0, -24600.0, 0.0),
        (12600.0, -24600.0, 180.0),
    )):
        cylinder(
            PREFIX + "StreetProp_SignPole_{:02d}".format(i),
            unreal.Vector(x, y, 150.0),
            12.0,
            300.0,
            dark,
            False,
        )
        cube(
            PREFIX + "StreetProp_SignPlate_{:02d}".format(i),
            unreal.Vector(x, y, 275.0),
            unreal.Vector(145.0, 18.0, 92.0),
            sidewalk,
            False,
            False,
            yaw,
        )
        prop_count += 2

    log("M11: street furniture parts={}".format(prop_count))


def build_green_clusters(mats):
    """Group confirmed UNIBLOCKS bushes with planters for stronger vegetation reads."""
    bush_mesh = find_asset("/Game/Uniblocks/Meshes", "SM_UB_Bush_x150")
    if not bush_mesh:
        warn("M11: green clusters skipped; SM_UB_Bush_x150 unavailable")
        return

    dark = mats["dark"] or mats["sidewalk"]
    clusters = (
        (-34000.0, 15500.0), (-28500.0, 15500.0), (-22000.0, 15500.0),
        (-34000.0, 33500.0), (-26000.0, 33500.0), (-15000.0, 33500.0),
        (15500.0, 17500.0), (33500.0, 15500.0), (33500.0, 28500.0),
        (20000.0, -28500.0), (28000.0, -28500.0), (20000.0, -19500.0),
    )

    bush_count = 0
    for cluster_index, (cx, cy) in enumerate(clusters):
        cube(
            PREFIX + "StreetProp_Planter_{:02d}".format(cluster_index),
            unreal.Vector(cx, cy, 44.0),
            unreal.Vector(520.0, 520.0, 88.0),
            dark,
            False,
            False,
        )

        for ox, oy, scale in ((-150.0, -70.0, 0.56), (145.0, -45.0, 0.64), (10.0, 145.0, 0.52)):
            actor = actor_subsystem().spawn_actor_from_class(
                unreal.StaticMeshActor,
                unreal.Vector(cx + ox, cy + oy, 116.0),
                unreal.Rotator(0.0, float((bush_count * 43) % 360), 0.0),
            )
            if not actor:
                continue
            set_label(actor, PREFIX + "Env_GreenCluster_{:03d}".format(bush_count))
            set_tags(actor, "OWNoPopulationSpawn")
            actor.static_mesh_component.set_static_mesh(bush_mesh)
            actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
            actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            bush_count += 1

    log("M11: green cluster bushes={}".format(bush_count))


def build_skyline_landmarks(mats):
    """Edge landmarks with stepped silhouettes and real facade inserts."""
    backgrounds = mats["background"] or [mats["sidewalk"]]
    dark = mats["dark"] or mats["sidewalk"]

    sites = (
        ("EastGate", 42500.0, 30000.0, 2200.0, 1500.0, 5600.0, 180.0, -120.0),
        ("NorthGate", 30000.0, 42500.0, 1500.0, 2350.0, 7000.0, -160.0, 220.0),
        ("Corner", 42000.0, 42000.0, 1950.0, 1750.0, 8200.0, 210.0, -190.0),
    )

    parts = 0
    authored_windows = 0

    for index, (name, x, y, sx, sy, tower_h, upper_dx, upper_dy) in enumerate(sites):
        pad_size = 6200.0 if name != "Corner" else 5400.0
        cube(
            PREFIX + "Skyline_{}_Pad".format(name),
            unreal.Vector(x, y, -4.0),
            unreal.Vector(pad_size, pad_size, 12.0),
            mats["sidewalk"],
            True,
            False,
        )

        podium_h = 620.0 + index * 70.0
        cube(
            PREFIX + "Skyline_{}_Podium".format(name),
            unreal.Vector(x, y, podium_h * 0.5),
            unreal.Vector(sx * 1.62, sy * 1.58, podium_h),
            backgrounds[index % len(backgrounds)],
            True,
            False,
        )
        parts += 1

        lower_h = tower_h * 0.61
        upper_h = tower_h - lower_h

        cube(
            PREFIX + "Skyline_{}_Lower".format(name),
            unreal.Vector(x, y, podium_h + lower_h * 0.5),
            unreal.Vector(sx, sy, lower_h),
            backgrounds[(index + 1) % len(backgrounds)],
            True,
            False,
        )
        parts += 1

        upper_x = x + upper_dx
        upper_y = y + upper_dy
        upper_sx = sx * (0.68 + index * 0.035)
        upper_sy = sy * (0.72 - index * 0.025)

        cube(
            PREFIX + "Skyline_{}_Upper".format(name),
            unreal.Vector(upper_x, upper_y, podium_h + lower_h + upper_h * 0.5),
            unreal.Vector(upper_sx, upper_sy, upper_h),
            backgrounds[(index + 2) % len(backgrounds)],
            True,
            False,
        )
        parts += 1

        crown_h = 360.0 + index * 80.0
        cube(
            PREFIX + "Skyline_{}_Crown".format(name),
            unreal.Vector(
                upper_x,
                upper_y,
                podium_h + tower_h + crown_h * 0.5,
            ),
            unreal.Vector(upper_sx * 0.58, upper_sy * 0.58, crown_h),
            dark,
            False,
            False,
        )
        parts += 1

        window_mesh = (
            AUTHORED_PARTS["window_big"]
            if index != 1
            else AUTHORED_PARTS["window_mid"]
        )
        for row in range(3):
            z = podium_h + lower_h * (0.22 + row * 0.25)
            part = spawn_authored_part_sized(
                PREFIX + "AuthoredSkyline_Window_{}_{:02d}".format(name, row),
                window_mesh,
                unreal.Vector(x, y + sy * 0.5 + 24.0, z),
                unreal.Vector(max(700.0, sx * 0.62), 48.0, 360.0),
                0.0,
                False,
            )
            if part:
                authored_windows += 1

        cube(
            PREFIX + "Skyline_{}_RoofServiceA".format(name),
            unreal.Vector(
                upper_x + upper_sx * 0.18,
                upper_y - upper_sy * 0.14,
                podium_h + tower_h + crown_h + 105.0,
            ),
            unreal.Vector(360.0, 300.0, 210.0),
            dark,
            False,
            False,
        )
        cube(
            PREFIX + "Skyline_{}_RoofServiceB".format(name),
            unreal.Vector(
                upper_x - upper_sx * 0.19,
                upper_y + upper_sy * 0.16,
                podium_h + tower_h + crown_h + 72.0,
            ),
            unreal.Vector(250.0, 280.0, 145.0),
            dark,
            False,
            False,
        )
        parts += 2

    log(
        "M11: skyline landmark parts={} authored_windows={}".format(
            parts,
            authored_windows,
        )
    )


def add_outer_street_lights(mats):
    dark = mats["dark"] or mats["sidewalk"]
    lamp_mesh = unreal.load_asset(AUTHORED_PARTS["lamp_head"])
    positions = []

    for p in (-36000.0, -24000.0, -12000.0, 12000.0, 24000.0, 36000.0):
        positions.append((p + 700.0, -42000.0))
        positions.append((p - 700.0, 42000.0))
        positions.append((-42000.0, p - 700.0))
        positions.append((42000.0, p + 700.0))

    for index, (x, y) in enumerate(positions):
        cylinder(
            PREFIX + "StreetLight_{:02d}_Pole".format(index),
            unreal.Vector(x, y, 230.0),
            16.0,
            460.0,
            dark,
            False,
        )
        if lamp_mesh:
            spawn_mesh_sized(
                PREFIX + "StreetLight_{:02d}_AuthoredHead".format(index),
                lamp_mesh,
                unreal.Vector(x + 62.0, y, 455.0),
                unreal.Vector(130.0, 70.0, 58.0),
                None,
                False,
                0.0,
            )
        else:
            cube(
                PREFIX + "StreetLight_{:02d}_Head".format(index),
                unreal.Vector(x + 55.0, y, 455.0),
                unreal.Vector(110.0, 24.0, 18.0),
                dark,
                False,
                False,
            )

    log("M11: outer streetlights={}".format(len(positions)))


def disable_prefab_local_lights():
    classes = []
    for name in ("PointLightComponent", "SpotLightComponent", "RectLightComponent"):
        cls = getattr(unreal, name, None)
        if cls:
            classes.append(cls)

    disabled = 0
    for actor in actor_subsystem().get_all_level_actors():
        if not actor:
            continue
        for cls in classes:
            try:
                components = actor.get_components_by_class(cls)
            except Exception:
                components = []
            for component in components:
                if not component:
                    continue
                try:
                    component.set_visibility(False, True)
                except Exception:
                    pass
                try:
                    component.set_editor_property("intensity", 0.0)
                except Exception:
                    pass
                try:
                    component.set_editor_property("cast_shadows", False)
                except Exception:
                    pass
                disabled += 1

    log("M11: decorative local lights disabled={}".format(disabled))


def retag_core_pedestrian_surfaces():
    # M9 originally treated its roads and huge ground slab as generic
    # OWWalkableSpawn surfaces. That was acceptable for the small prototype,
    # but in free roam it lets pedestrians appear directly in driving lanes.
    # Retag only road/ground actors; keep SidewalkPad actors walkable.
    changed = 0
    for actor in actor_subsystem().get_all_level_actors():
        if not actor:
            continue

        label = actor.get_actor_label()

        if (
            label == "OW_CITY_Ground"
            or label.startswith("OW_CITY_Road_NS")
            or label.startswith("OW_CITY_Road_EW")
        ):
            set_tags(actor, "OWRoadSurface", "OWNoPopulationSpawn")
            changed += 1

    log("M11: core road/ground pedestrian spawn surfaces disabled={}".format(changed))


def verify_m10_preserved():
    labels = {
        actor.get_actor_label()
        for actor in actor_subsystem().get_all_level_actors()
        if actor
    }

    required = (
        "OW_M10_SportsCar",
        "OW_M10_SportsCarInteraction",
    )
    missing = [label for label in required if label not in labels]
    if missing:
        raise RuntimeError(
            "M11: M10 vehicle integration missing before save: {}".format(
                ", ".join(missing)
            )
        )


def save_map():
    saved = unreal.EditorAssetLibrary.save_asset(TARGET_MAP, only_if_is_dirty=False)
    if not saved:
        raise RuntimeError(
            "M11: failed to save map. Close every Unreal Editor instance and rerun."
        )


def main():
    ensure_dependencies()

    if not level_subsystem().load_level(TARGET_MAP):
        raise RuntimeError("M11: failed to load {}".format(TARGET_MAP))

    clear_generated()
    verify_m10_preserved()

    mats = load_materials()

    build_world_base(mats)
    retag_core_pedestrian_surfaces()
    add_lane_markings(mats)
    build_district_pads(mats)
    build_hero_prefabs()
    build_background_districts(mats)
    build_phase_c_landscaping(mats)
    build_industrial_dressing(mats)
    build_park_edge(mats)

    # Phase D: make the expanded grid read like a lived-in open-world district.
    build_secondary_parking(mats)
    build_road_detail_pass(mats)
    build_street_furniture(mats)
    build_green_clusters(mats)
    build_skyline_landmarks(mats)

    add_outer_street_lights(mats)
    disable_prefab_local_lights()

    verify_m10_preserved()
    save_map()

    log("M11: PHASE E AUTHORED-ASSET CITY PASS COMPLETE")
    log("M11: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
