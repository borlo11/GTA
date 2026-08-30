# Milestone 4.5 — City Sample Environment Integration

## Goal

Move OWGame from the M1 test arena into a real urban World Partition environment before crime/police work begins.

The first target is Epic's **City Sample Small City** environment, not Big City.

OWGame remains the gameplay owner:

- AOWGameGameMode
- AOWGameCharacter / Manny
- M2 prototype vehicle
- M3 interaction HUD
- M4 population manager and pedestrian NPCs

City Sample is treated first as an environment/streaming asset source, not as a replacement gameplay framework.

## Why Small City first

Epic's City Sample includes both Big City and Small City. Big City is substantially more resource intensive. Small City uses the same core environment technologies in a more manageable map and is the correct first integration target.

## Integration policy

Do not replace the OWGame repository with the City Sample project.

Do not copy City Sample C++ code blindly into OWGame.

Do not enable both OWGame population and City Sample Mass Crowd/Traffic at the same time during the first validation pass.

Do not start M5 crime/police until the OWGame gameplay loop is proven inside the city.

## Stage A — acquire the source sample

Create the official City Sample as a **separate local Unreal project** using Fab / Epic Games Launcher and the UE 5.8-compatible sample.

Open the standalone City Sample once and confirm that:

- the project loads,
- Content > Map contains Small_City_LVL,
- Small_City_LVL opens.

No OWGame content is changed during this stage.

## Stage B — discovery before migration

Run the repository script:

`Tools/CitySample/inspect_city_sample.py`

against the standalone City Sample project.

It:

- finds the actual Small_City_LVL package path,
- loads the map headlessly,
- counts loaded actors,
- reports actors whose names/classes suggest Mass, Crowd, Traffic, Vehicle, Parking, spawner, or City Sample gameplay ownership,
- writes `Saved/CitySampleDiscovery.json` inside the standalone sample,
- does not save or modify the City Sample map.

The discovery report is used to choose the smallest safe environment migration.

## Stage C — curated environment migration

This stage is intentionally not automated until Stage B reveals the exact UE 5.8 map and dependency layout.

The planned destination is:

`/Game/Maps/OW_CitySample_Small`

The OWGame copy must:

- retain City Sample environment geometry, materials, lighting, World Partition and required environment Data Layers,
- use AOWGameGameMode,
- contain a valid PlayerStart,
- disable/remove City Sample gameplay spawners that conflict with OWGame during first-pass validation,
- keep City Sample's original project unchanged.

## Stage D — OWGame validation in the city

Required gameplay checks:

- Manny spawns and locomotion works,
- camera works,
- interaction HUD works,
- M2 vehicle supports enter/drive/exit,
- M4 pedestrians spawn and walk,
- driving through the city causes World Partition streaming without breaking possession,
- population follows the currently possessed pawn,
- no duplicate City Sample crowd/traffic simulation is active unless explicitly enabled later.

## Target validator

After the curated map exists, run:

`Content/Python/validate_m4_5_city_integration.py`

It checks:

- /Game/Maps/OW_CitySample_Small exists,
- the map loads,
- World Settings resolves to OWGameGameMode,
- at least one PlayerStart exists.

## Performance

M4.5 is an integration and profiling milestone.

Do not judge final visual settings yet. First establish functional correctness. Then profile Small City and lower scalability/screen percentage if needed during development.

The architecture target remains 60 FPS / 16.67 ms, but City Sample integration must be measured on the actual development machine before a concrete city rendering budget is frozen.

## Explicitly deferred

- City Sample native Mass Crowd integration
- City Sample native traffic integration
- replacing the M2 prototype vehicle with City Sample vehicles
- Big City
- custom procedural city generation
- crime/police
- combat
- missions

These are separate decisions after the environment integration is stable.
