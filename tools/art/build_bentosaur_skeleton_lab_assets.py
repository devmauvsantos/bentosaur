#!/usr/bin/env python3
"""Build registered 2D cutout layers for the Bentosaur skeleton lab.

The approved v002 proprietor sprites remain the visual authority.  Every
generated layer keeps the complete 865 x 1024 runtime canvas, so Godot can
stack the files at one shared origin without hand-maintained offsets.

This is deliberately a *lab* decomposition rather than final production art:
the source illustration was painted as one flattened character.  A small
under-neck backing is reconstructed from the upper torso so gentle head
rotation does not reveal the background.  Final production art should replace
that backing with an authored hidden-neck layer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import (
    Image,
    ImageChops,
    ImageDraw,
    ImageFilter,
    __version__ as PILLOW_VERSION,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "game/assets/characters/bentosaur_proprietor/v002"
OUTPUT_ROOT = (
    REPO_ROOT
    / "game/assets/characters/bentosaur_proprietor/skeleton_lab_v001"
)

CANVAS_SIZE = (865, 1024)
CANVAS_CENTER = (432.5, 512.0)

NEUTRAL_SOURCE = SOURCE_ROOT / "bentosaur_proprietor_counter_neutral_v002.png"
BLINK_SOURCE = SOURCE_ROOT / "bentosaur_proprietor_counter_blink_v002.png"
HANDS_SOURCE = SOURCE_ROOT / "bentosaur_proprietor_counter_hands_v002.png"
EXPECTED_SOURCE_HASHES = {
    NEUTRAL_SOURCE.name: (
        "a4cde397f77b3caab3c818dc9834803cd7537b13b9375f984af13ef6a5e2ed9a"
    ),
    BLINK_SOURCE.name: (
        "9a78c052cf3f026040eb840f5d0ab0fa0d809a3a06511c7d80ddc820420b4aa4"
    ),
    HANDS_SOURCE.name: (
        "e0bb42f189297414e01af5d44ec4d2cdebd18a09bc04c6110a5c3aa9c7b27a4d"
    ),
}

OUTPUT_NAMES = {
    "full_reference": "proprietor_full_reference_neutral_v001.png",
    "head_neutral": "proprietor_head_neutral_v001.png",
    "head_blink": "proprietor_head_blink_v001.png",
    "torso": "proprietor_torso_central_v001.png",
    "arm_left": "proprietor_arm_hand_screen_left_v001.png",
    "arm_right": "proprietor_arm_hand_screen_right_v001.png",
    "preview": "proprietor_rig_rest_preview_v001.png",
}
EXPECTED_ALPHA_BOUNDS = {
    OUTPUT_NAMES["full_reference"]: (0, 0, 865, 1024),
    OUTPUT_NAMES["head_neutral"]: (0, 0, 865, 751),
    OUTPUT_NAMES["head_blink"]: (0, 0, 865, 751),
    OUTPUT_NAMES["torso"]: (136, 674, 736, 986),
    OUTPUT_NAMES["arm_left"]: (82, 778, 370, 1024),
    OUTPUT_NAMES["arm_right"]: (502, 778, 787, 1024),
    OUTPUT_NAMES["preview"]: (0, 0, 865, 1024),
}

# The boundary follows the painted lower silhouette of the head.  It retains a
# little green below the chin so a +/- 3 degree lab rotation has no hard seam.
HEAD_MASK_POLYGON = (
    (0, 0),
    (865, 0),
    (865, 610),
    (780, 646),
    (700, 682),
    (650, 700),
    (610, 716),
    (545, 736),
    (500, 743),
    (432, 748),
    (365, 743),
    (320, 736),
    (255, 716),
    (215, 700),
    (165, 682),
    (85, 646),
    (0, 610),
)
HEAD_MASK_FEATHER_PX = 0.75

# The hands source already contains only the foreground arms/hands.  Its two
# components are disconnected, so a center split is lossless.
SCREEN_SPLIT_X = 432

# The flattened source contains no art behind the chin.  Build a narrow hidden
# neck/upper-torso backing by vertically stretching an existing painted torso
# strip, then reveal it only through this feathered mask.  At rest it sits
# behind the head and is effectively invisible.
NECK_SAMPLE_BOX = (190, 754, 675, 834)
NECK_UNDERLAY_BOX = (190, 674, 675, 806)
NECK_UNDERLAY_ELLIPSE = (205, 674, 660, 836)
NECK_UNDERLAY_FEATHER_PX = 10.0

PIVOTS_PX = {
    "head_neck": [432, 704],
    "torso": [432, 790],
    "arm_hand_screen_left": [220, 790],
    "arm_hand_screen_right": [645, 790],
}


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
    actual_hash = _sha256(path)
    expected_hash = EXPECTED_SOURCE_HASHES[path.name]
    if actual_hash != expected_hash:
        raise RuntimeError(
            f"Source hash mismatch for {path}: {actual_hash} != {expected_hash}"
        )
    with Image.open(path) as loaded:
        image = loaded.convert("RGBA")
    if image.size != CANVAS_SIZE:
        raise RuntimeError(f"Unexpected source size for {path}: {image.size}")
    return image


def _polygon_mask(
    points: tuple[tuple[int, int], ...],
    feather_px: float = 0.0,
) -> Image.Image:
    mask = Image.new("L", CANVAS_SIZE, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    if feather_px > 0.0:
        mask = mask.filter(ImageFilter.GaussianBlur(feather_px))
    return mask


def _mask_rgba(source: Image.Image, spatial_mask: Image.Image) -> Image.Image:
    layer = source.copy()
    layer.putalpha(ImageChops.multiply(source.getchannel("A"), spatial_mask))
    return layer


def _split_foreground_arms(hands: Image.Image) -> tuple[Image.Image, Image.Image]:
    left_mask = Image.new("L", CANVAS_SIZE, 0)
    right_mask = Image.new("L", CANVAS_SIZE, 0)
    left_draw = ImageDraw.Draw(left_mask)
    right_draw = ImageDraw.Draw(right_mask)
    left_draw.rectangle((0, 0, SCREEN_SPLIT_X, CANVAS_SIZE[1]), fill=255)
    right_draw.rectangle(
        (SCREEN_SPLIT_X + 1, 0, CANVAS_SIZE[0], CANVAS_SIZE[1]),
        fill=255,
    )
    return _mask_rgba(hands, left_mask), _mask_rgba(hands, right_mask)


def _build_neck_underlay(neutral: Image.Image) -> Image.Image:
    sample = neutral.crop(NECK_SAMPLE_BOX)
    target_size = (
        NECK_UNDERLAY_BOX[2] - NECK_UNDERLAY_BOX[0],
        NECK_UNDERLAY_BOX[3] - NECK_UNDERLAY_BOX[1],
    )
    sample = sample.resize(target_size, Image.Resampling.BICUBIC)

    underlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    underlay.alpha_composite(sample, (NECK_UNDERLAY_BOX[0], NECK_UNDERLAY_BOX[1]))

    reveal = Image.new("L", CANVAS_SIZE, 0)
    ImageDraw.Draw(reveal).ellipse(NECK_UNDERLAY_ELLIPSE, fill=255)
    reveal = reveal.filter(ImageFilter.GaussianBlur(NECK_UNDERLAY_FEATHER_PX))
    underlay_alpha = ImageChops.multiply(underlay.getchannel("A"), reveal)
    # Never extend the rest-pose silhouette.  The backing only fills hidden
    # pixels already occupied by the flattened character at registration.
    underlay.putalpha(
        ImageChops.multiply(underlay_alpha, neutral.getchannel("A"))
    )
    return underlay


def _build_torso(
    neutral: Image.Image,
    head_mask: Image.Image,
    arm_left: Image.Image,
    arm_right: Image.Image,
) -> Image.Image:
    source_alpha = neutral.getchannel("A")
    assigned_alpha = ImageChops.lighter(
        ImageChops.multiply(source_alpha, head_mask),
        ImageChops.lighter(
            arm_left.getchannel("A"),
            arm_right.getchannel("A"),
        ),
    )
    residual_alpha = ImageChops.subtract(source_alpha, assigned_alpha)
    torso = neutral.copy()
    torso.putalpha(residual_alpha)

    # Add the provisional hidden neck behind the residual body.  Because the
    # source body remains on top, this can only affect pixels uncovered by head
    # motion in the lab.
    neck_underlay = _build_neck_underlay(neutral)
    neck_underlay.alpha_composite(torso)
    return neck_underlay


def _save_png(image: Image.Image, filename: str) -> Path:
    path = OUTPUT_ROOT / filename
    image.save(path, format="PNG", optimize=True, compress_level=9)
    return path


def _qa_asset(path: Path) -> dict[str, Any]:
    with Image.open(path) as loaded:
        stored_mode = loaded.mode
        image = loaded.convert("RGBA")
    if stored_mode != "RGBA":
        raise RuntimeError(f"Asset must be stored as RGBA: {path}")
    if image.size != CANVAS_SIZE:
        raise RuntimeError(f"Asset registration changed: {path} {image.size}")
    alpha_bounds = image.getchannel("A").getbbox()
    if alpha_bounds is None:
        raise RuntimeError(f"Asset is empty: {path}")
    expected_alpha_bounds = EXPECTED_ALPHA_BOUNDS[path.name]
    if alpha_bounds != expected_alpha_bounds:
        raise RuntimeError(
            f"Unexpected alpha bounds for {path}: "
            f"{alpha_bounds} != {expected_alpha_bounds}"
        )
    corner_alpha = [
        image.getpixel((0, 0))[3],
        image.getpixel((image.width - 1, 0))[3],
        image.getpixel((0, image.height - 1))[3],
        image.getpixel((image.width - 1, image.height - 1))[3],
    ]
    if any(corner_alpha):
        raise RuntimeError(f"Asset has opaque canvas corners: {path}")
    return {
        "stored_mode": stored_mode,
        "size_px": list(image.size),
        "alpha_bounds_px": list(alpha_bounds),
        "corner_alpha": corner_alpha,
    }


def _asset_record(
    asset_id: str,
    role: str,
    path: Path,
    pivot_key: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "asset_id": asset_id,
        "role": role,
        "output": path.relative_to(REPO_ROOT).as_posix(),
        "output_sha256": _sha256(path),
        "decoded_rgba_sha256": _decoded_rgba_sha256(path),
        "qa": _qa_asset(path),
    }
    if pivot_key is not None:
        record["pivot_px"] = PIVOTS_PX[pivot_key]
    return record


def main() -> None:
    neutral = _load_verified(NEUTRAL_SOURCE)
    blink = _load_verified(BLINK_SOURCE)
    hands = _load_verified(HANDS_SOURCE)

    head_mask = _polygon_mask(HEAD_MASK_POLYGON, HEAD_MASK_FEATHER_PX)
    head_neutral = _mask_rgba(neutral, head_mask)
    head_blink = _mask_rgba(blink, head_mask)
    arm_left, arm_right = _split_foreground_arms(hands)
    torso = _build_torso(neutral, head_mask, arm_left, arm_right)

    preview = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    preview.alpha_composite(torso)
    preview.alpha_composite(head_neutral)
    preview.alpha_composite(arm_left)
    preview.alpha_composite(arm_right)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    paths = {
        "full_reference": _save_png(neutral, OUTPUT_NAMES["full_reference"]),
        "head_neutral": _save_png(head_neutral, OUTPUT_NAMES["head_neutral"]),
        "head_blink": _save_png(head_blink, OUTPUT_NAMES["head_blink"]),
        "torso": _save_png(torso, OUTPUT_NAMES["torso"]),
        "arm_left": _save_png(arm_left, OUTPUT_NAMES["arm_left"]),
        "arm_right": _save_png(arm_right, OUTPUT_NAMES["arm_right"]),
        "preview": _save_png(preview, OUTPUT_NAMES["preview"]),
    }

    qa_background = Image.new("RGBA", CANVAS_SIZE, (119, 119, 119, 255))
    reference_flat = qa_background.copy()
    reference_flat.alpha_composite(neutral)
    preview_flat = qa_background.copy()
    preview_flat.alpha_composite(preview)
    reference_rgb = reference_flat.convert("RGB")
    preview_rgb = preview_flat.convert("RGB")
    difference = ImageChops.difference(reference_rgb, preview_rgb)
    difference_bounds = difference.getbbox()
    difference_mask = ImageChops.lighter(
        difference.getchannel("R"),
        ImageChops.lighter(
            difference.getchannel("G"),
            difference.getchannel("B"),
        ),
    )
    changed_visible_pixels = sum(difference_mask.histogram()[1:])
    expected_difference_gate = (180, 680, 680, 780)
    if difference_bounds is None:
        raise RuntimeError("Rig preview unexpectedly has no decomposition changes")
    if not (
        difference_bounds[0] >= expected_difference_gate[0]
        and difference_bounds[1] >= expected_difference_gate[1]
        and difference_bounds[2] <= expected_difference_gate[2]
        and difference_bounds[3] <= expected_difference_gate[3]
    ):
        raise RuntimeError(
            "Visible rest reconstruction differences escaped the neck gate: "
            f"{difference_bounds}"
        )
    if changed_visible_pixels > 2500:
        raise RuntimeError(
            "Visible rest reconstruction difference is too large: "
            f"{changed_visible_pixels} pixels"
        )

    assets = [
        _asset_record(
            "character.bentosaur_proprietor.skeleton_lab.full_reference",
            "immutable neutral visual reference",
            paths["full_reference"],
        ),
        _asset_record(
            "character.bentosaur_proprietor.skeleton_lab.head.neutral",
            "riggable head; neutral eyes",
            paths["head_neutral"],
            "head_neck",
        ),
        _asset_record(
            "character.bentosaur_proprietor.skeleton_lab.head.blink",
            "riggable head; registered blink swap",
            paths["head_blink"],
            "head_neck",
        ),
        _asset_record(
            "character.bentosaur_proprietor.skeleton_lab.torso",
            "central torso plus provisional hidden-neck backing",
            paths["torso"],
            "torso",
        ),
        _asset_record(
            "character.bentosaur_proprietor.skeleton_lab.arm_hand.screen_left",
            "screen-left foreground arm and hand",
            paths["arm_left"],
            "arm_hand_screen_left",
        ),
        _asset_record(
            "character.bentosaur_proprietor.skeleton_lab.arm_hand.screen_right",
            "screen-right foreground arm and hand",
            paths["arm_right"],
            "arm_hand_screen_right",
        ),
        _asset_record(
            "character.bentosaur_proprietor.skeleton_lab.preview.rest",
            "QA composite of the generated layers at rest",
            paths["preview"],
        ),
    ]

    manifest = {
        "schema_version": 1,
        "asset_id": "character.bentosaur_proprietor.skeleton_lab.v001",
        "status": "prototype_not_visual_approval",
        "builder": "tools/art/build_bentosaur_skeleton_lab_assets.py",
        "builder_runtime": {
            "pillow_version": PILLOW_VERSION,
            "integrity_contract": (
                "decoded_rgba_sha256 is the cross-encoder authority; "
                "output_sha256 records exact PNG bytes"
            ),
        },
        "registration": {
            "canvas_size_px": list(CANVAS_SIZE),
            "canvas_center_px": list(CANVAS_CENTER),
            "coordinate_convention": (
                "screen-left/screen-right; origin at full-canvas top-left"
            ),
            "shared_origin": "all layers retain full v002 canvas registration",
            "pivots_px": PIVOTS_PX,
        },
        "source_assets": [
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "sha256": EXPECTED_SOURCE_HASHES[path.name],
                "role": role,
            }
            for path, role in (
                (NEUTRAL_SOURCE, "neutral appearance and registration authority"),
                (BLINK_SOURCE, "registered blink appearance authority"),
                (HANDS_SOURCE, "foreground arm/hand separation authority"),
            )
        ],
        "separation": {
            "head_mask_polygon_px": [list(point) for point in HEAD_MASK_POLYGON],
            "head_mask_feather_px": HEAD_MASK_FEATHER_PX,
            "screen_arm_split_x_px": SCREEN_SPLIT_X,
            "neck_sample_box_xyxy_px": list(NECK_SAMPLE_BOX),
            "neck_underlay_box_xyxy_px": list(NECK_UNDERLAY_BOX),
            "neck_underlay_ellipse_xyxy_px": list(NECK_UNDERLAY_ELLIPSE),
            "neck_underlay_feather_px": NECK_UNDERLAY_FEATHER_PX,
        },
        "known_compromises": [
            (
                "The flattened source has no painted geometry behind the head; "
                "the torso contains a resampled provisional under-neck backing."
            ),
            (
                "Arm layers retain generous shoulder overlap from the v002 "
                "foreground-hands mask; keep rotation subtle to avoid exposing "
                "the original flattened shoulder contour."
            ),
            (
                "No mouth overlay was emitted: the neutral mouth is baked into "
                "the head, and a safe expression swap requires an authored "
                "mouthless face plate rather than destructive inpainting."
            ),
            (
                "This lab validates cutout motion and blink swaps only; it is "
                "not founder-approved final animation production art."
            ),
        ],
        "rest_reconstruction_qa": {
            "difference_bounds_px": (
                list(difference_bounds) if difference_bounds is not None else None
            ),
            "expected_difference_gate_px": list(expected_difference_gate),
            "changed_visible_pixels": changed_visible_pixels,
            "total_canvas_pixels": CANVAS_SIZE[0] * CANVAS_SIZE[1],
            "note": (
                "Differences are expected only where the provisional hidden "
                "neck overlaps antialiased cut boundaries."
            ),
        },
        "asset_count": len(assets),
        "assets": assets,
    }
    manifest_path = OUTPUT_ROOT / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Built {len(assets)} registered skeleton-lab assets in {OUTPUT_ROOT}")
    for record in assets:
        qa = record["qa"]
        print(
            f"- {Path(record['output']).name}: "
            f"{qa['size_px']} alpha={qa['alpha_bounds_px']}"
        )
    print(f"- manifest.json: {_sha256(manifest_path)}")


if __name__ == "__main__":
    main()
