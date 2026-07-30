# Hybrid 3D UI and Animation Ownership

**Status:** Production contract v1  
**Date:** July 29, 2026  
**Runtime hypothesis:** Godot 4.7.1 Standard, typed GDScript, Mobile renderer  
**Canonical DCC:** Blender

## Governing rules

> Blender owns authored performance. Godot owns runtime behavior.

> If it belongs to the place, make it 3D. If it communicates exact
> information, make it screen-space 2D. If it should feel magical and physical,
> let it transition between the two.

These rules also survive a possible Unity switch. Blender remains the
authoritative animation source; only the runtime orchestration changes.

## Where animations live

### Blender owns

- skeleton hierarchy and rest/bind pose;
- deformation bones and skin weights;
- corrective shape keys;
- facial shape definitions or facial bone poses;
- named sockets for hands, tray, umbrella, bento and accessories;
- reusable skeletal performances:
  - `stall_idle`;
  - `street_walk`;
  - `wait`;
  - `request`;
  - `receive`;
  - `eat`;
  - `delight`;
  - `disappointed`;
- foot contacts, loops, silhouettes and performance timing;
- complex mesh deformation;
- hero interactions whose contacts must be precisely art-directed.

The `.blend` masters and action library are authoritative. Exported `.glb`
files are reproducible build artifacts, not the animation source.

### Godot owns

- which animation plays and why;
- state machines and transitions;
- blends, layers, masks and one-shots;
- speed and timing variations;
- interruption rules;
- foreground versus background animation LOD;
- runtime facial-expression selection;
- blink and gaze timing;
- look-at, limited IK and lightweight secondary motion;
- prop attach/detach timing;
- camera, lighting, rain, particles and material changes;
- audio, VFX and haptic synchronization;
- all UI motion and feedback.

Gameplay state initiates an action. An animation event may synchronize a sound,
sparkle or visible handoff, but it must not be the source of gameplay truth.

Example:

1. The order system confirms a successful serve.
2. The customer state enters `receive`.
3. A presentation cue attaches the tray at the authored contact moment.
4. Sound, particles and haptics play.
5. The economy has already recorded the result independently.

### Godot mapping

- Imported GLB actions appear in `AnimationPlayer`.
- `AnimationTree` controls states, transitions, blend spaces and layers.
- `SkeletonModifier3D`-family tools handle selected procedural adjustments.
- `AnimationPlayer`, Tweeners and shaders animate props, environment and UI.
- Custom engine tracks must be externalized or stored in engine-owned resources
  so a GLB reimport cannot erase them.

### Unity equivalent

- Imported FBX clips become `AnimationClip` assets.
- Animator Controllers, Blend Trees, Layers and Avatar Masks control runtime
  composition.
- Animation Rigging handles selected IK and constraints.
- Timeline handles directed sequences.
- UI animation remains in the engine.

Unity's Animation window can edit curves, but reusable character acting should
still remain canonical in Blender.

## Facial animation

Blender defines the available face:

- eyes;
- brows or eye-shape controls;
- cheeks;
- jaw and mouth;
- tongue where needed;
- corrective shapes for extreme delight/eating.

The engine chooses and combines those controls:

- blinking;
- gaze;
- anticipation;
- delight;
- disappointment;
- chewing;
- speech-like reactions;
- friendship-specific expression intensity.

Foreground customers receive the complete face system. Background pedestrians
use a cheaper subset or baked clips.

## Procedural motion

Use procedural animation selectively:

- foreground head/eye look-at;
- small hand-to-prop correction;
- foot grounding on uneven stall/street surfaces;
- restrained tail follow-through;
- small accessory settling.

Do not run every solver on every background dinosaur. Reduce update frequency
or disable procedural systems by distance and importance.

## Environment and prop animation

Model the stall, book, lanterns, shutters, drawers and props in Blender.

Animate in Blender only when deformation or authored performance is important.
Animate these in Godot:

- shutter open/close;
- drawer movement;
- lantern sway and flicker;
- steam intensity;
- rain and snow;
- wetness/material transitions;
- plants reacting to weather;
- simple camera moves;
- light fades;
- stall-opening and stall-closing timing.

## UI production classification

| Element | Production form |
|---|---|
| Stall, street, buildings | Full 3D |
| Dinosaurs | Full 3D |
| Bento, food and ingredient trays | Full 3D |
| Lanterns, plants, utensils, bell | Full 3D |
| Rain, steam, fireflies, comets | 3D/billboard particles |
| Physical customer coin | One reusable 3D model |
| Coin counter and number | Screen-space 2D/2.5D |
| Rating stars and progress | Screen-space 2D/2.5D |
| Order bubble | Screen-space 2D anchored to customer |
| Menus, settings and confirmations | Screen-space 2D |
| Album/book | Hybrid 3D book + 2D page content |
| Character portraits/cards | 2D renders from approved 3D masters |

The UI should look materially related to the world without literally building
every panel, number and button from real-time meshes.

The visual principle is:

> Physical metaphor, digital behavior.

Buttons may resemble clay, enamel, parchment or carved wood, but still receive
large touch targets, crisp text, immediate feedback, disabled states, safe-area
layout and accessibility.

## Reward handoff

Connect the 3D world to the 2D HUD:

```text
customer pays
→ physical 3D coin arcs/bounces on counter
→ coin transitions into screen space
→ icon flies to coin counter
→ counter bumps and increments
```

For satisfaction:

```text
customer reacts
→ world-space sparkle
→ star transitions into screen space
→ progress star fills
```

This provides physical reward without sacrificing exact UI state.

## Gameplay screen layers

1. **World:** street, customer, stall, lighting, weather.
2. **Interaction:** bento, food, trays and bell.
3. **Communication:** order bubble, coins, satisfaction and pause/book.
4. **Feedback:** outlines, crumbs, sparks, sound and haptics.

The order bubble is a `Control` anchored to a projected point above the
customer. It should not be a perspective-distorted 3D speech balloon.

Ingredient trays are full 3D because food placement is the tactile heart of the
loop. Selection should combine:

- warm rim/outline;
- a small squash/scale response;
- ceramic or wooden tap;
- light haptic;
- invisible touch target larger than the visible ingredient.

## Album/book

- Closed book on counter: full 3D prop.
- Tap: camera and book transition toward an intimate close-up.
- Open pages: lightweight 3D meshes.
- Portraits, stamps, text and buttons: 2D UI rendered to the page surfaces.
- Page curl: modest mesh deformation or controlled shader.
- Input: finger position controls curl; distance and release velocity decide
  commit/cancel.
- Finish: authored spring settle, page shadow, paper sound and light haptic.
- Accessibility: previous/next buttons and reduced-motion alternative.

Do not use cloth simulation. The pleasure comes from authored timing, direct
finger response, paper thickness, shadow, sound and settle.

## Godot scene architecture

```text
GameRoot
├── World3D
│   ├── Stall
│   ├── Street
│   ├── CustomerStage
│   ├── BentoInteraction
│   ├── AmbientActors
│   └── Weather
├── Camera3D
├── UI (CanvasLayer)
│   ├── HUD
│   ├── OrderBubble
│   ├── Menus
│   ├── RewardTransitionLayer
│   └── Accessibility
└── BookPresentation
    ├── Book3D
    ├── PageMesh
    └── PageSubViewports
```

The gameplay model publishes events such as `order_changed`, `coin_awarded`,
`rating_changed`, `customer_state_changed` and `book_opened`. The world and UI
respond. Neither contains the canonical economy logic.

## Performance and accessibility

- Activate book `SubViewport`s only while opening or changing a page.
- Freeze page textures once settled.
- Reuse UI atlases and nine-sliced frames.
- Share food and prop materials.
- Avoid blur-heavy translucent overlays and many world-space canvases.
- Pause or reduce off-screen animation.
- Disable expensive procedural solvers for background crowds.
- Provide reduced motion, haptic and screen-shake toggles.
- Never communicate correctness, mood or star state through color alone.
- Pause service timers when a menu or book fully obscures gameplay.

## Anti-patterns

- 3D mesh numbers or menu text.
- A separate real-time mesh for every HUD star or coin.
- Every HUD element in world space.
- Text baked into AI-generated textures.
- Physics-driven primary UI animation.
- Concept art treated as final production layout.
- Unrelated lighting directions between UI renders and the 3D world.
- Generic mobile dashboard cards over the diorama.
- Monetization banners, badges and currencies competing with the serving loop.

## Sources

- [Godot AnimationTree](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html)
- [Godot advanced 3D import settings](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/advanced_import_settings.html)
- [Godot animation track types](https://docs.godotengine.org/en/stable/tutorials/animation/animation_track_types.html)
- [Unity Animation Rigging](https://docs.unity3d.com/ja/current/Manual/com.unity.animation.rigging.html)

