# Roadmap

The roadmap defines broad engineering milestones only. Each milestone must be scoped separately before implementation.

## M1 — Core foundation

Player, camera, Enhanced Input foundation, interaction, logging, debugging/test foundation, documentation, and performance discipline.

## M2 — Vehicle vertical prototype

One vehicle, possession/enter/exit, driving input, camera integration, and measurable performance. No traffic fleet.

## M3 — Character & interaction vertical slice

Visible third-person prototype body, sprint, camera feel, contextual interaction prompt, forgiving interaction targeting, and M1/M2 continuity.

### M3.1 — Skeletal character visual upgrade

Free UE Third Person mannequin, Animation Blueprint locomotion, and regression validation. This is a polish checkpoint and does not replace M4.

## M4 — NPC / population prototype

Small autonomous mannequin pedestrian population with runtime spawn/despawn, distance-based simulation LOD, and profiling discipline.

### M4.5 — Lightweight original city

Generated original urban district using UNIBLOCKS FREE plus lightweight road/sidewalk geometry, with OWGame gameplay systems validated inside it.

## M5 — Crime / police prototype

Minimal crime reporting, persistent 0-3 wanted state, police response, pursuit/search, possession continuity, HUD feedback, and de-escalation loop.

## M6 — Combat prototype

Reusable health/damage architecture, camera-directed ranged combat, short-range melee, death cleanup, HUD feedback, and wanted integration.

## M7 — Mission framework

Persistent mission state, reusable objective types, runtime markers, SaveGame integration, debug controls, HUD feedback, and one playable Hot Run mission.

## M8 — Small open-world vertical slice

A compact original district combining M1-M7, an in-world Hot Run entry point, polished mission feedback, a 60 FPS debug budget overlay, and a non-destructive World Partition/streaming inspection.

## M9 — Visual & city overhaul

Denser urban grid, road markings, crosswalks, parking detail, varied building silhouettes, street furniture, dynamic lighting baseline, and continued 60 FPS validation.

## M10 — Realistic vehicle foundation

Replace the floating-box vehicle prototype with a Chaos Vehicles-based drivable car foundation, realistic wheel/suspension behavior, speed-sensitive steering, braking/handbrake, improved vehicle camera, and a reusable multi-vehicle architecture.

## M11 — Environment & free-roam world

Expand the compact district into a larger, more varied free-roam environment with distinct districts, stronger environmental density, improved graphics/atmosphere, long driving routes, and continued 60 FPS validation.

## M12 — Graphics & atmosphere

Refine lighting, materials, post-processing, time-of-day foundations, weather-ready atmosphere, and quality tiers after the larger world layout is stable.

## M13 — Living free roam

Traffic foundations, richer pedestrian behavior, ambient activity, improved police behavior, and free-roam UI/audio.

## M14 — World density & production optimization

Further district dressing, selected interiors, HLOD/streaming/World Partition work, asset optimization, and production-quality performance passes.

## Story phase

Story, mission chains, cutscenes, dialogue, progression, and narrative scripting become the next major focus after the free-roam world is strong enough to support them.
