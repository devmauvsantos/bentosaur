# Visual Gate 03 — H3.1 Detailed Geometry

This gate evaluates the first properly configured H3.1 Detailed, untextured
Bentosaur candidate before any production cleanup or material work.

The production candidate should depict the canonical upright baby Triceratops
as a standalone character with a relaxed, neutral closed-mouth seam. The real
mouth cavity, tongue, delighted open smile, and chewing deformation system are
constructed later in Blender. Props, clothing, floor, pedestal, environment,
text, and baked materials are outside this generation.

## Evaluation command

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup \
  --python tools/blender/evaluate_hd_geometry_gate.py -- \
  --input /absolute/path/to/model.glb \
  --output art/candidates/tripo/visual-gate-03/h31d-01/evaluation \
  --candidate-id bentosaur_vg03_h31d_01 \
  --source-role candidate \
  --expected-mouth closed
```

The evaluator:

- imports the raw GLB into a hidden, source-locked collection;
- performs all rendering and inspection on deep mesh duplicates;
- renders neutral-clay six views;
- renders close-ups of eyes, muzzle/neutral mouth seam from two angles, primary
  horns, frill knobs, hands, feet, and tail;
- calculates raw and seam-welded topology diagnostics;
- creates labeled review boards, a manifest, and a review template;
- emits a deterministic stop/hold/continue decision.

## Exact continuation policy

Automatic continuation to production rebuild work requires every machine
threshold and every visual threshold in `gate-policy-v1.json` to pass.

An incomplete visual review always yields `HOLD_FOR_CLAY_REVIEW`. This is
intentional: topology numbers cannot determine whether an eye looks doubled,
a mouth reads as a smile, or a horn is malformed.

Passing authorizes:

- retopology;
- semantic material authoring;
- controlled eye construction;
- production mouth cavity and tongue construction;
- facial deformation-loop construction.

It does not authorize final appearance approval, rigging, skinning, animation,
or game integration.

## Mouth modes

`closed` is the production mode and the evaluator default. It scores
`neutral_closed_mouth_seam` and only applies the mouth-specific blocker
`malformed_or_collapsed_neutral_mouth_seam`. It never requires a mouth cavity,
tongue, or open-mouth volume.

`open` remains available for evaluating a deliberately open-mouth source. In
that mode, open-mouth shape and cavity blockers apply.

## Placeholder validation

`placeholder-p1-evaluation/` may be generated against the old P1 GLB solely to
prove that the evaluator runs end to end. It is explicitly barred from
unlocking production and is not H3.1 evidence.
