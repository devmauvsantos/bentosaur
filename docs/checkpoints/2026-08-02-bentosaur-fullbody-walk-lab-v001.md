# Checkpoint — Bentosaur full-body 2D walk lab v001

Date: 2026-08-02
Status: implemented and runtime-captured; founder motion review pending

## Why this checkpoint exists

The earlier skeleton lab proved only a stall-bound head, torso and hands. It
did not answer whether the complete dinosaurs shown walking through the
village could be animated convincingly as native 2D characters.

This checkpoint tests the actual locomotion problem with a dedicated
side-facing, prop-free, full-body dinosaur.

## Outcome

Native Godot `Skeleton2D` is technically viable for Bentosaur background
walkers.

The reusable character scene contains 17 real `Bone2D` nodes:

```text
Hip
├── Torso
│   ├── Neck → Head
│   ├── Far upper arm → Far lower arm
│   └── Near upper arm → Near lower arm
├── Far thigh → Far lower leg → Far foot
├── Near thigh → Near lower leg → Near foot
└── Tail base → Tail middle → Tail tip
```

The lab demonstrates:

- an opposing-arm/leg walk cycle;
- left/right traversal through whole-character mirroring;
- hips, knees, feet, shoulders and elbows moving independently;
- breathing and restrained tail-root motion;
- wave, look/listen and hop reactions;
- deterministic and randomized behavior;
- three simultaneous smaller walkers at background-NPC scale;
- a full bone overlay and reduced-motion mode.

## What this proves

- One side-view puppet can walk both horizontal directions.
- The same controller can drive multiple independently seeded NPCs.
- Props can later be separate nodes attached to hand sockets; they do not need
  to be baked into each dinosaur.
- Godot is not the animation bottleneck. The production cost is authoring
  clean directional part kits with hidden overlap artwork.

## What this does not prove

- A side-view drawing cannot rotate into front/back/diagonal views like a 3D
  model. Each required camera direction needs separate art or a view-swap
  animation.
- The visible joint rings are useful for the feasibility gate but too
  paper-doll-like for production close-ups.
- The tail source contained complete tail variants rather than actual
  connected segments. V001 renders one intact tail from the root bone while
  retaining a three-bone debug chain. A production tail should use a weighted
  `Polygon2D` mesh or correctly authored overlapping segments.
- Feet are baked into each lower-leg layer. A final walk may benefit from two
  or three replacement foot drawings at contact, passing and lift poses.
- This is not yet integrated into the approved Home or gameplay scenes.

## Production recommendation

Use a hybrid approach:

1. Skeleton bones for body weight, head, arms, legs and tail motion.
2. Small replacement drawings for blinks, mouths, hands and difficult foot
   contacts.
3. Direction-specific side/front/back kits that share bone names and motion
   timing.
4. A shared texture atlas for each species/color family before crowd use.

This gives Bentosaur the reusable animation benefit of a rig without forcing
every pose to look like hinged cardboard.

## Run it

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path /Users/mauvsantos/Workspace/games/Bentosaur/game \
  res://scenes/labs/bentosaur_fullbody_walk_lab.tscn
```

Controls:

- `Auto` — randomized walk, wave, look and hop behavior.
- `Bones` — reveal the complete skeleton.
- `Crowd` — show/hide the small traversing background walkers.
- `Still` — reduced-motion pose.
- `Idle`, `Walk`, `Wave`, `Look`, `Hop`, `Random` — isolate motions.

## Evidence

Runtime captures are stored under:

`game/docs/runtime-captures/bentosaur-fullbody-walk-lab-v001/`

The clean and bone-overlay captures use the same deterministic sequence.

## Verification

- Full-body walker contract: `PASS`.
- Complete Godot contract suite: `25/25 passed`.
- Asset builder: two consecutive builds produced byte-identical runtime
  outputs.
- Runtime capture: Godot 4.7 Forward Mobile, 540 × 960 evidence encode at
  30 FPS, with no script or engine errors.
- Approved Home and gameplay scenes remain unchanged.

## Rollback

The prior checkpoint is commit `203e0e7` (`feat: add native 2d skeleton
animation lab`). No approved game scene was changed by this experiment.
