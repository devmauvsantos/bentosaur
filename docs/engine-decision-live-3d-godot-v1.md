# Engine Decision Record — Godot 4.7.1 Locked

**Decision date:** July 29, 2026  
**Status:** Locked for Bentosaur production  
**Final stack:** Godot 4.7.1 Standard, typed GDScript, Mobile renderer  
**Asset authority:** Blender masters exported as deterministic GLB  
**Emergency runtime fallback:** Bake the same Blender assets to 2D sprites

## Decision

Use **Godot 4.7.1 as Bentosaur's production engine** and **3D as Bentosaur's
asset source of truth**. Build the live 3D chibi diorama in Godot with typed
GDScript and the Mobile renderer.

This is the final engine selection, not another comparison round. The expensive work—approved
models, topology, UVs, materials, shared skeleton families, skinning, facial
controls, prop sockets, and reusable animation clips—must remain
engine-neutral in Blender. If live 3D fails the visual or mobile-device gate,
the same approved masters can be rendered into 2D sprite atlases without
discarding the character investment.

Unity is an emergency escape path, not an active alternative. It receives no
parallel prototype and no further evaluation unless the Godot production slice
finds a reproducible engine-specific blocker or the commercial service
requirements change materially.

## Why Godot still fits the 3D version

Bentosaur is a favorable mobile 3D workload:

- a fixed orthographic or very-low-FOV camera;
- a compact stall and short visible street rather than an open world;
- a limited number of visible characters;
- stylized opaque materials and deliberately simple geometry;
- short reusable reactions, walks, and service animations;
- UI-heavy play with 3D characters and environments behind it;
- data-driven content and an AI/MCP-authored project.

Godot's recommended GLB pipeline keeps Tripo → Blender → engine relatively
clean. `AnimationPlayer` and `AnimationTree` cover state machines, blend spaces,
one-shots, and root motion. Custom skeleton profiles and retargeting tools allow
the project to define Bentosaur-specific biped rigs rather than pretending every
dinosaur is a standard human.

Godot's text-based scenes and resources are also unusually useful for a
one-prompt production experiment: code and scene wiring can be generated,
diffed, tested, and repaired without making binary editor state the canonical
source.

## Correction to the 3D intuition

"A 3D character means we never recreate animations" is only partly true.

3D moves work from drawing every pose into:

- clean topology and UVs;
- coherent materials and textures;
- skeleton design and skin weights;
- facial controls;
- reusable animation clips;
- attachment sockets;
- retargeting cleanup;
- LOD, shader, lighting, memory, and thermal optimization.

After that gate, the user's intuition becomes correct: new camera angles,
lighting conditions, seasons, accessories, prop combinations, poses, and
expression/camera combinations become much cheaper than frame-by-frame 2D.

The same reuse advantage also exists in a 3D-to-2D sprite factory. Live 3D's
additional advantage is that it removes per-view rendering, cleanup, atlas
packing, and QA while permitting arbitrary runtime combinations.

## Bentosaur break-even heuristic

This is a production heuristic, not an industry benchmark.

Live 3D is likely to become cheaper over Bentosaur's lifetime when any two or
three of these are true:

1. Eight to twelve customer bodies share one or two skeleton families.
2. Six or more motions/reactions are reused per customer.
3. More than two views are needed: front, side, three-quarter, album, or photo.
4. Held props and accessories change independently.
5. Seasons, weather, and time of day relight the same world.

Bentosaur already wants a living street, many dinosaurs, front and side views,
expressions, separate props, album poses, and seasonal relighting. It likely
crosses this threshold.

For scale, twelve dinosaurs × two views × six clips × eight sampled frames can
produce 1,152 sprite images to render and inspect. Live 3D replaces that
per-frame inventory with twelve approved skins and shared clip libraries. The
saving disappears if every dinosaur receives a unique skeleton and bespoke
animations, so the shared skeleton contract is mandatory.

## Pinned architecture for the proof

- Godot 4.7.1 Standard
- typed GDScript for gameplay
- Mobile renderer on target devices
- Compatibility renderer retained only as a low-end fallback investigation
- no Forward+ on mobile
- fixed orthographic or very-low-FOV `Camera3D`
- one shadow-casting key light
- baked or faked ambient/window/lantern lighting
- opaque matte/toon materials first
- baked ambient occlusion where useful
- static or instanced diorama geometry
- visibility ranges/LODs or impostors for distant actors
- throttled animation updates for background dinosaurs
- `CanvasLayer`/`Control` for HUD and book UI
- a small 3D page mesh, `SubViewport`, or UI shader for the physical page turn
- Blender as canonical art, rig, and animation source
- deterministic GLB as the engine boundary
- JSON for customers, orders, seasons, economy, and spawn behaviors

Swift and Objective-C remain valuable for thin iOS plugins and StoreKit/vendor
bridges. They should not become the gameplay language. C# should not be used for
this Godot mobile project because GDScript is the first-class export path and
Godot's mobile C# support remains a weaker choice.

## Mandatory character contract

No placeholder capsule can validate this decision. The proof starts only after
the user approves one fully surfaced character.

The canonical character must have:

- approved front, side, back, and three-quarter appearance;
- separate character and prop meshes;
- no permanently fused umbrella, tray, bento, clothing, or accessory;
- one named shared skeleton family;
- production skin weights;
- tail, jaw, cheek/face, and hand/paw behavior;
- a defined expression method: bones, blend shapes, or controlled texture swaps;
- named hand and accessory sockets;
- four first clips: `stall_idle`, `street_walk`, `delight`, and
  `receive_or_eat`.

The user remains the visual approval gate. Rigging and animation quality do not
override an unapproved model.

## Minimum Godot proof

Build one narrow vertical slice:

1. One fully surfaced, user-approved Triceratops GLB.
2. The four named animation clips.
3. Separate tray, bento, and umbrella props attached through named sockets.
4. One fixed vertical stall camera and one short street view.
5. Stall, counter, floor, lanterns, one shadowed key light, and baked/static fill.
6. Eight to twelve instanced background dinosaurs with randomized idle offsets.
7. Rain and snow toggles plus one seasonal material/prop swap.
8. One complete loop: approach → request → serve → react → coin → leave.
9. One draggable book page turn in the real UI layer.
10. Release builds on one physical iPhone and one representative Android phone.

Record frame time, memory, cold start, build size, and ten-minute thermal
behavior.

## Pass gates

- The user approves the close-up and front/side/three-quarter character read.
- Blender edit → GLB export → Godot refresh takes under ten minutes and does not
  require repaired node, material, bone, socket, or animation names.
- The four clips have no collapse, unacceptable foot sliding, horn/tail
  clipping, or broken prop sockets.
- The representative phone sustains 60 FPS with ten dinosaurs and weather.
- The declared floor device sustains a stable 30 FPS without unacceptable
  heating after ten minutes.
- The frame budgets are treated literally: 16.7 ms for 60 FPS and 33.3 ms for
  30 FPS.
- MCP-generated scene wiring and JSON updates never modify canonical binary art.

## When Unity becomes the right answer

Rebuild only the same proof in Unity 6 LTS with URP Forward when one of these is
demonstrated:

- animation retargeting across three approved dinosaur species requires more
  than roughly one workday of manual repair per species in Godot and works
  materially better in Unity;
- the release scope requires ads mediation, cloud economy/save, remote config,
  segmentation, A/B testing, and analytics at version 1;
- the equivalent on-device scene misses its frame-time, memory, or thermal gate
  in Godot after one focused optimization pass but passes in URP;
- a maintained Unity package replaces four or more weeks of bespoke animation,
  camera, shader, or live-operations engineering;
- hiring, outsourcing, or a new platform target materially favors Unity.

Do not switch because the game is 3D, the book needs a satisfying page curl, the
street has rain and seasons, accessories are separate, or the cast needs many
camera angles. Godot can handle those requirements.

## Current conclusion

**Commit now to 3D-authoritative production. Prototype live 3D in Godot. Keep
the Blender-to-sprite route alive as the reversible fallback.**

The next real decision is not 2D versus 3D in the abstract. It is whether one
approved production character and one real stall loop retain the concept art's
heart while meeting the physical-device gate.

## Primary sources

- [Godot 4.7.1 maintenance release](https://godotengine.org/article/maintenance-release-godot-4-7-1/)
- [Godot renderer comparison](https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html)
- [Godot 3D scene formats and GLB guidance](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html)
- [Godot skeleton retargeting](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html)
- [Godot AnimationTree](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html)
- [Godot Android billing](https://docs.godotengine.org/en/stable/tutorials/platform/android/android_in_app_purchases.html)
- [Godot license](https://godotengine.org/license/)
- [Unity URP rendering-path comparison](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/rendering-paths-comparison.html)
- [Unity Animation Rigging](https://docs.unity3d.com/Manual/com.unity.animation.rigging.html)
- [Unity IAP](https://docs.unity.com/en-us/iap)
- [Unity services concepts](https://docs.unity.com/en-us/services/key-concepts)
- [Unity pricing](https://unity.com/products/pricing-updates)
