# Bentosaur Menu Refinement v4 — Generation Prompts

Built-in ImageGen was used. No paid external API or Tripo credits were used.

## v1 — refined classic menu

```text
Use case: precise-object-edit
Asset type: portrait mobile game home-menu mockup
Input image: Image 1 is the edit target.

Primary request: Change only the lower menu-button assembly. Keep the entire
Bentosaur stall, proprietor, rainy Japanese-inspired village square,
pedestrians, plants, props, lighting, palette, top coin HUD, weather medallion,
BENTOSAUR roof sign, three stars, camera, crop, and 9:16 composition unchanged.

Replace the current four oversized plaques with four smaller, more refined
physical wooden-and-enamel menu plaques centered below the counter. Give them
visibly more vertical separation and generous internal padding. The letters
must be smaller, with ample breathing room between every word and every button
border. Preserve the existing tactile carved-wood, warm gold trim, flat-cel
painted game-art style. The first plaque may remain muted moss green as the
primary action; the three secondary plaques remain dark warm wood. Make the
primary plaque only subtly larger than the secondary plaques, not massive.

Render these labels exactly once, in this exact order and spelling, in friendly
title case:
"Open Stall"
"Guestbook"
"Decorations"
"Pantry"

Typography: friendly chunky hand-painted shop-sign display lettering with
proportions close to Lilita One; smaller and calmer than the original all-caps
letters; warm cream-gold fill with restrained dark carved outline; extremely
legible; optically centered; no letters touching borders; no extra words or
symbols.

Add one small detached circular settings button with a clear gear/cog symbol
and no text. Offset it slightly to the lower-right side of the menu group so it
feels like a secondary utility control, with the same wood, enamel, and
gold-trim material language. Keep its visual size modest but its surrounding
clear space sufficient for a mobile touch target.

Layout target: preserve more visible rainy street around and below the menu.
Use consistent refined spacing, approximately 20–28 image pixels between
plaques. Keep the entire menu group balanced and centered, with no overlap over
the owner or counter.

Constraints: edit only the menu plaques, their text, and the added settings
cog. Preserve every other character and object identity and location. Preserve
image dimensions and framing. No new characters, icons, currencies, banners,
badges, popups, labels, or decoration. Do not alter the BENTOSAUR title. Do not
misspell any requested label. No watermark.
```

## v2 — preservation correction

```text
Use case: precise-object-edit and compositing
Asset type: portrait mobile game home-menu mockup
Input images: Image 1 is the immutable edit target and base scene. Image 2 is a
reference ONLY for the redesigned lower menu plaques and detached settings
cog.

Primary request: Preserve Image 1's entire scene exactly: same 941x1672
framing, same pixels and composition for the BENTOSAUR roof sign, stars, owner
dinosaur, every pedestrian dinosaur and their exact positions, plants, pots,
counter, pots, lanterns, bottles, cloth, awning, buildings, rain, pavement,
reflections, coin HUD, weather medallion, lighting, colors, camera, and crop.
Do not borrow any background, stall, character, or prop change from Image 2.

Replace ONLY Image 1's four oversized lower menu plaques with the refined menu
assembly demonstrated in Image 2: four smaller centered separate
wooden/enamel plaques, more vertical separation, smaller title-case lettering
with generous internal padding, first plaque muted moss green, three secondary
plaques dark warm wood, and one small detached circular gear/cog settings
button offset to the lower-right.

Render these labels exactly once, in this exact order and spelling:
"Open Stall"
"Guestbook"
"Decorations"
"Pantry"

Typography: friendly chunky carved shop-sign display proportions close to
Lilita One; warm cream-gold fill; restrained dark outline; smaller and calmer
than Image 1; ample space between letters and borders; optically centered;
highly legible; no extra words.

Critical invariant: change only the lower menu assembly and reconstruct only
the tiny portions of wooden stall façade or wet pavement directly revealed by
making the plaques smaller. Every pixel outside that former menu footprint
should visually match Image 1, not Image 2. Keep Image 1's characters at their
original locations. No new characters, props, symbols, currencies, banners,
decoration, or text. Do not alter the BENTOSAUR title. No watermark.
```
