# OWGame Architecture

## Purpose

OWGame is the internal technical codename for an original Unreal Engine 5.8 open-world action-game foundation. The repository intentionally starts small. Systems are added only after their ownership, performance cost, and extension points are understood.

## Current runtime module

`OWGame` remains a single runtime module through Milestone 4. Splitting into additional modules is intentionally deferred until boundaries are justified by real code.

## Game framework

- `AOWGameGameMode`: selects the native player pawn and controller.
- `AOWGamePlayerController`: minimal controller foundation.
- `AOWGameCharacter`: third-person movement, sprint, shoulder camera, Enhanced Input, timer-driven interaction focus, and optional UE Third Person template skeletal visuals with a safe primitive fallback.
- `IOWInteractable`: reusable interaction contract.
- `AOWTestInteractable`: Milestone 1 validation actor.
- `AOWPrototypeVehicle`: Milestone 2 enterable prototype pawn with vehicle input, camera, possession transfer, and an M3 contextual prompt.
- `AOWGameHUD`: Milestone 3 lightweight contextual interaction HUD.
- `AOWPopulationManager`: Milestone 4 runtime owner for a small pedestrian population, spawn/despawn, and distance-based simulation LOD.
- `AOWPopulationNPC`: Milestone 4 mannequin pedestrian with timer-driven local wandering and no custom Actor Tick.

No GameState or PlayerState is created yet because the current milestones have no persistent match/player state that requires them.

Milestone 4 population ownership lives in a world actor spawned by the authoritative GameMode. It is intentionally not a global singleton.

## Input

Milestone 1 uses `IMC_Default` for on-foot Move, Look, Jump, and Interact.

Milestone 2 adds `IMC_Vehicle` for throttle, steer, brake, exit, and vehicle camera look. The vehicle context is added while the vehicle is possessed and removed on unpossession. Binary input assets are generated through the real Unreal Editor by the bootstrap scripts.

## Interaction

Milestone 3 extends the interaction contract with contextual prompt text. The character uses a low-frequency timer and a camera-forward sphere sweep to identify an interactable without enabling Actor Tick. Pressing Interact performs the same query immediately before dispatching the interface call.

The M2 vehicle implements the same interface, so entering a vehicle does not add vehicle-specific branching to `AOWGameCharacter`. The HUD simply reads the current prompt from the possessed on-foot character.

## Vehicle ownership

On enter, `AOWPrototypeVehicle` temporarily stores the originating `AOWGameCharacter`, disables that character's visibility/collision/movement, and transfers the existing player controller to the vehicle.

On exit, the character is restored at a vehicle-relative exit offset and the controller possesses the original character again.

The prototype intentionally uses `UFloatingPawnMovement` rather than production car physics. This isolates the gameplay ownership boundary from a future Chaos Vehicles implementation.

## Ownership and lifetime

Character and vehicle components use Unreal default-subobject ownership. Input assets are UObject references held by their owning pawn defaults.

The vehicle keeps a transient UObject-aware reference to the current driver only while occupied. It does not create a global vehicle manager or persistent singleton.

## Population

Milestone 4 introduces a deliberately small pedestrian prototype. The GameMode creates one `AOWPopulationManager`, which maintains a target count around the currently possessed player pawn. NPCs are spawned only after a downward ground trace succeeds, are despawned beyond a configurable distance, and are replaced near the player's current area.

`AOWPopulationNPC` uses the M3.1 mannequin assets and `ABP_Unarmed`. It uses a lightweight Actor Tick only while actively moving so CharacterMovement receives smooth per-frame movement input and ABP_Unarmed gets coherent locomotion data. Wander decisions remain timer-driven. Dormant NPCs disable the actor tick, movement component tick, and skeletal component tick.

No NavMesh, AIController, Mass Entity, Smart Objects, traffic, crime, or combat behavior is introduced by M4.

## Deferred large-world technology

World Partition is already present in the M1 test map, with deterministic milestone actors marked always loaded for headless validation. Broader One File Per Actor, Data Layers, HLOD, async asset loading, PCG, and potentially Mass remain future concerns.

Mass, GAS, PCG-heavy generation, custom streaming layers, and bespoke ECS architecture must be introduced only when a milestone demonstrates a concrete need and profiling supports the cost.

## Performance philosophy

The project targets 60 FPS (16.67 ms). Custom Actor Tick is disabled on the player character, test interactable, prototype vehicle, and population manager. M4 population NPCs use a minimal active-movement tick to feed CharacterMovement smoothly; that tick is disabled for dormant NPCs. M3 interaction focus and M4 population decisions use timers rather than per-frame global searches.

Optimization should be profiling-led, while obvious scalability traps are rejected early.

## Extension direction

Future systems should communicate through narrow interfaces, components, subsystems, events, or data where appropriate. Global singletons and giant manager classes should be avoided unless lifecycle/ownership evidence clearly supports them.
