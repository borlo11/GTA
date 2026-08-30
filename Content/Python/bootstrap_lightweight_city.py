# bootstrap_lightweight_city.py
# M4.5 lightweight original city bootstrap for OWGame / Unreal Engine 5.8.
#
# Creates or rebuilds /Game/Maps/OW_LightweightCity using:
# - engine primitive meshes for ground, roads and sidewalks
# - UNIBLOCKS FREE SM_UB_Block_scalable for building masses
# - OWGame GameMode, PlayerStart, M2 vehicle and M4 runtime population
#
# Idempotent: reruns only replace actors whose labels start with OW_CITY_.

import unreal

TARGET_MAP = "/Game/Maps/OW_LightweightCity"
GENERATED_PREFIX = "OW_CITY_"

CUBE_MESH_PATH = "/Engine/BasicShapes/Cube.Cube"
UNIBLOCKS_ROOT = "/Game/Uniblocks"
UNIBLOCKS_BLOCK_NAME = "SM_UB_Block_scalable"

ROAD_MATERIAL_NAMES = (
    "MI_UBT_concreteSmooth_dark",
    "MI_UBT_concreteAged_lines",
)
SIDEWALK_MATERIAL_NAMES = (
    "MI_UBT_concreteSmooth_gray",
    "MI_UBT_concreteRaw_gray_plain",
)
BUILDING_MATERIAL_NAMES = (
    "MI_UBT_brickwork_white",
    "MI_UBT_concreteRaw_gray_plain",
    "MI_UBT_concreteRaw_white_plain",
    "MI_UBT_concreteSmooth_gray",
)

GROUND_Z = 0.0
GROUND_SIZE = 14000.0
ROAD_WIDTH = 1300.0
SIDEWALK_WIDTH = 220.0
SIDEWALK_HEIGHT = 18.0
ROAD_HEIGHT = 10.0

log = unreal.log
warn = unreal.log_warning


def find_asset_by_name(root, asset_name):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    for data in registry.get_assets_by_path(root, recursive=True):
        if str(data.asset_name) == asset_name:
            return unreal.EditorAssetLibrary.load_asset(str(data.package_name))
    return None


def first_asset_by_names(root, names):
    for name in names:
        asset = find_asset_by_name(root, name)
        if asset:
            return asset
    return None


def actor_subsystem():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def level_subsystem():
    return unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def set_label(actor, label):
    actor.set_actor_label(label)
    return actor


def delete_generated_actors():
    subsystem = actor_subsystem()
    deleted = 0
    for actor in list(subsystem.get_all_level_actors()):
        if actor and actor.get_actor_label().startswith(GENERATED_PREFIX):
            subsystem.destroy_actor(actor)
            deleted += 1
    if deleted:
        log("bootstrap_lightweight_city: removed {} previously generated actors".format(deleted))


def ensure_map():
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        ok = level_subsystem().load_level(TARGET_MAP)
        if not ok:
            raise RuntimeError("Could not load {}".format(TARGET_MAP))
        log("bootstrap_lightweight_city: loaded existing {}".format(TARGET_MAP))
        return

    maps_dir = "/Game/Maps"
    if not unreal.EditorAssetLibrary.does_directory_exist(maps_dir):
        unreal.EditorAssetLibrary.make_directory(maps_dir)

    ok = level_subsystem().new_level(TARGET_MAP, False)
    if not ok:
        raise RuntimeError("Could not create {}".format(TARGET_MAP))
    log("bootstrap_lightweight_city: created {}".format(TARGET_MAP))


def set_game_mode():
    game_mode_class = unreal.load_class(None, "/Script/OWGame.OWGameGameMode")
    if not game_mode_class:
        raise RuntimeError("OWGameGameMode class is unavailable; build the C++ module first")

    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings() if world else None
    if not settings:
        raise RuntimeError("Could not obtain WorldSettings")

    try:
        settings.set_editor_property("default_game_mode", game_mode_class)
        log("bootstrap_lightweight_city: WorldSettings -> OWGameGameMode")
    except Exception as exc:
        warn("bootstrap_lightweight_city: could not set map GameMode: {}".format(exc))


def spawn_cube(label, location, size, material=None):
    subsystem = actor_subsystem()
    actor = subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(actor, label)

    component = actor.static_mesh_component
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_static_mesh(unreal.load_asset(CUBE_MESH_PATH))
    if material:
        component.set_material(0, material)

    actor.set_actor_scale3d(
        unreal.Vector(size.x / 100.0, size.y / 100.0, size.z / 100.0)
    )
    return actor


def mesh_dimensions(mesh):
    box = mesh.get_bounding_box()
    minimum = box.min
    maximum = box.max
    return unreal.Vector(
        max(1.0, maximum.x - minimum.x),
        max(1.0, maximum.y - minimum.y),
        max(1.0, maximum.z - minimum.z),
    ), minimum, maximum


def spawn_uniblocks_building(label, center_xy, desired_size, material=None):
    mesh = find_asset_by_name(UNIBLOCKS_ROOT, UNIBLOCKS_BLOCK_NAME)
    if not mesh:
        raise RuntimeError(
            "Required UNIBLOCKS mesh {} not found".format(UNIBLOCKS_BLOCK_NAME)
        )

    dimensions, minimum, maximum = mesh_dimensions(mesh)
    scale = unreal.Vector(
        desired_size.x / dimensions.x,
        desired_size.y / dimensions.y,
        desired_size.z / dimensions.z,
    )

    # Place the scaled local bounding-box bottom exactly on the city ground.
    local_center_x = (minimum.x + maximum.x) * 0.5
    local_center_y = (minimum.y + maximum.y) * 0.5

    location = unreal.Vector(
        center_xy.x - local_center_x * scale.x,
        center_xy.y - local_center_y * scale.y,
        GROUND_Z - minimum.z * scale.z,
    )

    actor = actor_subsystem().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(actor, label)

    component = actor.static_mesh_component
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_static_mesh(mesh)
    if material:
        component.set_material(0, material)

    actor.set_actor_scale3d(scale)
    return actor


def build_streets():
    road_material = first_asset_by_names(
        "/Game/Uniblocks/Materials", ROAD_MATERIAL_NAMES
    )
    sidewalk_material = first_asset_by_names(
        "/Game/Uniblocks/Materials", SIDEWALK_MATERIAL_NAMES
    )

    # Neutral ground under the generated district.
    spawn_cube(
        GENERATED_PREFIX + "Ground",
        unreal.Vector(0.0, 0.0, GROUND_Z - 55.0),
        unreal.Vector(GROUND_SIZE, GROUND_SIZE, 100.0),
        sidewalk_material,
    )

    # Cross-shaped road network.
    spawn_cube(
        GENERATED_PREFIX + "Road_NS",
        unreal.Vector(0.0, 0.0, GROUND_Z + ROAD_HEIGHT * 0.5),
        unreal.Vector(ROAD_WIDTH, GROUND_SIZE, ROAD_HEIGHT),
        road_material,
    )
    spawn_cube(
        GENERATED_PREFIX + "Road_EW",
        unreal.Vector(0.0, 0.0, GROUND_Z + ROAD_HEIGHT * 0.5),
        unreal.Vector(GROUND_SIZE, ROAD_WIDTH, ROAD_HEIGHT),
        road_material,
    )

    sidewalk_offset = ROAD_WIDTH * 0.5 + SIDEWALK_WIDTH * 0.5

    # North/south road sidewalks.
    for index, x in enumerate((-sidewalk_offset, sidewalk_offset)):
        spawn_cube(
            GENERATED_PREFIX + "Sidewalk_NS_{:02d}".format(index),
            unreal.Vector(x, 0.0, GROUND_Z + SIDEWALK_HEIGHT * 0.5),
            unreal.Vector(SIDEWALK_WIDTH, GROUND_SIZE, SIDEWALK_HEIGHT),
            sidewalk_material,
        )

    # East/west road sidewalks.
    for index, y in enumerate((-sidewalk_offset, sidewalk_offset)):
        spawn_cube(
            GENERATED_PREFIX + "Sidewalk_EW_{:02d}".format(index),
            unreal.Vector(0.0, y, GROUND_Z + SIDEWALK_HEIGHT * 0.5),
            unreal.Vector(GROUND_SIZE, SIDEWALK_WIDTH, SIDEWALK_HEIGHT),
            sidewalk_material,
        )


def build_city_blocks():
    materials = []
    for name in BUILDING_MATERIAL_NAMES:
        asset = find_asset_by_name("/Game/Uniblocks/Materials", name)
        if asset:
            materials.append(asset)

    # Four quadrants, each with three deliberately different building masses.
    buildings = [
        # NW
        (-2600.0,  2500.0, 1800.0, 1500.0, 1800.0),
        (-4300.0,  2300.0, 1300.0, 1700.0, 2600.0),
        (-3100.0,  4400.0, 2400.0, 1200.0, 1400.0),
        # NE
        ( 2600.0,  2500.0, 1700.0, 1600.0, 2200.0),
        ( 4400.0,  2500.0, 1400.0, 1800.0, 1500.0),
        ( 3200.0,  4500.0, 2300.0, 1300.0, 2900.0),
        # SW
        (-2600.0, -2500.0, 1900.0, 1500.0, 1500.0),
        (-4400.0, -2400.0, 1400.0, 1800.0, 2400.0),
        (-3200.0, -4500.0, 2200.0, 1300.0, 1900.0),
        # SE
        ( 2600.0, -2500.0, 1800.0, 1700.0, 2700.0),
        ( 4400.0, -2500.0, 1500.0, 1600.0, 1700.0),
        ( 3200.0, -4500.0, 2300.0, 1200.0, 2100.0),
    ]

    for index, (x, y, sx, sy, sz) in enumerate(buildings):
        material = materials[index % len(materials)] if materials else None
        spawn_uniblocks_building(
            GENERATED_PREFIX + "Building_{:02d}".format(index + 1),
            unreal.Vector(x, y, 0.0),
            unreal.Vector(sx, sy, sz),
            material,
        )


def setup_lighting():
    subsystem = actor_subsystem()

    sun = subsystem.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0.0, 0.0, 4000.0),
        unreal.Rotator(-42.0, -35.0, 0.0),
    )
    set_label(sun, GENERATED_PREFIX + "Sun")
    try:
        sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        sun_component.set_editor_property("intensity", 7.5)
        sun_component.set_editor_property("atmosphere_sun_light", True)
    except Exception:
        pass

    atmosphere = subsystem.spawn_actor_from_class(
        unreal.SkyAtmosphere,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(atmosphere, GENERATED_PREFIX + "SkyAtmosphere")

    skylight = subsystem.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(0.0, 0.0, 800.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(skylight, GENERATED_PREFIX + "SkyLight")
    try:
        sky_component = skylight.get_component_by_class(unreal.SkyLightComponent)
        sky_component.set_editor_property("real_time_capture", True)
        sky_component.set_editor_property("intensity", 1.0)
    except Exception:
        pass

    fog = subsystem.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(fog, GENERATED_PREFIX + "Fog")


def setup_gameplay():
    subsystem = actor_subsystem()

    start = subsystem.spawn_actor_from_class(
        unreal.PlayerStart,
        unreal.Vector(-260.0, -2600.0, 120.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(start, GENERATED_PREFIX + "PlayerStart")

    vehicle_class = unreal.load_class(None, "/Script/OWGame.OWPrototypeVehicle")
    if not vehicle_class:
        raise RuntimeError("Could not load OWPrototypeVehicle; build the C++ module first")

    vehicle = subsystem.spawn_actor_from_class(
        vehicle_class,
        unreal.Vector(280.0, -2450.0, 100.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(vehicle, GENERATED_PREFIX + "PrototypeVehicle")


def save_level():
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("bootstrap_lightweight_city: saved {}".format(TARGET_MAP))


def main():
    if not unreal.EditorAssetLibrary.does_directory_exist(UNIBLOCKS_ROOT):
        raise RuntimeError("UNIBLOCKS content is missing at {}".format(UNIBLOCKS_ROOT))

    ensure_map()
    delete_generated_actors()
    set_game_mode()

    build_streets()
    build_city_blocks()
    setup_lighting()
    setup_gameplay()

    save_level()
    log("bootstrap_lightweight_city: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
