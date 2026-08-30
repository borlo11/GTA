# bootstrap_m1.py
# Milestone 1 editor bootstrap for OWGame (Unreal Engine 5.8).
#
# Idempotent. Safe to run multiple times. Never deletes user content.
#
# Creates/repairs:
#   /Game/Input/IA_Move      (Axis2D)
#   /Game/Input/IA_Look      (Axis2D)
#   /Game/Input/IA_Jump      (Bool)
#   /Game/Input/IA_Interact  (Bool)
#   /Game/Input/IMC_Default  (WASD / Mouse / Space / E mappings)
#
# Ensures in /Game/Maps/M1_TestMap (without damaging existing content):
#   - a test platform (labelled OW_M1_Platform)
#   - a PlayerStart (labelled OW_M1_PlayerStart)
#   - a visible AOWTestInteractable (labelled OW_M1_Interactable)
#
# Run headless:
#   UnrealEditor-Cmd.exe <project> -run=pythonscript -script=".../bootstrap_m1.py"

import unreal

INPUT_DIR = "/Game/Input"
MAP_PATH = "/Game/Maps/M1_TestMap"

PLATFORM_LABEL = "OW_M1_Platform"
PLAYERSTART_LABEL = "OW_M1_PlayerStart"
INTERACTABLE_LABEL = "OW_M1_Interactable"

PLATFORM_LOCATION = unreal.Vector(0.0, 0.0, 0.0)
PLATFORM_SCALE = unreal.Vector(20.0, 20.0, 1.0)
PLAYERSTART_LOCATION = unreal.Vector(0.0, -400.0, 150.0)
INTERACTABLE_LOCATION = unreal.Vector(0.0, 300.0, 130.0)

CUBE_MESH_PATH = "/Engine/BasicShapes/Cube.Cube"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
log = unreal.log
warn = unreal.log_warning


def make_factory(asset_class):
	"""Return a factory able to create asset_class.

	UE 5.8 does not expose the Enhanced Input factories to Python, but both
	UInputAction and UInputMappingContext derive from UDataAsset, so fall
	back to DataAssetFactory with data_asset_class set.
	"""
	dedicated = getattr(unreal, asset_class.__name__ + "Factory", None)
	if dedicated is not None:
		return dedicated()
	factory = unreal.DataAssetFactory()
	factory.set_editor_property("data_asset_class", asset_class)
	return factory


def ensure_asset(name, asset_class, factory):
	"""Load an existing asset or create it. Returns the asset object."""
	object_path = "{}/{}".format(INPUT_DIR, name)
	if unreal.EditorAssetLibrary.does_asset_exist(object_path):
		asset = unreal.EditorAssetLibrary.load_asset(object_path)
		if asset is None or not isinstance(asset, asset_class):
			raise RuntimeError(
				"Asset {} exists but is not a {}".format(object_path, asset_class.__name__))
		log("bootstrap_m1: found existing {}".format(object_path))
		return asset
	asset = asset_tools.create_asset(name, INPUT_DIR, asset_class, factory)
	if asset is None:
		raise RuntimeError("Failed to create {}".format(object_path))
	log("bootstrap_m1: created {}".format(object_path))
	return asset


def ensure_input_action(name, value_type):
	action = ensure_asset(name, unreal.InputAction, make_factory(unreal.InputAction))
	if action.get_editor_property("value_type") != value_type:
		action.set_editor_property("value_type", value_type)
		unreal.EditorAssetLibrary.save_loaded_asset(action)
		log("bootstrap_m1: set {} value_type={}".format(name, value_type))
	return action


def make_modifier(imc, modifier_class, props=None):
	modifier = unreal.new_object(modifier_class, outer=imc)
	if props:
		for key, value in props.items():
			modifier.set_editor_property(key, value)
	return modifier


def ensure_mapping(imc, action, key_name, modifier_specs):
	"""modifier_specs: list of (class, props-dict) applied to the mapping."""
	key = unreal.Key()
	key.set_editor_property("key_name", key_name)
	mappings = list(imc.get_editor_property("mappings"))

	for m in mappings:
		if m.get_editor_property("action") == action and \
		   str(m.get_editor_property("key").get_editor_property("key_name")) == key_name:
			return False  # already mapped; leave user configuration intact

	mapping = unreal.EnhancedActionKeyMapping()
	mapping.set_editor_property("action", action)
	mapping.set_editor_property("key", key)
	modifiers = [make_modifier(imc, cls, props) for cls, props in modifier_specs]
	mapping.set_editor_property("modifiers", modifiers)
	mappings.append(mapping)
	imc.set_editor_property("mappings", mappings)
	log("bootstrap_m1: mapped {} -> {}".format(key_name, action.get_name()))
	return True


def setup_input_assets():
	if not unreal.EditorAssetLibrary.does_directory_exist(INPUT_DIR):
		unreal.EditorAssetLibrary.make_directory(INPUT_DIR)

	ia_move = ensure_input_action("IA_Move", unreal.InputActionValueType.AXIS2D)
	ia_look = ensure_input_action("IA_Look", unreal.InputActionValueType.AXIS2D)
	ia_jump = ensure_input_action("IA_Jump", unreal.InputActionValueType.BOOLEAN)
	ia_interact = ensure_input_action("IA_Interact", unreal.InputActionValueType.BOOLEAN)

	imc = ensure_asset("IMC_Default", unreal.InputMappingContext,
					   make_factory(unreal.InputMappingContext))

	swizzle = (unreal.InputModifierSwizzleAxis, None)  # default YXZ: routes value to Y
	negate = (unreal.InputModifierNegate, None)

	changed = False
	# Move: W=+Y, S=-Y, A=-X, D=+X
	changed |= ensure_mapping(imc, ia_move, "W", [swizzle])
	changed |= ensure_mapping(imc, ia_move, "S", [negate, swizzle])
	changed |= ensure_mapping(imc, ia_move, "A", [negate])
	changed |= ensure_mapping(imc, ia_move, "D", [])
	# Look: Mouse X -> X, Mouse Y -> Y (negated for natural pitch)
	changed |= ensure_mapping(imc, ia_look, "MouseX", [])
	changed |= ensure_mapping(imc, ia_look, "MouseY", [negate])
	# Jump / Interact
	changed |= ensure_mapping(imc, ia_jump, "SpaceBar", [])
	changed |= ensure_mapping(imc, ia_interact, "E", [])

	if changed:
		unreal.EditorAssetLibrary.save_loaded_asset(imc)
	log("bootstrap_m1: input assets OK")


def find_actor_by_label(actor_subsystem, label):
	for actor in actor_subsystem.get_all_level_actors():
		if actor and actor.get_actor_label() == label:
			return actor
	return None


def mark_always_loaded(actor):
	"""World Partition: keep M1 reference actors always loaded so they are
	found again on the next editor/commandlet session (idempotency)."""
	try:
		actor.set_editor_property("is_spatially_loaded", False)
	except Exception:
		pass  # non-WP map or property unavailable


def setup_test_level():
	if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
		raise RuntimeError("Map {} not found; refusing to create a new one over user content".format(MAP_PATH))

	unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
	actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

	dirty = False

	# Platform
	platform = find_actor_by_label(actor_subsystem, PLATFORM_LABEL)
	if platform is None:
		platform = actor_subsystem.spawn_actor_from_class(
			unreal.StaticMeshActor, PLATFORM_LOCATION, unreal.Rotator(0, 0, 0))
		platform.set_actor_label(PLATFORM_LABEL)
		mark_always_loaded(platform)
		mesh_comp = platform.static_mesh_component
		mesh_comp.set_mobility(unreal.ComponentMobility.STATIC)
		mesh_comp.set_static_mesh(unreal.load_asset(CUBE_MESH_PATH))
		platform.set_actor_scale3d(PLATFORM_SCALE)
		dirty = True
		log("bootstrap_m1: spawned platform")

	# PlayerStart
	player_start = find_actor_by_label(actor_subsystem, PLAYERSTART_LABEL)
	if player_start is None:
		existing_starts = unreal.GameplayStatics.get_all_actors_of_class(
			unreal.EditorLevelLibrary.get_editor_world(), unreal.PlayerStart)
		if existing_starts:
			log("bootstrap_m1: PlayerStart already present; keeping user setup")
		else:
			player_start = actor_subsystem.spawn_actor_from_class(
				unreal.PlayerStart, PLAYERSTART_LOCATION, unreal.Rotator(0, 0, 90))
			player_start.set_actor_label(PLAYERSTART_LABEL)
			mark_always_loaded(player_start)
			dirty = True
			log("bootstrap_m1: spawned PlayerStart")

	# Test interactable
	interactable = find_actor_by_label(actor_subsystem, INTERACTABLE_LABEL)
	if interactable is None:
		interactable_class = unreal.load_class(None, "/Script/OWGame.OWTestInteractable")
		if interactable_class is None:
			raise RuntimeError("Could not load /Script/OWGame.OWTestInteractable; is the C++ module built?")
		interactable = actor_subsystem.spawn_actor_from_class(
			interactable_class, INTERACTABLE_LOCATION, unreal.Rotator(0, 0, 0))
		interactable.set_actor_label(INTERACTABLE_LABEL)
		mark_always_loaded(interactable)
		dirty = True
		log("bootstrap_m1: spawned test interactable")

	# Ensure the interactable has a visible mesh (C++ leaves it unset)
	mesh_comp = interactable.get_component_by_class(unreal.StaticMeshComponent)
	if mesh_comp and mesh_comp.static_mesh is None:
		mesh_comp.set_static_mesh(unreal.load_asset(CUBE_MESH_PATH))
		dirty = True
		log("bootstrap_m1: assigned cube mesh to interactable")

	if dirty:
		unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
		log("bootstrap_m1: saved map")
	log("bootstrap_m1: test level OK")


def main():
	setup_input_assets()
	setup_test_level()
	log("bootstrap_m1: DONE")


if __name__ == "__main__":
	main()
