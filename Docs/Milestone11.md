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


## Phase D — open-world dressing pass

The next additive pass targets the exact cues that still made the expanded map read as a blockout from normal driving height.

The generator now adds:

- lightweight facade bands, entry/door cues and rooftop service volumes to the procedural background masses;
- two secondary parking pockets, wheel stops and clearer parking-bay markings outside the civic lot;
- additional district crosswalks and stop bars at outer intersections;
- benches, bollards, bins, sign silhouettes and planter groups to restore human scale;
- denser grouped vegetation using the confirmed local UNIBLOCKS bush mesh;
- three lightweight edge-of-world skyline landmarks built from stepped volumes rather than single giant slabs.

All Phase D content remains under the `OW_M11_` ownership prefix and is regenerated idempotently by `bootstrap_m11_freeroam_expansion.py`.

The pass intentionally keeps transparent glass, dense dynamic lights, final traffic, interiors and high-cost foliage out of scope. The 60 FPS / 16.67 ms target remains authoritative.

Cloud-side Unreal validation is **NOT EXECUTED** because the repository runner does not provide UE 5.8. Local editor validation must run the bootstrap, `validate_m11_freeroam_expansion.py`, representative free-roam driving and the existing gameplay automation tests.


## Phase E — authored-asset city pass

Phase D improved density and silhouette, but the first driving screenshot still read as an advanced blockout: too many bare cuboids, a repetitive three-tower skyline and procedural street-light heads.

Phase E uses the local M11 asset inventory to move visible detail toward actual UNIBLOCKS content without redistributing Fab assets.

Changes:

- authored prefab LevelInstances increase from four outer heroes to twelve carefully placed residential/modern hero and infill sites;
- background massing skips every authored prefab lot so real architecture does not overlap procedural boxes;
- visible UNIBLOCKS swing/sliding door meshes and window/gate modules are attached to cheap background buildings at controlled dimensions;
- the industrial district uses the confirmed visible fence mesh through an exact asset path;
- outer street lights use a confirmed UNIBLOCKS lamp-head mesh when available, with the previous primitive head retained only as a fallback;
- the three skyline landmarks are rebuilt as stepped, offset silhouettes with multiple roof/service volumes instead of identical vertical slabs;
- skyline facades receive real visible UNIBLOCKS window/gate inserts.

All exact visible-part paths came from the user's local inventory. Missing optional parts degrade gracefully; core roads, M9/M10 gameplay and the 60 FPS / 16.67 ms target remain unchanged.

Cloud-side Unreal validation is **NOT EXECUTED**. Local acceptance requires rerunning the bootstrap and validator in UE 5.8, followed by representative on-foot and SportsCar free-roam screenshots/performance checks.


## Phase F — density and skyline correction

The first Phase E driving screenshot exposed a visual regression despite structural validation passing. Too many procedural lots had been removed for small authored prefabs, the south-east quadrant read as unfinished, facade inserts could appear as isolated panels, and the three edge towers still looked like prototype slabs.

Phase F corrects the visual strategy:

- authored LevelInstances are reduced to six deliberate hero/infill buildings instead of using them as a substitute for city mass;
- procedural district massing is restored and made denser/taller, with four-volume residential/modern clusters and fuller industrial lots;
- only the actual civic/parking core remains open in the south-east; surrounding ParkEdge lots now receive urban massing;
- risky standalone authored facade/window inserts are no longer spawned on procedural buildings;
- the three isolated high towers are removed and replaced by seven broader, lower, distributed mid-rise skyline landmarks with stepped upper masses and facade bands;
- an optional runtime discovery pass adds real local UNIBLOCKS street trees when a safe complete tree mesh is available, without making the bootstrap dependent on a fabricated asset path.

This phase prioritizes a coherent city silhouette and density over forcing individual modular pieces into contexts where their pivots/bounds are unknown.


## Phase G — street-level readability pass

The Phase F road-height screenshot showed that overall density and skyline distribution had improved, but the city still read as blockout architecture from the SportsCar camera. The remaining problem was not world size: it was street-edge composition.

Phase G therefore focuses on the player-height view:

- district background buildings are pushed toward the block perimeter to create a stronger street wall and remove oversized empty setbacks;
- modern buildings receive multiple dark window-row bands plus a ground-floor canopy;
- residential / park-edge buildings receive two or three window rows plus an entrance canopy;
- industrial buildings receive a large loading-door read and high clerestory strip;
- the two main boulevards receive 32 clearly visible UNIBLOCKS bush instances at larger scale;
- the central road axes receive 40 additional streetlights (pole + head) so lighting/street furniture exists inside the city rather than only on the outer perimeter;
- all new dressing remains static/non-colliding and keeps the existing gameplay/vehicle coordinates intact.

The intent is to make a normal driving screenshot read as an urban street first and as procedural generation second.


## Phase H — four-sided facades

The Phase G road-height screenshot exposed the next dominant blockout cue: buildings looked acceptable from the dressed frontage but immediately became giant blank walls from side/rear camera angles.

Phase H treats every cheap background building as an object that must survive a 360-degree driving camera:

- window-row bands are generated on north, south, east and west facades;
- vertical facade piers break continuous strips into a readable window grid;
- roof parapet bands and service volumes break raw engine-cube silhouettes;
- ground-floor dark storefront/entrance bands appear on opposing sides;
- projecting canopies create actual shadow/depth at pedestrian height;
- eight small curbside parking pockets add road-edge markings and wheel stops near internal blocks.

The pass deliberately uses opaque low-cost static geometry rather than transparent glass or hundreds of individual window assets, preserving the performance-first prototype target while removing the most obvious blank-wall failure mode.
