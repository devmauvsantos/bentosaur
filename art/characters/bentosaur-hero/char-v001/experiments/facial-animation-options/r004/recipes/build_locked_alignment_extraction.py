"""Build the source-locked open-mouth alignment and extraction checkpoint.

This recipe intentionally stops before any production-body edit.  It verifies
the immutable VG06 source hash, appends only the S40 r003 production body,
applies the exact shared S40 vendor-to-production matrix to the open source,
extracts an inspection-only source mouth region, and derives a depth
discontinuity mask directly from source ray hits.

No aperture spline, Bezier, ellipse, Boolean cutter, or hand-authored lip
curve is created here.  The generated mask is diagnostic evidence used to
decide whether a localized quad retopology can be authored without guessing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from collections import deque

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
import numpy as np


def repository_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError(f"No Git repository found above {start}")


OUTPUT = Path(__file__).resolve().parents[1]
ROOT = repository_root(OUTPUT)
OPEN_SOURCE = ROOT / (
    "art/candidates/tripo/visual-gate-06/h31-detailed-open-mouth/"
    "tripo-out/model.glb"
)
PRODUCTION_SOURCE = ROOT / (
    "art/characters/bentosaur-hero/char-v001/stages/"
    "s40-production-topology/r003/source/"
    "bentosaur_hero_s40_production_topology_r003.blend"
)
BODY_NAME = "BENTOSAUR_BODY_RETOPO_WIP_R003"
OPEN_SOURCE_SHA256 = (
    "7c0d7e2e1e4ee8fb4db320880f6f4b5c82c470bce37437ce28d26efa171b01d4"
)

# Exact shared closed-source production normalization:
# vendor +X front / +Y character-left / +Z up
# -> canonical -Y front / +X character-left / +Z up.
NORMALIZATION_SCALE = 1.0207102117712663
NORMALIZATION_Z_OFFSET = 0.499774008028646
SOURCE_TO_PRODUCTION = Matrix(
    (
        (0.0, NORMALIZATION_SCALE, 0.0, 0.0),
        (-NORMALIZATION_SCALE, 0.0, 0.0, 0.0),
        (0.0, 0.0, NORMALIZATION_SCALE, NORMALIZATION_Z_OFFSET),
        (0.0, 0.0, 0.0, 1.0),
    )
)

# Broad extraction bounds only.  These are not used to define the aperture.
REGION_BOUNDS = {
    "x_min": -0.155,
    "x_max": 0.155,
    "y_min": -0.455,
    "y_max": -0.175,
    "z_min": 0.375,
    "z_max": 0.595,
}

# Ray grid around the visible mouth.  The contour comes from source depth,
# while these bounds merely limit the diagnostic field of view.
GRID_WIDTH = 301
GRID_HEIGHT = 241
GRID_X_MIN = -0.155
GRID_X_MAX = 0.155
GRID_Z_MIN = 0.375
GRID_Z_MAX = 0.595
RAY_START_Y = -0.650
RAY_DIRECTION = Vector((0.0, 1.0, 0.0))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def save_checkpoint(path: Path) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
    return {
        "path": rel(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def ensure_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_exclusive(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> None:
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def append_body() -> bpy.types.Object:
    with bpy.data.libraries.load(str(PRODUCTION_SOURCE), link=False) as (
        data_from,
        data_to,
    ):
        if BODY_NAME not in data_from.objects:
            raise RuntimeError(
                f"{BODY_NAME!r} not found in {PRODUCTION_SOURCE}"
            )
        data_to.objects = [BODY_NAME]
    body = data_to.objects[0]
    bpy.context.scene.collection.objects.link(body)
    body.name = "S40_R003_PRODUCTION_BODY_LOCKED"
    body.hide_select = True
    body["source_path"] = rel(PRODUCTION_SOURCE)
    body["source_sha256"] = sha256(PRODUCTION_SOURCE)
    body["geometry_role"] = "production_body_geometry_authority"
    body["immutable_in_this_candidate"] = True
    return body


def import_open_source() -> bpy.types.Object:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(OPEN_SOURCE))
    imported = [
        obj
        for obj in bpy.data.objects
        if obj not in before and obj.type == "MESH"
    ]
    if len(imported) != 1:
        raise RuntimeError(
            f"Expected one imported open source mesh, found {len(imported)}"
        )
    source = imported[0]
    source.data = source.data.copy()
    source.data.transform(SOURCE_TO_PRODUCTION @ source.matrix_world)
    source.matrix_world = Matrix.Identity(4)
    source.name = "TRIPO_VG06_OPEN_SOURCE_LOCKED"
    source.data.name = "TRIPO_VG06_OPEN_SOURCE_LOCKED_MESH"
    source.hide_select = True
    source["source_path"] = rel(OPEN_SOURCE)
    source["source_sha256"] = OPEN_SOURCE_SHA256
    source["geometry_role"] = "open_mouth_geometry_authority"
    source["immutable_in_this_candidate"] = True
    source["source_to_production_matrix_row_major"] = json.dumps(
        [list(row) for row in SOURCE_TO_PRODUCTION]
    )
    return source


def in_region(point: Vector) -> bool:
    return (
        REGION_BOUNDS["x_min"] <= point.x <= REGION_BOUNDS["x_max"]
        and REGION_BOUNDS["y_min"] <= point.y <= REGION_BOUNDS["y_max"]
        and REGION_BOUNDS["z_min"] <= point.z <= REGION_BOUNDS["z_max"]
    )


def extract_source_region(source: bpy.types.Object) -> bpy.types.Object:
    selected_faces: list[tuple[int, int, int]] = []
    selected_vertices: set[int] = set()
    coordinates = [vertex.co.copy() for vertex in source.data.vertices]
    inside = [in_region(coordinate) for coordinate in coordinates]
    for polygon in source.data.polygons:
        vertices = tuple(polygon.vertices)
        if all(inside[index] for index in vertices):
            selected_faces.append(vertices)
            selected_vertices.update(vertices)

    remap = {
        old_index: new_index
        for new_index, old_index in enumerate(sorted(selected_vertices))
    }
    mesh = bpy.data.meshes.new("TRIPO_VG06_MOUTH_REGION_SOURCE_MESH")
    mesh.from_pydata(
        [coordinates[index] for index in sorted(selected_vertices)],
        [],
        [
            tuple(remap[index] for index in face)
            for face in selected_faces
        ],
    )
    mesh.update()
    region = bpy.data.objects.new(
        "TRIPO_VG06_MOUTH_REGION_SOURCE_LOCKED", mesh
    )
    region.hide_select = True
    region["source_object"] = source.name
    region["selection_role"] = (
        "inspection_only_broad_source_region_not_aperture"
    )
    region["region_bounds"] = json.dumps(REGION_BOUNDS, sort_keys=True)
    return region


def otsu_threshold(values: np.ndarray) -> float:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        raise RuntimeError("No finite ray hits for Otsu threshold")
    counts, edges = np.histogram(finite, bins=256)
    centers = (edges[:-1] + edges[1:]) * 0.5
    weights_left = np.cumsum(counts)
    weights_right = finite.size - weights_left
    sums_left = np.cumsum(counts * centers)
    total_sum = sums_left[-1]
    means_left = np.divide(
        sums_left,
        weights_left,
        out=np.zeros_like(sums_left, dtype=float),
        where=weights_left > 0,
    )
    means_right = np.divide(
        total_sum - sums_left,
        weights_right,
        out=np.zeros_like(sums_left, dtype=float),
        where=weights_right > 0,
    )
    between = (
        weights_left
        * weights_right
        * (means_left - means_right) ** 2
    )
    valid = (weights_left > 0) & (weights_right > 0)
    index = int(np.argmax(np.where(valid, between, -1.0)))
    return float(centers[index])


def connected_components(mask: np.ndarray) -> list[list[tuple[int, int]]]:
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    components: list[list[tuple[int, int]]] = []
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
                for delta_row, delta_column in (
                    (-1, 0),
                    (1, 0),
                    (0, -1),
                    (0, 1),
                ):
                    next_row = current_row + delta_row
                    next_column = current_column + delta_column
                    if (
                        0 <= next_row < height
                        and 0 <= next_column < width
                        and mask[next_row, next_column]
                        and not visited[next_row, next_column]
                    ):
                        visited[next_row, next_column] = True
                        queue.append((next_row, next_column))
            components.append(component)
    return components


def write_pgm(path: Path, pixels: np.ndarray) -> None:
    height, width = pixels.shape
    path.write_bytes(
        f"P5\n{width} {height}\n255\n".encode("ascii")
        + np.ascontiguousarray(pixels, dtype=np.uint8).tobytes()
    )


def write_ppm(path: Path, pixels: np.ndarray) -> None:
    height, width, channels = pixels.shape
    if channels != 3:
        raise RuntimeError("PPM image must have exactly three channels")
    path.write_bytes(
        f"P6\n{width} {height}\n255\n".encode("ascii")
        + np.ascontiguousarray(pixels, dtype=np.uint8).tobytes()
    )


def sample_depth(source: bpy.types.Object) -> dict[str, object]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = source.evaluated_get(depsgraph)
    bvh = BVHTree.FromObject(evaluated, depsgraph)
    x_values = np.linspace(GRID_X_MIN, GRID_X_MAX, GRID_WIDTH)
    z_values = np.linspace(GRID_Z_MAX, GRID_Z_MIN, GRID_HEIGHT)
    depth = np.full((GRID_HEIGHT, GRID_WIDTH), np.nan, dtype=np.float32)

    for row, z_value in enumerate(z_values):
        for column, x_value in enumerate(x_values):
            location, _normal, _index, _distance = bvh.ray_cast(
                Vector((float(x_value), RAY_START_Y, float(z_value))),
                RAY_DIRECTION,
            )
            if location is not None:
                depth[row, column] = location.y

    threshold = otsu_threshold(depth)
    candidate_mask = np.isfinite(depth) & (depth > threshold)
    components = connected_components(candidate_mask)
    if not components:
        raise RuntimeError("Depth threshold produced no components")

    deepest = np.unravel_index(np.nanargmax(depth), depth.shape)
    chosen = next(
        (
            component
            for component in components
            if deepest in component
        ),
        max(components, key=len),
    )
    mask = np.zeros_like(candidate_mask)
    for row, column in chosen:
        mask[row, column] = True

    boundary_pixels: list[tuple[int, int]] = []
    for row, column in chosen:
        if any(
            next_row < 0
            or next_row >= GRID_HEIGHT
            or next_column < 0
            or next_column >= GRID_WIDTH
            or not mask[next_row, next_column]
            for next_row, next_column in (
                (row - 1, column),
                (row + 1, column),
                (row, column - 1),
                (row, column + 1),
            )
        ):
            boundary_pixels.append((row, column))

    finite = depth[np.isfinite(depth)]
    minimum = float(finite.min())
    maximum = float(finite.max())
    normalized = np.zeros_like(depth, dtype=np.uint8)
    if maximum > minimum:
        normalized[np.isfinite(depth)] = np.clip(
            (depth[np.isfinite(depth)] - minimum)
            / (maximum - minimum)
            * 255.0,
            0.0,
            255.0,
        ).astype(np.uint8)

    qa = OUTPUT / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    write_pgm(qa / "source_front_depth.pgm", normalized)
    write_pgm(
        qa / "source_depth_component_mask.pgm",
        mask.astype(np.uint8) * 255,
    )
    overlay = np.repeat(normalized[:, :, None], 3, axis=2)
    for row, column in boundary_pixels:
        overlay[row, column] = (255, 64, 48)
    write_ppm(qa / "source_depth_boundary_overlay.ppm", overlay)

    boundary_points = [
        {
            "pixel": [column, row],
            "canonical_x": float(x_values[column]),
            "canonical_z": float(z_values[row]),
            "source_front_y": float(depth[row, column]),
        }
        for row, column in boundary_pixels
    ]
    np.save(qa / "source_front_depth.npy", depth)

    return {
        "grid": {
            "width": GRID_WIDTH,
            "height": GRID_HEIGHT,
            "x_min": GRID_X_MIN,
            "x_max": GRID_X_MAX,
            "z_min": GRID_Z_MIN,
            "z_max": GRID_Z_MAX,
            "ray_start_y": RAY_START_Y,
            "ray_direction": list(RAY_DIRECTION),
        },
        "front_y_range": [minimum, maximum],
        "otsu_threshold_front_y": threshold,
        "candidate_component_count": len(components),
        "candidate_component_sizes_desc": sorted(
            (len(component) for component in components), reverse=True
        )[:20],
        "deepest_pixel": [int(deepest[1]), int(deepest[0])],
        "chosen_component_pixels": int(mask.sum()),
        "chosen_boundary_pixels": len(boundary_pixels),
        "boundary_points_unordered": boundary_points,
        "artifacts": {
            "depth": rel(qa / "source_front_depth.pgm"),
            "component_mask": rel(
                qa / "source_depth_component_mask.pgm"
            ),
            "boundary_overlay": rel(
                qa / "source_depth_boundary_overlay.ppm"
            ),
            "depth_npy": rel(qa / "source_front_depth.npy"),
        },
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for directory in ("work", "source", "qa", "evidence/renders"):
        (OUTPUT / directory).mkdir(parents=True, exist_ok=True)

    actual_source_hash = sha256(OPEN_SOURCE)
    if actual_source_hash != OPEN_SOURCE_SHA256:
        raise RuntimeError(
            "Open source hash mismatch: "
            f"{actual_source_hash} != {OPEN_SOURCE_SHA256}"
        )

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene["candidate_role"] = (
        "source_locked_alignment_and_extraction_checkpoint"
    )
    scene["source_sha256_verified"] = True
    scene["no_paid_api_used"] = True
    scene["retopology_authored"] = False

    body_collection = ensure_collection("LOCKED_S40_R003_BODY")
    source_collection = ensure_collection("LOCKED_TRIPO_VG06_OPEN_SOURCE")
    extraction_collection = ensure_collection(
        "LOCKED_SOURCE_MOUTH_REGION_EXTRACTION"
    )

    body = append_body()
    move_exclusive(body, body_collection)
    source = import_open_source()
    move_exclusive(source, source_collection)
    locked_checkpoint = save_checkpoint(
        OUTPUT / "work/00_locked_inputs.blend"
    )

    alignment_checkpoint = save_checkpoint(
        OUTPUT / "work/10_exact_matrix_aligned_overlay.blend"
    )
    source.hide_select = False
    region = extract_source_region(source)
    extraction_collection.objects.link(region)
    source.hide_select = True
    region.hide_select = True
    extraction_checkpoint = save_checkpoint(
        OUTPUT / "work/20_source_mouth_region_extraction.blend"
    )

    depth_report = sample_depth(source)
    source_checkpoint = save_checkpoint(
        OUTPUT
        / "source/tripo_mouth_transfer_alignment_extraction.blend"
    )

    report = {
        "candidate_id": "tripo-mouth-transfer-candidate",
        "status": "locked_alignment_and_extraction_complete",
        "retopology_authored": False,
        "paid_api_usage": {
            "tripo_credits_spent": 0,
            "recorded_balance": 4695,
        },
        "inputs": {
            "open_source": {
                "path": rel(OPEN_SOURCE),
                "sha256_expected": OPEN_SOURCE_SHA256,
                "sha256_actual": actual_source_hash,
                "sha256_verified": True,
                "vertices": len(source.data.vertices),
                "triangles": len(source.data.polygons),
            },
            "production_body": {
                "path": rel(PRODUCTION_SOURCE),
                "sha256": sha256(PRODUCTION_SOURCE),
                "object": BODY_NAME,
                "vertices": len(body.data.vertices),
                "faces": len(body.data.polygons),
            },
        },
        "source_to_production_transform": {
            "matrix_row_major": [
                list(row) for row in SOURCE_TO_PRODUCTION
            ],
            "normalization_scale": NORMALIZATION_SCALE,
            "normalization_z_offset": NORMALIZATION_Z_OFFSET,
            "provenance": (
                "exact shared S40 closed-source production normalization"
            ),
        },
        "extraction": {
            "role": (
                "broad inspection-only source region; not an aperture curve"
            ),
            "bounds": REGION_BOUNDS,
            "vertices": len(region.data.vertices),
            "triangles": len(region.data.polygons),
        },
        "depth_diagnostic": depth_report,
        "checkpoints": {
            "locked_inputs": locked_checkpoint,
            "aligned_overlay": alignment_checkpoint,
            "source_region_extraction": extraction_checkpoint,
            "canonical_source": source_checkpoint,
        },
        "stop_rule": (
            "Do not author a mouth loop unless the source-derived depth "
            "evidence yields one clean, semantic aperture boundary."
        ),
    }
    report_path = OUTPUT / "qa/alignment_extraction_report.json"
    report_path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
