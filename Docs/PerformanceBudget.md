# Performance Budget

## Primary target

- Target frame rate: **60 FPS**
- Total frame budget: **16.67 ms**

This is an architectural target, not a claim that every future scenario already meets it.

## Rules

1. Profile before optimizing.
2. Do not accept unexplained sustained frame-time regressions.
3. Track CPU, GPU, memory, and streaming separately once representative scenes exist.
4. Avoid unnecessary Tick and polling when events/timers can express the behavior.
5. Avoid repeated global actor searches in gameplay hot paths.
6. Avoid avoidable synchronous asset loads during active gameplay.
7. Benchmark representative gameplay, not empty maps.
8. Keep headroom for spikes, streaming, effects, AI, and physics.

## Tools

Use Unreal Insights and relevant stat commands, including:

- `stat unit`
- `stat game`
- `stat gpu`
- memory profiling tools

## Deferred subsystem budgets

Exact budgets for rendering, game thread, AI, traffic, physics, animation, streaming, audio, and other systems will be assigned only after vertical prototypes provide real measurements.
