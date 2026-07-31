# Anime 90s Post-process

Status: preset 3 approved for the Bentosaur home menu — 2026-07-31

The runtime shader is a Bentosaur-specific adaptation of the post-processing
study in OrdinaryCicada's purchased
[Godot 4 Project - Shader Studies v1](https://oddpotatodev.itch.io/godot-46-shader-studies-v1).
The creator's product page explicitly permits use, editing, remixing, and
commercial projects.

The approved `Heavy transfer` preset uses restrained animated grain, a small
chromatic offset, mild glow bleed, a subtle luma curve, and slight
desaturation. Curvature, vignette, and scanlines stay disabled so the effect
reads as a 1990s animation transfer rather than a CRT overlay.

Runtime component:

`res://scenes/vfx/anime_90s_post_process.tscn`

The post-process lives in CanvasLayer 100, above the registered world canvas.
Its full-viewport ColorRect samples the completed screen, so background,
lighting, stall, and rain receive one coherent treatment.

The comparison lab remains available at
`res://scenes/labs/home_village_anime_90s_lab.tscn`. On desktop, keys `0`–`3`
select its four trial presets and `P` toggles the filter.
