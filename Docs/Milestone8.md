# Milestone 8 — Small Open-World Vertical Slice

## Goal

M8 turns the validated M1-M7 systems into one compact, coherent playable slice in OW_LightweightCity.

This milestone is intentionally an integration and presentation pass. It does not attempt to become a full open-world production game.

## Player-facing flow

The vertical slice now has a real in-world entry point instead of requiring the M7 debug key:

1. Spawn in OW_LightweightCity.
2. Find the green HOT RUN marker near the player start.
3. Use E to start the mission.
4. Reach the prototype vehicle.
5. Enter it.
6. Drive to the city checkpoint.
7. Escape the police response.
8. Receive a mission-complete presentation banner.
9. Return to the HOT RUN marker to replay.

The existing R/T debug controls remain available in non-shipping builds for testing.

## Vertical-slice director

`AOWVerticalSliceDirector` is spawned by the GameMode and only activates on OW_LightweightCity.

It uses a short timer to wait for the player pawn, then creates one `AOWMissionStartActor` near the starting area. No Actor Tick or global frame scan is introduced.

On non-vertical-slice maps the director destroys itself immediately.

## Mission start actor

`AOWMissionStartActor` implements the existing M3 interaction interface.

It provides:

- a collision target for the camera interaction sweep,
- a visible HOT RUN world marker,
- a small green point light,
- E interaction to start/restart the M7 mission,
- automatic hiding while the mission is active,
- automatic reappearance after completion/failure.

This keeps mission launch inside the world instead of adding mission-specific branching to the player character.

## Mission presentation

The M7 mission component remains the source of truth.

M8 adds a short completion-presentation window. The HUD uses that state to show a large centered completion banner immediately after Hot Run is completed, while the persistent small mission panel remains available afterward.

Mission save behavior is unchanged.

## HUD integration

M8 keeps the established information hierarchy:

- mission card: top-left,
- wanted: top-right,
- crosshair: center while on foot,
- health: bottom-left,
- interaction prompt: lower center.

The mission start actor means the normal interaction prompt now guides the player into the slice.

## Performance budget overlay

F9 toggles a lightweight development performance overlay.

It displays:

- current approximate FPS,
- current frame time in milliseconds,
- the 60 FPS / 16.67 ms target.

The overlay is presentation/debug instrumentation only. It does not claim that every machine will maintain 60 FPS; M8's acceptance test requires observing the slice on the target development machine and recording whether the budget is met.

## Streaming / World Partition experiment

M8 does not force a World Partition conversion into the already-working compact city.

Instead, `Content/Python/validate_m8_vertical_slice.py` performs a non-destructive inspection of the current map, generated bounds, building count, required M8 runtime classes, and reports whether a World Partition object is exposed by the current editor world.

This is deliberate: the current district is roughly a single compact 14k x 14k cm prototype. Introducing streaming infrastructure without a measured need would add complexity before the first vertical slice is evaluated.

The M8 result should be used to decide whether the next expansion requires a World Partition conversion, HLOD, Data Layers, or a larger map.

## Validation

Build:

`OWGameEditor Win64 Development`

Run:

`Content/Python/validate_m8_vertical_slice.py`

Required marker:

`VALIDATE_M8: ALL CHECKS PASSED`

Run all OWGame automation tests. M8 adds:

`OWGame.VerticalSlice.Defaults`

Required:

`TEST COMPLETE. EXIT CODE: 0`

## Manual acceptance

1. Launch OW_LightweightCity.
2. Green HOT RUN marker appears near the initial player area.
3. Looking at it shows `[E] Avvia Hot Run`.
4. E starts the mission and hides the start marker.
5. Mission HUD/marker guide the complete Hot Run flow.
6. Vehicle possession does not lose mission/wanted state.
7. Police response and de-escalation remain functional.
8. Combat controls still work on foot.
9. Completion produces the centered mission-complete banner.
10. The HOT RUN marker returns after completion and can replay the mission.
11. F9 toggles performance readout.
12. No regressions are observed in M1-M7 tests.
13. Record FPS/frame-time during the full mission on the target machine.

## M8 freeze criteria

M8 is complete when the branch passes build, validator, all OWGame tests, and the full manual mission flow.

At that point the prototype foundation should be frozen and evaluated before defining a post-M8 roadmap. Future work should be driven by the vertical-slice review rather than automatically adding more systems.
