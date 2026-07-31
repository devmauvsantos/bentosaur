# LIGHT-V001 — Registered Home-Village Lighting

This lighting set reconstructs the approved lights-on art direction over the immutable unlit master. It does not use the generator-repainted environment as a game background.

## Layer order

All RGBA layers are `941 × 1672`, pixel-registered, and authored for additive blending.

1. `bentosaur-home-village-lighting-v001-indirect-warm-spill.png`
2. `bentosaur-home-village-lighting-v001-light-halos.png`
3. `bentosaur-home-village-lighting-v001-light-cores.png`
4. `bentosaur-home-village-lighting-v001-warm-reflections.png`

## Motion policy

- Light cores: subtle smooth flicker is allowed.
- Light halos: synchronized flicker at lower amplitude is allowed.
- Indirect warm spill: fade on once, then remain stable.
- Warm reflections: fade on once, then remain stable. A smaller shimmer layer may be isolated later.

Broad spill and reflection layers must not continuously flicker; doing so would make painted building and pavement texture appear to pulse.

## Review files

- `bentosaur-home-village-lighting-v001-registered-composite-preview.png` shows the exact unlit master plus all four additive layers.
- `bentosaur-home-village-lighting-v001-toggle-proof.gif` alternates the immutable unlit source and registered composite to expose any geometry movement.
- `bentosaur-home-village-lighting-v001-mask-diagnostic.png` visualizes the core, architectural, and pavement masks.
- `bentosaur-home-village-lighting-v001-extraction-report.json` records dimensions, layer order, curb boundary, coverage, and motion policy.
