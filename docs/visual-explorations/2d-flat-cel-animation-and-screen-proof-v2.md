# 2D Flat-Cel Animation and Screen Proof v2

**Status:** Active visual direction; production proof pending

**Date:** July 30, 2026

**Founder decision:** flat-cel 2D is the leading direction for now

**Engine:** Godot remains the implementation proof target

**Production assets approved:** None

## Decision

Continue the flat-cel route. It preserves the warmth and identity of the
approved gameplay concept while giving the project a realistic animation and
asset-production model:

- reusable body layers and facial attachments instead of regenerating every
  pose;
- isolated effects and props;
- Godot-driven bones, transforms, sprite swaps, particles, UI, and shaders;
- a dynamic physical book rather than a library of full-screen page-turn
  renders.

The matching home/menu and book concepts were generated at Mau's explicit
request. This supersedes the earlier "do not generate additional screens
before the rig proof" research restriction. It does not make the generated
screens production assets.

## Character expression construction

The production rig must use one registered master, not two complete generated
characters.

```text
BentosaurCustomer2D
├── ArtRoot
│   ├── Shadow
│   ├── Tail
│   ├── Legs
│   ├── Body
│   ├── ArmsNeutral
│   ├── ArmsHappy
│   └── HeadBase
├── FaceSlots
│   ├── Eyes
│   └── Mouth
├── AccentFX
│   ├── LaughMark01
│   ├── LaughMark02
│   └── LaughMark03
├── PropSockets
└── AnimationPlayer
```

`HeadBase` contains no eyes, mouth, or accent marks. Eye and mouth textures use
discrete animation tracks. Arms may use bones for ordinary motion and a
registered attachment swap for the cheek-hugging silhouette.

### Neutral-to-happy timing

| Time | Change |
| --- | --- |
| `0.00 s` | neutral eyes, soft smile, relaxed arms |
| `0.00–0.06 s` | 4% anticipation squash |
| `0.07 s` | discrete happy-eye, open-mouth, and cheek-hand pose swap |
| `0.07–0.22 s` | slight upward overshoot and spring settle |
| `0.11 s` | laugh mark 01 pops from 65% scale |
| `0.15 s` | laugh mark 02 pops |
| `0.19 s` | laugh mark 03 pops |
| `0.30–0.35 s` | stable happy endpoint |

Each accent gets its own position, rotation, scale, and alpha track. The face
still reads as happy if all accents are disabled. Reverse the same clip to
return to neutral so rapid state changes do not queue conflicting reactions.

### First production expression kit

```text
eyes_open
eyes_blink
eyes_happy

mouth_soft_smile
mouth_open_smile
mouth_chew_a
mouth_chew_b

hands_relaxed
hands_cheeks
hands_receive
hands_hold_food
```

Author this kit in an editable vector/layer master, with hidden color bleed
under every joint. Export each runtime raster from the same artboard and
registration point.

## Book page-turn construction

The book uses one reusable object:

```text
BookView
├── BookBase
├── CurrentSpread
├── NextSpread
├── TurningPageFront
├── TurningPageUnderside
├── FoldShadow
├── PageCounter
├── PreviousButton
├── NextButton
├── PageAudio
└── PageTurnController
```

The current and next spread are rendered beneath the page. The turning page is
a lightly subdivided 2D mesh with registered front and underside art. A
`canvas_item` shader and/or vertex deformation maps `turn_progress` from `0`
to `1`, clips the page silhouette, reveals the underside, and moves one
controlled cel shadow.

The implementation must not bake every book spread into a new full-screen
image. Portraits, hearts, snapshots, discovery slots, and page numbers are
data-bound content.

### Interaction state

```text
IDLE
  → DRAGGING
      → SETTLING_COMMIT → IDLE
      → SETTLING_CANCEL → IDLE
```

1. Touch begins in the outer 18% of a page.
2. Horizontal drag sets `turn_progress` continuously.
3. Release commits at `progress >= 0.45` or on a strong destination-directed
   fling; otherwise it cancels.
4. A killable cubic-out Tween settles the remaining distance in `0.10–0.24 s`.
5. Only after a committed settle finishes does the page index change and the
   next pair of page textures bind.
6. Paper sound fires near the fold apex; a short optional haptic fires on the
   final settle.

The first device proof should use 12–16 horizontal mesh strips. Increase only
if the silhouette shows visible faceting at phone scale.

### Reduced motion

- Happy expression: apply endpoint face/hand layers immediately, with an
  optional opacity-only fade shorter than `80 ms`.
- Book: keep visible previous/next buttons and swap content immediately or
  with the same short opacity fade.
- Sound and haptic remain independently configurable.

## Screen construction

### Home/menu

The generated screen is composition authority for:

- top coin, daily stars, and weather/season summary;
- the physical stall as the upgradeable home;
- living background walkers, rain, steam, lanterns, puddles, and plants;
- four destinations: open, book, pantry, and decoration/seasons.

Production separates the environment, proprietor, walkers, weather, props,
and four real touch controls. A seasonal change modifies bounded layers and
color grade; it does not regenerate the entire screen.

### Regulars book

The generated screen is visual authority for the book's materials, framing,
page hierarchy, portrait treatment, and curl. Production separates the counter
scene, book base, spread content, turning page, shadow, buttons, and counter.

## Acceptance gate before cast expansion

Build one Godot proof with:

1. front-facing idle, blink, neutral-to-happy, and chew;
2. three independently controllable laugh marks;
3. side walk east plus mirrored west;
4. one independent prop socket;
5. one draggable page turn with commit, cancel, sound, haptic, and reduced
   motion;
6. phone-scale silhouette, frame-time, memory, and touch checks.

If this feels excellent on a physical phone, make flat-cel 2D the production
lock and retire the active 3D facial-topology path. If it fails emotionally or
operationally, preserve this pack and reopen the live-3D route with evidence.

## Evidence

All visual evidence, transparent proposals, exact prompts, hashes, and source
roles live in:

`art/concepts/2d-chibi/v2/`
