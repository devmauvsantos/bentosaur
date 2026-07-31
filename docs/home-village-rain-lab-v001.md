# Home Village Rain Lab V001

Status: founder-approved visual checkpoint; production integration pending.

This lab places only the approved empty Home Village, its registered additive
lighting, and a first production-shaped rain treatment in Godot. It does not
contain the stall, dinosaurs, menu, or gameplay.

## Reference technique

The implementation follows the structure demonstrated in Mclelun's
[Godot rain particle Short](https://www.youtube.com/shorts/x-qWmhZhkwI):

1. Layer different rain densities instead of drawing one uniform field.
2. Use a short, authored splash flipbook rather than a generic burst.
3. Set the hidden impact drops to `COLLISION_HIDE_ON_CONTACT`.
4. Trigger the splash particle system with `SUB_EMITTER_AT_COLLISION`.
5. Use a static `LightOccluder2D` as the 2D particle collision surface.

Godot's
[ParticleProcessMaterial reference](https://docs.godotengine.org/en/latest/classes/class_particleprocessmaterial.html)
documents the hide-on-contact and at-collision pairing specifically for effects
such as rain splashes. This path requires the Mobile or Forward+ renderer;
Compatibility does not support particle sub-emitters.

## Bentosaur adaptation

The reference game uses a side-view ground line. Bentosaur's approved Home
Village is a fixed, deep-perspective portrait painting. A single horizontal
collision line would make every splash appear at the same depth and would cut
off rain over most of the pavement.

V001 therefore separates:

- atmospheric back rain;
- a smaller foreground rain field;
- invisible impact seeds that collide with one static, pavement-only SDF
  surface;
- an eight-frame soft flat-cel splash atlas triggered by those collisions.

The invisible surface uses a varied perspective contour so impacts occur across
the depth of the wet square. It does not alter the approved background pixels.

## Motion contract

- Indirect warm spill and pavement reflections fade on once, then remain
  stable.
- Lantern/window cores receive only a very small continuous luminance drift.
- Halos inherit a lower-amplitude version of the same drift.
- Rain is already established on the first rendered frame; the village lights
  wake through the rainfall.
- Both visible rain layers and the splash atlas use normal alpha blending,
  cooler scene-derived tints, and restrained opacity. Rain reads as atmosphere
  instead of an emissive white overlay.
- `--reduced-weather` halves the active rain budget.
- `--deterministic-capture` fixes particle seeds for reproducible visual QA.
- `R` toggles rain in the desktop lab; `L` toggles registered lighting.

Particle ceilings at full density:

| System | Capacity |
| --- | ---: |
| Back rain | 96 |
| Front rain | 52 |
| Invisible collision seeds | 54 |
| Splash sub-emitter | 192 |

## Audio trial contract

- `Late Night Radio` by Kevin MacLeod loops continuously on the `Music` bus at
  `-21 dB`.
- `Gentle Rain 01` by DRAGON-STUDIO loops on the `Weather` bus at `-22 dB`.
- Rain audio starts whenever visible rain starts.
- Pressing `R` fades the rain channel over 240 ms, pauses it, and hides the
  visual weather. Pressing `R` again resumes the same ambience position and
  fades it back in with the weather.
- Music continues when rain is disabled.
- `--audio-off` disables both channels for silent automated captures.

## Living-light motion

The V004 calm baseline uses `0.992–1.006` core targets over `3.8–10.5 s`, 55%
halo inheritance, and one local flick every `60–105 s`.

The V005 physical-device test widened the core range and accelerated the local
flick, but its alpha-only core/halo output was still imperceptible on the
reference iPhone. That lighting profile is rejected.

The active V006 diagnostic repeats one fixed eight-second RGB-emission
trajectory. Cores hold at 55%, halos at 61.75%, and the indirect spill at
70.75% during the deliberately obvious minimum. At `5.3 s`, the brightest
left lantern performs a fixed double-flick. This is a compositor proof, not
final production motion; see the V006 checkpoint for exact timings.

In both profiles:

- smooth interpolation avoids a visible sine loop;
- wet-pavement reflections remain completely stable;
- a spatial mask limits every flick to one registered window or lantern;
- the diagnostic produces the same timeline at 30, 60, and 120 Hz.

## Roof-impact detail

- Tiny roof splashes reuse the authored eight-frame rain-impact atlas.
- Twenty-six registered anchor points cover only the approved tile planes
  identified in the visual review.
- One randomized one-shot timer emits an active V005 test impact every
  `0.26–0.62 s`; reduced weather slows this to `0.90–1.80 s`.
- Immediate anchor repetition is prevented.
- Roof splashes use only 26–42% scale and 42–54% opacity, remaining smaller and
  dimmer than pavement splashes.
- When the approved stall is present, the same scheduler routes 34% of events
  to sixteen stall-local roof anchors. That receiver inherits `StallStage`,
  renders at z-index 16, and uses 48–60% opacity so it stays registered on
  ultratall phones without merging coordinate systems.
- Disabling rain clears active roof impacts and stops their timer.

The source tracks, checksums, attribution, and license references are recorded
in `game/assets/audio/README.md`.

## Known lab boundaries

- The collision proof distributes splashes along one hidden perspective contour,
  not over a true 2D pavement mask. A shipping successor should use depth bands
  (or a dedicated pavement-impact shader) so splash scale and opacity decrease
  with distance.
- The approved background and four independently controllable light layers cost
  five full-screen passes. That is appropriate for this visual gate; profile on
  target phones before integration, then consider merging the stable spill and
  reflection layers while retaining separate animated cores and halos.
- The display-space lighting transcode is validated on Forward Mobile / Metal.
  Verify its output on Android Vulkan hardware before the production lock.
- The approved motion checkpoint remains a visual contract, not a native-device
  performance approval. Physical iPhone testing and the production ultratall
  environment master remain open.

## Rebuild

From the repository root:

```sh
python3 tools/art/build_home_village_runtime_assets.py
```

The builder deterministically generates the 720 × 1280 runtime environment
derivatives, two rain streak textures, the 8 × 1 splash atlas, and SHA-256
manifests. It also transcodes the approved linear-light overlay contribution
into the display-space additive deltas expected by Godot's Forward Mobile 2D
canvas. This preserves the approved lights-on result instead of compensating
with arbitrary runtime brightness multipliers.

## Launch

The lab intentionally does not modify `project.godot` or its current main scene:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  res://scenes/labs/home_village_rain_lab.tscn
```

Reduced weather:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  res://scenes/labs/home_village_rain_lab.tscn \
  -- --reduced-weather
```

Silent visual capture:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  res://scenes/labs/home_village_rain_lab.tscn \
  -- --deterministic-capture --audio-off
```

Contract test:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/home_village_rain_lab_test.gd
```
