# Tripo mouth transfer candidate — frozen source-extraction checkpoint

Status: **stopped at checkpoint 20; no mouth retopology authored**.

This bounded candidate tested whether the immutable VG06 open-mouth Tripo
source could provide a complete, source-defined aperture loop for a localized
welded quad retopology on the S40 r003 production body. It could not do so
without inventing the tongue-occluded lower lip contour, so the stop rule was
applied before any body edit.

## Locked inputs

- Open geometry authority:
  `art/candidates/tripo/visual-gate-06/h31-detailed-open-mouth/tripo-out/model.glb`
  — SHA-256
  `7c0d7e2e1e4ee8fb4db320880f6f4b5c82c470bce37437ce28d26efa171b01d4`.
- Production body:
  `art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/bentosaur_hero_s40_production_topology_r003.blend`
  — source SHA-256
  `181d93014f1667d9044d12e24fa297f4b391c9eb8d1164ddc5f45f3971f7caf9`.
- Body object: `BENTOSAUR_BODY_RETOPO_WIP_R003`, 10,050 vertices /
  10,048 all-quad faces.

The exact shared closed-source production normalization was applied:

```text
canonical_x = vendor_y * 1.0207102117712663
canonical_y = -vendor_x * 1.0207102117712663
canonical_z = vendor_z * 1.0207102117712663 + 0.499774008028646
```

## Preserved checkpoints

- `work/00_locked_inputs.blend`
- `work/10_exact_matrix_aligned_overlay.blend`
- `work/20_source_mouth_region_extraction.blend`
- `source/tripo_mouth_transfer_alignment_extraction.blend`

Checkpoint 20 contains the unchanged S40 body, the full locked open source,
and an 83,622-vertex / 165,859-triangle broad inspection-only source mouth
region. The region bounds are not an aperture curve.

## Stop-rule evidence

The first absolute open-depth diagnostic selected the lower muzzle/body
transition and was rejected. The one permitted correction used the preserved
r001 neutral/open front-depth delta, its validated `0.025` threshold, and the
measured production-space envelope `x ±0.10`, `z 0.4328..0.5143`.

It produced:

- one dominant connected recessed-cavity component: 1,008 pixels;
- two isolated one-pixel outliers;
- dominant bounds:
  `x -0.08290..0.08271`, `z 0.45788..0.51118`.

That dominant component is not a complete lip aperture. Its lower edge is the
visible tongue/front-volume occlusion edge. Turning it into a welded loop
would encode the tongue silhouette and invent the hidden lower lip contour.
The authorized source data therefore support a cavity envelope, not a
programmatically defensible production mouth loop.

No Boolean mouth, spline, ellipse, Bezier, reused r003 aperture, manual
projection, tongue mesh, or production-body edit was created.

## Next authorized action

Continue from `work/20_source_mouth_region_extraction.blend` in a deliberate
manual Blender retopology session:

1. keep the full VG06 shell and extracted region locked;
2. select an existing S40 facial boundary outside the mouth envelope;
3. use surface snapping / Shrinkwrap and Poly Build or an equivalent
   retopology tool to place three or four lip-support loops against every
   visible Tripo contour;
4. place the tongue-occluded lower lip loop as an explicit artist decision,
   guided by the neutral source and the continuous visible side contours;
5. rebuild the tongue as a separate closed mesh;
6. weld the facial region to the body and stop at
   `30_TRIPO_OPEN_MOUTH_TRANSFER_STATIC`.

This is not permission for another automatic contour, Boolean, generated
mouth, or paid Tripo task. Mau must approve the static front, three-quarter,
profile, gameplay, wireframe, and source-overlay evidence before rigging.

## Evidence and reports

- `evidence/tripo_transfer_stop_evidence_board.png`
- `qa/open_closed_delta_component_overlay.png`
- `qa/open_closed_delta_verdict.json`
- `qa/alignment_extraction_report.json`
- `qa/open_source_production_body_deviation.json`

The deviation render measures the unchanged closed-source S40 body against
the independently generated open source only; it is alignment evidence, not
a candidate-retopology error map.

## Reproduction

```bash
EXPERIMENT=art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r004

/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python "$EXPERIMENT/recipes/build_locked_alignment_extraction.py"

python3 "$EXPERIMENT/recipes/derive_open_closed_delta_verdict.py"

/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python "$EXPERIMENT/recipes/render_alignment_extraction_evidence.py"

node "$EXPERIMENT/recipes/build_artifact_manifest.mjs"
```

No paid API or Tripo operation was used. Credits spent: `0`; recorded balance:
`4,695`.
