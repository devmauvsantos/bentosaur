# Bentosaur Facial Surface Decision V1

**Document state:** superseded on 2026-07-30 by
[Faceit and AI Facial-Animation Pipeline V1](facial-animation-faceit-ai-pipeline-v1.md).
This file remains as the historical rationale for r003 and r004.

**Current decision:** continue with a physical 3D mouth through one bounded
localized Blender retopology revision snapped directly to the original Tripo
open-mouth geometry. Keep a 2D atlas/SDF face as the fallback, not as the
current direction.

## Why the 3D route remains viable

The r003 first attempt solved the important depth problems:

- the mouth is now a real opening rather than a floating black sticker;
- the tongue sits inside a recessed cavity;
- the old cyan lower loop is gone;
- the silhouette is close to the locked delighted-open reference.

Its failure is localized to the skin-colored transition ring. The ring is a
separate surface, so its normals and outer boundary catch light independently
from the muzzle. More offset, width, or normal-transfer tweaks will not make it
truly continuous.

## Source correction

The smooth delighted-open Tripo mouth was never part of the S20 → S30 → S40
topology lineage. It remained safe as a visual reference at:

`art/candidates/tripo/visual-gate-06/h31-detailed-open-mouth/tripo-out/model.glb`

The r001 source probe correctly recommended localized facial retopology against
that model. The subsequent r001 build did not import it; it generated a new
aperture from hard-coded Bézier curves. r002 inherited that proxy and r003
derived its window from the same curve data. The fidelity loss therefore
happened when the source-guided retopology recommendation was replaced by
procedural approximation.

The Tripo model is 960,234 vertices / 1,920,464 triangles and is one connected
watertight shell. Its tongue, cavity, lips, eyes, and body are fused, so it
cannot be pasted into the mobile mesh or paired directly with the independently
generated neutral source as a shape key. It remains the exact visual surface
authority.

## Next bounded revision

Create a new immutable revision from the S40 r003 body and:

1. keep every parent and r003 experiment file unchanged;
2. import the Tripo open source into a locked reference collection using the
   established production transform;
3. remove only a broader existing-loop facial region from the editable body;
4. retopologize inward from that boundary, snapping the aperture, muzzle
   transition, and cavity to the Tripo surface;
5. rebuild the fused visible tongue as a separate closed low-poly mesh;
6. weld the new facial topology to the body—no separate skin ring;
7. render front, three-quarter, profile, wireframe, source overlay, and
   gameplay-camera checkpoints before any animation;
8. stop after one implementation and at most one manual projection/loop
   correction.

## r004 source-transfer checkpoint

r004 verified the immutable VG06 hash, applied the exact shared production
transform, preserved the unchanged S40 body, and extracted an inspection-only
83,622-vertex Tripo mouth region. No production topology was edited.

The absolute-depth mask was rejected because it selected the lower muzzle. The
one permitted correction used the preserved neutral/open depth delta inside
the measured mouth envelope. It isolated one connected recessed-cavity
component, but its lower edge is the visible tongue occlusion—not a complete
lip contour. Automatically converting it to an edge loop would invent the
hidden lower lip.

The automated transfer therefore stopped at checkpoint 20. This does not
invalidate the Tripo mouth as the correct target. It establishes that the next
step is a deliberate manual Blender retopology session using the aligned VG06
surface, with the occluded lower loop treated as an explicit artist decision.
No further automatic mouth approximation is authorized.

Durable checkpoint:

`art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r004/work/20_source_mouth_region_extraction.blend`

Acceptance requires:

- no visible body-to-mouth seam;
- the Tripo aperture silhouette and soft corners, without reinterpretation;
- no cyan leak, central notch, or striped ring;
- no floating sticker in profile;
- cavity depth and tongue reveal matching the Tripo source;
- no visible damage to the nose, cheeks, muzzle, or body silhouette.

## Fallback if the localized revision fails

Use a reusable 3D character with a curved facial surface carrying a 2D atlas or
signed-distance-field mouth and eyes. That route retains 3D posing, lighting,
camera movement, accessories, and body animation while making expressions
smooth and inexpensive on mobile. A shallow hidden cavity can still appear for
rare eating close-ups.

## Cost and ownership

This work uses local Blender and Godot only. Tripo credits spent: `0`; recorded
balance: `4,695`. Mau owns every visual approval decision.
