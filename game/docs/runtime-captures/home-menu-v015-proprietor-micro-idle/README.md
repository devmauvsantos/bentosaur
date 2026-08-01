# Home Menu V015 Proprietor Micro-Idle Evidence

Date: 2026-08-01

Status: runtime implementation and physical-device deployment complete;
founder phone-scale motion approval pending

## Evidence

- `home-menu-v015-idle-motion-full.mp4` — true-scale `540 × 960`, 12-second
  Forward Mobile / Metal capture at 30 FPS.
- `home-menu-v015-idle-motion-character-crop.mp4` — four-times enlarged
  supplementary character crop for inspecting the micro-lean and hand contact.
- `home-menu-v015-rest-vs-peak-1080x600.png` — rest at `t=8.000 s` on the left
  and deterministic peak at `t=9.533 s` on the right.

The full-frame movie is the visual authority. The enlarged crop exists only
because a deliberately sub-degree gesture is difficult to judge in a still at
phone scale.

## Motion contract

- Existing breath remains `3.4 s`, at no more than `0.5%` vertical expansion
  and `0.25%` horizontal compensation.
- `VisualRoot/BodyMotionRoot` owns body/head breathing and the rare lean.
- `VisualRoot/ForegroundHands` is its sibling and never inherits those
  transforms, so the fingers stay planted on the counter.
- A lean begins after `6.5–10.0 s` of rest, reaches a random signed
  `0.35–0.50°`, pauses briefly, and returns smoothly to zero.
- A separate seeded RNG prevents the new gesture from changing blink timing.
- Reduced Motion removes breathing and leaning while preserving blinks.

For deterministic seed `48043`, the first gesture starts at `8.733 s` and
peaks at `9.533 s` at `0.4463°`.

## Validation

- Complete Godot suite: **23 passed, 0 failed**.
- Motion state and pose agree at 30, 60, and 120 FPS.
- Foreground-hand global transform remains unchanged across a 30-second
  deterministic simulation.
- Existing breath bounds remain unchanged.
- Reduced Motion and inactive states restore the exact registered transform.
- Foreground relight paths were updated for the nested body sprites and pass.
- Godot iOS export and generated-project personal-signing guards pass.
- Xcode debug build, strict code-sign verification, install, and launch pass on
  Mauricio's iPhone 17 Pro Max under personal team `53RJ43876F`.

## Reproduction

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --display-driver macos \
  --rendering-method mobile \
  --write-movie /absolute/output/home-menu-v015-idle-motion.avi \
  --fixed-fps 30 \
  --quit-after 360 \
  --disable-vsync \
  --audio-driver Dummy \
  -- --deterministic-capture --audio-off
```

Add `--reduced-motion` to the user arguments for the non-spatial endpoint.
