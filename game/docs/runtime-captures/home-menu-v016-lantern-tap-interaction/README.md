# Home Menu V016 Interactive Lantern Evidence

Date: 2026-08-01

Status: runtime implementation and physical-device deployment complete;
founder phone-scale interaction approval pending

## Evidence

- `home-menu-v016-lantern-tap-full.mp4` — true-scale `540 × 960`, six-second
  Forward Mobile / Metal capture at 30 FPS.
- `home-menu-v016-lantern-tap-enlarged.mp4` — enlarged stall-top crop for
  judging the sub-degree bell movement and short light dips.
- `home-menu-v016-lantern-tap-proof-grid.png` — frames around the left and
  right deterministic tap events.

The full-frame movie is the composition authority. The crop is supplementary
because the authored swing is intentionally tiny at phone scale.

## Deterministic choreography

- left lantern at `0.75 s`;
- right lantern at `2.50 s`;
- left lantern again at `4.25 s`.

This sequence is enabled only by the `--lantern-tap-proof` capture argument.
Normal builds are touch-driven.

## Reproduction

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --display-driver macos \
  --rendering-method mobile \
  --write-movie /absolute/output/home-menu-v016-lantern-tap.avi \
  --fixed-fps 30 \
  --quit-after 180 \
  --disable-vsync \
  --audio-driver Dummy \
  -- --deterministic-capture --audio-off --lantern-tap-proof
```
