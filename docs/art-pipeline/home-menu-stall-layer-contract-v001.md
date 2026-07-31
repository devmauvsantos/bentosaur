# Home Menu Stall Layer Contract v001

**Status:** Gate 1 approved — 2026-07-31

**Reference:** `art/concepts/2d-chibi/v4/01_menu-refinement/`
`bentosaur-home-menu-refined-classic-guestbook-v2.png`

**Target:** Godot 4.7 Mobile, portrait 9:16

**Working post-process:** 90s transfer preset 3

## Decision

The concept is a composition reference, not a flattened shipping asset.
Production reconstructs it as registered world layers, animated attachments,
and native Godot controls.

The first generation gate is only the unlit structural stall. No character,
props, lights, rank stars, menu controls, smoke, or ambient dinosaurs are
included in that gate.

## Master registration

- Author registered source layers on a `1440 × 2560` transparent canvas.
- Use the same canvas origin for every stall, character, prop, and light layer.
- Keep a full-canvas source plate for reconstruction and review.
- Runtime export may trim transparent bounds, but must write position and pivot
  metadata into `home_menu_layers.json`.
- Do not independently eyeball placement after trimming.

## World layer tree

```text
HomeMenuWorld
├── approved home-village background
├── ambient background dinosaurs
├── rain: back field
├── stall: ground contact shadow and registered wet reflection
├── stall: rear shell, roof, brand sign and awning
├── proprietor: body behind counter
├── stall: counter-front occluder
├── proprietor: left and right foreground hands
├── rank plaque and stars
├── counter props
├── hanging lantern shells
├── lantern cores, halos and registered warm spill
├── steam and other prop VFX
├── rain: foreground field with stall/interior exclusion
└── 90s world post-process

HomeMenuUI
├── button frame sprites behind native labels
├── native Godot labels and focus states
├── coin counter
├── weather control
└── settings control
```

The world is processed by the 90s shader. Text, focus rings, touch targets, and
HUD remain above it for readability.

## Stall assembly

### Structural master

Keep:

- blue-tile roof and wooden roof beams;
- the `BENTOSAUR` brand sign and fixed leaf ornament;
- vertical posts;
- empty service opening;
- countertop;
- buttonless wooden front facade.

Author the approved structure as two registered runtime layers:

- `stall_rear_shell_unlit`: roof, posts, sign, back wall and service opening;
- `stall_counter_front_buttonless`: countertop and front facade, used as the
  proprietor's occluder.

They appear as one coherent stall in the approval composite. The split exists
only so the dinosaur can stand behind the counter while its hands rest in
front without destructive masking.

Remove:

- proprietor dinosaur;
- foreground hands;
- all menu buttons and their text;
- rank plaque and all stars;
- both hanging lanterns;
- pot, lid and steam;
- small oil lantern;
- grapes and bowl;
- potted plant;
- bottle crate;
- red cloth;
- surrounding dinosaurs and umbrella;
- coin, weather and settings HUD;
- every emitted light, halo and warm reflection belonging to the stall.

### Separate structural attachments

- `stall_awning_valance`
- `stall_ground_contact_shadow`
- `stall_rank_plaque_empty`
- `stall_rank_star_empty`
- `stall_rank_star_filled`
- `stall_rank_star_shine`
- `stall_lantern_unlit` instantiated twice
- `stall_lantern_core`
- `stall_lantern_halo`
- `stall_warm_spill_registered`
- `stall_wet_ground_reflection_registered`

The lantern shell is separate so it can pivot gently from its hook. Core and
halo follow the shell; the broad spill remains mostly stable.

The brand sign may remain registered with the shell for Gate 1, but preserve
it as a reconstructable source layer so future roof or awning upgrades do not
force a repaint of the game's identity mark.

## Counter prop kit

- `stockpot_body`
- `stockpot_lid`
- `stockpot_contact_shadow`
- `steam_8x1` or equivalent authored VFX
- `small_oil_lantern`
- `grape_bowl`
- `counter_plant`
- `bottle_crate`
- `counter_cloth`

The lid must have a top-center visual registration and a centered bottom pivot.
It moves only `1–2 px` at the 720 × 1280 logical scale, with a slight rotation.
Steam bursts and lid motion share one randomized scheduler.

The pot body must include the rim and believable dark interior normally hidden
by the lid. Otherwise lifting the lid will reveal an empty painted patch.

Counter props are separate because the menu already promises a Decorations
system. Baking them into the stall would force a repaint for every decoration
loadout.

## Proprietor rig

The existing v3 neutral, blink, wave, and delighted state sheet is the identity
anchor. Do not redesign the main dinosaur.

Generate one identity-consistent **stall-pose** source sheet from that anchor,
then reconstruct the shipping layers manually. Do not independently generate
every attachment. Character generation waits for Structural Stall Gate 1:
the approved opening and countertop line define the character scale, root, and
hand registration.

Registered source layers:

- `proprietor_body_base` without eyes, mouth, or arms
- `proprietor_arm_left_neutral`
- `proprietor_arm_right_neutral`
- `proprietor_arm_left_react`
- `proprietor_arm_right_react`
- `proprietor_eyes_open_pair`
- `proprietor_eyes_closed_pair`
- `proprietor_mouth_neutral`
- `proprietor_mouth_open_happy`
- `proprietor_mouth_chew_a`
- `proprietor_mouth_chew_b`
- three independent laugh accent marks

This is a fourteen-layer kit. Do not separate horns, nose, cheeks, frill knobs,
torso, fingers, or hands from their continuous arms.

Generate the neutral, delighted, and savor/chew targets together on one
registered three-state sheet. Use the neutral panel as the canonical body
pixel set, then reconstruct the layers from it. The body stays behind the
structural stall; arm layers render over the countertop; face attachments
render over the body.

Idle contract:

- `3.4 s` breathing loop;
- blink every `2.3–5.4 s`;
- optional greeting every `8–14 s`;
- low-frequency hand and head secondary motion;
- state priority `reaction > gesture > blink > breath`.

## Native menu controls

Do not ship generated button text.

Generate only:

- scalable button frame, normal;
- scalable button frame, focused/selected;
- scalable button frame, pressed;
- optional disabled treatment;
- leaf ornaments as separate sprites.

Godot supplies:

- `Open Stall`, `Guestbook`, `Decorations`, and `Pantry` labels;
- final embedded font;
- localization;
- focus and controller navigation;
- touch targets;
- accessibility names;
- pressed/disabled state.

The button art can render below the 90s post-process while live text and focus
indicators remain above it.

## Rain and light integration

- Back rain renders behind the stall.
- Background roof impacts render behind the stall.
- Foreground rain may cross the roof and outer silhouette.
- The service opening, proprietor, counter, and sheltered props require a rain
  exclusion mask.
- Stall roof-impact anchors extend the existing sparse impact scheduler; they
  do not create a second competing rain system.
- Light cores and halos flicker independently at very low amplitude.
- The broad stall spill changes more slowly than the cores.
- Generate a geometry-identical lit reference from the approved unlit stall;
  do not regenerate the structure while adding light.

The current single weather depth must be split before final stall assembly.
This is an integration task, not a Gate 1 image-generation task.

## Runtime export

- Keep full-canvas registered PNGs as source masters only.
- Trim transparent runtime sprites to reduce texture memory and overdraw.
- Record each trimmed sprite's source rectangle, anchor, pivot, z-order,
  lantern sockets, roof-impact anchors, and hashes in
  `home_menu_layers.json`.
- Provide authored masks for counter/owner occlusion and sheltered-rain
  exclusion.

## Visual gates

1. **Structural stall, unlit:** approve silhouette, perspective, materials,
   empty opening, countertop, and facade. Review both the isolated registered
   cutout and its composite over the immutable approved village.
2. **Stall lighting:** approve unlit lantern shell, core, halo, and spill.
3. **Proprietor neutral pose:** approve identity and registered body/hands.
4. **Proprietor facial vocabulary:** approve eyes, mouth and laugh accents.
5. **Pot motion proof:** approve body, separate lid, steam and timing.
6. **Menu control proof:** approve button frame states with native text.
7. **Assembled living menu:** approve z-order, rain exclusion, preset 3, motion,
   audio and mobile performance.

Do not advance to a later visual gate without approval of the current gate.

## Gate 1 acceptance criteria

- The stall aligns to the approved Home Village street at the concept's scale
  and perspective.
- Roof, sign, posts, opening, countertop, and facade form one coherent object.
- Rear shell and counter-front layers align with no visible seam.
- The service opening is genuinely transparent.
- The countertop and front facade are completely reconstructed behind removed
  props and menu buttons.
- `BENTOSAUR` remains part of the fixed brand sign.
- No rank plaque, lantern, character, prop, light emission, smoke, HUD, or
  ambient NPC remains.
- No baked amber reflection remains on the stall or the street.
- The output has clean alpha, no key-color fringe, and no regenerated
  background pixels.
- The result survives a 50% scale preview without edge shimmer.

Gate 1 review material must show:

- the registered transparent cutout on a checkerboard;
- the unlit composite over the approved village;
- a reference-registration overlay;
- a `720 × 1280` Godot capture under preset 3.
