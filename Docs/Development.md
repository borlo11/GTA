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

If UE is unavailable, report tests as **NOT EXECUTED**.

## Source-control hygiene

Never commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, IDE state, or generated build artifacts.
