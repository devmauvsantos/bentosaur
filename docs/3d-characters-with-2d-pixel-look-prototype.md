# Live 3D Characters with a 2D / Pixel Look

**Status:** Mandatory prototype branch; not yet a production commitment  
**Decision date:** 2026-07-28  
**Parent decision:** `2d-character-reuse-architecture.md`

## Thesis

Yes: Bentosaur can use fully rigged 3D dinosaurs that visually read as authored
2D or pixel art.

The practical technique is a 2.5D / non-photorealistic-rendering pipeline:

1. Create one stylized 3D dinosaur identity.
2. Rig and animate it once.
3. Render it with a fixed orthographic camera, flat palette bands, deliberately
   stepped animation, and a one-pixel outline.
4. Either display that render live inside the 2D Godot scene or bake it to sprite
   sheets.

The important production decision is therefore not “2D or 3D character.” It is:

> Create the canonical dinosaur as a reusable 3D master, then choose live or
> baked delivery for each use.

That choice can be made per asset without throwing away the model, skeleton,
animations, accessories, or expression work.

## Why this deserves a prototype now

The previous 2D decision correctly observed that a flat side drawing cannot
reveal a front view. A 3D master does contain the missing geometry and therefore
can solve:

- side, front, three-quarter, and back consistency;
- one animation reused from multiple cameras;
- hats, aprons, umbrellas, bags, bowls, and trays attached to bones;
- palette skins without redrawing every frame;
- consistent album portraits and promotional renders;
- a larger cast sharing compatible skeleton and motion libraries.

Bentosaur still does not need a live 3D world. Backgrounds, interaction,
collisions, food, particles, book, and UI can remain 2D.

## Two outputs from one master

### A. Live 3D made to look 2D

Godot renders one or more rigged characters into a transparent, low-resolution
`SubViewport`. A `ViewportTexture` is displayed as a nearest-filtered
`Sprite2D`/`TextureRect` between the 2D background and the 2D counter
foreground.

Advantages:

- arbitrary poses and views at runtime;
- instant outfit/accessory changes;
- smaller animation storage;
- dynamic, reusable prop sockets;
- one master identity from every angle.

Risks:

- plastic or generic 3D appearance;
- pixel crawl from smooth motion or subpixel placement;
- 3D/2D occlusion and lighting mismatch;
- skinning, morph, viewport, outline, and mobile-rendering cost;
- art quality depends on the model and animation, not merely the shader.

### B. 3D master baked to 2D sprites

The same model, skeleton, actions, camera, palette, and expression states render
offline into fixed sprite sheets.

Advantages:

- pure 2D runtime;
- exact reviewed frames;
- stable pixels and predictable mobile performance;
- one 3D source can emit every required direction and costume.

Risks:

- atlas growth;
- re-rendering after source changes;
- hero frames still need Aseprite cleanup;
- fewer runtime view and outfit combinations.

### Recommended split if the prototype succeeds

- Counter customer and host: live 3D is allowed if it passes the art and device
  gates.
- Tiny street walkers: baked from the same 3D masters.
- Album portraits: controlled 3D renders, then hand-polished in Aseprite.
- Promotional art: higher-resolution controlled renders as reference, with
  human paint-over where needed.

## Godot composition

Use one character render target, not one `SubViewport` per dinosaur.

```text
GameplayScreen (Node2D)
├── Background2D
├── CharacterComposite2D
│   └── ViewportTexture from CharacterViewport
├── CounterAndForeground2D
├── Effects2D
├── UI (CanvasLayer)
└── CharacterViewport (SubViewport, 360×640, transparent)
    └── CharacterStage3D (Node3D)
        ├── WorldEnvironment (minimal)
        ├── Camera3D (orthographic, locked)
        ├── DirectionalLight3D (one, fixed, no shadow)
        ├── Host3D
        │   ├── Skeleton3D
        │   ├── MeshInstance3D
        │   ├── AnimationPlayer
        │   └── AnimationTree
        └── CurrentCustomer3D
            ├── Skeleton3D
            ├── MeshInstance3D
            ├── AnimationPlayer
            └── AnimationTree
```

The 360×640 character viewport matches the current source canvas. It is enlarged
only at integer scale using nearest filtering. The 2D foreground counter hides
the character's lower body naturally and preserves the loved ramen-stall
composition.

Use a separate 2D interaction representation. A dragged ingredient can remain a
2D sprite; at the serve event it can swap to a simple matching 3D prop attached
to a hand or tray socket.

## Model design: sculpt the illustration, not a dinosaur

The cel shader cannot rescue a generic model. The master must be built around
the approved Bentosaur silhouette:

- oversized head and frill;
- short muzzle;
- large, widely readable horns;
- round cheeks;
- tiny raised torso;
- short forearms used as hands;
- two planted hind legs;
- thick balancing tail;
- soft rounded planes without realistic scale detail.

The topology should support silhouette changes and clean deformation, not
anatomical realism.

### Camera-dependent cheats

A physically honest mesh may be adorable in profile and weak from the front.
Use corrective shape keys such as:

- `front_eye_spread`;
- `front_cheek_width`;
- `front_horn_separation`;
- `front_frill_roundness`;
- `side_snout_short`;
- `side_belly_silhouette`.

These reproduce what a 2D illustrator does naturally: redraw proportions for
the chosen view. They can be toggled for the counter camera or applied during
offline directional rendering.

## Face system

Do not paint one fixed face onto a spherical head.

Use small opaque face patches, a texture atlas, or discrete mesh states for:

- neutral;
- blink;
- speaking/order;
- waiting;
- delight;
- disappointment;
- chomp.

Use shape keys only for the cheek, lid, jaw, and mouth volume changes that
benefit from real deformation. The eyes and mouth should continue to behave like
authored 2D graphics.

## Rendering recipe

### Camera

- Fixed orthographic projection.
- Fixed elevation and framing per scene.
- No perspective breathing or camera drift.
- Snap projected root placement to the source-pixel grid.

### Material and palette

- Bentosaur's declared limited palette, not a generic PBR texture.
- Two to four hard light bands.
- Fixed upper-left warm key direction.
- Specular disabled; high roughness if StandardMaterial is used.
- No environment reflections, GI, or realistic normal maps.
- Prefer vertex colors or small flat nearest-filtered textures.
- Use painted/unshaded lighting if toon lighting does not remain stable.

### Outline

Start with a one-source-pixel silhouette outline applied after the character
viewport is rendered. Use deep brown/indigo rather than black.

A final-resolution alpha-neighborhood outline is preferred for the proof
because its thickness is deterministic. Inverted-hull or stencil outlines remain
available if internal 3D contours prove necessary.

### Pixel treatment

- Render at the actual logical/source resolution.
- Nearest-neighbor enlargement only.
- Optional 24-color palette quantization after the 3D render.
- Optional restrained ordered dithering only where the design system permits.
- No TAA, FXAA, FSR, motion blur, depth of field, bloom, or soft antialiasing.
- Leave transparent padding around the model.
- Use premultiplied-alpha compositing if edge color bleed appears.

Low-resolution 3D is pixelated but not automatically pixel-stable. Camera,
light, root placement, and animation sampling must be deterministic.

## Animation recipe

Animate like limited 2D animation:

- authored key poses;
- constant/stepped interpolation for body acting;
- visible pose changes at 8–12 fps;
- game logic and whole-character travel may remain 60 fps when visually stable;
- deliberate anticipation, holds, overshoot, and settle;
- two- or three-frame blinks;
- no generic continuous spline wobble;
- no automatic animation blending unless the blend itself passes the pixel
  stability test.

Required first actions:

- `walk`;
- `stall_idle`;
- `order`;
- `receive`;
- `delight`;
- `chomp`.

## Creating the master with AI assistance

### Reference preparation

Create a clean high-resolution turnaround of the approved identity:

1. front A-pose;
2. side A-pose;
3. back A-pose;
4. optional three-quarter A-pose.

Every view must share anatomy, proportions, palette placement, horns, frill,
hands, feet, and tail. Pixel-size game sprites are references for identity but
are too information-poor to be the only modeling inputs.

### Tripo + first-party Blender MCP amendment

Further research on July 29, 2026 identified a stronger controlled prototype
path:

- Tripo P1 and H3.1 can be compared from the same four-view turnaround;
- Tripo CLI/API is the repeatable orchestration surface;
- Blender 5.1.2 already has the official Blender Lab MCP 1.0.0 extension
  installed locally;
- Blender remains the source of truth and Godot remains the runtime proof.

The Tripo test deliberately generates two bare 5,000-face candidates, selects
one mesh before spending credits on rigging, then tests only idle, walk, and
turn as diagnostic motion. It does not outsource Bentosaur's face, service
acting, palette, tail/frill rig, or final topology.

See `tripo-blender-character-master-pipeline.md` and
`art/jobs/tripo-blender-character-master-bakeoff-v1.json`.

### AI mesh proposal

Meshy currently exposes text/image/multi-image-to-3D, remeshing, rigging,
animation, GLB/FBX export, REST API, and an official MCP server. Its multi-image
API accepts one to four views and can request A/T-pose output, lighting removal,
remeshing, target polycount, and GLB.

Recommended experimental request:

- multi-image rather than single-image;
- A-pose;
- lighting removal enabled;
- no PBR maps unless needed as a temporary source;
- a modest real-time poly target;
- GLB output;
- preserve the raw and remeshed models for comparison.

Treat the result as a model proposal, not a shipping asset.

Meshy's API documentation says programmatic auto-rigging currently works best
with standard humanoid bipeds with clearly defined limbs. Bentosaur's upright
body may pass that gate, but the tail, frill, horns, proportions, face, and
corrective shapes will still require Blender work.

### Blender authority

Blender remains the source of truth for:

- topology and silhouette cleanup;
- UV/vertex-color cleanup;
- skeleton convention;
- skin weights;
- tail and frill bones;
- corrective shape keys;
- face atlas or expression patches;
- animation actions;
- orthographic cameras;
- live GLB export;
- repeatable batch sprite rendering.

The Blender file is reusable whether the final runtime path is live or baked.

## Mobile constraints

Initial target:

- one shared low-resolution transparent character viewport;
- one or two live foreground skinned actors;
- low/mid-poly opaque meshes;
- one or two materials per character;
- one fixed unshadowed light, or unshaded palette materials;
- no GI, realtime shadows, reflections, volumetric effects, or costly
  post-processing;
- background crowd baked to sprites;
- pause hidden actors and disable viewport updates when not visible.

Begin with the Compatibility renderer because the technique needs only core 3D
features and widest device support. Benchmark Compatibility against Mobile/Metal
on real devices before locking the renderer.

## No-throwaway proof

Create one canonical upright Triceratops and produce all three comparison paths:

### A — Existing pure 2D

The approved PixelLab/Retro/Aseprite character pipeline.

### B — Baked 3D master

The Triceratops GLB rendered into 64/96 px sheets and cleaned in Aseprite.

The audited production hypothesis is now more precise:

- render each target size natively; never validate 64 px by shrinking 96 px;
- use exact `stall_front`, optional authored `stall_3q`, and `street_side`
  orthographic camera profiles instead of an automatic eight-direction batch;
- lock `Standard` color management, dither `0`, transparent PNG, filter width
  `0`, nearest sampling, and antialiasing off;
- emit color, silhouette, material-ID, and optional camera-normal passes;
- create a separate 32/48 px silhouette LOD for walkers;
- finish hero frames and flicker repair in Aseprite;
- ship ordinary Godot sprites plus a versioned JSON manifest.

See `3d-to-2d-pixel-sprite-factory-research-v1.md` for the tutorial, download,
script, companion-resource, licensing, and acceptance audit.

### C — Live 3D made to look 2D

The same GLB rendered in the 360×640 transparent Godot character viewport and
composited into the exact approved stall screen.

Test:

- side walk;
- front/counter idle;
- order;
- receive;
- delight;
- chomp;
- one apron;
- one umbrella;
- one bento tray.

## Acceptance gate

The 3D branch advances only when:

1. The still silhouette and face preserve the loved concept at phone scale.
2. It does not read as “plastic 3D with a pixel filter.”
3. Front and side views both score at least 4/5 for identity and cuteness.
4. Horns, frill, hands, feet, and tail remain readable during motion.
5. Pixel crawl is unobtrusive with the fixed camera and stepped timing.
6. Live compositing respects the counter, props, particles, and 2D lighting.
7. The oldest target phone maintains the total 60 fps frame budget.
8. The character layer adds no more than 2 ms average and 3 ms p95 GPU time on
   the lowest target device.
9. Baked output needs no more cleanup per clip than the accepted 2D pipeline.
10. A new palette skin or apron demonstrably reuses the model without full-sheet
    re-authoring.

If live fails but baked succeeds, keep the 3D master as the sprite factory. If
both fail the emotional-readability gate, return to directional 2D kits.

## Decision

This discovery does not justify converting the whole game to 3D. It does justify
testing a canonical 3D dinosaur now, before the cast is generated.

The current preferred hypothesis is:

> 2D game and world, 3D-authored dinosaur identities, baked tiny walkers, and
> live toon/pixel counter characters only if the A/B test proves they preserve
> Bentosaur's heart.

## Sources

- Godot official 3D-in-2D demo:
  https://github.com/godotengine/godot-demo-projects/tree/master/viewport/3d_in_2d
- Godot `SubViewport`:
  https://docs.godotengine.org/en/stable/classes/class_subviewport.html
- Godot `ViewportTexture`:
  https://docs.godotengine.org/en/stable/classes/class_viewporttexture.html
- Godot `Camera3D` orthographic projection:
  https://docs.godotengine.org/en/stable/classes/class_camera3d.html
- Godot spatial toon/unshaded modes:
  https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/spatial_shader.html
- Godot renderer comparison:
  https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html
- Godot 3D performance:
  https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html
- Godot glTF import:
  https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html
- Arc System Works: Guilty Gear Xrd 2D/3D GDC talk:
  https://www.arcsystemworks.com/guilty-gear-xrds-art-style-the-x-factor-between-2d-and-3d-talk-from-gdc-2015-is-now-available-online/
- Blender constant key interpolation:
  https://docs.blender.org/manual/en/4.5/editors/graph_editor/fcurves/properties.html
- Blender shape keys:
  https://docs.blender.org/manual/en/latest/animation/shape_keys/introduction.html
- Meshy multi-image-to-3D:
  https://docs.meshy.ai/en/api/multi-image-to-3d
- Meshy rigging limits:
  https://docs.meshy.ai/en/api/rigging
- Meshy AI/MCP integration:
  https://docs.meshy.ai/en/api/ai
