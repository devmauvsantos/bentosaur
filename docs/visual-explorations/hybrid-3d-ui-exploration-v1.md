# Hybrid 3D UI Exploration 01

**Status:** Visual architecture exploration  
**Date:** July 29, 2026  
**Generation mode:** Built-in ImageGen  
**Production approval:** None  
**Character approval:** None  
**Tripo credits used:** 0

## Outputs

### Gameplay service screen

`art/concepts/ui-3d-hybrid/bentosaur-gameplay-hybrid-ui-v1.png`

SHA-256:

`b7ad3b0df5b8a6a68009029d11f726e4b7b3eeb80ee306efe4d7ab040e49d731`

Validates:

- full-3D world and food;
- screen-space coin/star/mood UI;
- screen-space order bubble anchored near the customer;
- readable bento and four-bin touch hierarchy;
- living street without losing loop clarity.

### Album page turn

`art/concepts/ui-3d-hybrid/bentosaur-album-page-turn-ui-v1.png`

SHA-256:

`eb7f5df911461e761c30fbafa5ce0120f4071f7fdc3f7d5ace9309f621539c11`

Validates:

- 3D book and page geometry;
- 2D page content;
- a visible curl, underside, next-spread reveal and moving shadow;
- portraits, memories and friendship progress in the same visual world.

### Between-days stall hub

`art/concepts/ui-3d-hybrid/bentosaur-stall-hub-ui-v1.png`

SHA-256:

`42209b0c119b37a6868f4917b4cd82da58e23ea988d248b4d87d47bb638f5184`

Validates:

- the stall itself as the progression/home object;
- full-3D neighborhood and upgradable stall;
- four large screen-space 2.5D destinations;
- calm metagame presentation without generic dashboard cards.

## Production reading

The set establishes that the latest 3D diorama style can extend beyond one hero
frame. The serving loop, album and between-days hub remain visually coherent.

The images are direction, not generated production assets:

- typography and numbers will be real Godot controls;
- HUD frames/icons will be systematically rendered or authored;
- touch targets and safe areas will be rebuilt from a design system;
- the final customer will use the user-approved Tripo/Blender master;
- page curl must be prototyped and measured in engine;
- background cast and stall props require individual production assets.

## Reference set

1. `bentosaur-gameplay-3d-diorama-engine-target-v2.png`
   — primary material, lighting, rainy-street and diorama reference.
2. `bentosaur-gameplay-3d-diorama-exploration-v1.png`
   — service-loop hierarchy and tactile HUD reference.
3. `triceratops_master_v1/drafts/model-sheet-v1.png`
   — anatomy and color-identity reference.

## Exact prompt 1 — Gameplay

```text
Use case: ui-mockup
Asset type: shippable-fidelity vertical mobile game gameplay screen
Input images: Image 1 is the primary 3D material, lighting, rainy-street and
diorama style reference. Image 2 is the gameplay-loop and HUD hierarchy
reference. Image 3 is the anatomy and color identity reference for the
original upright biped baby Triceratops only.

Primary request: Create a refined Bentosaur service-loop screen that shows how
a real hybrid 3D plus screen-space UI implementation should look. The world,
wooden stall, street, customer, bento, ingredient bins, lanterns, rain, steam
and background pedestrians are full 3D. The HUD is practical flat screen-space
UI whose icons are pre-rendered to resemble small tactile enamel, lacquered
wood and soft clay pieces; it must stay front-facing, crisp and easy to tap
rather than floating in world perspective.

Scene: intimate rainy nighttime dinosaur neighborhood seen through a cozy
bento stall. One delighted sage-green upright biped baby Triceratops customer
is front-facing at the counter. It has cream belly, horns, frill knobs and
claws, coral cheeks and short rounded paws. Several independent dinosaur
pedestrians are visible deeper in the street. Warm amber interior light
contrasts cool indigo rain and wet paving.

Required gameplay hierarchy: safe-area coin counter at top left; three-star
progress track centered at top; compact customer mood portrait at top right;
one clear order bubble near the customer containing exactly three large
ingredient pictograms and no words; large three-compartment red bento in the
lower middle; exactly four large ingredient bins across the bottom; selected
ingredient has a restrained glow; generous unobstructed drag paths and large
touch targets. Include a small physical bell on the counter but do not fuse it
to a character.

Style: original premium handcrafted chibi diorama, rounded toy-like geometry,
matte clay characters, lacquered wood, soft baked-looking ambient occlusion,
restrained highlights, readable silhouettes, plausible real-time mobile
rendering. UI components share the same warm material language but remain
clean 2D/2.5D overlays.

Composition: full 9:16 vertical playable screen, mostly frontal fixed camera
with a gentle top-down angle for the food. Preserve the emotional customer
close-up while keeping order and ingredients immediately legible.

Constraints: original Bentosaur IP only; no copied franchise characters,
logos, icons, UI or world. No clothing or fused umbrella, tray, bento, food or
prop on any dinosaur. No photorealism, pixel-art filter, excessive depth of
field, tiny text, gibberish text, cropped HUD, extra menus or decorative
clutter. No words; numerals may show only "00".
```

## Exact prompt 2 — Album

```text
Use case: ui-mockup
Asset type: shippable-fidelity vertical mobile game album and page-turn screen
Input images: Image 1 is the primary 3D material, lighting, rainy-street and
diorama style reference. Image 2 establishes Bentosaur's tactile UI material
family. Image 3 is the anatomy and color identity reference for the original
upright biped baby Triceratops.

Primary request: Design the Bentosaur regulars album as a physical,
emotionally irresistible book interaction within the same full-3D chibi
diorama game. Show the book open in close-up on the warm wooden stall counter
while one thick cream paper page is midway through a finger-driven turn. The
curled page must visibly reveal the next spread underneath, with believable
paper thickness, curved silhouette, soft fold shadow and a satisfying
almost-settled motion. Do not show a human hand; the page itself communicates
touch response.

World and UI architecture: the book cover, spine, pages, page curl and counter
are 3D. The portraits, stamps, heart pips, page decorations and readable page
content are clean 2D artwork placed on the paper surfaces. A minimal
screen-space back button and tiny coin indicator use the same enamel/wood
2.5D icon language and remain front-facing.

Current spread: an original sage-green upright biped baby Triceratops portrait
with cream belly and horns, coral cheeks and joyful expression; two filled
heart pips and one empty heart pip; two small framed memory snapshots—one
under a tiny umbrella icon and one delighted at the stall—but all objects in
the illustrations remain separate rather than fused to the character.
Botanical and fossil-like margin motifs are subtle and original. Next spread
peeking through shows a different colored biped dinosaur silhouette and empty
discovery slots. Use only the large page counter text "3 / 12"; no other words.

Scene: warm amber lantern light across parchment and lacquered wood, with the
rainy indigo street softly visible beyond the counter. Fine paper grain,
rounded corners, stitched binding, tiny embossed dinosaur-foot motifs and
restrained magical dust at the settling edge.

Composition: 9:16 vertical mobile screen, intimate top-down three-quarter book
close-up, clear page curl and touch area, no obstruction of the important
portrait or hearts.

Constraints: original Bentosaur IP only. No copied franchise page layout,
characters, logos, icons or typography. No human hands, photorealism, pixel-art
filtering, thin unreadable text, gibberish text, excessive glitter, cloth
simulation look, loose paper flying away, or static flat-panel appearance. The
book must feel like a real interactable object in the same game world.
```

## Exact prompt 3 — Stall hub

```text
Use case: ui-mockup
Asset type: shippable-fidelity vertical mobile game between-days stall hub and
menu
Input images: Image 1 is the primary 3D diorama, material, lighting and
neighborhood reference. Image 2 establishes the tactile Bentosaur HUD family.
Image 3 establishes the canonical upright biped baby Triceratops anatomy and
palette only.

Primary request: Create the Bentosaur between-days hub that appears after
closing the service session. It must feel like returning to a beloved physical
place, not opening a generic mobile dashboard. Show a miniature full-3D view
of the same cozy bento stall at blue-hour after rain, shutters partly closed,
lanterns glowing, steam fading and a few separate biped dinosaur neighbors
walking past. The central stall is interactive and visually upgradable, with
visible but uncluttered slots for lanterns, awning, plants and counter
decorations.

Hybrid menu architecture: world, stall, props, weather and pedestrians are
full 3D. Screen-space controls are four large practical 2.5D icon buttons
arranged around the lower third, each rendered like tactile enamel or carved
wood but facing the screen: an open-sign icon for starting the next day, a
physical book icon for regulars, a pantry basket icon for recipes/stock, and a
lantern-with-leaf icon for stall decoration and seasons. A coin counter sits
in the safe-area top left. A compact three-star daily summary sits centered at
top. A small season/weather medallion sits top right. No modal panel blocks the
diorama.

Visual story: the stall itself is the home/progression object. Upgrades are
communicated by warm additional lanterns, a better awning, potted greenery,
tiny keepsakes and a more cared-for counter—not a disconnected house or
city-builder. Include one small closed red bento and one bell as separate
counter props.

Style: original premium handcrafted chibi diorama, rounded toy geometry, matte
clay, lacquered warm wood, soft ambient occlusion, gentle rain reflections,
cozy amber against indigo, plausible real-time mobile rendering. UI looks
materially related to the world while remaining crisp, accessible and easy to
tap.

Composition: 9:16 vertical mobile screen, fixed slightly elevated diorama
camera, generous safe areas, 48-point-equivalent touch targets, strong central
stall focus and uncluttered hierarchy.

Constraints: original Bentosaur IP only; no copied franchise characters,
logos, UI, buildings, icons or world. No fused props or clothing on dinosaurs.
No photorealism, pixel-art filter, generic rectangular dashboard cards, tiny
text, gibberish text, loot boxes, sale banners, multiple currencies, red
notification badges, or cluttered live-service UI. Use no words and no
numerals except "00".
```

