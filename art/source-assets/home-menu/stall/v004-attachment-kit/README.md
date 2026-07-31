# Stall Attachment Kit V004

**Visual gate:** G03 — Remaining non-character stall attachments

**Status:** complete source-art candidate gate; founder approval required before runtime promotion

This pack contains every remaining physical and interactive attachment for the
approved empty stall. The main Bentosaur character is explicitly out of scope.

## Complete inventory

### Counter props

- stockpot body with a finished open rim and dark interior;
- stockpot lid as a separate pivotable piece;
- procedural Godot steam emitter (no baked steam art);
- small counter oil lantern: one canonical OFF shell plus separate ON core,
  halo, and contact shadow;
- small green food/grape bowl;
- counter plant, preferably split into pot and foliage;
- bottle crate, with the crate and three bottles preserved as modular pieces;
- red patterned counter cloth.

### Stall UI

- rank plaque with three sockets;
- empty and filled star states plus an optional shine overlay;
- blank primary and secondary button frames, with normal, selected/focused,
  pressed, and disabled states;
- leaf ornaments separate from labels;
- compact settings/cog control with normal and pressed states;
- all labels rendered natively in Godot; no text is baked into the art.

## Shared visual contract

- Match the approved `bentosaur-home-menu-refined-classic-guestbook-v2.png`
  flat-cel storybook style: rounded forms, refined dark outlines, subtle painted
  grain, warm wood and amber accents, cool indigo-night context.
- Match the existing slightly top-down front perspective of the approved stall.
- Generate isolated modular pieces on flat `#FF00FF` chroma-key backgrounds.
- Never include a dinosaur, character, scenery, rain, smoke, steam, or baked UI
  lettering in a production component.
- Preserve every immutable generation result, prompt, extracted component, and
  registered review image.
- Nothing in this pack enters `game/assets` until the founder approves the
  registered visual approval board.

## Runtime behavior destination

- The pot lid idles with a restrained occasional rattle; steam is a procedural
  particle/line effect and stops when the pot is inactive.
- The counter lantern uses one unchanged shell for OFF and ON. ON adds core and
  halo layers; it does not use wind sway.
- Button press feedback is short and tactile (roughly 100–150 ms), using scale,
  translation, tint, and state art without bounce or elastic easing.
- Reduced-motion mode removes ambient prop motion while retaining essential
  short state transitions.

## Folder ownership during candidate generation

- `stockpot/` — stockpot body and lid;
- `counter-small/` — counter lantern and food bowl;
- `counter-decor/` — plant, bottle crate, bottles, and cloth;
- `ui/` — rank plaque, stars, button system, and settings control;
- `reviews/` — final registered approval board, assembled only after extraction.

## Candidate result

The full candidate kit is now generated, extracted, alpha-validated, and
registered against the approved V009 stall. It remains source art only.

Primary review evidence:

- `reviews/stall-attachment-full-context-approval-board-v001.png`
- `registered/stall-attachment-full-context-candidate-v001.png`
- `stockpot/reviews/stockpot-category-review-board-v001.png`
- `counter-small/reviews/counter-small-category-review-board-v001.png`
- `counter-decor/reviews/counter-decor-category-review-board-v001.png`
- `ui/reviews/ui-attachment-kit-category-board-v001.png`

The in-context board uses live preview labels and a procedural-steam mock. Those
pixels are not baked into any component.

## QA result

- 31 required transparent production components are present;
- all component corners are fully transparent;
- no surviving magenta-fringe pixels were detected;
- button-state and settings-state geometry measurements are preserved in the
  UI extraction report;
- prompts and immutable chroma outputs are retained beside every category;
- `manifest.json` records hashes and current review flags.

## Founder decisions still required

1. approve or revise the stockpot body/lid and registered scale;
2. decide whether the counter lantern's honey glass reads acceptably OFF;
3. approve plant, crate/bottles, bowl, and cloth at registered scale;
4. approve button visual states and settings control;
5. decide whether the clean brown rank plaque is acceptable or requires a
   controlled muted-green face paint pass.

The attempted plaque recolor V002 is retained only as rejected provenance. It
must not enter runtime assets.
