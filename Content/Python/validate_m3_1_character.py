# validate_m3_1_character.py
# Validates that Unreal Engine's free Third Person template character assets
# are present in the current project. Does not create or modify assets.

import unreal

CANDIDATES = [
    (
        "Manny",
        "/Game/Characters/Mannequins/Meshes/SKM_Manny",
        "/Game/Characters/Mannequins/Animations/ABP_Manny",
    ),
    (
        "Quinn",
        "/Game/Characters/Mannequins/Meshes/SKM_Quinn",
        "/Game/Characters/Mannequins/Animations/ABP_Quinn",
    ),
]


def require(condition, message):
    if not condition:
        raise RuntimeError("VALIDATE_M3_1: " + message)


def main():
    found = None

    for label, mesh_path, anim_bp_path in CANDIDATES:
        if (
            unreal.EditorAssetLibrary.does_asset_exist(mesh_path)
            and unreal.EditorAssetLibrary.does_asset_exist(anim_bp_path)
        ):
            found = (label, mesh_path, anim_bp_path)
            break

    require(
        found is not None,
        "Third Person template mannequin assets are missing. "
        "Add the Third Person feature/content pack to this project first.",
    )

    label, mesh_path, anim_bp_path = found

    mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
    anim_bp = unreal.EditorAssetLibrary.load_asset(anim_bp_path)

    require(mesh is not None, "could not load {}".format(mesh_path))
    require(anim_bp is not None, "could not load {}".format(anim_bp_path))

    unreal.log(
        "VALIDATE_M3_1: {} mesh and animation blueprint are present".format(label)
    )
    unreal.log("VALIDATE_M3_1: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
