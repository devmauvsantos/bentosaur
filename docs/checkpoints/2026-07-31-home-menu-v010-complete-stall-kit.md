# Home Menu V010 — Complete Modular Stall Kit

> Historical integration checkpoint. Phone-scale crate, rank-star, and
> stockpot-lid registration is superseded by
> [Home Menu V011](2026-07-31-home-menu-v011-registration-corrections.md).

**Status:** founder-approved V004 art promoted and integrated; 21/21 contracts
pass and V010 is running on the personal iPhone; founder device review pending

**Date:** 2026-07-31

## Outcome

The approved non-character V004 attachment set is now a real, modular Godot
assembly on the Home Menu stall. The source art is preserved separately, the
31 runtime textures are registered on the `720 × 1280` logical design grid,
and the Home Menu exposes semantic intent signals for every visible control.

This checkpoint completes the stall-kit integration. It does **not** complete
the main character, destination screens, or physical-iPhone approval.

![Home Menu V010 complete stall kit](assets/home-menu-v010-complete-stall-kit.png)

The historical candidate review remains at
[Stall Attachment Kit V004 — Complete Candidate Gate](2026-07-31-stall-attachment-kit-v004-candidates.md).
Mau subsequently approved the V004 set for this runtime promotion.

## Approved runtime asset set

The immutable source package and registered approval evidence remain under:

`art/source-assets/home-menu/stall/v004-attachment-kit/`

The promoted runtime package is:

`game/assets/environments/home_village/v001/stall/attachments/v004/`

Its `runtime_manifest.json` records source/output hashes, logical boxes, QA,
and the complete 31-texture inventory:

- stockpot: open body, separate lid, and contact shadow;
- counter oil lantern: canonical OFF body, additive core, additive halo, and
  contact shadow;
- counter decor: grape bowl, plant pot, separate foliage, empty bottle crate,
  three separate bottles, and draped red cloth;
- rank: plaque, empty star, filled star, and shine overlay;
- menu controls: primary and secondary normal, focused/selected, pressed, and
  disabled frames, plus two detached leaf ornaments;
- settings: normal and pressed cog states.

Only approved runtime components were promoted. Assembled review previews,
the rejected green rank recolor, generated steam rasters, fonts from the art
source pack, and the main character are excluded.

## Modular runtime structure

The Home Menu and the isolated stall lab both instance one reusable assembly:

```text
StallAttachmentKit
├── RankFixture
├── Stockpot
│   ├── ContactShadow
│   ├── Body
│   ├── SteamEmitter         soft wisps + outlined phone-scale curls
│   └── LidPivot            separate lid motion
├── CounterOilLantern
│   ├── ContactShadow
│   ├── LocalHalo           additive
│   ├── BodyOff             canonical shell
│   └── Core                additive
├── CounterDecor
│   ├── FoodBowl
│   ├── Plant              pot + foliage pivot
│   ├── BottleCrate        crate + three bottles
│   └── CounterCloth
├── OpenStallButton
├── GuestbookButton
├── DecorationsButton
├── PantryButton
└── SettingsButton
```

The source scenes are under `game/scenes/home/components/`; the typed
controllers are under `game/scripts/home/`. Keeping each practical object and
control independent allows later decoration changes, light direction,
animation tuning, and localization without repainting the stall.

The assembly remains a child of the responsive `StallStage`, so every
registered attachment inherits the same uniform framing transform as the
approved stall instead of receiving per-device stretching.

## Semantic controls and public API

The four menu entries and the settings cog are real Godot `Button` controls,
not decorative sprites with hidden hit regions. They provide:

- native press, disabled, focus, and keyboard/controller semantics;
- explicit focus-neighbor order;
- live `label_text` instead of text baked into the button art;
- primary and secondary visual-state systems with stable silhouettes;
- a canonical alpha mask on the normal button state to prevent edge shimmer;
- pressed feedback with bounded scale/translation, plus bounded rotation on
  the settings cog;
- immediate visual endpoints when reduced motion is enabled.

The Home Menu relays five intent signals:

```text
open_stall_requested
guestbook_requested
decorations_requested
pantry_requested
settings_requested
```

These signals establish the navigation boundary. V010 intentionally does not
implement or claim any destination screen or route.

## Procedural motion contract

No sprite sheet is required for the stall's ambient life:

- the stockpot creates procedural steam wisps and gives the separate lid a
  restrained occasional rattle;
- the plant foliage uses a slow, sub-degree sway while the pot stays fixed;
- the counter lantern keeps one canonical shell and adds independent power,
  pulse, and rare-flick levels to its core and halo;
- the rank fixture supports a bounded three-star fill transition and optional
  shine;
- menu buttons use a `70 ms` press-down and `90 ms` release; the settings cog
  follows the same timing with a bounded turn;
- `set_reduced_motion(true)` removes ambient drift and tween travel while
  preserving usable state changes and legible endpoints.

The hanging stall lanterns and the counter lantern can share the same practical
light-motion state. Warm wood spill and dedicated wet-pavement reflection masks
remain a later registered-lighting pass.

## Live typography and license

Stall labels use the vendored, unchanged `LilitaOne-Regular.ttf` rather than
baked text. The font, upstream metadata, README, and full license are stored at:

`game/assets/fonts/lilita_one/`

Lilita One is licensed under the **SIL Open Font License 1.1**. The license
permits embedding and bundling the unmodified font with the game; the font may
not be sold by itself, the license and copyright notice must remain with the
font, and the reserved font name `Lilita` applies to modified versions. V010
uses the unmodified official Google Fonts distribution and preserves
`OFL.txt` beside it.

## Explicit scope exclusions

V010 does not include:

- the main Bentosaur character, its expressions, idle, blink, or service
  animation;
- customer/background dinosaur animation;
- navigation destinations behind Open Stall, Guestbook, Decorations, Pantry,
  or Settings;
- final economy, collection, pantry, or decoration systems;
- warm stall-wood spill or fixture-specific wet-pavement reflection masks;
- a production ultratall outpaint of the approved village background.

The empty service opening is therefore intentional evidence of scope, not a
missing V010 asset.

## Evidence status

Integration and automated/runtime evidence are complete. Founder phone-scale
approval remains open; no historical V008/V009 result is being reused.

- [x] **Complete Godot suite:** 21/21 contracts pass under Godot `4.7-stable`.
- [x] **Forward Mobile / Metal capture:** deterministic normal and
  reduced-motion captures both completed at `540 × 960`, 60 frames / 2 seconds.
- [x] **Registration and reduced-motion review:** the normal and reduced modes
  preserve the responsive stall registration and usable control endpoints.
- [ ] **PENDING — founder capture approval:** Mau reviews the complete V010
  composition at phone scale.

Capture and command record:
[Home Menu V010 runtime evidence](../../game/docs/runtime-captures/home-menu-v010-complete-stall-kit/README.md).

## Personal iOS gate

The existing export contract is configured for the personal project:

- Apple team: `53RJ43876F` (`mauvsantos@gmail.com` personal account);
- bundle identifier: `com.mauvsantos.bentosaur`;
- Godot exports the generated Xcode project with automatic signing locked to
  personal team `53RJ43876F`;
- debug export method: Apple Development;
- current target family: iPhone, minimum iOS `14.0`.

Company account and Mellow signing markers remain forbidden by the automated
signing contract. This checkpoint passed the executable device gate:

- [x] **Personally signed V010 export/build:** strict `codesign` verification
  passed with `Apple Development: Mauricio Vargas (CRAZV8U43J)`, team
  `53RJ43876F`, and bundle `com.mauvsantos.bentosaur`.
- [x] **Physical install and launch:** installed and launched on Mauricio's
  iPhone 17 Pro Max (`iPhone18,2`, iOS `26.5.1`); the running process was
  observed after launch.
- [ ] **PENDING — safe-area and aspect-ratio review with no stretch or black
  band.**
- [ ] **PENDING — touch/focus/disabled-state legibility at device scale.**
- [ ] **PENDING — rain, music, ambience, and anime-filter continuity.**
- [ ] **PENDING — procedural motion and reduced-motion review.**
- [ ] **PENDING — founder physical-device approval.**

The Xcode template emitted non-blocking warnings for empty camera, microphone,
and photo-library usage descriptions. V010 does not request those permissions;
the unused template capability/warnings should be removed before a release
archive.

## Rollback and authority

The V004 source pack and runtime manifest remain the visual and registration
authority. If V010 fails a runtime or device gate, correct the component scene,
motion, registration, or responsive staging; do not overwrite the approved
source art or collapse the modular layers into one flattened image.
