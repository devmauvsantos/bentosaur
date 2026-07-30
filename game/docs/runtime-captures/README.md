# Facial Lab Runtime Captures

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
