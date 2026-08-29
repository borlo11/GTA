# Development

## Requirements

- Unreal Engine 5.8
- Windows PC initial target
- Visual Studio 2022 with the Unreal-supported C++ toolchain

## Opening the project

1. Install Unreal Engine 5.8 locally.
2. Clone the repository.
3. Right-click `OWGame.uproject` and generate Visual Studio project files if required.
4. Build `OWGameEditor` for Win64 Development Editor.
5. Open `OWGame.uproject`.

Cloud background agents are not expected to have Unreal Engine installed. They must not stall trying to install it.

## Enhanced Input asset setup

The repository intentionally does not fabricate binary `.uasset` files.

In the editor create:

- `IA_Move`: Axis2D
- `IA_Look`: Axis2D
- `IA_Jump`: Boolean
- `IA_Interact`: Boolean
- `IMC_Default`: Input Mapping Context

Suggested baseline mappings:

- W/S/A/D -> Move
- Mouse XY -> Look
- Space -> Jump
- E -> Interact

Create a Blueprint child of `AOWGameCharacter` only if needed to assign the four actions and mapping context, then configure that pawn in a derived GameMode or set the native defaults appropriately. Do not add unrelated gameplay logic to the Blueprint.

## Test interactable

Place `AOWTestInteractable` in a test map and give its Mesh component any safe local primitive/static mesh if visual feedback is desired. Interaction logs through `LogOWGame`.

## Tests

With UE installed, run the Unreal Automation tests matching:

`OWGame.Foundation.*`

If UE is unavailable, report tests as **NOT EXECUTED**.

## Source-control hygiene

Never commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, IDE state, or generated build artifacts.
