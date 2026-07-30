# S40 r003 — Symmetric All-Quad Body Bootstrap

Status: WIP technical bootstrap  
Human approval: pending  
Rig-ready: no

## Outcome

S40 r003 replaces the mixed-face center strip in r002 with a closed,
bilaterally symmetric all-quad body. The approved H3.1 high source, the
bounded Smart LowPoly scaffold, and the V12 facial research remain locked
inside the canonical Blender assembly.

The successful body route was:

1. preserve the r002 symmetrized bootstrap;
2. apply the source rotation without changing world-space geometry;
3. align the vendor `Y = 0` symmetry plane to Blender's `X = 0` QuadriFlow
   symmetry axis;
4. run symmetric QuadriFlow;
5. remove exact degenerates;
6. transform back to vendor coordinates;
7. snap only the mirrored open-boundary vertices to the symmetry plane;
8. weld coincident boundary pairs;
9. recalculate normals and independently validate the closed shell;
10. normalize the result into the production coordinate contract.

Every material operation above has its own numbered `.blend` in `work/`.

## Technical result

- 10,050 vertices
- 10,048 faces
- 10,048 quads
- 0 triangles or ngons
- 0 boundary or non-manifold edges
- 0 zero-area or zero-length geometry
- 1 connected, positively oriented shell
- exact mirrored vertex, edge, and face topology
- P95 deviation from the preserved r002 body: 0.09599% of character height
- seam median aspect ratio: 1.25
- seam P95 aspect ratio: 2.60

## Explicit blockers

- Two valence-2 vertices and several warped/aspect outliers remain around the
  crotch/tail-base transition.
- The production mouth is not yet welded into the face.
- The clean experimental mouth module is retained separately, while its
  automatic Boolean muzzle boundary is rejected.
- Shoulder, elbow, pelvis, knee, and tail-base flow still require deformation
  evidence.
- G40 remains pending, and no later stage is authorized.

## Mouth decision carried forward

The isolated mouth experiment proved a reusable four-loop lip module,
recessed bag, separate tongue, separate eyes, and neutral/open control. Front
silhouette is promising; the automatic three-quarter boundary protrudes and
is not production quality. The next valid operation is a manually routed,
mirrored quad muzzle patch joined to the module's 64-edge outer loop.

## Approval boundary

This revision is promoted only as the current production-topology bootstrap.
It is not approval of final topology, face, materials, rig, animation, or
runtime appearance.
