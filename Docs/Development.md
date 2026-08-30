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

## One-command Milestone 1 editor bootstrap

The project enables Unreal's Python Editor Script Plugin.

After the C++ module is built and the test map is open, run this from the Unreal Output Log while it is in Cmd mode:

```text
py "C:\Users\MyPC\Documents\OWGame\Content\Python\bootstrap_m1.py"
```

Adjust the path only if the repository is cloned elsewhere.

The script is idempotent and will create or repair:

- `IA_Move` as Axis2D
- `IA_Look` as Axis2D
- `IA_Jump` as Boolean
- `IA_Interact` as Boolean
- `IMC_Default`
- WASD movement mappings
- Mouse X/Y look mappings
- Space jump
- E interact
- a small deterministic M1 test platform
- an M1 PlayerStart
- one visible `AOWTestInteractable` cube

The native `AOWGameCharacter` resolves these input assets from `/Game/Input` automatically, so a Blueprint character is not required for Milestone 1.

## Enhanced Input asset setup

Binary `.uasset` files are generated through the real Unreal Editor rather than fabricated in source control.

Expected assets:

- `IA_Move`: Axis2D
- `IA_Look`: Axis2D
- `IA_Jump`: Boolean
- `IA_Interact`: Boolean
- `IMC_Default`: Input Mapping Context

Baseline mappings:

- W/S/A/D -> Move
- Mouse X/Y -> Look
- Space -> Jump
- E -> Interact

## Test interactable

The bootstrap script places one `AOWTestInteractable` using the engine cube mesh. Interaction logs through `LogOWGame`.

## Tests

With UE installed, run the Unreal Automation tests matching:

`OWGame.Foundation.*`

If UE is unavailable, report tests as **NOT EXECUTED**.

## Source-control hygiene

Never commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, IDE state, or generated build artifacts.
