# Tripo Smart LowPoly Test V1

Status: experiment complete; production pipeline not locked  
Date: 2026-07-29  
User approval status: result awaiting Mau's review

## Question

Can Tripo's post-process Smart LowPoly turn the accepted H3.1 Extreme
high-resolution visual source into a usable production starting mesh without
regenerating or changing the character?

## Controlled test

- Source task: `26811821-3e6d-4b62-a695-679275c04f60`
- Smart LowPoly task: `b14be279-1330-4697-8f06-770de66bf358`
- Operation: `highpoly_to_lowpoly`
- Model version: `P-v2.0-20251225`
- Requested target: 10,000 quad faces
- Quad output: enabled
- Texture bake: enabled
- Paid submissions: exactly one
- Status: success
- Runtime: about 8 minutes 22 seconds
- Cost: 30 Tripo credits
- Balance before: 4,765 available credits
- Balance after: 4,735 available credits

The FBX result is the expected editable output format for the quad option. No
new character prompt or geometry generation was performed.

## Result

| Measurement | H3.1 Extreme source | Smart LowPoly result |
|---|---:|---:|
| Triangles | 1,974,918 | 24,071 |
| Polygon faces | 1,974,918 triangles | 12,996 mixed faces |
| Quad faces | 0 | 11,075 |
| Triangle faces | 1,974,918 | 1,921 |
| Vertices | 1,010,650 after textured GLB import | 12,059 |
| File size | 85,259,072 bytes | 13,284,124 bytes |
| UV layers | 1 | 1 |
| Rig / skin / animation | none | none |

This is an 82.05× triangle reduction, or 98.7812%. The result is 85.22% quads
by polygon count, but it is not literally a 10,000-face all-quad mesh.

The baked result retains:

- 8192 × 8192 base color
- 4096 × 4096 normal
- 4096 × 4096 roughness
- 4096 × 4096 metallic

## What worked

The global character shape survived unusually well. Across 12,059 low-poly
vertices, nearest-surface distance to the high-resolution source was:

- mean: 0.074% of character height
- 95th percentile: 0.182% of character height
- maximum: 0.437% of character height

Front, three-quarter, and profile comparisons preserve the frill, horns,
face volume, torso, limbs, and tail closely enough that the low mesh still
reads immediately as the same H3.1 character.

## What failed

The returned mesh contains 95 open boundary edges in 20 disconnected groups.
The largest defects sit symmetrically beside the belly and under the arms and
are visible in both surfaced and clay renders. Smaller openings appear around
other extremities.

These are not harmless duplicated seams:

- merge-by-distance from `0.0000001` through `0.001` normalized units merged
  zero vertices;
- all 95 open edges remained;
- a destructive `0.005` merge still left 68 open edges while collapsing
  3,550 vertices.

The bake also projects visible gray/green artifacts around the missing belly
patches. The result has no production mouth topology, expression system,
deformation test, rig, skin, or animation.

## Current verdict

Smart LowPoly is **promising as a first automatic retopology candidate**, not
accepted as the Bentosaur production mesh and not yet a locked pipeline step.

It proved that Tripo can preserve H3.1's silhouette while removing roughly
98.8% of the triangles. It did not prove that Tripo can return a clean,
closed, deformation-ready character. The raw result requires Blender repair,
facial and joint topology review, a proper mouth system, rebaking or texture
repair, rigging, and an animation deformation test.

The next zero-credit experiment, if Mau wants it, is to repair a duplicate of
this FBX in Blender and measure the actual labor required. That repair test—not
the attractive silhouette alone—should determine whether Smart LowPoly earns
a permanent place in the pipeline.

## Evidence

- Controlled comparison:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/evaluation/boards/vg05_result_comparison_labeled.png`
- Open-boundary diagnostic:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/evaluation/boards/vg05_open_boundaries_labeled.png`
- Raw FBX:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/tripo-out/model.fbx`
- Task record:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/tripo-out/task.json`
- Blender metrics:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/evaluation/metrics.json`
- Topology diagnostic:
  `../art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/evaluation/topology-diagnostic/topology_diagnostic.json`
