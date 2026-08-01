# Home Menu V014 — Lantern-Motivated Lighting Study

Status: **visual approval pending; no runtime lighting changes**

Snapshot date: 2026-07-31

## Safety checkpoint

The exact approved build shown on the iPhone is preserved at:

- Commit: `118c472ef540b1e803e89d90276104738f6d43e6`
- Tag: `checkpoint/home-flat-light-approved-2026-07-31`
- Remote: the commit and tag are both pushed to `origin`

The unrelated untracked `art/environments/home-village/env-v001/ultratall/`
work is not part of this checkpoint and was not modified.

## Problem being solved

The stall and proprietor use attractive finished art, but their illumination is
nearly uniform. The surrounding village is painted as a dark rainy night, while
the stall and proprietor read as though they have broad studio illumination.
The lantern sprites glow, but they do not currently illuminate nearby artwork.

The scene audit confirms the mismatch:

- the village's registered warm spill is behind the stall at `z = 10`;
- the proprietor body, stall, hands, attachments, and lanterns occupy `z = 14–17`;
- the stall has only a mild `7.5%` lower-depth falloff;
- the proprietor has no lighting material;
- the lantern fixtures use additive core/halo sprites, not light receivers.

This is a lighting-stack issue, not a reason to repaint the approved stall or
character.

## Visual target

![Current approved versus proposed lantern-motivated lighting](home-menu-v014-current-vs-proposed-v001.png)

The right-hand image is an approval-only lighting concept. It is not a runtime
asset and is not pixel-identical source authority. It demonstrates four goals:

1. A restrained cool navy night base on non-emissive stall and character art.
2. Soft local amber falloff from the two hanging lanterns.
3. A smaller warm pool from the counter lantern.
4. Gentle eave, prop-contact, character/counter, and lower-cabinet depth.

The individual concept is stored at
`home-menu-v014-lantern-motivated-lighting-concept-v001.png`.

## Recommended first implementation after approval

Use a non-destructive, art-directed foreground relight. Do not use a global
`CanvasModulate`, because the village already has approved baked night lighting
and `CanvasModulate` affects an entire canvas.

Starting values for the balanced target:

| Receiver | Base multiplier |
|---|---:|
| Stall structure | `0.76` |
| Proprietor | `0.66` |
| Physical button frames | `0.80` |
| Live labels | about `0.90` |

- Cool ambient tint: approximately `Color(0.72, 0.80, 0.92)`, mixed at `0.18`.
- Hanging-lantern centers: `(134.5, 515)` and `(583.5, 515)` on the logical
  `720 × 1280` stage, with broad `270 × 240` falloff.
- Counter-lantern center: `(240.5, 675)`, with compact `125 × 135` falloff.
- Warm surface contribution: approximately `0.18–0.22`.
- Keep the existing lower-depth falloff for the first pass.
- Exclude additive lantern cores and halos from the ambient grade.
- Derive runtime light centers from the stall canvas transform so ultratall and
  iPhone layouts remain registered.

The first runtime version must ship behind an on/off comparison flag. It should
use static light energy first. Only after the static iPhone comparison is
approved should the warm pools share the existing lantern pulse/flick state.

## Explicitly deferred

- No replacement or repainting of approved art.
- No global scene darkening.
- No normal map on the proprietor's face.
- No dynamic `LightOccluder2D` shadows in the first pass.
- No `PCF13` shadow filtering.
- No motion coupling before the static lighting balance is approved.

Normal maps remain a possible later wood/counter experiment, but generated
normal maps can mistake painted highlights and outlines for geometry. They are
not needed to solve the current mismatch.

## Approval gate

Approve the **lighting relationship**, not exact AI-rendered pixels:

- Does the stall now belong to the same night as the village?
- Is Bentosaur still immediately readable and cute?
- Are lanterns clearly motivating the warm areas?
- Is the lower stall darker without losing button readability?
- Is the overall result still cozy rather than gloomy?

After approval, implement the balanced static treatment, capture it in Forward
Mobile/Metal, install it on the iPhone, and compare it against the checkpoint.

## Research references

- [Godot: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- [Godot: CanvasModulate](https://docs.godotengine.org/en/stable/classes/class_canvasmodulate.html)
- [Godot: Light2D](https://docs.godotengine.org/en/stable/classes/class_light2d.html)
- [Godot: CanvasTexture normal and specular maps](https://docs.godotengine.org/en/stable/classes/class_canvastexture.html)
- [Godot: CanvasItem shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html)
- [Godot official 2D Lights and Shadows demo](https://godotengine.org/asset-library/asset/2721)

## Concept-generation record

The concept was produced with the built-in image-generation tool as a
`lighting-weather` edit of the current deterministic V013 capture. The prompt
required the exact composition, objects, character pose, text, rain, and 90s
anime treatment to remain unchanged while only the light relationship changed.
The generated image is a visual target only; the approved runtime treatment
will be deterministic Godot lighting over the existing source assets.
