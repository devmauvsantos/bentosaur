#!/usr/bin/env python3
"""Build the registered hands-on-counter Bentosaur proprietor runtime kit.

The neutral candidate is the immutable registration authority. The generated
blink candidate is used only inside two feathered eye masks so generative
redraw differences cannot shimmer elsewhere during a blink. A foreground arm
and hand layer is cut from that same neutral source; Godot places the stall
between the body and this layer so the fingers can rest on the counter.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, __version__ as PILLOW_VERSION


REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_ROOT = (
    REPO_ROOT / "art/candidates/2d/proprietor-counter-pose-v001"
)
SOURCE_ROOT = CANDIDATE_ROOT / "exports"
OUTPUT_ROOT = (
    REPO_ROOT / "game/assets/characters/bentosaur_proprietor/v002"
)

SOURCE_SIZE = (1254, 1254)
COMMON_CROP = (192, 102, 1057, 1126)
RUNTIME_SIZE = (865, 1024)
LOGICAL_SCALE = 0.20
SPRITE_CENTER_FROM_COUNTER = (0.0, -512.0)

NEUTRAL_SOURCE = (
    SOURCE_ROOT / "bentosaur-proprietor-counter-neutral-transparent-v001.png"
)
BLINK_SOURCE = (
    SOURCE_ROOT / "bentosaur-proprietor-counter-blink-transparent-v001.png"
)
EXPECTED_SOURCE_HASHES = {
    NEUTRAL_SOURCE.name: (
        "07968f5530707c6af00682af8ad4ad73890439cb63c950995e046269057f9024"
    ),
    BLINK_SOURCE.name: (
        "7115ac4d5fb891f5e8d84b80bba26490e1bc99548e4c4f25ccbc06b7e87e28f9"
    ),
}

NEUTRAL_OUTPUT = "bentosaur_proprietor_counter_neutral_v002.png"
BLINK_OUTPUT = "bentosaur_proprietor_counter_blink_v002.png"
HANDS_OUTPUT = "bentosaur_proprietor_counter_hands_v002.png"

# Full-canvas coordinates. The generous feather stays on the green face and
# makes the eye-only edit disappear into the neutral source texture.
EYE_PATCH_ELLIPSES = (
    (390, 525, 555, 710),
    (690, 525, 855, 710),
)
EYE_PATCH_FEATHER_PX = 16.0

# The inner edges follow the authored arm lines and intentionally exclude the
# cream belly. The upper edge overlaps identical body pixels in open space;
# the only visible z-order change occurs where the stall counter sits between
# the body and this extracted foreground layer.
LEFT_FOREGROUND_ARM = (
    (180, 880),
    (420, 880),
    (430, 940),
    (470, 975),
    (515, 1010),
    (552, 1050),
    (570, 1126),
    (180, 1126),
)
RIGHT_FOREGROUND_ARM = tuple(
    (SOURCE_SIZE[0] - x, y) for x, y in LEFT_FOREGROUND_ARM
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decoded_rgba_sha256(path: Path) -> str:
    with Image.open(path) as loaded:
        image = loaded.convert("RGBA")
    digest = hashlib.sha256()
    digest.update(f"RGBA:{image.width}x{image.height}\0".encode("ascii"))
    digest.update(image.tobytes())
    return digest.hexdigest()


def _load_verified(path: Path) -> Image.Image:
    expected_hash = EXPECTED_SOURCE_HASHES[path.name]
    actual_hash = _sha256(path)
    if actual_hash != expected_hash:
        raise RuntimeError(
            f"Candidate source hash mismatch for {path}: "
            f"{actual_hash} != {expected_hash}"
        )
    with Image.open(path) as loaded:
        image = loaded.convert("RGBA")
    if image.size != SOURCE_SIZE:
        raise RuntimeError(f"Unexpected source size for {path}: {image.size}")
    return image


def _build_registered_blink(
    neutral: Image.Image,
    generated_blink: Image.Image,
) -> tuple[Image.Image, Image.Image]:
    mask = Image.new("L", SOURCE_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    for ellipse in EYE_PATCH_ELLIPSES:
        draw.ellipse(ellipse, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(EYE_PATCH_FEATHER_PX))
    return Image.composite(generated_blink, neutral, mask), mask


def _build_foreground_hands(neutral: Image.Image) -> tuple[Image.Image, Image.Image]:
    spatial_mask = Image.new("L", SOURCE_SIZE, 0)
    draw = ImageDraw.Draw(spatial_mask)
    draw.polygon(LEFT_FOREGROUND_ARM, fill=255)
    draw.polygon(RIGHT_FOREGROUND_ARM, fill=255)
    source_alpha = neutral.getchannel("A")
    final_mask = ImageChops.multiply(spatial_mask, source_alpha)
    foreground = neutral.copy()
    foreground.putalpha(final_mask)
    return foreground, final_mask


def _qa_image(path: Path, expected_alpha_bounds: tuple[int, int, int, int]) -> dict[str, Any]:
    with Image.open(path) as loaded:
        stored_mode = loaded.mode
        image = loaded.convert("RGBA")
    alpha_bounds = image.getchannel("A").getbbox()
    if stored_mode != "RGBA":
        raise RuntimeError(f"Runtime sprite must be RGBA: {path}")
    if image.size != RUNTIME_SIZE:
        raise RuntimeError(f"Unexpected runtime sprite size: {path} {image.size}")
    if alpha_bounds != expected_alpha_bounds:
        raise RuntimeError(
            f"Unexpected alpha bounds for {path}: "
            f"{alpha_bounds} != {expected_alpha_bounds}"
        )
    corners = [
        image.getpixel((0, 0))[3],
        image.getpixel((image.width - 1, 0))[3],
        image.getpixel((0, image.height - 1))[3],
        image.getpixel((image.width - 1, image.height - 1))[3],
    ]
    if any(corners):
        raise RuntimeError(f"Runtime sprite has opaque corners: {path}")
    return {
        "stored_mode": stored_mode,
        "size_px": list(image.size),
        "alpha_bounds_px": list(alpha_bounds),
        "corner_alpha": corners,
    }


def _save_runtime(image: Image.Image, filename: str) -> Path:
    output_path = OUTPUT_ROOT / filename
    image.crop(COMMON_CROP).save(
        output_path,
        format="PNG",
        optimize=True,
        compress_level=9,
    )
    return output_path


def main() -> None:
    neutral = _load_verified(NEUTRAL_SOURCE)
    generated_blink = _load_verified(BLINK_SOURCE)
    registered_blink, blink_mask = _build_registered_blink(
        neutral,
        generated_blink,
    )
    foreground_hands, hand_mask = _build_foreground_hands(neutral)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    neutral_path = _save_runtime(neutral, NEUTRAL_OUTPUT)
    blink_path = _save_runtime(registered_blink, BLINK_OUTPUT)
    hands_path = _save_runtime(foreground_hands, HANDS_OUTPUT)

    blink_difference = ImageChops.difference(
        neutral.convert("RGB"),
        registered_blink.convert("RGB"),
    )
    difference_bounds = blink_difference.getbbox()
    if difference_bounds is None:
        raise RuntimeError("Registered blink is identical to neutral")
    if not (
        difference_bounds[0] >= 360
        and difference_bounds[1] >= 495
        and difference_bounds[2] <= 885
        and difference_bounds[3] <= 740
    ):
        raise RuntimeError(
            f"Blink changed pixels outside the face gate: {difference_bounds}"
        )

    hand_bounds = hand_mask.getbbox()
    if hand_bounds is None:
        raise RuntimeError("Foreground hand layer is empty")

    assets = [
        {
            "asset_id": "character.bentosaur_proprietor.counter.neutral",
            "output": neutral_path.relative_to(REPO_ROOT).as_posix(),
            "output_sha256": _sha256(neutral_path),
            "decoded_rgba_sha256": _decoded_rgba_sha256(neutral_path),
            "qa": _qa_image(neutral_path, (0, 0, 865, 1024)),
        },
        {
            "asset_id": "character.bentosaur_proprietor.counter.blink",
            "output": blink_path.relative_to(REPO_ROOT).as_posix(),
            "output_sha256": _sha256(blink_path),
            "decoded_rgba_sha256": _decoded_rgba_sha256(blink_path),
            "qa": _qa_image(blink_path, (0, 0, 865, 1024)),
        },
        {
            "asset_id": "character.bentosaur_proprietor.counter.hands",
            "output": hands_path.relative_to(REPO_ROOT).as_posix(),
            "output_sha256": _sha256(hands_path),
            "decoded_rgba_sha256": _decoded_rgba_sha256(hands_path),
            "qa": _qa_image(
                hands_path,
                (
                    hand_bounds[0] - COMMON_CROP[0],
                    hand_bounds[1] - COMMON_CROP[1],
                    hand_bounds[2] - COMMON_CROP[0],
                    hand_bounds[3] - COMMON_CROP[1],
                ),
            ),
        },
    ]
    manifest = {
        "schema_version": 1,
        "asset_id": "character.bentosaur_proprietor.runtime.v002",
        "status": "founder_visual_approval_pending",
        "approval_boundary": (
            "pose and runtime layering candidate; founder owns visual approval"
        ),
        "builder": "tools/art/promote_bentosaur_proprietor_counter_v002.py",
        "builder_runtime": {
            "pillow_version": PILLOW_VERSION,
            "integrity_contract": (
                "decoded_rgba_sha256 is cross-encoder authority; "
                "output_sha256 records the committed PNG bytes"
            ),
        },
        "source_candidate": CANDIDATE_ROOT.relative_to(REPO_ROOT).as_posix(),
        "source_assets": [
            {
                "path": NEUTRAL_SOURCE.relative_to(REPO_ROOT).as_posix(),
                "sha256": EXPECTED_SOURCE_HASHES[NEUTRAL_SOURCE.name],
                "role": "immutable registration and appearance authority",
            },
            {
                "path": BLINK_SOURCE.relative_to(REPO_ROOT).as_posix(),
                "sha256": EXPECTED_SOURCE_HASHES[BLINK_SOURCE.name],
                "role": "eye-patch pixels only",
            },
        ],
        "registration": {
            "source_canvas_px": list(SOURCE_SIZE),
            "common_crop_xyxy_px": list(COMMON_CROP),
            "runtime_size_px": list(RUNTIME_SIZE),
            "logical_scale": LOGICAL_SCALE,
            "sprite_center_from_counter_px": list(SPRITE_CENTER_FROM_COUNTER),
            "shared_origin": "counter_contact_bottom_center",
            "scene_root_position": [360.0, 699.0],
            "body_effective_z": 14,
            "stall_effective_z": 15,
            "foreground_hands_effective_z": 16,
        },
        "separation": {
            "blink_patch_ellipses_source_px": [
                list(ellipse) for ellipse in EYE_PATCH_ELLIPSES
            ],
            "blink_patch_feather_px": EYE_PATCH_FEATHER_PX,
            "blink_difference_bounds_source_px": list(difference_bounds),
            "foreground_left_polygon_source_px": [
                list(point) for point in LEFT_FOREGROUND_ARM
            ],
            "foreground_right_polygon_source_px": [
                list(point) for point in RIGHT_FOREGROUND_ARM
            ],
        },
        "assets": assets,
        "asset_count": len(assets),
    }
    manifest_path = OUTPUT_ROOT / "runtime_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Promoted Bentosaur hands-on-counter runtime kit")
    for asset in assets:
        print(f"- {asset['output']}")
    print(f"- {manifest_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
