# Agent Instructions

This repository is an Unreal Engine 5.8 C++ project with internal module codename `OWGame`.

## Critical environment rule

GitHub/Copilot cloud runners may NOT have Unreal Engine installed.

- Do not spend time repeatedly searching for Unreal Engine.
- Do not attempt a large Unreal Engine installation in a background-agent runner.
- If UE 5.8 build tools are unavailable, continue with source/config/documentation work.
- Mark Unreal build, editor, runtime, and automation-test validation as **NOT EXECUTED** when they cannot actually be run.
- Never claim a build/test/editor validation succeeded unless it was executed.

## Asset rule

Do not fabricate binary `.uasset` files. If a required Unreal asset cannot be safely generated through a real UE editor/commandlet, implement the C++ side and document the minimal editor steps.

## Scope discipline

Prefer small, reviewable milestones. Do not implement vehicles, traffic, police, combat, missions, crowds, economy, weather, or large-world content unless the active task explicitly requests them.

## Engineering rules

- Unreal Engine 5.8, C++ first for core systems.
- 60 FPS / 16.67 ms is the architectural target.
- Avoid unnecessary Actor Tick.
- Avoid repeated global actor searches.
- Keep hot-path allocations and synchronous loads under control.
- Use UE ownership/GC patterns correctly.
- Use project-specific logging.
- Preserve clean module boundaries.
- Do not commit Binaries, Intermediate, Saved, DerivedDataCache, IDE state, or generated build artifacts.
- Review the diff before finishing.
