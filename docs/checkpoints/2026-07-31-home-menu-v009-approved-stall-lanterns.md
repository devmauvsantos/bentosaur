# Home Menu V009 — Approved Modular Stall Lanterns

**Status:** founder approved, runtime promoted

**Date:** 2026-07-31

## Outcome

The approved empty stall now carries two real modular hanging lanterns. They
are not flattened into the stall and they do not switch between separately
generated ON/OFF pictures.

```text
OFF = fixed anchor + canonical body_off
ON  = fixed anchor + canonical body_off + core_add + halo_add
```

This keeps the anchor stationary, lets the complete physical shell sway from
the center of its upper ring, and guarantees that power changes cannot alter
the silhouette or cage geometry.

![V009 Godot runtime capture](assets/home-menu-v009-approved-stall-lanterns.png)

## Approved source authority

The visual gate, immutable generation result, extracted components, prompt,
manifest, and approval evidence live under:

`art/source-assets/home-menu/stall/v003-lantern-lighting/`

Mau approved the design, scale, registration, dark-honey OFF appearance,
amber ON core/halo, and anchor connection. A subtle warm spill across the
stall's wooden surfaces is intentionally deferred; it must not force a future
lantern redesign.

## Runtime assets

Runtime textures are trimmed derivatives, not direct references to source-art
candidates:

```text
game/assets/environments/home_village/v001/stall/attachments/v001/lantern/
├── stall_lantern_anchor_v001.png       43 × 35
├── stall_lantern_body_off_v001.png     75 × 175
├── stall_lantern_core_add_v001.png     57 × 72
├── stall_lantern_halo_add_v001.png     208 × 224
└── runtime_manifest.json
```

The halo is the exact trim of the approved registered proof, not a newly
approximated gradient. The promotion is rebuilt by:

`tools/art/promote_stall_lantern_runtime_v001.py`

## Registration

Both instances remain children of the responsive `StallStage` and therefore
inherit its locked `0.86` framing transform on ultratall phones.

| Fixture | Ring-center root | Body top-left | Core top-left |
|---|---:|---:|---:|
| Left | `(134.5, 437)` | `(97, 425)` | `(106, 479)` |
| Right | `(583.5, 437)` | `(546, 425)` | `(555, 479)` |

The source ring-hole center was measured at local `(37.5, 12)`. This pivot
reproduces the approved static placement while making the sway mechanically
believable.

## Runtime component

`game/scenes/home/components/stall_lantern_fixture.tscn` contains:

```text
StallLanternFixture
├── Anchor                  fixed
└── SwayPivot
    ├── LocalHalo           additive, unshaded
    ├── BodyOff             canonical physical shell
    └── Core                additive, unshaded
```

The typed controller supports:

- animated and immediate `set_powered` transitions;
- autonomous restrained ambient sway;
- future shared-wind ownership through `apply_wind`;
- future light-director ownership through `apply_light_motion`;
- reduced motion;
- deterministic tests;
- an absolute `1.4°` rotation ceiling.

No `PointLight2D`, physics joint, skeleton, or raster animation sheet is used.
Core and halo power fades do not reset sway phase or rotation.

## Deferred lighting polish

The following are deliberately not part of V009:

- subtle warm spill painted across the stall wood;
- lantern-specific wet-pavement reflection masks;
- coupling the new fixtures to the neighborhood pulse/flick director;
- physical-iPhone motion and brightness tuning.

These additions must remain separate registered layers and follow each
fixture's frame-level light state without modifying the approved shell.

## Verification

The complete current Godot test suite passed under Godot `4.7-stable` Mobile:

- 13 of 13 `tests/*_test.gd` contracts;
- home-menu boot and `StallStage` integration;
- exact texture dimensions and ring-center registration;
- static anchor versus rotating shell hierarchy;
- geometry-identical OFF/ON states;
- additive core and halo materials;
- power fade, sway-phase preservation, reduced motion, and hard rotation cap;
- post-process coverage, rain, mobile display, and personal iOS signing.

The final capture rendered through Forward Mobile / Metal at `540 × 960`,
including the approved anime-transfer shader.
