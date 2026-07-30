# 2D Flat-Cel Production Feasibility 01

**Status:** Research; bounded contingency proof  
**Date:** July 30, 2026  
**Founder signal:** the flat-cel candidate feels more possible  
**Production approval:** None  
**Engine decision changed:** No  
**Tripo credits used:** 0  
**Generation tool:** built-in ImageGen

## Decision at this checkpoint

Use the following image as the only candidate for a real 2D production proof:

`art/concepts/2d-chibi/v1/01_generated-exploration/bentosaur-gameplay-2d-flat-cel-v2.png`

The painted gameplay, hub, and album screens remain useful mood evidence, but
they are not the recommended asset-production style. Their dense painted
shading would turn every new pose and seasonal variation into a repainting
task.

Do not generate the flat-cel hub or album yet. First prove that one character
can be rebuilt as authored layers, rigged, animated, and displayed in Godot
without losing the silhouette or emotional appeal.

This proof does not silently replace the live-3D engine lock. It evaluates the
documented baked-2D contingency with a style that was not available when the
lock was written.

## The generated screenshot is not an asset pack

The candidate is one flattened raster image. It cannot be shipped by cropping
the customer, food, UI, and street out of the screenshot:

- hidden joint areas do not exist;
- overlapping objects have missing pixels behind them;
- lighting and shadows are baked together;
- the character has no pivots, bones, attachment sockets, or face slots;
- UI numbers and icons are not real controls;
- the street is not split into parallax or seasonal layers.

The screenshot is a visual target. Production assets must be reconstructed
individually.

## Production asset architecture

### Front counter rig

Author one neutral front-facing master with deliberate hidden overlap at every
joint.

```text
customer_front
├── shadow
├── tail_back
├── leg_back_left
├── leg_back_right
├── body
├── belly_patch
├── arm_left
├── arm_right
├── hand_left
├── hand_right
├── head_and_frill
├── eye_left_slot
├── eye_right_slot
├── mouth_slot
├── cheek_left
├── cheek_right
├── front_highlight
├── hand_socket_left
├── hand_socket_right
└── prop_socket_center
```

Keep the horns and frill knobs in `head_and_frill` unless a shipped animation
requires them to move. Fewer pieces preserve the mascot's silhouette.

Required face attachments:

```text
eyes: open, blink, happy, surprised, disappointed
mouths: neutral, small_talk, open_smile, chew_a, chew_b, disappointed
hands: relaxed, cheek, receive, hold_food
```

Every rotating or deforming piece needs painted bleed beneath its neighbor.
The overlap must survive the maximum approved pose without revealing a gap.

### Side street rig

Author east once and mirror the outer visual root for west:

```text
customer_side
├── shadow
├── tail_base
├── tail_tip
├── leg_far
├── arm_far
├── body
├── belly_patch
├── head_and_frill
├── eye_slot
├── leg_near
├── arm_near
├── hand_socket
└── accessory_socket
```

An explicit west kit is needed only for asymmetric accessories or actions.

### Portrait kit

The album portrait is not a crop of the runtime customer. Reuse the approved
identity and face vocabulary, then author one higher-detail bust or full-body
portrait master with the same palette.

### Environment layers

```text
stall_gameplay
├── far_sky
├── far_buildings
├── far_lanterns
├── street_walkers_back
├── middle_buildings
├── street_and_puddles
├── street_walkers_front
├── rain_back
├── steam_and_mist
├── stall_frame
├── customer
├── counter_props
├── counter
├── bento
├── ingredient_bins
├── rain_front
└── HUD
```

Rain, snow, steam, lantern flicker, puddle ripples, spring petals, and autumn
leaves should be deterministic Godot particles, shaders, or short loop assets.
Do not regenerate an entire background for every weather state.

Season packs modify small authored layers:

- roof and curb overlays;
- plants and ground dressing;
- lantern or awning color accents;
- weather particles;
- a restrained background palette grade.

### Food, props, and UI

- Author food and props as isolated masters with a shared outline, shadow, and
  highlight contract.
- Use one reusable selected-state outline/glow rather than a second generated
  image for every ingredient.
- Build counters, labels, progress, and touch behavior as real Godot `Control`
  nodes.
- Use nine-slice frames and separate icons. Never bake changing numbers into
  the screen artwork.

### Book

The 2D album needs one reusable construction:

```text
album
├── cover_and_binding
├── left_page_base
├── right_page_base
├── dynamic_left_content
├── dynamic_right_content
├── turning_page_front
├── turning_page_underside
├── turning_page_shadow
└── screen_space_controls
```

Customer portraits, hearts, memories, discovery slots, and page numbers come
from data. The page turn is a deformable `Polygon2D`/mesh plus authored shadow
and settle animation, not a separate full-screen render for every spread.

## Generation and cleanup pipeline

```text
approved concept and identity references
→ isolated front and side key art
→ editable vector/layer reconstruction
→ manual silhouette, palette, overlap, and pivot cleanup
→ stable front and side layer kits
→ Godot cutout/mesh rig
→ face, hand, and contact sprite attachments
→ authored animation clips
→ phone-scale visual and performance gate
→ only then generate the rest of the cast and screens
```

### AI may do

- concept screens and composition variants;
- isolated prop and food proposals;
- front/side key-pose proposals from the locked identity;
- controlled expression references;
- style-model training after a real approved asset set exists;
- vector-conversion or shape-fill assistance that remains fully editable.

### AI must not own

- final character topology/layer boundaries;
- hidden overlap art at joints;
- pivots, bone hierarchy, weights, sockets, or naming;
- final animation timing and loop continuity;
- independently generated animation frames;
- UI text, gameplay state, hit targets, or safe areas;
- human visual approval.

AI video is useful for motion reference only. It does not provide stable game
layers, transparent loops, repeatable topology, sockets, or deterministic
frame identity.

## Tool choice

### Use for the first proof

1. **Built-in ImageGen:** concepts, isolated key-pose proposals, and expression
   reference only.
2. **Adobe Illustrator or equivalent vector editor:** convert the approved
   raster direction into editable paths, then manually simplify and layer it.
   Illustrator's current Concept to Vector and Generative Shape Fill features
   can accelerate this, but generated vectors still require cleanup.
3. **Godot 4.7.1:** first rig, clips, state machine, FX, UI, and device proof.
   Godot supports cutout animation, sprite attachments, `Skeleton2D`,
   `Bone2D`, weighted `Polygon2D`, `AnimationPlayer`, and mixed cel/cutout
   animation.

### Escalate only if the Godot authoring proof hurts

Use **Spine Professional** if mesh deformation, curve editing, reusable skins,
or animation authoring is materially faster there. The official Spine
runtimes repository includes `spine-godot`. Spine Essential lacks meshes and
other advanced features, so it is not the relevant tier for this character.

Do not purchase Spine before the free Godot proof identifies an actual
authoring problem.

### Useful later

- **Scenario:** train one Bentosaur style model only after a cleaned set of
  approved characters, props, food, and environment pieces exists. Use it to
  propose consistent assets, not to manufacture rigged animations.
- **Recraft:** useful as an alternate vector/SVG proposal and icon generator.
  Final layer and silhouette authority still belongs to the editable master.

### Poor fits for this selected style

- **PixelLab and Retro Diffusion:** strong pixel-art tools. PixelLab's current
  animation API creates pixel animation at bounded pixel resolutions. Using
  either tool as the main authoring path would pull this candidate back toward
  actual pixel art.
- **Rive:** excellent interactive vector animation, but its official game
  runtime list currently names Unity, Unreal, and Defold rather than Godot.
- **Substance 3D Painter:** not part of a flat-cel 2D asset pipeline.

## Animation ownership

| Motion | Production method |
| --- | --- |
| Counter breathing and sway | Front cutout rig |
| Blink and happy eyes | Face attachment swaps |
| Talk and order | Mouth swaps plus subtle head/hand curves |
| Delight | Front rig plus cheek-hands and open-smile attachments |
| Chew | Two or three mouth attachments plus head/body timing |
| Receive food | Front rig, hand attachment, prop socket |
| Street walk | Side rig; mirror for opposite direction |
| Pause and look around | Side rig plus eye/head variation |
| Rain, snow, steam, petals, leaves | Godot FX |
| Lantern flicker and puddle ripple | Godot shader/animation |
| Ingredient select and drop | Godot tween, outline, squash, particles |
| Book page turn | Reusable 2D page mesh, shadow, and spring settle |

The recommended style is hybrid cutout/cel animation. Bones provide continuity;
replacement drawings preserve expressive hands, faces, contacts, and strong
silhouette changes.

## One-character proof gate

### Build only

- one standalone front layered master;
- one standalone side layered master;
- one Godot character scene with stable semantic node names;
- `front_idle`;
- randomized blink;
- `front_delight`;
- `front_chew`;
- `side_walk`;
- east/west mirroring;
- one separate bento or ingredient attached through a socket;
- one small scene containing the counter customer and several phase-shifted
  background walkers.

### Pass only if

- Mau approves the identity at gameplay scale;
- the silhouette still feels soft and chibi rather than like a paper puppet;
- no gaps or sliding seams appear at the arms, legs, head, or tail;
- eyes and mouth remain crisp during motion;
- side-walk mirroring is visually acceptable;
- animation curves can be reused on a second palette/species test;
- the phone build meets the existing frame-time and thermal gates;
- measured cleanup time is acceptable for a solo production pipeline.

### Stop and reconsider if

- one front or side kit requires repeated full repainting;
- joint cleanup cannot be solved with bounded overlap and replacement parts;
- the result only looks good when every action is frame-by-frame;
- a second character cannot reuse the rig and animation semantics;
- the 2D result loses the emotional appeal that motivated the exploration.

## What happens after a pass

1. Lock the flat-cel palette, outlines, shadow shapes, highlights, and texture.
2. Generate and reconstruct the flat-cel hub and album.
3. Create one shared UI icon and nine-slice kit.
4. Build the season/weather layer contract.
5. Produce the first three customer identities against the same front/side
   rig contracts.
6. Compare the measured 2D production cost against the paused 3D character
   pipeline before changing `docs/engine-lock.json`.

## Current recommendation

The flat-cel route is plausible enough to deserve one real rig proof. It is not
yet evidence that 2D is cheaper than finishing one reusable 3D master.

The correct next artifact is an animated character, not another full-screen
concept.

## Current sources

- Godot cutout animation:
  https://docs.godotengine.org/en/stable/tutorials/animation/cutout_animation.html
- Godot 2D skeletons:
  https://docs.godotengine.org/en/stable/tutorials/animation/2d_skeletons.html
- Godot 2D sprite animation:
  https://docs.godotengine.org/en/4.5/tutorials/2d/2d_sprite_animation.html
- Spine runtimes, including `spine-godot`:
  https://github.com/EsotericSoftware/spine-runtimes
- Spine pricing and feature tiers:
  https://esotericsoftware.com/spine-purchase
- Adobe Illustrator generative-vector overview:
  https://helpx.adobe.com/illustrator/desktop/use-generative-ai/generative-ai-faq-illustrator.html
- Adobe Illustrator Concept to Vector:
  https://helpx.adobe.com/illustrator/desktop/use-generative-ai/generate-vector-artwork-from-images.html
- PixelLab API:
  https://api.pixellab.ai/
- Scenario model training:
  https://help.scenario.com/articles/5151772792-basics-of-model-training
- Rive game runtimes:
  https://rive.app/docs/game-runtimes/game-runtimes/game-runtimes

