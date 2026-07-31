# UI Attachment Kit — Extraction Notes v001

Status: candidate art only. Nothing in this folder is promoted to Godot runtime assets.

## Scope and provenance

- Approved visual reference: `art/concepts/2d-chibi/v4/01_menu-refinement/bentosaur-home-menu-refined-classic-guestbook-v2.png`
- Exactly three built-in image-generation calls were used:
  1. rank plaque, empty/filled star, and shine
  2. primary/secondary button state system and detached leaves
  3. circular settings cog normal/pressed states
- The verbatim prompts are preserved in `prompts/`.
- The direct chroma outputs are preserved in `generated/` and were not overwritten.
- No lettering, character art, scenery, or rain was generated in this UI pass.

## Chroma-key extraction

The generated sheets use a flat `#FF00FF` field. The transparent derivatives in `transparent/` were produced with the ImageGen skill's border-key workflow using a 12-pixel hard-distance threshold, 220-pixel soft-distance threshold, soft alpha, and magenta despill.

Validation results:

- all four sheet corners are alpha `0`
- measured visible magenta fringe pixels: `0` on every transparent sheet and extracted component, using `alpha > 0`, `R > 170`, `B > 170`, `G < 90`
- transparent and partially transparent pixel counts are recorded in `extraction-report-v001.json`

## Rank plaque

Approval candidate: `components/rank/rank-plaque-empty-sockets-v001.png`

Extraction boxes from `transparent/rank-plaque-kit-cutout-v001.png`:

| Asset | Source rectangle | Output size |
| --- | --- | --- |
| plaque with three empty sockets | `x=67, y=129, w=1539, h=425` | `1539×425` |
| empty star | `x=358, y=615, w=259, h=249` | `259×249` |
| filled star | `x=741, y=615, w=259, h=249` | `259×249` |
| shine accent | `x=1146, y=684, w=130, h=147` | `130×147` |

The empty and filled star alpha silhouettes have IoU `0.992638`, so they are effectively the same placement geometry but not pixel-identical.

`rank-plaque-kit-chroma-v002.png`, its transparent derivative, and its mask are retained only as provenance for one deterministic local recolor experiment. That experiment is rejected: the mask contaminated wood/screw regions and created visible brown wedges around the star sockets. It is intentionally absent from the review board and must not be treated as an approval candidate. The desired muted moss-green plaque face remains pending a future controlled paint pass. Per the stop rule, no further generation or recolor iteration was made here.

## Button system

Each state is extracted on the same fixed `346×205` canvas. The primary row starts at `y=155`; the secondary row starts at `y=416`. State columns start at `x=30`, `407`, `784`, and `1160` for normal, selected, pressed, and disabled respectively.

State intent:

- normal: resting surface
- selected: brighter gold/green emphasis
- pressed: darker recessed surface
- disabled: desaturated, lower-contrast surface

Alpha-silhouette IoU against primary normal:

| State | IoU |
| --- | ---: |
| primary normal | 1.000000 |
| primary selected | 0.996813 |
| primary pressed | 0.995132 |
| primary disabled | 0.998169 |
| secondary normal | 0.998230 |
| secondary selected | 0.996475 |
| secondary pressed | 0.994973 |
| secondary disabled | 0.997933 |

This is strong candidate consistency. If approved, runtime preparation should canonicalize all state alpha masks to one shared outline before import so state changes cannot shimmer by a pixel.

Candidate NinePatchRect margins for a first integration test are `left=72`, `right=72`, `top=52`, `bottom=52`. These are review guidance, not a runtime manifest. Keep labels as live game text and layer the detached leaf assets separately.

## Settings control

- normal: `components/settings/settings-cog-normal-v001.png`
- pressed: `components/settings/settings-cog-pressed-v001.png`
- both use a fixed `563×583` canvas
- alpha-silhouette IoU: `0.998862`

The pressed treatment is deliberately restrained. It needs an on-device tap-legibility check before approval; runtime scale/offset feedback may still be preferable to additional painted states.

## Review board

`reviews/ui-attachment-kit-category-board-v001.png` is a textless board containing only the clean v001 candidates. It does not include the rejected rank v002 recolor.

## Promotion gate

Before any runtime integration:

1. founder approves or rejects each category from the board
2. the plaque-face color direction is resolved
3. button state readability is checked at target iPhone size
4. approved button masks are canonicalized and NinePatchRect margins are validated
5. only approved files are copied into game runtime assets
