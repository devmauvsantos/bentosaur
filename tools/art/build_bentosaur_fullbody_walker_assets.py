#!/usr/bin/env python3
"""Build the v001 side-view Bentosaur cutout puppet kit.

The source sheet was generated as one deliberately separated paper-doll sheet.
This builder removes guesswork from runtime imports: each region is cropped,
trimmed with consistent transparent padding, hashed, and described in a
manifest.  It never modifies the source artwork.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "art/characters/bentosaur-walker/char-v001/source"
SOURCE_SHEET = SOURCE_ROOT / "bentosaur_walker_side_puppet_sheet_transparent_v001.png"
SOURCE_MASTER = SOURCE_ROOT / "bentosaur_walker_side_master_transparent_v001.png"
OUTPUT_ROOT = REPO_ROOT / "game/assets/characters/bentosaur_walker/v001"

PADDING = 8

# Non-overlapping authored regions in the 1024 x 1536 source sheet.
REGIONS: dict[str, tuple[int, int, int, int]] = {
    "head": (20, 20, 620, 650),
    "torso": (620, 190, 950, 700),
    "upper_arm_shared": (20, 620, 270, 960),
    "lower_arm_far": (250, 620, 465, 960),
    "lower_arm_near": (450, 650, 650, 950),
    "thigh_far": (40, 920, 315, 1195),
    "thigh_near": (310, 920, 560, 1185),
    "lower_leg_far": (50, 1180, 320, 1480),
    "lower_leg_near": (310, 1180, 570, 1480),
    "tail_base": (620, 820, 1010, 1100),
    "tail_mid": (620, 1070, 990, 1270),
    "tail_tip": (620, 1270, 920, 1470),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def trim_region(source: Image.Image, region: tuple[int, int, int, int]) -> tuple[Image.Image, tuple[int, int, int, int]]:
    crop = source.crop(region)
    alpha_bounds = crop.getchannel("A").getbbox()
    if alpha_bounds is None:
        raise ValueError(f"Region {region} has no visible pixels")

    absolute_bounds = (
        region[0] + alpha_bounds[0],
        region[1] + alpha_bounds[1],
        region[0] + alpha_bounds[2],
        region[1] + alpha_bounds[3],
    )
    visible = source.crop(absolute_bounds)
    padded = Image.new(
        "RGBA",
        (visible.width + PADDING * 2, visible.height + PADDING * 2),
        (0, 0, 0, 0),
    )
    padded.alpha_composite(visible, (PADDING, PADDING))
    return padded, absolute_bounds


def build_contact_sheet(parts: dict[str, Image.Image], output: Path) -> None:
    thumb_size = (220, 220)
    cell_size = (246, 274)
    columns = 4
    rows = (len(parts) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * cell_size[0], rows * cell_size[1]), (24, 31, 39, 255))
    draw = ImageDraw.Draw(sheet)

    for index, (name, image) in enumerate(parts.items()):
        preview = image.copy()
        preview.thumbnail(thumb_size, Image.Resampling.LANCZOS)
        x = (index % columns) * cell_size[0]
        y = (index // columns) * cell_size[1]
        checker = Image.new("RGBA", thumb_size, (39, 49, 57, 255))
        checker.alpha_composite(
            preview,
            ((thumb_size[0] - preview.width) // 2, (thumb_size[1] - preview.height) // 2),
        )
        sheet.alpha_composite(checker, (x + 13, y + 10))
        draw.text((x + 13, y + 238), name.replace("_", " "), fill=(234, 222, 194, 255))

    sheet.save(output, optimize=True)


def main() -> None:
    if not SOURCE_SHEET.exists() or not SOURCE_MASTER.exists():
        raise FileNotFoundError("The v001 walker source master and puppet sheet are required")

    source = Image.open(SOURCE_SHEET).convert("RGBA")
    if source.size != (1024, 1536):
        raise ValueError(f"Unexpected source sheet size: {source.size}")
    if source.getpixel((0, 0))[3] != 0:
        raise ValueError("Source sheet corner must be transparent")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    parts: dict[str, Image.Image] = {}
    manifest_parts: dict[str, dict[str, object]] = {}

    for name, region in REGIONS.items():
        part, bounds = trim_region(source, region)
        output = OUTPUT_ROOT / f"walker_{name}_v001.png"
        part.save(output, optimize=True)
        parts[name] = part
        manifest_parts[name] = {
            "file": output.name,
            "source_bounds": list(bounds),
            "size": list(part.size),
            "sha256": sha256(output),
        }

    contact_sheet = OUTPUT_ROOT / "walker_parts_contact_sheet_v001.png"
    build_contact_sheet(parts, contact_sheet)

    manifest = {
        "schema_version": 1,
        "character": "bentosaur_walker",
        "version": "v001",
        "view": "side_facing_screen_right",
        "purpose": "native Godot Skeleton2D full-body locomotion feasibility gate",
        "source_master": {
            "path": str(SOURCE_MASTER.relative_to(REPO_ROOT)),
            "sha256": sha256(SOURCE_MASTER),
        },
        "source_sheet": {
            "path": str(SOURCE_SHEET.relative_to(REPO_ROOT)),
            "size": list(source.size),
            "sha256": sha256(SOURCE_SHEET),
        },
        "padding_px": PADDING,
        "parts": manifest_parts,
        "known_compromises": [
            "The far upper arm reuses the shared upper-arm art in this feasibility rig.",
            "Joint rings are intentionally hidden by draw order and overlap; production art should remove interior seam outlines.",
            "One side-view rig supports horizontal mirroring only, not front/back walking.",
        ],
    }
    manifest_path = OUTPUT_ROOT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Built {len(parts)} walker parts in {OUTPUT_ROOT}")
    for name, data in manifest_parts.items():
        print(f"- {name}: {data['size']} from {data['source_bounds']}")
    print(f"- manifest.json: {sha256(manifest_path)}")


if __name__ == "__main__":
    main()
