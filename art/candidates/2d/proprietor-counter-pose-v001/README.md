# Bentosaur proprietor counter pose — V001 candidate

Status: runtime promotion candidate; founder visual approval pending.

This gate answers one specific composition requirement: the proprietor is
front-facing with both connected arms bent forward and both three-clawed hands
resting on one invisible counter line. No stall, prop, rain, clothing, or
accessory is baked into the character.

The neutral source is the registration and appearance authority. The blink
generation is intentionally not a second whole-sprite runtime frame: the V002
builder takes only its eye pixels and keeps every pixel outside two feathered
eye masks registered to the neutral source. The foreground hand layer is also
cut from the neutral source, allowing Godot to render body → stall → hands.

## Built-in ImageGen mode

Built-in generation was used for both the identity-preserving neutral source
and the precise blink edit. Chroma removal was performed locally against the
uniform magenta backdrop.

Reference roles:

- pose/composition authority:
  `art/concepts/2d-chibi/v4/01_menu-refinement/bentosaur-home-menu-refined-classic-guestbook-v2.png`;
- character identity/style authority:
  `art/concepts/2d-chibi/v3/02_main-character-idle/registered/bentosaur-neutral-open-registered-v1.png`;
- blink edit target: the generated neutral magenta source in this folder.

## Neutral prompt

```text
Use case: identity-preserve
Asset type: Bentosaur mobile-game proprietor character source sprite
Input images: Image 1 is the exact pose and counter interaction authority; Image 2 is the exact clean character identity, proportions, palette, linework, and rendering-style authority.
Primary request: Create a clean front-facing cutout of the same green chibi triceratops proprietor from Image 2, posed exactly like the central proprietor in Image 1: calm friendly closed-mouth smile, torso facing forward, both arms naturally bent forward, with both small three-clawed hands resting symmetrically on one invisible horizontal counter edge. The forearms must connect continuously and anatomically from the shoulders to the hands. Include head, frill, horns, torso, complete bent arms, hands, and enough lower torso to hide behind a counter; legs and feet are not needed.
Style/medium: preserve the premium flat-cel 2D storybook style, dark clean outlines, gentle painted cel shading, warm cream horns and belly, muted sage-green body, coral cheeks. Match Image 2 exactly; do not redesign or make it more 3D, glossy, painterly, pixelated, or plush.
Composition/framing: centered straight-on orthographic game sprite, perfectly symmetrical registration, generous padding on every side. Hands share exactly the same baseline and are clearly separated from the torso silhouette at their fingertips. No perspective tilt.
Scene/backdrop: perfectly flat solid #ff00ff chroma-key background for local background removal. The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation. Do not use #ff00ff anywhere in the character.
Constraints: no stall, no counter, no table, no lantern, no food, no props, no clothing, no accessories, no rain, no text, no watermark, no cast shadow, no contact shadow. Keep only one character. Preserve the two large forehead horns, small nose horn, round frill knobs, black oval eyes with white highlights, coral cheek circles, soft smile, body palette, and childlike proportions. The hands must visibly rest on an invisible counter line rather than hang at the sides.
```

## Blink edit prompt

```text
Use case: precise-object-edit
Asset type: Bentosaur mobile-game proprietor blink-state source sprite
Input images: Image 1 is the exact edit target and must remain registered identically.
Primary request: Change only the two black open oval eyes into two small gentle closed-eye upward curves, matching the happy blink expression language of the supplied Bentosaur references. Keep the friendly closed mouth exactly unchanged.
Constraints: preserve the canvas size, subject position, silhouette, body proportions, frill, every horn, nose, cheeks, mouth, torso, arms, hands, finger positions, colors, outlines, shading, texture, and perfectly flat solid #ff00ff background exactly. Do not move, redraw, crop, rescale, relight, recolor, or restyle any part except the two eyes. No new objects, no text, no watermark. The background must remain one perfectly uniform #ff00ff chroma-key color.
```

## Reproduction

The built-in results were saved unchanged under `source/`. Transparent exports
were produced with the ImageGen skill's local helper:

```bash
python3 /Users/mauvsantos/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py \
  --input source/bentosaur-proprietor-counter-neutral-magenta-v001.png \
  --out exports/bentosaur-proprietor-counter-neutral-transparent-v001.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill \
  --edge-contract 1 \
  --force
```

Repeat with the blink source/output names. Runtime promotion is then:

```bash
python3 tools/art/promote_bentosaur_proprietor_counter_v002.py
```

The builder verifies source hashes, creates the registered blink, extracts the
foreground hands, performs alpha/registration QA, and writes a runtime manifest
under `game/assets/characters/bentosaur_proprietor/v002/`. Encoded PNG hashes
record the committed files; decoded RGBA hashes are the cross-encoder pixel
authority, so a Pillow/zlib upgrade cannot masquerade as an art change.
