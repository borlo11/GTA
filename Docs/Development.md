# Development

## Requirements

- Unreal Engine 5.8
- Windows PC initial target
- Visual Studio 2026 or another UE 5.8-supported C++ toolchain

## Opening the project

1. Install Unreal Engine 5.8 locally.
2. Clone the repository.
3. Right-click `OWGame.uproject` and generate Visual Studio project files if required.
4. Build `OWGameEditor` for Win64 Development Editor.
5. Open `OWGame.uproject`.

Cloud background agents are not expected to have Unreal Engine installed. They must not stall trying to install it.

## Milestone 1 bootstrap

The project enables Unreal's Python Editor Script Plugin.

Run the validated M1 bootstrap through Unreal:

```text
py "C:\Users\MyPC\Documents\OWGame\Content\Python\bootstrap_m1.py"
```

The script creates/repairs the M1 Enhanced Input assets and deterministic test actors in `/Game/Maps/M1_TestMap`.

## Milestone 2 vehicle prototype

Milestone 2 source and automation are documented in `Docs/Milestone2.md`.

After the M2 C++ source builds locally, run:

```powershell
& "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "C:\Users\MyPC\Documents\OWGame\OWGame.uproject" `
  -run=pythonscript `
  -script="C:\Users\MyPC\Documents\OWGame\Content\Python\bootstrap_m2.py" `
  -stdout -unattended -nosplash
```

Then run the same command with `Content\Python\validate_m2.py`. Required marker:

`VALIDATE_M2: ALL CHECKS PASSED`

## Milestone 3 character / interaction slice

Milestone 3 is code-only and does not require new binary assets. It adds the visible prototype character body, sprint, camera polish, timer-driven interaction focus, and contextual HUD. See `Docs/Milestone3.md`.

## Milestone 3.1 skeletal character upgrade

M3.1 uses the free Unreal Engine Third Person template mannequin content. Add the Third Person feature/content pack from the Content Browser, then run `Content/Python/validate_m3_1_character.py`. See `Docs/Milestone3_1.md`.

## Milestone 4 population prototype

M4 is code-only on top of the M3.1 mannequin content. It adds `AOWPopulationManager`, `AOWPopulationNPC`, distance-based simulation tiers, runtime spawn/despawn, timer-driven decisions, and a minimal active locomotion tick for smooth CharacterMovement input. See `Docs/Milestone4.md`.

## Milestone 4.5 lightweight city

M4.5 generates `/Game/Maps/OW_LightweightCity` with `Content/Python/bootstrap_lightweight_city.py`. Validate it with `Content/Python/validate_lightweight_city.py`. See `Docs/Milestone4_5.md`.

## Milestone 5 crime / police prototype

M5 is code-only on top of the M4.5 city. Press `F` in non-shipping builds to report a severity-1 prototype crime. Wanted state persists on `AOWGamePlayerController`, `AOWPoliceDirector` owns response spawning, and officers pursue/search the currently possessed pawn. See `Docs/Milestone5.md`.

## Milestone 6 combat prototype

M6 is code-only and requires no new binary input assets. While Manny is possessed, Left Mouse fires the prototype hitscan attack and Q performs melee. The reusable `UOWHealthComponent` is attached to player, population NPCs, and police. Combat reports into M5 wanted state. See `Docs/Milestone6.md`.

## Milestone 7 mission framework

M7 is code-only and requires no new binary assets. The persistent mission component lives on `AOWGamePlayerController`. In development builds, `R` starts/restarts Hot Run and `T` clears the mission save slot. Progress is stored through `UOWMissionSaveGame`. See `Docs/Milestone7.md`.

## Milestone 8 small open-world vertical slice

M8 integrates the previous systems into the first player-facing slice in `OW_LightweightCity`. A green in-world HOT RUN marker starts the mission with normal E interaction; F9 toggles a lightweight FPS/frame-time overlay. Run `Content/Python/validate_m8_vertical_slice.py` for the non-destructive city/World Partition inspection. See `Docs/Milestone8.md`.

## Input assets

On-foot baseline:

- `IA_Move`: Axis2D
- `IA_Look`: Axis2D
- `IA_Jump`: Boolean
- `IA_Interact`: Boolean
- `IMC_Default`

Vehicle prototype:

- `IA_VehicleThrottle`: Axis1D
- `IA_VehicleSteer`: Axis1D
- `IA_VehicleBrake`: Boolean
- `IA_VehicleExit`: Boolean
- `IMC_Vehicle`

Binary `.uasset` files must be generated through the real Unreal Editor rather than fabricated by source-control tooling.

## Tests

With UE installed, run Unreal Automation tests matching:

- `OWGame.Foundation.*`
- `OWGame.Vehicle.*`
- `OWGame.Character.*`
- `OWGame.Population.*`
- `OWGame.CrimePolice.*`
- `OWGame.Combat.*`
- `OWGame.Mission.*`
- `OWGame.VerticalSlice.*`

If UE is unavailable, report tests as **NOT EXECUTED**.

## Source-control hygiene

Never commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, IDE state, or generated build artifacts.
