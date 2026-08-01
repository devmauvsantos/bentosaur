# Home Menu V014 — Static Foreground Relight

Date: 2026-07-31

Status: implemented and installed; physical-iPhone visual approval pending.

## Founder decision

Mau approved the lantern-motivated lighting study with one change: the four
menu buttons must remain a little brighter. The rest of the visual target was
approved.

## Safety boundary

The exact pre-relight build remains recoverable at pushed tag:

`checkpoint/home-flat-light-approved-2026-07-31`

The runtime relight itself is also reversible without changing scenes:

```gdscript
set_foreground_relight_enabled(false)
```

or with launch argument `--foreground-relight-off`.

## Implementation

V014 adds a stage-level `StallForegroundRelight` controller and three static
`PointLight2D` pools. It does not alter source artwork, village lighting,
weather, anime post-processing, existing practical-light motion, or the
approved fixture components.

The controller grades only foreground receivers, assigns an isolated light
mask to non-emissive artwork, and restores every touched modulation/mask during
the OFF comparison. The PointLight nodes inherit `StallStage`, so their
registration survives iPhone and ultratall aspect containment.

Buttons use a brighter ambient base than the stall cabinet, and their live
labels receive a small additional lift. The warm pools remain static for this
gate; source/halo/reflection flicker coupling is a later approval.

## Mobile cost boundary

- Three procedural `256 × 256` light textures.
- Additive blend.
- No shadows or occluders.
- No normal/specular maps.
- No per-frame controller work.
- Strict receiver mask and z/layer bounds.

## Evidence

See
[`game/docs/runtime-captures/home-menu-v014-static-relight/`](../../game/docs/runtime-captures/home-menu-v014-static-relight/README.md).

All 23 current Godot contracts and the deterministic Forward Mobile / Metal A/B
capture pass. The personally signed build is installed and running on
Mauricio's iPhone 17 Pro Max. Physical review remains the authority for final
tuning.
