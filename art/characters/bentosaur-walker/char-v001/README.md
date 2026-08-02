# Bentosaur side walker — character source v001

This folder contains the first full-body, side-facing 2D source authored
specifically to answer the background-NPC locomotion question. It is an
isolated feasibility character, not a replacement for an approved gameplay
character.

## Source images

- `source/bentosaur_walker_side_master_chroma_v001.png` — assembled side-view
  identity on a removable magenta background.
- `source/bentosaur_walker_side_master_transparent_v001.png` — locally keyed
  assembled reference.
- `source/bentosaur_walker_side_puppet_sheet_chroma_v001.png` — exploded
  paper-doll source sheet.
- `source/bentosaur_walker_side_puppet_sheet_transparent_v001.png` — locally
  keyed puppet source.

The images were generated with the built-in image-generation workflow using:

1. The approved flat-cel full-body proprietor as the identity/rendering
   reference.
2. The approved Bento Garden world concept as the character-family and
   environmental-scale reference.

## Final source prompt — assembled walker

> Create one complete cute green bipedal triceratops in a clean true
> side-profile neutral walking rest pose, facing screen-right. Preserve the
> approved Bentosaur flat-cel storybook language: oversized rounded head and
> frill, cream horns and belly, small torso, two distinguishable arms, two
> distinguishable stout legs and feet on one ground line, and a long tapered
> tail. Keep far limbs slightly offset, limbs away from the torso, and the
> whole character prop-free. Isolate it on a perfectly flat solid `#ff00ff`
> chroma-key background with no shadow, floor, text, watermark, 3D/plastic
> rendering, or cropped anatomy.

## Final source prompt — puppet kit

> Convert the exact side-facing dinosaur into an exploded 2D paper-doll parts
> sheet. Do not show an assembled character. Provide separate non-touching
> head, torso, near/far upper and lower arms, near/far thighs and lower
> legs/feet, and tail artwork with rounded hidden joint overlap. Preserve the
> same palette, line weight, paper texture and screen-right orientation. Use a
> perfectly flat `#ff00ff` background; no labels, guide lines, props, duplicate
> heads or torsos, floor, shadow, text, watermark, pixel art, or 3D rendering.

## Deterministic runtime build

Run:

```sh
python3 tools/art/build_bentosaur_fullbody_walker_assets.py
```

The builder trims the separated pieces and writes the runtime kit plus a hash
manifest to:

`game/assets/characters/bentosaur_walker/v001/`

## Known v001 compromises

- The generated sheet supplied one reusable upper-arm part. The far arm uses
  that shared part in the feasibility rig.
- The sheet's three tail candidates were three complete tails at different
  sizes, not true contiguous tail segments. The clean rig therefore renders
  one intact tail from the tail-root bone; the remaining tail bones stay
  visible in debug mode as the intended future deformation chain.
- Interior joint rings make the mechanics easy to inspect but are too visible
  for production close-ups. Production art should use overlap pads without
  exterior seam outlines.
- This source supports rightward walking and horizontal mirroring. Front,
  back, seated and diagonal views still require their own authored kits.
