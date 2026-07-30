# 3D-to-2D Pixel Sprite Factory — Tutorial Audit and Bentosaur Plan

**Status:** Research complete; proof is blocked on the user's visual approval of
one fully surfaced character  
**Decision date:** July 29, 2026  
**Related decision:** `3d-characters-with-2d-pixel-look-prototype.md`  
**Machine-readable proof:** `art/jobs/bentosaur-sprite-factory-proof-v1.json`

## Decision

Adopt the linked Blender method as the basis of Bentosaur's **baked 3D-master
prototype**.

This is not a one-click pixel filter and it is not a reason to make the game a
live 3D game. It is an offline character factory:

```text
approved 3D master
→ fixed orthographic cameras
→ native-resolution palette renders
→ stepped animation frames
→ optional camera-normal pass
→ Aseprite pixel cleanup
→ color/normal sheets + JSON manifest
→ ordinary 2D Godot runtime
```

The route is valuable because one approved mesh, rig, face system, and action
library can produce the front-facing stall customer, side walkers, album
portraits, retakes, and later accessory variants without asking an image model
to reinvent the dinosaur in every frame.

It does **not** remove the need for pixel-art judgment. Silhouette, cluster
shape, flicker, outline gaps, and hero-frame cleanup remain authored work.

## Source reviewed

The primary source is KitagawaGameDev's
[How To Make Pixel Art In Blender — The Complete Guide](https://www.youtube.com/watch?v=PBIPJdEECWg),
published October 3, 2025.

The full video, description, chapter sequence, automatic transcript, linked
render script, linked starter file, and three companion videos were reviewed.
The downloaded files were treated as untrusted and inspected with Blender
auto-execution disabled.

### What the video actually demonstrates

1. Render at the intended native sprite size. The example uses 128×128.
2. Set Blender's render pixel filter width to zero.
3. Add a compositor-only pixel preview by scaling down with Nearest, inserting
   a zero-effect Exposure node, and scaling back up with Nearest.
4. Use a locked orthographic camera parented to an Empty.
5. Model for the target sprite silhouette: broad forms, intentional planes, and
   no essential subpixel features.
6. Build silhouette outlines from alpha dilation or repair them in Aseprite.
7. Choose palette highlight and shadow cells manually instead of relying on
   realistic light.
8. Use Blender's `Standard` view transform so palette colors survive export.
9. Animate with a small number of strong, stepped poses at a low frame rate.
10. Rotate one rooted character only through the directions the game needs.
11. Render a second camera-space normal pass with Workbench's
    `check_normal+y.exr` MatCap and antialiasing disabled.
12. Import the frames into Aseprite, remove jaggies and flicker, export normals
    before indexing the color layer, and produce sheets by rows.

The zero-effect Exposure node in the preview path is intentional. It prevents
Blender from combining the inverse scale operations and optimizing the visible
pixelation away. The final Composite output should receive the untouched render;
the branch exists only for live authoring preview.

### Companion-resource findings

#### Canvas size

[Adam C. Younis's resolution lesson](https://www.youtube.com/watch?v=upEGBGCiWEw)
reinforces choosing the logical resolution before drawing or rendering and
scaling by integer multiples. A portrait 360×640 Bentosaur canvas scales exactly
to 720×1280 and 1080×1920.

That does not mean every character must be a 360×640 render. Each isolated
sprite profile receives its own native cell size:

- counter customer proof: native 96 px and 64 px variants;
- street walker: native 48 px and, only if still readable, 32 px;
- album portrait: native 192 px or 256 px;
- no 96→64 or 48→32 downscale is accepted as evidence.

#### Outlines

[Levi Magony's outline survey](https://www.youtube.com/watch?v=cnQu1kMs49s)
confirms that the Alpha Over + Dilate/Erode compositor method creates a
deterministic outer silhouette but has overlap and interior-line limitations.

For Bentosaur:

- generate the outer one-source-pixel edge at the final target size;
- keep eyes, mouth, horn separations, arm/belly gaps, and frill gaps as authored
  material or geometry decisions;
- let Aseprite be the final authority when the outline bridges small gaps;
- do not begin with inverted-hull or Line Art outlines for tiny baked sprites.

#### Gradient texturing

[Moltenbolt's gradient-texturing lesson](https://www.youtube.com/watch?v=9ITJgW9hVrE)
projects low-poly faces onto a tiny light-to-dark palette atlas. The linked
[mobile gradient-texturing analysis](https://itch.io/blog/797457/optimization-of-3d-texturing-for-mobile-games-definition-of-the-gradient-texturing-process-and-analysis-of-its-efficiency-and-performance-in-engine)
recommends point filtering, lossless PNG, shared atlases, and careful art
direction, but also notes that the workflow becomes less convenient for complex
rigged characters.

Use the technique for stalls, bowls, lanterns, signs, and other shared props.
For the deforming dinosaur master, begin with flat material IDs or vertex
colors plus two to four deliberately chosen value bands. A baked sprite receives
no runtime optimization benefit from complicated gradient-atlas UVs.

## Starter `.blend` audit

The description links a Google Drive file called `pixel_setup.blend`.

| Property | Inspected value |
|---|---|
| Size | 990,824 bytes |
| SHA-256 | `4237da1b3fc49cac380d17aeebdebbcb8d4569a69cf92c27d0b141e95d061e55` |
| Saved version | Blender 4.2 series |
| Local inspection runtime | Blender 5.1.2 |
| Embedded Text/Python blocks | None |
| Engine | Eevee |
| Output | 128×128, PNG RGBA, 8-bit |
| Timeline | 1–24 at 12 fps |
| Render pixel filter | 0 |
| Camera | Orthographic, scale 6, parented to an Empty |
| Preview branch | 0.25× Nearest → Exposure 0 → 4× Nearest |
| Workbench AA | Viewport and render off |
| Normal MatCap | `check_normal+y.exr` |

The file is a useful learning specimen, not a production template. Its saved
state has important differences from the tutorial:

- view transform is `AgX`, while the video explicitly calls for `Standard`;
- dither is `1.0`, which can create extra near-colors;
- Film Transparent is disabled;
- the downloaded file has no outline node chain;
- output path is the generic `/tmp/`;
- the old live-preview node arrangement is not a stable cross-version contract.

The Bentosaur template must explicitly force `Standard`, dither `0`, PNG RGBA,
transparent film, filter width `0`, nearest sampling, and the selected engine's
antialiasing off. PNG compression is lossless; palette drift should be diagnosed
in tone mapping, dithering, filtering, materials, and lighting rather than
blamed on PNG compression.

The starter rendered successfully under the installed Blender 5.1.2 with
auto-execution disabled. Its default AgX/dither/background state produced 24
unique RGBA colors in the trivial three-color cube scene. Without saving or
altering the source file, forcing `Standard`, dither `0`, and transparent film
produced exactly four unique RGBA values: three visible face colors plus
transparent background. This directly validates the corrected color contract.

The final native-resolution render does not depend on the compositor preview
trick. If the Blender 5.1 preview differs from the Blender 4.2 tutorial, the
production render can still be deterministic.

## Linked render-script audit

The description's
[rotation script](https://gist.github.com/kit-agawa/94a18f982d5b1c016a119d4cbe25882f)
is a small prototype that:

- reads the active object;
- rotates it around Z in eight 45-degree steps;
- renders every frame in the scene range;
- names the whole batch as one continuous numbered sequence;
- restores the original rotation and output path after normal completion.

The reviewed raw revision has SHA-256:

```text
a63eb8c9501fc33215977b69d8d4eda46b8bc8fc2479272150fce4cc2c3b2ec8
```

It contains no network, subprocess, or deletion behavior. It is still not a
production renderer:

- it can overwrite existing output;
- it does not create or validate directories;
- it lacks `try/finally` recovery;
- it assumes the active object is the complete character root;
- it does not choose named actions or view profiles;
- it does not coordinate lights with rotation;
- it does not emit color, normal, silhouette, or material-ID passes;
- it does not produce a Godot manifest or contact sheet.

A Tripo GLB can contain an armature, mesh children, and separate expression
objects. All production pieces must sit beneath one declared export/render root.
Rotating an arbitrary active mesh would turn only part of such a character.

## Rights rule

Neither the Gist nor the Google Drive starter file declares a reusable license.
They may be inspected to understand the technique, but neither file will be
copied, modified, redistributed, or committed as a Bentosaur dependency.

The production renderer and `.blend` template will be implemented cleanly from
the behavior described here. Bentosaur will also use its own approved palette;
the tutorial palette is not part of the game's identity.

## Bentosaur-specific asset tiers

### Counter customer and host

Target native 96 px first. This is the strongest fit for the method:

- exact front-facing `stall_front` camera;
- optional authored `stall_3q` camera, not an arbitrary 45-degree turn;
- visible eyes, muzzle, all three horns, frill knobs, cheeks, hands, and bento
  interaction;
- one-source-pixel outer edge;
- two to four hard palette bands;
- optional normal pass tested only after the color sprite passes.

Native 64 px is a separate proof. At this size the center horn may fuse into the
muzzle, the side horns and frill knobs may merge, and a one-pixel outline may
become too heavy. Camera-specific corrective shape keys are permitted.

### Street walkers

Use a separate silhouette LOD from the same approved identity:

- native 48 px first, 32 px only if it remains readable;
- broad frill/horn mass rather than literal tiny facial detail;
- three to five value groups;
- no internal ink unless it survives at one-to-one scale;
- no normal map;
- one canonical east-facing side render mirrored west, unless an asymmetric
  prop or action requires unique directions;
- randomized pause/look timing belongs in Godot, not in the sprite sheet.

At 24 px, a literal three-horn face cannot be a hard requirement. Species
recognition must come from the silhouette.

### Album portrait

Use the master as a posing and lighting source at 192 or 256 px, then hand-polish
the final image. The album does not need to expose the raw 3D render.

### World, weather, and UI

Rain, snow, lantern glow, windows, street ambience, counter occlusion, cooking
particles, and the book UI remain authored 2D/Godot layers. Blender may produce
isolated prop bakes or perspective references; it does not need to own the full
rainy street.

## Clean-room production template

Use Blender 5.1.2, which is installed locally, and validate the template in that
exact version. Pin the version in every render receipt.

### Scene contract

```text
COL_RENDER_ASSEMBLIES
└── RENDER_ASSEMBLY_<character_id>
    ├── ROOT_CHARACTER_<character_id>
    │   ├── Armature and rig controls
    │   ├── Body
    │   └── FaceStates
    └── ATTACHMENTS
        └── ROOT_PROP_<prop_id>

COL_CAMERAS
├── CAM_stall_front_096
├── CAM_stall_front_064
├── CAM_stall_3q_096
├── CAM_stall_3q_064
├── CAM_street_side_048
└── CAM_street_side_032

COL_RENDER
├── LIGHT_or_palette_reference
├── BG_transparent
└── pass helpers
```

The character itself remains prop-free. Trays, bowls, umbrellas, aprons, and
food stay separate and are attached only for the specific render job. The
renderer turns the **render assembly**, never an arbitrary mesh or the character
alone.

Every renderable object, armature, rig controller, Armature modifier target,
constraint target, face object, and evaluated dependency must either descend
from the assembly root or appear in an explicit validated world-fixed allowlist.
The default allowlist is empty.

Each attachment record declares:

- the separate prop/accessory asset and root;
- attachment method: bone parent, `Child Of`, or shared armature;
- target socket/bone;
- parent and child transform spaces;
- bind transform;
- visible actions/frames;
- whether left/right renders may be mirrored.

A rigid bowl can bone-parent to a hand or tray socket. A deforming apron may be
a separate skinned mesh using the approved armature. Both remain separate
assets, but both must follow `RENDER_ASSEMBLY_<character_id>` during a
directional render.

### Isolated Blender invocation

Run the renderer in background mode with controlled empty user config/script
directories and the flags placed before the `.blend` path:

```text
BLENDER_USER_CONFIG=<controlled-empty-config>
BLENDER_USER_SCRIPTS=<controlled-empty-scripts>
Blender --background --factory-startup --disable-autoexec \
  <approved-master.blend> \
  --python <reviewed-renderer.py> -- --job <job.json>
```

`--factory-startup` skips the user's startup scene; the controlled Blender
environment prevents user add-ons/preferences from becoming invisible render
dependencies. `--disable-autoexec` blocks embedded scripts and Python-expression
drivers, while the explicitly named reviewed renderer still runs.

The first proof therefore forbids Python-expression drivers. Constraints,
keyframes, shape keys, and non-scripted drivers are validated before rendering.
If a later master truly needs scripted drivers, each expression and dependency
must be allowlisted and the isolation decision revisited explicitly.

### Dependency closure

The `.blend` hash alone is insufficient. External palettes, textures, linked
libraries, fonts, caches, or absolute file paths could change independently.

Prefer packed resources. Otherwise the job manifest must enumerate and hash
every external dependency, reject missing or unlisted paths, reject mutable
absolute paths, and include the dependency-manifest hash in every render
receipt.

### Common color/output settings

- view transform: `Standard`;
- look: none;
- exposure: 0;
- gamma: 1;
- dither: 0;
- output: PNG RGBA, 8-bit;
- transparent film: on;
- pixel filter: 0;
- no bloom, motion blur, depth of field, TAA, FXAA, temporal upscaling, or
  lossy texture compression;
- flat material IDs or nearest-filtered tiny textures;
- no specular, reflections, realistic normal maps, or ambient color drift.

`Nearest` is not one Blender setting. The renderer maps it explicitly:

- Image Texture nodes: `Closest`;
- compositor Transform nodes: `Nearest`;
- final Composite: no scaling or preview transform;
- Godot import: Nearest filtering and lossless texture handling.

### Per-pass engine settings

#### Color

- engine: Blender 5.1 `BLENDER_EEVEE`;
- `scene.eevee.taa_render_samples = 1`;
- `scene.eevee.taa_samples = 1`;
- temporal reprojection, bokeh jitter, shadow jitter, and shadows off;
- palette materials are unlit/emission or an equivalently validated flat
  shader;
- pixel filter width `0`;
- no compositor resampling on the saved image.

The hard highlight/shadow bands are authored palette regions, not soft realtime
lighting.

#### Silhouette and material ID

Use the same deterministic Eevee configuration with explicit unlit override
materials. The silhouette is binary. Material-ID colors are fixed identifiers,
not color-managed beauty colors and not lit material previews.

#### Camera-normal

Use an isolated Workbench render with all of the following set explicitly:

- engine: `BLENDER_WORKBENCH`;
- light: `MATCAP`;
- studio light: `check_normal+y.exr`;
- color type: `SINGLE`;
- single color: white;
- studio-light rotation `0` and intensity `1`;
- shadows, cavity, specular highlight, and object outline off;
- Workbench viewport and render AA: `OFF`;
- Standard transform, dither `0`, no palette indexing.

Leaving Workbench at its default material color multiplies the MatCap result and
corrupts the normal vector. A safe test changed the same center normal from
sRGBA `(137, 120, 254)` to `(124, 108, 231)` when material color was allowed.
The normal pass cannot inherit color-pass defaults accidentally.

### Passes

Every proof render produces:

1. `color` — palette sprite with transparent alpha;
2. `silhouette` — binary identity/readability test;
3. `material_id` — flat repair and recolor mask;
4. `normal_camera` — optional camera-space normal pass, disabled for walkers.

Normal images remain RGB data and are never palette-indexed. Godot normal
orientation is validated with a four-direction `Light2D` test before use.

### Animation

- 12 fps Blender timeline for the first proof;
- stepped/constant body timing;
- six to eight authored frames for the first action;
- held frames are explicit;
- root placement and camera framing snap to whole target pixels;
- the script renders named frame ranges, not the entire timeline;
- no automatic eight-direction batch.

### Footprint and pivot contract

Cell size alone is not a fair comparison. The 2D control uses a maximum 56×56
art footprint inside a 64×64 cell with pivot `[32, 58]`. Every 3D profile
therefore locks its maximum content box, baseline, and pivot before rendering:

| Profile size | Maximum art box | Pivot | Baseline Y |
|---|---:|---:|---:|
| 96×96 | 84×84 | `[48, 87]` | 87 |
| 64×64 | 56×56 | `[32, 58]` | 58 |
| 48×48 | 42×42 | `[24, 44]` | 44 |
| 32×32 | 28×28 | `[16, 29]` | 29 |

The box is a maximum, not permission to stretch each pose to its edges. All
frames in one clip use the same camera, pivot, baseline, and transparent cell.
The 2D control and 3D candidate are composited at the same scene-space pivot.

The renderer performs snapping in **orthographic camera space**, not by rounding
Blender world coordinates:

```text
world_units_per_pixel_y = camera_ortho_scale / render_height
camera_view_width = camera_ortho_scale × render_aspect
world_units_per_pixel_x = camera_view_width / render_width
```

It projects the declared assembly anchor into camera space, aligns the requested
pivot to the target pixel-center convention, then transforms it back. Pixel
aspect and odd/even cell dimensions are part of the calculation. A one-pixel
marker validation must prove there is no half-pixel drift before a batch runs.

## Renderer requirements

The clean-room Blender renderer must:

1. read a versioned JSON job;
2. validate the requested character root, action, camera, frames, pass, output
   directory, Blender version, and palette revision;
3. refuse an occupied output directory unless an explicit safe overwrite mode
   names the exact job directory;
4. save and restore scene state in `try/finally`;
5. rotate the declared root or select a declared camera profile;
6. keep camera-relative palette lighting consistent;
7. render only requested directions and frames;
8. emit deterministic filenames;
9. create color, silhouette, material-ID, and optional normal frames;
10. write a JSON manifest with frame size, action, direction, fps, pivot,
    camera, palette, source model revision, Blender version, and hashes;
11. create a contact sheet and animation preview for human review;
12. validate the packed or hashed external-dependency closure;
13. reject Python-expression drivers in the first proof;
14. start from an isolated Blender user configuration;
15. never execute embedded third-party `.blend` scripts.

Proposed output:

```text
exports/sprites/<character>/<master_revision>/<job_id>/
  color/<profile>/<action>/<direction>/frame_000.png
  silhouette/<profile>/<action>/<direction>/frame_000.png
  material_id/<profile>/<action>/<direction>/frame_000.png
  normal_camera/<profile>/<action>/<direction>/frame_000.png
  sheets/
  previews/
  manifest.json
  validation.json
```

## Proof sequence and human gates

### Gate 0 — approved character appearance

Do not rig or animate a production candidate until the user explicitly approves
its complete surfaced 3D appearance. This research does not override that gate.

No current candidate is approved.

### Gate 1 — static sprite identity

After approval, render:

- blocking primary stills: front counter at native 96 and side walker at native
  48;
- nonblocking diagnostics: front counter at native 64, authored
  three-quarter counter at native 96/64, and side walker at native 32;
- color, silhouette, and material-ID passes;
- one-to-one in-scene phone mockups plus four-times defect views.

Gate 1 passes when the 96 px front counter and 48 px side walker pass. The
diagnostics determine whether smaller or three-quarter uses are allowed; they
do not block the primary route.

Reject or revise the counter profiles if:

- the three horns or frill identity disappear;
- the face reads as plastic, generic, or puppy-like;
- outline gaps bridge;
- small limbs become isolated/noisy pixels;
- the native palette exceeds the agreed color budget without a reason.

For side walkers, require a recognizable Triceratops frill/horn mass and a clean
upright biped silhouette. Do not require three separately countable horns in a
32/48 px side projection.

### Gate 2 — minimal motion A/B

Only after Gate 1 passes:

- one six-to-eight-frame front-facing `receive → delight` action;
- one six-to-eight-frame side walk;
- blocking primary output at native 96 counter and 48 walker;
- nonblocking stress output at native 64 counter and 32 walker;
- identical palette, framing, timing, and scene placement for the 2D control.

Measure:

- three-horn/frill, eye, hand, and foot readability for counter views;
- frill/horn-mass and upright-biped readability for walker views;
- silhouette crawl and held-pose flicker;
- orphan pixels and bridged outline gaps;
- loop seam and foot slide;
- whether the render reads as plastic;
- Aseprite cleanup minutes per frame;
- sprite-sheet size and Godot import behavior.

Blind-test at least five people on which version feels warmer, more like
Bentosaur, and less like raw 3D.

For the prop-free walker, render one canonical east-facing loop and mirror the
visual node for west in Godot. Render both directions only when an asymmetric
prop, marking, action, or light treatment has an explicit job-level reason.

### Gate 3 — optional normals

Normals are a separate experiment after the color result passes. Test only the
foreground customer beneath the warm lantern. Reject normals if they make the
sprite look smooth, plastic, or inconsistent with the painted environment.

## Routing decision

- **96 px counter and 48 px walker pass:** adopt the 3D master as the sprite
  factory.
- **Counter passes; walker fails:** keep the master for foreground customers
  and build a hand-simplified walker LOD.
- **Motion passes; surface finish fails:** render pose/lighting reference and
  draw over it in Aseprite.
- **Only live 3D passes:** compare its mobile and visual costs separately; this
  document does not promote it automatically.
- **Identity or heart fails:** return to directional 2D kits.

## Cost and credit note

The last verified project ledger is
`art/jobs/tripo-visual-gate-01.json`: 5,000 original credits → 165 cumulative
credits consumed → **4,835 verified remaining**.

This research made no Tripo API call:

- balance carried into this research: 4,835;
- consumed by this research: 0;
- expected carried-forward balance: 4,835;
- fresh balance query for this document: not performed.

Downloading and inspecting the public tutorial resources and rendering locally
in Blender do not consume Tripo credits. A future sprite bake from an already
approved master is estimated at 0 Tripo credits, but its actual-use field stays
`null` until the bake runs.

Upstream Tripo generation, rigging, or purchased animation is outside the local
bake cost and remains recorded in its originating Tripo job.

## Sources

- [Primary Blender pixel-art video](https://www.youtube.com/watch?v=PBIPJdEECWg)
- [Linked rotation-render Gist](https://gist.github.com/kit-agawa/94a18f982d5b1c016a119d4cbe25882f)
- [Linked starter `.blend`](https://drive.google.com/file/d/1vo8Fjf3RvRez_HcGsdHQmQBmaqCighai/view?usp=sharing)
- [Canvas-size companion](https://www.youtube.com/watch?v=upEGBGCiWEw)
- [Outline companion](https://www.youtube.com/watch?v=cnQu1kMs49s)
- [Gradient-texturing companion](https://www.youtube.com/watch?v=9ITJgW9hVrE)
- [Gradient texturing for mobile games](https://itch.io/blog/797457/optimization-of-3d-texturing-for-mobile-games-definition-of-the-gradient-texturing-process-and-analysis-of-its-efficiency-and-performance-in-engine)
- [Dead Cells 3D-to-2D art pipeline](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- [Godot 2D lights and normal maps](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- [GitHub guidance for repositories without a license](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
