# Milestone 9 — Visual & City Overhaul

## Goal

M9 is the first production-facing visual pass after the M8 vertical slice.

The objective is not to make a final photorealistic city in one step. It is to remove the strongest "prototype blockout" cues while preserving the gameplay coordinates and performance discipline already validated through M8.

## What changes

`OW_LightweightCity` is rebuilt into a denser compact district with:

- a three-by-three road grid instead of a single cross,
- main and secondary road widths,
- raised urban blocks,
- lane dashes,
- crosswalks,
- parking-bay markings,
- authored UNIBLOCKS FREE building LevelInstances instead of stretched block meshes,
- four real prefab variants: Art House Elevated, Classic House, Futuristic Cabin, and Modern House 2,
- rotated/offset 1:1 prefab placement for repeat variation,
- plaza / open-space blocks,
- bollards and simple urban furniture,
- street-light poles, heads and low-cost point lights,
- revised sun / skylight / atmosphere / fog baseline,
- optional volumetric clouds when the engine class is available.

The mission checkpoint and M2-M8 gameplay coordinates are preserved so the existing Hot Run vertical slice remains valid.

## Dynamic rendering baseline

M9 moves the project toward a fully dynamic city-lighting workflow.

`DefaultEngine.ini` enables the intended desktop rendering baseline:

- Lumen global illumination,
- Lumen reflections,
- mesh distance fields,
- virtual shadow maps,
- auto exposure,
- bloom,
- ambient occlusion.

The M9 bootstrap also attempts to enable `ForceNoPrecomputedLighting` on the city WorldSettings. The intention is to remove the old "lighting must be rebuilt" workflow and warning rather than hiding it.

The authored architecture is loaded through `ALevelInstance` / `unreal.LevelInstance` from the UNIBLOCKS prefab World assets discovered locally. The generator does not redistribute those Fab assets; it references the user's installed pack.

## Default startup map

The project now opens and launches directly into:

`/Game/Maps/OW_LightweightCity`

M1_TestMap remains in the repository for foundation regression checks but is no longer the default user-facing startup map.

## Third-party content policy

UNIBLOCKS FREE remains a local Fab dependency.

The repository does not add or redistribute the source pack. The M9 generator references material/mesh names already expected from the local pack and uses engine primitive meshes for lightweight detailing.

## Performance discipline

M8 demonstrated substantial headroom on the development machine before this pass.

M9 deliberately keeps the district compact and uses simple static meshes for the additional dressing. The richer visual pass must still be validated with the F9 frame-time overlay and all existing gameplay active.

The target remains:

- 60 FPS,
- 16.67 ms frame time.

If the new scene misses the target during the full Hot Run mission, visual density should be reduced before expanding the district.

## Generation

After building the current C++ branch, run:

`Content/Python/bootstrap_m9_city_overhaul.py`

Required marker:

`M9: ALL CHECKS PASSED`

The script is idempotent and only replaces actors with the `OW_CITY_` label prefix.

## Validation

Run:

`Content/Python/validate_m9_city_overhaul.py`

Required marker:

`VALIDATE_M9: ALL CHECKS PASSED`

Then run all existing `OWGame.*` automation tests.

## Manual acceptance

1. Open OW_LightweightCity.
2. The old single-cross blockout has been replaced by a denser grid.
3. Road markings and crosswalks are clearly visible.
4. Building silhouettes have visible height/setback variation.
5. Buildings visibly use authored prefab architecture with windows/doors/forms from the installed pack rather than monolithic cubes.
6. Street furniture / lights reduce empty pavement areas.
7. The red baked-lighting warning is gone after the rebuilt map is saved/reloaded.
7. Manny, ambient NPCs and police still spawn correctly.
8. The prototype vehicle still enters/exits and drives through the road network.
9. Hot Run remains fully completable.
10. F9 remains at or above the 60 FPS / 16.67 ms target during representative play.

## Explicitly deferred to M10+

M9 does not yet replace the prototype vehicle with Chaos Vehicles.

It also does not attempt:

- final architectural asset quality,
- interiors,
- traffic AI,
- final vegetation,
- final signage/art direction,
- cinematic weather/time-of-day,
- final post-process grading,
- city-scale World Partition conversion.

The next milestone is M10 — realistic vehicle foundation using Chaos Vehicles.
