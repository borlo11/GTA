# Milestone 3.1 — Free Skeletal Character Upgrade

## Goal

Replace the M3 primitive humanoid with a real Unreal Engine skeletal mannequin and its locomotion animation blueprint, without paying for third-party assets and without changing the M4 NPC milestone.

## Asset source

M3.1 uses the character content shipped with Unreal Engine's **Third Person** template.

Preferred character:

- Manny

Fallback:

- Quinn

Expected project paths:

- `/Game/Characters/Mannequins/Meshes/SKM_Manny`
- `/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed`

The character code also supports Quinn at the equivalent paths.

## Why this source

The UE 5.8 Third Person template already contains the UE5 mannequins, their skeletal meshes, Animation Blueprints, rigs, and locomotion animations.

No paid marketplace asset is required.

## Runtime behavior

`AOWGameCharacter` first attempts to load `SKM_Manny_Simple` with `ABP_Unarmed` from the UE 5.8 template content at BeginPlay.

If both are present:

- the inherited Character skeletal-mesh component becomes visible,
- Manny is positioned/rotated to fit the capsule,
- `ABP_Manny` drives locomotion,
- the M3 primitive body is hidden.

If Manny is unavailable, the code tries Quinn.

If neither template character is installed, the project safely falls back to the validated M3 primitive humanoid rather than breaking gameplay.

## Adding the free template content

Inside the Unreal Editor Content Browser:

1. click **Add (+)**,
2. choose **Add Feature or Content Pack**,
3. choose **Third Person**,
4. add it to this project.

This imports Epic's Third Person template content into the existing project. It should not replace the OWGame GameMode or C++ gameplay classes.

## Validation

After adding the content, run:

```powershell
& "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "C:\Users\MyPC\Documents\OWGame\OWGame.uproject" `
  -run=pythonscript `
  -script="C:\Users\MyPC\Documents\OWGame\Content\Python\validate_m3_1_character.py" `
  -stdout -unattended -nosplash
```

Required marker:

`VALIDATE_M3_1: ALL CHECKS PASSED`

Then build `OWGameEditor Win64 Development` and run the existing Foundation, Vehicle, and Character automation suites.

## PIE acceptance

- real Manny or Quinn body is visible,
- idle animation is active while stationary,
- locomotion animation responds to movement,
- walk/sprint transition remains compatible with M3 speeds,
- jump/fall animation responds to Space and airborne state,
- camera and interaction prompt still work,
- vehicle enter/drive/exit still works,
- skeletal character becomes visible again after exiting the vehicle.

## Scope

M3.1 does not add Motion Matching, custom animation authoring, combat animation, NPC animation logic, or paid character content.

Those remain later concerns.
