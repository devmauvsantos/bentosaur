# Bentosaur Flat-Cel 2D — Menu Refinement v4

Status: founder review candidate; not approved for production

Effective: 2026-07-30

## Purpose

Refine only the classic stall-menu assembly while preserving the selected
rainy village, stall, proprietor, lighting, HUD, and flat-cel visual language.

Requested changes:

- smaller, calmer menu plaques;
- smaller title-case lettering;
- more internal padding between text and borders;
- more visible street around the menu;
- `Open Stall`, `Guestbook`, `Decorations`, and `Pantry`;
- one detached settings cog;
- a real embeddable runtime-font direction.

## Review files

| File | Purpose |
|---|---|
| `01_menu-refinement/bentosaur-home-menu-refined-classic-guestbook-v1.png` | First refined edit; slightly larger visual controls |
| `01_menu-refinement/bentosaur-home-menu-refined-classic-guestbook-v2.png` | More compact corrective pass; current recommendation |
| `02_typography/bentosaur-menu-font-comparison-v1.png` | Four real TTF specimens |
| `02_typography/bentosaur-menu-font-finalists-v1.png` | Lilita One versus Paytone One |
| `03_boards/bentosaur-classic-menu-before-after-v1.png` | Original versus v1 |
| `03_boards/bentosaur-classic-menu-before-after-v2.png` | Original versus v2 |

Both menu images are 941×1672. They are concept mockups, not flattened
production screens. Image generation preserved the scene semantically and
compositionally, but regenerated pixels outside the menu footprint. Runtime
work must use separately authored background, plaque, cog, and live-text
layers.

## Typography recommendation

Primary candidate: **Lilita One Regular**

- closest to the existing warm, softly carved shop-sign character;
- slightly condensed, so `Decorations` retains generous side insets;
- very legible with a restrained outline at phone size;
- approximately 27 KB for the official regular TTF;
- Latin and Latin Extended coverage;
- distributed through Google Fonts under the SIL Open Font License.

Alternate: **Paytone One Regular**

- cleaner and slightly less quirky;
- includes Vietnamese coverage;
- approximately 112 KB;
- wider than Lilita One but still practical for these labels;
- also distributed under the SIL Open Font License.

Official sources:

- <https://fonts.google.com/specimen/Lilita+One>
- <https://github.com/google/fonts/tree/main/ofl/lilitaone>
- <https://fonts.google.com/specimen/Paytone+One>
- <https://github.com/google/fonts/tree/main/ofl/paytoneone>
- <https://openfontlicense.org/ofl-faq/>

No font has been added to the game yet. After Mau selects the face, vendor the
unchanged official TTF plus its copyright, license notice, and OFL text.

## Runtime contract after approval

Plaques ship without baked labels. Godot owns the live strings:

```text
menu.open_stall   = Open Stall
menu.guestbook    = Guestbook
menu.decorations  = Decorations
menu.pantry       = Pantry
menu.settings     = Settings
```

`Guestbook` can therefore become `Collection` without replacing artwork.

At a 390-point portrait reference:

- visible primary plaque: approximately 48–52 points high;
- visible secondary plaque: approximately 40–46 points high;
- interaction rectangle: minimum 48 points, preferably 52–56;
- settings cog may look smaller but still receives a 48-point-or-larger
  interaction rectangle;
- use title case, not all caps;
- never horizontally compress glyphs to fit localization;
- reduce size only to a documented floor, then allow a wider plaque or a
  deliberate two-line label.

The generated lettering is a visual target only. The final Godot proof must
render the actual selected TTF over text-free plaque art before typography is
approved.
