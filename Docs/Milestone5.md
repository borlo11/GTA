# Milestone 5 — Crime / Police Prototype

## Goal

Milestone 5 adds the first reactive-world gameplay loop to OWGame:

crime report -> wanted level -> police response -> pursuit/search -> de-escalation.

It deliberately excludes combat and arrests. The purpose is to validate ownership, possession continuity, response spawning, line-of-sight observation, search behavior, and escape.

## Wanted ownership

Wanted state lives on `UOWWantedComponent`, a default subobject of `AOWGamePlayerController`.

This is intentional: the same PlayerController survives possession changes between Manny and the M2 prototype vehicle, so the wanted level is not lost when the player enters or exits a vehicle.

Prototype wanted range:

- 0: no response
- 1: one officer
- 2: two officers
- 3: three officers

Crime severity adds to the current level and clamps at 3.

## Debug crime trigger

During non-shipping builds, press:

`F`

to report a severity-1 prototype crime at the currently possessed pawn.

This is only a milestone test trigger. Future combat, missions, vehicle collisions, theft, and scripted events should call the wanted component directly instead of simulating keyboard input.

## Police response

`AOWPoliceDirector` is spawned by `AOWGameGameMode`.

It:

- runs on a 0.5 second timer,
- reads wanted state from the persistent OWGame PlayerController,
- spawns a small response around the last known player location,
- rejects obvious lightweight-city building rooftops as spawn ground,
- removes invalid or very distant officers,
- scales response count with wanted level,
- destroys the response when wanted returns to zero.

Police are not added to the M4 ambient population array.

## Police officers

`AOWPoliceOfficer` uses the UE mannequin and ABP_Unarmed.

Officers:

- use CharacterMovement and per-frame movement input for smooth locomotion,
- do not require an AIController or NavMesh in this prototype,
- use a visibility trace inside a limited sight range,
- refresh the wanted component's last-known location only while the player is visible,
- pursue the currently possessed pawn, so entering a vehicle does not break pursuit,
- search small randomized positions around the stale last-known location after losing sight,
- are visually marked with a blue POLICE text label.

Direct steering is intentionally temporary. NavMesh/pathfinding and vehicle police belong to later work.

## De-escalation

The wanted component checks de-escalation on a 1 second timer.

If police observation has not refreshed for 10 seconds:

- wanted level drops by one,
- another hidden 10-second period is required for the next drop,
- at level 0 the last-known location is cleared and police response is removed.

This means a level-3 response requires sustained escape rather than disappearing immediately.

## HUD

AOWGameHUD displays the wanted level independently of the currently possessed pawn, so it remains visible while driving.

The existing interaction prompt remains on-foot only.

## Local validation

Build:

`OWGameEditor Win64 Development`

Required:

`Result: Succeeded`

Run:

- `OWGame.Foundation.*`
- `OWGame.Vehicle.*`
- `OWGame.Character.*`
- `OWGame.Population.*`
- `OWGame.CrimePolice.*`

Required:

`TEST COMPLETE. EXIT CODE: 0`

## PIE acceptance in OW_LightweightCity

1. Spawn as Manny.
2. Press F once -> wanted level 1 appears and one police officer responds.
3. Press F again -> wanted level 2 and response grows.
4. Enter the M2 vehicle -> wanted HUD remains and police target the vehicle.
5. Drive far enough / break line of sight -> police search the last-known area instead of teleporting onto the player.
6. Stay unseen -> wanted drops one level after each decay delay.
7. At wanted 0 -> police response disappears.
8. Exit the vehicle -> Manny controls and existing M1-M4.5 gameplay remain functional.

## Explicitly deferred

- weapons and damage,
- arrest/fail state,
- police vehicles,
- dispatch audio,
- pedestrian crime witnesses,
- traffic law detection,
- NavMesh pursuit,
- cover/search tactics,
- helicopters,
- final wanted UI/visual design.

These belong to later milestones.
