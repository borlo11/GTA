# Milestone 11 — Environment & Free-Roam World

## Goal

M11 changes the project's priority from story-first iteration to world-first iteration.

The milestone is successful when OWGame is enjoyable to drive and walk around for an extended free-roam session even with no active mission. The current compact district becomes the seed of a larger, more varied world rather than the final map.

## Core target

The practical acceptance target is:

> Launch OWGame, enter the SportsCar, and free-roam for roughly 10–15 minutes through a world that feels varied, readable, visually intentional, and performant without needing to start Hot Run.

## Scope

M11 focuses on five areas.

### 1. Larger road network

- expand beyond the current compact 3x3 road layout;
- create longer uninterrupted driving routes;
- add intersections with different shapes and widths;
- include parking areas, service roads, dead ends, and broader arterial roads;
- preserve a deterministic safe PlayerStart and SportsCar spawn;
- keep existing gameplay systems functional.

### 2. Distinct districts

The expanded world should read as multiple places rather than one repeated block pattern.

Initial district targets:

- central / modern district;
- lower-density residential district;
- industrial / service district;
- waterfront / edge-of-map district;
- one open civic or park-like space.

The exact architectural asset mix must be based on assets actually present in the user's local project. M11 does not fabricate unsupported asset paths.

### 3. Environmental density and art direction

Use modular authored assets where they improve the scene and lightweight geometry where it is visually unobtrusive.

Priorities:

- believable building scale and setbacks;
- sidewalks and curbs;
- parking markings;
- street lights;
- bollards, barriers, railings, signs and street furniture;
- vegetation where suitable assets exist;
- facade variation;
- skyline landmarks;
- fewer blank monolithic walls and repeated hero prefabs.

UNIBLOCKS FREE remains a local dependency and must not be redistributed by the repository.

### 4. Graphics and atmosphere

Keep the M9 dynamic-lighting foundation while improving presentation incrementally:

- Lumen GI/reflections;
- Virtual Shadow Maps where affordable;
- controlled exposure;
- fog/atmosphere;
- stronger material contrast;
- improved road and pavement readability;
- restrained post-process changes;
- optional quality tiers later rather than sacrificing the 60 FPS baseline.

M11 should not chase cinematic effects at the cost of free-roam performance.

### 5. Free-roam performance

Representative testing must include:

- on foot;
- driving the Chaos SportsCar;
- NPC population active;
- wanted/police systems available;
- dense district views;
- long road views.

Target remains approximately:

- 60 FPS;
- 16.67 ms frame time.

Editor PIE measurements are informative but standalone/game-mode measurements are the acceptance reference.

## Implementation phases

### Phase A — Asset inventory

Run a read-only environment discovery pass and inventory the local assets that can support:

- buildings/prefabs;
- road pieces;
- props;
- vegetation;
- signs;
- fences/railings;
- industrial dressing;
- park/civic dressing;
- materials.

The report is written under `Saved/` and is not committed.

### Phase B — World layout expansion

Create a larger road-and-block structure with district boundaries and long free-roam routes before adding dense decoration.

### Phase C — Authored district pass

Populate each district from the discovered asset inventory. Avoid repeating the same prefab in every block.

### Phase D — Dressing and atmosphere

Add props, vegetation, parking, street furniture, facade detail, lighting refinement, and skyline cues.

### Phase E — Optimization and acceptance

Validate:

- no blocked PlayerStart;
- no vehicle spawn inside geometry;
- no NPC/police roof spawns;
- Chaos vehicle remains usable;
- Hot Run remains functional;
- no obvious world holes on intended routes;
- representative standalone performance remains near the 60 FPS target.

## Deferred

M11 intentionally does not prioritize:

- final story missions;
- cutscenes;
- dialogue systems;
- final interiors;
- large mission chains;
- final traffic simulation;
- final production weather system.

Those systems come after the free-roam world has a strong foundation.


## Phase A result

The first M11 local inventory completed successfully and confirmed a large local environment library:

- 4,138 scanned assets;
- 9 prefab World assets;
- 3,202 static-mesh candidates;
- 29 Blueprint candidates;
- 311 material candidates.

The inventory also confirmed the four useful authored house/cabin families already known from M9, plus visible garden and gate/fence parts suitable for residential and industrial dressing.

## Phase B — first additive expansion

`bootstrap_m11_freeroam_expansion.py` intentionally preserves the M9 central district and M10 Chaos SportsCar while adding an outer free-roam world under the `OW_M11_` ownership prefix.

The first pass adds:

- a much larger world base;
- seven north/south and seven east/west long roads;
- long lane-marking runs and outer crosswalks;
- four district identities: Residential, Modern, Industrial, ParkEdge;
- four additional authored hero prefab LevelInstances;
- lightweight district background architecture;
- industrial fence/loading-dock dressing;
- a civic/park plaza with optional UNIBLOCKS bushes;
- a dedicated parking area;
- sparse outer street lights.

This is a layout-and-silhouette pass, not the final art pass. Phase C will replace the weakest placeholder/background architecture with better combinations from the local visual inventory after the expanded driving routes are accepted.


## Phase C — environment readability pass

The first free-roam screenshots showed the expanded road network working, but the single-volume background architecture still read as oversized placeholder slabs.

Phase C therefore changes the environment strategy without increasing authored LevelInstance density:

- one giant block per background lot is removed;
- Residential lots become three low staggered volumes with visible setbacks;
- Modern lots become two slender mid-rise masses plus a low podium;
- Industrial lots become paired low warehouses with a service gap;
- heights are capped far below the previous slab-like silhouettes;
- sparse confirmed UNIBLOCKS bush meshes add residential/modern landscaping;
- thin non-colliding boulevard edge bands improve road hierarchy;
- existing M9/M10 gameplay, M11 road layout, hero prefabs, industrial dressing, park/parking areas, and 60 FPS intent remain preserved.

This is still a procedural staging pass, but it deliberately removes the most obvious "giant white cube" failure mode before deeper art-direction work.
