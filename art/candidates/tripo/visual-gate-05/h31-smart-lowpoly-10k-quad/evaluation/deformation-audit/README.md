# Smart LowPoly deformation-topology audit

Source: `tripo-out/model.fbx`  
Method: read-only import into Blender 5.1.2; no source edits and no paid API calls.

![Deformation topology board](deformation_topology_board.png)

Legend:

- dark blue: edge belongs only to quads in the selected region;
- orange: edge touches a triangle and therefore interrupts or redirects a quad loop;
- magenta: open boundary edge and genuine mesh defect.

The semantic regions are coordinate-based inspection windows, so their counts
should be used comparatively rather than treated as universal rigging scores.

## Verdict by region

| Region | Measured evidence | Animation verdict |
| --- | --- | --- |
| Face shell | 89.7% quads; 26.0% of vertices touch triangles; 70.4% clean all-quad valence-4 vertices | Static head/frill shape is usable. Local facial deformation still needs purpose-built topology. |
| Mouth | No open oral cavity; 79.4% quads; 41.8% of vertices touch triangles; only 52.5% clean all-quad valence-4; median face aspect ratio 3.18 | Rebuild. The current mouth is a closed crease, not an animatable mouth. |
| Eyes | Each side is 89.6% quads and exactly mirrored, but the eyes are fused into the one connected character shell | Shape keys may support very subtle squinting. Separate eye/lid construction is preferable for gaze and expressive blinking. |
| Shoulders | About 81.6% quads; 35.7–37.0% of vertices touch triangles; only 50.8–51.4% clean all-quad valence-4; p95 face aspect ratio 6.25 | Rebuild the shoulder/armpit deformation bands. |
| Elbow/arm windows | About 80.0% quads; 51.2–51.8% of vertices touch triangles; only about 39.8% clean all-quad valence-4 | Add explicit elbow rings and redirect poles away from the bend. Current flow is unreliable for a pronounced bend. |
| Hips/groin | 22–26 open edges in the local windows; about 81–82% quads; only 49–50% clean all-quad valence-4; p95 face aspect ratio 11.51 and maximum about 21.95 | Highest-priority body rebuild. Close the holes, then rebuild pelvis-to-thigh loops. |
| Knees | 84.2% quads; no local open edges; 34.0% of vertices touch triangles; 51.9% clean all-quad valence-4 | Salvageable only for very subtle motion. Install a clean three-loop knee band for walking/squatting. |
| Tail | Base is 85.5% quads and 62.2% clean regular topology; visible longitudinal and cross-tail rings are coherent | Best deformation region. Keep most of it; locally clean the base, tiny boundary defects, spike junctions and tip. |

## Symmetry

- Mirror plane: `Y = 0.00002016`.
- Median mirrored-vertex error: `0.000000042` model units.
- P95 mirrored-vertex error: `0.000000119` model units.
- 97.39% of vertices match within 0.05% of character height.
- Of those close matches, 97.63% have matching valence and 96.36% have
  matching triangle incidence.

The geometry is therefore strongly bilateral. Manual retopology should be done
on one side with a Mirror modifier rather than repairing both sides separately.

## Shell structure

The entire character is one connected shell: body, eyes, horns, claws and
spikes are all topologically connected. This is not automatically invalid, but:

- horns, claws and plates must receive rigid, carefully isolated weights;
- the fused eyes cannot rotate like eyeballs;
- facial expression work cannot rely on cleanly separated facial parts.

## Minimum manual rebuild before a production rig

1. Repair every open boundary and revalidate manifoldness.
2. Retopologize one mirrored mouth/cheek patch with concentric lip loops, an
   actual mouth opening, inner mouth bag, tongue and jaw deformation support.
3. Decide whether the eyes are separate eyeballs/lids or shape-keyed graphic
   eyes; rebuild accordingly.
4. Retopologize the shoulder/armpit and pelvis/groin junctions with continuous
   circular deformation bands.
5. Add explicit three-loop bend bands at each elbow and knee, keeping triangles
   and high-valence poles outside the compression zones.
6. Preserve most of the tail, cleaning only its base, dorsal-plate junctions,
   tiny open defects and tip.
7. Only after these changes: rig, mirror weights, and run extreme-pose tests
   for arm lift, elbow bend, squat, walk, tail swing, smile and chewing.

The full numerical output is in
[`deformation_topology_audit.json`](deformation_topology_audit.json).
