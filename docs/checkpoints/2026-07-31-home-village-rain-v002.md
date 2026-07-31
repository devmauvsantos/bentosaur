# Checkpoint — Home Village Rain V002

Status: founder-approved major visual checkpoint

Date: 2026-07-31

Git tag: `checkpoint/home-village-rain-v002`

## Why this checkpoint exists

The empty Home Village now feels alive in-engine: rain is established before
the first frame, the registered lantern and window lighting wakes through the
weather, the wet pavement preserves the approved reflections, and collision
splashes animate across the square. Mau called the result a big success and
approved preserving it as a durable checkpoint.

The final V002 restraint pass replaces bright white-looking rain with
normal-alpha, cool-tinted layers:

| Layer | Locked opacity |
|---|---:|
| Back rain | 23% |
| Front rain | 37% |
| Splash tint | 50% |

## Included in the repository checkpoint

- approved Home Village unlit background and registered light layers;
- deterministic Godot rain lab and source-asset builder;
- V001 brighter weather evidence and V002 soft-blend evidence;
- runtime contract coverage for full, reduced, and deterministic weather;
- native-resolution canvas, ultratall expansion, Metal, VSync, and ProMotion
  settings plus an automated display contract;
- the bounded Home → Service → Summary first playable and its captures;
- the current flat-cel concept pack and preserved 3D/character source additions
  that were present at the time of the checkpoint.

## Evidence

- `game/docs/runtime-captures/home-village-rain-v002-soft-blend/`
- `docs/home-village-rain-lab-v001.md`
- `docs/mobile-display-quality-contract-v001.md`

## What this does not approve

- The current `941 × 1672` source as the final native-density environment
  master.
- A production ultratall crop or outpaint.
- Physical-device frame time, thermals, touch safe areas, or 120 Hz behavior.
- The first playable's temporary flattened menu and service backdrops as
  shippable art.
- A production-ready animated dinosaur character.

Those gates remain explicit so this success can be preserved without quietly
promoting unfinished assets.
