# Hanging Lantern Layers V001 Prompt

**Tool:** OpenAI built-in image generation

**Operation:** reference-guided asset generation

**References:**

- `art/concepts/2d-chibi/v4/01_menu-refinement/`
  `bentosaur-home-menu-refined-classic-guestbook-v2.png`
- a temporary enlarged crop of the approved left hanging lantern

## Prompt

Create a production visual-gate asset sheet for the hanging stall lantern from
the supplied Bentosaur home-menu artwork.

Preserve the recognizable design and visual language of the reference:
rounded amber Japanese-inspired globe, dark warm-bronze top and bottom
fittings, simple front cage ribs, tiny lower stem and bead, premium flat-cel
2D chibi storybook rendering, refined dark outlines, softly painted cel
shading, restrained paper-like texture, cool indigo shadows, and warm amber
light. Do not redesign it into a generic paper lantern. Do not add ornaments,
leaves, writing, dinosaurs, stall pieces, rain, steam, props, or scenery.

This is a modular Godot asset proof, not a concept scene. It must support a
fixed beam anchor, a hanging body that sways from a clear top-center pivot, and
explicit OFF and ON states.

Use a perfectly flat `#FF00FF` chroma-magenta background edge to edge, with no
grid, labels, borders, shadows, ground plane, vignette, or decorative frame.
Arrange five well-separated items:

1. fixed beam anchor and short hook only;
2. complete detached lantern body/shell in the OFF state;
3. opaque inner amber light-core shape only;
4. assembled OFF preview;
5. assembled ON preview.

The OFF and ON previews must have identical anchor, cage, fittings, outline,
size, pose, and silhouette. The only ON change is illumination inside the
glass. Keep bloom restrained and close to the globe. Use strict front-on 2D,
zero perspective change, zero rotation, clean edges, and no baked cast shadow,
floor reflection, environmental spill, or text. The design must stay readable
at roughly `70–90` logical pixels wide on a `720 × 1280` mobile canvas.

## Deterministic correction

The generated preview assemblies are look targets only. Production does not
switch between them. The builder extracts one OFF shell, one fixed anchor, and
one inner core, then constructs OFF and ON from those exact same source pixels.
This removes the possibility of an AI-created geometry pop at power change.

