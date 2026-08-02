# Bentosaur Skeleton Animation Lab V001

**Status:** implemented and runtime-verified; founder visual review pending

**Date:** 2026-08-02

## Purpose

This lab is a deliberately small feasibility gate for painted 2D character
animation. It tests whether a Bentosaur guest can retain the approved flat-cel
illustration while a native Godot `Skeleton2D` supplies restrained secondary
motion.

It is not a production character, a final asset-cutting specification, or a
promise that every expression can be synthesized from bones. The useful
question is narrower: can one layered puppet breathe, look, react, and settle
without becoming rubbery or requiring a full-frame sprite sheet?

## Run the lab

From the repository root:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  res://scenes/labs/bentosaur_skeleton_animation_lab.tscn
```

Or open `game/project.godot`, then open and run:

`res://scenes/labs/bentosaur_skeleton_animation_lab.tscn`

Run its headless contract with:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/bentosaur_skeleton_animation_lab_test.gd
```

## What to inspect

Use the on-screen controls rather than editing the character scene while
judging the proof:

- **Nod**, **Look**, **Hands**, **Chew**, and **Delight** trigger one named
  gesture;
- **Random** chooses a gesture from that same set;
- **Auto** schedules quiet randomized gestures between idle periods;
- **Bones** reveals the pivot hierarchy for explanation;
- **Still** enables the reduced-motion rest pose while retaining blink swaps;
- **Reset** cancels the current gesture and returns to the current idle pose.

The behavioral API behind those controls is intentionally small:

```text
trigger_gesture(name)
trigger_random_gesture()
reset_pose()
step_motion(delta)
set_auto_mode(enabled)
set_show_bones(enabled)
set_reduced_motion(enabled)
set_deterministic_test_mode(enabled, seed)
get_current_gesture()
```

The puppet contract is:

```text
CharacterStage/GuestPuppet/Skeleton2D/TorsoBone
├── HeadBone
├── LeftArmBone
└── RightArmBone
```

The overlay is an explanation aid only. It should not appear in the game.

## Known limitations

- This proof uses a small, purpose-cut layer set. It cannot invent a hidden
  side of the head, arm, or body.
- Large pose changes, perspective changes, turns, hands interacting with
  ingredients, and strongly different mouth silhouettes still need authored
  replacement art or a compact sprite sequence.
- Bone transforms are best for breathing, tiny head tilts, arm settles, body
  squash, and similarly restrained motion. Excessive rotation or mesh
  deformation will make the painted character look like a paper puppet.
- Blinks, mouths, laugh marks, hearts, steam, and other crisp graphic changes
  should generally remain image swaps or effects rather than bone deformation.
- V001 includes the neutral and blink head swaps. `MouthOpen`, `MouthChewA`,
  and `MouthChewB` are intentionally empty extension points because extracting
  a safe mouth from the flattened source would require destructive inpainting.
  Chew and delight therefore demonstrate skeletal motion, not final facial
  artwork.
- The lab demonstrates authoring feasibility. It does not yet measure the
  memory and batching cost of a complete customer cast on a physical iPhone.

## Automated acceptance gate

The lab is not accepted unless the headless contract confirms all of the
following:

- the scene loads and advances frames without missing dependencies;
- the stable `Skeleton2D` and four named `Bone2D` nodes exist at their
  documented paths;
- all five required puppet sprites use their canonical, loadable textures;
- the three intentionally optional mouth placeholders may remain empty, but
  any future texture assigned to them must be loadable;
- manual and seeded-random gesture APIs work;
- repeated `reset_pose()` calls return every bone to the same baseline without
  cumulative drift;
- long-running gesture samples remain inside the agreed translation, rotation,
  and scale budgets;
- reduced motion never amplifies movement and returns cleanly to baseline;
- the lab can be instantiated, stepped, and freed in a headless run.

## Founder visual acceptance gate

Automation cannot approve the look. V001 passes only if all answers below are
yes on the target phone:

1. Does the character still read as the approved Bentosaur illustration rather
   than a collection of hinged pieces?
2. Are the seams between the head, torso, and arms invisible during normal
   motion?
3. Do breathing and random gestures make the guest feel alive without pulling
   attention away from the bento decision?
4. Does the reset pose match the original illustration exactly?
5. Is reduced motion calm and compositionally stable?
6. Is the visual gain large enough to justify cutting future guests into the
   same layer contract?

If the answer to seams or silhouette preservation is no, stop. The fallback is
not more deformation; it is fewer bones plus expression swaps and short,
authored sprite sequences for the actions that truly change silhouette.

## Verification record

- Headless import: **pass**
- Skeleton animation lab contract: **pass**
- Full existing Godot contract suite: **24/24 pass**
- Deterministic Forward Mobile art capture: **pass**, 540 × 960, 30 FPS,
  18 seconds
- Deterministic Forward Mobile bone-overlay capture: **pass**, 540 × 960,
  30 FPS, 18 seconds
- Engine warnings/errors during the verified lab contract: **none**
- Registered rest reconstruction: **1,781 / 885,760 pixels differ**, confined
  to the provisional hidden-neck gate
- Physical iPhone review: **pending**
- Founder decision: **pending**

## Captured evidence

- `game/docs/runtime-captures/bentosaur-skeleton-animation-lab-v001/`
  `bentosaur-skeleton-lab-art-v001.mp4`
- `game/docs/runtime-captures/bentosaur-skeleton-animation-lab-v001/`
  `bentosaur-skeleton-lab-bones-v001.mp4`
- matching six-frame contact sheets live beside the videos;
- the raw Movie Maker AVI intermediates are not part of the retained evidence.
