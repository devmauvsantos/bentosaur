# Home Menu V016 — Interactive Stall Lanterns

**Status:** implemented, tested, captured, and deployed; founder phone-scale
interaction approval pending

**Date:** 2026-08-01

## Outcome

Both hanging stall lanterns are now independent tactile details. Tapping either
one creates a brief two-dip light flick and a tiny damped bell swing. The
fixture's foreground light pool follows the same intensity, while the wall
anchor remains completely fixed.

![Deterministic tap proof](../../game/docs/runtime-captures/home-menu-v016-lantern-tap-interaction/home-menu-v016-lantern-tap-proof-grid.png)

## Runtime structure

```text
StallLanternFixture                ring-center registration
├── Anchor                         fixed; never rotates
└── SwayPivot                      ambient wind + tap bell response
    ├── LocalHalo
    ├── BodyOff
    ├── Core
    └── TapTarget                  invisible 104 × 190 phone target
        └── CollisionShape2D
```

The pivot is the actual hanging ring at the fixture origin. The shell, core,
halo, and touch region rotate together beneath it; the separate anchor does
not inherit the transform.

## Interaction contract

| Property | V016 value |
| --- | ---: |
| Tap cooldown | `1.5 s` |
| Visible response | `1.10 s` |
| Tap swing contribution | up to `1.15°` |
| Combined wind + tap hard cap | `1.4°` |
| Swing frequency | `2.35 Hz` |
| Exponential damping | `2.9` |
| Local hit target | `104 × 190 px` |

- The first valid press responds immediately.
- Presses during cooldown are ignored and never queued.
- Each lantern owns its own cooldown and response.
- The tap uses two soft, irregular intensity dips instead of a harsh strobe.
- Core, local halo, and the corresponding `PointLight2D` pool recover to their
  exact pre-tap levels.
- Existing asynchronous ambient wind and practical-light pulse remain intact.
- Reduced Motion suppresses the tap flick and spatial swing and restores the
  registered neutral pose.

## Validation

- complete Godot suite: **23/23 pass**;
- phone-sized input target and pivot hierarchy: pass;
- immediate response, non-queuing cooldown, and reactivation at `1.5 s`: pass;
- independent left/right foreground light-pool coupling: pass;
- fixed anchor and combined `1.4°` transform cap: pass;
- reduced-motion suppression and exact recovery endpoints: pass;
- 6-second Forward Mobile / Metal deterministic capture: pass;
- Godot iOS export and generated-project personal-signing guard: pass;
- Xcode debug build and strict code-sign validation: pass;
- install and launch on Mauricio's iPhone 17 Pro Max: pass.

## Preserved rollback

The exact approved V015 source is commit `f456601` and annotated tag
`checkpoint/home-proprietor-micro-idle-v015-2026-08-01`. It was already on the
remote before V016 work began.
