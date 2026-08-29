# OWGame Architecture

## Purpose

OWGame is the internal technical codename for an original Unreal Engine 5.8 open-world action-game foundation. The repository intentionally starts small. Systems are added only after their ownership, performance cost, and extension points are understood.

## Current runtime module

`OWGame` is a single runtime module for Milestone 1. Splitting into additional modules is intentionally deferred until boundaries are justified by real code.

## Game framework

- `AOWGameGameMode`: selects the native player pawn and controller.
- `AOWGamePlayerController`: minimal controller foundation.
- `AOWGameCharacter`: third-person movement, camera, Enhanced Input binding hooks, and a small interaction trace.
- `IOWInteractable`: reusable interaction contract.
- `AOWTestInteractable`: validation actor only.

No GameState or PlayerState is created yet because Milestone 1 has no persistent match/player state that requires them.

## Input

The C++ layer expects Enhanced Input assets for Move, Look, Jump, Interact, and one mapping context. Binary assets are deliberately not fabricated in source control. See Development.md for the editor setup.

## Interaction

The character performs an interaction trace only when the Interact action fires. It does not continuously scan every frame. Hit actors opt in through `IOWInteractable`, keeping doors, vehicles, NPCs, shops, and other future systems out of the character class.

## Ownership and lifetime

Character-owned camera components use Unreal default-subobject ownership. Input assets are UObject references exposed as defaults. World actors are not retained by the character after interaction, avoiding unnecessary lifetime coupling.

## Deferred large-world technology

Likely future UE systems include World Partition, One File Per Actor, Data Layers, HLOD, async asset loading, PCG, and potentially Mass for high-count simulation. None is committed as a hard dependency yet.

Mass, GAS, PCG-heavy generation, custom streaming layers, and bespoke ECS architecture must be introduced only when a milestone demonstrates a concrete need and profiling supports the cost.

## Performance philosophy

The project targets 60 FPS (16.67 ms). Tick is disabled by default on current custom actors. Optimization should be profiling-led, while obvious scalability traps are rejected early.

## Extension direction

Future systems should communicate through narrow interfaces, components, subsystems, events, or data where appropriate. Global singletons and giant manager classes should be avoided unless lifecycle/ownership evidence clearly supports them.
