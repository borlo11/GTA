# Milestone 6 — Combat Prototype

## Goal

Milestone 6 adds a compact on-foot combat foundation without turning OWGame into a full weapon framework.

The prototype validates:

- reusable health/damage ownership,
- one camera-directed ranged attack,
- one short-range melee attack,
- hit detection against pawn capsules while respecting blocking world geometry,
- civilian/police damage integration,
- death cleanup,
- crime/wanted continuity,
- basic combat HUD feedback.

## Controls

While Manny is possessed:

- Left Mouse Button: prototype hitscan shot
- Q: prototype melee strike
- F: existing M5 debug crime trigger

Combat input is intentionally bound directly in C++ for this milestone. No new binary input assets are required.

Vehicle controls remain unchanged. Combat bindings belong to the on-foot character, so entering the M2 vehicle naturally removes on-foot attack input with possession.

## Health architecture

`UOWHealthComponent` is a reusable ActorComponent with:

- MaxHealth / Health,
- damage application,
- normalized health query,
- death state,
- health-changed and death delegates.

M6 adds the component to:

- `AOWGameCharacter`,
- `AOWPopulationNPC`,
- `AOWPoliceOfficer`.

This keeps health out of the population/police managers and provides a narrow extension point for later weapons, mission damage, explosions, and enemy attacks.

## Ranged prototype

The player fires from the active third-person camera direction.

The shot first resolves blocking world geometry, then sweeps for Pawn objects only up to that obstruction. This prevents the combat targeting pass from shooting through city buildings while remaining robust to mannequin/capsule visibility-channel settings.

Prototype values:

- range: 6000 cm
- damage: 40
- targeting radius: 28 cm

A firearm discharge reports a severity-1 crime. Hitting a police officer adds one additional severity step.

## Melee prototype

Q performs a short forward pawn sweep.

Prototype values:

- range: 190 cm
- damage: 55
- targeting radius: 85 cm

A successful melee hit reports a crime:

- civilian: severity 1
- police: severity 2

## Death handling

Population NPCs and police officers stop movement/simulation immediately at zero health, disable capsule collision, keep their visible body briefly, then destroy after a short lifespan.

Population/police managers ignore dead actors when maintaining their target counts, so active world populations recover without waiting for the visual corpse cleanup delay.

The player also owns health but M6 does not yet introduce hostile police attacks, respawning, arrest, or a fail state.

## HUD

While on foot the HUD now displays:

- a small center crosshair,
- HP in the lower-left,
- existing interaction prompt,
- existing M5 wanted display.

Wanted remains visible during vehicle possession.

## Local validation

Build:

`OWGameEditor Win64 Development`

Required:

`Result: Succeeded`

Run all OWGame automation tests. M6 adds:

`OWGame.Combat.Defaults`

Required:

`TEST COMPLETE. EXIT CODE: 0`

## PIE acceptance in OW_LightweightCity

1. Manny spawns with HP shown.
2. Left-click produces a prototype shot and raises wanted.
3. Shooting an ambient NPC reduces health; repeated hits remove the NPC after death.
4. Q damages a nearby NPC only inside melee range.
5. Shooting/hitting police escalates wanted more aggressively.
6. Entering the M2 vehicle still works and on-foot combat does not fire while driving.
7. Exiting the vehicle restores normal Manny controls and combat.
8. M4 pedestrians continue replacing dead/despawned ambient NPCs.
9. M5 police response continues scaling and de-escalating.

## Explicitly deferred

- weapon inventory,
- ammunition/reload,
- weapon meshes and polished animation,
- recoil/spread,
- projectiles,
- police returning fire,
- enemy combat AI,
- cover,
- ragdolls,
- armor,
- healing pickups,
- respawn/death screen,
- blood/gore,
- final combat VFX/audio.

These require later scoped milestones or polish passes.
