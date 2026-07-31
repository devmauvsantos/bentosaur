# Bentosaur Home Village — ENV-V001

Canonical source-art package for the empty home-village environment.

## Approved assets

- `source/bentosaur-home-village-background-unlit-approved-v001.png`
  - Status: approved
  - Approval date: 2026-07-30
  - Purpose: immutable lights-off master used to derive every registered lighting composite and runtime overlay
  - Contains: empty village square, dark fixtures and windows, wet pavement with cool ambient sheen
  - Excludes: stall, dinosaurs, UI, rain, steam, warm light, and warm reflections
- `lighting/lighting-v001/`
  - Status: approved registered lighting set
  - Blend mode: additive
  - Contains: light cores, soft halos, indirect warm spill, warm pavement reflections, and a reconstructed composite
  - Registration: every layer is exactly `941 × 1672` and aligns with the approved unlit master

## Pipeline

1. Approve the immutable unlit source. ✅
2. Establish the lights-on art-direction target. ✅
3. Transfer only registered additive light onto the immutable source. ✅
4. Separate motion-safe cores and halos from static indirect spill and reflections. ✅
5. Import optimized derivatives into Godot.

Runtime-ready derivatives belong under `game/assets/`; this directory keeps lossless art sources, review composites, layer masters, and generation provenance.
