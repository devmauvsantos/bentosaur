# Bentosaur Faceit and AI Facial-Animation Pipeline V1

Status: researched direction; bounded pilot selected

Date: 2026-07-30

Approval owner: Mau

## Decision

Build a Faceit-style facial system for Bentosaur, but do not build a complete
Faceit clone.

The production character will have one canonical topology, a small hybrid
bone-and-morph facial vocabulary, reusable expression presets, baked GLB
delivery, and a Godot runtime mixer. Faceit 2.3 is the preferred first
authoring accelerator after the topology gate. If one prepared pilot fails,
the fallback is a narrow Bentosaur-specific Blender tool using native
armatures, drivers, shape keys, and validation scripts.

## What the reviewed videos establish

### Blender Facial Animation Addon | Faceit

The Faceit overview demonstrates this authoring sequence:

1. register the connected face and optional eyes, teeth, tongue, and other
   facial geometry;
2. fit a landmark guide to the character;
3. generate and bind a Rigify-style facial rig;
4. pose and sculpt expressions non-destructively;
5. bake the resulting deformations into same-topology shape keys;
6. send ordinary morph targets or baked animation to a game engine.

Video:
https://www.youtube.com/watch?v=-MEglong_co

### Blender Facial Shape-Keys — FAST

The second video explains the underlying mechanism rather than a competing
tool: a Basis mesh and exact-topology vertex variants can be sculpted directly
or produced by posing a rig and joining the result as a shape key.

Its 52-shape requirement applies to a complete ARKit facial-capture target.
Bentosaur does not need 52 shapes for authored game acting.

Video:
https://www.youtube.com/watch?v=bqjM49G_MDY

## What Faceit solves

- landmark-guided face-rig generation;
- binding and weighting assistance;
- custom expression and preset management;
- pose plus corrective-sculpt authoring;
- non-destructive rollback between authoring stages;
- baking rig/modifier/sculpt deformation to shape keys;
- ARKit, Face Cap, Live Link Face, and Audio2Face data import/retargeting;
- shape-key control and animation tools.

Faceit officially supports realistic, cartoon, and anthropomorphic characters.
Its documentation explicitly discusses dragons and flat anime-like eyes.

## What Faceit does not solve

- retopology;
- hidden or missing lip anatomy;
- independently generated open/closed meshes with different vertex order;
- fused Tripo eyes, skin, cavity, and tongue as a production-ready character;
- final artistic approval;
- automatic correction of every stylized deformation;
- Godot runtime logic.

Faceit's documented best practice starts from a neutral expression with open
eyes, a closed mouth, one connected main skin surface, and clean deformation
topology. Eyes, tongue, teeth, and similar parts may be separate objects or
isolated surfaces; keeping Bentosaur's tongue and eyes separate is our
production preference.

The immutable Tripo open-mouth model remains a sculpt and silhouette target.
It is not a shape key and does not ship.

## Purchase versus custom development

The current official Faceit listing offers:

| Edition | Intended use | Price at research time |
|---|---|---:|
| Faceit 1.8 | Fixed ARKit expression workflow | USD 78 |
| Faceit 2.3 | Custom and unlimited expressions | USD 99 |
| Faceit 2.3 Studio | 2–9 seats | USD 289 |

Faceit 2.3 is the relevant option. The listing currently covers Blender
3.0–5.2, which includes the Bentosaur Blender 5.1 authoring environment.

Faceit `2.3.71` is now installed locally for Blender `5.1.2`. The repository
does not store license credentials or purchase records.

A disposable background smoke test passed object registration and confirmed
the operator surface needed for setup, landmarks, rig generation, binding,
shape-key baking, and Audio2Face import. Background automation must explicitly
enable `bl_ext.user_default.faceit` for each disposable process; the test does
not save user preferences.

Automation contract:

`tools/blender/faceit/README.md`

A complete clone would require general-purpose landmark fitting, automatic
binding, non-destructive stage reconstruction, dozens of expression presets,
mocap importers, retargeting, multi-character robustness, and a maintained
Blender UI. That is product-scale work unrelated to shipping the game.

## Bentosaur facial architecture

```text
canonical neutral topology
        |
        +-- deform bones: jaw, tongue base/tip, optional eye aim
        |
        +-- morph targets: lips, smile, cheeks, eyelids, happy eyes,
        |                  emotion shapes, jaw correctives
        |
        +-- expression presets and Blender animation clips
                              |
                              v
                      baked GLB delivery
                              |
                              v
                    Godot expression mixer
```

### Initial control vocabulary

Deform bones:

- `jaw`;
- `tongue_01`;
- `tongue_02`;
- optional eye/look controls if the approved eye design uses separate eyeballs.

Morph targets:

- `jaw_open_corrective`;
- `lip_seal`;
- `mouth_smile`;
- `mouth_o`;
- `mouth_sad`;
- `cheek_puff`;
- `blink_L`;
- `blink_R`;
- `eye_happy_L`;
- `eye_happy_R`.

Game presets/clips:

- `neutral`;
- `delighted_open`;
- `happy_open`;
- `blink`;
- `chew`;
- `savor`;
- `surprised`;
- `disappointed`.

The approved reference expression is a mix, not another character mesh:

```text
jaw_open              0.80
mouth_smile           1.00
eye_happy_L           1.00
eye_happy_R           1.00
cheek_puff            0.25
tongue_up             0.20
```

Exact values are artistic starting points and require Mau's approval.

## Where AI genuinely helps

| Use | Decision | Reason |
|---|---|---|
| Generate a different mesh for every expression | Avoid | It destroys the shared-topology requirement that makes animation possible |
| Tripo high-detail expression sources | Use as reference only | Excellent silhouette/sculpt targets; unsuitable as direct morph targets |
| Codex plus Blender automation | Use now | Can prepare scenes, invoke deterministic scripts, name controls, render gates, compare evidence, validate topology, build manifests, and test exports |
| AI-assisted landmark proposal | Experimental | Vision can suggest 2D landmark positions, but projection, pivots, and deformation quality still require a controlled Blender pass |
| AI visual QA | Use now with human approval | Overlay renders, measure silhouette/source deviation, and flag clipping or identity drift; Mau remains the visual authority |
| NVIDIA Audio2Face | Later, only if voiced dialogue matters | Generates audio-driven blendshape curves that Faceit can import/retarget |
| iPhone Face Cap or Live Link Face capture | Optional reference/performance capture | Fast acting input through ARKit; it is capture rather than generative asset creation |
| MediaPipe video/webcam extraction | Experimental blocking only | Tools such as DeadFace can derive rough face coefficients from video, but documented weak mouth-close/pucker capture makes this inappropriate for final mouth approval |
| AI-generated final corrective shapes without review | Avoid | A numerically valid deformation can still look wrong, lose volume, or change the character |

### Faceit plus NVIDIA Audio2Face

This is the documented direct AI integration:

```text
voice audio
   -> NVIDIA Audio2Face
   -> ARKit/FACS blendshape weights
   -> Faceit import and retarget
   -> artist cleanup/bake
   -> GLB/Godot
```

It can accelerate dialogue, lip sync, and broad emotional performance. It
does not create Bentosaur's topology or expression targets.

The current NVIDIA Audio2Face-3D stack is GPU service software with meaningful
deployment requirements. NVIDIA's hosted Audio2Face endpoint is marked
deprecated, while the downloadable SDK requires CUDA/NVIDIA hardware on
Windows or Linux. It is not a local-Mac dependency.
Faceit's documented importer targets exported weight data; current NVIDIA NIM
output may require a small adapter before it matches the older Faceit import
format. Therefore Audio2Face is not part of the first no-dialogue facial
pilot.

The lowest-risk first performance input is iPhone ARKit capture through Face
Cap or Live Link Face. That is not generative AI, but it is already documented
by Faceit and gives us editable acting data without making a remote GPU service
part of production.

### AI-assisted Faceit operation

Faceit has no documented MCP server. Once installed in Blender, an agent can
operate around it through Blender/Python automation:

- validate object roles before registration;
- generate or import Bentosaur landmark proposals;
- call stable Faceit Blender operators where available;
- render every landmark and expression checkpoint;
- run topology, clipping, range, naming, and export tests;
- produce the expression manifest and Godot binding contract.

Faceit's internal operator API is not promised as a stable public integration.
Automation must be pinned to the purchased version and protected by a smoke
test. UI-driving is a fallback, not the production contract.

The installed Faceit build exposes 174 Blender operators, but landmark
placement is a modal 3D-view workflow that depends on visible editor and mouse
context. This is the deliberate interactive boundary: AI can propose and
validate landmark positions, while Mau reviews the visible landmark fit before
rig generation. Headless scripts own repeatable preflight, evidence, baking,
export, and QA—not invisible landmark guessing.

## Bounded pilot

### F0 — topology prerequisite

Before Faceit:

- one canonical neutral closed-mouth skin topology;
- complete lips, cavity, and tongue;
- soft delighted-open target authored on the same vertices;
- no seam, fold, intersection, or identity drift;
- Mau approves clay, shaded, wireframe, source overlay, and gameplay views.

The one-attempt r006 automated broad-face bridge failed this prerequisite and
was frozen before Faceit. Radial/concentric loop bridging is retired; the next
candidate requires explicit Poly Build or dedicated topology-transfer work.
See [F0 r006 stop report](facial-topology-f0-r006-stop-report.md).

### F1 — Faceit setup

- install the approved Faceit 2.3 version;
- freeze a new Blender checkpoint;
- register face and facial parts;
- fit landmarks from front and side;
- approve jaw and eye pivots;
- generate and bind once;
- allow one focused correction, then stop and reassess.

### F2 — minimal expression proof

Create only:

- neutral;
- delighted-open;
- blink/happy eyes;
- cheek puff;
- chew.

Review every shape at 0%, 50%, and 100%, plus the important combinations.

### F3 — bake and Godot

- bake approved expressions to named shape keys and required deform bones;
- export GLB with only production deformation bones;
- re-import the GLB into a clean Blender scene as an export check;
- validate names and ranges in the Godot facial lab;
- capture gameplay-camera and physical-device evidence.

### Stop rule

If the prepared Faceit setup fails after the initial implementation and one
focused correction, preserve the evidence and switch to the native Blender
fallback. Do not enter repeated automatic binding, landmark, or weight-paint
loops.

## Sources

- Faceit overview:
  https://faceit-doc.readthedocs.io/en/latest/
- Faceit geometry requirements:
  https://faceit-doc.readthedocs.io/en/latest/geometry/
- Faceit expressions:
  https://faceit-doc.readthedocs.io/en/latest/create-expressions/
- Faceit mocap and Audio2Face:
  https://faceit-doc.readthedocs.io/en/latest/mocap_general/
- Faceit importer workflow:
  https://faceit-doc.readthedocs.io/en/beta/mocap_importers/
- Faceit export:
  https://faceit-doc.readthedocs.io/en/beta/export/
- Official Faceit listing:
  https://superhivemarket.com/products/faceit
- Apple blend-shape guidance:
  https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapes
- NVIDIA Audio2Face-3D:
  https://docs.nvidia.com/ace/latest/modules/a2f-docs/
- NVIDIA Audio2Face-3D SDK:
  https://github.com/NVIDIA/Audio2Face-3D-SDK
- DeadFace MediaPipe extraction experiment:
  https://github.com/Qaanaaq/DeadFace
- Godot 4.7 blend-shape tracks:
  https://docs.godotengine.org/en/4.7/tutorials/animation/animation_track_types.html
- Godot 3D format guidance:
  https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html
