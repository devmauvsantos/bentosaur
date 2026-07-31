# Counter Decor V001 — Generation and Extraction Notes

**Status:** source-art candidates only; no runtime promotion

**Generated:** 2026-07-31

## Generation contract

Exactly three OpenAI built-in image-generation calls were made. Every call
used the approved home-menu image only as a style, material, scale, and
slightly top-down front-perspective reference:

`art/concepts/2d-chibi/v4/01_menu-refinement/`
`bentosaur-home-menu-refined-classic-guestbook-v2.png`

The prompts are preserved verbatim under `prompts/`:

1. `counter-plant-modular-kit-v001.md`
2. `bottle-crate-modular-kit-v001.md`
3. `red-counter-cloth-v001.md`

No follow-up or corrective generation call was made.

## Immutable generated plates

| Plate | Size | SHA-256 |
|---|---:|---|
| `generated/counter-plant-modular-sheet-chroma-candidate-v001.png` | 1536×1024 | `e411acebe4474e1f302cda41b82336f4db57e090c8590eb62cdda22413cfa627` |
| `generated/bottle-crate-modular-sheet-chroma-candidate-v001.png` | 1672×941 | `70e1d40040412253a43d7979cb2041bcd8e49b3712adb38050d47d19123f26df` |
| `generated/red-counter-cloth-chroma-candidate-v001.png` | 1164×1351 | `4098cbb2e01f4ed56a9970f57737b69c9e8ce0b8bf670f226c1261172939dde9` |

The immutable plates remain untouched after copying from the built-in tool's
generated-image store.

## Chroma extraction

The installed ImageGen helper was used with its standard soft-matte and
despill path:

```text
python3 /Users/mauvsantos/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py
  --input <chroma source>
  --out <cutout output>
  --auto-key border
  --soft-matte
  --transparent-threshold 12
  --opaque-threshold 220
  --despill
```

| Cutout sheet | Sampled key | Transparent px | Partial-alpha px | SHA-256 |
|---|---:|---:|---:|---|
| `generated/counter-plant-modular-sheet-cutout-candidate-v001.png` | `#fb05fa` | 1,210,279 | 7,075 | `f623863840a065bf9d53207525634471f413993273cbcea0404fae60314fbc88` |
| `generated/bottle-crate-modular-sheet-cutout-candidate-v001.png` | `#fb03fa` | 1,209,558 | 6,353 | `213c062df675cced8ef1a2af382ffc3e615fc92ac128afffa246f89ee2454fe7` |
| `generated/red-counter-cloth-cutout-candidate-v001.png` | `#fa03fa` | 997,019 | 3,935 | `ce61e44309b73f452abc0816f9dfa87bee7df0f8fafed0ccda89341f44a52119` |

All twelve sheet corners are alpha `0`. A post-extraction scan found zero
surviving magenta-like or hot-magenta pixels with alpha greater than zero, so
no edge contraction or second matte pass was applied.

## Deterministic component crops

Every crop preserves the extracted pixels exactly and adds approximately
eight transparent pixels around its detected subject bounds.

| Component | Crop from sheet | Canvas | Used alpha bounds |
|---|---:|---:|---:|
| `components/counter_plant_pot_candidate_v001.png` | `497×487+213+371` | 497×487 | `482×472+7+8` |
| `components/counter_plant_foliage_candidate_v001.png` | `527×723+806+115` | 527×723 | `511×707+8+8` |
| `components/bottle_crate_empty_candidate_v001.png` | `501×379+23+296` | 501×379 | `485×363+8+8` |
| `components/bottle_brown_candidate_v001.png` | `164×303+561+302` | 164×303 | `149×287+7+8` |
| `components/bottle_green_candidate_v001.png` | `175×332+767+275` | 175×332 | `159×316+8+8` |
| `components/bottle_cream_blue_cap_candidate_v001.png` | `184×306+963+302` | 184×306 | `169×290+7+8` |
| `components/bottle_crate_assembled_preview_candidate_v001.png` | `482×412+1180+271` | 482×412 | `466×397+8+7` |
| `components/counter_cloth_red_draped_candidate_v001.png` | `912×984+128+173` | 912×984 | `897×968+7+8` |

The assembled crate is review evidence only. Runtime promotion, if approved,
must use the empty crate and three independent bottle pieces.

## Visual QA

- Plant plate contains exactly one pot and one independent foliage cluster.
- Bottle plate contains exactly one empty crate, three independent bottle
  identities, and one assembled preview.
- Cloth plate contains exactly one cloth and no counter or support pixels.
- No character, dinosaur, scenery, rain, smoke, steam, UI lettering, or
  watermark appears in any plate.
- The extracted silhouettes remain readable on the dark neutral review matte.
- No generated candidate has been resized, registered onto the stall, or
  promoted under `game/assets`.

Review board:

`reviews/counter-decor-category-review-board-v001.png`

SHA-256:
`7b1452ccb28678eb83b3d2c7f9ccd507f6e3f1b29e05f8b436e420617fbbfbfc`
