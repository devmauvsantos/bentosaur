# Stall Aspect Repair V002

Status: approved and promoted to runtime — 2026-07-31

## Defect

The untouched Gate 1 cutout has visible alpha bounds of `862 × 1333`, an
aspect ratio of `0.6467`. The v001 registration independently scaled the two
axes and produced runtime bounds of `492 × 875`, an aspect ratio of `0.5623`.
The runtime stall therefore retained only about `86.9%` of its correct width
relative to its height.

## Repair

V002 starts from the immutable cutout:

`art/source-assets/home-menu/stall/v001/generated/`
`stall_structure_unlit_cutout_v001.png`

It applies one uniform `130.8327%` scale, then registers that result on the
existing `1440 × 2560` canvas at `(116, 140)`. This preserves the current
vertical size and placement while restoring the source aspect ratio.

Measured repaired bounds:

- registered source: `1129 × 1746 +156 +396`;
- runtime candidate: `566 × 874 +77 +197`.

No pixels were generated or repainted. This is a deterministic registration
repair.

## Files

- `generated/stall_structure_unlit_registered_1440x2560_v002.png`
- `generated/stall_structure_unlit_runtime_720x1280_v002.png`
- `reviews/stall_structure_unlit_composite_720x1280_v002.png`
- `reviews/home_menu_ultratall_corrected_stall_preview_720x1564_v002.png`

The founder rejected the narrow deployed stall on the physical iPhone and
approved this proportion repair. The runtime stall and owner occluder are now
both derived from this corrected master. The automated contract locks the
visible silhouette to the source aspect ratio so it cannot regress to
independent X/Y scaling.
