# Visual Gate 03 — bentosaur_vg06_h31d_open_01

**Decision:** `HOLD_FOR_CLAY_REVIEW`  
**Expected mouth:** `open`  
**Source role:** `candidate`

This package evaluates untextured geometry only. The source GLB is imported
into `00_SOURCE_LOCKED_READ_ONLY`, hidden from renders, and never modified.
Every render uses deep mesh duplicates.

For the production Bentosaur candidate, `closed` means a relaxed neutral mouth
seam. A mouth cavity, tongue, delighted open smile, and chewing deformation
system are constructed later during the Blender production rebuild.

## Evidence

- `boards/vg03_hd_clay_six_view.png`
- `boards/vg03_hd_clay_feature_closeups.png`
- `topology-metrics.json`
- `gate-policy.json`
- `gate-decision.json`
- `review-template.json`
- `bentosaur_vg06_h31d_open_01_source_locked_evaluation.blend`

## Continuation rule

The pipeline may programmatically continue only when:

1. every machine check in `gate-decision.json` passes;
2. every visual feature receives an integer score of at least `2/3`;
3. the visual-feature average is at least `2.5/3`;
4. every named visual blocker is explicitly `false`;
5. this is a real `candidate`, not a `placeholder`.

A pass authorizes retopology, semantic material authoring, controlled eye
construction, and production mouth construction. It does **not** authorize
rigging, skinning, animation, game integration, or final appearance approval.

Score meaning:

- `0`: missing, fundamentally wrong, or unusable;
- `1`: major visible defects; regeneration is preferable;
- `2`: correct broad volume; repairable during production rebuild;
- `3`: clean intentional source form with only minor cleanup.
