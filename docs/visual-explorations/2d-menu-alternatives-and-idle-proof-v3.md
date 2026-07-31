# 2D Menu Alternatives and Main-Character Idle Proof v3

**Status:** Active visual exploration; production layer reconstruction pending

**Date:** July 30, 2026

## Result

The flat-cel direction now has four coherent home-menu structures:

1. icon grid;
2. diegetic stall hotspots;
3. horizontal threshold dock;
4. classic stall-shaped text menu.

The classic text version most directly answers Mau's latest direction: a
traditional readable menu integrated into the stall, with the small rainy
Japanese-inspired villa square still active behind it.

The main Bentosaur also has one coherent four-state source sheet, transparent
cropped states, registered prototype canvases, and an actual rendered idle
loop.

## Menu recommendation

Do not lock purely from the concept render.

- Use the classic text menu as the clarity benchmark.
- Use the diegetic hotspot menu as the emotional/differentiation benchmark.
- Use the threshold dock as the repeat-use speed benchmark.
- Keep the icon grid as the balanced control.

The first Godot UI proof should implement the classic menu and one compact
icon-based alternative with real controls, localization, safe areas, focus,
touch targets, and a physical phone test. The generated text is never shipped.

## Idle architecture

Every dinosaur needs visible life, but not bespoke full-body frames for every
blink and breath. The scalable system is:

```text
shared body motion
+ discrete eye/mouth attachments
+ optional arm/hand pose
+ one low-frequency signature action
+ randomized timing and phase
```

For crowds:

- start every breathing loop at a random phase;
- choose a stable per-instance speed within `0.94–1.06×`;
- schedule blinks every `2.3–5.4 s`;
- suppress off-camera animation work where possible;
- avoid triggering identical signature actions simultaneously.

For the front-facing proprietor:

- `3.4 s` breathing loop;
- `0.18 s` blink;
- optional wave every `8–14 s`;
- neutral/happy facial attachments;
- three independent laugh marks;
- state priority `reaction > wave > blink > breath`.

## Generation finding

Generating all four states in one sheet produced strong identity continuity.
Neutral and blink alpha silhouettes differ by less than `0.7%`, which is good
enough for a visual prototype.

It still does not solve production registration by itself. Full-body generated
states contain small interior shading and line differences. Repeated texture
swaps can therefore shimmer even when silhouettes align.

## Production conclusion

AI can generate the complete source-pose vocabulary for the main Bentosaur.
It should not independently generate the shipping layer files.

The production step is one controlled reconstruction into:

```text
body base
neutral / wave / happy arm layers
open / blink / happy eye layers
neutral / happy mouth layers
three accent marks
```

All main layers share one artboard and origin. Godot animates the shared body,
selects attachments on discrete tracks, and randomizes timing. Frame-by-frame
sprites remain reserved for actions with major silhouette/contact changes.

## Evidence

All generated screens, sprite sources, registered prototype states, animation
previews, exact prompts, roles, and hashes live in:

`art/concepts/2d-chibi/v3/`
