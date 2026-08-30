# Milestone 7 — Mission Framework

## Goal

Milestone 7 introduces reusable mission state and proves it with one compact mission inside OW_LightweightCity.

The framework must survive possession changes, expose objective state to the HUD, persist progress through Unreal SaveGame, and integrate existing vehicle / wanted systems without hard-coding mission logic into those systems.

## Ownership

Mission state lives in `UOWMissionComponent`, a default subobject of `AOWGamePlayerController`.

That ownership mirrors M5 wanted state and is deliberate:

- the controller survives Manny <-> vehicle possession,
- mission progress does not reset when entering a vehicle,
- gameplay systems do not need a global singleton,
- the HUD can read mission state independent of the current pawn.

## Mission states

- Inactive
- Active
- Completed
- Failed

The component also owns an ordered list of runtime objective specs.

M7 objective types:

- ReachVehicle
- EnterVehicle
- ReachLocation
- LoseWanted

The framework exposes a `FailMission` API even though the first prototype mission does not yet use a fail trigger.

## First mission — Hot Run

Debug control:

- R: start/restart Hot Run
- T: reset mission and delete the mission save slot

Objective sequence:

1. Raggiungi il veicolo.
2. Entra nel veicolo.
3. Guida fino al checkpoint on the north/south road.
4. Semina la polizia.

When objective 4 begins, the mission guarantees at least wanted level 2, reusing the existing M5 crime/police loop. The mission completes only after wanted returns to zero.

This intentionally validates M2, M5, and M7 together.

## Marker

`AOWMissionMarker` is a lightweight runtime actor containing:

- an engine sphere mesh with collision disabled,
- a text label,
- no Actor Tick.

The mission component updates the marker on its existing 0.2 second objective timer.

Vehicle-related objectives follow the nearest prototype vehicle. The driving checkpoint uses a fixed location appropriate to the current lightweight-city prototype.

## Save integration

`UOWMissionSaveGame` stores:

- mission id,
- mission state,
- current objective index.

The component saves after objective transitions, completion, and failure. It restores progress in BeginPlay.

The prototype slot is:

`OWGame_MissionState_0`

Press T in a development build to delete that slot and return to a fresh inactive mission state.

## HUD

The HUD displays mission information independently of the currently possessed pawn:

- mission title,
- current objective,
- approximate distance when the objective has a world location,
- completed / failed state.

Existing HP, crosshair, interaction prompt, and wanted HUD remain unchanged.

## Performance

No mission Actor Tick is introduced.

Objective evaluation is timer-driven at 0.2 seconds. The marker has no Tick.

This is appropriate for coarse open-world objective conditions and keeps mission logic out of the frame loop.

## Local validation

Build:

`OWGameEditor Win64 Development`

Required:

`Result: Succeeded`

M7 adds:

`OWGame.Mission.Defaults`

Run all `OWGame.*` automation tests.

Required:

`TEST COMPLETE. EXIT CODE: 0`

## PIE acceptance

1. Open OW_LightweightCity and Play.
2. Press T once to clear an old mission save if necessary.
3. Press R.
4. HUD shows Hot Run and "Raggiungi il veicolo".
5. Approach the prototype vehicle -> objective changes to "Entra nel veicolo".
6. Press E -> objective changes to "Guida fino al checkpoint".
7. Drive to the runtime marker.
8. Reaching it starts "Semina la polizia" and raises wanted to at least level 2.
9. Break police line of sight until wanted returns to zero.
10. HUD reports "Missione completata".
11. Stop PIE and start again -> completed mission state reloads.
12. Press R -> mission restarts from objective 1.
13. Existing M1-M6 gameplay remains functional.

## Explicitly deferred

- multiple authored missions,
- content/data assets for designers,
- branching mission graphs,
- cutscenes/dialogue,
- mission rewards/economy,
- scripted NPC roles,
- fail conditions tied to player death/arrest,
- checkpoints that restore full world state,
- cloud/account saves,
- mission editor tooling.

Those belong after the framework is validated in the M8 vertical slice.
