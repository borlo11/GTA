# bootstrap_m10_chaos_vehicle.py
# M10 city integration for the migrated UE 5.8 Vehicle Template SportsCar.
#
# Replaces the old OWPrototypeVehicle instance in OW_LightweightCity with the
# real BP_VehicleAdvSportsCar Chaos pawn plus an OWGame interaction proxy.
# The script is idempotent and only owns actors whose label starts with OW_M10_.

import unreal

TARGET_MAP = "/Game/Maps/OW_LightweightCity"
PREFIX = "OW_M10_"

SPORTS_CAR_CLASS = (
    "/Game/VehicleTemplate/Blueprints/SportsCar/"
    "BP_VehicleAdvSportsCar.BP_VehicleAdvSportsCar_C"
)
PROXY_CLASS = "/Script/OWGame.OWVehicleInteractionProxy"

VEHICLE_LOCATION = unreal.Vector(280.0, -2450.0, 145.0)
VEHICLE_ROTATION = unreal.Rotator(0.0, 0.0, 0.0)


def actor_subsystem():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def level_subsystem():
    return unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def set_tags(actor, *tags):
    actor.set_editor_property(
        "tags",
        [unreal.Name(tag) for tag in tags],
    )


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        raise RuntimeError("M10: city map missing: {}".format(TARGET_MAP))

    if not level_subsystem().load_level(TARGET_MAP):
        raise RuntimeError("M10: could not load city map")

    sports_car_class = unreal.load_class(None, SPORTS_CAR_CLASS)
    if not sports_car_class:
        raise RuntimeError(
            "M10: migrated SportsCar class missing. "
            "Migrate BP_VehicleAdvSportsCar into OWGame first."
        )

    proxy_class = unreal.load_class(None, PROXY_CLASS)
    if not proxy_class:
        raise RuntimeError(
            "M10: OWVehicleInteractionProxy unavailable; build current C++ first"
        )

    actors = list(actor_subsystem().get_all_level_actors())

    removed = 0
    for actor in actors:
        if not actor:
            continue

        label = actor.get_actor_label()
        if label.startswith(PREFIX) or label == "OW_CITY_PrototypeVehicle":
            actor_subsystem().destroy_actor(actor)
            removed += 1

    unreal.log("M10: removed {} old/generated vehicle actors".format(removed))

    vehicle = actor_subsystem().spawn_actor_from_class(
        sports_car_class,
        VEHICLE_LOCATION,
        VEHICLE_ROTATION,
    )
    if not vehicle:
        raise RuntimeError("M10: failed to spawn BP_VehicleAdvSportsCar")

    vehicle.set_actor_label(PREFIX + "SportsCar")
    set_tags(vehicle, "OWMissionVehicle", "OWNoPopulationSpawn")

    try:
        vehicle.set_editor_property(
            "auto_possess_player",
            unreal.AutoReceiveInput.DISABLED,
        )
    except Exception as exc:
        unreal.log_warning(
            "M10: could not force auto_possess_player disabled: {}".format(exc)
        )

    proxy = actor_subsystem().spawn_actor_from_class(
        proxy_class,
        VEHICLE_LOCATION,
        VEHICLE_ROTATION,
    )
    if not proxy:
        actor_subsystem().destroy_actor(vehicle)
        raise RuntimeError("M10: failed to spawn vehicle interaction proxy")

    proxy.set_actor_label(PREFIX + "SportsCarInteraction")
    set_tags(proxy, "OWNoPopulationSpawn")

    try:
        proxy.initialize_vehicle(vehicle)
    except Exception as exc:
        actor_subsystem().destroy_actor(proxy)
        actor_subsystem().destroy_actor(vehicle)
        raise RuntimeError(
            "M10: failed to link interaction proxy to SportsCar: {}".format(exc)
        )

    saved = unreal.EditorAssetLibrary.save_asset(
        TARGET_MAP,
        only_if_is_dirty=False,
    )
    if not saved:
        raise RuntimeError(
            "M10: failed to save {}. Close all Unreal Editor windows and rerun.".format(
                TARGET_MAP
            )
        )

    unreal.log("M10: spawned {}".format(vehicle.get_actor_label()))
    unreal.log("M10: spawned {}".format(proxy.get_actor_label()))
    unreal.log("M10: CHAOS SPORTS CAR CITY INTEGRATION COMPLETE")
    unreal.log("M10: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
