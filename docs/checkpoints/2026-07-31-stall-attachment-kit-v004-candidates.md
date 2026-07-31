# Stall Attachment Kit V004 — Complete Candidate Gate

**Status:** source-art candidates complete; founder approval pending

**Runtime impact:** none

![Complete registered attachment candidate](../../art/source-assets/home-menu/stall/v004-attachment-kit/reviews/stall-attachment-full-context-approval-board-v001.png)

## Outcome

Every remaining non-character attachment requested for the home-menu stall now
has a preserved modular candidate:

- complete open stockpot body, separate lid, and contact shadow;
- procedural-steam destination contract;
- counter oil lantern with canonical OFF shell and separate ON core/halo;
- green food bowl;
- plant pot and foliage;
- empty bottle crate, three separate bottles, and assembled prefab preview;
- red counter cloth;
- rank plaque, empty/filled star states, and shine overlay;
- primary and secondary menu-button systems in normal, selected, pressed, and
  disabled states;
- detached leaf ornaments and live preview labels;
- settings control in normal and pressed states.

The main Bentosaur character remains deliberately excluded.

## Source authority

All prompts, immutable generated images, transparent derivatives, extracted
components, QA reports, hashes, and review boards are under:

`art/source-assets/home-menu/stall/v004-attachment-kit/`

The generated art was compared at registered phone scale against the approved
V009 stall. No candidate has been copied into `game/assets` or instantiated in
a Godot scene.

## Validation

- 31 required transparent components present;
- fully transparent corners on every component;
- zero detected magenta-fringe pixels;
- source files and local derivatives preserved separately;
- button and settings state silhouette consistency measured;
- placement and motion destinations captured in
  `placement-and-motion-contract.json`.

## Open visual decisions

- The clean rank plaque is brown. A V002 green recolor experiment is rejected
  because it contaminated the wood and socket edges. Founder decides whether
  brown is acceptable or a future controlled green paint pass is required.
- The counter lantern's canonical OFF shell uses honey-amber glass and may read
  faintly luminous even without the separate core and halo.
- Cloth, plant, pot, and bottle-crate proportions must be judged from the
  registered composite, not from their large source sheets.

## Next step after approval

Promote only approved components into versioned runtime folders, implement the
stockpot and counter-lantern reusable scenes, build the procedural steam effect,
wire NinePatchRect button states with native labels, and run the first on-device
tap/motion test. Warm hanging-lantern spill remains a later atmosphere pass.
