# S40 r002 center-seam all-quad experiment

Status: isolated experiment complete. No production file was modified.

## Recommended experimental candidate

`axis-qf-seam-stitch/30_axis_qf_closed_cleanup.blend`

SHA-256:
`8c0d8e08ed05d14cb2407f52f791eb43c05eaaa0f373bad158d9b4de44076cd6`

The successful route was:

1. Duplicate the preserved S40 r002 symmetrized bootstrap.
2. Apply its tiny vendor rotation while preserving world-space geometry.
3. Rotate the vendor Y=0 bilateral plane onto Blender QuadriFlow's X axis.
4. Explicitly set Mesh symmetry to X.
5. Run symmetric QuadriFlow.
6. Remove exact degenerates.
7. Rotate back to vendor coordinates.
8. Snap only the open mirrored boundary vertices onto Y=0.
9. Weld coincident mirror-boundary pairs.
10. Recalculate normals and validate.

All material operations have their own `.blend` checkpoint under:

- `axis-aligned-symmetric-quadriflow/`
- `axis-qf-seam-stitch/`

Final technical QA:

- vertices: 10,050
- edges: 20,096
- faces: 10,048
- quads: 10,048
- triangles/ngons: 0 / 0
- boundary/non-manifold edges: 0 / 0
- zero-area faces: 0
- connected shells: 1
- Euler characteristic: 2
- signed volume: +0.0934428664
- loose/zero-length geometry: 0
- exact vertex symmetry: yes
- exact mirrored edge/face topology: yes
- P95 deviation from preserved S40: 0.09599% of character height
- acceptance ceiling: 0.15% of character height

The original production checkpoint remains:

- SHA-256:
  `f690e66b6d4d744eb75bcab00af18ef73a1d692d72e8600916528cc7dd571894`

## Quad quality

The welded seam is materially cleaner than the zero-motion retile:

- seam P95 aspect ratio: 2.60
- seam median aspect ratio: 1.25
- seam P95 corner skew: 29.79 degrees
- seam P95 diagonal warpage: 38.41 degrees
- 99.35% of seam vertices have valence 3, 4, or 5

Known local cleanup remains around the crotch/tail-base transition:

- two valence-2 vertices near X -0.12, Z -0.21
- maximum seam aspect ratio: 9.70
- a few strongly warped quads around the same transition

This is therefore a strong all-quad symmetric bootstrap, not yet a rig-ready
deformation master. The mouth/oral cavity and authored joint routing remain
separate production topology work.

## Alternate evidence

`mirrored-final-pair/30_all_quad_exact_symmetric_candidate.blend` also passes
the formal topology/symmetry/deviation gates while preserving every source
vertex exactly. It is not recommended as the primary candidate because its
edited quads are substantially worse:

- edited P95 aspect ratio: 22.45
- edited P95 corner skew: 88.61 degrees
- edited P95 diagonal warpage: 103.59 degrees

Its value is forensic: it proves the 132 triangles and 120 pentagons can be
eliminated without moving any source vertex.

The first global QuadriFlow attempt omitted the Mesh `use_mirror_*` axis
configuration and was correctly rejected for asymmetry. Direct vendor-Y
symmetry produced exact mirrored vertex positions but an open seam. The
axis-aligned route plus explicit seam stitch is the best tested result.

## Evidence

- Full validation: `axis-qf-seam-stitch/report.json`
- Independent shell audit: `axis-qf-seam-stitch/final_integrity_audit.json`
- Quad quality: `axis-qf-seam-stitch/quad_quality_audit.json`
- Six-view seam board: `axis-qf-seam-stitch/seam_wire_qa_board.png`
- Individual close-ups: `axis-qf-seam-stitch/seam-wire-closeups/`
- Exact-zero-motion fallback report: `mirrored-final-pair/report.json`
- All scripts and probe reports are preserved in this directory.
