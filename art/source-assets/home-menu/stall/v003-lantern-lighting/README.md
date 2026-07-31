# Stall Lantern Lighting V003

**Visual gate:** G02 — Stall lighting

**Status:** candidate pending founder approval — 2026-07-31

This source pack begins the non-character stall attachment pass. It keeps the
approved empty stall immutable and introduces one reusable hanging-lantern kit
for the left and right fixtures.

## Locked state model

```text
OFF = fixed anchor + canonical body_off
ON  = fixed anchor + canonical body_off + core_add + halo_add + warm_spill_add
```

The physical shell never changes when power changes. The ON state is a
composition, not a separately generated lantern. This guarantees identical
silhouette, cage, outline, pivot, and scale in both states.

The wall/beam anchor is static. The shell sways from the center of its upper
ring. The core and near halo follow the shell. The broad spill remains mostly
registered to the stall so the complete pool of light does not rotate.

## Current candidate registration

- logical canvas: `720 × 1280`;
- shared `StallStage` framing scale: `0.86`;
- shared framing pivot: `(360, 634)`;
- body source: `282 × 657`;
- candidate runtime body width: `75 px` before the stage transform;
- left body top-left: `(97, 425)`;
- right body top-left: `(546, 425)`;
- fixed-anchor top: `y = 392`.

Both fixtures use the same symmetric shell and core. The source anchor is also
symmetric enough to instance twice; if the final eave connection needs handed
mounts, only the anchor will be mirrored or repainted.

## Files

### Immutable generation result

- `generated/lantern-modular-sheet-chroma-candidate-v001.png`
- `generated/lantern-modular-sheet-cutout-candidate-v001.png`

### Extracted candidate components

- `components/stall_lantern_anchor_candidate_v001.png`
- `components/stall_lantern_body_off_candidate_v001.png`
- `components/stall_lantern_core_candidate_v001.png`

### Deterministic registered proof layers

- `registered/stall_lantern_anchors_registered_candidate_v001.png`
- `registered/stall_lantern_bodies_off_registered_candidate_v001.png`
- `registered/stall_lantern_cores_add_registered_candidate_v001.png`
- `registered/stall_lantern_halos_add_registered_candidate_v001.png`
- `registered/stall_lantern_warm_spill_add_registered_candidate_v001.png`

### Approval evidence

- `reviews/stall-lantern-off-registered-composite-v001.png`
- `reviews/stall-lantern-on-registered-composite-v001.png`
- `reviews/stall-lantern-off-on-approval-board-v001.png`

`tools/art/build_stall_lantern_gate_v003.py` rebuilds the registered layers,
reviews, and hashes. The prompt is preserved under `prompts/`.

## Motion destination after approval

- steady shell sway around `0.45–0.9°`, hard maximum `1.4°`;
- shared wind direction with slightly different response/phase per fixture;
- core fade around `180 ms`, halo around `260 ms`, broad spill around `340 ms`;
- power changes never reset the sway phase;
- pulse and flick use the same home-light director as the village sources;
- reduced motion preserves the short power fade but disables ambient sway,
  pulse, and flick.

There will be no physics joint, real-time `PointLight2D`, or animation sheet.
The runtime fixture is transforms, alpha, and low-cost shader scalars.

## Gate decision required

Approve or reject:

1. lantern design relative to the original concept;
2. size and placement against the approved stall;
3. dark-honey OFF appearance;
4. amber ON intensity and halo;
5. the anchor/ring connection.

No pot, button, or remaining counter-prop generation advances until G02 is
approved, per the locked stall layer contract.

