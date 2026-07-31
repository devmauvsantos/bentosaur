# Home Menu Stall v001

**Status:** Gate 1 approved — 2026-07-31

This package reconstructs the empty, completely unlit home-menu stall from:

`art/concepts/2d-chibi/v4/01_menu-refinement/`
`bentosaur-home-menu-refined-classic-guestbook-v2.png`

The approved Home Village background was not regenerated or painted into the
stall asset.

## Generation

- Workflow: built-in image generation followed by local chroma-key removal
- Use case: precise object edit
- Chroma key: flat magenta, sampled as `#f703e7`
- Generated canvas: `941 × 1672`
- Registered source canvas: `1440 × 2560`
- Runtime canvas: `720 × 1280`

The production prompt required:

- exact Bentosaur stall design, front-facing perspective, and materials;
- preserved `BENTOSAUR` sign and dinosaur emblem;
- empty transparent service opening;
- clean buttonless wooden façade;
- no dinosaur, rank plaque, stars, lanterns, props, smoke, HUD, pedestrians,
  rain, illumination, or reflections;
- flat magenta everywhere outside and through the opening.

## Files

- `generated/stall_structure_unlit_chroma_v001.png`: immutable generated source
- `generated/stall_structure_unlit_cutout_v001.png`: alpha-extracted source
- `generated/stall_structure_unlit_registered_1440x2560_v001.png`: registered
  source master
- `reviews/stall_structure_unlit_composite_720x1280_v001.png`: review composite

Runtime files live under:

`game/assets/environments/home_village/v001/stall/`

The counter occluder is derived from the same registered pixels. It will render
above the future proprietor body so the dinosaur can stand behind the stall
without repainting or destructive masking.
