# Tripo Visual Gate 01 — Complete Character Candidates

**Status:** Target design approved; P1 form provisionally selected; final appearance pending  
**Run date:** July 29, 2026  
**Rigging performed:** No  
**Animation performed:** No  
**Approval owner:** User only  
**Approval recorded:** July 29, 2026

Notion record:

`https://app.notion.com/p/3acbcf1d040381208d5bfefaac50da9d`

## What this gate proves

This test generated two complete, unclothed, prop-free Bentosaur candidates
from the same four-view turnaround. Both include the final visible body,
horns, frill knobs, face, belly, claws, palette, UVs, and packed PBR textures.
They were then imported into isolated Blender evaluation scenes and rendered
from six matching cameras in five diagnostic modes.

In this document, **surfaced** means the character has its visible color and
materials. **Rigged** means it has a skeleton. **Skinned** in the technical 3D
sense means the mesh vertices have been bound and weighted to that skeleton.
This gate is deliberately surfaced but not yet rigged or technically skinned.

The user approved the canonical turnaround as the visual target and accepted
P1's reconstructed 3D form as a viable character option. P1 is the provisional
geometry base because it preserves the target silhouette with fewer triangles
and fewer reported boundary/non-manifold edges than H3.1. The pale automatic
Tripo material is not approved as final appearance. Rigging and animation remain
blocked until a finished material, face, and mouth approval package exists.

## Locked appearance scope

- One permanent sage, cream, coral, and dark-ink character appearance.
- Upright baby Triceratops with two hind legs and two free forearms.
- No clothes and no outfit-changing system.
- No umbrella, tray, bento, bowl, book, scenery, or fused prop.
- No accessories in this gate.
- Neutral face suitable for a later replaceable expression system.
- Cream dorsal and tail knobs are visible in both candidates because they were
  present in the generated turnaround. The user's approval of the turnaround
  includes these details.

## Canonical turnaround

The 2×2 model sheet was generated as a new bitmap using four role-labelled
references:

1. `candidate-12.png` — side silhouette and upright biped proportions only.
2. `bentosaur-front-face-reference.png` — front species identity only.
3. `bentosaur-character-reference.png` — color and emotional identity only.
4. `bentosaur-biped-anatomy-reference.png` — biped body language only.

Generation requirements included:

- front, left, back, and right views in a fixed 2×2 order;
- the same unclothed character in every panel;
- exactly two hind legs, two free forearms, and three horns;
- sage body, cream belly/horns/frill knobs/claws, coral cheeks, and dark face;
- neutral expression, empty hands, no prop, no clothing, no scenery;
- flat gray background and low-shadow orthographic presentation.

Preserved source sheet:

`art/turnarounds/triceratops_master_v1/drafts/model-sheet-v1.png`

Validated 1024×1024 opaque inputs:

- `art/turnarounds/triceratops_master_v1/inputs-v1/bentosaur_front.png`
- `art/turnarounds/triceratops_master_v1/inputs-v1/bentosaur_left.png`
- `art/turnarounds/triceratops_master_v1/inputs-v1/bentosaur_back.png`
- `art/turnarounds/triceratops_master_v1/inputs-v1/bentosaur_right.png`

## Candidate A — `bentosaur_vg01_p1`

- Tripo model: P1 `P1-20260311`
- Tripo task: `4a069b80-c6d5-40b7-84c5-43fa26081d61`
- Cost: 50 Tripo credits = USD 0.50
- Mesh: one object, 5,270 vertices, 5,036 triangles
- UV layers: one
- Texture set: packed 2048×2048 base color, ORM, and OpenGL normal
- Armatures: zero
- Actions: zero
- GLB SHA-256:
  `4c7fabeef6f7efdf7abfe3b896cad837aea5d6267515c842a2c5aea60c8f99e8`

Artifacts:

- Raw GLB:
  `art/candidates/tripo/visual-gate-01/p1/tripo-out/bentosaur-visual-gate-01-p1-4a069b80/model.glb`
- Evaluation scene:
  `art/candidates/tripo/visual-gate-01/p1/evaluation/bentosaur_vg01_p1_evaluation.blend`
- Metrics:
  `art/candidates/tripo/visual-gate-01/p1/evaluation/metrics.json`
- Surfaced board:
  `art/candidates/tripo/visual-gate-01/p1/evaluation/renders/sheets/surfaced_6view.png`
- Clay board:
  `art/candidates/tripo/visual-gate-01/p1/evaluation/renders/sheets/clay_6view.png`
- Toon diagnostic:
  `art/candidates/tripo/visual-gate-01/p1/evaluation/renders/sheets/toon_6view.png`
- Native 64 px diagnostic enlarged 8×:
  `art/candidates/tripo/visual-gate-01/p1/evaluation/renders/sheets/pixel64_8x_6view.png`
- Wireframe board:
  `art/candidates/tripo/visual-gate-01/p1/evaluation/renders/sheets/wireframe_6view.png`

## Candidate B — `bentosaur_vg01_h31`

- Tripo model: H3.1 `v3.1-20260211`
- Tripo task: `21b0ae8e-b5aa-4169-a3ee-c0c015f88bfe`
- Cost: 40 Tripo credits = USD 0.40
- Mesh: one object, 6,609 vertices, 6,278 triangles
- UV layers: one
- Texture set: packed 2048×2048 base color, ORM, and OpenGL normal
- Armatures: zero
- Actions: zero
- GLB SHA-256:
  `6b0db89131ee8c16b0b7b1cca77d1663df767ba15369d5c4ad0f433c516a2194`

Artifacts:

- Raw GLB:
  `art/candidates/tripo/visual-gate-01/h31/tripo-out/bentosaur-visual-gate-01-h31-21b0ae8e/model.glb`
- Evaluation scene:
  `art/candidates/tripo/visual-gate-01/h31/evaluation/bentosaur_vg01_h31_evaluation.blend`
- Metrics:
  `art/candidates/tripo/visual-gate-01/h31/evaluation/metrics.json`
- Surfaced board:
  `art/candidates/tripo/visual-gate-01/h31/evaluation/renders/sheets/surfaced_6view.png`
- Clay board:
  `art/candidates/tripo/visual-gate-01/h31/evaluation/renders/sheets/clay_6view.png`
- Toon diagnostic:
  `art/candidates/tripo/visual-gate-01/h31/evaluation/renders/sheets/toon_6view.png`
- Native 64 px diagnostic enlarged 8×:
  `art/candidates/tripo/visual-gate-01/h31/evaluation/renders/sheets/pixel64_8x_6view.png`
- Wireframe board:
  `art/candidates/tripo/visual-gate-01/h31/evaluation/renders/sheets/wireframe_6view.png`

## Evidence shared by both candidates

Direct comparison boards:

- Surfaced:
  `art/candidates/tripo/visual-gate-01/comparison/surfaced_6view_p1_vs_h31.png`
- Clay:
  `art/candidates/tripo/visual-gate-01/comparison/clay_6view_p1_vs_h31.png`
- Native 64 px toon diagnostic:
  `art/candidates/tripo/visual-gate-01/comparison/pixel64_8x_6view_p1_vs_h31.png`

Visual passes:

- recognizable as the same Bentosaur from front, profile, back, and both
  three-quarter views;
- upright and clearly bipedal;
- complete free arms and planted feet;
- three horns and a broad knobbed frill;
- coherent tail and rear silhouette;
- no clothing, accessories, held objects, background, or stand;
- immediately readable at native 64×64, though the final pixel shader and
  outline system are not represented by this diagnostic.

Production issues discovered:

- both meshes are fully triangulated reconstruction topology rather than
  deformation-friendly animation topology;
- Blender reports 4,494 boundary/non-manifold edges on P1 and 5,684 on H3.1;
- the raw models therefore require weld/cleanup or retopology before production
  rigging and weight painting;
- eyes, cheeks, belly color, and much of the mouth identity are texture-led;
  an expressive game character needs a controlled face layer using separate
  eye/mouth geometry, decals, texture states, or shape keys;
- the diagnostic toon shader exposes coarse normal/shading bands; it is a QA
  view, not the approved final Godot material;
- neither candidate has a skeleton, skin weights, or animation yet.

These findings do not reject the visual design. They define the next
production stage for the selected P1 base.

## Credit ledger

Tripo calls API usage **credits**, not tokens.

- API wallet before this visual gate: 4,925 credits
- P1 candidate: 50 credits
- H3.1 candidate: 40 credits
- This visual gate: 90 credits = USD 0.90
- Verified API wallet after this visual gate: 4,835 credits
- Cumulative from the original 5,000-credit wallet:
  165 consumed = USD 1.65, 4,835 remaining

## Clarified user decision

The Notion block selected by the user is `model-sheet-v1.png`: the canonical
reconstruction was acceptable.

Geometry routing:

```text
USE bentosaur_vg01_p1 AS THE PROVISIONAL LOOKDEV AND RETOPOLOGY BASE
```

P1 is the engineering tie-break, not a different or "barebones" character:

- P1: 5,036 triangles and 4,494 reported boundary/non-manifold edges;
- H3.1: 6,278 triangles and 5,684 reported boundary/non-manifold edges;
- no meaningful geometry advantage for H3.1 was identified by the approval owner.

This is not final-character approval. The original Tripo PBR render is
washed out, the clay render intentionally has no texture, and the toon render
is only a diagnostic material. The final gate must show art-directed materials
and the actual facial system on the P1-derived production mesh.

The controlled next sequence is:

1. preserve the raw P1 GLB and approved target sheet;
2. create the mouth-expression addendum;
3. build the controlled sage/cream/coral/ink material and face lookdev;
4. clean/weld or retopologize the body while preserving the P1 form;
5. rebuild the muzzle with lip loops, a mouth cavity, tongue, and a jaw-ready
   lower muzzle;
6. return closed-neutral, open-delight, three-quarter, mouth-interior, mobile
   scale, and rainy-stall-camera renders to the user;
7. obtain explicit final-appearance and facial-construction approval;
8. only then create the skeleton, bind, weight, and run deformation QA;
9. only after deformation approval create production animations.
