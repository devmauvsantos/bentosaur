# Home Menu V011 Runtime Evidence

Date: 2026-07-31

## Captures

- `home-menu-v011-normal-540x960.png`
- `home-menu-v011-reduced-motion-540x960.png`
- `home-menu-v011-normal-vs-reduced-1080x960.png`

Both modes were recorded through Godot Movie Maker with the Forward Mobile /
Metal renderer at 30 FPS for 60 deterministic frames. The transient frame
sequences and WAV files were removed after the final snapshots were preserved.

## Validation

- all 21 `game/tests/*_test.gd` contracts pass;
- normal and reduced-motion captures retain identical crate, star, lid, and
  responsive-stage registration;
- the personal-team iOS export passed strict `codesign` verification, installed,
  and launched on the connected iPhone 17 Pro Max.

## Reproduction

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --write-movie /absolute/output/frame.png \
  --fixed-fps 30 \
  --quit-after 60 \
  --disable-vsync \
  -- --deterministic-capture --audio-off
```

Add `--reduced-motion` after `--deterministic-capture` for the reduced capture.
