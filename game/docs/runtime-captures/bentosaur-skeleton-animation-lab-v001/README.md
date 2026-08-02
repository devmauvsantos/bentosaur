# Bentosaur Skeleton Animation Lab V001 Evidence

Date: 2026-08-02

Status: native Godot rig implemented and verified; founder visual approval and
physical-iPhone review pending

## Evidence

- `bentosaur-skeleton-lab-art-v001.mp4` — clean puppet view, 540 × 960,
  30 FPS, 18 seconds.
- `bentosaur-skeleton-lab-bones-v001.mp4` — the identical deterministic
  sequence with the runtime pivot overlay visible.
- `bentosaur-skeleton-lab-art-contact-sheet-v001.png` — six evenly sampled
  frames from the clean sequence.
- `bentosaur-skeleton-lab-bones-contact-sheet-v001.png` — the same six samples
  with bones visible.

The retained MP4s are H.264/YUV420p for easy review. Raw Movie Maker AVI
intermediates were temporary capture files and are intentionally excluded.

## Reproduction

Clean art view:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --display-driver macos \
  --rendering-method mobile \
  --write-movie /absolute/output/bentosaur-skeleton-lab-art.avi \
  --fixed-fps 30 \
  --quit-after 540 \
  --disable-vsync \
  --audio-driver Dummy \
  res://scenes/labs/bentosaur_skeleton_animation_lab.tscn \
  -- --deterministic-capture
```

Add `--show-bones` after `--deterministic-capture` for the explanatory rig
view. Add `--reduced-motion` for the still endpoint.

## Result

- Headless rig contract: pass.
- Full current Godot test suite: 24/24 pass.
- Verified lab run: no engine warnings or errors.
- Rest reconstruction differs from the registered source only within the
  provisional hidden-neck overlap.

V001 validates cutout motion, registration, and blink swapping. It does not
claim that the baked neutral mouth can become a production chew or open smile.
Those states require one authored mouthless head plate plus registered mouth
attachments.
