# Bentosaur Facial Experiment r005

Status: frozen rejected research checkpoint

Production approval: no

Rigging authorization: no

This versioned checkpoint preserves the two bounded Checkpoint-30 attempts to
transfer the immutable VG06 delighted-open Tripo mouth onto a copy of the S40
r003 production body. It is retained because its positive and negative results
directly define the topology prerequisite for the next Faceit-style facial
pipeline.

No paid API was called and no Tripo credits were consumed.

## Lineage

The exact upstream files are already versioned in r004:

- `r004/work/00_locked_inputs.blend`
  — SHA-256
  `1b29d0f22e796c61cd4a2bd348c46601ed143d8067029761cc1601caac5852d1`;
- `r004/work/10_exact_matrix_aligned_overlay.blend`
  — byte-identical to checkpoint 00;
- `r004/work/20_source_mouth_region_extraction.blend`
  — SHA-256
  `9f9ca58f34dc46037e7c3bcadd2e8c399ba7e12f62a9551322c1a2c4dde3951f`.

Those duplicates are not copied into r005. The new topology-changing source
files are:

- `work/30a01_TRIPO_OPEN_MOUTH_TRANSFER_STATIC.blend`;
- `work/30a02_TRIPO_OPEN_MOUTH_TRANSFER_STATIC.blend`.

The `.blend` files are editable Blender sources, not runtime assets.

## a01 — rejected

The first implementation retained the selected 320-quad disk connectivity and
radially repositioned its 278 interior vertices.

It proved that a recessed, closed, all-quad mouth bag and a separate tongue
could remain within the mobile budget. It failed visually and topologically:

- panel-like facial region;
- spikes and folds below the mouth;
- patch aspect P95 `22.67`, maximum `249.41`;
- seam-normal P95 `84.89°`, maximum `122.46°`.

Evidence:

`evidence/a01/a01_evidence_board.png`

## a02 — improved but rejected

The one permitted correction rebuilt the selected region while preserving the
exact 86-vertex outer boundary:

- 344 skin-annulus quads;
- 602 cavity-wall quads;
- 462 all-quad cap faces;
- separate closed tongue;
- total candidate budget of 22,976 rendered triangles.

It passed:

- unchanged outside connectivity;
- exact preserved boundary coordinates;
- one connected closed all-quad body shell;
- Euler characteristic `2`;
- zero boundary, non-manifold, loose, overfull, or zero-area elements;
- maximum symmetry error `6.34e-8`;
- upper-lip/corner source-fit maximum `0.00253`;
- separate closed, centered tongue;
- the bounded mobile triangle budget.

It failed:

- visible folds/tears beneath both mouth corners;
- five patch-involved self-overlap candidates;
- patch aspect P95 `5.65`, maximum `109.07`;
- seam-normal P95 `119.28°`, maximum `177.48°`;
- 12 of 86 outer seam edges above `30°`.

Therefore a02 must not be rigged, animated, exported to Godot, or promoted to
S40.

Evidence:

- `evidence/a01_vs_a02_stop_board.png`;
- `evidence/a02/a02_evidence_board.png`;
- `evidence/a02/05_front_mouth_close.png`;
- `evidence/a02/06_wire_front_close.png`;
- `evidence/a02/08_source_overlay.png`.

QA:

- `qa/checkpoint30_static_transfer_report_a01.json`;
- `qa/checkpoint30_static_transfer_report_a02.json`;
- `qa/checkpoint30_a02_readonly_integrity.json`.

## Stop decision and next direction

The bounded rule allowed one implementation and one focused correction. No
a03 was attempted.

The experiment proves that the Tripo delighted-open silhouette, cavity, and
tongue can fit inside the mobile budget. It also proves that this selected S40
boundary is not a safe direct weld target without a redesigned transition
zone.

The next direction is documented in:

`docs/facial-animation-faceit-ai-pipeline-v1.md`

Faceit does not repair r005. Work resumes with one approved canonical neutral
face, then a bounded Faceit 2.3 authoring pilot.
