# Bentosaur Runtime Captures

- `first-playable-v1/` contains the current Home, Service, and Summary evidence
  from the flat-cel gameplay slice.
- `home-village-rain-v002-soft-blend/` is the founder-approved Home Village
  atmosphere checkpoint: rain from frame one, registered light wake-up, and a
  restrained normal-alpha weather composite.
- `home-village-rain-v001/` preserves the brighter pre-restraint rain pass.
- `home-menu-preset3-stall-v002/` proves the production preset-3 post-process,
  corrected stall proportions, and physical-iPhone deployment checkpoint.

## Preserved facial lab

These are fixed-camera Godot Mobile-renderer captures, grouped by imported
character revision.

- `v001/` preserves the first captured workaround state. The earlier raw
  tongue-near-nose failure was diagnosed before this capture set and is
  documented in the r002 experiment history, but is not claimed by these
  frames.
- `v002/` preserves the second result after applying the tongue object's
  transforms before skinning/export.

The `v002` structural contract passes, but its visual gate does not. The
tongue remains mostly below or behind the mouth because the experiment uses a
layered aperture over an uncut muzzle rather than a real cavity.

`v002/mouth_mode_comparison.png` is ordered:

```text
morph-only | bone-only | hybrid
```

The orange status line inside each frame records the active mode.
