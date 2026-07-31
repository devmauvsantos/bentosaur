#!/usr/bin/env python3
"""Build the deterministic visual proof for Stall Lighting Gate 2.

The generated sheet is only a source candidate. This builder extracts one
canonical off shell, reuses it for every fixture, and constructs the on state
from separate core/halo layers. As a result, changing power cannot change the
lantern silhouette.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[2]
PACK_ROOT = (
    REPO_ROOT
    / "art/source-assets/home-menu/stall/v003-lantern-lighting"
)
COMPONENT_ROOT = PACK_ROOT / "components"
REGISTERED_ROOT = PACK_ROOT / "registered"
REVIEW_ROOT = PACK_ROOT / "reviews"

BACKGROUND_PATH = (
    REPO_ROOT
    / "game/assets/environments/home_village/v001/background_unlit_720x1280.png"
)
STALL_PATH = (
    REPO_ROOT
    / "game/assets/environments/home_village/v001/stall/"
    "stall_structure_unlit_720x1280.png"
)

ANCHOR_PATH = COMPONENT_ROOT / "stall_lantern_anchor_candidate_v001.png"
BODY_PATH = COMPONENT_ROOT / "stall_lantern_body_off_candidate_v001.png"
CORE_PATH = COMPONENT_ROOT / "stall_lantern_core_candidate_v001.png"

RUNTIME_SIZE = (720, 1280)
BODY_RUNTIME_WIDTH = 75
BODY_TOPS = ((97, 425), (546, 425))
ANCHOR_TOP_Y = 392


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)


def _resize_width(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _paste(canvas: Image.Image, layer: Image.Image, position: tuple[int, int]) -> None:
    canvas.alpha_composite(layer, position)


def _additive_composite(base: Image.Image, layer: Image.Image) -> Image.Image:
    base_rgba = np.asarray(base.convert("RGBA"), dtype=np.float32) / 255.0
    layer_rgba = np.asarray(layer.convert("RGBA"), dtype=np.float32) / 255.0
    contribution = layer_rgba[..., :3] * layer_rgba[..., 3, None]
    rgb = np.clip(base_rgba[..., :3] + contribution, 0.0, 1.0)
    alpha = np.maximum(base_rgba[..., 3], layer_rgba[..., 3])
    encoded = np.dstack((rgb, alpha))
    return Image.fromarray(
        np.round(encoded * 255.0).astype(np.uint8),
        mode="RGBA",
    )


def _with_opacity(layer: Image.Image, opacity: float) -> Image.Image:
    adjusted = layer.copy().convert("RGBA")
    alpha = adjusted.getchannel("A").point(
        lambda value: round(value * opacity)
    )
    adjusted.putalpha(alpha)
    return adjusted


def _make_halo_layer(
    centers: tuple[tuple[int, int], ...],
    size: tuple[int, int] = RUNTIME_SIZE,
) -> Image.Image:
    scale = 4
    halo = Image.new("RGBA", (size[0] * scale, size[1] * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(halo)
    for center_x, center_y in centers:
        box = (
            (center_x - 58) * scale,
            (center_y - 68) * scale,
            (center_x + 58) * scale,
            (center_y + 68) * scale,
        )
        draw.ellipse(box, fill=(255, 156, 44, 78))
        inner = (
            (center_x - 31) * scale,
            (center_y - 40) * scale,
            (center_x + 31) * scale,
            (center_y + 40) * scale,
        )
        draw.ellipse(inner, fill=(255, 196, 76, 92))
    halo = halo.filter(ImageFilter.GaussianBlur(20 * scale))
    return halo.resize(size, Image.Resampling.LANCZOS)


def _make_spill_layer(
    centers: tuple[tuple[int, int], ...],
    size: tuple[int, int] = RUNTIME_SIZE,
) -> Image.Image:
    scale = 3
    spill = Image.new("RGBA", (size[0] * scale, size[1] * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(spill)
    for center_x, center_y in centers:
        draw.ellipse(
            (
                (center_x - 92) * scale,
                (center_y - 112) * scale,
                (center_x + 92) * scale,
                (center_y + 138) * scale,
            ),
            fill=(255, 136, 35, 34),
        )
    spill = spill.filter(ImageFilter.GaussianBlur(42 * scale))
    return spill.resize(size, Image.Resampling.LANCZOS)


def _fit_components() -> tuple[Image.Image, Image.Image, Image.Image]:
    anchor_source = Image.open(ANCHOR_PATH).convert("RGBA")
    body_source = Image.open(BODY_PATH).convert("RGBA")
    core_source = Image.open(CORE_PATH).convert("RGBA")

    body = _resize_width(body_source, BODY_RUNTIME_WIDTH)
    scale = body.width / body_source.width
    anchor = anchor_source.resize(
        (
            round(anchor_source.width * scale),
            round(anchor_source.height * scale),
        ),
        Image.Resampling.LANCZOS,
    )
    core = core_source.resize(
        (
            round(core_source.width * scale),
            round(core_source.height * scale),
        ),
        Image.Resampling.LANCZOS,
    )
    return anchor, body, core


def _build_registered_layers() -> dict[str, Image.Image]:
    anchor, body, core = _fit_components()
    anchors = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))
    bodies = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))
    cores = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))

    core_local_x = (body.width - core.width) // 2
    core_local_y = 54
    for body_x, body_y in BODY_TOPS:
        center_x = body_x + body.width // 2
        anchor_x = center_x - anchor.width // 2
        _paste(anchors, anchor, (anchor_x, ANCHOR_TOP_Y))
        _paste(bodies, body, (body_x, body_y))
        _paste(cores, core, (body_x + core_local_x, body_y + core_local_y))

    glow_centers = tuple(
        (body_x + body.width // 2, body_y + 91) for body_x, body_y in BODY_TOPS
    )
    return {
        "anchors": anchors,
        "bodies_off": bodies,
        "cores_add": cores,
        "halos_add": _make_halo_layer(glow_centers),
        "warm_spill_add": _make_spill_layer(glow_centers),
    }


def _build_scene_proofs(layers: dict[str, Image.Image]) -> tuple[Image.Image, Image.Image]:
    background = Image.open(BACKGROUND_PATH).convert("RGBA")
    stall = Image.open(STALL_PATH).convert("RGBA")

    unlit_base = background.copy()
    _paste(unlit_base, stall, (0, 0))
    _paste(unlit_base, layers["anchors"], (0, 0))
    _paste(unlit_base, layers["bodies_off"], (0, 0))

    lit = background.copy()
    lit = _additive_composite(lit, layers["warm_spill_add"])
    _paste(lit, stall, (0, 0))
    lit = _additive_composite(lit, _with_opacity(layers["halos_add"], 0.82))
    _paste(lit, layers["anchors"], (0, 0))
    _paste(lit, layers["bodies_off"], (0, 0))
    lit = _additive_composite(lit, _with_opacity(layers["cores_add"], 0.68))
    return unlit_base, lit


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    filename = "Arial Bold.ttf" if bold else "Arial.ttf"
    return ImageFont.truetype(
        f"/System/Library/Fonts/Supplemental/{filename}",
        size,
    )


def _center_text(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
) -> None:
    bounds = draw.textbbox((0, 0), text, font=font)
    text_width = bounds[2] - bounds[0]
    draw.text((x + (width - text_width) // 2, y), text, font=font, fill=fill)


def _build_review_board(off: Image.Image, on: Image.Image) -> Image.Image:
    board = Image.new("RGBA", (1600, 1120), (24, 30, 39, 255))
    draw = ImageDraw.Draw(board)
    cream = (244, 232, 205, 255)
    muted = (181, 190, 204, 255)
    card = (36, 45, 57, 255)

    _center_text(
        draw,
        0,
        28,
        board.width,
        "VISUAL GATE 02 — MODULAR STALL LANTERN",
        _font(38, bold=True),
        cream,
    )
    _center_text(
        draw,
        0,
        78,
        board.width,
        "OFF is the canonical shell · ON adds core + halo · geometry never changes",
        _font(23),
        muted,
    )

    crop_box = (0, 245, 720, 755)
    off_crop = off.crop(crop_box)
    on_crop = on.crop(crop_box)
    panel_positions = ((50, 154, "OFF"), (830, 154, "ON"))
    for image, (x, y, label) in zip((off_crop, on_crop), panel_positions):
        draw.rounded_rectangle((x - 4, y - 4, x + 724, y + 562), 18, fill=card)
        board.alpha_composite(image, (x, y + 48))
        _center_text(draw, x, y + 8, 720, label, _font(28, bold=True), cream)

    component_y = 784
    draw.rounded_rectangle((50, component_y, 1550, 1080), 20, fill=card)
    _center_text(
        draw,
        50,
        component_y + 18,
        1500,
        "SHIPPING LAYER CONTRACT",
        _font(24, bold=True),
        cream,
    )

    anchor = Image.open(ANCHOR_PATH).convert("RGBA")
    body = Image.open(BODY_PATH).convert("RGBA")
    core = Image.open(CORE_PATH).convert("RGBA")
    anchor_preview = _resize_width(anchor, 90)
    body_preview = _resize_width(body, 80)
    core_preview = _resize_width(core, 74)
    board.alpha_composite(anchor_preview, (165, 872))
    board.alpha_composite(body_preview, (485, 826))
    board.alpha_composite(core_preview, (794, 872))

    labels = (
        (90, "FIXED ANCHOR", "does not sway"),
        (420, "OFF SHELL", "canonical physical art"),
        (720, "ON CORE", "additive child layer"),
        (1045, "RUNTIME HALO", "procedural, follows shell"),
        (1320, "WARM SPILL", "registered, mostly stationary"),
    )
    for x, title, subtitle in labels:
        draw.text((x, 1020), title, font=_font(18, bold=True), fill=cream)
        draw.text((x, 1047), subtitle, font=_font(16), fill=muted)

    # Small deterministic swatches communicate the two soft runtime layers.
    swatch_halo = _make_halo_layer(((60, 60),), (120, 120))
    swatch_spill = _make_spill_layer(((75, 65),), (150, 130))
    board.alpha_composite(swatch_halo, (1090, 845))
    board.alpha_composite(swatch_spill, (1350, 840))
    return board


def main() -> None:
    required = (BACKGROUND_PATH, STALL_PATH, ANCHOR_PATH, BODY_PATH, CORE_PATH)
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)

    layers = _build_registered_layers()
    output_paths: dict[str, Path] = {}
    for layer_name, image in layers.items():
        output = REGISTERED_ROOT / f"stall_lantern_{layer_name}_registered_candidate_v001.png"
        _save(image, output)
        output_paths[layer_name] = output

    off, on = _build_scene_proofs(layers)
    off_path = REVIEW_ROOT / "stall-lantern-off-registered-composite-v001.png"
    on_path = REVIEW_ROOT / "stall-lantern-on-registered-composite-v001.png"
    board_path = REVIEW_ROOT / "stall-lantern-off-on-approval-board-v001.png"
    _save(off, off_path)
    _save(on, on_path)
    _save(_build_review_board(off, on), board_path)

    report = {
        "pack_id": "home-menu-stall-lantern-gate02-v003",
        "status": "candidate_pending_founder_approval",
        "runtime_canvas": list(RUNTIME_SIZE),
        "body_runtime_width": BODY_RUNTIME_WIDTH,
        "body_top_lefts": [list(position) for position in BODY_TOPS],
        "anchor_top_y": ANCHOR_TOP_Y,
        "state_contract": {
            "off": ["anchors", "bodies_off"],
            "on": [
                "anchors",
                "bodies_off",
                "cores_add",
                "halos_add",
                "warm_spill_add",
            ],
            "geometry_changes_on_power_toggle": False,
        },
        "outputs": {
            key: {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "sha256": _sha256(path),
            }
            for key, path in {
                **output_paths,
                "off_review": off_path,
                "on_review": on_path,
                "approval_board": board_path,
            }.items()
        },
    }
    report_path = PACK_ROOT / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path.relative_to(REPO_ROOT))
    print(board_path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
