"""Apply the single permitted source-depth diagnostic correction.

The first absolute-open-depth diagnostic selected the lower muzzle/body
transition.  This correction uses the already preserved r001 neutral/open
front-depth pair, the r001 validated 0.025 normalized-depth separation, and
the measured production-space mouth envelope.  It does not construct a curve
or edit geometry.

The result is deliberately evaluated for semantic completeness: a connected
recessed-cavity component is not automatically a usable aperture loop when
its lower edge is an occluding tongue/front-volume edge.
"""

from __future__ import annotations

from collections import deque
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def repository_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError(f"No Git repository found above {start}")


CANDIDATE = Path(__file__).resolve().parents[1]
ROOT = repository_root(CANDIDATE)
PROBE = ROOT / (
    "art/characters/bentosaur-hero/char-v001/experiments/"
    "facial-animation-options/r001/qa/source-probe"
)
SCALE = 1.0207102117712663
Z_OFFSET = 0.499774008028646
DELTA_THRESHOLD = 0.025
ENVELOPE = {
    "canonical_x_min": -0.10,
    "canonical_x_max": 0.10,
    "canonical_z_min": 0.4328,
    "canonical_z_max": 0.5143,
}


def components(mask: np.ndarray) -> list[list[tuple[int, int]]]:
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    result: list[list[tuple[int, int]]] = []
    for row in range(height):
        for column in range(width):
            if not mask[row, column] or visited[row, column]:
                continue
            queue = deque([(row, column)])
            visited[row, column] = True
            component: list[tuple[int, int]] = []
            while queue:
                current_row, current_column = queue.popleft()
                component.append((current_row, current_column))
                for next_row, next_column in (
                    (current_row - 1, current_column),
                    (current_row + 1, current_column),
                    (current_row, current_column - 1),
                    (current_row, current_column + 1),
                ):
                    if (
                        0 <= next_row < height
                        and 0 <= next_column < width
                        and mask[next_row, next_column]
                        and not visited[next_row, next_column]
                    ):
                        visited[next_row, next_column] = True
                        queue.append((next_row, next_column))
            result.append(component)
    return result


def main() -> None:
    qa = CANDIDATE / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    raw = json.loads((PROBE / "source_probe_raw.json").read_text())
    closed = np.load(PROBE / "closed_front_depth.npz")["depth"]
    opened = np.load(PROBE / "open_front_depth.npz")["depth"]
    difference = closed - opened
    valid = np.isfinite(closed) & np.isfinite(opened)
    height, width = difference.shape

    y_normalized = np.linspace(0.0, 1.0, width)
    z_normalized = np.linspace(1.0, 0.0, height)
    open_minimum = np.array(raw["open"]["bounds"]["minimum"])
    open_dimensions = np.array(raw["open"]["bounds"]["dimensions"])
    open_world_y = open_minimum[1] + y_normalized * open_dimensions[1]
    open_world_z = open_minimum[2] + z_normalized * open_dimensions[2]
    canonical_x = open_world_y * SCALE
    canonical_z = open_world_z * SCALE + Z_OFFSET

    envelope_mask = (
        valid
        & (
            canonical_x[None, :]
            >= ENVELOPE["canonical_x_min"]
        )
        & (
            canonical_x[None, :]
            <= ENVELOPE["canonical_x_max"]
        )
        & (
            canonical_z[:, None]
            >= ENVELOPE["canonical_z_min"]
        )
        & (
            canonical_z[:, None]
            <= ENVELOPE["canonical_z_max"]
        )
    )
    recessed = envelope_mask & (difference >= DELTA_THRESHOLD)
    found = sorted(components(recessed), key=len, reverse=True)
    dominant = found[0]
    dominant_mask = np.zeros_like(recessed)
    for row, column in dominant:
        dominant_mask[row, column] = True

    component_rows = []
    for component in found:
        points = np.array(component)
        row_min, column_min = points.min(axis=0)
        row_max, column_max = points.max(axis=0)
        component_rows.append(
            {
                "pixels": len(component),
                "canonical_bounds_xz": {
                    "minimum": [
                        float(canonical_x[column_min]),
                        float(canonical_z[row_max]),
                    ],
                    "maximum": [
                        float(canonical_x[column_max]),
                        float(canonical_z[row_min]),
                    ],
                },
            }
        )

    # Render the signed delta and the corrected component at native resolution.
    magnitude = np.nan_to_num(
        np.clip(np.abs(difference) / 0.08, 0.0, 1.0),
        nan=0.0,
        posinf=1.0,
        neginf=0.0,
    )
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    positive = difference >= 0.0
    rgb[..., 0] = np.where(positive, 40 + magnitude * 180, 20)
    rgb[..., 1] = np.where(positive, 30 + magnitude * 120, 50)
    rgb[..., 2] = np.where(positive, 20, 40 + magnitude * 180)
    rgb[~valid] = (18, 20, 24)
    rgb[dominant_mask] = (255, 188, 52)

    image = Image.fromarray(rgb, mode="RGB")
    draw = ImageDraw.Draw(image)
    columns = np.where(
        (canonical_x >= ENVELOPE["canonical_x_min"])
        & (canonical_x <= ENVELOPE["canonical_x_max"])
    )[0]
    rows = np.where(
        (canonical_z >= ENVELOPE["canonical_z_min"])
        & (canonical_z <= ENVELOPE["canonical_z_max"])
    )[0]
    draw.rectangle(
        (
            int(columns.min()),
            int(rows.min()),
            int(columns.max()),
            int(rows.max()),
        ),
        outline=(104, 222, 255),
        width=1,
    )
    image = image.resize((960, 960), Image.Resampling.NEAREST)
    overlay_path = qa / "open_closed_delta_component_overlay.png"
    image.save(overlay_path)

    mask_image = Image.fromarray(
        dominant_mask.astype(np.uint8) * 255,
        mode="L",
    ).resize((960, 960), Image.Resampling.NEAREST)
    mask_path = qa / "open_closed_delta_dominant_mask.png"
    mask_image.save(mask_path)

    report = {
        "diagnostic": "single_permitted_open_minus_neutral_depth_correction",
        "inputs": {
            "closed_depth": str(
                (PROBE / "closed_front_depth.npz").relative_to(ROOT)
            ),
            "open_depth": str(
                (PROBE / "open_front_depth.npz").relative_to(ROOT)
            ),
            "closed_sha256": raw["closed"]["sha256"],
            "open_sha256": raw["open"]["sha256"],
        },
        "source_to_production": {
            "scale": SCALE,
            "z_offset": Z_OFFSET,
        },
        "measured_envelope": ENVELOPE,
        "recessed_threshold_normalized_front_depth": DELTA_THRESHOLD,
        "envelope_samples": int(envelope_mask.sum()),
        "recessed_samples": int(recessed.sum()),
        "component_count": len(found),
        "components": component_rows,
        "dominant_component_is_connected": True,
        "dominant_component_is_full_aperture_boundary": False,
        "semantic_limitation": (
            "The dominant component is the visible recessed cavity change. "
            "Its lower image-space edge is produced by tongue/lower-front "
            "occlusion, not by an observable complete lip boundary. A welded "
            "aperture loop derived from this edge would encode the tongue "
            "silhouette and invent the hidden lower lip contour."
        ),
        "verdict": {
            "localized_welded_quad_retopology_programmatically_defensible": (
                False
            ),
            "stop_checkpoint": "20_source_mouth_region_extraction",
            "reason": (
                "No complete semantic lip/aperture contour is recoverable "
                "from the authorized source delta without manual artistic "
                "loop placement or another extraction method."
            ),
            "no_geometry_approximation_performed": True,
        },
        "artifacts": {
            "delta_component_overlay": str(overlay_path.relative_to(ROOT)),
            "dominant_mask": str(mask_path.relative_to(ROOT)),
        },
    }
    path = qa / "open_closed_delta_verdict.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
