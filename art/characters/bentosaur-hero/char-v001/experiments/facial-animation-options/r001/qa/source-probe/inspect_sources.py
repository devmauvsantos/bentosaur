"""Read-only geometric comparison of Bentosaur closed/open Tripo sources.

The script imports each GLB into a temporary Blender scene, records transforms
and topology, and samples a normalized orthographic front-depth map.  It never
edits either input.  A final diagnostic .blend stores locked copies of both
sources in their original coordinate systems for later inspection.

Run with Blender 5.x:

    blender --background --factory-startup \
      --python inspect_sources.py -- \
      --closed /absolute/path/closed.glb \
      --open /absolute/path/open.glb \
      --out /absolute/path/output
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--closed", required=True, type=Path)
    parser.add_argument("--open", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--width", type=int, default=360)
    parser.add_argument("--height", type=int, default=360)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        for corner in obj.bound_box
    ]
    return (
        Vector(tuple(min(point[i] for point in points) for i in range(3))),
        Vector(tuple(max(point[i] for point in points) for i in range(3))),
    )


def import_glb(path: Path) -> list[bpy.types.Object]:
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError(f"No mesh found in {path}")
    return meshes


def matrix_rows(matrix) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix]


def topology_summary(meshes: list[bpy.types.Object]) -> dict[str, object]:
    objects = []
    totals = {
        "vertices": 0,
        "edges": 0,
        "polygons": 0,
        "triangles": 0,
        "uv_layers": 0,
        "material_slots": 0,
        "shape_keys": 0,
        "vertex_groups": 0,
    }
    for obj in meshes:
        mesh = obj.data
        mesh.calc_loop_triangles()
        shape_key_count = (
            len(mesh.shape_keys.key_blocks) if mesh.shape_keys else 0
        )
        row = {
            "name": obj.name,
            "matrix_world": matrix_rows(obj.matrix_world),
            "location": [float(v) for v in obj.location],
            "rotation_euler_radians": [
                float(v) for v in obj.rotation_euler
            ],
            "scale": [float(v) for v in obj.scale],
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "triangles": len(mesh.loop_triangles),
            "uv_layers": len(mesh.uv_layers),
            "material_slots": len(obj.material_slots),
            "shape_keys": shape_key_count,
            "vertex_groups": len(obj.vertex_groups),
        }
        objects.append(row)
        for key in totals:
            totals[key] += int(row[key])
    return {"mesh_objects": len(meshes), "totals": totals, "objects": objects}


def joined_bvh(meshes: list[bpy.types.Object]) -> BVHTree:
    """Build a world-space BVH without changing the imported object."""
    vertices: list[tuple[float, float, float]] = []
    polygons: list[tuple[int, int, int]] = []
    for obj in meshes:
        matrix = obj.matrix_world
        base = len(vertices)
        vertices.extend(tuple(matrix @ vertex.co) for vertex in obj.data.vertices)
        obj.data.calc_loop_triangles()
        polygons.extend(
            tuple(base + index for index in triangle.vertices)
            for triangle in obj.data.loop_triangles
        )
    return BVHTree.FromPolygons(vertices, polygons, all_triangles=True)


def front_depth_map(
    bvh: BVHTree,
    minimum: Vector,
    maximum: Vector,
    width: int,
    height: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return +X-facing normalized depth sampled on a normalized Y/Z grid."""
    dimensions = maximum - minimum
    y_values = np.linspace(0.0, 1.0, width, dtype=np.float32)
    # Row zero is the top of the character, convenient for image output.
    z_values = np.linspace(1.0, 0.0, height, dtype=np.float32)
    depths = np.full((height, width), np.nan, dtype=np.float32)
    ray_origin_x = maximum.x + dimensions.x * 0.10
    ray_length = dimensions.x * 1.30
    direction = Vector((-1.0, 0.0, 0.0))
    for row, z_norm in enumerate(z_values):
        z = minimum.z + float(z_norm) * dimensions.z
        for column, y_norm in enumerate(y_values):
            y = minimum.y + float(y_norm) * dimensions.y
            location, _normal, _index, _distance = bvh.ray_cast(
                Vector((ray_origin_x, y, z)), direction, ray_length
            )
            if location is not None:
                depths[row, column] = (
                    float(location.x) - minimum.x
                ) / dimensions.x
    return depths, y_values, z_values


def describe_source(
    label: str,
    path: Path,
    out: Path,
    width: int,
    height: int,
) -> dict[str, object]:
    clear_scene()
    meshes = import_glb(path)
    minimum, maximum = world_bounds(meshes)
    dimensions = maximum - minimum
    topology = topology_summary(meshes)
    bvh = joined_bvh(meshes)
    depth, y_values, z_values = front_depth_map(
        bvh, minimum, maximum, width, height
    )
    np.savez_compressed(
        out / f"{label}_front_depth.npz",
        depth=depth,
        y=y_values,
        z=z_values,
    )
    return {
        "label": label,
        "source": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "bounds": {
            "minimum": [float(v) for v in minimum],
            "maximum": [float(v) for v in maximum],
            "dimensions": [float(v) for v in dimensions],
            "center": [float(v) for v in ((minimum + maximum) * 0.5)],
        },
        "topology": topology,
        "normalized_landmark_windows": {
            "mouth": {
                "minimum": [0.74, 0.30, 0.42],
                "maximum": [1.01, 0.70, 0.59],
            },
            "eye_character_left": {
                "minimum": [0.84, 0.52, 0.55],
                "maximum": [1.01, 0.77, 0.70],
            },
            "eye_character_right": {
                "minimum": [0.84, 0.23, 0.55],
                "maximum": [1.01, 0.48, 0.70],
            },
            "full_face": {
                "minimum": [0.70, 0.16, 0.38],
                "maximum": [1.01, 0.84, 0.76],
            },
        },
    }


def save_locked_overlay(
    closed_path: Path, open_path: Path, destination: Path
) -> None:
    clear_scene()
    for label, path in (("CLOSED", closed_path), ("OPEN", open_path)):
        collection = bpy.data.collections.new(
            f"{label}__SOURCE_LOCKED_READ_ONLY"
        )
        bpy.context.scene.collection.children.link(collection)
        imported = import_glb(path)
        imported_set = set(imported)
        # Include any imported parent empties in the dedicated collection.
        hierarchy = set(imported)
        for obj in list(imported):
            parent = obj.parent
            while parent is not None:
                hierarchy.add(parent)
                parent = parent.parent
        for obj in hierarchy:
            for existing in list(obj.users_collection):
                existing.objects.unlink(obj)
            collection.objects.link(obj)
            obj[f"bentosaur_{label.lower()}_source_locked"] = True
            obj.hide_select = True
        collection["bentosaur_source_locked"] = True
        collection["source_path"] = str(path)
        collection["source_sha256"] = sha256(path)
        # Closed is visible by default; open can be toggled for overlay review.
        collection.hide_viewport = label == "OPEN"
        collection.hide_render = label == "OPEN"
    bpy.context.scene["inspection_only_no_source_edits"] = True
    bpy.ops.wm.save_as_mainfile(filepath=str(destination))


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "1.0.0",
        "purpose": "read_only_open_closed_facial_source_probe",
        "coordinate_contract": {
            "front": "+X",
            "character_left": "+Y",
            "up": "+Z",
            "normalized_space": (
                "(world_position - source_bounds_minimum) / "
                "source_bounds_dimensions"
            ),
        },
        "closed": describe_source(
            "closed", args.closed, args.out, args.width, args.height
        ),
        "open": describe_source(
            "open", args.open, args.out, args.width, args.height
        ),
        "depth_map": {
            "projection": "orthographic rays from +X toward -X",
            "width": args.width,
            "height": args.height,
            "stored_value": "normalized X of first surface hit",
            "missing_value": "NaN",
        },
    }
    (args.out / "source_probe_raw.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    save_locked_overlay(
        args.closed,
        args.open,
        args.out / "open_closed_source_locked_overlay.blend",
    )
    print(json.dumps({"status": "ok", "output": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
