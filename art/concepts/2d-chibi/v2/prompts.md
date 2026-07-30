# Flat-Cel Direction Proof v2 — Generation Prompts

Generation mode: built-in ImageGen

Date: July 30, 2026

## Expression pair

Reference 1:
`art/concepts/2d-chibi/v1/01_generated-exploration/bentosaur-gameplay-2d-flat-cel-v2.png`

Role: style and in-game identity authority.

Reference 2:
`art/turnarounds/triceratops_master_v2/neutral-no-catchlight/inputs-v1/bentosaur_front.png`

Role: neutral expression and front-facing proportions.

Reference 3:
`art/turnarounds/triceratops_master_v3/open-mouth-delighted/inputs-v1/bentosaur_front.png`

Role: delighted open-mouth expression.

```text
Use case: identity-preserve game character asset exploration.
Asset type: two-pose 2D character expression sheet for a mobile game cutout rig.

Input images:
- Image 1 is the REQUIRED flat-cel visual style and final in-game character
  identity reference. Match its sage-green biped baby triceratops, cream horns
  and frill knobs, peach cheeks, thick dark warm outline, compact chibi
  proportions, graphic cel shadows, tiny restrained texture, and cute
  handmade mobile-game finish.
- Image 2 is the neutral expression and front-facing body/proportion reference.
- Image 3 is the delighted open-mouth expression reference.

Primary request:
Create exactly TWO front-facing full-body drawings of the exact same Bentosaur
character, aligned side-by-side at identical scale, baseline, silhouette,
proportions, color, lighting, and line weight.
LEFT = REGULAR/NEUTRAL: oval open eyes with small highlights, tiny gentle
closed smile, relaxed arms down.
RIGHT = HAPPY: closed upside-down-U happy eyes, broad open smiling mouth with
dark warm interior and coral tongue, both hands touching the cheeks as in
Image 1.

Style/medium:
Production-friendly flat cel 2D game art. Smooth coherent silhouettes, broad
flat color fills, thick dark-brown outlines, one restrained hard-edged shadow
tone and one small highlight tone. No 3D render, no volumetric shading, no
painterly gradients, no photorealism, no pixelated edges.

Scene/backdrop:
Perfectly flat uniform solid #ff00ff magenta chroma-key background. No floor,
cast shadow, gradient, vignette, texture, reflection, or lighting variation.

Composition:
Wide landscape sheet. Two figures only. Generous clear padding around and
between them. Entire frill, horns, tail, hands, and feet visible. No overlap.
Both figures must be easy to crop into separate assets.

Critical constraints:
- Do not redesign the dinosaur. Preserve the exact face, frill, three facial
  horns, ring of cream frill knobs, body shape, belly patch, three fingers,
  three toes, and short tail.
- NO laugh/emphasis/accent lines anywhere. Those three marks will be separate
  overlay sprites.
- No props, clothing, accessories, food, bento, umbrella, labels, captions,
  arrows, frames, dividers, UI, scenery, text, watermark, or extra characters.
- Do not use #ff00ff inside either character.
- Crisp antialiased edges suitable for local chroma-key removal.
```

Post-processing:

```text
remove_chroma_key.py
  --auto-key border
  --soft-matte
  --transparent-threshold 12
  --opaque-threshold 220
  --despill
```

The transparent pair was split into left/right proposals. That operation does
not create production-ready cutout layers.

## Home / main menu

Reference 1: selected flat-cel gameplay screen.

Reference 2: `art/concepts/ui-3d-hybrid/bentosaur-stall-hub-ui-v1.png`.

Reference 3: generated expression pair.

```text
Use case: identity-preserve mobile game UI mockup.
Asset type: Bentosaur between-days HOME / MAIN MENU screen.

Input images:
- Image 1 is the REQUIRED final flat-cel visual language: exact warm dark
  outlines, graphic cel color blocks, restrained texture, rainy indigo street,
  amber lantern light, sage-green baby triceratops, wood-and-enamel UI.
- Image 2 is the REQUIRED composition and information-architecture reference
  for the home hub only.
- Image 3 is the character identity/expression sheet; use the same exact
  Bentosaur design.

Primary request:
Recreate Image 2's home hub as a polished portrait 9:16 FLAT-CEL 2D mobile game
screen in Image 1's exact visual language. This is the player's cozy
between-days menu after closing the bento stall.

Composition:
- Top HUD: coin medallion with exactly “00” on the left, a compact three-star
  daily summary centered, circular rainy-weather/season medallion on the right.
- Middle: centered full view of the same small wooden dinosaur bento stall,
  partly closed and resting at blue hour after rain. Warm glowing lanterns,
  wet street reflections, curling steam, potted plants and flowers. The same
  sage-green Bentosaur owner stands behind the counter, happy and waving.
  Several small biped dinosaur neighbors stroll in the background.
- Lower third: exactly four large tactile square icon buttons in a clean 2×2
  layout: hanging OPEN SIGN, red REGULARS BOOK, PANTRY BASKET with
  rice/berries/leaves, and glowing LANTERN WITH LEAF for decoration/seasons.
  Icons only; no labels.
- Leave safe margins and strong touch targets.

Style/medium:
Purpose-built 2D mobile game UI. Thick warm dark-brown outlines, broad flat
color regions, simplified cel shadows, small crisp highlights, subtle handmade
grain only inside shapes. Cozy illustrated chibi diorama composition, but
absolutely rendered as layered 2D cel art rather than 3D.

Continuity constraints:
- Preserve the exact Bentosaur proportions, three facial horns, ring of cream
  frill knobs, green body, cream belly, peach cheeks.
- Preserve the same stall roof silhouette, red awning, dinosaur emblem,
  lantern warmth, wet blue street, neighborhood scale, and red book.
- No copyrighted characters or logos.
- No additional menus, banners, currencies, badges, popups, sale prompts, XP
  bars, labels, paragraphs, or unreadable decorative text.
- No photorealism, 3D render, clay, plastic, isometric map, pixelated edges, or
  watermark.
```

## Regulars book

Reference 1: selected flat-cel gameplay screen.

Reference 2: `art/concepts/ui-3d-hybrid/bentosaur-album-page-turn-ui-v1.png`.

Reference 3: generated expression pair.

```text
Use case: identity-preserve mobile game UI mockup.
Asset type: Bentosaur REGULARS BOOK / collection album screen at the middle of
an interactive page turn.

Primary request:
Recreate the composition reference as a polished portrait 9:16 FLAT-CEL 2D
mobile game screen in the selected gameplay screen's exact visual language.
It must look like a physical keepsake album lying on the wooden stall counter,
caught at a tactile mid-page-turn moment.

Composition:
- Thin top environmental band: flat-cel rainy street and warm lanterns beyond
  the counter. Back arrow top left. Coin medallion with exactly “00” top right.
- Large open physical book: forest-green cover edge, brown stitched binding,
  warm cream pages, visible page stack and spine.
- Left page: one large same sage-green Bentosaur portrait in delighted
  hands-on-cheeks pose; exactly two filled coral hearts and one empty outlined
  heart; exactly two memory snapshots, one umbrella and one bento.
- Center: one page rises and curls right-to-left. Show a cream front, darker
  tan underside, one hard-edged moving fold shadow, and attachment to the spine.
- Right page partly revealed: a different purple baby dinosaur, exactly four
  empty discovery slots, and exactly three empty outlined hearts.
- Bottom center: counter reading exactly “3 / 12”.

Style/medium:
Purpose-built layered 2D game art. Thick dark-brown contours; flat parchment;
one hard-edged tan page-shadow tone; broad graphic shapes; small crisp
highlights; subtle grain inside shapes only. Physical depth comes from overlap,
silhouette, and controlled shadow shapes, not 3D rendering.

Critical constraints:
- Preserve Bentosaur identity.
- Make the page physically understandable: front, underside, hinge, fold,
  shadow, and next-page reveal.
- Render only “00” and “3 / 12”; no headings or fake handwriting.
- No extra hearts, snapshots, slots, currencies, stars, weather badge,
  popups, menu buttons, clay, plastic, 3D rendering, soft AO, lens blur,
  painterly gradients, pixelated edges, or watermark.
```

## Page-turn key poses

Reference: generated flat-cel regulars-book screen.

```text
Create a wide four-panel animation sheet showing the SAME open physical album
and SAME page moving from right to left. All panels use the same camera, book
dimensions, spine position, palette, line weight, page content, and counter
background.

1. REST / 0%: page lies flat on the right.
2. LIFT / 25%: lower-right corner curls inward; underside first appears.
3. ARCH / 60%: tall central C-shaped arch with front, underside, and moving
   shadow clearly separated.
4. SETTLE / 100%: page has landed flat on the left; new spread visible.

Use flat-cel production key poses. Keep each page connected to the binding.
No labels, numbers, arrows, hands, HUD, text, watermark, 3D rendering, or
photorealism.
```
