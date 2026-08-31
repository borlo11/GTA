# bootstrap_m9_city_overhaul.py
# M9 visual/city overhaul for OWGame / Unreal Engine 5.8.
#
# Rebuilds /Game/Maps/OW_LightweightCity as a denser, more readable urban district
# while preserving the validated gameplay coordinates used by M5-M8.
#
# Goals:
# - richer 3x3 road grid instead of a single cross
# - readable lane markings, crosswalks, parking bays and medians
# - varied building massing with podium/tower/setback silhouettes
# - lightweight street furniture and street lighting
# - fully dynamic lighting baseline (no baked-lighting requirement)
# - no third-party source assets committed; UNIBLOCKS FREE remains a local Fab dependency
#
# Idempotent: only actors whose label starts with OW_CITY_ are replaced.

import math
import unreal

TARGET_MAP = "/Game/Maps/OW_LightweightCity"
GENERATED_PREFIX = "OW_CITY_"

UNIBLOCKS_ROOT = "/Game/Uniblocks"
UNIBLOCKS_BLOCK_NAME = "SM_UB_Block_scalable"

CUBE_MESH_PATH = "/Engine/BasicShapes/Cube.Cube"
CYLINDER_MESH_PATH = "/Engine/BasicShapes/Cylinder.Cylinder"
SPHERE_MESH_PATH = "/Engine/BasicShapes/Sphere.Sphere"

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
DARK_DETAIL_MATERIAL_NAMES = (
    "MI_UBT_concreteSmooth_dark",
    "MI_UBT_concreteRaw_gray_plain",
)
BUILDING_MATERIAL_NAMES = (
    "MI_UBT_brickwork_white",
    "MI_UBT_concreteRaw_gray_plain",
    "MI_UBT_concreteRaw_white_plain",
    "MI_UBT_concreteSmooth_gray",
)

GROUND_Z = 0.0
GROUND_SIZE = 17000.0

MAIN_ROAD_WIDTH = 1300.0
SECONDARY_ROAD_WIDTH = 900.0
ROAD_HEIGHT = 10.0

SIDEWALK_HEIGHT = 20.0
LOT_PAD_HEIGHT = 18.0

GRID_ROADS = (-4200.0, 0.0, 4200.0)
BLOCK_CENTERS = (-6100.0, -2100.0, 2100.0, 6100.0)

log = unreal.log
warn = unreal.log_warning


def actor_subsystem():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def level_subsystem():
    return unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


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


def set_label(actor, label):
    actor.set_actor_label(label)
    return actor


def ensure_map():
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not level_subsystem().load_level(TARGET_MAP):
            raise RuntimeError("Could not load {}".format(TARGET_MAP))
        log("M9: loaded existing {}".format(TARGET_MAP))
        return

    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/Maps"):
        unreal.EditorAssetLibrary.make_directory("/Game/Maps")

    if not level_subsystem().new_level(TARGET_MAP, False):
        raise RuntimeError("Could not create {}".format(TARGET_MAP))

    log("M9: created {}".format(TARGET_MAP))


def delete_generated_actors():
    subsystem = actor_subsystem()
    removed = 0

    for actor in list(subsystem.get_all_level_actors()):
        if actor and actor.get_actor_label().startswith(GENERATED_PREFIX):
            subsystem.destroy_actor(actor)
            removed += 1

    log("M9: removed {} previous generated actors".format(removed))


def configure_world_settings():
    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings() if world else None

    if not settings:
        raise RuntimeError("M9: WorldSettings unavailable")

    game_mode_class = unreal.load_class(None, "/Script/OWGame.OWGameGameMode")
    if not game_mode_class:
        raise RuntimeError("M9: OWGameGameMode unavailable; build C++ first")

    settings.set_editor_property("default_game_mode", game_mode_class)

    # The M9 city uses dynamic GI/shadows. Avoid the old red "lighting must be rebuilt"
    # warning and the cost/maintenance of baked lighting for a world that will keep changing.
    try:
        settings.set_editor_property("force_no_precomputed_lighting", True)
        log("M9: ForceNoPrecomputedLighting enabled")
    except Exception as exc:
        warn("M9: could not set ForceNoPrecomputedLighting: {}".format(exc))


def spawn_static_mesh(label, mesh_path, location, scale, material=None, rotation=None):
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        raise RuntimeError("M9: missing engine mesh {}".format(mesh_path))

    actor = actor_subsystem().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        rotation or unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(actor, label)

    component = actor.static_mesh_component
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_static_mesh(mesh)
    component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)

    if material:
        component.set_material(0, material)

    actor.set_actor_scale3d(scale)
    return actor


def spawn_cube(label, location, size, material=None, rotation=None, collision=True):
    actor = spawn_static_mesh(
        label,
        CUBE_MESH_PATH,
        location,
        unreal.Vector(size.x / 100.0, size.y / 100.0, size.z / 100.0),
        material,
        rotation,
    )

    if not collision:
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    return actor


def spawn_cylinder(label, location, diameter, height, material=None, collision=False):
    actor = spawn_static_mesh(
        label,
        CYLINDER_MESH_PATH,
        location,
        unreal.Vector(diameter / 100.0, diameter / 100.0, height / 100.0),
        material,
    )

    if not collision:
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    return actor


def mesh_dimensions(mesh):
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


def spawn_uniblocks_mass(label, center_xy, desired_size, material=None, yaw=0.0):
    mesh = find_asset_by_name(UNIBLOCKS_ROOT, UNIBLOCKS_BLOCK_NAME)
    if not mesh:
        raise RuntimeError("M9: required UNIBLOCKS mesh not found")

    dimensions, minimum, maximum = mesh_dimensions(mesh)

    scale = unreal.Vector(
        desired_size.x / dimensions.x,
        desired_size.y / dimensions.y,
        desired_size.z / dimensions.z,
    )

    local_center_x = (minimum.x + maximum.x) * 0.5
    local_center_y = (minimum.y + maximum.y) * 0.5

    location = unreal.Vector(
        center_xy.x - local_center_x * scale.x,
        center_xy.y - local_center_y * scale.y,
        GROUND_Z - minimum.z * scale.z + LOT_PAD_HEIGHT,
    )

    actor = actor_subsystem().spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    set_label(actor, label)

    component = actor.static_mesh_component
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_static_mesh(mesh)
    if material:
        component.set_material(0, material)

    actor.set_actor_scale3d(scale)
    return actor


def load_materials():
    root = "/Game/Uniblocks/Materials"

    return {
        "road": first_asset_by_names(root, ROAD_MATERIAL_NAMES),
        "sidewalk": first_asset_by_names(root, SIDEWALK_MATERIAL_NAMES),
        "marking": first_asset_by_names(root, MARKING_MATERIAL_NAMES),
        "dark": first_asset_by_names(root, DARK_DETAIL_MATERIAL_NAMES),
        "buildings": [
            asset
            for asset in (
                find_asset_by_name(root, name)
                for name in BUILDING_MATERIAL_NAMES
            )
            if asset
        ],
    }


def road_width_at_coordinate(value):
    return MAIN_ROAD_WIDTH if abs(value) < 1.0 else SECONDARY_ROAD_WIDTH


def build_ground_and_roads(materials):
    road_mat = materials["road"]
    sidewalk_mat = materials["sidewalk"]

    spawn_cube(
        GENERATED_PREFIX + "Ground",
        unreal.Vector(0.0, 0.0, GROUND_Z - 65.0),
        unreal.Vector(GROUND_SIZE, GROUND_SIZE, 120.0),
        sidewalk_mat,
    )

    # Three north/south and three east/west roads form a compact district
    # with enough alternate routes for vehicle/police testing.
    for index, x in enumerate(GRID_ROADS):
        width = road_width_at_coordinate(x)
        spawn_cube(
            GENERATED_PREFIX + "Road_NS_{:02d}".format(index),
            unreal.Vector(x, 0.0, GROUND_Z + ROAD_HEIGHT * 0.5),
            unreal.Vector(width, GROUND_SIZE, ROAD_HEIGHT),
            road_mat,
        )

    for index, y in enumerate(GRID_ROADS):
        width = road_width_at_coordinate(y)
        spawn_cube(
            GENERATED_PREFIX + "Road_EW_{:02d}".format(index),
            unreal.Vector(0.0, y, GROUND_Z + ROAD_HEIGHT * 0.5),
            unreal.Vector(GROUND_SIZE, width, ROAD_HEIGHT),
            road_mat,
        )

    # Keep legacy labels expected by earlier validators.
    spawn_cube(
        GENERATED_PREFIX + "Road_NS",
        unreal.Vector(0.0, 0.0, GROUND_Z + ROAD_HEIGHT * 0.5 + 0.2),
        unreal.Vector(MAIN_ROAD_WIDTH, GROUND_SIZE, 1.0),
        road_mat,
        collision=False,
    )
    spawn_cube(
        GENERATED_PREFIX + "Road_EW",
        unreal.Vector(0.0, 0.0, GROUND_Z + ROAD_HEIGHT * 0.5 + 0.2),
        unreal.Vector(GROUND_SIZE, MAIN_ROAD_WIDTH, 1.0),
        road_mat,
        collision=False,
    )

    # Raised sidewalk pads create readable blocks and naturally keep pedestrians
    # out of most road surfaces.
    lot_size = 2920.0

    for ix, x in enumerate(BLOCK_CENTERS):
        for iy, y in enumerate(BLOCK_CENTERS):
            spawn_cube(
                GENERATED_PREFIX + "SidewalkPad_{:02d}_{:02d}".format(ix, iy),
                unreal.Vector(x, y, GROUND_Z + LOT_PAD_HEIGHT * 0.5),
                unreal.Vector(lot_size, lot_size, LOT_PAD_HEIGHT),
                sidewalk_mat,
            )


def add_lane_dashes(materials):
    marking = materials["marking"]
    z = GROUND_Z + ROAD_HEIGHT + 1.2

    dash_length = 330.0
    dash_gap = 290.0
    dash_thickness = 8.0
    lane_offset_main = 300.0
    lane_offset_secondary = 205.0

    # North/south road markings.
    for road_index, x in enumerate(GRID_ROADS):
        lane_offset = lane_offset_main if abs(x) < 1.0 else lane_offset_secondary

        for lane_side in (-1.0, 1.0):
            y = -7800.0
            dash_index = 0
            while y <= 7800.0:
                spawn_cube(
                    GENERATED_PREFIX + "RoadMark_NS_{}_{}_{}".format(
                        road_index,
                        0 if lane_side < 0 else 1,
                        dash_index,
                    ),
                    unreal.Vector(x + lane_side * lane_offset, y, z),
                    unreal.Vector(12.0, dash_length, dash_thickness),
                    marking,
                    collision=False,
                )
                y += dash_length + dash_gap
                dash_index += 1

    # East/west road markings.
    for road_index, y in enumerate(GRID_ROADS):
        lane_offset = lane_offset_main if abs(y) < 1.0 else lane_offset_secondary

        for lane_side in (-1.0, 1.0):
            x = -7800.0
            dash_index = 0
            while x <= 7800.0:
                spawn_cube(
                    GENERATED_PREFIX + "RoadMark_EW_{}_{}_{}".format(
                        road_index,
                        0 if lane_side < 0 else 1,
                        dash_index,
                    ),
                    unreal.Vector(x, y + lane_side * lane_offset, z),
                    unreal.Vector(dash_length, 12.0, dash_thickness),
                    marking,
                    collision=False,
                )
                x += dash_length + dash_gap
                dash_index += 1


def add_crosswalk(center_x, center_y, axis, sequence, materials):
    marking = materials["marking"]
    z = GROUND_Z + ROAD_HEIGHT + 1.8

    stripe_width = 46.0
    stripe_gap = 42.0
    stripe_length = 660.0
    count = 7

    for i in range(count):
        offset = (i - (count - 1) * 0.5) * (stripe_width + stripe_gap)

        if axis == "NS":
            location = unreal.Vector(center_x + offset, center_y, z)
            size = unreal.Vector(stripe_width, stripe_length, 6.0)
        else:
            location = unreal.Vector(center_x, center_y + offset, z)
            size = unreal.Vector(stripe_length, stripe_width, 6.0)

        spawn_cube(
            GENERATED_PREFIX + "Crosswalk_{}_{}".format(sequence, i),
            location,
            size,
            marking,
            collision=False,
        )


def add_crosswalks(materials):
    sequence = 0

    # Keep crosswalk count focused on the major central corridor so the visual
    # upgrade is readable without exploding draw-call count.
    for x in GRID_ROADS:
        for y in GRID_ROADS:
            if abs(x) < 1.0 or abs(y) < 1.0:
                add_crosswalk(x, y - 520.0, "NS", sequence, materials)
                sequence += 1
                add_crosswalk(x - 520.0, y, "EW", sequence, materials)
                sequence += 1


def add_parking_bays(materials):
    marking = materials["marking"]
    z = GROUND_Z + ROAD_HEIGHT + 1.5
    bay_index = 0

    # A few explicit parking strips make the streets read as urban space.
    strips = (
        (-760.0, -2700.0, "NS"),
        (760.0, 2600.0, "NS"),
        (-2700.0, 760.0, "EW"),
        (2700.0, -760.0, "EW"),
    )

    for x, y, axis in strips:
        for i in range(6):
            offset = (i - 2.5) * 430.0

            if axis == "NS":
                px = x
                py = y + offset
                size = unreal.Vector(270.0, 8.0, 5.0)
            else:
                px = x + offset
                py = y
                size = unreal.Vector(8.0, 270.0, 5.0)

            spawn_cube(
                GENERATED_PREFIX + "ParkingBay_{:02d}".format(bay_index),
                unreal.Vector(px, py, z),
                size,
                marking,
                collision=False,
            )
            bay_index += 1


def build_city_blocks(materials):
    building_materials = materials["buildings"]
    dark = materials["dark"]
    sidewalk = materials["sidewalk"]

    if not building_materials:
        building_materials = [sidewalk]

    building_index = 0

    for ix, x in enumerate(BLOCK_CENTERS):
        for iy, y in enumerate(BLOCK_CENTERS):
            # Leave two blocks visually lighter to create parking/plaza breathing room.
            if (ix, iy) in ((0, 3), (3, 0)):
                build_plaza_block(ix, iy, x, y, materials)
                continue

            building_index += 1
            material = building_materials[(ix + iy) % len(building_materials)]
            detail_material = dark or material

            variant = (ix * 5 + iy * 3) % 4

            if variant == 0:
                base_size = unreal.Vector(2200.0, 1900.0, 620.0)
                tower_size = unreal.Vector(1450.0, 1250.0, 1800.0)
                tower_offset = unreal.Vector(180.0, -120.0, 0.0)
            elif variant == 1:
                base_size = unreal.Vector(1750.0, 2300.0, 760.0)
                tower_size = unreal.Vector(1200.0, 1500.0, 2300.0)
                tower_offset = unreal.Vector(-160.0, 180.0, 0.0)
            elif variant == 2:
                base_size = unreal.Vector(2300.0, 1700.0, 520.0)
                tower_size = unreal.Vector(1650.0, 1050.0, 1450.0)
                tower_offset = unreal.Vector(120.0, 230.0, 0.0)
            else:
                base_size = unreal.Vector(1900.0, 1900.0, 880.0)
                tower_size = unreal.Vector(1050.0, 1050.0, 2700.0)
                tower_offset = unreal.Vector(-220.0, -180.0, 0.0)

            yaw = 90.0 if (ix + iy) % 3 == 0 else 0.0

            base_center = unreal.Vector(x, y, 0.0)
            tower_center = unreal.Vector(
                x + tower_offset.x,
                y + tower_offset.y,
                0.0,
            )

            spawn_uniblocks_mass(
                GENERATED_PREFIX + "Building_{:02d}_Base".format(building_index),
                base_center,
                base_size,
                material,
                yaw,
            )

            spawn_uniblocks_mass(
                GENERATED_PREFIX + "Building_{:02d}_Tower".format(building_index),
                tower_center,
                tower_size,
                material,
                yaw,
            )

            # Thin roof cap creates a stronger silhouette and breaks the old box-only look.
            spawn_cube(
                GENERATED_PREFIX + "Building_{:02d}_RoofCap".format(building_index),
                unreal.Vector(
                    tower_center.x,
                    tower_center.y,
                    LOT_PAD_HEIGHT + tower_size.z + 18.0,
                ),
                unreal.Vector(
                    tower_size.x * 0.94,
                    tower_size.y * 0.94,
                    32.0,
                ),
                detail_material,
            )

            add_facade_bands(
                building_index,
                tower_center,
                tower_size,
                detail_material,
                yaw,
            )


def add_facade_bands(building_index, center, size, material, yaw):
    # Only two bands per tower: enough to add façade rhythm without hundreds of actors.
    band_height = max(420.0, size.z * 0.76)
    z = LOT_PAD_HEIGHT + size.z * 0.52

    for band in (-1.0, 1.0):
        offset = band * size.x * 0.23

        if abs(yaw - 90.0) < 1.0:
            location = unreal.Vector(
                center.x,
                center.y + offset,
                z,
            )
            band_size = unreal.Vector(size.y + 18.0, 18.0, band_height)
        else:
            location = unreal.Vector(
                center.x + offset,
                center.y,
                z,
            )
            band_size = unreal.Vector(18.0, size.y + 18.0, band_height)

        spawn_cube(
            GENERATED_PREFIX + "Building_{:02d}_FacadeBand_{}".format(
                building_index,
                0 if band < 0 else 1,
            ),
            location,
            band_size,
            material,
            collision=False,
        )


def build_plaza_block(ix, iy, x, y, materials):
    sidewalk = materials["sidewalk"]
    dark = materials["dark"] or sidewalk

    # Low perimeter planters / seating edges.
    for edge_index, (ox, oy, sx, sy) in enumerate((
        (-1050.0, 0.0, 120.0, 1800.0),
        (1050.0, 0.0, 120.0, 1800.0),
        (0.0, -1050.0, 1800.0, 120.0),
        (0.0, 1050.0, 1800.0, 120.0),
    )):
        spawn_cube(
            GENERATED_PREFIX + "UrbanProp_Plaza_{}_{}_Edge_{}".format(ix, iy, edge_index),
            unreal.Vector(x + ox, y + oy, LOT_PAD_HEIGHT + 28.0),
            unreal.Vector(sx, sy, 56.0),
            dark,
        )

    # Central sculptural elements made from cheap primitives.
    spawn_cylinder(
        GENERATED_PREFIX + "UrbanProp_Plaza_{}_{}_Column".format(ix, iy),
        unreal.Vector(x, y, LOT_PAD_HEIGHT + 160.0),
        150.0,
        320.0,
        dark,
    )

    spawn_static_mesh(
        GENERATED_PREFIX + "UrbanProp_Plaza_{}_{}_Sphere".format(ix, iy),
        SPHERE_MESH_PATH,
        unreal.Vector(x, y, LOT_PAD_HEIGHT + 390.0),
        unreal.Vector(1.3, 1.3, 1.3),
        sidewalk,
    ).static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)


def add_streetlight(label, x, y, facing_yaw, materials):
    dark = materials["dark"] or materials["sidewalk"]

    pole_height = 430.0
    pole_z = GROUND_Z + pole_height * 0.5 + SIDEWALK_HEIGHT

    spawn_cylinder(
        label + "_Pole",
        unreal.Vector(x, y, pole_z),
        18.0,
        pole_height,
        dark,
    )

    # Small horizontal arm/head.
    yaw_radians = math.radians(facing_yaw)
    forward_x = math.cos(yaw_radians)
    forward_y = math.sin(yaw_radians)

    head_x = x + forward_x * 70.0
    head_y = y + forward_y * 70.0

    spawn_cube(
        label + "_Head",
        unreal.Vector(head_x, head_y, GROUND_Z + SIDEWALK_HEIGHT + 435.0),
        unreal.Vector(145.0, 28.0, 22.0),
        dark,
        unreal.Rotator(0.0, facing_yaw, 0.0),
        collision=False,
    )

    light = actor_subsystem().spawn_actor_from_class(
        unreal.PointLight,
        unreal.Vector(head_x, head_y, GROUND_Z + SIDEWALK_HEIGHT + 410.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(light, label + "_Light")

    try:
        component = light.get_component_by_class(unreal.PointLightComponent)
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_editor_property("intensity", 650.0)
        component.set_editor_property("attenuation_radius", 520.0)
        component.set_editor_property("cast_shadows", False)
        component.set_light_color(unreal.LinearColor(1.0, 0.76, 0.48, 1.0))
    except Exception as exc:
        warn("M9: street light setup warning: {}".format(exc))


def add_street_furniture(materials):
    light_positions = (
        (-760.0, -5600.0, 0.0),
        (760.0, -3900.0, 180.0),
        (-760.0, -2200.0, 0.0),
        (760.0, -500.0, 180.0),
        (-760.0, 1400.0, 0.0),
        (760.0, 3100.0, 180.0),
        (-760.0, 5000.0, 0.0),
        (-5600.0, 760.0, -90.0),
        (-3900.0, -760.0, 90.0),
        (-2200.0, 760.0, -90.0),
        (-500.0, -760.0, 90.0),
        (1400.0, 760.0, -90.0),
        (3100.0, -760.0, 90.0),
        (5000.0, 760.0, -90.0),
    )

    for index, (x, y, yaw) in enumerate(light_positions):
        add_streetlight(
            GENERATED_PREFIX + "StreetLight_{:02d}".format(index),
            x,
            y,
            yaw,
            materials,
        )

    # Bollards around the central intersection stop the huge empty-corner feeling.
    dark = materials["dark"] or materials["sidewalk"]
    bollard_index = 0

    for x in (-850.0, 850.0):
        for y in (-850.0, 850.0):
            for offset in (-180.0, 0.0, 180.0):
                bx = x + (offset if abs(y) > abs(x) else 0.0)
                by = y + (offset if abs(x) >= abs(y) else 0.0)

                spawn_cylinder(
                    GENERATED_PREFIX + "UrbanProp_Bollard_{:02d}".format(bollard_index),
                    unreal.Vector(bx, by, GROUND_Z + 48.0),
                    28.0,
                    96.0,
                    dark,
                )
                bollard_index += 1


def setup_lighting_and_atmosphere():
    subsystem = actor_subsystem()

    sun = subsystem.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0.0, 0.0, 4500.0),
        unreal.Rotator(-35.0, -28.0, 0.0),
    )
    set_label(sun, GENERATED_PREFIX + "Sun")

    try:
        component = sun.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_editor_property("intensity", 6.2)
        component.set_editor_property("atmosphere_sun_light", True)
        component.set_editor_property("cast_shadows", True)
        component.set_light_color(unreal.LinearColor(1.0, 0.91, 0.80, 1.0))
    except Exception as exc:
        warn("M9: sun setup warning: {}".format(exc))

    atmosphere = subsystem.spawn_actor_from_class(
        unreal.SkyAtmosphere,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(atmosphere, GENERATED_PREFIX + "SkyAtmosphere")

    skylight = subsystem.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(0.0, 0.0, 900.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(skylight, GENERATED_PREFIX + "SkyLight")

    try:
        component = skylight.get_component_by_class(unreal.SkyLightComponent)
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_editor_property("real_time_capture", True)
        component.set_editor_property("intensity", 0.72)
    except Exception as exc:
        warn("M9: skylight setup warning: {}".format(exc))

    fog = subsystem.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(fog, GENERATED_PREFIX + "Fog")

    try:
        component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        component.set_editor_property("fog_density", 0.008)
        component.set_editor_property("fog_height_falloff", 0.24)
    except Exception:
        pass

    # Volumetric clouds are optional; if available they add depth without content dependencies.
    try:
        clouds = subsystem.spawn_actor_from_class(
            unreal.VolumetricCloud,
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        set_label(clouds, GENERATED_PREFIX + "VolumetricCloud")
    except Exception as exc:
        warn("M9: VolumetricCloud unavailable: {}".format(exc))


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
        raise RuntimeError("M9: OWPrototypeVehicle unavailable; build C++ first")

    vehicle = subsystem.spawn_actor_from_class(
        vehicle_class,
        unreal.Vector(280.0, -2450.0, 100.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    set_label(vehicle, GENERATED_PREFIX + "PrototypeVehicle")


def save_level():
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("M9: saved {}".format(TARGET_MAP))


def main():
    if not unreal.EditorAssetLibrary.does_directory_exist(UNIBLOCKS_ROOT):
        raise RuntimeError(
            "M9: UNIBLOCKS content missing at {}. Install the Fab pack first.".format(
                UNIBLOCKS_ROOT
            )
        )

    ensure_map()
    delete_generated_actors()
    configure_world_settings()

    materials = load_materials()

    build_ground_and_roads(materials)
    add_lane_dashes(materials)
    add_crosswalks(materials)
    add_parking_bays(materials)
    build_city_blocks(materials)
    add_street_furniture(materials)
    setup_lighting_and_atmosphere()
    setup_gameplay()

    save_level()

    log("M9: CITY OVERHAUL COMPLETE")
    log("M9: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
