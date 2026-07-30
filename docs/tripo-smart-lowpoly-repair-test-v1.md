# Tripo Smart LowPoly Repair Test V1

Status: experiment complete; pipeline recommendation ready  
Date: 2026-07-29  
Additional Tripo cost: 0 credits  
Tripo balance remains: 4,735 available credits  
User approval: approved for the bounded retopology-scaffold role only

## Decision

Tripo Smart LowPoly earns a **bounded place in the Bentosaur pipeline as an
automatic silhouette and retopology scaffold**.

It does not earn a place as the final production or rig-ready mesh.

The experiment proved that its visible holes and broken bake are repairable
without regenerating the character or spending more credits. It also proved
that closing those holes does not solve the more important animation-topology
work around the mouth, shoulders, elbows, pelvis, and knees.

## Geometry repair

The raw Smart LowPoly FBX contained:

- 12,059 vertices
- 12,996 polygon faces
- 24,071 evaluated triangles
- 11,075 quads
- 1,921 triangle faces
- 95 open boundary edges
- 95 non-manifold edges
- 20 connected boundary groups

The 20 boundary groups actually contained 24 holes. Four groups were
figure-eight networks: two holes touching at one degree-four vertex. This is
why Blender's ordinary global Fill Holes operation did not complete the job.

### Automatic methods tested

| Method | Result |
|---|---|
| Global `holes_fill` | Added 22 faces, left 12 open/non-manifold edges, created 8 zero-area faces |
| Repeated `holes_fill` | No additional progress |
| Global `triangle_fill` | Left 4 open edges, 9 non-manifold edges, and 9 zero-area faces |
| Cycle-aware high-resolution-guided patch | 0 open edges, 0 non-manifold edges, 0 zero-area faces |

### Successful repair method

1. Decompose each boundary graph into individual edge-disjoint cycles,
   splitting figure-eight groups at their degree-four hubs.
2. Detect collapsed triangular cycles using world-space area below `1e-9`.
3. Project only the affected boundary vertices to the accepted H3.1
   high-resolution surface using a nearest-surface BVH query.
4. Create one patch face for each of the 24 cycles.
5. Transfer nearby face data and UV attributes.
6. Recalculate normals over the complete connected shell.
7. Save and reopen the candidate before validating it again.

Ten nearly collapsed cycles required projection. The maximum vertex movement
was `0.001583` normalized units, approximately 0.162% of character height.

The repaired Blender candidate validates as:

- one connected shell
- 12,059 vertices
- 13,020 polygon faces
- 0 open boundary edges
- 0 non-manifold edges
- 0 zero-area faces
- positive signed volume
- one UV layer
- one material

The 24 repair patches contain 18 triangles, three octagons, one heptagon, and
two pentagons. They close the shell but are not acceptable deformation
topology.

## Texture repair

The inherited Tripo UVs and bake remain visibly invalid around the filled
patches. Filling geometry alone replaces the holes with black or gray texture
projections.

A fresh experimental Smart UV unwrap and selected-to-active bake from the H3.1
source was tested:

- map: base colour only
- resolution: 1024 × 1024
- bake time: 4.43 seconds
- cage extrusion: 0.006
- maximum ray distance: 0.025
- margin: 12 pixels

The fresh bake removes the visible black patch artifacts. This proves the
surface can be recovered, but it is only a proof:

- normal, roughness, metallic, and AO still need rebaking;
- the 1K Smart UV layout is not the approved production UV layout;
- final authored material work still belongs in Substance 3D Painter or the
  selected production texturing workflow.

## Animation-topology audit

The repaired shell is not ready to rig.

### Rebuild

- **Mouth and facial mask:** no oral cavity, mouth bag, tongue, jaw, or
  expression-ready lip loops. In the mouth window, 41.8% of vertices touch
  triangle faces and only 52.5% are clean all-quad valence-four vertices.
- **Shoulders and armpits:** roughly 81.6% quads, but only about 51% clean
  regular vertices. Face aspect ratio reaches 14.25.
- **Elbow bend zones:** about 51% of vertices touch triangles and only about
  40% are clean regular vertices.
- **Pelvis and groin:** the highest-priority body rebuild. Only about 49% of
  vertices are clean regular topology; 95th-percentile face aspect ratio is
  11.51 and the maximum is about 21.95.
- **Knees:** no remaining holes, but they need deliberate three-loop bend
  bands before deformation testing.

### Preserve and clean

- **Tail:** the strongest automatic topology region. Its base is 85.5% quads
  and 62.2% clean regular topology. Preserve most of it and clean the base,
  plates, and tip locally.
- **Back of head, frill, and static silhouette areas:** useful as a direct
  scaffold where deformation is minimal.

### Structural considerations

- Geometry symmetry is excellent: 97.35% of vertices mirror within 0.05% of
  character height. Production retopology can therefore be performed on one
  side with a Mirror modifier.
- The entire dinosaur is currently one fused shell, including eyes, horns,
  claws, and frill knobs. Eyes should become separate or purpose-built
  expressive components if gaze, blinking, or face animation is required.

## Production implication

Smart LowPoly saves the work of recreating the overall H3.1 proportions and
non-deforming silhouette from scratch. It does not eliminate the character
retopology phase.

The production route is now:

1. Keep the H3.1 Extreme mesh as the immutable visual source.
2. Use this repaired Smart LowPoly result as a scaffold and comparison mesh.
3. Rebuild the mouth/facial mask, shoulder-arm bands, pelvis-groin junction,
   and knee loops with deliberate quad topology on one side.
4. Mirror and weld the rebuilt side.
5. Preserve and locally clean suitable tail, frill, head-back, and static body
   regions.
6. Separate or rebuild eyes and other components that need independent
   animation.
7. Create production UVs.
8. Bake full PBR maps from H3.1.
9. Author final materials.
10. Rig, weight, and run expression/walk/chew deformation gates.

The user approved this bounded scaffold role on July 29, 2026 and authorized
the S40 production-topology stage. That approval does not authorize rigging the
Smart LowPoly mesh itself.

This is materially less work than using the two-million-triangle source
directly, but it remains a real manual character-production phase.

## Evidence

- Repair progression:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/boards/repair_rebake_progression.png`
- Raw versus repaired clay:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/boards/repair_geometry_raw_vs_closed.png`
- Texture limitation:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/boards/repair_surface_raw_vs_closed.png`
- Animation-topology board:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/evaluation/deformation-audit/deformation_topology_board.png`
- Closed experimental Blender candidate:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/subagent-cycle-audit/cycle_patch_candidate.blend`
- Cycle repair validation:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/subagent-cycle-audit/cycle_patch_report.json`
- Rebaked visual proof:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/rebake-proof/repaired_rebaked.glb`
- Rebake report:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/rebake-proof/rebake_report.json`
- Native repaired-mesh deformation audit:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/deformation-audit-native/deformation_topology_audit.json`
