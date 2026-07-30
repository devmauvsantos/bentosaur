# Bentosaur localized joint deformation repair

## Outcome

**Final status: failed diagnostic branch retained for evidence.**

The best isolated candidate is formally closed, all-quad, one-shell, and
mirror-connected, but it is **not usable and must not be promoted**. The
nearest-surface projection step collapsed many of the newly inserted support
ring vertices into nearly coincident points. The resulting sliver geometry
fails practical rest-shape QA and performs worse than canonical r003 in the
bounded deformation re-probe.

No canonical file, r003 file, prior experiment, or production location was
modified. No user approval is asserted.

## Immutable input

- Canonical blend:
  `art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/bentosaur_hero_s40_production_topology_r003.blend`
- Object: `BENTOSAUR_BODY_RETOPO_WIP_R003`
- SHA-256 before and after:
  `181d93014f1667d9044d12e24fa297f4b391c9eb8d1164ddc5f45f3971f7caf9`

## Current diagnostic candidate

- Blend: `stages/40_paired_joint_support_loops_candidate.blend`
- Object: `BENTOSAUR_JOINT_REPAIR_CANDIDATE_NOT_APPROVED`
- 10,610 vertices, 21,216 edges, 10,608 quad faces
- Zero triangles/ngons/boundaries/non-manifold edges
- One positive-volume shell, Euler characteristic 2
- Lineage-aware mirror audit: 21,216/21,216 edges and 10,608/10,608
  faces match, with zero mirror-map involution failures
- 560 new vertices:
  - shoulders/armpits: 120
  - hips/groin: 232
  - knees: 208
- Passing tail zone: zero new vertices; all 861 original tail vertices retain
  exact coordinates
- Mouth/head zone: zero new vertices above Z=0.60; all 3,272 original vertices
  in that audit zone retain exact coordinates

The unconstrained nearest-point symmetry ratio in the primary topology record
is intentionally retained as a diagnostic. It is not authoritative because it
can pair a newly inset vertex with a nearby preserved canonical vertex. The
partitioned canonical/new-lineage map is bijective and is the authoritative
connectivity result.

## Why the candidate fails

Rest-shape support-ring audit:

- minimum new-incident edge: `1.1175870895385742e-08`
- 500 new-incident edges below 35% of preserved-edge median
- 472 new-incident faces with edge aspect ratio above 10
- new-incident face-aspect p95: `1,112,142.62`

The BMesh inset itself remained all-quad. The failure occurred when its new
vertices were independently projected to the nearest point on canonical r003:
many points landed on or extremely near existing positions. Formal
non-manifold/zero-length tests were too permissive to catch this practical
collapse, but the explicit rest-geometry audit and deformation probe did.

## Bounded deformation re-probe

The re-probe reused the exact preserved r003 head-lock armature, automatic
weight baseline, single cleanup, pose definitions, region classifier, metrics,
and thresholds.

| Pose | Canonical r003 | Candidate | Result |
| --- | --- | --- | --- |
| neutral | pass | pass | unchanged |
| reach/tray hold | fail | fail, materially more flagged faces/edges | fail |
| squat | fail | fail, materially more flagged faces/edges | fail |
| walk extreme | fail | fail, materially more flagged faces/edges | fail |
| tail bend | pass | fail threshold evaluation in legs/torso | regression |

Authoritative report:
`deformation-reprobe/bounded_deformation_reprobe_report.json`

Pose evidence:
`deformation-reprobe/bounded_reprobe_pose_contact_sheet.png`

## Visual QA

- Matched before/after wire board:
  `evidence/before_after_wire_board.png`
- Coral marks faces incident to the new support-ring vertices.
- Editable render scene:
  `stages/50_before_after_wireframe_qa_scene.blend`

## Numbered editable source checkpoints

Topology:

1. `stages/00_canonical_r003_full_exact_copy.blend`
2. `stages/05_body_only_working_snapshot.blend`
3. `stages/10_paired_shoulder_armpit_support_ring.blend`
4. `stages/20_paired_hip_groin_support_ring.blend`
5. `stages/30_paired_knee_support_ring.blend`
6. `stages/40_paired_joint_support_loops_candidate.blend`
7. `stages/50_before_after_wireframe_qa_scene.blend`

Bounded re-probe:

1. `deformation-reprobe/stages/60_reprobe_armature_no_weights.blend`
2. `deformation-reprobe/stages/65_reprobe_automatic_weights.blend`
3. `deformation-reprobe/stages/70_reprobe_headlock_weights_neutral.blend`
4. `deformation-reprobe/stages/80_pose_neutral.blend`
5. `deformation-reprobe/stages/81_pose_reach_tray_hold.blend`
6. `deformation-reprobe/stages/82_pose_squat.blend`
7. `deformation-reprobe/stages/83_pose_walk_extreme.blend`
8. `deformation-reprobe/stages/84_pose_tail_bend.blend`

All failed branches and their reason codes remain under `failed-branches/`.

## Reproducibility and QA

- Primary report: `qa/paired_joint_support_loop_report.json`
- Practical geometry audit: `qa/support_ring_geometry_audit.json`
- Lineage-aware symmetry audit: `qa/partitioned_symmetry_audit.json`
- New-vertex indices: `qa/paired_new_vertex_indices.json`
- Full SHA-256 inventory: `qa/inventory_manifest.json`
- Failed-branch outcomes: `failed-branches/branch_outcomes.json`
- Reproducible scripts: `recipes/`

## Constraint for any future authorized iteration

Do not reuse independent nearest-point projection for new inset vertices.
Construct genuinely spaced manual quad rings along tangent/geodesic flow,
validate edge length, face area, and face aspect before any rig run, and only
then repeat the bounded deformation gate. This branch does not authorize or
perform that next iteration.
