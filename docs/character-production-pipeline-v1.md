# Bentosaur Character Production Pipeline V1

Status: active production pipeline  
Pipeline owner: Mau  
Authoritative DCC: Blender  
Runtime engine: Godot  
Current character: `bentosaur-hero/char-v001`  
Current stage: S40 Production Topology, revision r003  

## Outcome

This pipeline turns one approved character design into:

- a clean, animation-ready 3D character;
- a reusable family skeleton and action vocabulary;
- complete native source files for every stage;
- deterministic GLB exports for Godot;
- visual and machine-readable approval evidence;
- a repeatable starting point for future Bentosaur characters.

The Blender `.blend` at each stage is the editable source of truth. GLB, FBX,
PNG, texture maps, previews, and Godot imports are derivatives.

## Production tree

```text
art/characters/
  _pipeline/
    v1/
      schemas/
      policies/

  bentosaur-hero/
    character.json
    char-v001/
      pipeline.json
      pipeline-validation.json
      stages/
        s10-reference-lock/
        s20-high-visual-source/
        s30-retopo-scaffold/
        s40-production-topology/
        s50-uv-and-bake/
        s60-final-lookdev/
        s70-rig-and-skin/
        s80-animation-library/
        s90-godot-runtime/
      gates/
```

Every stage revision uses the following shape:

```text
s40-production-topology/
  r002/
    manifest.json
    source/
      bentosaur_hero_s40_production_topology_r002.blend
    work/
      00_input_snapshot.blend
      10_operation.blend
      20_next_operation.blend
    recipes/
      exact_versioned_scripts
      exact_reproduction_instructions
    evidence/
      comparison boards
      approval renders
    qa/
      reports
      diagnostic scenes
      diagnostic renders
```

## Non-destructive source rules

1. Historical `art/candidates/` files are immutable evidence. They are never
   moved, renamed, or overwritten.
2. Every production stage from S20 through S90 has exactly one canonical
   editable `.blend` per revision.
3. Every meaningful destructive or topology-changing operation produces its
   own numbered `.blend` checkpoint.
4. A frozen revision is never edited. Continuing work creates `r002`, `r003`,
   and so on.
5. Never use `final`, `latest`, `new`, or `approved` in filenames.
   `pipeline.json` is the only active-revision pointer.
6. Every input, source, recipe, report, and frozen output records:
   repository-relative path, byte size, and SHA-256.
7. Blender resources are packed at a milestone, or every external dependency
   is enumerated and hashed.
8. No vendor export becomes lineage authority.
9. Human visual and performance approval is separate from automated QA.
10. API credentials never enter `.blend` text blocks, manifests, scripts,
    renders, logs, or the repository.

The complete machine-readable policy is:

```text
art/characters/_pipeline/v1/policies/source-preservation-policy.json
```

Binary storage and restore rules are documented in:

```text
docs/character-binary-storage-policy-v1.md
```

## Mandatory checkpoint protocol

“Save every step” means every meaningful rollback point—not every viewport
movement. A meaningful step is any operation that changes topology, UVs,
materials, rig structure, weights, corrective shapes, animation timing, or
the runtime export contract.

For each meaningful operation:

1. Open the previous numbered checkpoint; never overwrite it.
2. Save the new state as `NN_descriptive_operation.blend` before starting the
   next operation.
3. Pack external Blender resources, or write and hash an explicit dependency
   inventory beside the checkpoint.
4. Register the checkpoint in the active WIP manifest with its byte size,
   SHA-256, role, and parent artifact.
5. Save the exact script, command, settings, or short reproduction note that
   produced it.
6. Run the smallest relevant technical and visual check.
7. Preserve rejected branches under the experiment inventory; only the
   successful chain is copied into the next production revision.
8. Reopen and inspect the intended canonical `.blend` before freezing a
   revision.

Every stage starts with `00_input_snapshot.blend` copied from the approved
parent. Recommended stage checkpoints are:

| Stage | Required native checkpoints |
|---|---|
| S20 | raw vendor import; orientation/material repair; immutable high-source master |
| S30 | high-source snapshot; generated scaffold; manifold repair; bounded scaffold master |
| S40 | parent snapshot; body bootstrap; each joint-flow repair; mouth aperture; lip loops and cavity; tongue and eyes; each facial control pass; deformation candidate |
| S50 | approved S40 snapshot; seam pass; unwrap pass; bake cage; each accepted bake set; UV/bake master |
| S60 | S50 snapshot; material-authoring pass; each lighting review pass; final-lookdev master; `.spp` milestones when Painter is used |
| S70 | S60 snapshot; skeleton; control rig; each weight region; each corrective-shape group; socket pass; deformation candidate |
| S80 | approved rig snapshot; blocking and polish checkpoints for every required clip; animation-library master |
| S90 | approved animation snapshot; export-prep master; deterministic GLB; Godot wrapper scene; validation and device-gate captures |

The canonical stage source is a reviewed copy of the latest successful
checkpoint. Failed work never silently becomes lineage, and a downstream
derivative never replaces its native Blender source.

## Stage and gate map

| Stage | Editable source | Purpose | Exit gate |
|---|---|---|---|
| S10 Reference Lock | design files | Freeze turnaround, anatomy, palette, and gameplay identity | G10 Identity Lock |
| S20 High Visual Source | `.blend` | Preserve the approved H3.1 appearance and silhouette source | G20 High Visual Source |
| S30 Retopo Scaffold | `.blend` | Preserve the repaired Smart LowPoly as a bounded projection/scaffold source | G30 Scaffold Acceptance |
| S40 Production Topology | `.blend` | Author body topology, components, eyes, oral cavity, tongue, expression loops, and deformation flow | G40 Deformation Topology |
| S50 UV and Bake | `.blend` | Create production UVs and bake full PBR maps from H3.1 | G50 Bake Integrity |
| S60 Final Lookdev | `.blend`, optionally `.spp` | Author final materials and approve actual in-game appearance | G60 Final Appearance |
| S70 Rig and Skin | `.blend` | Build the export skeleton, controls, weights, shape keys, and sockets | G70 Rig Deformation |
| S80 Animation Library | `.blend` | Author the reusable cute acting and locomotion set | G80 Animation Performance |
| S90 Godot Runtime | `.blend`, `.glb`, `.tscn` | Deterministic export, import contract, stress scene, and device gate | G90 Mobile Runtime |

Stages describe work. Gates authorize movement. A technical pass never grants a
human visual approval.

## Coordinate contract

### Preserved vendor source

- front: Blender `+X`;
- character left: Blender `+Y`;
- up: Blender `+Z`;
- original vendor origin and scale are preserved in S20 and S30.

### Production contract from S40 onward

- front: Blender `-Y`;
- character left: Blender `+X`;
- up: Blender `+Z`;
- symmetry plane: local `X = 0`;
- units: metric, one Blender unit equals one meter;
- character height: approximately one meter;
- feet: `Z = 0`;
- origin: midway between planted feet;
- mesh and armature transforms: identity;
- no negative or non-uniform scale.

The coordinate conversion happens exactly once, before skinning. Blender GLB
export uses `export_yup=true`.

## S10 — Reference lock

Required:

- front, left, back, and right orthographic turnaround;
- character anatomy contract;
- palette contract;
- approved gameplay identity image;
- no props or clothing fused to the character.

This stage is frozen for `bentosaur-hero/char-v001`.

## S20 — High visual source

Authority:

```text
art/characters/bentosaur-hero/char-v001/stages/
  s20-high-visual-source/r001/source/
```

The H3.1 Extreme model is the immutable visual and silhouette source:

- 1,010,650 vertices;
- 1,974,918 triangles;
- 8K base colour;
- source SHA-256
  `40de6b43b0dc0313e084005b711cb549dfe6dfceeebe45c6275761c99b96dc79`.

It is not edited or rigged. Later topology is projected and baked from it.

## S30 — Retopology scaffold

Authority:

```text
art/characters/bentosaur-hero/char-v001/stages/
  s30-retopo-scaffold/r001/source/
```

The repaired Smart LowPoly is approved only as a bounded scaffold:

- 12,059 vertices;
- 13,020 faces;
- 24,118 evaluated triangles;
- zero open, non-manifold, or zero-area faces;
- one connected shell.

It preserves H3.1 proportions well, but it is not deformation-ready and is
never rigged as the hero.

## S40 — Production topology

### Current revision

```text
art/characters/bentosaur-hero/char-v001/stages/
  s40-production-topology/r003/
```

S40 r001 assembled and normalized:

- locked H3.1 high source;
- locked repaired scaffold;
- editable topology work mesh;
- separate V12 face research pieces:
  eyes, cheeks, mouth bag, lip ring, tongue, aperture cutter;
- production coordinate contract.

S40 r002 improved the joint grid but retained 132 triangles and 120 pentagons
along its reconstructed symmetry strip. It is now frozen as the direct parent
of r003.

S40 r003 replaces that mixed-face strip through the following preserved
sequence:

1. preserve the r002 symmetrized bootstrap;
2. apply its source rotation without changing world-space geometry;
3. rotate the vendor `Y = 0` bilateral plane onto Blender QuadriFlow's
   `X = 0` symmetry axis;
4. explicitly enable Mesh X symmetry and run QuadriFlow;
5. remove exact degenerates and return to vendor coordinates;
6. snap only the mirrored open-boundary vertices onto the symmetry plane;
7. weld coincident boundary pairs and recalculate normals;
8. independently validate shell integrity and quad quality;
9. normalize into the production coordinate system;
10. correct the editable body to exact local `X = 0` symmetry and `Z = 0`
    floor contact.

Current measured result:

- 10,050 vertices;
- 10,048 faces;
- 10,048 quads;
- zero triangles or ngons;
- zero boundary, non-manifold, zero-area, zero-length, or loose geometry;
- one connected, positively oriented shell;
- exact bilateral vertex, edge, and face topology;
- P95 surface deviation: 0.09599% of character height;
- seam median aspect ratio: 1.25;
- seam P95 aspect ratio: 2.60;
- production body bounds centered exactly on local `X = 0`;
- production body minimum `Z = 0`.

The body bootstrap passes its isolated technical gate. It remains WIP because
two valence-2 vertices and several warped/aspect outliers remain around the
crotch/tail-base transition, the target smile is not yet integrated, and the
actual r003 probe fails at the shoulder/armpit and hip/groin/knee transitions.

The first welded-mouth experiment is retained only as a topology proof. Its
oval/circular aperture and visible lip ring do not match the approved
Bentosaur design, and Mau explicitly rejected it. It is not part of the
canonical r003 source.

The replacement is governed by:

```text
art/characters/bentosaur-hero/char-v001/design-contracts/
  mouth-expression-v1.json
```

Its primary visual authority is
`art/turnarounds/triceratops_master_v1/drafts/mouth-expression-addendum-v1.png`.

The bounded r003 deformation probe used the exact canonical source hash and
confirmed the production coordinate contract:

- neutral: pass;
- reach/tray hold: fail at shoulder/armpit;
- squat: fail at hip/groin plus local knee/leg outliers;
- extreme walk: fail at shoulder and hip/knee;
- tail bend: pass.

Sixteen diagnostic `.blend` checkpoints are preserved in the hashed Tier C
archive. Compact reports, exact recipes, hashes, and visual boards are
registered under `r003/qa/deformation-probe/`.

### Required authored work

1. Replace the rejected oval mouth with a shallow curved neutral smile and a
   wider-than-tall, lifted-corner delighted opening.
2. Integrate the recessed bag without exposing a circular outer lip ring.
3. Split open-mouth motion across jaw rotation, lip corners, and corrective
   shapes instead of one stretched radial morph.
4. Keep the tongue separate.
5. Keep eyes as separate expressive objects.
6. Repair the crotch/tail-base valence and quad-quality outliers.
7. Author localized shoulder/armpit and pelvis/groin/knee deformation flow;
   retain the passing tail.
8. Keep poles outside primary bend regions.
9. Preserve the accepted H3.1 silhouette.

### Required facial states

- neutral closed;
- delighted open;
- smile;
- mouth O;
- chew compression;
- cheek puff;
- blink left;
- blink right;
- squint left;
- squint right;
- corrective jaw open.

The delighted expression combines jaw motion, smile, squint, and the corrective
open-mouth shape. Teeth are not required.

### G40 acceptance

Geometry:

- zero boundary and non-manifold edges;
- zero degenerate or loose geometry;
- no centerline ngons;
- all primary deformation bands are quads;
- one intentional body shell plus explicitly named face/mouth components;
- LOD0 at or below approximately 25,000 rendered triangles;
- exact bilateral topology where intended;
- approved silhouette versus H3.1.

Deformation:

- no shoulder collapse during arm lift or tray hold;
- no elbow collapse during reach;
- no pelvis/groin collapse during squat or step;
- no knee collapse at walk contact and passing poses;
- no tail-base pinch through four-direction bends;
- no mouth tear, leak, or cheek collapse through smile and chew;
- clean blink without doubled eye surfaces.

No work advances to UVs until G40 passes.

## S50 — Production UV and full bake

The S50 source begins by copying the approved S40 source. It never edits S40.

Required:

- final seam decisions;
- mirrored overlap only where explicitly safe;
- no unintended overlap;
- face, mouth, hands, and torso receive priority texel density;
- sufficient 2K padding;
- full high-to-low bake from immutable H3.1.

Maps:

- base colour, sRGB;
- normal, linear;
- roughness, linear;
- metallic, linear;
- ambient occlusion, linear;
- semantic/material masks;
- packed ORM for runtime.

The earlier 1K base-colour rebake is evidence only.

## S60 — Final lookdev

Use Blender and, if it improves authorship, Substance 3D Painter.

Native files preserved:

- S60 `.blend`;
- Painter `.spp`, when used;
- exported texture maps;
- material parameter report.

Runtime material budget:

- opaque materials first;
- no alpha unless a reviewed need survives;
- maximum three surfaces for LOD0;
- no procedural Blender-only shader nodes in the runtime export;
- backface culling enabled;
- 2K hero textures initially.

Approval uses actual final materials in neutral, warm-stall, rainy-street, and
gameplay-distance lighting.

## S70 — Rig and skin

Blender owns:

- control rig;
- deformation skeleton;
- constraints;
- weights;
- corrective shapes;
- sockets;
- deformation tests.

Only clean deformation bones and runtime sockets export.

Minimal exported hierarchy:

```text
root
└── pelvis
    ├── spine_01
    │   └── chest
    │       ├── neck
    │       │   └── head
    │       │       ├── jaw
    │       │       │   └── tongue_01
    │       │       ├── eye_l
    │       │       └── eye_r
    │       ├── clavicle_l → upper_arm_l → forearm_l → hand_l
    │       └── clavicle_r → upper_arm_r → forearm_r → hand_r
    ├── thigh_l → shin_l → foot_l → toe_l
    ├── thigh_r → shin_r → foot_r → toe_r
    └── tail_01 → tail_02 → tail_03 → tail_04 → tail_05
```

Runtime sockets:

- `socket_hand_l`;
- `socket_hand_r`;
- `socket_tray`;
- `socket_mouth_bite`.

Skinning requirements:

- one exported armature;
- zero unweighted vertices;
- no vertex above four influences;
- normalized weights;
- no control bones exported;
- no accidental helpers;
- expected bones and sockets exactly match the manifest.

## S80 — Animation library

Author at 24 FPS. Godot renders at its runtime frame rate.

First reusable set:

| Action | Target | Type |
|---|---:|---|
| `stall_idle-loop` | 3.5–5.0 s | loop |
| `street_walk-loop` | 0.8–1.2 s | in-place loop |
| `wait-loop` | 2.5–4.0 s | loop variation |
| `request` | 0.8–1.5 s | one-shot |
| `receive` | 1.0–1.8 s | one-shot |
| `eat-loop` | 0.8–1.4 s | loop |
| `delight` | 1.3–2.2 s | one-shot |
| `disappointed` | 1.2–2.2 s | one-shot |
| `face_blink` | 0.12–0.25 s | additive one-shot |

Blender owns poses, contacts, deformation, and timing. Godot owns state
transitions, random offsets, gaze/blink scheduling, sound, particles, haptics,
and prop attachment.

Animation acceptance:

- planted-foot drift below 5 mm;
- ground penetration below 3 mm;
- loop root drift below 5 mm;
- loop boundary rotation difference below 0.5 degrees;
- no horn/frill/body or tongue/lip collision longer than two frames;
- tray socket drift below 5 mm through hold intervals;
- all expressions remain readable at gameplay distance.

## S90 — Godot runtime

Godot project work has not started. The repository currently has no
`project.godot`, `.tscn`, `.gd`, or `.tres`.

Before producing import metadata, resolve the engine pin:

- installed: Godot `4.7.stable.official.5b4e0cb0f`;
- recorded lock: Godot `4.7.1`.

Planned runtime tree:

```text
game/
  project.godot
  assets/characters/bentosaur/v001/
    bentosaur_runtime_v001.glb
    export_manifest.json
  scenes/characters/bentosaur_character.tscn
  scenes/validation/character_validation.tscn
  scripts/characters/bentosaur_character.gd
  tests/character_contract_test.gd
```

The imported GLB remains replaceable. The `.tscn` wrapper is Godot-owned and
survives reimport.

Validation scene capabilities:

- front, side, back, and three-quarter camera presets;
- clip selection, pause, slow motion, and frame stepping;
- facial-shape controls;
- tray, bento, and umbrella socket tests;
- neutral, warm-stall, and rainy-street lighting;
- one-character close-up and ten-character stress mode;
- screenshots at the real portrait gameplay crop.

Device gate:

- representative phone: 60 FPS / 16.7 ms with ten dinosaurs and weather;
- floor device: stable 30 FPS / 33.3 ms;
- ten-minute thermal run after functional acceptance.

## Deterministic GLB export contract

Pinned settings:

```python
export_format="GLB"
use_active_collection=True
export_yup=True
export_apply=False
export_texcoords=True
export_normals=True
export_tangents=True
export_materials="EXPORT"
export_cameras=False
export_lights=False
export_extras=True
export_animations=True
export_animation_mode="ACTIONS"
export_nla_strips=True
export_force_sampling=True
export_frame_step=1
export_optimize_animation_size=True
export_def_bones=True
export_leaf_bone=False
export_skins=True
export_influence_nb=4
export_all_influences=False
export_morph=True
export_morph_normal=True
export_morph_tangent=False
export_morph_animation=True
export_current_frame=False
export_rest_position_armature=True
export_draco_mesh_compression_enable=False
export_use_gltfpack=False
```

Only `EXPORT_CHARACTER` ships.

## Reusing the pipeline for another character

Start from the machine-readable upright-biped template:

```text
art/characters/_pipeline/v1/templates/
  upright-biped-character-template.json
```

1. Create a new stable character ID and `char-v001`.
2. Freeze its design, turnaround, anatomy, and palette under S10.
3. Generate or model the high visual source and freeze its vendor request,
   receipt, editable Blender import, cost, and hash under S20.
4. Generate a scaffold only if it saves work; freeze it under S30 and define
   its exact approved scope.
5. Copy the standard skeleton family, action names, socket names, coordinate
   contract, validators, render recipes, and manifests.
6. Retopologize the new anatomy under S40; never assume one character's
   weights or facial topology can be copied unchanged.
7. Bake, surface, rig, animate, export, and validate through the same gates.
8. Preserve each native stage source even when downstream derivatives exist.

Reusable across the cast:

- directory and manifest schema;
- source-preservation policy;
- coordinate contract;
- exported skeleton hierarchy;
- action names and timing language;
- runtime socket names;
- Blender export recipe;
- Godot validation scene and contract tests;
- QA thresholds and approval boards.

Character-specific:

- visual source;
- topology;
- facial proportions;
- UVs and bake;
- materials;
- weight painting;
- corrective shapes;
- selected animation polish.

## Revision automation

The reusable filesystem and manifest harness is:

```text
tools/character_pipeline/character_pipeline.mjs
```

It creates new versioned revision directories without overwriting an existing
revision, generates the required manifest skeleton and hashed parent lineage,
registers saved sources and checkpoints, checks or refreshes artifact hashes,
protects frozen and superseded manifests from tool-driven edits, and prints a
concise pipeline status table.

Preview the next S40 revision without changing any file:

```sh
node tools/character_pipeline/character_pipeline.mjs create-revision \
  --root /Users/mauvsantos/Workspace/games/Bentosaur \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json \
  --stage S40 \
  --activate \
  --supersede-active \
  --dry-run
```

The exact operational commands, safety behavior, artifact registration
examples, and `.tmp` test command are documented in:

```text
tools/character_pipeline/README.md
```

## Validation command

From the repository root:

```sh
node tools/character_pipeline/validate_character_pipeline.mjs \
  --root /Users/mauvsantos/Workspace/games/Bentosaur \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json \
  --report art/characters/bentosaur-hero/char-v001/pipeline-validation.json
```

The current S10–S40 chain passes byte and SHA-256 validation.

## Current next actions

1. Complete and visually compare the replacement smile system.
2. Complete localized shoulder/armpit and pelvis/groin/knee topology repairs.
3. Merge only successful isolated branches into the next S40 revision.
4. Rerun neutral, reach, squat, walk, tail, smile, chew, and delighted-open
   tests.
5. Build the deterministic G40 visual and deformation reel.
6. Obtain Mau's explicit G40 approval.
7. Begin S50 only from the approved S40 source.
