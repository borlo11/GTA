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
