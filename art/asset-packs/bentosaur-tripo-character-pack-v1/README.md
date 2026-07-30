# Bentosaur Tripo Character Pack v1

A concise, browseable handoff pack containing the strongest Tripo image inputs
and GLBs for the Bentosaur hero's closed and delighted-open mouth states.

This pack is a curated copy. The historical files under `art/turnarounds/`,
`art/candidates/`, and `art/characters/` remain the immutable sources of truth.

## Start here

| Need | Open |
| --- | --- |
| See the closed input set | `01_closed-mouth/03_previews/bentosaur_closed-mouth_v1_multiview-contact-sheet.png` |
| See the open input set | `02_open-mouth/03_previews/bentosaur_open-mouth-delighted_v1_multiview-contact-sheet.png` |
| Latest closed model with materials | `01_closed-mouth/02_models/bentosaur_closed-mouth_v2_h31-extreme-textured.glb` |
| Best raw closed geometry | `01_closed-mouth/02_models/bentosaur_closed-mouth_v1_h31-detailed_geometry.glb` |
| Best raw open-mouth geometry | `02_open-mouth/02_models/bentosaur_open-mouth-delighted_v1_h31-detailed_geometry.glb` |
| Inspect the expression difference | `03_shared-reference/bentosaur_closed-vs-open_depth-comparison_v1.png` |

## Tripo multiview upload

Upload the four individual PNGs from `01_multiview-inputs/` in this exact
numbered order:

1. front
2. left
3. back
4. right

Do not upload the contact sheet. It is only a human preview.

## Version labels

- **Closed v1:** H3.1 Detailed raw geometry. No UVs, material, texture, rig,
  shape keys, or animation.
- **Closed v2:** the latest complete Tripo-surfaced closed model. It contains
  the same approved closed surface plus UVs, an 8K base color, and PBR maps.
- **Open v1:** H3.1 Detailed raw open-mouth geometry. No surfaced open-mouth
  Tripo model currently exists.

## Important limitations

- The closed and open GLBs were generated independently. Their topology and
  vertex order differ, so they cannot be used directly as two shape keys.
- All three GLBs are high-resolution visual sources, not mobile runtime
  meshes. Retopology, rigging, deformation work, and runtime optimization
  remain separate production stages.
- The open model's tongue, mouth cavity, eyes, horns, and body are fused into
  one watertight shell.
- The closed v2 model is the latest **surfaced** source, not a claim that the
  model is production-ready.

## What was intentionally excluded

To keep this folder concise, it omits Blender workbenches, low-poly repair
experiments, rejected facial-transfer attempts, old Visual Gate candidates,
and duplicate canonical copies. See `manifest.json` for exact provenance and
model hashes.

