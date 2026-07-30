"""Analyze and visualize normalized front-depth samples from inspect_sources."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RAW = json.loads((ROOT / "source_probe_raw.json").read_text())
closed = np.load(ROOT / "closed_front_depth.npz")["depth"]
opened = np.load(ROOT / "open_front_depth.npz")["depth"]
valid = np.isfinite(closed) & np.isfinite(opened)
difference = closed - opened
height, width = closed.shape
y_values = np.linspace(0.0, 1.0, width)
z_values = np.linspace(1.0, 0.0, height)


REGIONS = {
    "mouth": (0.30, 0.70, 0.42, 0.59),
    "eye_character_left": (0.52, 0.77, 0.55, 0.70),
    "eye_character_right": (0.23, 0.48, 0.55, 0.70),
    "full_face": (0.16, 0.84, 0.38, 0.76),
    "body_below_face": (0.05, 0.95, 0.02, 0.42),
}


def region_mask(bounds: tuple[float, float, float, float]) -> np.ndarray:
    y0, y1, z0, z1 = bounds
    return (
        valid
        & (y_values[None, :] >= y0)
        & (y_values[None, :] <= y1)
        & (z_values[:, None] >= z0)
        & (z_values[:, None] <= z1)
    )


def percentiles(values: np.ndarray) -> dict[str, float]:
    return {
        f"p{percentile:02d}": float(np.percentile(values, percentile))
        for percentile in (1, 5, 25, 50, 75, 90, 95, 99)
    }


def normalized_box(mask: np.ndarray) -> dict[str, list[float]] | None:
    rows, columns = np.where(mask)
    if not len(rows):
        return None
    return {
        "minimum_yz": [
            float(y_values[columns].min()),
            float(z_values[rows].min()),
        ],
        "maximum_yz": [
            float(y_values[columns].max()),
            float(z_values[rows].max()),
        ],
    }


def world_box_from_yz(
    source: dict[str, object], box: dict[str, list[float]]
) -> dict[str, list[float]]:
    minimum = np.array(source["bounds"]["minimum"], dtype=float)
    dimensions = np.array(source["bounds"]["dimensions"], dtype=float)
    ymin, zmin = box["minimum_yz"]
    ymax, zmax = box["maximum_yz"]
    return {
        "minimum_yz": [
            float(minimum[1] + ymin * dimensions[1]),
            float(minimum[2] + zmin * dimensions[2]),
        ],
        "maximum_yz": [
            float(minimum[1] + ymax * dimensions[1]),
            float(minimum[2] + zmax * dimensions[2]),
        ],
    }


def rgba_depth(depth: np.ndarray) -> Image.Image:
    # Keep a common facial-depth range so the two sources are comparable.
    value = np.clip((depth - 0.55) / 0.45, 0.0, 1.0)
    gray = np.uint8(value * 235.0 + 12.0)
    rgba = np.zeros((*depth.shape, 4), dtype=np.uint8)
    rgba[..., :3] = gray[..., None]
    rgba[..., 3] = np.where(np.isfinite(depth), 255, 0).astype(np.uint8)
    image = Image.fromarray(rgba, "RGBA")
    background = Image.new("RGBA", image.size, (25, 28, 33, 255))
    background.alpha_composite(image)
    return background.convert("RGB")


def rgba_difference(values: np.ndarray) -> Image.Image:
    limit = 0.08
    magnitude = np.clip(np.abs(values) / limit, 0.0, 1.0)
    rgba = np.zeros((*values.shape, 4), dtype=np.uint8)
    positive = values >= 0.0
    # Gold = open source is recessed relative to closed (mouth cavity).
    rgba[..., 0] = np.where(positive, 245, 55)
    rgba[..., 1] = np.where(positive, 151, 151)
    rgba[..., 2] = np.where(positive, 55, 245)
    rgba[..., 3] = np.where(valid, 40 + magnitude * 215, 0).astype(np.uint8)
    image = Image.fromarray(rgba, "RGBA")
    background = Image.new("RGBA", image.size, (25, 28, 33, 255))
    background.alpha_composite(image)
    return background.convert("RGB")


def to_pixel_box(bounds: tuple[float, float, float, float]) -> tuple[int, ...]:
    y0, y1, z0, z1 = bounds
    left = round(y0 * (width - 1))
    right = round(y1 * (width - 1))
    top = round((1.0 - z1) * (height - 1))
    bottom = round((1.0 - z0) * (height - 1))
    return left, top, right, bottom


def font(size: int) -> ImageFont.ImageFont:
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def labeled_panel(image: Image.Image, title: str) -> Image.Image:
    scale = 2
    panel = image.resize((width * scale, height * scale), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(panel)
    for name, bounds in REGIONS.items():
        if name not in ("mouth", "eye_character_left", "eye_character_right"):
            continue
        box = tuple(value * scale for value in to_pixel_box(bounds))
        color = (255, 210, 90) if name == "mouth" else (107, 215, 255)
        draw.rectangle(box, outline=color, width=3)
    title_height = 52
    result = Image.new(
        "RGB", (panel.width, panel.height + title_height), (25, 28, 33)
    )
    result.paste(panel, (0, title_height))
    ImageDraw.Draw(result).text(
        (16, 12), title, fill=(245, 238, 220), font=font(24)
    )
    return result


def build_board() -> None:
    panels = [
        labeled_panel(rgba_depth(closed), "CLOSED — normalized front depth"),
        labeled_panel(rgba_depth(opened), "OPEN — normalized front depth"),
        labeled_panel(
            rgba_difference(difference),
            "SIGNED CHANGE — gold=recessed, blue=forward",
        ),
    ]
    board = Image.new(
        "RGB",
        (sum(panel.width for panel in panels), max(panel.height for panel in panels)),
        (20, 23, 28),
    )
    x = 0
    for panel in panels:
        board.paste(panel, (x, 0))
        x += panel.width
    board.save(ROOT / "open_closed_front_depth_comparison.png")


def main() -> None:
    region_metrics = {}
    for name, bounds in REGIONS.items():
        mask = region_mask(bounds)
        signed = difference[mask]
        region_metrics[name] = {
            "sample_count": int(signed.size),
            "signed_closed_minus_open_normalized_x": percentiles(signed),
            "absolute_normalized_x": percentiles(np.abs(signed)),
        }

    mouth_mask = region_mask(REGIONS["mouth"])
    # A 2.5%-of-character-depth separation strongly exceeds body noise and
    # isolates the visible mouth opening in this source pair.
    recessed = mouth_mask & (difference >= 0.025)
    forward = mouth_mask & (difference <= -0.025)
    recessed_box = normalized_box(recessed)
    forward_box = normalized_box(forward)
    report = {
        "schema_version": "1.0.0",
        "inputs": {
            "closed_sha256": RAW["closed"]["sha256"],
            "open_sha256": RAW["open"]["sha256"],
        },
        "alignment": {
            "object_transforms_are_identity": True,
            "axes_match": True,
            "dimension_ratio_open_over_closed": [
                float(open_value / closed_value)
                for open_value, closed_value in zip(
                    RAW["open"]["bounds"]["dimensions"],
                    RAW["closed"]["bounds"]["dimensions"],
                )
            ],
            "center_delta_open_minus_closed": [
                float(open_value - closed_value)
                for open_value, closed_value in zip(
                    RAW["open"]["bounds"]["center"],
                    RAW["closed"]["bounds"]["center"],
                )
            ],
            "interpretation": (
                "The sources share orientation, origin, and nearly identical "
                "overall scale, but are independently generated surfaces."
            ),
        },
        "topology_compatibility": {
            "closed_vertices": RAW["closed"]["topology"]["totals"]["vertices"],
            "open_vertices": RAW["open"]["topology"]["totals"]["vertices"],
            "vertex_count_delta_open_minus_closed": (
                RAW["open"]["topology"]["totals"]["vertices"]
                - RAW["closed"]["topology"]["totals"]["vertices"]
            ),
            "same_vertex_count": False,
            "shape_key_compatible": False,
            "reason": (
                "Blend shapes require identical topology and vertex order; "
                "these independently generated one-shell triangle meshes have "
                "different vertex and face counts."
            ),
        },
        "region_metrics": region_metrics,
        "visible_mouth_opening_change": {
            "threshold_normalized_x": 0.025,
            "recessed_sample_count": int(recessed.sum()),
            "recessed_normalized_yz_bounds": recessed_box,
            "recessed_open_world_yz_bounds": world_box_from_yz(
                RAW["open"], recessed_box
            ),
            "forward_sample_count": int(forward.sum()),
            "forward_normalized_yz_bounds": forward_box,
            "note": (
                "The recessed region is the useful visual mouth-aperture "
                "envelope. Forward changes include tongue/lower-lip volume "
                "plus stochastic cheek and muzzle differences and should not "
                "be interpreted as a clean tongue segmentation."
            ),
        },
        "structural_read": {
            "mesh_objects_each": 1,
            "connected_components_each": 1,
            "mouth_cavity_separate": False,
            "tongue_separate": False,
            "eyes_separate": False,
            "interpretation": (
                "Head, eyelid/eye arcs, lips, cavity floor/tongue, horns, "
                "claws, and body are fused into one watertight shell. They "
                "cannot be independently animated without authored production "
                "topology or replacement face components."
            ),
        },
    }
    (ROOT / "facial_probe_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    build_board()


if __name__ == "__main__":
    main()
