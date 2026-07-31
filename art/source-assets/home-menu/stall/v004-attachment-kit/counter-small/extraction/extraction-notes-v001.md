# Counter-Small Extraction Notes V001

**Status:** candidate pending founder approval

**Generation mode:** built-in image generation, exactly two calls

**Reference:**
`art/concepts/2d-chibi/v4/01_menu-refinement/`
`bentosaur-home-menu-refined-classic-guestbook-v2.png`

## Immutable sources

- `generated/counter-oil-lantern-modular-sheet-chroma-candidate-v001.png`
  (`1672 × 941`, SHA-256
  `029ca37b9e701b97505f1319ee993cde8698986a87db13fcb63c6512b9d3b058`)
- `generated/grape-food-bowl-chroma-candidate-v001.png`
  (`1254 × 1254`, SHA-256
  `0d693b09fca54e54013bf99de9d2f72757c66e9fdef7b3421779d74eb2d56667`)

Both immutable files are read-only. The generator produced near-flat magenta
rather than byte-exact `#FF00FF`: median border keys were approximately
`(249, 3, 243)` and `(251, 3, 249)`. Border color-distance p95 remained at or
below `3`, so border auto-keying was stable. The immutable images were not
normalized or repainted.

## Chroma extraction

The installed ImageGen helper was run with:

```text
--auto-key border
--soft-matte
--transparent-threshold 12
--opaque-threshold 220
--despill
```

Detected keys:

- oil-lantern sheet: `#FA03F3`;
- grape bowl: `#FB03F9`.

The full-sheet transparent derivatives are preserved for traceability. Final
component crops use eight transparent pixels of padding around the detected
alpha bounds.

## Component extraction rectangles

Coordinates are `x, y, width, height` in each transparent full sheet.

| Component | Source rectangle | Output size |
|---|---:|---:|
| Oil-lantern body OFF | `150,184,257,539` | `257 × 539` |
| Oil-lantern core ADD | `605,407,94,201` | `94 × 201` |
| Oil-lantern halo ADD | `843,290,334,426` | `334 × 426` |
| Oil-lantern contact shadow | `1245,648,304,64` | `304 × 64` |
| Green grape bowl | `397,366,457,498` | `457 × 498` |

## Translucent halo handling

The generated halo was composited over the magenta backdrop, so ordinary
chroma removal left contaminated pink RGB in its translucent center. The raw
transparent extraction is preserved under `extraction/`.

For the component candidate, its generated alpha silhouette was blurred by
four pixels, capped at `0.36` opacity, and applied to a deterministic warm
amber radial color field (`#FFF1A0` center to `#FF8D2C` edge). This preserves
the generated size and falloff while eliminating chroma contamination. The
halo remains a candidate additive layer, not approved runtime art.

## Validation

- Every component is RGBA and has four fully transparent corners.
- Detected magenta-fringe pixels across the five component candidates: `0`.
- Oil-lantern body visible bounds: `241 × 523 + 8 + 8`.
- Core visible bounds: `78 × 185 + 8 + 8`.
- Halo alpha range: `0.0–0.3608`; every visible halo pixel is translucent.
- Contact-shadow visible bounds: `288 × 48 + 8 + 8`.
- Grape-bowl visible bounds: `441 × 482 + 8 + 8`.
- The OFF shell contains no separate flame or emitted halo. Its honey-amber
  glass remains somewhat luminous-looking and should be judged visually by the
  founder before promotion.
- No character, scenery, rain, text, steam, or wind anchor entered either
  candidate.

## Review authority

`reviews/counter-small-category-review-board-v001.png` compares the canonical
OFF shell, a non-destructive ON composite, and the isolated grape bowl. Nothing
in this category is authorized for `game/assets` until founder approval.
