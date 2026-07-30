# Bentosaur Facial Animation Options — r003 Static Mouth Gate

Status: **static Blender visual gate failed; stop rule reached; all attempts
frozen; not production approved**.

## Goal

Replace r002's floating dark aperture with the soft, rounded open mouth shown
in the locked 3D reference:

- a flush skin transition;
- a real opening instead of a face sticker;
- a recessed dark cavity;
- a coral tongue contained inside;
- no cyan/body-colored leak;
- no visible seam in front, three-quarter, or profile view.

This revision intentionally stops before new mouth morphs, jaw weights, tongue
weights, or Godot integration. Mau owns visual approval.

## Attempt 01 — best result, still not approved

`attempts/a01-wide-window/`

The first static window removes the old cyan lower loop, puts the tongue inside
the cavity, and gives the mouth real depth. It is the closest result in this
revision.

It still fails because the skin-colored transition's outer seam is visible,
especially at three-quarter view. That seam would move and light differently
from the face, so this cannot be promoted to an animation base.

## Attempt 02 — rejected localized adjustment

`attempts/a02-narrow-window-normal-transfer/`

The only permitted correction narrowed the window and transferred body
normals to the transition. It made the boundary more obvious and introduced a
striped ring. The second result is worse and is rejected.

## Stop decision

There will be no third procedural window/offset/normal tweak. Both attempts
show that:

- the cavity and contained-tongue direction is viable;
- the remaining blocker is the body-to-mouth seam;
- anti-aliasing cannot repair that geometry;
- Substance Painter cannot weld or retopologize the seam.

The next choice must be deliberate:

1. **Manual localized Blender retopology/welding** — recommended if the hero
   must have a geometric cavity and tongue. Weld a small quad mouth module
   into the body, preserve the outer facial surface, then author morphs and
   weights.
2. **2D/atlas or SDF facial surface** — recommended for the lowest-risk indie
   pipeline. Keep the reusable 3D character and animate smooth mouth/eye
   graphics on a curved facial surface; add shallow cavity geometry only for
   the rare eating close-up if needed.

Do not add morphs or import r003 into the Godot character lab until Mau chooses
one of those routes.

## Evidence

- Reference versus best attempt:
  `evidence/reference_vs_a01_front.png`
- Attempt 01 front / three-quarter / profile:
  `evidence/a01_static_mouth_angles.png`
- Attempt 02 front / three-quarter / profile:
  `evidence/a02_static_mouth_angles.png`
- Two-row comparison, attempt 01 above attempt 02:
  `evidence/a01_vs_a02_static_gate.png`

Each attempt preserves:

- the exact build recipe used;
- numbered Blender checkpoints;
- canonical editable source;
- static GLB;
- Blender GLB round-trip file;
- renders and a machine-readable QA report.

## Cost

No paid API or Tripo operation was used. Tripo credits spent: `0`; recorded
balance: `4,695`.
