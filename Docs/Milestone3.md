# Milestone 3 — Character & Interaction Vertical Slice

## Goal

Milestone 3 makes the validated M1/M2 foundation feel like a small playable game loop without introducing paid assets or large new systems.

The player should now have:

- a visible third-person prototype body,
- a more polished shoulder camera,
- walk and sprint speeds,
- a contextual interaction prompt,
- forgiving interaction targeting,
- clean enter/exit continuity with the M2 vehicle.

## Scope

Included:

- native C++ prototype character visuals assembled from Unreal Engine basic shapes,
- no third-party character assets,
- Left Shift / Right Shift sprint,
- camera lag and shoulder offset,
- interaction focus scan on a low-frequency timer rather than Actor Tick,
- sphere-sweep interaction assist,
- HUD prompt such as [E] Entra nel veicolo,
- prompt text supplied by the IOWInteractable interface,
- M1/M2 regression compatibility,
- dedicated M3 automation defaults test.

Explicitly excluded:

- production skeletal character,
- locomotion animation Blueprint,
- motion matching,
- combat,
- NPC population,
- crime/police,
- inventory,
- missions,
- paid marketplace content.

## Prototype character visual

The M3 player body is deliberately a code-only placeholder built from engine primitive meshes.

Its purpose is to validate third-person framing, scale, camera collision, vehicle entry/exit visibility and basic feel without adding external asset dependencies.

It should be replaced by a proper skeletal character in a later milestone.

## Sprint

On foot:

- WASD — movement
- Mouse — look
- Space — jump
- Left Shift / Right Shift — sprint while held
- E — interact

Sprint changes MaxWalkSpeed from the configured walk speed to the configured sprint speed and restores walk speed on release.

## Camera

The character spring arm uses:

- a longer third-person distance,
- shoulder offset,
- camera lag,
- camera rotation lag,
- standard spring-arm collision testing.

No custom camera Actor Tick is introduced.

## Interaction focus

The character checks for a nearby interactable at a modest fixed interval using an Unreal timer.

The query uses a sphere sweep along the camera forward direction, making interaction less dependent on pixel-perfect aiming while avoiding continuous per-frame actor searches.

IOWInteractable now exposes a prompt string. For example, the M2 prototype vehicle returns Entra nel veicolo.

The HUD draws the prompt only while the on-foot character has a valid interactable in focus.

## Required local validation

Build with the normal OWGameEditor Win64 Development UE 5.8 build command.

Required: Result: Succeeded.

Automation:

- OWGame.Foundation.*
- OWGame.Vehicle.*
- OWGame.Character.*

Required: TEST COMPLETE. EXIT CODE: 0.

PIE checklist:

- prototype humanoid body visible,
- camera sits behind/right of the player,
- WASD and mouse work,
- Space jumps,
- Shift increases movement speed and releasing Shift restores walk speed,
- approaching the vehicle shows [E] Entra nel veicolo,
- E enters the vehicle,
- vehicle controls still work,
- E exits,
- player body and on-foot controls return,
- prompt returns after exiting when an interactable is in focus.

## Performance

The character Actor Tick remains disabled.

Interaction focus uses a timer at a low fixed frequency. The milestone must preserve the 60 FPS / 16.67 ms architectural target.
