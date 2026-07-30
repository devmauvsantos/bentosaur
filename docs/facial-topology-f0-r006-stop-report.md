# Facial Topology F0 r006 Stop Report

Status: frozen failed experiment

Date: 2026-07-30

Approval owner: Mau

## Outcome

The one authorized automated broad-face topology attempt failed its technical
gate and was stopped before Faceit.

It created a strong Tripo-matched open-mouth silhouette inside a clean,
manifold, all-quad mobile shell. It did not create acceptable cheek and muzzle
flow. The final evidence visibly shows folded lower cheeks, and geometric QA
found severe boundary-normal reversals and 117 overlap candidates.

This is not an approval candidate.

Evidence and editable source:

`art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r006/`

## Checkpoints

### Checkpoint 0 — locked input

Input:

`art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r004/work/20_source_mouth_region_extraction.blend`

SHA-256:

`9f9ca58f34dc46037e7c3bcadd2e8c399ba7e12f62a9551322c1a2c4dde3951f`

The locked S40 body and Tripo open-mouth source were not modified.

### Checkpoint 1 — broad topology implementation

Frozen output:

`art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r006/work/10_F0_BROAD_OPEN_TOPOLOGY_FAILED_FROZEN.blend`

The build used:

- one 496-quad broad face cut;
- one exact 112-edge outer boundary;
- two original-body-surface transition rings;
- two additional rings approaching the mouth;
- a four-ring cavity wall;
- a 28 by 28 all-quad internal cap;
- a separate closed tongue.

### Checkpoint 2 — technical gate

Passed:

- one closed all-quad shell;
- Euler `2`;
- zero non-manifold, boundary, overfull, loose, or inconsistent elements;
- unchanged outside connectivity and boundary coordinates;
- Tripo aperture maximum error `0.00253`;
- `23,168` rendered triangles including tongue;
- no paid API and zero Tripo credits.

Failed:

- seam P95 `162.95°`, maximum `177.18°`;
- aspect P95 `8.45`, maximum `49.19`;
- 117 vertex-disjoint patch overlap candidates;
- visible cheek folds and tears.

The neutral Basis, open expression shape key, expression sweep, Faceit pilot,
rig, animation, and export were therefore not created.

## Root cause

This was not a cut-size problem.

Both r005 and r006 attempted to connect an existing body loop to a very
different smile-shaped aperture by assigning one continuous column to every
boundary vertex. That correspondence is topologically legal but facially
wrong. It forces columns to turn over each other around the lower corners and
pushes the distortion into whichever outer loop is preserved.

A production face needs deliberately placed edge loops and poles:

- circular flow around the lips;
- separate cheek and chin flow;
- controlled count reduction away from the mouth;
- no poles at the smile corners or lower center;
- an independently authored mouth bag.

Faceit cannot infer or repair that mesh flow. Its work begins after it exists.

## Decision

Retire automated concentric/radial mouth bridging for Bentosaur.

The next F0 candidate must use an actual retopology workflow. With the current
installation, that means:

1. duplicate and isolate the head;
2. enable X Mirror and clipping;
3. use Poly Build in Blender's visible 3D viewport;
4. snap and Shrinkwrap to the locked Tripo open-mouth target;
5. author lip loops, cheek flow, chin flow, and poles by hand;
6. build the mouth bag and tongue separately;
7. mirror, weld, and run deterministic QA;
8. ask Mau to approve open static evidence;
9. only then author the neutral Basis on the same vertices;
10. only after F0 approval run Faceit.

AI remains useful for scene preparation, symmetry, source overlays, automated
QA, renders, naming, shape-key bookkeeping, and export tests. It is not a
substitute for this small piece of facial topology design.

## Stop rule honored

No second r006 geometry implementation was made. The failed source, evidence,
recipe, report, and hashes were saved so this route is never repeated.
