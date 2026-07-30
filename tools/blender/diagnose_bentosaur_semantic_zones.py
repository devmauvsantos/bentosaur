"""Render candidate-specific semantic-zone coverage on the accepted H3.1 mesh.

The oriented ellipsoids in the JSON profile are classifiers only. This script
never creates ellipsoid objects. It assigns diagnostic materials directly to
the existing source polygons whose centers fall inside the configured zones.

Run:

    /Applications/Blender.app/Contents/MacOS/Blender \
      --background \
      art/candidates/tripo/visual-gate-03/h31-detailed-neutral/evaluation/\
bentosaur_vg03_h31_detailed_neutral_source_locked_evaluation.blend \
      --python tools/blender/diagnose_bentosaur_semantic_zones.py -- \
      --profile tools/blender/config/\
bentosaur_h31_detailed_neutral_semantic_zones_v1.json \
      --output art/candidates/tripo/visual-gate-03/h31-detailed-neutral/\
semantic-zone-diagnostic-v1
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Euler, Matrix, Vector
import numpy as np


VIEW_DIRECTIONS = {
    "front": Vector((1.0, 0.0, 0.0)),
    "left": Vector((0.0, 1.0, 0.0)),
    "back": Vector((-1.0, 0.0, 0.0)),
    "right": Vector((0.0, -1.0, 0.0)),
    "three_quarter_left": Vector((1.0, 1.0, 0.08)).normalized(),
    "three_quarter_right": Vector((1.0, -1.0, 0.08)).normalized(),
}

GROUP_COLORS = {
    "belly_patch": "#F3D38B",
    "primary_horns": "#FF9C62",
    "frill_knobs": "#FFE86E",
    "dorsal_tail_knobs": "#C7F36B",
    "hand_claws": "#FF8EC7",
    "foot_claws": "#77DDF5",
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=640)
    return parser.parse_args(argv)


def hex_rgba(value: str) -> tuple[float, float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) / 255.0
                 for index in (0, 2, 4)) + (1.0,)


def make_material(name: str, color: str) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = hex_rgba(color)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = hex_rgba(color)
    bsdf.inputs["Roughness"].default_value = 0.88
    bsdf.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.14
    return material


def world_bounds(obj: bpy.types.Object) -> tuple[np.ndarray, np.ndarray]:
    corners = np.array([
        tuple(obj.matrix_world @ Vector(corner))
        for corner in obj.bound_box
    ], dtype=np.float64)
    return corners.min(axis=0), corners.max(axis=0)


def polygon_centers_and_normals(
    obj: bpy.types.Object,
) -> tuple[np.ndarray, np.ndarray]:
    polygons = obj.data.polygons
    centers = np.empty(len(polygons) * 3, dtype=np.float64)
    normals = np.empty(len(polygons) * 3, dtype=np.float64)
    polygons.foreach_get("center", centers)
    polygons.foreach_get("normal", normals)
    centers = centers.reshape((-1, 3))
    normals = normals.reshape((-1, 3))

    world = np.array(obj.matrix_world, dtype=np.float64)
    centers = centers @ world[:3, :3].T + world[:3, 3]
    normal_matrix = np.array(
        obj.matrix_world.to_3x3().inverted().transposed(),
        dtype=np.float64,
    )
    normals = normals @ normal_matrix.T
    lengths = np.linalg.norm(normals, axis=1)
    normals /= np.maximum(lengths[:, None], 1e-12)
    return centers, normals


def region_mask(
    normalized_centers: np.ndarray,
    world_normals: np.ndarray,
    region: dict[str, object],
) -> np.ndarray:
    center = np.array(region["center"], dtype=np.float64)
    radii = np.array(region["radii"], dtype=np.float64)
    if np.any(radii <= 0.0):
        raise ValueError(f"Non-positive radii in {region['id']}")
    degrees = region.get("orientation_euler_degrees", [0.0, 0.0, 0.0])
    rotation = Euler(
        tuple(math.radians(float(value)) for value in degrees),
        "XYZ",
    ).to_matrix()
    rotation_np = np.array(rotation, dtype=np.float64)
    local = (normalized_centers - center) @ rotation_np
    mask = np.sum((local / radii) ** 2, axis=1) <= 1.0
    normal_filter = region.get("normal_filter")
    if normal_filter:
        axis = np.array(normal_filter["axis"], dtype=np.float64)
        axis /= max(np.linalg.norm(axis), 1e-12)
        mask &= (
            world_normals @ axis
            >= float(normal_filter["minimum_dot"])
        )
    return mask


def source_mesh() -> bpy.types.Object:
    preferred = [
        obj for obj in bpy.data.objects
        if obj.type == "MESH" and obj.name.startswith("EVAL_HD__")
    ]
    if not preferred:
        preferred = [
            obj for obj in bpy.data.objects
            if obj.type == "MESH"
            and "tripo_node" in obj.name
            and not obj.hide_render
        ]
    if len(preferred) != 1:
        raise RuntimeError(
            f"Expected one visible evaluated H3.1 mesh, found "
            f"{[obj.name for obj in preferred]}"
        )
    return preferred[0]


def apply_zone_materials(
    obj: bpy.types.Object,
    profile: dict[str, object],
) -> dict[str, object]:
    body = make_material("SEMANTIC_DIAGNOSTIC_BODY", "#657A68")
    materials = [body]
    material_indices = {"body": 0}
    for group, color in GROUP_COLORS.items():
        material_indices[group] = len(materials)
        materials.append(
            make_material(
                f"SEMANTIC_DIAGNOSTIC_{group.upper()}",
                color,
            )
        )
    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)

    centers, normals = polygon_centers_and_normals(obj)
    minimum, maximum = world_bounds(obj)
    dimensions = maximum - minimum
    normalized = (centers - minimum) / dimensions
    assignments = np.zeros(len(obj.data.polygons), dtype=np.int32)
    rows: list[dict[str, object]] = []

    for group, regions in profile["zones"].items():
        group_union = np.zeros(len(assignments), dtype=bool)
        for region in regions:
            mask = region_mask(normalized, normals, region)
            group_union |= mask
            selected = normalized[mask]
            row = {
                "group": group,
                "id": region["id"],
                "selected_polygons": int(mask.sum()),
            }
            if len(selected):
                row["selected_normalized_bounds"] = {
                    "minimum": selected.min(axis=0).round(6).tolist(),
                    "maximum": selected.max(axis=0).round(6).tolist(),
                }
            rows.append(row)
        assignments[group_union] = material_indices[group]

    obj.data.polygons.foreach_set("material_index", assignments)
    obj.data.update()
    return {
        "mesh_object": obj.name,
        "polygon_count": len(obj.data.polygons),
        "source_bounds": {
            "minimum": minimum.tolist(),
            "maximum": maximum.tolist(),
            "dimensions": dimensions.tolist(),
        },
        "selected_polygons_total": int(np.count_nonzero(assignments)),
        "selected_polygon_ratio": float(np.count_nonzero(assignments)
                                        / len(assignments)),
        "regions": rows,
        "debug_materials": {
            group: {
                "color": GROUP_COLORS[group],
                "material_index": material_indices[group],
            }
            for group in GROUP_COLORS
        },
        "renderable_classifier_geometry_created": False,
    }


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


def place_camera(
    camera: bpy.types.Object,
    target: Vector,
    direction: Vector,
    distance: float,
) -> None:
    camera.location = target + direction.normalized() * distance
    point_at(camera, target)


def render_views(
    obj: bpy.types.Object,
    output: Path,
    resolution: int,
) -> dict[str, str]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filter_size = 0.75
    scene.render.use_file_extension = True
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.background_type = "VIEWPORT"
    scene.display.shading.background_color = (0.018, 0.024, 0.032)
    for candidate in bpy.data.objects:
        if candidate.type == "MESH" and candidate is not obj:
            candidate.hide_render = True

    camera = next(
        (candidate for candidate in bpy.data.objects
         if candidate.type == "CAMERA"),
        None,
    )
    if camera is None:
        camera_data = bpy.data.cameras.new("SEMANTIC_ZONE_CAMERA")
        camera = bpy.data.objects.new(
            "SEMANTIC_ZONE_CAMERA", camera_data
        )
        scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.dof.use_dof = False
    scene.camera = camera

    minimum_np, maximum_np = world_bounds(obj)
    minimum = Vector(minimum_np.tolist())
    maximum = Vector(maximum_np.tolist())
    center = (minimum + maximum) * 0.5
    scale = max(maximum - minimum)
    camera.data.ortho_scale = scale / 0.89
    distance = scale * 3.2

    paths = {}
    for name, direction in VIEW_DIRECTIONS.items():
        place_camera(camera, center, direction, distance)
        path = output / "renders" / f"{name}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths[name] = str(path)
    return paths


def main() -> None:
    args = parse_args()
    profile_path = args.profile.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    obj = source_mesh()
    metrics = apply_zone_materials(obj, profile)
    metrics["profile"] = str(profile_path)
    metrics["renders"] = render_views(obj, output, args.resolution)
    (output / "coverage-metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )
    bpy.ops.wm.save_as_mainfile(
        filepath=str(output / "semantic-zone-diagnostic.blend")
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
