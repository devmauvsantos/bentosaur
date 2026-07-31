#!/usr/bin/env python3
"""Build deterministic Godot-ready Home Village and rain VFX assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "art/environments/home-village/env-v001"
ENV_OUTPUT = REPO_ROOT / "game/assets/environments/home_village/v001"
RAIN_OUTPUT = REPO_ROOT / "game/assets/vfx/weather/rain/v001"
RUNTIME_SIZE = (720, 1280)

ENVIRONMENT_SOURCES = {
    "background_unlit_720x1280.png": (
        SOURCE_ROOT
        / "source/bentosaur-home-village-background-unlit-approved-v001.png"
    ),
    "lighting/indirect_warm_spill_720x1280.png": (
        SOURCE_ROOT
        / "lighting/lighting-v001/"
        "bentosaur-home-village-lighting-v001-indirect-warm-spill.png"
    ),
    "lighting/light_halos_720x1280.png": (
        SOURCE_ROOT
        / "lighting/lighting-v001/"
        "bentosaur-home-village-lighting-v001-light-halos.png"
    ),
    "lighting/light_cores_720x1280.png": (
        SOURCE_ROOT
        / "lighting/lighting-v001/"
        "bentosaur-home-village-lighting-v001-light-cores.png"
    ),
    "lighting/warm_reflections_720x1280.png": (
        SOURCE_ROOT
        / "lighting/lighting-v001/"
        "bentosaur-home-village-lighting-v001-warm-reflections.png"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)


def _srgb_to_linear(value: np.ndarray) -> np.ndarray:
    return np.where(
        value <= 0.04045,
        value / 12.92,
        ((value + 0.055) / 1.055) ** 2.4,
    )


def _linear_to_srgb(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return np.where(
        value <= 0.0031308,
        value * 12.92,
        1.055 * np.power(value, 1.0 / 2.4) - 0.055,
    )


def _transcode_lighting_for_godot_canvas() -> None:
    """Encode linear-light source contributions for Godot's sRGB canvas add."""
    background_path = ENV_OUTPUT / "background_unlit_720x1280.png"
    base_srgb = (
        np.asarray(Image.open(background_path).convert("RGB"), dtype=np.float32)
        / 255.0
    )
    accumulated_linear = _srgb_to_linear(base_srgb)
    layer_paths = [
        ENV_OUTPUT / "lighting/indirect_warm_spill_720x1280.png",
        ENV_OUTPUT / "lighting/light_halos_720x1280.png",
        ENV_OUTPUT / "lighting/light_cores_720x1280.png",
        ENV_OUTPUT / "lighting/warm_reflections_720x1280.png",
    ]
    for layer_path in layer_paths:
        source_rgba = (
            np.asarray(Image.open(layer_path).convert("RGBA"), dtype=np.float32)
            / 255.0
        )
        contribution_linear = (
            _srgb_to_linear(source_rgba[..., :3]) * source_rgba[..., 3, None]
        )
        before_srgb = _linear_to_srgb(accumulated_linear)
        accumulated_linear = np.clip(
            accumulated_linear + contribution_linear,
            0.0,
            1.0,
        )
        after_srgb = _linear_to_srgb(accumulated_linear)
        display_space_delta = np.maximum(after_srgb - before_srgb, 0.0)

        # Godot Forward Mobile canvas additive blending applies the texture's
        # RGB contribution in display space. Store the exact incremental delta
        # with opaque alpha so a CanvasItem additive pass reconstructs the
        # approved linear-light composite instead of under-driving it.
        alpha = np.ones(display_space_delta.shape[:2] + (1,), dtype=np.float32)
        encoded = np.dstack((display_space_delta, alpha))
        save_png(
            Image.fromarray(
                np.round(np.clip(encoded, 0.0, 1.0) * 255.0).astype(np.uint8),
                mode="RGBA",
            ),
            layer_path,
        )


def build_environment() -> list[dict[str, object]]:
    for relative_output, source_path in ENVIRONMENT_SOURCES.items():
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        with Image.open(source_path) as source:
            mode = "RGBA" if "lighting/" in relative_output else "RGB"
            runtime = source.convert(mode).resize(
                RUNTIME_SIZE,
                Image.Resampling.LANCZOS,
            )
        output_path = ENV_OUTPUT / relative_output
        save_png(runtime, output_path)

    _transcode_lighting_for_godot_canvas()

    built: list[dict[str, object]] = []
    for relative_output, source_path in ENVIRONMENT_SOURCES.items():
        output_path = ENV_OUTPUT / relative_output
        built.append(
            {
                "output": output_path.relative_to(REPO_ROOT).as_posix(),
                "output_sha256": sha256(output_path),
                "source": source_path.relative_to(REPO_ROOT).as_posix(),
                "source_sha256": sha256(source_path),
                "size": list(RUNTIME_SIZE),
            }
        )
    return built


def _draw_streak(width: int, height: int, strength: float) -> Image.Image:
    scale = 6
    size = (width * scale, height * scale)
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    core = Image.new("RGBA", size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    core_draw = ImageDraw.Draw(core)
    start = (int(width * 0.68 * scale), int(height * 0.08 * scale))
    end = (int(width * 0.32 * scale), int(height * 0.92 * scale))
    glow_draw.line(
        (start, end),
        fill=(111, 184, 240, int(72 * strength)),
        width=max(4, int(width * 0.42 * scale)),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(max(2, int(width * scale * 0.16))))
    core_draw.line(
        (start, end),
        fill=(205, 233, 255, int(196 * strength)),
        width=max(3, int(width * 0.13 * scale)),
    )
    highlight_end = (
        int(start[0] + (end[0] - start[0]) * 0.58),
        int(start[1] + (end[1] - start[1]) * 0.58),
    )
    core_draw.line(
        (start, highlight_end),
        fill=(239, 249, 255, int(214 * strength)),
        width=max(2, int(width * 0.065 * scale)),
    )
    return Image.alpha_composite(glow, core).resize(
        (width, height),
        Image.Resampling.LANCZOS,
    )


def _arc(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    start: int,
    end: int,
    color: tuple[int, int, int, int],
    width: int,
    scale: int,
) -> None:
    scaled = tuple(int(value * scale) for value in box)
    draw.arc(scaled, start=start, end=end, fill=color, width=width * scale)


def _line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    color: tuple[int, int, int, int],
    width: int,
    scale: int,
) -> None:
    draw.line(
        [(int(x * scale), int(y * scale)) for x, y in points],
        fill=color,
        width=width * scale,
        joint="curve",
    )


def _ellipse(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    color: tuple[int, int, int, int],
    scale: int,
) -> None:
    draw.ellipse(
        tuple(int(value * scale) for value in box),
        fill=color,
    )


def _draw_splash_frame(frame: int, cell_width: int, cell_height: int) -> Image.Image:
    scale = 5
    canvas = Image.new(
        "RGBA",
        (cell_width * scale, cell_height * scale),
        (0, 0, 0, 0),
    )
    outline = ImageDraw.Draw(canvas)
    highlight = ImageDraw.Draw(canvas)
    blue = (112, 178, 222, 165)
    white = (223, 243, 255, 225)
    faint_blue = (112, 178, 222, 92)
    faint_white = (223, 243, 255, 126)

    if frame == 0:
        _line(outline, [(32, 5), (31, 18)], blue, 3, scale)
        _line(highlight, [(32, 6), (31, 17)], white, 1, scale)
        _ellipse(outline, (28, 18, 34, 23), blue, scale)
        _ellipse(highlight, (29, 18, 33, 21), white, scale)
    elif frame == 1:
        _line(outline, [(31, 8), (31, 19)], blue, 3, scale)
        _line(highlight, [(31, 8), (31, 17)], white, 1, scale)
        _arc(outline, (22, 16, 42, 28), 194, 346, blue, 3, scale)
        _arc(highlight, (23, 17, 41, 27), 197, 343, white, 1, scale)
    elif frame == 2:
        _line(outline, [(30, 20), (23, 12), (18, 9)], blue, 3, scale)
        _line(outline, [(34, 20), (41, 12), (46, 10)], blue, 3, scale)
        _line(highlight, [(30, 19), (23, 12), (19, 10)], white, 1, scale)
        _line(highlight, [(34, 19), (41, 12), (45, 11)], white, 1, scale)
        _arc(outline, (24, 18, 40, 28), 190, 350, blue, 3, scale)
        _arc(highlight, (25, 19, 39, 27), 194, 346, white, 1, scale)
    elif frame == 3:
        _arc(outline, (12, 14, 52, 31), 188, 352, blue, 3, scale)
        _arc(highlight, (13, 15, 51, 30), 192, 348, white, 1, scale)
        _ellipse(outline, (13, 8, 18, 13), blue, scale)
        _ellipse(highlight, (14, 8, 17, 11), white, scale)
        _ellipse(outline, (47, 6, 52, 11), blue, scale)
        _ellipse(highlight, (48, 6, 51, 9), white, scale)
    elif frame == 4:
        _arc(outline, (5, 13, 59, 31), 184, 356, blue, 3, scale)
        _arc(highlight, (6, 14, 58, 30), 188, 352, white, 1, scale)
        _arc(outline, (20, 19, 44, 29), 190, 350, faint_blue, 2, scale)
        _ellipse(outline, (7, 10, 11, 14), blue, scale)
        _ellipse(outline, (54, 9, 58, 13), blue, scale)
    elif frame == 5:
        _arc(outline, (2, 15, 34, 31), 185, 305, blue, 3, scale)
        _arc(outline, (30, 15, 62, 31), 235, 355, blue, 3, scale)
        _arc(highlight, (3, 16, 33, 30), 188, 302, white, 1, scale)
        _arc(highlight, (31, 16, 61, 30), 238, 352, white, 1, scale)
        _ellipse(outline, (15, 13, 18, 16), faint_blue, scale)
        _ellipse(outline, (47, 12, 50, 15), faint_blue, scale)
    elif frame == 6:
        _arc(outline, (2, 18, 62, 32), 188, 352, faint_blue, 2, scale)
        _arc(highlight, (7, 19, 57, 31), 192, 348, faint_white, 1, scale)
    else:
        _line(
            outline,
            [(13, 27), (24, 26), (32, 27), (40, 26), (51, 27)],
            (112, 178, 222, 45),
            1,
            scale,
        )

    return canvas.resize((cell_width, cell_height), Image.Resampling.LANCZOS)


def build_rain() -> list[dict[str, object]]:
    RAIN_OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = {
        "rain_streak_back.png": _draw_streak(10, 42, 0.72),
        "rain_streak_front.png": _draw_streak(16, 72, 1.0),
        "rain_impact_seed_transparent.png": Image.new(
            "RGBA",
            (1, 1),
            (0, 0, 0, 0),
        ),
    }

    frame_count = 8
    cell_size = (64, 32)
    atlas = Image.new(
        "RGBA",
        (cell_size[0] * frame_count, cell_size[1]),
        (0, 0, 0, 0),
    )
    for frame in range(frame_count):
        atlas.alpha_composite(
            _draw_splash_frame(frame, *cell_size),
            (frame * cell_size[0], 0),
        )
    assets["rain_splash_8x1.png"] = atlas

    built: list[dict[str, object]] = []
    for filename, image in assets.items():
        path = RAIN_OUTPUT / filename
        save_png(image, path)
        built.append(
            {
                "output": path.relative_to(REPO_ROOT).as_posix(),
                "output_sha256": sha256(path),
                "size": list(image.size),
            }
        )
    return built


def write_manifests(
    environment_assets: list[dict[str, object]],
    rain_assets: list[dict[str, object]],
) -> None:
    environment_manifest = {
        "asset_id": "env.home_village.runtime.v001",
        "canvas": {"width": RUNTIME_SIZE[0], "height": RUNTIME_SIZE[1]},
        "source_package": "art/environments/home-village/env-v001",
        "lighting_blend_mode": "additive",
        "lighting_source_space": "linear-light straight-alpha contribution",
        "lighting_runtime_space": "Godot Forward Mobile canvas sRGB additive delta",
        "lighting_order": [
            "indirect_warm_spill",
            "light_halos",
            "light_cores",
            "warm_reflections",
        ],
        "assets": environment_assets,
        "builder": "tools/art/build_home_village_runtime_assets.py",
    }
    rain_manifest = {
        "asset_id": "vfx.weather.rain.v001",
        "style": "soft flat-cel storybook rain",
        "splash_atlas": {
            "frames": 8,
            "layout": "8x1",
            "cell_size": [64, 32],
            "duration_seconds": 0.34,
        },
        "assets": rain_assets,
        "builder": "tools/art/build_home_village_runtime_assets.py",
    }
    (ENV_OUTPUT / "runtime_manifest.json").write_text(
        json.dumps(environment_manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    (RAIN_OUTPUT / "runtime_manifest.json").write_text(
        json.dumps(rain_manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    environment_assets = build_environment()
    rain_assets = build_rain()
    write_manifests(environment_assets, rain_assets)
    print(
        "Built "
        f"{len(environment_assets)} environment assets and "
        f"{len(rain_assets)} rain assets."
    )


if __name__ == "__main__":
    main()
