# Bentosaur Flat-Cel Direction Proof v2

**Status:** founder-selected leading visual direction; production proof pending

**Date:** July 30, 2026

**Generation tool:** built-in ImageGen

**Runtime engine:** Godot remains the proof engine

**Production approval:** the direction is selected; the generated rasters are not
production assets

Mau selected the flat-cel 2D direction after seeing the gameplay study. This
pack tests whether the same language survives a character expression change,
the between-days home/menu, and the physical regulars book.

## Start here

| Purpose | File |
| --- | --- |
| Neutral-to-happy motion board | `03_animation/boards/bentosaur-neutral-to-happy-motion-board-v1.png` |
| Transparent neutral character proposal | `01_character-expression/exports/bentosaur-neutral-fullbody-flat-cel-v1.png` |
| Transparent happy character proposal | `01_character-expression/exports/bentosaur-happy-fullbody-flat-cel-v1.png` |
| Home/menu screen | `02_screens/bentosaur-home-menu-flat-cel-v1.png` |
| Regulars-book screen | `02_screens/bentosaur-regulars-book-flat-cel-v1.png` |
| Book page-turn motion board | `03_animation/boards/bentosaur-book-page-turn-motion-board-v1.png` |
| Independent laugh marks | `03_animation/laugh-lines/laugh-mark-01.svg` through `laugh-mark-03.svg` |

## What this checkpoint establishes

- The selected gameplay language extends coherently to the hub and book.
- Regular and delighted expressions can share one character identity.
- The three laugh marks are independent overlay sprites, not part of the happy
  face.
- The book can remain a physical object in 2D by separating page front,
  underside, fold shadow, next-spread content, and binding.
- Godot can own all timing, input, state, particles, dynamic UI, and page
  deformation.

## What these files are not

The two transparent characters are cleaned concept proposals, not a finished
cutout rig. They currently contain whole poses. A production character must be
redrawn into registered layers with deliberate hidden overlap at joints.

The menu and book are screen targets, not shippable flattened screenshots.
Counters, buttons, page content, street walkers, weather, rain, steam, lantern
flicker, and seasonal dressing must remain separate runtime elements.

The page-turn board is motion direction. The four images are not intended to
be played as a sprite sequence. Production uses one deformable page driven by
a continuous `turn_progress` value.

## Production character contract

Every export uses the same canvas size, origin, and neutral registration point.

```text
bentosaur_customer_front
├── shadow
├── tail_back
├── legs
├── body
├── belly_patch
├── arm_left
├── arm_right
├── hand_left
├── hand_right
├── head_base
├── cheeks
├── eyes_slot
│   ├── open
│   ├── blink
│   └── happy
├── mouth_slot
│   ├── soft_smile
│   ├── open_smile
│   ├── chew_a
│   └── chew_b
├── accent_fx
│   ├── laugh_mark_01
│   ├── laugh_mark_02
│   └── laugh_mark_03
├── hand_socket_left
├── hand_socket_right
└── prop_socket_center
```

`head_base` contains no eyes, mouth, or laugh marks. The happy hand pose may be
a discrete hand/arm attachment swap; body bounce and arm travel remain
transform animation.

## Book contract

```text
regulars_book
├── cover_and_binding
├── page_stack
├── current_spread
├── next_spread
├── turning_page_front
├── turning_page_underside
├── fold_shadow
├── dynamic_portraits_and_memories
├── page_counter
└── input_surface
```

The page turn has one continuous input:

```text
turn_progress = 0.0  # page resting on the right
turn_progress = 1.0  # page settled on the left
```

The drag controls this value directly. Releasing commits or cancels, then a
short cubic ease settles the remaining distance. The data model changes page
only after a committed settle completes.

## Source and approval rules

- `v1/.../bentosaur-gameplay-2d-flat-cel-v2.png` remains style authority.
- The former 3D hybrid screens remain composition authority only.
- Generated screens may not silently become sprite atlases or UI layouts.
- No cast expansion begins until one front character rig and one side-walk rig
  animate successfully in Godot at phone scale.
- Mau remains the approval owner for final character layers, animation timing,
  page feel, UI, and every production asset.

Exact prompts and reference roles are in `prompts.md`. Hashes and provenance
are in `manifest.json`.
