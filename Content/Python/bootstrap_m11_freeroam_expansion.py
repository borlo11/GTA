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
                unreal.Vector(x, y, 8.0),
                unreal.Vector(size, size, 16.0),
                mats["sidewalk"],
                True,
                True,
            )
            count += 1

    log("M11: district pads={}".format(count))


def build_hero_prefabs():
    heroes = (
        ("Residential_Hero_Classic", "classic", -30000.0, 30000.0, 0.0),
        ("Residential_Hero_Art", "art", -18000.0, 18000.0, 180.0),
        ("Modern_Hero_Modern", "modern", 18000.0, 30000.0, 180.0),
        ("Modern_Hero_Future", "future", 30000.0, 18000.0, 0.0),
    )

    for label, prefab_key, x, y, yaw in heroes:
        spawn_prefab(
            PREFIX + label,
            PREFABS[prefab_key],
            unreal.Vector(x, y, 18.0),
            yaw,
        )

    log("M11: authored outer hero prefabs={}".format(len(heroes)))


def build_background_districts(mats):
    mesh = find_asset("/Game/Uniblocks/Meshes", "SM_UB_Block_scalable")
    if not mesh:
        raise RuntimeError("M11: SM_UB_Block_scalable missing")

    backgrounds = mats["background"] or [mats["sidewalk"]]
    hero_lots = {
        (-30000.0, 30000.0),
        (-18000.0, 18000.0),
        (18000.0, 30000.0),
        (30000.0, 18000.0),
    }

    count = 0
    for x in BLOCK_CENTERS:
        for y in BLOCK_CENTERS:
            if abs(x) < 10000.0 and abs(y) < 10000.0:
                continue
            if (x, y) in hero_lots:
                continue

            district = district_for(x, y)

            # South-east is intentionally open for park/plaza/parking.
            if district == "ParkEdge":
                continue

            material = backgrounds[count % len(backgrounds)]

            if district == "Residential":
                target = unreal.Vector(
                    2500.0 + (count % 2) * 500.0,
                    2100.0,
                    700.0 + (count % 3) * 180.0,
                )
            elif district == "Modern":
                target = unreal.Vector(
                    2600.0,
                    2400.0,
                    1200.0 + (count % 4) * 260.0,
                )
            else:
                # Industrial: wide, deliberately low warehouses.
                target = unreal.Vector(
                    5200.0,
                    3300.0,
                    650.0 + (count % 2) * 160.0,
                )

            actor = spawn_mesh_sized(
                PREFIX + "{}_Background_{:02d}".format(district, count),
                mesh,
                unreal.Vector(x, y, 18.0 + target.z * 0.5),
                target,
                material,
                True,
                0.0 if count % 2 == 0 else 90.0,
            )
            if not actor:
                raise RuntimeError("M11: failed background actor {}".format(count))
            count += 1

    log("M11: lightweight district buildings={}".format(count))


def spawn_optional_visible_mesh(label, asset_name, location, scale, yaw=0.0):
    mesh = find_asset("/Game/Uniblocks/Meshes", asset_name)
    if not mesh:
        warn("M11: optional mesh unavailable: {}".format(asset_name))
        return None

    actor = actor_subsystem().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    if not actor:
        return None

    set_label(actor, label)
    set_tags(actor, "OWNoPopulationSpawn")
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
    actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    actor.set_actor_scale3d(scale)
    return actor


def build_industrial_dressing(mats):
    # Fence/gate parts are confirmed by the M11 inventory and come from visible
    # Parts/, not Colliders/.
    fence_mesh_name = "SM_UBP_Gate_sgmtFenceBig_01"
    fence_count = 0

    for base_x, base_y, yaw in (
        (-33000.0, -18000.0, 0.0),
        (-27000.0, -18000.0, 0.0),
        (-21000.0, -30000.0, 90.0),
        (-21000.0, -24000.0, 90.0),
        (-33000.0, -30000.0, 0.0),
        (-27000.0, -30000.0, 0.0),
    ):
        actor = spawn_optional_visible_mesh(
            PREFIX + "Industrial_Fence_{:02d}".format(fence_count),
            fence_mesh_name,
            unreal.Vector(base_x, base_y, 35.0),
            unreal.Vector(1.0, 1.0, 1.0),
            yaw,
        )
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
        unreal.Vector(24000.0, -24000.0, 18.0),
        unreal.Vector(8500.0, 8500.0, 20.0),
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
        unreal.Vector(36000.0, -24000.0, 14.0),
        unreal.Vector(8800.0, 7600.0, 10.0),
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
                unreal.Vector(float(x), row_y, 20.0),
                unreal.Vector(14.0, 900.0, 1.0),
                marking,
                False,
                False,
            )
            marks += 1

    log("M11: park bushes={} parking_marks={}".format(bush_count, marks))


def add_outer_street_lights(mats):
    dark = mats["dark"] or mats["sidewalk"]
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
    build_industrial_dressing(mats)
    build_park_edge(mats)
    add_outer_street_lights(mats)
    disable_prefab_local_lights()

    verify_m10_preserved()
    save_map()

    log("M11: PHASE B FREE-ROAM EXPANSION COMPLETE")
    log("M11: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
