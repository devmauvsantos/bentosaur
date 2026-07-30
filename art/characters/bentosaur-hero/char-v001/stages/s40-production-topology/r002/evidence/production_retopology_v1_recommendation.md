# Bentosaur Production Retopology V1 — Executable Recommendation

Status: analysis and disposable Blender probes complete  
Scope: topology bootstrap through rig-ready geometry  
Production files modified: none

## Decision

Use a hybrid pipeline:

1. The accepted H3.1 Extreme GLB remains the immutable visual source.
2. The repaired Smart LowPoly Blender file remains the silhouette/projection
   scaffold.
3. Run Blender QuadriFlow once, without its symmetry option, at roughly 12,000
   target faces to create a globally regular all-quad bootstrap.
4. Remove exact degenerates and use BMesh Symmetrize from the negative-Y side
   to obtain an exact bilateral, closed bootstrap.
5. Treat the center strip, mouth/face, shoulder roots, elbows, pelvis/groin,
   knees, and eye construction as authored production topology.
6. Preserve suitable QuadriFlow areas such as limbs, torso panels, most of the
   head back, and most of the tail.

This is materially less manual work than patching the original Tripo face flow
or retopologizing the two-million-triangle source from nothing. It is not a
one-click final mesh.

## Source inventory

| Role | File | SHA-256 |
| --- | --- | --- |
| Immutable appearance source | `art/candidates/tripo/visual-gate-04/h31-extreme-texture/tripo-out/model.glb` | `40de6b43b0dc0313e084005b711cb549dfe6dfceeebe45c6275761c99b96dc79` |
| Repaired topology/silhouette scaffold | `art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/subagent-cycle-audit/cycle_patch_candidate.blend` | `41a48a1edecb9ace84cef6284e0d17c1355199cc3570af0f1fede78e87d37e7f` |
| Rebake appearance proof only | `art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/rebake-proof/repaired_rebaked.glb` | `b9d80ab6c2e1362a14aa4703c270f7fda2b0b33b5586148e7c4f884c8f99811a` |
| Mouth look/behavior reference, not topology source | `art/candidates/tripo/visual-gate-04/mouth-diagnostic-v12-hd-final-proxy/bentosaur_vg03_h31_mouth_diagnostic_v12_hd_final_proxy_static_master_user_approval_required.blend` | `9eb87828392c95d25572c07575ea5ece58224e9cfa80c23b85c2ce8d4ec0a571` |

## Blender probe evidence

### QuadriFlow without symmetry

Input repaired scaffold:

- 13,020 faces
- 11,075 quads
- 1,939 triangles
- 6 ngons
- 0 boundary or non-manifold edges

Disposable QuadriFlow result:

- 11,425 faces, all quads
- 6 boundary/non-manifold edges
- mean deviation from repaired scaffold: 0.0253% of character height
- P95 deviation: 0.0893% of height
- maximum deviation: 0.794% of height

The surface is retained closely and the body/joint grid becomes much more
regular, but the result is not bilaterally topological and the mouth flow is
not anatomical.

### Exact BMesh symmetry from negative Y

After degenerate cleanup and BMesh `symmetrize(direction="-Y")`:

- one connected, closed shell
- exact bilateral geometry and topology
- 11,888 faces
- 11,636 quads
- 132 triangles
- 120 ngons
- 0 boundary or non-manifold edges
- mean deviation from the repaired scaffold: 0.0253% of character height
- P95 deviation: 0.0924% of height
- maximum deviation: 0.983% of height

The mixed faces are concentrated along the reconstructed center strip. That
strip must be manually cleaned; it must not be sent directly to rigging.

### Measured deformation-zone improvement

| Region | Repaired Smart LowPoly | Symmetrized QuadriFlow bootstrap |
| --- | ---: | ---: |
| Shoulder | 81.6% quads / 50.8% clean | 100% quads / 98.9% clean |
| Elbow | 80.0% quads / 39.9% clean | 99.8% quads / 97.1% clean |
| Hip | 78.6% quads / 49.0% clean | 100% quads / 98.9% clean |
| Knee | 84.2% quads / 51.9% clean | 100% quads / 99.5% clean |
| Tail base | 85.5% quads / 62.2% clean | 94.8% quads / 88.6% clean |
| Mouth | 79.4% quads / 52.5% clean | 85.1% quads / 75.6% clean, but P95 aspect ratio worsens to 17.25 |

"Clean" means an all-quad, valence-four vertex in the heuristic region. It
does not prove anatomical edge-loop routing. The mouth still has no opening,
oral cavity, jaw, or concentric lip loops.

### Rejected automatic variants

- Blender QuadriFlow with the original Y-axis symmetry flags produced hundreds
  of open edges because the operator is effectively X-plane oriented.
- Rotating into the operator's X symmetry produced a half result with hundreds
  of boundary edges and did not yield a closed production mesh after a live
  mirror.
- A simple Mirror/Bisect application on the no-symmetry result made exact
  symmetry, but created center-strip tris/ngons and could preserve the wrong
  local defect depending on the retained side.

The tested BMesh negative-Y symmetry is the best bootstrap, but it remains a
bootstrap.

## Required source-preserving directory contract

Each stage must be append-only and must physically preserve its direct input:

```text
art/production/characters/bentosaur/master-v1/
  00-provenance/
    sources/
      h31-extreme-source.glb
      smart-lowpoly-repaired-source.blend
      mouth-look-reference.blend
    source-manifest.json
  01-topology-bootstrap/
    source/
      stage-00-approved.blend
    work/
      bentosaur-retopo-bootstrap-wip-v001.blend
      bentosaur-retopo-bootstrap-wip-v002.blend
    output/
      bentosaur-retopo-bootstrap-candidate-v001.blend
    qa/
    stage-manifest.json
  02-center-and-components/
    source/
      stage-01-approved.blend
    work/
    output/
    qa/
    stage-manifest.json
  ...
```

Rules:

- Never edit `source/` in place.
- Never overwrite a WIP or output file; increment the version.
- Every manifest records parent stage, input and output SHA-256, Blender
  version, script version, parameters, QA results, and human approval state.
- The next stage begins only from a copied, accepted output of the previous
  stage.
- Pack external resources into milestone `.blend` files, while retaining the
  original external sources in `00-provenance/sources`.
- Render front, side, back, three-quarter, and critical closeups at every gate.

## Executable stages

### 00 — Provenance lock

Automation:

- copy all four source files into the production tree;
- hash and size them;
- create a source-lock Blender file with read-only/hidden collections;
- record +X front, ±Y sides, +Z up and the exact character bounds.

Gate:

- hashes equal the current accepted source hashes;
- no source object has been modified.

### 01 — Hybrid topology bootstrap

Automation:

- deep-duplicate the repaired Smart LowPoly mesh;
- run QuadriFlow at a versioned target near 12,000 faces with symmetry off;
- remove exact degenerates;
- BMesh-symmetrize from negative Y;
- recalculate normals;
- preserve the high source as a shrinkwrap/projection reference;
- create named vertex groups marking center, mouth, shoulder, elbow, hip,
  knee, tail base, and preserved static regions;
- run manifold, symmetry, aspect-ratio, and surface-deviation audits.

Manual:

- approve silhouette versus H3.1;
- identify any softened horn, claw, frill, finger, or toe shape.

Gate:

- one closed shell;
- exact bilateral topology;
- accepted silhouette;
- center-strip mixed faces explicitly tagged for Stage 02.

### 02 — Center strip and independent components

Manual:

- rebuild the center strip as controlled quads;
- make eyes separate expressive objects;
- decide whether the nose horn, dorsal/frill knobs, claws, and primary horns
  remain attached or become rigid overlapping components;
- keep poles away from the mouth, jaw hinge, limb roots, and tail base.

Automation:

- shrinkwrap/projection assistance;
- paired-side validation;
- component naming and export-role metadata.

Gate:

- no centerline ngons;
- no accidental duplicate or internal faces;
- eyes can support gaze and blink;
- silhouette still matches H3.1.

### 03 — Production face and mouth

Manual:

- delete the automatic mouth patch;
- author three or four concentric lip loops;
- create a real aperture and recessed mouth bag;
- create jaw-hinge support loops through cheek and lower muzzle;
- build a separate tongue;
- author neutral-closed, delighted-open, smile, chew-compression, and blink
  shape states;
- refine the existing V12 mouth look rather than copying its Boolean topology.

Automation:

- place the approved mouth landmark;
- generate a same-count mouth-bag starting mesh and tongue starting mesh;
- drive diagnostic shape keys/controllers;
- detect flipped faces, intersections, and vertices leaving the high-source
  silhouette.

Gate:

- neutral and open states read correctly at gameplay camera distance;
- no visible cavity leaks in front, profile, or three-quarter views;
- no teeth;
- mouth supports jaw motion and chew without collapsing the cheeks.

### 04 — Upper-body deformation topology

Manual:

- three deformation rings around each shoulder root;
- deliberate armpit flow with a compression wedge;
- three-loop elbow bend band;
- move high-valence poles outside the bend zones.

Automation:

- Mirror-based left/right consistency;
- shrinkwrap after loop edits;
- temporary arm bones, auto-weight seed, and extreme-pose renders.

Gate poses:

- arm lift;
- arm forward to hold bento;
- elbow bend;
- hands together at the stall.

### 05 — Pelvis, legs, and tail

Manual:

- rebuild the pelvis-to-thigh junction;
- create continuous groin/glute flow;
- create three-loop knee bands with more volume on the outer bend and enough
  spacing on the inner compression side;
- clean the tail base and center strip while preserving most tail flow.

Automation:

- temporary hips/leg/tail skeleton;
- mirrored weight seed;
- squat, step, and tail-bend validation renders.

Gate poses:

- walk contact and passing poses;
- shallow and deep squat;
- one-foot lift;
- tail left/right/up/down.

### 06 — Topology deformation gate

Automation:

- build the full temporary test skeleton;
- generate deterministic test poses;
- render clay plus wireframe closeups;
- calculate skin-volume change and detect obvious intersections.

Manual:

- weight-paint correction;
- topology correction where weights alone cannot solve deformation;
- user approval of neutral silhouette, open smile, chew, hold-bento, walk,
  squat, and tail poses.

Nothing advances to UVs until this gate passes.

### 07 — Production UV and PBR bake

Manual:

- final seam decisions;
- prioritize face, mouth, hands, and front torso texel density.

Automation:

- UV packing and overlap audit;
- bake base color, normal, roughness, metallic, AO, and material masks from
  the immutable H3.1 source;
- generate bake comparison boards.

Use Substance 3D Painter here if available for cleanup and authored finish.
Painter should not be used before topology and UV approval.

### 08 — Final rig and weights

Semi-automatic:

- generate the Bentosaur skeleton template;
- seed automatic weights;
- mirror valid weights;
- create jaw, eyes, head, root, arm, leg, and tail controls.

Manual:

- bone placement;
- weight painting;
- corrective shape keys for shoulders, hips, knees, and mouth if required.

Gate:

- production pose suite passes without visible collapse or texture stretching.

### 09 — Animation library

Create and preserve source `.blend` actions for:

- idle breathing and tail sway;
- blink and look variants;
- walk;
- approach/stop;
- order reaction;
- hold/receive bento;
- happy reaction;
- chew;
- turn and leave.

Animations live in the Blender source master. Exported clips are derived assets
for Godot.

### 10 — Godot export and runtime validation

Automation:

- deterministic GLB export;
- action-name and bone-name validation;
- texture compression and LOD outputs;
- import smoke test.

Recommended budgets:

- master/LOD0: roughly 25,000–40,000 rendered triangles including face parts;
- LOD1: roughly 10,000–15,000 triangles;
- LOD2/background: roughly 2,500–5,000 triangles;
- one 2K material set for hero/master; smaller atlases for background variants.

Gate:

- same silhouette, materials, mouth states, and animation timing in Blender
  and Godot;
- stable mobile frame time with the planned number of background dinosaurs.

## Automation boundary

| Work | Automation level |
| --- | --- |
| Source copy, hashing, naming, manifests, stage bootstrapping | Full |
| QuadriFlow bootstrap, exact-degenerate cleanup, initial symmetry | Full, then inspect |
| Shrinkwrap/projection and paired-side checks | Full assistance |
| Center strip, mouth loops, shoulder/hip topology and pole placement | Manual |
| Mouth bag/tongue starting geometry and expression controllers | Parameterized starting point |
| UV packing and PBR baking | Mostly automatic after manual seams |
| Skeleton creation and first-pass weights | Semi-automatic |
| Weight correction and corrective shapes | Manual |
| QA poses, renders, metrics, GLB export and Godot smoke tests | Full |
| Animation blocking | Template-assisted |
| Cute motion timing, arcs, overlap, facial acting, final polish | Manual/creative |

## Immediate production action

Create and show only these two checkpoints first:

1. `00-provenance` with copied sources and verified hashes.
2. `01-topology-bootstrap` with the QuadriFlow/BMesh-symmetrized candidate,
   a three-view clay board, a three-view wireframe board, and a topology JSON.

Do not begin rigging, painting, or animation at that point. After the bootstrap
silhouette is accepted, proceed directly to the authored center and mouth
stage.

## Disposable evidence

- `.tmp/subagents/retopo_execution/quadriflow_probe.json`
- `.tmp/subagents/retopo_execution/quadriflow_probe.blend`
- `.tmp/subagents/retopo_execution/quadriflow_audit/`
- `.tmp/subagents/retopo_execution/bmesh_symmetrize_probe.json`
- `.tmp/subagents/retopo_execution/quadriflow_symmetrized_negative_y.blend`
- `.tmp/subagents/retopo_execution/quadriflow_symmetrized_audit/`
- `.tmp/subagents/retopo_execution/rotated_symmetry_quadriflow_probe.json`

These files are analysis artifacts, not approved production sources.
