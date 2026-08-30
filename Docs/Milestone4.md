# Milestone 4 — NPC / Population Prototype

## Goal

Milestone 4 gives the test world a small autonomous pedestrian population while keeping the architecture intentionally lightweight and measurable.

This is not yet a city-scale crowd system. The milestone exists to validate ownership, spawn/despawn behavior, basic locomotion, simulation LOD, and performance discipline before population counts increase.

## Runtime structure

### AOWPopulationManager

The GameMode creates one population manager at runtime.

The manager:

- targets a small population of 8 pedestrians by default,
- samples spawn points around the currently possessed player pawn,
- traces down to find valid ground,
- despawns pedestrians that become too far from the player,
- replaces despawned pedestrians near the new player location,
- assigns simulation tiers based on distance,
- updates at a fixed low frequency rather than every frame.

The currently possessed pawn is used as the population reference, so the same system follows the player while on foot or while driving the M2 vehicle.

### AOWPopulationNPC

Each pedestrian is an ACharacter using the free UE Third Person mannequin assets imported for M3.1.

Manny and Quinn are alternated deterministically to avoid a completely identical crowd.

Pedestrians:

- use ABP_Unarmed for locomotion,
- choose local wandering destinations around a home point,
- occasionally stop and idle,
- use a minimal Actor Tick only while active to feed CharacterMovement smoothly,
- keep destination/idle decisions on timers rather than doing global logic every frame,
- reduce update frequency as they get farther from the player.

## Simulation tiers

Default prototype tiers:

- High: nearest population, 0.05 s decision interval
- Medium: 0.15 s
- Low: 0.45 s
- Dormant: custom movement and skeletal component ticking disabled
- Despawn: actor removed and later replaced near the player

Distances are configurable on the population manager.

This is an early simulation-LOD experiment, not the final crowd architecture.

## Spawn/despawn

The manager performs ground traces before spawning and ignores already spawned population actors during those traces.

Spawn collision handling uses AdjustIfPossibleButAlwaysSpawn so a failed exact position does not collapse the entire population prototype.

The target count is intentionally small while behavior and cost are being validated.

## Performance rules

- No custom Actor Tick on the population manager.
- Pedestrian NPC Actor Tick is limited to active smooth locomotion input; dormant NPCs disable it.
- No repeated GetAllActorsOfClass scans.
- Population management runs on a 0.5 s timer by default.
- Pedestrian decision updates use tiered timers.
- CharacterMovement and skeletal animation still use their normal engine component lifecycles when active.
- Dormant pedestrians disable movement and skeletal component ticks.

The architectural target remains 60 FPS / 16.67 ms.

## Explicitly excluded

Milestone 4 does not add:

- police,
- crime,
- combat,
- weapons,
- pedestrian dialogue,
- reactions to the player,
- traffic,
- navmesh/pathfinding,
- Mass Entity,
- Smart Objects,
- city-scale spawning,
- persistent NPC identities.

Those should only be introduced after this prototype is profiled and understood.

## Local validation

Build OWGameEditor Win64 Development with Unreal Engine 5.8.

Required:

`Result: Succeeded`

Run automation suites:

- OWGame.Foundation.*
- OWGame.Vehicle.*
- OWGame.Character.*
- OWGame.Population.*

Required:

`TEST COMPLETE. EXIT CODE: 0`

## PIE acceptance checklist

On M1_TestMap:

- the existing player still spawns as Manny,
- M1 interaction still works,
- the M2 vehicle still supports enter/drive/exit,
- several pedestrian mannequins appear automatically,
- pedestrians visibly alternate between idle and walking,
- they remain near local wandering areas instead of walking forever in one direction,
- moving far away in the vehicle eventually removes old population,
- replacement pedestrians appear around the player's new area when ground is available,
- returning on foot after vehicle exit still works,
- there are no obvious per-frame population log floods or custom actor-tick regressions.

## Next step

After M4 is validated and profiled, M5 can introduce the first minimal crime/police response prototype without turning the population experiment into a monolithic AI system.
