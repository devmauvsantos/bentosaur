# Home Menu V013 Runtime Evidence

Date: 2026-07-31

Status: runtime implementation captured; founder character approval and
physical-iPhone filter longevity gate pending.

## Captures

- `home-menu-v013-neutral-540x960.png`
- `home-menu-v013-blink-540x960.png`
- `home-menu-v013-neutral-vs-blink-1080x960.png`
- `home-menu-v013-idle-motion.mp4`
- `home-menu-v013-counter-contact-detail.png`
- `home-menu-v013-filter-t358s-540x960.png`
- `home-menu-v013-filter-t358s-stall-detail.png`

The character frames came from a six-second deterministic Forward Mobile /
Metal capture at 30 FPS. The longevity frame came from a separate 360-frame
Forward Mobile / Metal capture at one fixed frame per second, representing six
simulated minutes of shader lifetime.

## Reproduction

Character motion gate:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --display-driver macos \
  --rendering-method mobile \
  --write-movie /absolute/output/frame.png \
  --fixed-fps 30 \
  --quit-after 180 \
  --disable-vsync \
  --audio-driver Dummy \
  -- --deterministic-capture --audio-off
```

Six-minute accelerated filter gate:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --display-driver macos \
  --rendering-method mobile \
  --write-movie /absolute/output/filter-360s.avi \
  --fixed-fps 1 \
  --quit-after 360 \
  --audio-driver Dummy \
  -- --deterministic-capture --audio-off
```

Physical iPhone longevity approval is intentionally not inferred from either
desktop-Metal capture.
