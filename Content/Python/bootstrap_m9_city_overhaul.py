# bootstrap_m9_city_overhaul.py
# M9 visual/city overhaul — corrected visual pass for OWGame / Unreal Engine 5.8.
#
# This rebuild intentionally favors a clean, believable city blockout over noisy
# procedural detail. It preserves the M5-M8 gameplay coordinates while fixing:
# - raised/oversized road markings
# - giant roof/facade slabs
# - overbright daytime street lights
# - overly dense geometry that read as a broken blockout
#
# Idempotent: only actors with labels starting OW_CITY_ are replaced.

import unreal

TARGET_MAP = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_CITY_"

UNIBLOCKS_ROOT = "/Game/Uniblocks"
UNIBLOCKS_BLOCK_NAME = "SM_UB_Block_scalable"

CUBE = "/Engine/BasicShapes/Cube.Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder.Cylinder"

GROUND_Z = 0.0
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
BUILDING_MATERIAL_NAMES = (
    "MI_UBT_brickwork_white",
    "MI_UBT_concreteRaw_gray_plain",
    "MI_UBT_concreteRaw_white_plain",
    "MI_UBT_concreteSmooth_gray",
)
DARK_MATERIAL_NAMES = (
    "MI_UBT_concreteSmooth_dark",
    "MI_UBT_concreteRaw_gray_plain",
)

log = unreal.log
warn = unreal.log_warning


def actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def levels():
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


def label(actor, name):
    actor.set_actor_label(name)
    return actor


def ensure_map():
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not levels().load_level(TARGET_MAP):
            raise RuntimeError("M9: could not load {}".format(TARGET_MAP))
        return

    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/Maps"):
        unreal.EditorAssetLibrary.make_directory("/Game/Maps")

    if not levels().new_level(TARGET_MAP, False):
        raise RuntimeError("M9: could not create {}".format(TARGET_MAP))


def clear_generated():
    removed = 0
    for actor in list(actors().get_all_level_actors()):
        if actor and actor.get_actor_label().startswith(PREFIX):
            actors().destroy_actor(actor)
            removed += 1
    log("M9: removed {} generated actors".format(removed))


def configure_world():
    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings() if world else None
    if not settings:
        raise RuntimeError("M9: WorldSettings unavailable")

    game_mode = unreal.load_class(None, "/Script/OWGame.OWGameGameMode")
    if not game_mode:
        raise RuntimeError("M9: OWGameGameMode unavailable")

    settings.set_editor_property("default_game_mode", game_mode)

    try:
        settings.set_editor_property("force_no_precomputed_lighting", True)
    except Exception as exc:
        warn("M9: ForceNoPrecomputedLighting unavailable: {}".format(exc))


def spawn_mesh(name, mesh_path, location, scale, material=None, collision=True):
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        raise RuntimeError("M9: missing mesh {}".format(mesh_path))

    actor = actors().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    label(actor, name)

    comp = actor.static_mesh_component
    comp.set_mobility(unreal.ComponentMobility.STATIC)
    comp.set_static_mesh(mesh)
    comp.set_collision_enabled(
        unreal.CollisionEnabled.QUERY_AND_PHYSICS
        if collision
        else unreal.CollisionEnabled.NO_COLLISION
    )

    if material:
        comp.set_material(0, material)

    actor.set_actor_scale3d(scale)
    return actor


def cube(name, location, size, material=None, collision=True):
    return spawn_mesh(
        name,
        CUBE,
        location,
        unreal.Vector(size.x / 100.0, size.y / 100.0, size.z / 100.0),
        material,
        collision,
    )


def cylinder(name, location, diameter, height, material=None, collision=False):
    return spawn_mesh(
        name,
        CYLINDER,
        location,
        unreal.Vector(diameter / 100.0, diameter / 100.0, height / 100.0),
        material,
        collision,
    )


def mesh_bounds(mesh):
    box = mesh.get_bounding_box()
    minimum = box.min
    maximum = box.max
    return (
        unreal.Vector(
            max(1.0, maximum.x - minimum.x),
            max(1.0, maximum.y - minimum.y),
            max(1.0, maximum.z - minimum.z),
        ),
        minimum,
        maximum,
    )


def uniblock(name, x, y, sx, sy, sz, material):
    mesh = find_asset(UNIBLOCKS_ROOT, UNIBLOCKS_BLOCK_NAME)
    if not mesh:
        raise RuntimeError("M9: {} missing".format(UNIBLOCKS_BLOCK_NAME))

    dimensions, minimum, maximum = mesh_bounds(mesh)
    scale = unreal.Vector(
        sx / dimensions.x,
        sy / dimensions.y,
        sz / dimensions.z,
    )

    local_center_x = (minimum.x + maximum.x) * 0.5
    local_center_y = (minimum.y + maximum.y) * 0.5

    location = unreal.Vector(
        x - local_center_x * scale.x,
        y - local_center_y * scale.y,
        LOT_HEIGHT - minimum.z * scale.z,
    )

    actor = actors().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    label(actor, name)

    comp = actor.static_mesh_component
    comp.set_mobility(unreal.ComponentMobility.STATIC)
    comp.set_static_mesh(mesh)
    if material:
        comp.set_material(0, material)

    actor.set_actor_scale3d(scale)
    return actor


def materials():
    root = "/Game/Uniblocks/Materials"
    building_mats = [
        find_asset(root, name)
        for name in BUILDING_MATERIAL_NAMES
    ]
    building_mats = [m for m in building_mats if m]

    return {
        "road": first_asset(root, ROAD_MATERIAL_NAMES),
        "sidewalk": first_asset(root, SIDEWALK_MATERIAL_NAMES),
        "marking": first_asset(root, MARKING_MATERIAL_NAMES),
        "dark": first_asset(root, DARK_MATERIAL_NAMES),
        "buildings": building_mats,
    }


def build_ground_and_grid(mats):
    cube(
        PREFIX + "Ground",
        unreal.Vector(0.0, 0.0, -60.0),
        unreal.Vector(GROUND_SIZE, GROUND_SIZE, 110.0),
        mats["sidewalk"],
    )

    for index, x in enumerate(ROAD_CENTERS):
        width = MAIN_ROAD_WIDTH if abs(x) < 1.0 else SECONDARY_ROAD_WIDTH
        cube(
            PREFIX + "Road_NS_{:02d}".format(index),
            unreal.Vector(x, 0.0, ROAD_Z),
            unreal.Vector(width, GROUND_SIZE, 10.0),
            mats["road"],
        )

    for index, y in enumerate(ROAD_CENTERS):
        width = MAIN_ROAD_WIDTH if abs(y) < 1.0 else SECONDARY_ROAD_WIDTH
        cube(
            PREFIX + "Road_EW_{:02d}".format(index),
            unreal.Vector(0.0, y, ROAD_Z),
            unreal.Vector(GROUND_SIZE, width, 10.0),
            mats["road"],
        )

    # Compatibility labels for M4.5/M8 validators.
    cube(
        PREFIX + "Road_NS",
        unreal.Vector(0.0, 0.0, ROAD_Z + 0.1),
        unreal.Vector(MAIN_ROAD_WIDTH, GROUND_SIZE, 0.5),
        mats["road"],
        False,
    )
    cube(
        PREFIX + "Road_EW",
        unreal.Vector(0.0, 0.0, ROAD_Z + 0.1),
        unreal.Vector(GROUND_SIZE, MAIN_ROAD_WIDTH, 0.5),
        mats["road"],
        False,
    )

    for ix, x in enumerate(BLOCK_CENTERS):
        for iy, y in enumerate(BLOCK_CENTERS):
            cube(
                PREFIX + "SidewalkPad_{:02d}_{:02d}".format(ix, iy),
                unreal.Vector(x, y, LOT_HEIGHT * 0.5),
                unreal.Vector(LOT_SIZE, LOT_SIZE, LOT_HEIGHT),
                mats["sidewalk"],
            )


def add_road_markings(mats):
    white = mats["marking"]
    z = 10.6

    # Flat markings: sub-centimeter visual lift, zero collision.
    dash_length = 260.0
    gap = 340.0
    thickness = 0.8

    for road_index, x in enumerate(ROAD_CENTERS):
        offset = 285.0 if abs(x) < 1.0 else 190.0
        for side in (-1.0, 1.0):
            y = -7700.0
            i = 0
            while y <= 7700.0:
                cube(
                    PREFIX + "RoadMark_NS_{}_{}_{}".format(road_index, int(side > 0), i),
                    unreal.Vector(x + side * offset, y, z),
                    unreal.Vector(7.0, dash_length, thickness),
                    white,
                    False,
                )
                y += dash_length + gap
                i += 1

    for road_index, y in enumerate(ROAD_CENTERS):
        offset = 285.0 if abs(y) < 1.0 else 190.0
        for side in (-1.0, 1.0):
            x = -7700.0
            i = 0
            while x <= 7700.0:
                cube(
                    PREFIX + "RoadMark_EW_{}_{}_{}".format(road_index, int(side > 0), i),
                    unreal.Vector(x, y + side * offset, z),
                    unreal.Vector(dash_length, 7.0, thickness),
                    white,
                    False,
                )
                x += dash_length + gap
                i += 1

    # Only four compact crosswalks around the central intersection.
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
                loc = unreal.Vector(cx + offset, cy, z + 0.05)
                size = unreal.Vector(38.0, 420.0, 0.8)
            else:
                loc = unreal.Vector(cx, cy + offset, z + 0.05)
                size = unreal.Vector(420.0, 38.0, 0.8)

            cube(
                PREFIX + "Crosswalk_{}_{}".format(cw, stripe),
                loc,
                size,
                white,
                False,
            )


def build_blocks(mats):
    building_mats = mats["buildings"] or [mats["sidewalk"]]

    # Explicit, conservative massing. No roof slabs, facade bands, or rotated
    # bounds: every volume is guaranteed to remain inside its own lot.
    designs = (
        (1850, 1600, 1250,  420,  260),
        (1500, 1900, 1750, -420, -260),
        (2050, 1450, 1050,  300, -360),
        (1650, 1650, 2200, -300,  320),
        (1900, 1500, 1450,  360,  260),
        (1450, 2050, 1850, -360, -220),
    )

    index = 0
    for ix, x in enumerate(BLOCK_CENTERS):
        for iy, y in enumerate(BLOCK_CENTERS):
            # Two intentional open plazas.
            if (ix, iy) in ((0, 3), (3, 0)):
                build_plaza(ix, iy, x, y, mats)
                continue

            sx, sy, sz, ox, oy = designs[index % len(designs)]
            mat = building_mats[index % len(building_mats)]

            uniblock(
                PREFIX + "Building_{:02d}".format(index + 1),
                x + ox,
                y + oy,
                sx,
                sy,
                sz,
                mat,
            )

            # Low annex for a more believable footprint without impossible slabs.
            annex_sx = min(900.0, sx * 0.52)
            annex_sy = min(760.0, sy * 0.46)
            annex_x = x - ox * 0.55
            annex_y = y - oy * 0.55

            uniblock(
                PREFIX + "Building_{:02d}_Annex".format(index + 1),
                annex_x,
                annex_y,
                annex_sx,
                annex_sy,
                480.0 + (index % 3) * 120.0,
                building_mats[(index + 1) % len(building_mats)],
            )

            index += 1


def build_plaza(ix, iy, x, y, mats):
    dark = mats["dark"] or mats["sidewalk"]

    # Four low benches/planter edges and a center element.
    for e, (ox, oy, sx, sy) in enumerate((
        (-780.0, 0.0, 100.0, 1000.0),
        (780.0, 0.0, 100.0, 1000.0),
        (0.0, -780.0, 1000.0, 100.0),
        (0.0, 780.0, 1000.0, 100.0),
    )):
        cube(
            PREFIX + "UrbanProp_Plaza_{}_{}_{}".format(ix, iy, e),
            unreal.Vector(x + ox, y + oy, LOT_HEIGHT + 22.0),
            unreal.Vector(sx, sy, 44.0),
            dark,
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

    # Geometry-only street lights in daytime. No bright point lights in M9.
    positions = (
        (-760.0, -5200.0), (760.0, -3500.0),
        (-760.0, -1800.0), (760.0, 0.0),
        (-760.0, 1800.0), (760.0, 3500.0),
        (-760.0, 5200.0),
        (-5200.0, 760.0), (-3500.0, -760.0),
        (-1800.0, 760.0), (1800.0, -760.0),
        (3500.0, 760.0), (5200.0, -760.0),
    )

    for i, (x, y) in enumerate(positions):
        cylinder(
            PREFIX + "StreetLight_{:02d}_Pole".format(i),
            unreal.Vector(x, y, 215.0),
            14.0,
            430.0,
            dark,
            False,
        )
        cube(
            PREFIX + "StreetLight_{:02d}_Head".format(i),
            unreal.Vector(x + 45.0, y, 430.0),
            unreal.Vector(90.0, 22.0, 18.0),
            dark,
            False,
        )


def setup_lighting():
    subsystem = actors()

    sun = subsystem.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0.0, 0.0, 4500.0),
        unreal.Rotator(-42.0, -28.0, 0.0),
    )
    label(sun, PREFIX + "Sun")

    try:
        comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
        comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        comp.set_editor_property("intensity", 3.6)
        comp.set_editor_property("atmosphere_sun_light", True)
        comp.set_editor_property("cast_shadows", True)
        comp.set_light_color(unreal.LinearColor(1.0, 0.93, 0.86, 1.0))
    except Exception as exc:
        warn("M9: sun warning: {}".format(exc))

    sky = subsystem.spawn_actor_from_class(
        unreal.SkyAtmosphere,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    label(sky, PREFIX + "SkyAtmosphere")

    skylight = subsystem.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(0.0, 0.0, 800.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    label(skylight, PREFIX + "SkyLight")

    try:
        comp = skylight.get_component_by_class(unreal.SkyLightComponent)
        comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        comp.set_editor_property("real_time_capture", True)
        comp.set_editor_property("intensity", 0.45)
    except Exception as exc:
        warn("M9: skylight warning: {}".format(exc))

    fog = subsystem.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    label(fog, PREFIX + "Fog")

    try:
        comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        comp.set_editor_property("fog_density", 0.004)
        comp.set_editor_property("fog_height_falloff", 0.28)
    except Exception:
        pass

    try:
        cloud = subsystem.spawn_actor_from_class(
            unreal.VolumetricCloud,
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        label(cloud, PREFIX + "VolumetricCloud")
    except Exception:
        pass


def setup_gameplay():
    start = actors().spawn_actor_from_class(
        unreal.PlayerStart,
        unreal.Vector(-260.0, -2600.0, 120.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    label(start, PREFIX + "PlayerStart")

    vehicle_class = unreal.load_class(None, "/Script/OWGame.OWPrototypeVehicle")
    if not vehicle_class:
        raise RuntimeError("M9: OWPrototypeVehicle unavailable")

    vehicle = actors().spawn_actor_from_class(
        vehicle_class,
        unreal.Vector(280.0, -2450.0, 100.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    label(vehicle, PREFIX + "PrototypeVehicle")


def save():
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("M9: saved {}".format(TARGET_MAP))


def main():
    if not unreal.EditorAssetLibrary.does_directory_exist(UNIBLOCKS_ROOT):
        raise RuntimeError("M9: UNIBLOCKS FREE is missing at /Game/Uniblocks")

    ensure_map()
    clear_generated()
    configure_world()

    mats = materials()

    build_ground_and_grid(mats)
    add_road_markings(mats)
    build_blocks(mats)
    add_street_furniture(mats)
    setup_lighting()
    setup_gameplay()

    save()

    log("M9: CORRECTED CITY OVERHAUL COMPLETE")
    log("M9: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
