# Home Village Rain Lab V001

Status: implementation checkpoint, pending visual approval.

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
- a smaller, brighter front rain field;
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
- Rain density, splash readability, and the lights-to-rain timing remain pending
  the user's visual approval.

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

Contract test:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/home_village_rain_lab_test.gd
```
