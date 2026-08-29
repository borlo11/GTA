# OWGame

Internal codename for an original open-world action game being built with Unreal Engine 5.8 and C++.

## Current status

Milestone 1 bootstrap is in place:

- UE 5.8 C++ project descriptor
- runtime module
- third-person character foundation
- camera foundation
- Enhanced Input hooks
- reusable interaction interface
- test interactable
- project logging
- automation-test foundation
- performance/documentation baseline
- background-agent instructions that explicitly prevent cloud agents from stalling on Unreal installation

The repository does **not** contain copied Rockstar/GTA code, assets, maps, characters, or other proprietary game content.

## Important for coding agents

Read `AGENTS.md` before making changes.

If Unreal Engine 5.8 is unavailable in the execution environment, continue source work and report Unreal build/editor validation as **NOT EXECUTED**. Do not waste time repeatedly searching for or installing the engine.

See `Docs/Development.md`, `Docs/Architecture.md`, `Docs/PerformanceBudget.md`, and `Docs/Roadmap.md`.
