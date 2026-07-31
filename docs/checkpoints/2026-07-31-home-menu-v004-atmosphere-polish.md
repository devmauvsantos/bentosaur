# Home Menu V004 — Quiet Atmosphere Polish

Status: implemented, desktop-verified, and signed for iOS; physical-device
verification pending because the paired phone was unavailable

Date: 2026-07-31

## Founder direction

Keep the approved rainy Home composition calm and handmade while adding three
nearly subliminal cues:

1. irregular, non-repeating warmth in the village windows and lanterns;
2. a rare, slight electrical-like flick no more than once per minute;
3. enough lower-stall shading to prevent the cutout from reading as flat.

The music and rain bed should both become a little quieter. The approved anime
transfer must be proven persistent rather than judged from memory.

## Locked implementation

### Living light

- Cores move between randomized `0.992–1.006` luminance targets.
- Segment lengths vary from `3.8–10.5 s` and use smooth interpolation, producing
  uneven hills rather than a visible sine loop.
- Halos inherit 55% of this already sub-one-percent drift.
- Indirect warm spill and wet-pavement reflections remain fixed after wake.
- A local dip/rebound is scheduled every `60–105 s`, never more than once per
  minute.
- The rebound is capped at `1.003`, so even the brightest allowed global pulse
  stays below the core layer's alpha ceiling instead of flattening at a clipped
  peak.
- Each event selects one of ten registered fixtures. An aspect-correct spatial
  mask prevents the aggregate light map from brownout or vertical smearing.
- Fixed-seed tests produce the same event times and fixture choices at 30, 60,
  and 120 Hz.

### Stall depth

The complete stall uses one shared, reusable cool-tinted lower-falloff material:

- strength `0.075`;
- starts at authored UV `0.52`;
- reaches its maximum at UV `0.88`;
- leaves the roof, sign, alpha edges, and upper structure unchanged.

The corrected shader uses the incoming canvas `COLOR`; sampling the texture a
second time would square the source colors and is a forbidden regression. The
future foreground counter occluder must share this exact material so it cannot
draw a brighter patch over the stall.

Shared resource:
`game/assets/vfx/lighting/stall_depth_falloff_material.tres`.

![Corrected subtle stall-depth A/B](assets/stall-depth-falloff-fixed-ab-v004.png)

Temporal-median A/B measurements:

- upper opaque stall mean absolute error: effectively `0 / 255`;
- lower falloff mean absolute change: `0.394 / 255`;
- lower p95 channel change: `1`;
- maximum temporal-median change: `4`.

This is intentionally almost imperceptible. Any stronger revision requires a
new phone visual gate rather than silently increasing the value.

### Audio

- `Late Night Radio`: `-21 dB` on the `Music` bus.
- `Gentle Rain 01`: `-22 dB` on the `Weather` bus.

The source loudness and license details remain in
`game/assets/audio/README.md`.

## Anime-transfer persistence proof

The production Home scene contains one full-screen CanvasLayer at layer `100`,
using approved preset 3. There is no runtime script, tween, timer, or state path
that lowers its strength or visibility.

Godot's [screen-reading shader documentation](https://docs.godotengine.org/en/stable/tutorials/shaders/screen-reading_shaders.html)
states that the first 2D `hint_screen_texture` use triggers a full-screen
back-buffer copy and warns primarily about overlapping screen-reading shaders.
Home has exactly one such post-process, so that documented overlap failure mode
does not apply here.

![Preset 3 off versus on](assets/anime-preset3-off-vs-on-detail-v004.png)

The controlled static A/B changed `99.2100%` of pixels, with RGB mean absolute
error `3.3295 / 255`. Two filter-off controls were byte-identical.

![Preset 3 persistence from 0 to 90 seconds](assets/anime-preset3-persistence-0-to-90s-v004.png)

The filtered-versus-clean difference remained stable through a 90-second
accelerated capture:

| Time | Changed pixels | RGB MAE / 255 |
| ---: | ---: | ---: |
| 0 s | 99.5293% | 4.3918 |
| 10 s | 99.5195% | 4.4614 |
| 30 s | 99.5260% | 4.4584 |
| 60 s | 99.5271% | 4.4556 |
| 90 s | 99.5285% | 4.4593 |

From 2–90 seconds, MAE standard deviation was only `0.00228`; no fade or stop
occurred. A separate physical-device lifecycle check is still required for the
specific foreground → background → foreground path.

The transfer grain is currently authored in physical pixels. It therefore
appears finer on the Retina framebuffer than in the 540 × 960 desktop preview.
Changing grain scale is an aesthetic revision and remains outside this
checkpoint.

## Integrated Pro Max proof

![Home Menu V004 at 720 by 1564](assets/home-menu-v004-light-motion-depth-pro-max.png)

This Metal render contains the responsive approved stall, rain, registered
lights, subtle lower depth, and anime preset 3 at the iPhone 17 Pro Max logical
aspect.

## Environment canvas decision

The current 9:16 world is uniformly cover-scaled on an ultratall phone, which
crops approximately 65 authored pixels from each side. Merely generating more
village to the left and right does not solve that geometry: the cover transform
would still scale to height and crop it.

The correct next visual gate is a vertically extended `1440 × 3200` master:

- protect the approved `1440 × 2560` composition at the top;
- outpaint `640 px` of wet pavement below it;
- pad all four registered light maps transparently to the same canvas;
- keep the current 9:16 assets untouched;
- replace the cover bridge only after the extended unlit image passes founder
  approval and seam QA.

No experimental outpaint is promoted by this checkpoint.

## Verification

- All 11 base Godot contract tests pass.
- Both deterministic rain-lab variants pass, including reduced weather.
- Metal 720 × 1564 integrated capture succeeds.
- Godot iOS debug export succeeds.
- Generated-Xcode personal-signing contract passes.
- Generic iOS device build succeeds and passes strict code-sign verification.
- Bundle: `com.mauvsantos.bentosaur`.
- Team: `53RJ43876F`.
- Identity: `Apple Development: Mauricio Vargas (CRAZV8U43J)`.
- The paired iPhone 17 Pro Max was listed as unavailable, so install, listening,
  and foreground → background → foreground filter checks remain pending.
