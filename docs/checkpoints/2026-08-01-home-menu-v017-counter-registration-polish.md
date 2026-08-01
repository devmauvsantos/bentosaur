# Home Menu V017 — Counter Registration Polish

**Status:** implemented, tested, captured, and deployed; founder phone-scale
approval pending

**Date:** 2026-08-01

## Outcome

Three counter props now meet their painted contact surfaces more naturally.
No asset, scale, z-order, lighting, or animation amplitude changed.

![V016 left, V017 right](../../game/docs/runtime-captures/home-menu-v017-counter-registration/home-menu-v016-v017-counter-comparison.png)

## Registration changes

| Element | V016 | V017 | Delta |
| --- | ---: | ---: | ---: |
| Grape bowl | `(-170, 45)` | `(-178, 53)` | `-8x, +8y` |
| Bottle crate | `(168.5, 28.5)` | `(168.5, 36.5)` | `+8y` |
| Stockpot lid pivot | `(-1, -82)` | `(-1, -74)` | `+8y` |

The lid correction moves `LidPivot`, not only its child sprite. Its resting
pose and procedural rattle therefore share the same corrected physical contact
point at stage coordinate `(178, 653)`.

## Validation

- complete Godot suite: **23/23 pass**;
- canonical sprite sources and uniform scales unchanged: pass;
- bottle-crate z-order and counter-cloth overlap unchanged: pass;
- lid one-pixel travel and `0.7°` rattle hard limits unchanged: pass;
- deterministic motion equivalence at 30, 60, and 120 FPS: pass;
- Forward Mobile / Metal runtime capture: pass;
- Godot iOS export and personal-signing guard: pass;
- strict code-sign verification, install, and launch on Mauricio's iPhone: pass.

## Preserved rollback

The exact V016 source is commit `e70f6a9` and annotated tag
`checkpoint/home-interactive-lanterns-v016-2026-08-01`.
