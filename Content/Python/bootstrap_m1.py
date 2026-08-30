import unreal

INPUT_DIR = "/Game/Input"
MOVE_PATH = f"{INPUT_DIR}/IA_Move"
LOOK_PATH = f"{INPUT_DIR}/IA_Look"
JUMP_PATH = f"{INPUT_DIR}/IA_Jump"
INTERACT_PATH = f"{INPUT_DIR}/IA_Interact"
IMC_PATH = f"{INPUT_DIR}/IMC_Default"

PLATFORM_LABEL = "M1_TestPlatform"
PLAYER_START_LABEL = "M1_PlayerStart"
INTERACTABLE_LABEL = "M1_TestInteractable"


def log(message):
    unreal.log(f"[OWGame Bootstrap] {message}")


def warn(message):
    unreal.log_warning(f"[OWGame Bootstrap] {message}")


def make_key(name):
    key = unreal.Key()
    key.set_editor_property("key_name", unreal.Name(name))
    return key


def load_or_create_input_action(name, value_type):
    path = f"{INPUT_DIR}/{name}"
    asset = unreal.load_asset(path)

    if asset is None:
        factory = unreal.InputAction_Factory()
        asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name,
            INPUT_DIR,
            unreal.InputAction,
            factory,
        )

    if asset is None:
        raise RuntimeError(f"Could not create {path}")

    asset.set_editor_property("value_type", value_type)
    return asset


def load_or_create_mapping_context():
    asset = unreal.load_asset(IMC_PATH)

    if asset is None:
        factory = unreal.InputMappingContext_Factory()
        asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "IMC_Default",
            INPUT_DIR,
            unreal.InputMappingContext,
            factory,
        )

    if asset is None:
        raise RuntimeError(f"Could not create {IMC_PATH}")

    return asset


def swizzle_y(outer):
    modifier = unreal.InputModifierSwizzleAxis(outer=outer)
    modifier.set_editor_property("order", unreal.InputAxisSwizzle.YXZ)
    return modifier


def negate_x(outer):
    modifier = unreal.InputModifierNegate(outer=outer)
    modifier.set_editor_property("x", True)
    modifier.set_editor_property("y", False)
    modifier.set_editor_property("z", False)
    return modifier


def mapping(action, key_name, modifiers=None):
    return unreal.EnhancedActionKeyMapping(
        action=action,
        key=make_key(key_name),
        modifiers=modifiers or [],
    )


def configure_input():
    log("Configuring Enhanced Input assets...")

    move = load_or_create_input_action(
        "IA_Move",
        unreal.InputActionValueType.AXIS2D,
    )
    look = load_or_create_input_action(
        "IA_Look",
        unreal.InputActionValueType.AXIS2D,
    )
    jump = load_or_create_input_action(
        "IA_Jump",
        unreal.InputActionValueType.BOOLEAN,
    )
    interact = load_or_create_input_action(
        "IA_Interact",
        unreal.InputActionValueType.BOOLEAN,
    )

    imc = load_or_create_mapping_context()

    mappings = [
        # Move: X = right/left, Y = forward/back.
        mapping(move, "W", [swizzle_y(imc)]),
        mapping(move, "S", [negate_x(imc), swizzle_y(imc)]),
        mapping(move, "A", [negate_x(imc)]),
        mapping(move, "D"),

        # Look: assemble a Vector2D from the two scalar mouse axes.
        mapping(look, "MouseX"),
        mapping(look, "MouseY", [swizzle_y(imc)]),

        # Actions.
        mapping(jump, "SpaceBar"),
        mapping(interact, "E"),
    ]

    imc.set_editor_property("mappings", mappings)

    asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    for path in [MOVE_PATH, LOOK_PATH, JUMP_PATH, INTERACT_PATH, IMC_PATH]:
        if not asset_subsystem.save_asset(path, False):
            warn(f"Asset save reported failure for {path}")

    log("Enhanced Input ready: WASD, mouse, Space, E.")
    return move, look, jump, interact, imc


def find_actor_by_label(actor_subsystem, label):
    for actor in actor_subsystem.get_all_level_actors():
        try:
            if actor.get_actor_label() == label:
                return actor
        except Exception:
            pass
    return None


def ensure_test_arena():
    log("Ensuring M1 test arena exists in the current level...")

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if cube is None:
        warn("Engine cube asset not found; skipping visual test arena.")
        return

    platform = find_actor_by_label(actor_subsystem, PLATFORM_LABEL)
    if platform is None:
        platform = actor_subsystem.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(0.0, 0.0, 1000.0),
            unreal.Rotator(0.0, 0.0, 0.0),
            False,
        )
        platform.set_actor_label(PLATFORM_LABEL)
        platform.set_actor_scale3d(unreal.Vector(20.0, 20.0, 0.5))

    platform_mesh = platform.get_component_by_class(unreal.StaticMeshComponent)
    if platform_mesh:
        platform_mesh.set_static_mesh(cube)

    player_start = find_actor_by_label(actor_subsystem, PLAYER_START_LABEL)
    if player_start is None:
        player_start = actor_subsystem.spawn_actor_from_class(
            unreal.PlayerStart,
            unreal.Vector(0.0, 0.0, 1130.0),
            unreal.Rotator(0.0, 0.0, 0.0),
            False,
        )
        player_start.set_actor_label(PLAYER_START_LABEL)

    test_class = unreal.load_class(None, "/Script/OWGame.OWTestInteractable")
    if test_class is None:
        warn("OWTestInteractable class was not found; build the C++ module first.")
    else:
        test_actor = find_actor_by_label(actor_subsystem, INTERACTABLE_LABEL)
        if test_actor is None:
            test_actor = actor_subsystem.spawn_actor_from_class(
                test_class,
                unreal.Vector(250.0, 0.0, 1075.0),
                unreal.Rotator(0.0, 0.0, 0.0),
                False,
            )
            test_actor.set_actor_label(INTERACTABLE_LABEL)

        test_mesh = test_actor.get_component_by_class(unreal.StaticMeshComponent)
        if test_mesh:
            test_mesh.set_static_mesh(cube)
            test_actor.set_actor_scale3d(unreal.Vector(0.75, 0.75, 0.75))

    if not level_subsystem.save_current_level():
        warn("Could not save the current level automatically. Use Save All once.")
    else:
        log("Current level saved with the M1 test arena.")


def run():
    log("Starting Milestone 1 bootstrap.")
    configure_input()
    ensure_test_arena()
    log("DONE. Press Play: WASD move, mouse look, Space jump, E interact.")


if __name__ == "__main__":
    run()
