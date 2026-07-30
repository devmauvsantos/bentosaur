# Bentosaur Character Reuse Architecture

**Status:** Accepted for the vertical slice  
**Decision date:** 2026-07-28  
**Scope:** Customer dinosaurs, ambient street dinosaurs, portraits, props, and animation production

## Decision

Bentosaur will remain a 2D Godot game. Its characters will not be produced as a
separate, independently generated sprite sheet for every situation.

Each customer identity is expressed through a small **directional character
kit**:

1. **Side view** for walking and ambient street behavior. Author east once and
   mirror it for west unless an asymmetric accessory makes mirroring incorrect.
2. **Front / counter-facing view** for ordering, waiting, receiving food, eating,
   and reacting at the stall.
3. **Portrait / expression view** for the Regulars album. This is a cropped face
   and emote system, not another full-body animation rig.
4. **Back view only if a shipped scene proves it is necessary.** It is not part
   of the vertical-slice budget.

The side and front views share the same identity contract, naming, animation
semantics, palette channels, face vocabulary, accessories, and prop sockets.
They do not share the same pixels: a flat side drawing has no information about
the front surfaces hidden from the camera.

This is the 2D analogue of a reusable 3D character, with one important
limitation:

> A 2D rig can reuse parts and motion within a view. It cannot reconstruct a
> viewpoint that was never drawn.

## Why only two views are needed

Bentosaur does not have free character rotation or a roaming camera. The
restaurant composition determines the views:

- Dinosaurs cross the street in profile.
- A customer at the counter faces the player.
- The album uses an authored portrait.

Therefore the production problem is not “eight directions multiplied by every
animation.” It is “one side motion family plus one front acting family.”

```text
One dinosaur identity
├── Side kit
│   ├── walk
│   ├── pause
│   ├── look around
│   ├── carry / umbrella overlay
│   └── mirrored west-facing presentation
├── Front kit
│   ├── idle / blink
│   ├── order / speak
│   ├── wait
│   ├── receive tray
│   ├── delight / disappointment
│   └── chomp
└── Portrait kit
    ├── neutral
    ├── delighted
    └── relationship-state decorations
```

## Runtime versus authoring

The production pipeline is deliberately hybrid.

### Runtime in Godot

Godot plays clean, baked pixel clips through `AnimatedSprite2D` / `SpriteFrames`.
It owns behavior, state changes, clip scheduling, whole-character movement,
east/west mirroring, prop attachment, discrete face swaps, particles, sounds,
and interaction events.

This keeps the shipped result deterministic, mobile-friendly, and visually
identical to the approved frames.

### Motion authoring

Use a reusable cutout skeleton to block motion, but do not require a live
skeletal runtime for every dinosaur.

Recommended stack:

1. PixelLab or Retro Diffusion creates an approved side anchor and a matching
   front-facing anchor from the same identity references.
2. Aseprite cleans both anchors and separates body parts where rigging helps.
3. PixelOver blocks reusable motions with bones, pivots, parent-child
   hierarchies, and IK.
4. PixelOver exports fixed-cell PNG sheets or `.aseprite`.
5. Aseprite performs the final pixel pass: silhouette, face, feet, palette,
   timing, squash, smears, and loop continuity.
6. Godot imports the baked sheets with lossless, nearest-neighbor settings.

PixelOver is an **offline rig and bake tool**, not a second runtime dependency.
Its current one-time price is USD 29.99; the trial includes all features except
export.

### What may stay live

For one to three larger close-up actors, a restrained Godot master rig may use:

- `Skeleton2D` and rigid `Sprite2D` children;
- `Bone2D` for hierarchy and stable sockets;
- `AnimationPlayer` as the canonical clip/event store;
- `AnimationTree` only where layered acting is genuinely useful;
- `AnimatedSprite2D` child nodes for replacement faces, hands, and mouths.

Do not use weighted `Polygon2D` deformation, continuous animation blending, or
runtime IK on 24–64 px shipping sprites by default. Rotations and weighted
deformation make the pixel clusters crawl and turn the character into a paper
puppet.

## Directional rig contract

All compatible rigs use stable semantic names. The art differs by view, but the
meaning remains consistent.

```text
DinosaurActor2D
├── IdentityController
├── SidePresentation
│   ├── root / hips
│   ├── torso
│   ├── head / frill
│   ├── arm_near / arm_far
│   ├── leg_near / leg_far
│   ├── tail_base / tail_tip
│   ├── face_slot
│   ├── hand_socket
│   └── accessory_slots
├── FrontPresentation
│   ├── root / torso
│   ├── head / frill
│   ├── hand_left / hand_right
│   ├── eyes_slot / mouth_slot
│   ├── tray_socket
│   └── accessory_slots
├── AnimationPlayer
└── StateController
```

View changes are discrete. Never morph the side silhouette into the front
silhouette.

For a multipart side rig, mirror only an outer visual node. Keep gameplay,
collision, and motion logic outside the mirrored hierarchy. If an apron, horn,
bag, text, or hand action is asymmetric, supply an explicit west asset or swap
the asymmetric overlay.

## Resolution routing

### Ambient street dinosaurs: 24–48 px

Use a baked side loop. A four- to six-frame east walk is mirrored for west.
Small loops such as pause, blink, look, umbrella, or carry are scheduled and
phase-shifted by Godot. At this size, drawing or cleaning the final frames is
faster and better than shipping a live rig.

### Counter customers: 64–96 px

Use the front kit. The stable torso/head can be reused while face, mouth, hands,
tray, and accessory layers swap discretely. Block animation with the reusable
front rig, then bake any action involving contact, a strong silhouette change,
or food.

### Album portraits

Use the approved front identity as the source, but author album expressions as
separate portrait cells. Do not crop runtime world sprites and call them
portraits.

## Art-count reality

A naive plan for one dinosaur might be:

```text
4 directions × 4 actions × 4 frames = 64 independently generated cels
```

The Bentosaur plan is closer to:

```text
1 side anchor + 1 front anchor
+ reusable motion templates
+ a small face/hand/prop replacement set
+ one mirrored side presentation
```

We still approve final frames, but we do not prompt an image model for every
frame. AI generates identity anchors and controlled variations; deterministic
animation tools create continuity.

## The true one-model alternative: 3D-to-2D

If one source must generate genuinely arbitrary angles, the source must contain
3D information. The safe hybrid is:

```text
Blender rigged character
→ orthographic render or PixelOver 3D import
→ required directions and animation frames
→ Aseprite cleanup
→ baked 2D sprite sheets in Godot
```

This provides a real reusable mesh, skeleton, animation library, prop sockets,
and camera angles while keeping the game itself 2D.

It is not the default for the vertical slice because:

- the first polished mascot model, topology, texture, rig, and render recipe are
  a material production project of their own;
- raw 3D-to-pixel output often loses the hand-shaped cheeks, frill, eyes, and
  warm asymmetry that give the concept its heart;
- every hero animation still needs a pixel cleanup pass;
- live 3D introduces lighting, skinning, hybrid occlusion, pixel shimmer,
  renderer, and device-QA work that the fixed restaurant camera does not need.

Use Blender rather than Blockbench for the main soft, round mascot if this gate
is crossed. Blockbench remains useful for stalls, crates, cookware, and a
deliberately voxel-styled prototype.

### Prototype amendment — live 3D made to look 2D

Further research confirms that the same 3D master can also be rendered live
inside the 2D Godot scene through a transparent, low-resolution `SubViewport`.
An orthographic camera, toon/palette material, stepped 8–12 fps body animation,
one-source-pixel post outline, and nearest-neighbor compositing can make the
model read like authored 2D/pixel art.

This is now a mandatory three-way proof before the cast is generated:

1. existing directional 2D;
2. the 3D master baked to pixel sheets;
3. the same 3D master rendered live in the approved stall composition.

The whole world does not become 3D. If the live version succeeds, it is reserved
for the host/current counter customer; tiny street walkers remain baked. If live
fails but baked succeeds, the 3D master remains the sprite factory.

See `3d-characters-with-2d-pixel-look-prototype.md`.

## Engine and tool decision

### Use now

- **Godot:** 2D runtime, state machine, `AnimatedSprite2D`, audio, props,
  particles, and optional restrained close-up cutout rigs.
- **PixelLab / Retro Diffusion:** identity anchors and directional key art, not
  independently generated animation cels.
- **PixelOver:** deterministic motion blocking and baking.
- **Aseprite:** final pixel authority.

### Defer

- **Spine Professional:** excellent for a large live cutout cast and runtime
  dress-up, but currently expensive and unnecessary. Reconsider only after the
  cast has roughly 20+ compatible characters, multiple outfits per body family,
  or a demonstrated maintenance problem with baked clips.
- **Live 3D Godot characters:** technically possible through a low-resolution
  `SubViewport`; reconsider only if free rotation, procedural posing, dynamic
  lighting, or many modular outfits becomes central.
- **Rive:** no official Godot runtime and a poor match for exact low-resolution
  pixel characters.
- **Creature, DragonBones/LoongBones, Spriter runtime, Live2D:** no current
  production advantage over this stack for Bentosaur.

## Escape condition

Prototype a 3D master character only when at least two of these become true:

1. Characters need free or frequently changing camera angles.
2. Dozens of modular outfits must work without atlas duplication.
3. Procedural posing or animation blending becomes central to the loop.
4. Manual directional cleanup is the measured production bottleneck.
5. Sprite memory or download size becomes a real device-budget problem.
6. Dynamic scene lighting must affect characters accurately.

The present counter-and-street design satisfies none of those conditions.

## Immediate proof

Use the approved upright Triceratops to build one production proof:

1. Lock its side anchor.
2. Generate a front / slight-counter-facing anchor from the same references,
   palette, proportions, anatomy contract, and identity traits.
3. Create a side kit with `walk`, `pause`, and `look`.
4. Create a front kit with `idle`, `blink`, `order`, `receive`, `delight`, and
   `chomp`.
5. Make an umbrella and a bento tray as socketed overlays.
6. Export baked target-resolution sheets.
7. Test at phone scale in Godot.
8. Record cleanup minutes per clip.

Only if this proof shows that directional authoring is the bottleneck should we
spend time building the same character as a Blender master model.

## Sources

- Godot 2D skeletons:
  https://docs.godotengine.org/en/stable/tutorials/animation/2d_skeletons.html
- Godot cutout animation:
  https://docs.godotengine.org/en/stable/tutorials/animation/cutout_animation.html
- Godot `Skeleton2D`:
  https://docs.godotengine.org/en/stable/classes/class_skeleton2d.html
- Godot `AnimationTree`:
  https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html
- Godot sprite animation:
  https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html
- Godot `SubViewport`:
  https://docs.godotengine.org/en/stable/classes/class_subviewport.html
- Godot glTF import:
  https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html
- PixelOver:
  https://pixelover.io/
- PixelOver animation reuse:
  https://docs.pixelover.io/manual/animation/
- PixelOver export:
  https://docs.pixelover.io/manual/export/
- PixelOver 3D:
  https://docs.pixelover.io/tutorials/first_steps3d/
- PixelLab directional characters:
  https://www.pixellab.ai/docs/tools/create-8-rotations-pro
- PixelLab automatic animations:
  https://www.pixellab.ai/docs/tools/create-animations-automatic
- Spine pricing and license:
  https://esotericsoftware.com/spine-purchase
- Spine Godot runtime:
  https://esotericsoftware.com/spine-godot
- Blockbench export formats:
  https://www.blockbench.net/wiki/guides/export-formats/
- Blender glTF:
  https://docs.blender.org/manual/en/3.3/addons/import_export/scene_gltf2.html
