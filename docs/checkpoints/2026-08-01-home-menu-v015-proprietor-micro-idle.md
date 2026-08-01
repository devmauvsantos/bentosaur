# Home Menu V015 — Proprietor Micro-Idle

**Status:** implemented, tested, captured, and deployed; founder phone-scale
motion approval pending

**Date:** 2026-08-01

## Outcome

The counter proprietor now feels alive without becoming rubbery. The existing
small breath remains unchanged, and a rare body-pivot lean creates the illusion
of a tiny head movement with the current flattened character art.

![Rest versus deterministic peak](../../game/docs/runtime-captures/home-menu-v015-proprietor-micro-idle/home-menu-v015-rest-vs-peak-1080x600.png)

## Runtime structure

```text
VisualRoot                         fixed registered scale 0.20
├── BodyMotionRoot                 breath + rare micro-lean
│   ├── Neutral
│   └── Blink
└── ForegroundHands                fixed counter contact, effective z16
```

The body pivot is the existing counter-contact bottom center. Rotation
therefore grows toward the oversized head while remaining nearly zero at the
counter. The hands are outside that pivot and remain physically fixed.

This is the safest head-led motion available without cutting a new independent
head layer. It adds no bones, deformation mesh, shader warp, or new raster.

## Motion values

| Property | V015 value |
| --- | ---: |
| Breath period | `3.4 s` |
| Breath vertical maximum | `0.5%` |
| Breath horizontal compensation | `0.25%` |
| Quiet interval after a gesture | `6.5–10.0 s` |
| Lean-in | `0.72–1.05 s` |
| Hold | `0.28–0.72 s` |
| Return | `0.82–1.18 s` |
| Signed angle | `±0.35–0.50°` |

The deterministic proof starts its first lean at `8.733 s`, reaches a
`0.4463°` peak at `9.533 s`, and then returns to the registered pose.

## Accessibility and performance

Reduced Motion returns scale and rotation to the exact baseline immediately.
The discrete blink expression remains active. Runtime cost is one extra
`Node2D` transform, a separate lightweight RNG, and a few scalar operations per
frame; no Tween, allocation loop, skeleton, or extra texture is involved.

## Validation

- complete Godot suite: **23/23 pass**;
- deterministic equivalence at 30, 60, and 120 FPS: pass;
- foreground hands unchanged for the full 30-second motion probe: pass;
- breath and rotation budgets: pass;
- reduced-motion and inactive endpoints: pass;
- V014 foreground-relight receiver paths and contract: pass;
- 12-second Forward Mobile / Metal full-frame and enlarged-crop captures: pass;
- Godot iOS export and personal-signing contracts: pass;
- Xcode debug build and strict code-sign validation: pass;
- install and launch on Mauricio's iPhone 17 Pro Max: pass.

The physical phone remains the final authority for whether `0.35–0.50°` is the
right personality. If it is too visible, tune only the angle range; if it feels
too frequent, tune only the quiet interval.

## Preserved rollback

The exact pre-motion V014 source remains commit `d7a8e4a`. It was separately
exported, personally signed, installed, and launched on the phone before any
V015 source edit, as requested.
