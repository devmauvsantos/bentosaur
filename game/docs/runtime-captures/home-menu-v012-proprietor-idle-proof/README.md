# Home Menu V012 Proprietor Idle Evidence

Date: 2026-07-31

Status: first-playable whole-sprite proof; founder approval and production
layer reconstruction pending

## Captures

- `home-menu-v012-neutral-540x960.png`
- `home-menu-v012-blink-540x960.png`
- `home-menu-v012-neutral-vs-blink-1080x960.png`
- `home-menu-v012-reduced-motion-540x960.png`
- `home-menu-v012-idle-motion.mp4`

The six-second motion proof was recorded through Godot Movie Maker with the
Forward Mobile / Metal renderer at 30 FPS. It contains the live randomized
breath phase, bottom-anchored 3.4-second breath, procedural rain and stall
motion, and the deterministic blink at approximately 3.4 seconds. Audio was
disabled only for capture.

The reduced-motion run removes spatial breathing while preserving the discrete
blink expression.

## Validation

- complete Godot suite: **22 passed, 0 failed**;
- the character controller produces identical deterministic state at 30, 60,
  and 120 FPS;
- vertical breath stays at or below `0.5%` and horizontal compensation at or
  below `0.25%`;
- both expression textures share one `374 × 490` crop and bottom-center origin;
- character body renders at `z14`, behind the complete stall at `z15`, while
  attachments remain above at `z16+` and weather at `z20`.

## Reproduction

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --write-movie /absolute/output/frame.png \
  --fixed-fps 30 \
  --quit-after 180 \
  --disable-vsync \
  -- --deterministic-capture --audio-off
```

Add `--reduced-motion` after `--deterministic-capture` for the reduced run.

## Approval boundary

The source identity and registered neutral/blink pair are approved visual
exploration assets, but this runtime proof swaps complete character images.
It is not the shipping layer kit. After the in-stall scale and personality are
approved, the production pass must reconstruct one shared body plus separate
eyes, mouth, foreground arms/hands, and optional expression accents.
