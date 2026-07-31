# Mobile Display Quality Contract V001

Status: locked implementation baseline

Effective: 2026-07-31

Primary high-end reference device: iPhone 17 Pro Max

## What “720 × 1280” means

Bentosaur keeps a `720 × 1280` **logical design grid**. It is not a 720p
framebuffer and it does not cap the iPhone's output resolution.

Godot's `canvas_items` stretch mode renders 2D directly at the target display
resolution. On the reference iPhone, that target is `1320 × 2868` physical
pixels. The logical grid keeps gameplay coordinates readable and stable while
Godot rasterizes controls, particles, transforms, and dynamic text at the
device resolution.

The locked project settings are:

```ini
[application]
run/max_fps=0

[display]
window/size/viewport_width=720
window/size/viewport_height=1280
window/stretch/mode="canvas_items"
window/stretch/aspect="expand"
window/stretch/scale_mode="fractional"
window/handheld/orientation=1
window/dpi/allow_hidpi=true
window/ios/allow_high_refresh_rate=true
window/vsync/vsync_mode=1

[rendering]
renderer/rendering_method="mobile"
renderer/rendering_method.mobile="mobile"
rendering_device/driver.ios="metal"
```

Godot recommends `720 × 1280` for a portrait mobile base, with `1080 × 1920`
as an alternative for projects targeting high-end hardware. Bentosaur does not
gain sharpness merely by multiplying every logical coordinate by 1.5:
`canvas_items` already renders at the target resolution. The higher-value move
is to preserve the stable logical grid and supply sufficiently large source
art, native text, vector UI where useful, and responsive layouts.

Sources:

- [Godot 4.7 multiple-resolution guidance](https://docs.godotengine.org/en/4.7/tutorials/rendering/multiple_resolutions.html#mobile-game-in-portrait-mode)
- [Apple iPhone 17 Pro and Pro Max specifications](https://www.apple.com/iphone-17-pro/specs/)

## Reference device geometry

| Property | iPhone 17 Pro Max |
|---|---:|
| Physical display | 1320 × 2868 px |
| Logical display | 440 × 956 pt at 3× |
| Portrait ratio | 110:239, approximately 19.55:9 |
| Maximum refresh | Adaptive ProMotion up to 120 Hz |

The iPhone is substantially taller than 9:16. `expand` therefore exposes more
logical canvas instead of non-uniformly stretching the scene or adding black
bars. Full-bleed scenery can occupy that space; interactive UI must be anchored
inside the runtime safe area.

## Full-bleed and safe-area rules

- Backgrounds, rain, lighting, and noninteractive ambience extend edge to edge.
- Buttons, currency, navigation, text, and touch targets use
  `DisplayServer.get_display_safe_area()` at runtime.
- No Dynamic Island, status-bar, or Home-indicator inset is hardcoded.
- Safe-area layout updates when the viewport size changes.
- The central 9:16 composition remains a cross-device safe region.
- Tall and tablet variants expose or extend scenery; they never squash it.

The current approved `720 × 1280` world is presented through one
native-main-viewport `CanvasLayer` cover transform. Background, registered
lighting, stall, rain, roof splashes, and pavement collisions share that
single transform so they cannot drift apart. On the iPhone 17 Pro Max, the
expanded logical canvas is approximately `720 × 1564`; the temporary cover
bridge scales the world uniformly by about `1.222` and crops about `65.4`
design pixels from each side. The stall remains fully visible and no uncovered
band is exposed.

This centered crop is the prototype bridge, not the final environment-master
strategy. The final layered outpaint described below should replace the crop
when the ultratall source art is ready. Responsive UI must remain in a
separate, unscaled `CanvasLayer`.

Apple's layout guidance requires interfaces to account for device shape and
safe areas. Godot exposes the unobscured interactive region on both iOS and
Android:

- [Apple Human Interface Guidelines: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Godot DisplayServer safe area](https://docs.godotengine.org/en/4.7/classes/class_displayserver.html#class-displayserver-method-get-display-safe-area)

## Raster-art quality gate

The approved Home Village source is `941 × 1672`; the current runtime
derivatives are `720 × 1280`. They are sufficient for composition and motion
approval, but they are not the final native-density production masters for a
`1320 × 2868` display.

Before the environment ships:

1. Outpaint the approved scene vertically instead of stretching it.
2. Preserve the center 9:16 composition exactly.
3. Produce a layered source master of at least `1440 × 3200`.
4. Keep critical scenery within a central `1440 × 2560` safe composition.
5. Rebuild the unlit background and every registered lighting layer from the
   same master and crop transform.
6. Import large painted layers losslessly with mipmaps when downscaling is
   expected.
7. Reapprove both 9:16 and ultratall captures before replacing the current
   visual checkpoint.

This is an asset-resolution gate, not a reason to reject the approved image.
The current image remains the composition and color authority.

## Frame-rate and motion quality

- Stable 60 fps is the production baseline.
- iOS may use adaptive 120 Hz when thermal and power conditions allow it.
- Gameplay and animation use elapsed time or `delta`, never frame counts.
- VSync remains enabled and the engine is not artificially capped.
- The full weather tier may be tested with a 60 Hz particle simulation;
  reduced weather may retain 30 Hz simulation if interpolation remains clean.
- Performance approval requires a sustained physical-device run, not only the
  iOS Simulator. The current rain sub-emitters require the Mobile renderer.

At 60 Hz the frame budget is 16.67 ms; at 120 Hz it is 8.33 ms. ProMotion is a
capability, not permission to compromise the stable 60 fps experience.

## Required viewport matrix

Every production screen must pass:

| Preview | Purpose |
|---|---|
| 540 × 960 | 9:16 development reference |
| 440 × 956 | iPhone 17 Pro Max aspect at logical preview scale |
| 540 × 1200 | Common 20:9 Android shape |
| 768 × 1024 | Tablet stress case |
| 1320 × 2868 physical device | Native iPhone visual, touch, thermal, and refresh gate |

## Explicit non-decisions

- HDR output is not enabled in this checkpoint. The approved palette is SDR;
  HDR requires its own color, glow, bandwidth, and device-validation gate.
- MSAA is not enabled blindly. The project is painted 2D; native canvas
  rendering and adequate texture sources matter more than polygon-edge MSAA.
- The approved 9:16 Home Village is not silently stretched, regenerated, or
  replaced while implementing display support.

The automated guard is:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/mobile_display_quality_contract_test.gd
```
