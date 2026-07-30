# Bentosaur Facial Animation Options — r001

Status: verified mobile control/export proof; **not production facial
topology and not a visual-appearance approval candidate**.

## Result

This revision proves that one reusable 3D Bentosaur can support:

- a closed neutral mouth;
- a continuous delighted-open morph;
- a jaw bone layered with the mouth corrective;
- a separate tongue controlled by a tongue bone;
- chew compression;
- independent left and right blinks;
- a shared happy-eye expression.

The Blender GLB round trip retained the required shape keys and skeleton. The
proof is approximately 21.3K triangles, including the existing S40 r003 body,
and the exported GLB is about 438 KB.

The recommended production method is the **hybrid**:

```text
jaw bone
+ delighted-open lip/corner corrective
+ separate tongue bone
+ small eye morph meshes
```

Bone-only opening cannot preserve the joyful mouth silhouette. A full
morph-only opening can preserve it, but the hybrid gives the jaw a physical
arc while the corrective protects the lifted corners, cheek read, and tongue
reveal.

## Visual checkpoint

`evidence/facial_states_contact_sheet.png` contains the fixed-camera neutral,
partial, open, blink, happy, and chew states. Mau retains visual approval.

## Source preservation

- The S40 r003 source remains unchanged.
- `work/00` through `work/50` are numbered rollback checkpoints.
- `source/bentosaur_hero_facial_animation_options_r001.blend` is the canonical
  editable proof.
- `recipes/` contains the exact deterministic build and contact-sheet scripts.
- `qa/source-probe/` preserves the open/closed source comparison, numeric
  depth data, locked Blender overlay, and hashes.
- `exports/` contains the tested engine-boundary GLB.

## Honest limit

The proof uses a conforming layered facial aperture over the unchanged
scaffold. It proves controls, export, naming, topology budget, and reuse. It
does **not** yet provide the final welded lip loops, cut mouth aperture,
recessed cavity, production jaw volume, final skin weights, UVs, textures, or
LODs.

The next production art step is a small authored facial mask/cavity using the
open Tripo source as the shape target and the closed source as neutral—not a
full-body retopology restart.

## Reproduce

From the repository root:

```sh
EXPERIMENT=art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r001

/Applications/Blender.app/Contents/MacOS/Blender \
  --background \
  art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/bentosaur_hero_s40_production_topology_r003.blend \
  --python "$EXPERIMENT/recipes/build_facial_rig_proof.py" -- \
  --output "$EXPERIMENT" \
  --resolution 640

python3 "$EXPERIMENT/recipes/make_contact_sheet.py" \
  --root "$EXPERIMENT"
```

This run used no paid API calls. Tripo credits spent: `0`; recorded account
balance remains `4,695`.
