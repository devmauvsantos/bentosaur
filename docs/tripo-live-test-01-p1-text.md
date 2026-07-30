# Tripo Live Test 01 — Prop-Free P1 Text Character

**Status:** Pipeline proven; character rejected as the canonical Bentosaur  
**Run date:** July 29, 2026  
**Machine-readable run record:** `art/jobs/tripo-live-test-01-p1-text.json`

> **Tripo API credit ledger:** 5,000 starting → **75 consumed
> (USD 0.75)** → **4,925 remaining**.
>
> Tripo calls this usage “credits,” not tokens.

## Outcome

The core 3D hypothesis works.

One prop-free text prompt produced an upright bipedal Triceratops mesh, Tripo
recognized it as a biped, generated a usable skeleton with a three-bone tail,
and delivered one GLB containing front-facing idle and side-walk actions.
Blender imported the raw, rigged, and animated GLBs without errors.

This proves that one 3D character master can be:

- posed at the stall from the front;
- turned to either side for street movement;
- shown from behind;
- animated once and rendered from multiple cameras;
- exported as live 3D or baked into 2D sprite sheets.

The generated identity is not yet Bentosaur. It is a successful plumbing model,
not a production character.

This run intentionally continued through rigging and animation despite failing
the identity gate because its purpose was to validate the complete technical
route. Future production runs do not do this. They stop after visual
bare-geometry review and require explicit approval before rigging or animation.

## Test configuration

| Item | Value |
|---|---|
| Generator | Tripo P1 `P1-20260311` |
| Input | Text only |
| Seed | `28102026` |
| Face limit | `5000` |
| Texture / PBR / UV | Disabled |
| Pose | Neutral upright biped A-pose |
| Character attachments | None |
| Rig | Tripo-native biped |
| Diagnostic actions | `preset:idle`, `preset:walk` |
| Root motion | In place |

The exact positive prompt, 243-character negative prompt, parameters, timestamps,
task IDs, and credit receipts are preserved in the downloaded `task.json`
files. No API credential is stored in the project.

## Cost and timing

| Operation | Credits | Result |
|---|---:|---|
| P1 bare text-to-model | 30 | Success |
| Rig check | 0 | `riggable: true`, `rig_type: biped` |
| Tripo-native biped rig | 25 | Success |
| Idle + walk retarget | 20 | Success |
| **Total** | **75 = USD 0.75** | Complete |

The generation stage completed in roughly thirteen seconds. The account balance
after the run was 4,925 API credits.

Tripo Studio and Tripo API use independent wallets. The Studio subscription and
its credits do not fund CLI/API generation. Studio and API use the same
underlying generation technology; the choice is workflow and billing, not an
expected quality difference.

## Geometry result

Raw mesh:

- one mesh object;
- 2,434 vertices;
- 4,826 triangles;
- no materials;
- no armature;
- no prop, accessory, platform, or environment geometry.

It passes:

- exactly two weight-bearing hind legs;
- two free forearms;
- elevated torso;
- readable Triceratops frill and three horns;
- real tail geometry;
- no fused tray, umbrella, clothing, or scenery;
- under the 5,000-face target.

It fails the canonical identity gate:

- muzzle reads too puppy-like;
- hands are not perfectly symmetrical;
- cream rounded frill-rim knobs are missing;
- cheeks and face do not match the approved pixel identity;
- the text stage invented an orange toy reference instead of the sage/cream/coral
  Bentosaur palette;
- text-only generation had no approved back or side design to preserve.

Do not texture or polish this mesh into the hero. Keep it as the pipeline proof.

## Rig result

The rigged GLB contains:

- one 32-bone armature;
- 32 matching vertex groups on the character mesh;
- four-bone chains for the left and right arms;
- four-bone chains for the left and right legs;
- a multi-bone head chain;
- a three-bone tail chain.

Tripo also emitted one small unbound `Icosphere` helper mesh. It is excluded
from animation-preview framing and must not ship.

This is a strong result for an oversized-head, short-legged, tailed biped. The
tail did not disappear into a generic humanoid skeleton.

## Animation result

The animated GLB contains two named Blender actions:

- `preset:idle`, source range 1–369;
- `preset:walk`, source range 1–57.

Both actions drive the same model and can be rendered from any camera. The
default retargets are diagnostic, not shippable:

- foot grounding needs correction;
- short-leg deformation and stride weight need cleanup;
- the generic idle does not express Bentosaur's personality;
- hand poses and tail timing need authored service-game acting.

The production route is therefore:

1. use Tripo rigging as a fast skeleton and weight seed;
2. repair grounding and weights in Blender;
3. keep or rebuild the useful tail chain;
4. author Bentosaur-specific idle, walk, order, receive, delight, and chomp
   actions in Blender;
5. render those same actions from front, side, and three-quarter cameras.

## Hard asset-separation contract

### The character master owns

- bare anatomy: head, frill, rounded rim knobs, horns, muzzle, cheeks, torso,
  arms, hands, legs, feet, and tail;
- neutral proportions and silhouette;
- base palette material slots;
- armature, weights, corrective shapes, and replaceable face system;
- prop-free body actions and interaction poses;
- stable attachment sockets.

Species-defining horns, frill knobs, cheeks, and tail are anatomy, not
accessories.

### The character master excludes

- umbrella, tray, bento, bowl, cup, utensils, and book;
- apron, hat, bag, glasses, and scarf;
- counters, floors, backgrounds, shadows, weather, and VFX;
- food fused to a hand or mouth;
- one permanently painted expression.

### Required sockets

```text
socket_hand_l
socket_hand_r
socket_tray
socket_mouth_bite
socket_head_hat
socket_back
socket_umbrella
socket_apron_chest
socket_apron_waist_l
socket_apron_waist_r
```

Sockets belong to the character. Attached objects do not.

### Prop and accessory rule

Every prop has its own mesh, materials, version, origin, and declared grip
socket. A tray may expose child food-slot sockets. Rigid accessories attach to
character sockets. Deformable aprons may bind to the compatible armature but
remain separate mesh assets and exports.

Runtime assembly is data, not fused geometry:

```text
character_master_id
+ palette_skin_id
+ accessory_ids[]
+ held_prop_id
+ action_id
```

Boundary test:

> If removing it changes the dinosaur's species identity or bare neutral
> anatomy, it belongs to the character master. If it can be swapped between
> compatible customers, it is a prop or accessory.

## Prompting rules learned

1. Put the desired anatomy in the positive prompt, not only in negatives.
2. State “exactly two weight-bearing hind legs” and “two free forearms used as
   hands.”
3. Repeat “isolated character only,” “empty hands,” and “no held objects.”
4. List common unwanted Bentosaur props explicitly in the negative prompt.
5. Tripo limits `negative_prompt` to 255 characters; keep the complete contract
   in the positive prompt and compress the negative list.
6. Use `texture=false`, `pbr=false`, and `export_uv=false` for the first gate.
   Attractive generated textures can hide weak anatomy.
7. Use a fixed seed and preserve every `task.json`.
8. Do not ask text-to-3D to invent the production identity. Use four approved
   orthographic views.

## Preserved artifacts

```text
art/candidates/tripo/live-test-01-p1-text/
  tripo-out/                         raw P1 GLB and task record
  blender-inspection/               five-view renders, metrics, scratch .blend
  rig-check/                         rig classification task
  rig/                               rigged GLB and 32-bone inspection
  animation/                         idle/walk GLB, Blender inspection, GIFs
```

Primary visual files:

- `blender-inspection/contact-sheet.png`;
- `animation/previews/idle-front/idle-front.gif`;
- `animation/previews/walk-left/walk-left.gif`.

Reusable inspection tools:

- `tools/blender/inspect_tripo_character.py`;
- `tools/blender/render_tripo_animation_preview.py`.

## Decision and next test

Adopt Tripo as a candidate base-mesh and rig accelerator. Do not adopt
text-to-3D as the Bentosaur identity generator.

Before another paid character request:

1. approve or normalize the side silhouette from PixelLab candidate 12;
2. create clean 1024 px front, left, back, and right orthographic views;
3. enforce neutral closed mouth, empty hands, no accessories, and identical
   proportions;
4. run the planned P1 versus H3.1 bare-geometry bake-off;
5. review the five-view, wireframe, metrics, and 64 px visual QA bundle;
6. explicitly approve exactly one candidate for rigging;
7. give Blender authority over palette, face, sockets, weights, animation, and
   final export.

The strongest conclusion from this run is not “Tripo made the final dinosaur.”
It is: **one reusable 3D dinosaur can replace the explosion of independently
generated front, side, back, idle, and walking sprite identities.**
