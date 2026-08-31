# bootstrap_m9_city_overhaul.py
# M9 visual/city overhaul — authored UNIBLOCKS prefab pass for UE 5.8.
#
# Rebuilds OW_LightweightCity using the real UNIBLOCKS FREE prefab World assets
# discovered locally, instead of stretching SM_UB_Block_scalable into fake towers.
#
# Preserves M5-M8 gameplay coordinates and remains idempotent:
# only actors whose label starts with OW_CITY_ are replaced.

import unreal

TARGET_MAP = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_CITY_"

UNIBLOCKS_ROOT = "/Game/Uniblocks"

PREFAB_WORLDS = (
    "/Game/Uniblocks/Maps/LI_prefab_Art_house_elevated_v1",
    "/Game/Uniblocks/Maps/LI_prefab_Classic_house_v1",
    "/Game/Uniblocks/Maps/LI_prefab_Futuristic_cabin_v1",
    "/Game/Uniblocks/Maps/LI_prefab_Modern_house2_v1",
)

CUBE = "/Engine/BasicShapes/Cube.Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder.Cylinder"

GROUND_SIZE = 17000.0
ROAD_Z = 5.0
MAIN_ROAD_WIDTH = 1300.0
SECONDARY_ROAD_WIDTH = 900.0
ROAD_CENTERS = (-4200.0, 0.0, 4200.0)
BLOCK_CENTERS = (-6100.0, -2100.0, 2100.0, 6100.0)
LOT_SIZE = 2860.0
LOT_HEIGHT = 12.0

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


def set_label(actor, name):
    actor.set_actor_label(name)
    return actor


def set_tags(actor, *tags):
    try:
        actor.set_editor_property("tags", [unreal.Name(tag) for tag in tags])
    except Exception:
        pass


def ensure_map():
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not level_subsystem().load_level(TARGET_MAP):
            raise RuntimeError("M9: could not load {}".format(TARGET_MAP))
        return

    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/Maps"):
        unreal.EditorAssetLibrary.make_directory("/Game/Maps")

    if not level_subsystem().new_level(TARGET_MAP, False):
        raise RuntimeError("M9: could not create {}".format(TARGET_MAP))


def clear_generated():
    removed = 0
    for actor in list(actor_subsystem().get_all_level_actors()):
        if actor and actor.get_actor_label().startswith(PREFIX):
            actor_subsystem().destroy_actor(actor)
            removed += 1

    log("M9: removed {} generated actors".format(removed))


def configure_world():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    settings = world.get_world_settings() if world else None
    if not settings:
        raise RuntimeError("M9: WorldSettings unavailable")

    game_mode = unreal.load_class(None, "/Script/OWGame.OWGameGameMode")
    if not game_mode:
        raise RuntimeError("M9: OWGameGameMode unavailable; build C++ first")

    settings.set_editor_property("default_game_mode", game_mode)

    try:
        settings.set_editor_property("force_no_precomputed_lighting", True)
    except Exception as exc:
        warn("M9: ForceNoPrecomputedLighting unavailable: {}".format(exc))


def spawn_mesh(name, mesh_path, location, scale, material=None, collision=True, walkable=False):
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        raise RuntimeError("M9: missing mesh {}".format(mesh_path))

    actor = actor_subsystem().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(actor, name)

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


def cube(name, location, size, material=None, collision=True, walkable=False):
    return spawn_mesh(
        name,
        CUBE,
        location,
        unreal.Vector(size.x / 100.0, size.y / 100.0, size.z / 100.0),
        material,
        collision,
        walkable,
    )


def cylinder(name, location, diameter, height, material=None, collision=False):
    return spawn_mesh(
        name,
        CYLINDER,
        location,
        unreal.Vector(diameter / 100.0, diameter / 100.0, height / 100.0),
        material,
        collision,
        False,
    )


def load_materials():
    root = "/Game/Uniblocks/Materials"
    return {
        "road": first_asset(root, ROAD_MATERIAL_NAMES),
        "sidewalk": first_asset(root, SIDEWALK_MATERIAL_NAMES),
        "marking": first_asset(root, MARKING_MATERIAL_NAMES),
        "dark": first_asset(root, DARK_MATERIAL_NAMES),
    }


def validate_prefab_assets():
    missing = []
    for path in PREFAB_WORLDS:
        asset = unreal.load_asset(path)
        if not asset:
            missing.append(path)

    if missing:
        raise RuntimeError(
            "M9: required prefab worlds missing: {}".format(", ".join(missing))
        )

    if not hasattr(unreal, "LevelInstance"):
        raise RuntimeError("M9: unreal.LevelInstance is unavailable in this editor build")


def spawn_prefab(name, world_path, location, yaw):
    world_asset = unreal.load_asset(world_path)
    if not world_asset:
        raise RuntimeError("M9: prefab world missing: {}".format(world_path))

    instance = actor_subsystem().spawn_actor_from_class(
        unreal.LevelInstance,
        location,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    if not instance:
        raise RuntimeError("M9: failed to spawn LevelInstance for {}".format(world_path))

    set_label(instance, name)
    set_tags(instance, "OWNoPopulationSpawn")

    if not instance.set_world_asset(world_asset):
        actor_subsystem().destroy_actor(instance)
        raise RuntimeError("M9: LevelInstance rejected {}".format(world_path))

    try:
        instance.load_level_instance()
    except Exception as exc:
        warn("M9: load_level_instance warning for {}: {}".format(world_path, exc))

    return instance


def build_ground_and_grid(mats):
    cube(
        PREFIX + "Ground",
        unreal.Vector(0.0, 0.0, -60.0),
        unreal.Vector(GROUND_SIZE, GROUND_SIZE, 110.0),
        mats["sidewalk"],
        True,
        True,
    )

    for index, x in enumerate(ROAD_CENTERS):
        width = MAIN_ROAD_WIDTH if abs(x) < 1.0 else SECONDARY_ROAD_WIDTH
        cube(
            PREFIX + "Road_NS_{:02d}".format(index),
            unreal.Vector(x, 0.0, ROAD_Z),
            unreal.Vector(width, GROUND_SIZE, 10.0),
            mats["road"],
            True,
            True,
        )

    for index, y in enumerate(ROAD_CENTERS):
        width = MAIN_ROAD_WIDTH if abs(y) < 1.0 else SECONDARY_ROAD_WIDTH
        cube(
            PREFIX + "Road_EW_{:02d}".format(index),
            unreal.Vector(0.0, y, ROAD_Z),
            unreal.Vector(GROUND_SIZE, width, 10.0),
            mats["road"],
            True,
            True,
        )

    # Legacy compatibility labels used by earlier validators.
    cube(
        PREFIX + "Road_NS",
        unreal.Vector(0.0, 0.0, ROAD_Z + 0.1),
        unreal.Vector(MAIN_ROAD_WIDTH, GROUND_SIZE, 0.5),
        mats["road"],
        False,
        False,
    )
    cube(
        PREFIX + "Road_EW",
        unreal.Vector(0.0, 0.0, ROAD_Z + 0.1),
        unreal.Vector(GROUND_SIZE, MAIN_ROAD_WIDTH, 0.5),
        mats["road"],
        False,
        False,
    )

    for ix, x in enumerate(BLOCK_CENTERS):
        for iy, y in enumerate(BLOCK_CENTERS):
            cube(
                PREFIX + "SidewalkPad_{:02d}_{:02d}".format(ix, iy),
                unreal.Vector(x, y, LOT_HEIGHT * 0.5),
                unreal.Vector(LOT_SIZE, LOT_SIZE, LOT_HEIGHT),
                mats["sidewalk"],
                True,
                True,
            )


def add_road_markings(mats):
    white = mats["marking"]
    z = 10.6
    thickness = 0.8

    for road_index, x in enumerate(ROAD_CENTERS):
        lane_offset = 285.0 if abs(x) < 1.0 else 190.0
        for side in (-1.0, 1.0):
            y = -7700.0
            i = 0
            while y <= 7700.0:
                cube(
                    PREFIX + "RoadMark_NS_{}_{}_{}".format(road_index, int(side > 0), i),
                    unreal.Vector(x + side * lane_offset, y, z),
                    unreal.Vector(7.0, 260.0, thickness),
                    white,
                    False,
                    False,
                )
                y += 600.0
                i += 1

    for road_index, y in enumerate(ROAD_CENTERS):
        lane_offset = 285.0 if abs(y) < 1.0 else 190.0
        for side in (-1.0, 1.0):
            x = -7700.0
            i = 0
            while x <= 7700.0:
                cube(
                    PREFIX + "RoadMark_EW_{}_{}_{}".format(road_index, int(side > 0), i),
                    unreal.Vector(x, y + side * lane_offset, z),
                    unreal.Vector(260.0, 7.0, thickness),
                    white,
                    False,
                    False,
                )
                x += 600.0
                i += 1

    crosswalks = (
        (0.0, -760.0, "H"),
        (0.0, 760.0, "H"),
        (-760.0, 0.0, "V"),
        (760.0, 0.0, "V"),
    )

    for cw, (cx, cy, axis) in enumerate(crosswalks):
        for stripe in range(6):
            offset = (stripe - 2.5) * 72.0

            if axis == "H":
                location = unreal.Vector(cx + offset, cy, z + 0.05)
                size = unreal.Vector(38.0, 420.0, thickness)
            else:
                location = unreal.Vector(cx, cy + offset, z + 0.05)
                size = unreal.Vector(420.0, 38.0, thickness)

            cube(
                PREFIX + "Crosswalk_{}_{}".format(cw, stripe),
                location,
                size,
                white,
                False,
                False,
            )


def build_prefab_district(mats):
    # Two intentionally open corner plazas keep sightlines and mission driving readable.
    plaza_lots = {(0, 3), (3, 0)}

    # Slight offsets/rotations break repetition while leaving each authored prefab at 1:1 scale.
    offsets = (
        (0.0, 0.0, 0.0),
        (170.0, -120.0, 90.0),
        (-140.0, 120.0, 180.0),
        (110.0, 150.0, 270.0),
    )

    prefab_index = 0

    for ix, x in enumerate(BLOCK_CENTERS):
        for iy, y in enumerate(BLOCK_CENTERS):
            if (ix, iy) in plaza_lots:
                build_plaza(ix, iy, x, y, mats)
                continue

            world_path = PREFAB_WORLDS[prefab_index % len(PREFAB_WORLDS)]
            ox, oy, yaw = offsets[(ix + iy + prefab_index) % len(offsets)]

            spawn_prefab(
                PREFIX + "Building_{:02d}_Prefab".format(prefab_index + 1),
                world_path,
                unreal.Vector(x + ox, y + oy, LOT_HEIGHT),
                yaw,
            )

            prefab_index += 1


def build_plaza(ix, iy, x, y, mats):
    dark = mats["dark"] or mats["sidewalk"]

    for edge, (ox, oy, sx, sy) in enumerate((
        (-780.0, 0.0, 100.0, 1000.0),
        (780.0, 0.0, 100.0, 1000.0),
        (0.0, -780.0, 1000.0, 100.0),
        (0.0, 780.0, 1000.0, 100.0),
    )):
        cube(
            PREFIX + "UrbanProp_Plaza_{}_{}_{}".format(ix, iy, edge),
            unreal.Vector(x + ox, y + oy, LOT_HEIGHT + 22.0),
            unreal.Vector(sx, sy, 44.0),
            dark,
            True,
            False,
        )

    cylinder(
        PREFIX + "UrbanProp_PlazaCenter_{}_{}".format(ix, iy),
        unreal.Vector(x, y, LOT_HEIGHT + 70.0),
        110.0,
        140.0,
        dark,
        False,
    )


def add_street_furniture(mats):
    dark = mats["dark"] or mats["sidewalk"]

    positions = (
        (-760.0, -5200.0), (760.0, -3500.0),
        (-760.0, -1800.0), (760.0, 0.0),
        (-760.0, 1800.0), (760.0, 3500.0),
        (-760.0, 5200.0),
        (-5200.0, 760.0), (-3500.0, -760.0),
        (-1800.0, 760.0), (1800.0, -760.0),
        (3500.0, 760.0), (5200.0, -760.0),
    )

    for index, (x, y) in enumerate(positions):
        cylinder(
            PREFIX + "StreetLight_{:02d}_Pole".format(index),
            unreal.Vector(x, y, 215.0),
            14.0,
            430.0,
            dark,
            False,
        )
        cube(
            PREFIX + "StreetLight_{:02d}_Head".format(index),
            unreal.Vector(x + 45.0, y, 430.0),
            unreal.Vector(90.0, 22.0, 18.0),
            dark,
            False,
            False,
        )


def setup_lighting():
    subsystem = actor_subsystem()

    sun = subsystem.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0.0, 0.0, 4500.0),
        unreal.Rotator(-42.0, -28.0, 0.0),
    )
    set_label(sun, PREFIX + "Sun")

    try:
        component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_editor_property("intensity", 3.2)
        component.set_editor_property("atmosphere_sun_light", True)
        component.set_editor_property("cast_shadows", True)
        component.set_light_color(unreal.LinearColor(1.0, 0.94, 0.88, 1.0))
    except Exception as exc:
        warn("M9: sun warning: {}".format(exc))

    sky = subsystem.spawn_actor_from_class(
        unreal.SkyAtmosphere,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(sky, PREFIX + "SkyAtmosphere")

    skylight = subsystem.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(0.0, 0.0, 800.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(skylight, PREFIX + "SkyLight")

    try:
        component = skylight.get_component_by_class(unreal.SkyLightComponent)
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_editor_property("real_time_capture", True)
        component.set_editor_property("intensity", 0.55)
    except Exception as exc:
        warn("M9: skylight warning: {}".format(exc))

    fog = subsystem.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(fog, PREFIX + "Fog")

    try:
        component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        component.set_editor_property("fog_density", 0.003)
        component.set_editor_property("fog_height_falloff", 0.30)
    except Exception:
        pass

    try:
        cloud = subsystem.spawn_actor_from_class(
            unreal.VolumetricCloud,
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        set_label(cloud, PREFIX + "VolumetricCloud")
    except Exception:
        pass


def setup_gameplay():
    start = actor_subsystem().spawn_actor_from_class(
        unreal.PlayerStart,
        unreal.Vector(-260.0, -2600.0, 120.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(start, PREFIX + "PlayerStart")

    vehicle_class = unreal.load_class(None, "/Script/OWGame.OWPrototypeVehicle")
    if not vehicle_class:
        raise RuntimeError("M9: OWPrototypeVehicle unavailable")

    vehicle = actor_subsystem().spawn_actor_from_class(
        vehicle_class,
        unreal.Vector(280.0, -2450.0, 100.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(vehicle, PREFIX + "PrototypeVehicle")


def save_level():
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("M9: saved {}".format(TARGET_MAP))


def main():
    if not unreal.EditorAssetLibrary.does_directory_exist(UNIBLOCKS_ROOT):
        raise RuntimeError("M9: UNIBLOCKS FREE is missing at /Game/Uniblocks")

    ensure_map()
    clear_generated()
    configure_world()
    validate_prefab_assets()

    mats = load_materials()

    build_ground_and_grid(mats)
    add_road_markings(mats)
    build_prefab_district(mats)
    add_street_furniture(mats)
    setup_lighting()
    setup_gameplay()

    save_level()

    log("M9: AUTHORED PREFAB CITY COMPLETE")
    log("M9: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
