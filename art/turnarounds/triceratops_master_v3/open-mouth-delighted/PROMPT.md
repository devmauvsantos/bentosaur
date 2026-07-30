# Bentosaur Open-Mouth Multiview Input

## Input roles

- `triceratops_master_v1/drafts/model-sheet-v1.png` — edit target; locks the
  full-body character, anatomy, proportions, palette, materials, poses, camera
  views, and panel layout.
- `triceratops_master_v1/drafts/mouth-expression-addendum-v1.png` — expression
  reference; locks the delighted open smile, recessed cavity, tongue, lifted
  corners, and closed happy eyes.

## Generation prompt

Use case: precise-object-edit

Asset type: production multiview input sheet for Tripo 3D reconstruction.

Edit the full-body four-view model sheet only so the same Bentosaur has the
delighted open smile from the expression reference wherever the mouth is
visible. Preserve the orthographic turnaround and all body geometry.

- Front: broad lifted-corner open smile, dark genuinely recessed mouth cavity,
  small coral tongue resting inside the lower mouth, and closed happy crescent
  eyes.
- Left profile: the same physically open recessed mouth and tongue, consistent
  from profile.
- Back: unchanged because the mouth is not visible.
- Right profile: the same physically open recessed mouth and tongue, consistent
  from profile.

The smile is a wide rounded-triangular/U-shaped delighted grin with lifted
corners. It is not a circular or oval O, black sticker, painted disc,
protruding ring, pacifier muzzle, or separate object. The lips blend naturally
into the cheeks.

Keep the same single unclothed upright baby Triceratops in every panel:
exactly two hind legs, two free forearms, three horns, cream belly/horns/frill
knobs/claws, sage body, coral cheeks, full body visible, empty hands, and a
plain neutral background. No props, clothes, accessories, scenery, text,
labels, ground plane, cast shadow, extra objects, extra limbs, duplicate
features, or expression drift.

## Output contract

- One square 2×2 sheet, 1254×1254 PNG.
- Panel order: front, left, back, right.
- Each quadrant is cropped exactly at 627×627 and resized to 1024×1024 for the
  Tripo multiview request.
- The original generated sheet and every submitted view are preserved.
