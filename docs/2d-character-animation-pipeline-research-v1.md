# Bentosaur 2D Character Animation Pipeline Research V1

**Status:** official desktop runtime pilot passed; Bentosaur integration awaits
Spine Professional licensing and physical-iPhone availability

**Date:** 2026-08-02

**Scope:** approved full-body side-view Bentosaur, future foreground guests,
ambient street walkers, Godot 4.7 Mobile, and iOS

## Recommendation

Use a hybrid Spine pipeline:

1. **Spine Professional** is the character-rig and animation source of truth.
2. The official **spine-godot GDExtension** renders the proprietor and other
   important foreground/interactable dinosaurs live in Godot.
3. Background walkers and crowds are exported from those same Spine rigs as
   restrained **10–12 FPS sprite sheets** and played by `AnimatedSprite2D`.
4. Godot continues to own movement, AI/state scheduling, interactions, props,
   audio, weather, UI, camera, and scene transitions.
5. **Moho Pro 14.4** is the only fallback worth testing if Spine cannot preserve
   the approved soft silhouette.

The original plan was to complete a no-purchase runtime pilot first. Spine's
current license does not permit Trial users to integrate the Spine Runtimes
into a product, so the official sample was evaluated outside the Bentosaur
project. A valid Spine Professional license is required before the runtime is
copied into this repository or exported in a Bentosaur iOS build.

See
[the desktop runtime checkpoint](checkpoints/2026-08-02-spine-runtime-desktop-pilot-v001.md).

## Why this solves the actual failure

The rejected Godot feasibility rig treated the character like a humanoid chain:
independently generated upper and lower limbs were assembled at full scale. The
result had giant arms and legs even though the source character was cute.

The approved V002 character has a different anatomy contract:

- the head/frill dominates the silhouette;
- the torso is a compact bean;
- each arm is one tiny integrated shape, not an upper-arm/forearm chain;
- each leg is one extremely short integrated shape, not a thigh/shin chain;
- soft bending should come from sparse mesh weights, not additional visible
  limb segments;
- eyes and mouths should swap as attachments rather than stretch with the face.

Spine Professional directly supports weighted meshes, automatic weight
calculation, IK, attachment swaps, skins, animation tracks, mixing, and atlas
export. Its official Godot runtime avoids inventing a custom character format.

## Tool comparison

| Tool | Art preservation | Godot/iOS delivery | Current cost | Bentosaur verdict |
|---|---|---|---:|---|
| **Spine Professional** | Excellent raster attachments, sparse meshes, weights, IK, swaps, skins | Official Godot 4.7 GDExtension and iOS build path | **US$379** sale / $449 shown regular, one-time | **Use** |
| **Moho Pro 14.4** | Excellent PSD/bitmap rigging, Smart Bones, warp meshes, dynamics | Official animated GLB/glTF export; Godot receives a 3D scene | **US$399.99**, one-time | One fallback pilot only |
| Toon Boom Harmony Premium | Very high film/TV ceiling | No turnkey Godot skeletal runtime; bake sprite sheets | $139/month or $1,128/year currently shown | Excessive for this game |
| Live2D Cubism | Excellent front-facing face/body deformation | No official Godot runtime; optimized for portrait acting | Subscription | Not the walking-character tool |
| Rive | Strong vector/UI state machines and interaction | Official runtime list does not include Godot | Subscription/free tiers | Consider for UI research, not NPCs |
| DragonBones/LoongBones | Mesh and IK features | Community runtime ownership and maintenance risk | Free/varied | Prototype only |
| Spriter 2 | Rigid cutout workflow | Community importers; Spriter 2 remains beta | Varied | Too weak for soft deformation |
| Creature | Auto-walk and mesh concepts | Official repository targets Godot 3 and is inactive | Varied | Reject |
| Blender 2D/planes | Powerful and free | Requires a 3D/SubViewport or baked-frame pipeline | Free | More complexity than Spine |

No reviewed alternative clearly beats Spine for an exact raster character in a
native Godot 2D game. Moho is the only close challenger, but its new engine
export is a 3D-container workflow (`Skeleton3D`, meshes, and morph targets), so
it requires the compositing and mobile testing that Spine avoids.

## Confirmed Godot 4.7 and iOS support

The official stable Spine 4.3 runtime build matrix currently includes Godot
`4.7.1-stable`. Its package contains macOS, iOS, Android, Windows, Linux, and
web GDExtension artifacts. The exact pinned artifact and matching sample commit
also pass with Bentosaur's installed Godot `4.7.0-stable`. Spine 4.4 exists as
a source-only pre-release branch; no official 4.4 binary package is published.

Use the GDExtension route, not Spine's custom Godot editor/module:

- it drops into the existing project under `bin/`;
- it keeps the ordinary Godot 4.7 editor and ordinary iOS export workflow;
- it exposes `SpineSprite`, animation state, tracks, mixing, events, bone nodes,
  slot nodes, skins, and custom materials to GDScript;
- it does **not** integrate Spine clips into Godot's `AnimationPlayer`; clips
  remain authored in Spine and are selected/mixed from GDScript;
- the custom module adds `AnimationPlayer` support but creates a permanent
  custom-editor and export-template maintenance burden that Bentosaur does not
  need.

Primary references:

- [Official spine-godot guide and samples](https://esotericsoftware.com/spine-godot)
- [Official Spine runtime repository](https://github.com/EsotericSoftware/spine-runtimes)
- [Official stable Godot build matrix](https://github.com/EsotericSoftware/spine-runtimes/blob/4.3/.github/workflows/spine-godot-extension-v4-all.yml)
- [Official stable multi-platform GDExtension workflow](https://github.com/EsotericSoftware/spine-runtimes/blob/4.3/.github/workflows/spine-godot-extension-v4.yml)

## Completed runtime pilot

On 2026-08-02 the untouched official Spine 4.3 samples were run against the
official prebuilt GDExtension and both Godot 4.7.0 and 4.7.1:

```text
Spine runtime: 4.3 stable
GDExtension target: Godot 4.7.1-stable
Pinned source commit: 4be2da7d25fdf046bddaf1633d6bde73e25cce81
Godot editors: 4.7.stable.official.5b4e0cb0f and 4.7.1.stable.official.a13da4feb
Desktop renderer: Metal 4.0 / Apple M5
Result: import PASS; SpineBoy PASS; weighted Raptor PASS; 145 FPS cap
```

The first attempt combined the published runtime artifact with the latest 4.3
branch sample instead of the artifact's exact source commit. Its asset import
was incomplete and produced a null animation state. The pinned sample then ran
cleanly with both editors. Runtime binary, sample/export schema, and later
Bentosaur exports must be versioned as one unit.

Godot 4.7.1 is still the recommended maintenance upgrade before production
integration, but the pilot does not require it to prove compatibility with the
current project.

Pinned official archive:

`https://spine-godot.s3.eu-central-1.amazonaws.com/4.3/4.7.1-stable/`
`spine-godot-extension-4.3-4.7.1-stable.zip`

Locally verified SHA-256:

`0bfd296040d2a28bea9031df1edbd2591201ede54199335bf21e8f9d225b6cda`

No Spine runtime, example data, or third-party sample artwork was added to the
repository. Local render evidence is retained only in ignored build output at:

`build/spine-evaluation/official-spineboy-godot-4.7.1-proof.png`

`build/spine-evaluation/official-spineboy-godot-4.7.1-proof.avi`

`build/spine-evaluation/official-raptor-godot-4.7.0-proof.png`

`build/spine-evaluation/official-raptor-godot-4.7.0-proof.avi`

The remaining gates are:

1. obtain a valid Spine Professional license;
2. pin runtime, sample/export schema, and future Spine editor to version 4.3;
3. preferably update the working editor and iOS export templates together to
   Godot 4.7.1 before production integration;
4. integrate only the pinned macOS and iOS GDExtension artifacts with the
   required Spine license notice;
5. run the official weighted raptor at 0, 1, 10, and 20 instances in an
   isolated lab that reuses the village, rain, lighting, and anime filter;
6. run an eight-minute 20-instance soak to cover the historical filter issue;
7. connect and unlock Mauricio's iPhone 17 Pro Max, then build, inspect signing,
   install, launch, and profile under personal team `53RJ43876F`;
8. only after runtime performance passes, prepare and rig the approved
   Bentosaur layered source.

Licensing references:

- [Spine Runtimes License](https://esotericsoftware.com/spine-runtimes-license)
- [Spine Editor License, Trial restriction and runtime integration](https://esotericsoftware.com/spine-editor-license)
- [Godot 4.7.1 maintenance release](https://godotengine.org/article/maintenance-release-godot-4-7-1/)

## Production authoring recipe

The approved silhouette—not the skeleton—is the authority. Bones deform inside
the compact chibi shapes and must never invent humanoid anatomy.

1. Cut or redraw one layered master with `frill`, `head`, `body`, `tail`,
   `arm_back`, `arm_front`, `leg_back`, `leg_front`, `eye`, and `mouth`.
   Preserve claws within the limb art and draw only the concealed overlap
   needed beneath joints.
2. Reassemble the layers and require no visible difference from the approved
   flattened source at close-up or intended background scale before rigging.
3. Use a compact hierarchy rooted at the hips, two leg IK targets outside the
   hip chain for planted feet, FK arms, and a three- or four-bone tail.
4. Keep each arm and leg as one whole weighted mesh. Two internal bones may
   bend that mesh, but there must be no visible upper/lower-limb seam.
5. Start with automatic weights, then hand-correct. Prefer one or two bone
   influences per vertex, use three only near broad bends, and cap at four.
   Avoid direct keyed mesh-deform timelines unless a reviewed exception needs
   one.
6. Build the walk pose-to-pose: contact, down, passing, up, opposite contact.
   Verify planted feet using temporary container travel, then export an
   in-place cycle.
7. Keep `idle/base` restrained. Schedule blink, look, happy, and other overlays
   from Godot on higher tracks so the character does not repeat one canned
   super-loop.
8. Use attachment swaps for `eye_open`, `eye_half`, `eye_closed`,
   `mouth_closed`, `mouth_smile`, and `mouth_open`. Laugh accent lines remain a
   separate hidden slot.
9. Export Spine 4.3 binary `.skel`, `.atlas`, and one straight-alpha PNG atlas
   page. Share one `SpineSkeletonDataResource` across matching instances.

First-rig working limits:

- 22–30 bones;
- two leg IK constraints and no arm IK initially;
- three or four tail bones;
- at most roughly 300 visible mesh vertices and 600 vertex transforms;
- no clipping, one atlas page, and no direct deform timelines;
- one live right-facing side rig mirrored by Godot for screen-left travel.

Useful official tutorials:

- [How to cut assets for animation](https://esotericsoftware.com/blog/How-to-cut-your-assets-for-animation)
- [Import PSD and layer tags](https://esotericsoftware.com/spine-import-psd)
- [Chibi Stickers example](https://esotericsoftware.com/spine-examples-chibi-stickers)
- [Raptor example](https://esotericsoftware.com/spine-examples-raptor)
- [Spineboy biped and IK example](https://esotericsoftware.com/spine-examples-spineboy)
- [Walk-cycle tutorial](https://www.youtube.com/watch?v=Giuanw16gyY)
- [Mesh attachments](https://esotericsoftware.com/spine-meshes)
- [Weights](https://esotericsoftware.com/spine-weights)
- [Metrics](https://esotericsoftware.com/spine-metrics)
- [Applying layered animations](https://esotericsoftware.com/spine-applying-animations)

## Approved-art preparation contract

The immutable visual source is:

`art/characters/bentosaur-walker/char-v002/gate01/`
`bentosaur_walker_side_gate01_transparent_v002.png`

The character must not be regenerated as an exploded puppet sheet.

### Layered master

Create one layered PSD over the approved source, preserving its registered
position and canvas. The exact layer naming can use Spine PSD tags after the
pilot, but the visual layer contract is:

```text
reference_locked (not exported)
expression_fx
mouth
eye
head_frill_horns
arm_front
leg_front
torso_belly
tail_back
arm_rear
leg_rear
```

The setup pose must reassemble to the approved source before a bone is added.
Only concealed pixels may be newly painted:

- a small shoulder overlap under each arm;
- a small hip overlap under each leg;
- the tail root behind the torso;
- the neck/body surface hidden by the head;
- clean face surface underneath replaceable eye and mouth slots.

Those fills may use AI-assisted inpainting, but they are hidden in the approved
rest pose and must be manually reviewed. AI must not redesign visible anatomy or
independently generate limbs.

Spine can directly import layered PSDs from Photoshop, Affinity, Krita, GIMP,
Clip Studio Paint, Photopea, Procreate, and other PSD-writing tools. PSD names
can declare bones, slots, skins, folders, and meshes.

- [Official Spine PSD import and tagging guide](https://esotericsoftware.com/spine-import-psd)

### Rest-pose acceptance gate

Before rigging:

1. composite all production layers at their setup transforms;
2. compare the composite with the immutable approved PNG;
3. produce a visual difference image and numeric report;
4. require no visible change at close-up and background scale;
5. reject any seam, silhouette drift, extra horn, altered face, or limb growth.

The approved whole drawing—not the separated files—is always the visual source
of truth.

## Compact production rig

The first rig deliberately avoids human joint anatomy:

```text
root
└── body
    ├── head
    ├── tail_01
    │   └── tail_02
    │       └── tail_03
    ├── arm_front
    ├── arm_rear
    ├── leg_front
    └── leg_rear
```

Additional controls may drive body squash, eye direction, or the feet, but they
must not create visible upper/lower arm or thigh/shin pieces.

- Head and torso: sparse weighted meshes for tiny breathing/squash changes.
- Tail: a sparse weighted mesh across two or three bones.
- Arms: one short control each, mostly rigid or very lightly weighted.
- Legs: one short control each. Add foot/IK controls only if the contact test
  proves useful without elongating the silhouette.
- Horns and frill knobs: remain part of the head unless a later test proves a
  production need to separate them.
- Eye, blink, mouth, chew, and laugh marks: replacement attachments/slots.
- No clipping unless a real production pose requires it.

Spine's automatic weights are a deterministic starting point. Final weighting,
contact poses, and timing remain manual art-direction work.

- [Official mesh attachments guide](https://esotericsoftware.com/spine-meshes)
- [Official weights and automatic-weight workflow](https://esotericsoftware.com/spine-weights)
- [Official mesh-weight workflow guidance](https://esotericsoftware.com/blog/Mesh-weight-workflows)
- [Official IK guide](https://esotericsoftware.com/spine-ik-constraints)

## First animation pilot

Build only these clips:

1. `idle` — 2.4 seconds, restrained body breath, tiny head drift, small delayed
   tail response;
2. `walk` — 0.8–1.0 seconds, small steps, low body travel, no limb extension;
3. `blink` — a short overlay attachment animation;
4. `look` — optional tiny head/eye variation after the first three pass.

Godot track convention:

```text
track 0: idle / walk / carry
track 1: blink / look
track 2: reaction / wave / delight
```

The pilot is rejected if the character looks hinged, rubbery, humanoid, or less
cute than the static approved source.

## Runtime export and import

Preferred Spine export:

```text
bentosaur-side-v002.skel       # binary skeleton and animation data
bentosaur-side-v002.atlas      # atlas coordinates
bentosaur-side-v002.png        # one atlas page if possible
```

- Prefer binary `.skel` because it is smaller and faster to load.
- Use normal alpha, not premultiplied alpha; spine-godot currently does not
  support premultiplied-alpha atlas exports.
- Share one `SpineSkeletonDataResource` between matching instances.
- Resolve animation names defensively in GDScript during iteration; stale
  default animation names have caused a current Godot 4.7 runtime crash after
  export changes.
- Keep the existing anime filter, rain, lighting, and shader pipeline active in
  the physical-device test.

Current integration cautions:

- [Godot 4.7 slot-flipping issue and current fix](https://esotericsoftware.com/forum/d/30404-spine-43-with-godot-47-sub-slots-flipped-y-axis)
- [Godot 4.7 stale animation-name crash report](https://en.esotericsoftware.com/forum/d/30493-godot-43-47-stable-crashes-if-you-change-resources-with-new-animation-names)

## Why background walkers should be baked

The official runtime is appropriate for important characters, but Godot does
not currently batch Spine's required triangle-mesh rendering path like ordinary
sprites. A live skeleton can approach one draw call per visible slot. A crowd
of 20 ten-slot rigs can therefore approach 200 character draw calls before the
village, rain, lighting, shader, smoke, and UI.

Background walkers should normally be rendered from the approved Spine rig into
10–12 FPS sheets:

```text
same approved layered art
→ same Spine skeleton and animations
→ PNG sprite sheet
→ Godot AnimatedSprite2D
```

This is not recreating every animation by hand. Spine remains the reusable
animation source; baking only changes delivery for small/distant actors.

Keep live Spine rigs for actors that benefit from runtime mixing, accessories,
expressions, prop sockets, or direct interaction. If a live background rig is
needed, use manual update mode at 15–30 Hz and stop updates while offscreen.

- [Spine/Godot draw-call investigation](https://esotericsoftware.com/forum/d/29600-spinesprite-generating-1-draw-call-per-slot-batching-failure-in-subviewport)
- [Official batching limitation discussion](https://esotericsoftware.com/forum/d/28447-441-gdextension-how-to-enable-auto-batching)

## No-purchase technical pilot

Before buying Spine Professional:

1. obtain the official Godot 4.7 spine-godot GDExtension and example project;
2. run its hello-world, animation, skin, slot, material, and 2D-light examples
   on macOS;
3. add the project's post-process shader and confirm the filter remains stable;
4. export the sample to the connected iPhone under the personal developer
   account already documented for Bentosaur;
5. profile 1, 10, and 20 sample skeletons alongside rain and lighting;
6. record FPS, frame time, draw calls, memory, visual correctness, and launch
   stability;
7. purchase Spine Professional only if this gate passes.

The trial can demonstrate Spine's editor and official example rigs, but it does
not grant product runtime-distribution rights and cannot save/export production
work. Do not build Bentosaur's production rig in a disposable trial session.

## Cost and licensing

Prices verified on 2026-08-02; promotional prices may change:

- Spine Essential: **US$69** currently shown, regular price shown as $99.
- Spine Professional: **US$379** currently shown, regular price shown as $449.
- Moho Pro 14: **US$399.99**.

Bentosaur needs Spine **Professional**. Essential omits meshes, weighted
deformation, IK, clipping, and physics. The Spine purchase page says future
updates are included. Businesses or individuals at/above the stated $500,000
revenue/investment/funding threshold require Enterprise licensing.

- [Official Spine pricing and feature matrix](https://esotericsoftware.com/spine-purchase)
- [Spine runtime license](https://esotericsoftware.com/spine-runtimes-license)
- [Official Moho pricing/features](https://moho.lostmarble.com/pages/features)

## AI's useful and non-useful roles

Spine does not currently provide generative AI rigging or animation. It does
provide automatic mesh tracing and automatic weight calculation.

AI may help with:

- concealed overlap reconstruction;
- tightly controlled eye and mouth attachment candidates;
- palette/species variants after the master rig works;
- automated rest-pose image comparison and QA.

AI should not decide:

- visible anatomy;
- bone placement;
- final weights;
- foot contacts;
- animation timing and appeal;
- whether a generated variant still belongs to the approved character family.

- [Official Spine position on current AI capability](https://esotericsoftware.com/forum/d/29913-why-doesnt-spine-focus-on-ai-or-automated-skeletal-animation-generation)

## Recommended learning sequence

1. [Spine First Steps](https://esotericsoftware.com/spine-first-steps)
2. [Official Spine User Guide video playlist](https://www.youtube.com/playlist?list=PLwGl7Ikd_6GRFo7d0uRu_fN2RIlvkxW7b)
3. [Attachments and meshes — part 1](https://www.youtube.com/watch?v=76Var_oS8EM)
4. [Attachments and meshes — part 2](https://www.youtube.com/watch?v=3SqxwSN4xPo)
5. [Weights](https://www.youtube.com/watch?v=d-YeActEi38)
6. [Inverse kinematics](https://www.youtube.com/watch?v=sos36zmLFOc)
7. [Animating with Spine playlist](https://www.youtube.com/playlist?list=PLwGl7Ikd_6GQ9EpVw2qdvvqgbhjSw7dIj)
8. [Official spine-godot integration and runnable samples](https://esotericsoftware.com/spine-godot)

Moho fallback materials:

- [Moho 14.4 game-engine export tutorial](https://www.youtube.com/watch?v=aamqqcTwPC4)
- [Moho 14.4 announcement](https://www.youtube.com/watch?v=NOS5VdiCBu4)
- [Official Moho/Godot sample assets](https://moho.lostmarble.com/pages/addons)

## Decision gate

The research recommendation is complete, but the production pipeline is not
locked until the no-purchase runtime pilot passes on the connected iPhone.

If it passes: buy Spine Professional, prepare the approved V002 layered master,
and run the rest-pose pixel-match gate.

If it fails: test the official Moho 14.4 Godot sample before touching the
approved source. If both live-runtime paths fail, use Spine or Moho only as the
offline authoring tool and ship baked sprite sheets.
