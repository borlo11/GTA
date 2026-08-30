# Milestone 4.5 — Lightweight Original City

## Goal

Replace the empty M1 test arena with the first original urban gameplay district while staying within the development machine's storage budget.

The City Sample path was intentionally abandoned because the complete sample requires far more temporary and installed disk space than is practical on the current machine.

M4.5 instead uses:

- OWGame gameplay code,
- UNIBLOCKS FREE modular content,
- Unreal Engine primitive geometry for cheap road/sidewalk massing,
- a generated original map named `/Game/Maps/OW_LightweightCity`.

## First district

The bootstrap creates a deliberately small urban prototype:

- cross-shaped two-road layout,
- sidewalks,
- twelve varied building masses,
- several UNIBLOCKS materials when available,
- directional light, sky atmosphere, skylight and fog,
- PlayerStart,
- M2 prototype vehicle,
- OWGame GameMode.

M4 population remains runtime-owned by `AOWGameGameMode`, so pedestrians appear automatically during PIE.

## UNIBLOCKS usage

The first pass uses `SM_UB_Block_scalable` as a robust scalable building mass.

This is intentional. The free pack contains thousands of fine-grained modular pieces and Blueprints. Before spending time assembling detailed façades, M4.5 validates city scale, road width, vehicle handling, pedestrian behavior, camera feel and performance.

Later passes can replace building masses with detailed UNIBLOCKS façade assemblies without changing gameplay coordinates.

## Repository policy

UNIBLOCKS FREE is treated as an external Fab dependency. The imported `/Game/Uniblocks` source content is intentionally not tracked in this public repository. Install the pack locally through Fab before running the city bootstrap. The generated OWGame map may be tracked; it will resolve its UNIBLOCKS references when the dependency is installed at `/Game/Uniblocks`.

## Automation

Run:

`Content/Python/bootstrap_lightweight_city.py`

The script is idempotent. It only removes actors whose labels start with `OW_CITY_` when rebuilding the generated city.

Run:

`Content/Python/validate_lightweight_city.py`

Required marker:

`VALIDATE_M4_5: ALL CHECKS PASSED`

## PIE acceptance

- Manny spawns in OW_LightweightCity,
- roads and sidewalks are visible,
- at least eight UNIBLOCKS building masses are visible,
- M4 pedestrians spawn and walk,
- E enters the prototype vehicle,
- driving works through the road intersection,
- E exits back to Manny,
- interaction HUD remains functional,
- no obvious teleporting NPC regression,
- frame rate remains appropriate for a small prototype district.

## Scope

M4.5 does not yet add:

- traffic AI,
- detailed interiors,
- full city blocks,
- procedural road generation,
- police,
- crime,
- combat,
- missions.

Those remain later milestones.
