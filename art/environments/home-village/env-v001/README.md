# Bentosaur Home Village — ENV-V001

Canonical source-art package for the empty home-village environment.

## Approved gate

- `source/bentosaur-home-village-background-unlit-approved-v001.png`
  - Status: approved
  - Approval date: 2026-07-30
  - Purpose: immutable lights-off master used to derive every registered lighting composite and runtime overlay
  - Contains: empty village square, dark fixtures and windows, wet pavement with cool ambient sheen
  - Excludes: stall, dinosaurs, UI, rain, steam, warm light, and warm reflections

## Pipeline

1. Approve the immutable unlit source.
2. Create a registered lights-on composite without changing geometry.
3. Approve the lights-on composite.
4. Extract registered transparent light and reflection layers.
5. Import optimized derivatives into Godot.

Runtime-ready derivatives belong under `game/assets/`; this directory keeps lossless art sources, review composites, layer masters, and generation provenance.

