# Bentosaur Menu Alternatives and Main-Character Idle Proof v3

**Status:** Active visual exploration; production layer reconstruction pending

**Date:** July 30, 2026

**Generation tool:** built-in ImageGen

**Runtime proof target:** Godot 4.7.1

## Start here

| Purpose | File |
| --- | --- |
| Four-menu comparison | `03_boards/bentosaur-home-menu-alternatives-board-v1.png` |
| Classic text menu | `01_menu-alternatives/bentosaur-home-menu-classic-stall-text-v1.png` |
| Diegetic hotspot menu | `01_menu-alternatives/bentosaur-home-menu-diegetic-hotspots-v1.png` |
| Threshold dock menu | `01_menu-alternatives/bentosaur-home-menu-threshold-dock-v1.png` |
| Transparent mascot state sheet | `02_main-character-idle/exports/bentosaur-core-state-sheet-transparent-v1.png` |
| Registered prototype sprites | `02_main-character-idle/registered/` |
| Animated idle preview | `02_main-character-idle/bentosaur-idle-prototype-v1.gif` |

## Menu alternatives

### 1 — Icon grid

The v2 baseline keeps four large equal controls in a lower 2×2 grid.

- strongest balance of scanability, thumb size, and environmental visibility;
- conventional but still tactile;
- consumes the most vertical world space after the classic text menu.

### 2 — Diegetic hotspots

The four controls are visually attached to stall objects.

- most immersive and most specific to Bentosaur;
- makes the stall itself feel like the player's home;
- weakest reading order and most vulnerable to seasonal-decoration overlap;
- requires consistent screen-space hit plates even when the art looks physical.

### 3 — Threshold dock

The four equal icons occupy one horizontal row along the bottom curb.

- fastest repeat-use scan and strongest thumb reach;
- leaves the stall and square unobstructed;
- narrower buttons make icon simplification and small-screen testing important;
- feels slightly more like a conventional mobile toolbar.

### 4 — Classic text menu

The stall façade becomes a vertical text menu while the rainy square remains
alive behind it.

- strongest first-session clarity;
- explicit labels reduce icon-learning cost;
- establishes the `BENTOSAUR` title cleanly;
- requires real localized Godot text and adaptive button sizing;
- occupies more of the lower scene than the other structures.

The generated lettering is visual direction only. Production recreates the
buttons with real `Control`, `Label`, focus, localization, accessibility, and
safe-area behavior.

## Does every dinosaur need an idle?

Yes, but not a unique frame-by-frame sheet.

Every visible dinosaur receives:

1. a shared breathing loop;
2. a randomized blink;
3. a randomized start phase so crowds never synchronize;
4. one role/species-specific micro-action only where the camera can read it.

Examples of micro-actions include a tail flick, curious glance, foot shuffle,
small wave, smelling steam, or checking the rain. Background walkers can use a
cheaper two-layer or whole-sprite idle. The proprietor and counter customer use
the full face/arm attachment rig.

## What was generated for the main Bentosaur

One coherent source sheet contains:

- neutral/open;
- neutral/blink;
- gentle wave;
- delighted/hands-to-cheeks.

The chroma background was removed and all four states were normalized to a
common `512 × 576` transparent canvas with bottom-center registration.

Neutral and blink are unusually consistent for generated composite sprites:
their binary alpha silhouettes differ by only `869` pixels out of roughly
`128,159` union pixels, under `0.7%`. That is stable enough for the included
prototype idle.

It is not sufficient to call the whole-body state swap a final production rig.
Small color, line, and interior-shading differences remain. Shipping art must
reuse one shared body and change only registered eye, mouth, and arm layers.

## Included idle prototype

`bentosaur-idle-prototype-v1.gif` and `.mp4` demonstrate:

- a `3.4 s` grounded breathing loop;
- approximately `0.5%` vertical expansion;
- compensating horizontal contraction;
- one `0.17 s` blink;
- feet anchored to the same baseline.

The preview is rendered evidence, not runtime code. Godot should reproduce the
motion parametrically and schedule blinks independently.

## Production sprite kit for the main Bentosaur

The smallest complete front-facing kit is:

```text
body_base.png          # no arms, eyes, or mouth
arms_neutral.png
arms_wave.png
arms_happy.png
eyes_open.png
eyes_blink.png
eyes_happy.png
mouth_neutral.png
mouth_happy.png
laugh_mark_01.png
laugh_mark_02.png
laugh_mark_03.png
```

Every character layer except the trimmed laugh marks uses the same untrimmed
canvas, bottom-center origin, and export scale.

```text
BentosaurFrontIdle
├── ArtRoot
│   ├── BodyBase
│   ├── ArmsNeutral
│   ├── ArmsWave
│   ├── ArmsHappy
│   ├── Eyes
│   ├── Mouth
│   └── LaughMarks
├── BodyMotionPlayer
├── ExpressionPlayer
├── BlinkTimer
└── StateController
```

### Runtime timing

- Breathing: `3.4 s`, random session speed `0.94–1.06×`, random start phase.
- Blink: `0.18 s`, scheduled every `2.3–5.4 s`.
- Double blink: `12%` chance, second blink `0.14 s` after reopening.
- Home-screen wave: optional micro-action every `8–14 s`, never while a higher
  priority reaction is active.
- Happy reaction: `0.32 s` entrance, independent accent pops at `0.11`,
  `0.15`, and `0.19 s`.

Priority is `happy reaction > wave > blink > breathing`.

## Approval boundary

The state sheet proves that AI can propose consistent source poses and usable
prototype composites. It does not prove that independent generation can
produce final registered layers. The next production task is one controlled
reconstruction of the approved neutral, blink, wave, and delighted designs into
the layer kit above. No additional mascot action library should be generated
before that master works in Godot.

Exact prompts and source roles are in `prompts.md`. File hashes and output
roles are in `manifest.json`.
