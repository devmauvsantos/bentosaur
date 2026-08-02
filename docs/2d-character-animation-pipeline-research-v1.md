# Bentosaur 2D Character Animation Pipeline Research V1

**Status:** recommendation complete; technical pilot not yet run

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

Do not purchase Spine until its official Godot 4.7 sample runtime has been
deployed to the connected iPhone and profiled with the existing rain, lighting,
and post-process shader.

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

The official Spine runtime repository's current build matrix explicitly includes
`4.7-stable`. Its workflow builds and packages macOS, iOS, Android, Windows,
Linux, and web GDExtension artifacts.

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
- [Official Godot 4.7 build matrix](https://github.com/EsotericSoftware/spine-runtimes/blob/4.4/.github/workflows/spine-godot-extension-v4-all.yml)
- [Official multi-platform GDExtension build workflow](https://github.com/EsotericSoftware/spine-runtimes/blob/4.4/.github/workflows/spine-godot-extension-v4.yml)

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
