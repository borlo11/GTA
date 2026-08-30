# Milestone 2 — Vehicle Vertical Prototype

## Goal

Milestone 2 adds one deliberately small vehicle gameplay loop on top of the validated Milestone 1 foundation:

1. approach one vehicle on foot,
2. press **E** to enter,
3. drive with **W/S** and steer with **A/D**,
4. look with the mouse,
5. brake with **Space**,
6. press **E** to exit back to the original character.

This milestone is a gameplay/ownership prototype, not the final vehicle-physics solution.

## Scope

Included:

- one native C++ prototype vehicle pawn,
- interaction-driven enter/exit,
- possession transfer between character and vehicle,
- vehicle-specific Enhanced Input mapping context,
- third-person vehicle camera,
- deterministic M2 bootstrap into the existing M1 test map,
- headless M2 validation,
- automation coverage for vehicle defaults,
- 60 FPS discipline and no custom Actor Tick.

Explicitly excluded:

- Chaos wheeled-vehicle tuning,
- production vehicle meshes or licensed third-party content,
- traffic,
- AI drivers,
- vehicle damage,
- doors/seat animations,
- multiple seats,
- weapons,
- police,
- missions,
- garages,
- persistence.

## Prototype movement model

`AOWPrototypeVehicle` currently uses `UFloatingPawnMovement` and a simple speed-scaled yaw steer.

That is intentional for M2. It lets the project validate possession, input ownership, camera switching and enter/exit behavior without requiring a skeletal vehicle, Physics Asset, wheel Blueprints or production car content.

A later milestone may replace the movement implementation behind the same gameplay boundary with Chaos Vehicles after the interaction loop is proven and representative vehicle assets exist.

## Input assets

`Content/Python/bootstrap_m2.py` creates or repairs:

- `IA_VehicleThrottle` — Axis1D
- `IA_VehicleSteer` — Axis1D
- `IA_VehicleBrake` — Boolean
- `IA_VehicleExit` — Boolean
- `IMC_Vehicle`

Mappings:

- W → throttle +1
- S → throttle -1
- A → steer -1
- D → steer +1
- Mouse X/Y → existing `IA_Look`
- Space → brake
- E → exit vehicle

The vehicle mapping context is added only while the vehicle is possessed and removed on unpossession. `IMC_Default` remains active, so `IMC_Vehicle` intentionally does not duplicate the Mouse X/Y mappings.

## Editor bootstrap

After the C++ module builds, run:

```powershell
& "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "C:\Users\MyPC\Documents\OWGame\OWGame.uproject" `
  -run=pythonscript `
  -script="C:\Users\MyPC\Documents\OWGame\Content\Python\bootstrap_m2.py" `
  -stdout -unattended -nosplash
```

The script uses the existing `/Game/Maps/M1_TestMap` and adds one always-loaded World Partition actor labelled `OW_M2_Vehicle`.

It does not fabricate binary assets outside the real Unreal Editor.

## Headless validation

After bootstrap, run:

```powershell
& "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "C:\Users\MyPC\Documents\OWGame\OWGame.uproject" `
  -run=pythonscript `
  -script="C:\Users\MyPC\Documents\OWGame\Content\Python\validate_m2.py" `
  -stdout -unattended -nosplash
```

Required log marker: `VALIDATE_M2: ALL CHECKS PASSED`.

## Required local validation

ChatGPT source changes are not considered a completed M2 until the local UE 5.8 machine verifies them.

Build:

```powershell
$Project = (Resolve-Path ".\OWGame.uproject").Path
& "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat" `
  OWGameEditor Win64 Development "-Project=$Project" -WaitMutex
```

Required result: `Result: Succeeded`.

Then run the M2 bootstrap, `validate_m2.py`, and Unreal Automation tests matching `OWGame.Vehicle.*`.

Finally perform a short PIE check:

- character spawns,
- walking/camera still work,
- E enters the vehicle,
- vehicle camera becomes active,
- W/S move the vehicle,
- A/D steer only while moving,
- Space stops the prototype vehicle,
- E exits to the character,
- character visibility/collision/movement are restored.

## Performance

The prototype vehicle actor itself has custom Actor Tick disabled. Movement is handled by Unreal's movement component and steering work occurs only from Enhanced Input events.

For M2, profile one vehicle in the test map with `stat unit` and `stat game`. The milestone must not be used to justify traffic-scale performance assumptions.
