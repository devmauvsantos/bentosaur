#!/usr/bin/env python3
"""Promote the registered V3 Bentosaur proprietor proof into Godot.

The visual-exploration sources remain immutable. Neutral and blink use one
common crop so a runtime texture swap cannot change registration. This is a
first-playable whole-sprite proof, not the final separated face/arm layer kit.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PACK = REPO_ROOT / "art/concepts/2d-chibi/v3"
SOURCE_MANIFEST = SOURCE_PACK / "manifest.json"
SOURCE_DIR = SOURCE_PACK / "02_main-character-idle/registered"
OUTPUT_ROOT = (
    REPO_ROOT / "game/assets/characters/bentosaur_proprietor/v001"
)

SOURCE_CANVAS = (512, 576)
COMMON_CROP = (69, 62, 443, 552)
LOGICAL_SCALE = 0.52
BASELINE_FROM_CROP_CENTER = (0.0, -269.0)

ASSETS = (
    {
        "asset_id": "character.bentosaur_proprietor.neutral",
        "source": "bentosaur-neutral-open-registered-v1.png",
        "output": "bentosaur_proprietor_neutral_v001.png",
    },
    {
        "asset_id": "character.bentosaur_proprietor.blink",
        "source": "bentosaur-blink-registered-v1.png",
        "output": "bentosaur_proprietor_blink_v001.png",
    },
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_hashes() -> dict[str, str]:
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    return {
        item["path"]: item["sha256"]
        for item in manifest["outputs"]
        if isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and isinstance(item.get("sha256"), str)
    }


def _qa_image(path: Path) -> dict[str, Any]:
    with Image.open(path) as loaded:
        stored_mode = loaded.mode
        image = loaded.convert("RGBA")
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if stored_mode != "RGBA":
        raise RuntimeError(f"Runtime sprite must be RGBA: {path}")
    if image.size != (374, 490):
        raise RuntimeError(f"Unexpected runtime sprite size: {path} {image.size}")
    if bounds is None:
        raise RuntimeError(f"Runtime sprite is fully transparent: {path}")
    corner_alpha = [
        image.getpixel((0, 0))[3],
        image.getpixel((image.width - 1, 0))[3],
        image.getpixel((0, image.height - 1))[3],
        image.getpixel((image.width - 1, image.height - 1))[3],
    ]
    if any(corner_alpha):
        raise RuntimeError(f"Runtime sprite has opaque corners: {path}")
    return {
        "stored_mode": stored_mode,
        "size_px": list(image.size),
        "alpha_bounds_px": list(bounds),
        "corner_alpha": corner_alpha,
    }


def main() -> None:
    hashes = _source_hashes()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    built: list[dict[str, Any]] = []

    for spec in ASSETS:
        source_path = SOURCE_DIR / spec["source"]
        source_relative = source_path.relative_to(SOURCE_PACK).as_posix()
        expected_hash = hashes.get(source_relative)
        if expected_hash is None:
            raise RuntimeError(f"Source is absent from V3 manifest: {source_relative}")
        actual_hash = _sha256(source_path)
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"Source hash mismatch for {source_relative}: "
                f"{actual_hash} != {expected_hash}"
            )

        with Image.open(source_path) as loaded:
            source = loaded.convert("RGBA")
        if source.size != SOURCE_CANVAS:
            raise RuntimeError(
                f"Unexpected registered source canvas: {source_path} {source.size}"
            )
        output = source.crop(COMMON_CROP)
        output_path = OUTPUT_ROOT / spec["output"]
        output.save(output_path, format="PNG", optimize=True, compress_level=9)

        built.append(
            {
                "asset_id": spec["asset_id"],
                "source": source_path.relative_to(REPO_ROOT).as_posix(),
                "source_sha256": actual_hash,
                "output": output_path.relative_to(REPO_ROOT).as_posix(),
                "output_sha256": _sha256(output_path),
                "operation": "lossless_common_crop",
                "qa": _qa_image(output_path),
            }
        )

    manifest = {
        "schema_version": 1,
        "asset_id": "character.bentosaur_proprietor.runtime.v001",
        "status": "first_playable_whole_sprite_proof",
        "approval_boundary": (
            "identity-approved source states; shipping separated layer rig pending"
        ),
        "source_pack": SOURCE_PACK.relative_to(REPO_ROOT).as_posix(),
        "source_manifest_sha256": _sha256(SOURCE_MANIFEST),
        "registration": {
            "source_canvas_px": list(SOURCE_CANVAS),
            "common_crop_xyxy_px": list(COMMON_CROP),
            "runtime_size_px": [374, 490],
            "logical_scale": LOGICAL_SCALE,
            "sprite_center_from_baseline_px": list(BASELINE_FROM_CROP_CENTER),
            "shared_origin": "bottom_center",
        },
        "motion_contract": {
            "breath_period_seconds": 3.4,
            "breath_vertical_expansion": 0.005,
            "breath_horizontal_contraction": 0.0025,
            "breath_speed_range": [0.94, 1.06],
            "randomized_start_phase": True,
            "blink_seconds": 0.18,
            "blink_interval_seconds": [2.3, 5.4],
            "double_blink_chance": 0.12,
            "double_blink_gap_seconds": 0.14,
        },
        "asset_count": len(built),
        "assets": built,
        "builder": "tools/art/promote_bentosaur_proprietor_v001.py",
    }
    manifest_path = OUTPUT_ROOT / "runtime_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Promoted {len(built)} Bentosaur proprietor proof sprites")
    print(f"- {manifest_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
