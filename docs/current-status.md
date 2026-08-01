# Bentosaur Current Status

Status: active

Snapshot date: 2026-07-31

## Executive state

Mau selected flat-cel 2D as Bentosaur's leading visual direction and ended the
open-ended exploration phase. The Godot project now boots the production-shaped
Home Village assembly: approved rainy street and registered light wake-up,
uniformly scaled V002 stall, two approved modular hanging lanterns, the
founder-approved V004 non-character attachment kit with live semantic
controls, and the approved 1990s-anime transfer preset 3. V011 corrects the
phone-scale crate perspective/layering, rank-star sockets, and stockpot-lid
contact found during V010 review. V012 now adds the first live flat-cel
proprietor proof behind that stall: bottom-anchored breathing, randomized
blink/double-blink timing, and a reduced-motion endpoint. Its complete
22-contract suite and normal/reduced Metal captures pass. Mau's visual review
of the in-stall character remains open. The iOS build remains under the
personal Apple team.

The complete bounded first-playable loop remains preserved at
`game/scenes/vertical_slice/first_playable.tscn`: classic-stall Home, three
ordered bento customers, correctable service, coins, first-try stars, local
persistence, shift summary, and replay. It is no longer the boot scene while
the real layered home menu is assembled.

The current runtime uses the approved flattened concept screens as temporary
backdrops. They preserve the intended atmosphere while the real gameplay model
and UI are tested, but they are not production assets. If the loop passes, the
next implementation milestone is one registered front customer that idles,
blinks, receives the bento, chews, and delights.

The former live-3D direction is preserved as the last locked production path,
but it is paused while this decisive 2D proof runs. The visual selection does
not make the generated rasters production assets and does not silently discard
the 3D lineage.

No character is currently approved as production-ready, rig-ready, or
animation-ready in either route.

The Home Village lighting and rain proof is now a founder-approved visual
checkpoint. Rain remains active from frame one, registered lights wake through
it, and the weather uses a softer normal-alpha treatment instead of bright
white streaks over the scene. Music and rain ambience both play through
separate buses at the device-tuned `-21 dB` music and `-22 dB` rain gains; iOS
Silent Mode is respected.

The V004 atmosphere baseline first introduced breathing, local flicks, and a
measured lower-stall depth falloff. Its motion assumptions are historical. Mau
later observed the anime treatment visibly sliding upward on the physical
iPhone, proving that the prior static A/B did not cover iOS surface/lifecycle
changes. See [Home Menu V004 atmosphere checkpoint](checkpoints/2026-07-31-home-menu-v004-atmosphere-polish.md).

V005's stronger randomized alpha motion was still completely imperceptible on
the physical iPhone and is rejected. Its denser shared roof-impact scheduler
and sixteen stall-local anchors remain active for device review. See
[Home Menu V005 failed device test](checkpoints/2026-07-31-home-menu-v005-device-motion-test.md).

Mau confirmed V006's intentionally excessive breath and fixed double-flick were
both visible on the physical iPhone. V007 then established the irregular
explicit-RGB production motion, but its six-source, one-minute cadence and
fixed reflections are now superseded.

V008 registers all 18 painted windows and lanterns, including the complete
right side, and maps them to nine wet-pavement reflection bands. A source and
its reflection now breathe and flick from the same frame-level motion state;
reflections are only attenuated, never delayed or independently randomized.
The first event begins after `6–12 s`, later events recur after `14–28 s`, and
each still contains one, two, or three irregular dips. The anime pass now owns
an explicit full-viewport back-buffer copy and an always-active coverage
controller so an iOS resize or lifecycle transition cannot expose an untreated
band. All 14 executed Godot contracts and a 390-frame Forward Mobile / Metal
capture pass. A personally signed V008 device build is ready; physical install
and confirmation of the original slide-away report wait for the iPhone to
reconnect. See [Home Menu V008 linked reflections and stable anime coverage](checkpoints/2026-07-31-home-menu-v008-linked-reflections-and-filter-coverage.md).

V009 promotes the founder-approved hanging lantern as a reusable Godot
fixture. Each side shares one canonical OFF shell; ON adds separate additive
core and halo layers without changing geometry. Fixed anchors remain outside
the ring-center sway pivots, and both fixtures inherit the responsive
`StallStage`. All 13 current Godot contracts pass. Warm spill across the stall
wood, fixture-specific pavement reflections, neighborhood pulse/flick
coupling, and physical-iPhone tuning remain explicitly deferred. See
[Home Menu V009 approved modular stall lanterns](checkpoints/2026-07-31-home-menu-v009-approved-stall-lanterns.md).

V010 promotes and integrates the founder-approved V004 complete stall
attachment kit. Thirty-one registered runtime textures now compose reusable
stockpot, counter-lantern, counter-decor, three-star rank, menu-button, and
settings fixtures. The stockpot steam and lid, plant foliage, practical light,
rank fill, and control feedback are procedural and share one reduced-motion
boundary. The four menu entries and settings cog are real semantic Godot
buttons with live Lilita One labels; they emit navigation intent only, because
their destination screens are outside V010. The main character is also
deliberately excluded. All 21 Godot contracts pass; normal and reduced-motion
Forward Mobile / Metal captures are recorded. The personal-team build is
strictly signed, installed, and running on Mauricio's iPhone 17 Pro Max.
Phone-scale visual/interaction approval remains pending.
See [Home Menu V010 complete modular stall kit](checkpoints/2026-07-31-home-menu-v010-complete-stall-kit.md).

V011 replaces only V010's failed prop registrations. It promotes the exact
approved static bottle-crate composition, preserves the independent pieces for
future variants, centers the stars on the plaque's measured nine-sliced
sockets, and seats the still-independent lid at its optical contact point. All
21 contracts pass and normal/reduced Forward Mobile / Metal captures are
recorded. The personally signed build is installed and running on Mauricio's
iPhone 17 Pro Max. Founder phone-scale approval remains pending.
See [Home Menu V011 registration corrections](checkpoints/2026-07-31-home-menu-v011-registration-corrections.md).

V012 promotes the registered V3 neutral and blink states into one reusable
Godot proprietor controller. The complete stall shell occludes the prototype
body at `z15`; the character remains behind it at `z14`, existing foreground
attachments stay at `z16+`, and weather stays at `z20`. A seeded elapsed-time
controller provides a 3.4-second breath, randomized session phase/speed,
randomized blinks and occasional double blinks. All 22 contracts pass at the
suite level, including deterministic equivalence at 30/60/120 FPS. This is an
explicit whole-sprite proof, not the final separated body/face/hands rig.
Founder visual approval is pending.
See [Home Menu V012 proprietor idle proof](checkpoints/2026-07-31-home-menu-v012-proprietor-idle-proof.md).

V013 replaces V012's arms-down motion proof with the authored counter pose.
The neutral source is the registration authority; only two feathered eye
patches change for the blink. A source-identical foreground arm/hand layer now
creates the runtime order body `z14` → stall `z15` → fingers `z16`, while one
bottom-anchored breathing root keeps hand contact stable. V013's leading
diagnosis for the five-minute iPhone filter artifact is the old unbounded sine
grain hash: the visible `-0.16` boundary slope matches its constant-phase slope.
The shader now uses a controller-owned 256-frame bounded ring and a bounded
no-sine hash. A six-simulated-minute Forward Mobile / Metal capture stays
coherent. Founder character approval and an 8–10 minute physical-iPhone
longevity/resume gate remain pending before causality is considered proven.
See [Home Menu V013 counter proprietor and bounded filter](checkpoints/2026-07-31-home-menu-v013-counter-proprietor-bounded-filter.md).

V014 is an open visual-only lighting gate. The current V013 iPhone build is
preserved and pushed at tag
`checkpoint/home-flat-light-approved-2026-07-31`. Research and scene auditing
confirm that the foreground mismatch comes from uniformly lit stall/character
sprites sitting above the village's baked light layers. No runtime change has
been made. The proposed direction is a cool foreground night base plus three
soft lantern-motivated warm pools, with normal maps and cast shadows deferred.
See [Home Menu V014 lantern-motivated lighting study](../game/docs/visual-gates/home-menu-v014-lighting-study/README.md).

The mobile display baseline is also locked: `720 × 1280` is the stable logical
design grid, `canvas_items` renders at the target device resolution, `expand`
supports ultratall displays, and iOS uses Metal with ProMotion permitted. The
approved `941 × 1672` Home Village remains the visual authority but requires a
separate `1440 × 3200` layered outpaint/upscale gate before shipping on the
`1320 × 2868` iPhone 17 Pro Max display.

See [Mobile display quality contract](mobile-display-quality-contract-v001.md)
and [Home Village rain lab](home-village-rain-lab-v001.md).

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

The current menu and idle expansion is:

`art/concepts/2d-chibi/v3/`

The active implementation contract is:

`docs/first-playable-v1.md`

The preserved gameplay proof is:

`game/scenes/vertical_slice/first_playable.tscn`

The current Godot boot scene is:

`game/scenes/home/home_menu.tscn`

Mau explicitly requested the matching hub, book, expression, and page-turn
exploration, superseding the earlier screen-generation restriction. The pack
now establishes visual continuity, menu alternatives, and prototype idle
feasibility, not production readiness.

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

### Home Menu V012 — proprietor idle visual gate

- [x] hash-verify and promote the registered neutral/blink pair;
- [x] integrate the proprietor behind the complete stall shell;
- [x] implement deterministic breath, blink, occasional double blink, and
  reduced motion;
- [x] run and record the complete 22-contract Godot suite;
- [x] capture normal, blink, and reduced-motion Forward Mobile / Metal evidence;
- [ ] obtain Mau's approval of identity, scale, placement, and idle feeling;
- [ ] after approval, reconstruct the shared production body, separate face,
  and continuous foreground counter hands.

### Home Menu V011 — corrected device gate

- [x] correct crate perspective/layering, star sockets, and lid contact;
- [x] run and record the complete 21-contract Godot suite;
- [x] capture normal and reduced-motion Forward Mobile / Metal evidence;
- [x] export with personal team `53RJ43876F`, strictly verify signing, install,
  and launch bundle `com.mauvsantos.bentosaur` on the physical iPhone;
- [ ] verify aspect ratio, safe area, touch states, audio, rain, anime-filter
  coverage, and procedural motion on the phone;
- [ ] obtain Mau's explicit phone-scale approval before calling V011 closed.

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

- The v2/v3 flat-cel expressions, screens, menu alternatives, and sprite-state
  concepts used built-in ImageGen; no Tripo credits or paid external API were
  used.
- Faceit `2.3.71` is installed locally; no license credential or transaction
  record is stored in the repository.
- No paid API was called during r004, r005, or r006.
- Tripo credits spent by r004/r005/r006: `0`.
- Recorded Tripo balance: `4,695`.
- No repository push is authorized by this status document.
