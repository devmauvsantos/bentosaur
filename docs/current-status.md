# Bentosaur Current Status

Status: active

Snapshot date: 2026-07-30

## Executive state

Mau selected flat-cel 2D as Bentosaur's leading visual direction for now. A
matching expression proof, home/menu, regulars-book screen, independent laugh
marks, and page-turn motion breakdown now exist. The immediate project gate is
one real layered front character, one side-walk character, and one draggable
book page running in Godot on a phone.

The former live-3D direction is preserved as the last locked production path,
but it is paused while this decisive 2D proof runs. The visual selection does
not make the generated rasters production assets and does not silently discard
the 3D lineage.

No character is currently approved as production-ready, rig-ready, or
animation-ready in either route.

## Preserved live-3D stack

- Godot 4.7.1 Standard.
- Mobile renderer and typed GDScript.
- Blender as the native asset, rig, and animation authority.
- GLB as the deterministic engine boundary.
- Live 3D chibi diorama at runtime.
- Screen-space 2D/2.5D HUD with a hybrid 3D book.

## Active flat-cel 2D direction

The original selected style target remains:

`art/concepts/2d-chibi/v1/01_generated-exploration/bentosaur-gameplay-2d-flat-cel-v2.png`

The expanded proof pack is:

`art/concepts/2d-chibi/v2/`

Mau explicitly requested the matching hub, book, expression, and page-turn
exploration, superseding the earlier screen-generation restriction. The pack
now establishes visual continuity, not production readiness.

The first implementation remains bounded. One layered front rig and one
layered side rig must successfully idle, blink, delight, chew, walk, mirror,
and use a separate prop socket in Godot. The same proof adds one interactive
book page with drag, commit, cancel, sound, haptic, and reduced motion.

See
[2D flat-cel animation and screen proof](visual-explorations/2d-flat-cel-animation-and-screen-proof-v2.md).

## Character lineage

| Stage | State | Authority |
|---|---|---|
| S10 reference lock | Frozen | Approved design, anatomy, palette, and identity references |
| S20 high visual source | Frozen | H3.1 Extreme appearance and silhouette |
| S30 retopology scaffold | Frozen | Repaired Smart LowPoly, used only as a scaffold |
| S40 production topology | In progress | r003 body plus ongoing facial research |
| S50 UV/bake | Pending | Must wait for S40 approval |
| S60 look development | Pending | Must show final materials, not clay |
| S70 rig/skin | Pending | Must wait for topology and appearance gates |
| S80 animation | Pending | Must wait for the production rig |
| S90 Godot runtime | Lab exists; production pending | Mobile device gate remains open |

The machine-readable pointer remains:

`art/characters/bentosaur-hero/char-v001/pipeline.json`

## Facial experiment history

| Revision | Result |
|---|---|
| r001 | Blender/Godot morph proof; transform and tongue-placement problems |
| r002 | Structural mobile facial-control proof; art remained a proxy |
| r003 | Physical aperture/cavity proof; separate transition ring visibly failed |
| r004 | Exact Tripo alignment and mouth-region extraction; automatic contour stopped because the tongue hides the true lower lip |
| r005 | Two bounded welded-retopology attempts; a02 improved the mouth but failed at the outer seam and was frozen |
| r006 | One bounded broad-face bridge; mouth fit and mobile budget passed, but cheek flow folded and the attempt stopped before Faceit |

The r005 research checkpoint is:

`art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r005/`

Its best candidate:

- remains within the bounded mobile budget at 22,976 rendered triangles;
- is one closed all-quad body shell with a separate closed tongue;
- preserves the locked body outside the selected face boundary;
- closely matches the Tripo aperture and upper corners;
- fails production because of visible corner tears, five self-overlap
  candidates, poor extreme face aspect ratios, and a severe seam-normal break.

The two-attempt stop condition was honored. r005 must not be rigged, exported,
or promoted to S40.

The r006 checkpoint is:

`art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r006/`

It proved that enlarging the cut and keeping two transition rings on the
original S40 surface does not repair a one-to-one radial bridge. The candidate
is a closed all-quad shell, matches the Tripo aperture within `0.00253`, and
fits the working mobile budget at `23,168` rendered triangles including the
tongue. It nevertheless has seam-normal P95 `162.95°`, 117 overlap
candidates, and visible folded lower cheeks.

The one-attempt stop rule was honored. r006 did not proceed to neutral/open
shape keys or Faceit. Automated concentric mouth bridging is now retired.
See [F0 r006 stop report](facial-topology-f0-r006-stop-report.md).

## Facial direction now

Use one manually authored canonical neutral topology and a Faceit-style
authoring workflow:

1. neutral closed-mouth basis with the complete oral cavity and tongue present;
2. jaw/tongue controls plus a small set of Bentosaur-specific morph targets;
3. delightful open-mouth, blink, happy-eye, cheek, and chew presets;
4. bake to ordinary shape keys/deform bones;
5. export GLB;
6. mix expressions and animation in Godot.

Faceit is an authoring accelerator, not a retopology tool. Faceit 2.3 receives
one bounded pilot only after the canonical topology is visually and
technically approved. A custom Bentosaur-only tool is the fallback; a full
Faceit clone is not part of the game scope.

See [Faceit and AI facial-animation strategy](facial-animation-faceit-ai-pipeline-v1.md).

### Local Faceit installation

Faceit `2.3.71` is installed for Blender `5.1.2`. A disposable background
smoke test successfully enabled the extension for that process, registered a
generated mesh through `faceit.add_facial_part`, and confirmed the required
setup, landmarks, rig, bind, shape-key, and Audio2Face operators.

The automation session did not save Blender preferences or a `.blend`. The
repeatable smoke test is:

`tools/blender/faceit/faceit_smoke_test.py`

The live extension exposes 174 Faceit operators. Landmark fitting remains a
visible, modal 3D-view workflow and therefore requires an interactive
checkpoint rather than unattended headless execution.

Installation readiness does not authorize using the rejected r005 mesh.
It also does not authorize using the rejected r006 mesh.

## Immediate gates

### 2D P0 — registered layer master

- redraw the approved character into editable registered layers;
- keep the head base free of eyes, mouth, and accents;
- author open, blink, and happy eyes;
- author soft smile, open smile, and two chew mouths;
- keep all three laugh marks independently addressable;
- add hidden color bleed and stable pivots under every joint.

### 2D P1 — Godot character proof

- front idle, blink, neutral-to-happy, and chew;
- side walk east and mirrored west;
- independent prop socket;
- reversible reactions and reduced-motion endpoints;
- phone-scale silhouette and frame-time approval.

### 2D P2 — Godot book proof

- one continuous deformable page rather than a sprite sequence;
- touch drag, commit, cancel, and boundary handling;
- distinct front, underside, fold shadow, and next-page reveal;
- paper sound, optional haptic, visible buttons, and reduced motion;
- physical-device touch and performance approval.

The live-3D F0–F3 gates below remain preserved fallback work. Do not resume
them during the bounded 2D proof unless Mau explicitly reopens that route.

### F0 — canonical face

Mau receives front, three-quarter, profile, gameplay, wireframe, and shaded
evidence of the neutral basis and maximum delighted-open state using exactly
the same topology.

Pass conditions:

- soft reference-matching mouth silhouette;
- complete lips, cavity, and contained tongue;
- smooth outer transition with no seam or fold;
- no self-intersection at neutral, half-open, or fully open;
- topology suitable for jaw, smile, cheek, eye, and chewing deformation.

### F1 — Faceit authoring pilot

After F0 approval:

- register the production face and facial parts;
- fit and visually approve landmarks;
- generate/bind the facial controls;
- author only the required Bentosaur expressions;
- stop after one setup and one focused correction.

### F2 — expression performance

Approve:

- neutral to delighted-open;
- independent blink and happy-eye controls;
- chewing and savoring;
- combinations at 0%, 50%, and 100%;
- no clipping, volume collapse, or loss of character identity.

### F3 — Godot mobile proof

- baked names and ranges survive GLB export/import;
- the existing facial lab drives the controls by name;
- animation remains visually stable at the gameplay camera;
- physical-device frame time, memory, and thermals are measured.

## Costs and external actions

- The v2 flat-cel expression, hub, book, and key-pose concepts used built-in
  ImageGen; no Tripo credits or paid external API were used.
- Faceit `2.3.71` is installed locally; no license credential or transaction
  record is stored in the repository.
- No paid API was called during r004, r005, or r006.
- Tripo credits spent by r004/r005/r006: `0`.
- Recorded Tripo balance: `4,695`.
- No repository push is authorized by this status document.
