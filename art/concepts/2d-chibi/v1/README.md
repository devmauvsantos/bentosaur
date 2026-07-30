# Bentosaur 2D Chibi Exploration v1

**Status:** Research  
**Founder signal:** the flat-cel gameplay candidate feels more production-feasible  
**Production approval:** None  
**Engine decision changed:** No

This folder collects the existing Bentosaur game-screen concepts and a bounded
2D translation study.

## Start here

| Purpose | File |
| --- | --- |
| Feasibility comparison | `02_boards/bentosaur-gameplay-3d-vs-2d-comparison-v1.png` |
| Selected proof candidate | `01_generated-exploration/bentosaur-gameplay-2d-flat-cel-v2.png` |
| Painted gameplay mood study | `01_generated-exploration/bentosaur-gameplay-2d-painted-chibi-v1.png` |
| Painted home/hub mood study | `01_generated-exploration/bentosaur-stall-hub-2d-painted-chibi-v1.png` |
| Painted album mood study | `01_generated-exploration/bentosaur-album-page-turn-2d-painted-chibi-v1.png` |

## Current reading

The painted screens preserve the 3D diorama's warmth, but their dense shading
would make every new character, pose, prop, and season expensive to author and
hard to keep consistent.

The flat-cel gameplay image is the production-feasibility candidate because it
has:

- stable dark outlines;
- broad color regions;
- limited shadow and highlight shapes;
- clean silhouettes;
- obvious separable planes;
- a character that can be rebuilt as front and side cutout rigs.

It is still concept art. It is not a sprite sheet, layered character, vector
master, animation rig, or runnable game screen.

Do not generate matching flat-cel home and album screens until the character
proof in `docs/visual-explorations/2d-flat-cel-production-feasibility-v1.md`
passes.

## Folder map

```text
00_reference-screens/
  Existing pixel, 3D diorama, gameplay, home, and album concepts.

01_generated-exploration/
  New 2D mood studies and the flat-cel feasibility candidate.

02_boards/
  Human-readable comparison evidence.
```

Exact reference provenance, output hashes, and approval state are recorded in
`manifest.json`.

