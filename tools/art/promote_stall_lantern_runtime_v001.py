#!/usr/bin/env python3
"""Promote the founder-approved stall lantern into trimmed Godot assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (
    REPO_ROOT
    / "art/source-assets/home-menu/stall/v003-lantern-lighting/components"
)
OUTPUT_ROOT = (
    REPO_ROOT
    / "game/assets/environments/home_village/v001/stall/attachments/v001/lantern"
)
HALO_REGISTERED_SOURCE = (
    REPO_ROOT
    / "art/source-assets/home-menu/stall/v003-lantern-lighting/registered/"
    "stall_lantern_halos_add_registered_candidate_v001.png"
)

SOURCE_ASSETS = {
    "stall_lantern_anchor_v001.png": SOURCE_ROOT
    / "stall_lantern_anchor_candidate_v001.png",
    "stall_lantern_body_off_v001.png": SOURCE_ROOT
    / "stall_lantern_body_off_candidate_v001.png",
    "stall_lantern_core_add_v001.png": SOURCE_ROOT
    / "stall_lantern_core_candidate_v001.png",
}

BODY_WIDTH = 75
CORE_TOP_LEFT_IN_BODY = (9, 54)
BODY_PIVOT_LOCAL = (37.5, 12.0)
BODY_TOP_LEFT_FROM_PIVOT = (-37.5, -12.0)
ANCHOR_LOCAL_TOP_LEFT = (-21.5, -45.0)
CORE_TOP_LEFT_FROM_PIVOT = (-28.5, 42.0)
HALO_SOURCE_RECT = (30, 404, 208, 224)
HALO_TOP_LEFT_FROM_PIVOT = (-104.5, -33.0)
HALO_CENTER_FROM_PIVOT = (-0.5, 79.0)
FIXTURE_PIVOTS = ((134.5, 437.0), (583.5, 437.0))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)


def _resize(image: Image.Image, scale: float) -> Image.Image:
    return image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )


def main() -> None:
    for path in (*SOURCE_ASSETS.values(), HALO_REGISTERED_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)

    body_source = Image.open(SOURCE_ASSETS["stall_lantern_body_off_v001.png"]).convert(
        "RGBA"
    )
    runtime_scale = BODY_WIDTH / body_source.width

    built: list[dict[str, object]] = []
    for output_name, source_path in SOURCE_ASSETS.items():
        source = Image.open(source_path).convert("RGBA")
        runtime = _resize(source, runtime_scale)
        output_path = OUTPUT_ROOT / output_name
        _save(runtime, output_path)
        built.append(
            {
                "output": output_path.relative_to(REPO_ROOT).as_posix(),
                "output_sha256": _sha256(output_path),
                "output_size_px": list(runtime.size),
                "source": source_path.relative_to(REPO_ROOT).as_posix(),
                "source_sha256": _sha256(source_path),
            }
        )

    halo_path = OUTPUT_ROOT / "stall_lantern_halo_add_v001.png"
    halo_registered = Image.open(HALO_REGISTERED_SOURCE).convert("RGBA")
    halo_x, halo_y, halo_width, halo_height = HALO_SOURCE_RECT
    halo = halo_registered.crop(
        (halo_x, halo_y, halo_x + halo_width, halo_y + halo_height)
    )
    _save(halo, halo_path)
    built.append(
        {
            "output": halo_path.relative_to(REPO_ROOT).as_posix(),
            "output_sha256": _sha256(halo_path),
            "output_size_px": list(halo.size),
            "source": HALO_REGISTERED_SOURCE.relative_to(REPO_ROOT).as_posix(),
            "source_sha256": _sha256(HALO_REGISTERED_SOURCE),
            "source_rect_px_720": list(HALO_SOURCE_RECT),
        }
    )

    manifest = {
        "asset_id": "env.home_village.stall.lantern.runtime.v001",
        "status": "founder_approved",
        "approval": {
            "gate": "G02_STALL_LIGHTING",
            "decided_at": "2026-07-31T16:24:27-04:00",
            "evidence": (
                "art/source-assets/home-menu/stall/v003-lantern-lighting/reviews/"
                "stall-lantern-off-on-approval-board-v001.png"
            ),
        },
        "coordinate_contract": {
            "canvas_px": [720, 1280],
            "stage_path": "StallStage",
            "stage_scale": 0.86,
            "stage_pivot_px": [360, 634],
            "fixture_pivots_px": [list(position) for position in FIXTURE_PIVOTS],
        },
        "assembly": {
            "body_pivot_local_px": list(BODY_PIVOT_LOCAL),
            "body_top_left_from_pivot_px": list(BODY_TOP_LEFT_FROM_PIVOT),
            "anchor_top_left_from_pivot_px": list(ANCHOR_LOCAL_TOP_LEFT),
            "core_top_left_in_body_px": list(CORE_TOP_LEFT_IN_BODY),
            "core_top_left_from_pivot_px": list(CORE_TOP_LEFT_FROM_PIVOT),
            "halo_top_left_from_pivot_px": list(HALO_TOP_LEFT_FROM_PIVOT),
            "halo_center_from_pivot_px": list(HALO_CENTER_FROM_PIVOT),
            "off": ["anchor", "body_off"],
            "on": ["anchor", "body_off", "core_add", "halo_add"],
            "geometry_changes_on_toggle": False,
        },
        "motion": {
            "anchor": "fixed",
            "body_core_halo": "shared restrained sway pivot",
            "maximum_sway_degrees": 1.4,
            "power_toggle_preserves_sway_phase": True,
        },
        "deferred": [
            "registered warm spill across stall wood",
            "stall-specific wet reflection masks",
        ],
        "assets": built,
        "builder": "tools/art/promote_stall_lantern_runtime_v001.py",
    }
    manifest_path = OUTPUT_ROOT / "runtime_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path.relative_to(REPO_ROOT))
    for item in built:
        print(item["output"], item["output_size_px"])


if __name__ == "__main__":
    main()
