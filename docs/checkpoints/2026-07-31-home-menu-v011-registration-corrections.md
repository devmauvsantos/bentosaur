# Home Menu V011 — Stall Registration Corrections

**Status:** corrected, captured, tested 21/21, and running on the personal
iPhone; founder phone-scale approval pending

**Date:** 2026-07-31

## Outcome

V011 corrects four phone-scale registration failures found in V010 without
changing the approved stall design:

- the bottle crate now uses the same coherent assembled composition that was
  shown in the approved gate, so the bottles follow the crate's perspective;
- the crate renders in front of the plant pot and behind the red cloth;
- the three rank stars use the plaque's measured, non-uniform socket centers;
- the stockpot lid rests on the rim while remaining a separate, animated part.

![Home Menu V011](assets/home-menu-v011-registration-corrections.png)

![V011 registration detail](assets/home-menu-v011-registration-detail.png)

## Crate authority

The V004 approval proof used
`bottle_crate_assembled_preview_candidate_v001.png`, while V010 later rebuilt
the prop from independently generated pieces. Equal bottle heights, one shared
baseline, and a rectangular front-wall crop erased the authored depth and
redrew the diagonal socket deck over the bottles.

The crate has no first-playable animation or state, so V011 promotes the
approved composition as one static `234 × 202` runtime texture rendered at the
exact logical box `Rect2(470, 618, 117, 101)`. The empty crate and three bottle
pieces remain preserved in source and runtime inventory for a future variant
system; they are not destroyed or treated as interchangeable production
layers.

## Optical registrations

The plaque is horizontally nine-sliced, so its socket cadence is not uniform.
The corrected star positions are:

```text
(29, 8.5)   (93, 8.5)   (158, 8.5)
```

Each slot remains `42 × 34`; fill animation scales around the measured optical
pivot `(21, 17.5)`.

The lid and steam emitter move down together by `20` logical pixels. The lid's
one-pixel translation and `0.7°` occasional rattle remain unchanged, including
their reduced-motion endpoints.

## Evidence

- complete Godot contract suite: **21 passed, 0 failed**;
- deterministic normal and reduced-motion Forward Mobile / Metal captures:
  `540 × 960`, 60 frames, 30 FPS;
- runtime asset promotion: **32 transparent PNG derivatives**, including the
  approved static crate prefab;
- strict app signature: bundle `com.mauvsantos.bentosaur`, personal team
  `53RJ43876F`, `Apple Development: Mauricio Vargas (CRAZV8U43J)`;
- installed and launched on Mauricio's iPhone 17 Pro Max (`iPhone18,2`).

The capture record is under
`game/docs/runtime-captures/home-menu-v011-registration-corrections/`.

## Remaining gate

Mau must review this installed build at physical phone scale. V011 is not a
founder-approved final composition until that review is explicit.
