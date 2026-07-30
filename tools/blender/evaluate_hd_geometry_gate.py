"""Evaluate an untextured Tripo H3.1 Detailed character candidate.

This is a non-destructive Visual Gate 03 evaluator. It imports the source GLB
into a locked, hidden collection, duplicates mesh datablocks for inspection,
and never writes to the source file.

Outputs:

* neutral-clay six-view renders;
* feature close-ups for eyes, muzzle/mouth, horns, frill, hands, feet, tail;
* two labeled review boards;
* raw and seam-welded topology diagnostics;
* an exact continuation-policy decision;
* an editable visual-review template;
* a source-locked Blender evaluation scene.

The evaluator cannot infer whether an eye, smile, or horn *looks right* from
topology counts. Therefore automatic continuation requires both:

1. all deterministic machine checks to pass; and
2. a completed visual-review JSON whose scores meet the policy.

Without the review JSON, the result is intentionally HOLD_FOR_CLAY_REVIEW.

Run:

    /Applications/Blender.app/Contents/MacOS/Blender \
      --background --factory-startup \
      --python tools/blender/evaluate_hd_geometry_gate.py -- \
      --input /absolute/path/model.glb \
      --output /absolute/path/evaluation \
      --candidate-id bentosaur_vg03_h31d_01 \
      --source-role candidate \
      --expected-mouth closed

After filling review-template.json, re-run with:

      --review-json /absolute/path/completed-review.json
"""

from __future__ import annotations

import argparse
import bmesh
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Iterable

import bpy
from mathutils import Vector


GATE_ID = "bentosaur_visual_gate_03_hd_geometry"
POLICY_VERSION = "1.0.0"
BOARD_FONT = "/System/Library/Fonts/Helvetica.ttc"

MACHINE_THRESHOLDS = {
    "mesh_object_count_min": 1,
    "evaluated_triangles_min": 20_000,
    "evaluated_triangles_max": 2_000_000,
    "welded_boundary_edge_ratio_max": 0.005,
    "welded_non_manifold_edge_ratio_max": 0.005,
    "welded_boundary_edges_absolute_max": 1_000,
    "welded_non_manifold_edges_absolute_max": 1_000,
    "degenerate_face_ratio_max": 0.0005,
    "loose_edges_max": 0,
    "loose_vertices_max": 0,
    "connected_components_max": 64,
    "largest_component_vertex_share_min": 0.90,
    "smallest_to_largest_bound_ratio_min": 0.12,
}

VISUAL_THRESHOLDS = {
    "score_min_each": 2,
    "score_average_min": 2.5,
    "score_max": 3,
    "all_blockers_must_be_false": True,
}

COMMON_VISUAL_FEATURES = (
    "overall_silhouette",
    "eye_forms",
    "muzzle_and_cheeks",
    "primary_horns",
    "frill_and_frill_knobs",
    "hands_and_fingers",
    "feet_and_toes",
    "tail",
)

MOUTH_FEATURES = {
    "closed": ("neutral_closed_mouth_seam",),
    "open": ("open_mouth_shape_and_volume",),
    "unknown": ("mouth_geometry_matches_reference",),
}

COMMON_VISUAL_BLOCKERS = (
    "doubled_or_ghost_eye_geometry",
    "fused_or_malformed_primary_horns",
    "lumpy_or_melted_frill_knobs",
    "fused_or_missing_digits",
    "broken_tail_silhouette",
    "severe_left_right_asymmetry",
    "unintended_detached_large_parts",
)

MOUTH_BLOCKERS = {
    "closed": ("malformed_or_collapsed_neutral_mouth_seam",),
    "open": (
        "collapsed_or_pinhole_open_mouth",
        "open_mouth_without_real_cavity",
    ),
    "unknown": ("mouth_geometry_fundamentally_malformed",),
}


def visual_features(expected_mouth: str) -> tuple[str, ...]:
    return (
        COMMON_VISUAL_FEATURES[:3]
        + MOUTH_FEATURES[expected_mouth]
        + COMMON_VISUAL_FEATURES[3:]
    )


def visual_blockers(expected_mouth: str) -> tuple[str, ...]:
    return COMMON_VISUAL_BLOCKERS + MOUTH_BLOCKERS[expected_mouth]


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument(
        "--source-role",
        choices=("candidate", "placeholder"),
        default="candidate",
    )
    parser.add_argument(
        "--expected-mouth",
        choices=("open", "closed", "unknown"),
        default="closed",
    )
    parser.add_argument(
        "--front-axis",
        choices=("+X", "-X", "+Y", "-Y"),
        default="+X",
    )
    parser.add_argument("--resolution", type=int, default=1024)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--review-json", type=Path)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def link_exclusively(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> None:
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def import_source_locked(
    source: Path,
) -> tuple[list[bpy.types.Object], list[bpy.types.Object]]:
    locked = bpy.data.collections.new("00_SOURCE_LOCKED_READ_ONLY")
    bpy.context.scene.collection.children.link(locked)
    evaluation = bpy.data.collections.new("10_GEOMETRY_EVALUATION_DUPLICATES")
    bpy.context.scene.collection.children.link(evaluation)

    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    source_meshes = [obj for obj in imported if obj.type == "MESH"]
    if not source_meshes:
        raise RuntimeError("Imported GLB contains no mesh objects.")

    for obj in imported:
        link_exclusively(obj, locked)
        obj["bentosaur_source_locked"] = True
        obj.hide_render = True
        obj.hide_set(True)
        obj.hide_select = True

    duplicates: list[bpy.types.Object] = []
    for source_obj in source_meshes:
        duplicate = source_obj.copy()
        duplicate.data = source_obj.data.copy()
        duplicate.animation_data_clear()
        duplicate.parent = None
        duplicate.matrix_world = source_obj.matrix_world.copy()
        duplicate.name = f"EVAL_HD__{source_obj.name}"
        duplicate["bentosaur_evaluation_duplicate"] = True
        if "bentosaur_source_locked" in duplicate:
            del duplicate["bentosaur_source_locked"]
        duplicate.hide_render = False
        duplicate.hide_set(False)
        duplicate.hide_select = False
        evaluation.objects.link(duplicate)
        duplicates.append(duplicate)

    return source_meshes, duplicates


def world_bounds(
    mesh_objects: Iterable[bpy.types.Object],
) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in mesh_objects
        for corner in obj.bound_box
    ]
    if not points:
        raise RuntimeError("Cannot calculate bounds without mesh objects.")
    minimum = Vector(
        (
            min(point.x for point in points),
            min(point.y for point in points),
            min(point.z for point in points),
        )
    )
    maximum = Vector(
        (
            max(point.x for point in points),
            max(point.y for point in points),
            max(point.z for point in points),
        )
    )
    return minimum, maximum


def front_direction(axis: str) -> Vector:
    return {
        "+X": Vector((1.0, 0.0, 0.0)),
        "-X": Vector((-1.0, 0.0, 0.0)),
        "+Y": Vector((0.0, 1.0, 0.0)),
        "-Y": Vector((0.0, -1.0, 0.0)),
    }[axis]


def view_directions(axis: str) -> dict[str, Vector]:
    front = front_direction(axis)
    up = Vector((0.0, 0.0, 1.0))
    character_left = up.cross(front).normalized()
    character_right = -character_left
    return {
        "front": front,
        "left": character_left,
        "back": -front,
        "right": character_right,
        "three_quarter_left": (
            front + character_left + up * 0.08
        ).normalized(),
        "three_quarter_right": (
            front + character_right + up * 0.08
        ).normalized(),
    }


def create_clay_material() -> bpy.types.Material:
    material = bpy.data.materials.new("VG03_NEUTRAL_CLAY")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (
        0.24,
        0.285,
        0.27,
        1.0,
    )
    principled.inputs["Metallic"].default_value = 0.0
    principled.inputs["Roughness"].default_value = 0.82
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.22
    if "Coat Weight" in principled.inputs:
        principled.inputs["Coat Weight"].default_value = 0.0
    return material


def assign_clay_material(
    mesh_objects: Iterable[bpy.types.Object],
    clay: bpy.types.Material,
) -> None:
    for obj in mesh_objects:
        if not obj.data.materials:
            obj.data.materials.append(clay)
            continue
        for index in range(len(obj.data.materials)):
            obj.data.materials[index] = clay


def create_background_material() -> bpy.types.Material:
    material = bpy.data.materials.new("VG03_GROUND")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (
        0.055,
        0.065,
        0.078,
        1.0,
    )
    principled.inputs["Roughness"].default_value = 0.95
    return material


def create_world() -> bpy.types.World:
    world = bpy.data.worlds.new("VG03_NEUTRAL_WORLD")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (
        0.035,
        0.042,
        0.052,
        1.0,
    )
    background.inputs["Strength"].default_value = 0.12
    bpy.context.scene.world = world
    return world


def create_area_light(
    name: str,
    energy: float,
    size: float,
    color: tuple[float, float, float],
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_lights(scale: float) -> dict[str, bpy.types.Object]:
    energy_scale = max(scale * scale, 0.01)
    return {
        "key": create_area_light(
            "VG03_KEY",
            245.0 * energy_scale,
            scale * 1.9,
            (1.0, 0.91, 0.80),
        ),
        "fill": create_area_light(
            "VG03_FILL",
            82.0 * energy_scale,
            scale * 2.5,
            (0.72, 0.84, 1.0),
        ),
        "rim": create_area_light(
            "VG03_RIM",
            175.0 * energy_scale,
            scale * 1.6,
            (0.82, 0.90, 1.0),
        ),
        "top": create_area_light(
            "VG03_TOP",
            62.0 * energy_scale,
            scale * 2.0,
            (1.0, 0.96, 0.88),
        ),
    }


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


def place_camera_and_lights(
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    target: Vector,
    direction: Vector,
    distance: float,
    scale: float,
) -> None:
    view = direction.normalized()
    up = Vector((0.0, 0.0, 1.0))
    right = view.cross(up)
    if right.length < 0.001:
        right = Vector((0.0, 1.0, 0.0))
    right.normalize()

    camera.location = target + view * distance
    point_at(camera, target)

    lights["key"].location = (
        target
        + view * distance * 0.48
        - right * scale * 1.30
        + up * scale * 1.45
    )
    lights["fill"].location = (
        target
        + view * distance * 0.36
        + right * scale * 1.55
        + up * scale * 0.35
    )
    lights["rim"].location = (
        target
        - view * distance * 0.46
        + right * scale * 0.50
        + up * scale * 1.05
    )
    lights["top"].location = target + up * scale * 2.7
    for light in lights.values():
        point_at(light, target)


def create_camera() -> bpy.types.Object:
    data = bpy.data.cameras.new("VG03_ORTHOGRAPHIC_CAMERA")
    data.type = "ORTHO"
    data.lens = 70.0
    data.dof.use_dof = False
    camera = bpy.data.objects.new("VG03_ORTHOGRAPHIC_CAMERA", data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    return camera


def create_floor(
    minimum: Vector, center: Vector, scale: float
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(
        size=scale * 8.0,
        location=(
            center.x,
            center.y,
            minimum.z - scale * 0.008,
        ),
    )
    floor = bpy.context.active_object
    floor.name = "VG03_NEUTRAL_GROUND"
    floor.data.materials.append(create_background_material())
    return floor


def configure_render(resolution: int, samples: int) -> None:
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filter_size = 0.75
    scene.render.use_file_extension = True
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = samples
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "use_gtao"):
        scene.eevee.use_gtao = True
        scene.eevee.gtao_distance = 3.0
        scene.eevee.gtao_factor = 1.2
    try:
        scene.view_settings.view_transform = "AgX"
    except (TypeError, ValueError):
        pass
    for look in ("AgX - Medium High Contrast", "AgX - Medium High Contrast"):
        try:
            scene.view_settings.look = look
            break
        except (TypeError, ValueError):
            continue
    scene.view_settings.exposure = -0.35


def render_still(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def feature_target(
    minimum: Vector,
    maximum: Vector,
    ratio: tuple[float, float, float],
) -> Vector:
    dimensions = maximum - minimum
    return Vector(
        (
            minimum.x + dimensions.x * ratio[0],
            minimum.y + dimensions.y * ratio[1],
            minimum.z + dimensions.z * ratio[2],
        )
    )


def render_views_and_closeups(
    output: Path,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    minimum: Vector,
    maximum: Vector,
    directions: dict[str, Vector],
    expected_mouth: str,
) -> tuple[dict[str, str], dict[str, str]]:
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    scale = max(dimensions)
    distance = max(scale * 3.2, 1.0)

    six_views: dict[str, str] = {}
    camera.data.ortho_scale = scale / 0.87
    for name, direction in directions.items():
        place_camera_and_lights(
            camera, lights, center, direction, distance, scale
        )
        six_views[name] = render_still(
            output / "renders" / "clay" / "six-view" / f"{name}.png"
        )

    # Normalized crop locations are stable for the canonical upright Bentosaur
    # framing. They intentionally include context around each feature so a bad
    # crop cannot hide adjacency, fusion, or silhouette errors.
    mouth_specs = {
        "closed": {
            "muzzle_and_neutral_mouth": {
                "direction": directions["front"],
                "target": (0.55, 0.50, 0.585),
                "scale": 0.43,
            },
            "neutral_mouth_three_quarter": {
                "direction": directions["three_quarter_right"],
                "target": (0.56, 0.50, 0.565),
                "scale": 0.44,
            },
        },
        "open": {
            "muzzle_and_open_mouth": {
                "direction": directions["front"],
                "target": (0.55, 0.50, 0.585),
                "scale": 0.43,
            },
            "mouth_interior_three_quarter": {
                "direction": directions["three_quarter_right"],
                "target": (0.56, 0.50, 0.565),
                "scale": 0.44,
            },
        },
        "unknown": {
            "muzzle_and_mouth": {
                "direction": directions["front"],
                "target": (0.55, 0.50, 0.585),
                "scale": 0.43,
            },
            "mouth_three_quarter": {
                "direction": directions["three_quarter_right"],
                "target": (0.56, 0.50, 0.565),
                "scale": 0.44,
            },
        },
    }
    closeup_specs = {
        "eyes": {
            "direction": directions["front"],
            "target": (0.52, 0.50, 0.705),
            "scale": 0.50,
        },
        **mouth_specs[expected_mouth],
        "primary_horns": {
            "direction": directions["three_quarter_left"],
            "target": (0.50, 0.50, 0.735),
            "scale": 0.62,
        },
        "frill_and_knobs": {
            "direction": directions["front"],
            "target": (0.48, 0.50, 0.735),
            "scale": 0.72,
        },
        "hands_and_fingers": {
            "direction": directions["front"],
            "target": (0.55, 0.50, 0.390),
            "scale": 0.62,
        },
        "feet_and_toes": {
            "direction": directions["front"],
            "target": (0.50, 0.50, 0.155),
            "scale": 0.50,
        },
        "tail_side": {
            "direction": directions["left"],
            "target": (0.28, 0.50, 0.34),
            "scale": 0.60,
        },
    }
    closeups: dict[str, str] = {}
    for name, spec in closeup_specs.items():
        target = feature_target(minimum, maximum, spec["target"])
        camera.data.ortho_scale = scale * spec["scale"]
        place_camera_and_lights(
            camera,
            lights,
            target,
            spec["direction"],
            distance,
            scale,
        )
        closeups[name] = render_still(
            output / "renders" / "clay" / "closeups" / f"{name}.png"
        )
    return six_views, closeups


def component_sizes(bm: bmesh.types.BMesh) -> list[int]:
    unseen = set(bm.verts)
    sizes: list[int] = []
    while unseen:
        seed = unseen.pop()
        stack = [seed]
        size = 0
        while stack:
            vertex = stack.pop()
            size += 1
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in unseen:
                    unseen.remove(other)
                    stack.append(other)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def bmesh_diagnostics(
    mesh: bpy.types.Mesh,
    weld_distance: float,
) -> dict[str, object]:
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    raw_components = component_sizes(bm)
    raw = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "loose_edges": sum(not edge.link_faces for edge in bm.edges),
        "loose_vertices": sum(not vert.link_faces for vert in bm.verts),
        "connected_components": len(raw_components),
        "largest_component_vertices": raw_components[0]
        if raw_components
        else 0,
    }

    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=weld_distance)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    welded_components = component_sizes(bm)
    area_threshold = max(weld_distance * weld_distance, 1e-18)
    degenerate_faces = sum(
        face.calc_area() <= area_threshold for face in bm.faces
    )
    welded = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "loose_edges": sum(not edge.link_faces for edge in bm.edges),
        "loose_vertices": sum(not vert.link_faces for vert in bm.verts),
        "connected_components": len(welded_components),
        "component_vertex_counts_desc": welded_components[:128],
        "largest_component_vertices": welded_components[0]
        if welded_components
        else 0,
        "degenerate_faces": degenerate_faces,
    }
    bm.free()
    return {"raw": raw, "welded": welded}


def topology_metrics(
    mesh_objects: list[bpy.types.Object],
    dimensions: Vector,
) -> dict[str, object]:
    scale = max(dimensions)
    weld_distance = max(scale * 1e-5, 1e-9)
    rows: list[dict[str, object]] = []
    totals = {
        "mesh_objects": len(mesh_objects),
        "vertices": 0,
        "edges": 0,
        "polygons": 0,
        "evaluated_triangles": 0,
        "triangle_faces": 0,
        "quad_faces": 0,
        "ngons": 0,
        "uv_layers": 0,
        "material_slots": 0,
        "shape_keys": 0,
        "raw_boundary_edges": 0,
        "raw_non_manifold_edges": 0,
        "welded_vertices": 0,
        "welded_edges": 0,
        "welded_faces": 0,
        "welded_boundary_edges": 0,
        "welded_non_manifold_edges": 0,
        "welded_loose_edges": 0,
        "welded_loose_vertices": 0,
        "welded_connected_components": 0,
        "welded_degenerate_faces": 0,
    }
    all_component_sizes: list[int] = []

    for obj in mesh_objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        face_sizes = [len(poly.vertices) for poly in mesh.polygons]
        diagnostics = bmesh_diagnostics(mesh, weld_distance)
        raw = diagnostics["raw"]
        welded = diagnostics["welded"]
        row = {
            "name": obj.name,
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "evaluated_triangles": len(mesh.loop_triangles),
            "triangle_faces": sum(size == 3 for size in face_sizes),
            "quad_faces": sum(size == 4 for size in face_sizes),
            "ngons": sum(size > 4 for size in face_sizes),
            "uv_layers": len(mesh.uv_layers),
            "material_slots": len(obj.material_slots),
            "vertex_groups": len(obj.vertex_groups),
            "shape_keys": (
                len(mesh.shape_keys.key_blocks) if mesh.shape_keys else 0
            ),
            "analysis": diagnostics,
        }
        rows.append(row)

        totals["vertices"] += row["vertices"]
        totals["edges"] += row["edges"]
        totals["polygons"] += row["polygons"]
        totals["evaluated_triangles"] += row["evaluated_triangles"]
        totals["triangle_faces"] += row["triangle_faces"]
        totals["quad_faces"] += row["quad_faces"]
        totals["ngons"] += row["ngons"]
        totals["uv_layers"] += row["uv_layers"]
        totals["material_slots"] += row["material_slots"]
        totals["shape_keys"] += row["shape_keys"]
        totals["raw_boundary_edges"] += raw["boundary_edges"]
        totals["raw_non_manifold_edges"] += raw["non_manifold_edges"]
        totals["welded_vertices"] += welded["vertices"]
        totals["welded_edges"] += welded["edges"]
        totals["welded_faces"] += welded["faces"]
        totals["welded_boundary_edges"] += welded["boundary_edges"]
        totals["welded_non_manifold_edges"] += welded[
            "non_manifold_edges"
        ]
        totals["welded_loose_edges"] += welded["loose_edges"]
        totals["welded_loose_vertices"] += welded["loose_vertices"]
        totals["welded_connected_components"] += welded[
            "connected_components"
        ]
        totals["welded_degenerate_faces"] += welded["degenerate_faces"]
        all_component_sizes.extend(welded["component_vertex_counts_desc"])

    all_component_sizes.sort(reverse=True)
    welded_edges = max(totals["welded_edges"], 1)
    welded_faces = max(totals["welded_faces"], 1)
    welded_vertices = max(totals["welded_vertices"], 1)
    totals["welded_boundary_edge_ratio"] = (
        totals["welded_boundary_edges"] / welded_edges
    )
    totals["welded_non_manifold_edge_ratio"] = (
        totals["welded_non_manifold_edges"] / welded_edges
    )
    totals["welded_degenerate_face_ratio"] = (
        totals["welded_degenerate_faces"] / welded_faces
    )
    totals["largest_component_vertex_share"] = (
        all_component_sizes[0] / welded_vertices
        if all_component_sizes
        else 0.0
    )
    totals["component_vertex_counts_desc"] = all_component_sizes[:256]
    totals["weld_distance_world_units"] = weld_distance
    totals["raw_to_welded_vertex_reduction_ratio"] = (
        1.0 - totals["welded_vertices"] / max(totals["vertices"], 1)
    )
    return {"totals": totals, "objects": rows}


def machine_checks(
    topology: dict[str, object], dimensions: Vector
) -> list[dict[str, object]]:
    totals = topology["totals"]
    smallest_to_largest = min(dimensions) / max(max(dimensions), 1e-12)
    values = {
        "mesh_object_count_min": totals["mesh_objects"],
        "evaluated_triangles_min": totals["evaluated_triangles"],
        "evaluated_triangles_max": totals["evaluated_triangles"],
        "welded_boundary_edge_ratio_max": totals[
            "welded_boundary_edge_ratio"
        ],
        "welded_non_manifold_edge_ratio_max": totals[
            "welded_non_manifold_edge_ratio"
        ],
        "welded_boundary_edges_absolute_max": totals[
            "welded_boundary_edges"
        ],
        "welded_non_manifold_edges_absolute_max": totals[
            "welded_non_manifold_edges"
        ],
        "degenerate_face_ratio_max": totals[
            "welded_degenerate_face_ratio"
        ],
        "loose_edges_max": totals["welded_loose_edges"],
        "loose_vertices_max": totals["welded_loose_vertices"],
        "connected_components_max": totals[
            "welded_connected_components"
        ],
        "largest_component_vertex_share_min": totals[
            "largest_component_vertex_share"
        ],
        "smallest_to_largest_bound_ratio_min": smallest_to_largest,
    }
    checks: list[dict[str, object]] = []
    for name, threshold in MACHINE_THRESHOLDS.items():
        value = values[name]
        passed = value >= threshold if name.endswith("_min") else value <= threshold
        checks.append(
            {
                "id": name,
                "value": value,
                "operator": ">=" if name.endswith("_min") else "<=",
                "threshold": threshold,
                "passed": passed,
            }
        )
    return checks


def review_template(
    candidate_id: str,
    expected_mouth: str,
) -> dict[str, object]:
    features = visual_features(expected_mouth)
    blockers = visual_blockers(expected_mouth)
    return {
        "schema_version": 1,
        "candidate_id": candidate_id,
        "reviewer": None,
        "expected_mouth": expected_mouth,
        "score_guide": {
            "0": "missing, fundamentally wrong, or unusable",
            "1": "major visible defects; regeneration is preferable",
            "2": "correct broad volume; repairable during production rebuild",
            "3": "clean, intentional source form with only minor cleanup",
        },
        "scores": {feature: None for feature in features},
        "blockers": {blocker: None for blocker in blockers},
        "notes": {},
    }


def validate_visual_review(
    review_path: Path | None,
    candidate_id: str,
    expected_mouth: str,
) -> tuple[dict[str, object], dict[str, object] | None]:
    if review_path is None:
        return (
            {
                "provided": False,
                "complete": False,
                "passed": False,
                "reason": "No completed visual-review JSON supplied.",
            },
            None,
        )
    path = review_path.expanduser().resolve()
    if not path.is_file():
        return (
            {
                "provided": True,
                "complete": False,
                "passed": False,
                "reason": f"Review file does not exist: {path}",
            },
            None,
        )
    review = json.loads(path.read_text(encoding="utf-8"))
    problems: list[str] = []
    features = visual_features(expected_mouth)
    blocker_names = visual_blockers(expected_mouth)
    if review.get("candidate_id") != candidate_id:
        problems.append("candidate_id does not match")
    if review.get("expected_mouth") != expected_mouth:
        problems.append("expected_mouth does not match evaluator mode")
    scores = review.get("scores", {})
    blockers = review.get("blockers", {})
    for feature in features:
        value = scores.get(feature)
        if not isinstance(value, int) or isinstance(value, bool):
            problems.append(f"score {feature} must be an integer")
        elif not 0 <= value <= VISUAL_THRESHOLDS["score_max"]:
            problems.append(f"score {feature} must be between 0 and 3")
    for blocker in blocker_names:
        if not isinstance(blockers.get(blocker), bool):
            problems.append(f"blocker {blocker} must be true or false")
    if problems:
        return (
            {
                "provided": True,
                "complete": False,
                "passed": False,
                "reason": "; ".join(problems),
            },
            review,
        )

    score_values = [scores[feature] for feature in features]
    average = sum(score_values) / len(score_values)
    below_minimum = [
        feature
        for feature in features
        if scores[feature] < VISUAL_THRESHOLDS["score_min_each"]
    ]
    active_blockers = [
        blocker for blocker in blocker_names if blockers[blocker]
    ]
    passed = (
        not below_minimum
        and average >= VISUAL_THRESHOLDS["score_average_min"]
        and not active_blockers
    )
    return (
        {
            "provided": True,
            "complete": True,
            "passed": passed,
            "average_score": average,
            "below_minimum_features": below_minimum,
            "active_blockers": active_blockers,
            "thresholds": VISUAL_THRESHOLDS,
            "reason": (
                "Visual review passed."
                if passed
                else "Visual review failed one or more exact thresholds."
            ),
        },
        review,
    )


def gate_decision(
    machine: list[dict[str, object]],
    visual: dict[str, object],
    source_role: str,
) -> dict[str, object]:
    failed_machine = [
        check["id"] for check in machine if not check["passed"]
    ]
    if source_role == "placeholder":
        state = "PLACEHOLDER_ONLY_NO_CONTINUATION"
        reason = "Placeholder runs can validate tooling but never unlock work."
    elif failed_machine:
        state = "STOP_GEOMETRY_GATE_FAILED"
        reason = "One or more deterministic geometry thresholds failed."
    elif not visual["complete"]:
        state = "HOLD_FOR_CLAY_REVIEW"
        reason = "Machine checks passed; completed visual review is required."
    elif not visual["passed"]:
        state = "STOP_VISUAL_GATE_FAILED"
        reason = "The completed visual review failed exact thresholds."
    else:
        state = "CONTINUE_TO_PRODUCTION_REBUILD"
        reason = (
            "Machine and visual thresholds passed; retopology, semantic "
            "materials, and production mouth construction may begin."
        )
    continuation = state == "CONTINUE_TO_PRODUCTION_REBUILD"
    return {
        "state": state,
        "reason": reason,
        "automatic_continuation_allowed": continuation,
        "failed_machine_checks": failed_machine,
        "authorized_if_passed": [
            "retopology",
            "semantic_material_authoring",
            "production_eye_construction",
            "production_mouth_cavity_and_tongue_construction",
            "facial_deformation_loop_construction",
        ],
        "still_blocked_even_if_passed": [
            "final_appearance_approval",
            "rigging",
            "skinning",
            "animation",
            "game_integration",
        ],
    }


def create_board(
    magick: str,
    output: Path,
    image_rows: list[tuple[str, str]],
    tile: str,
    geometry: str,
    title: str,
    subtitle: str,
) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    body = output.with_name(f"_{output.stem}_body.png")
    command = [
        magick,
        "montage",
        "-font",
        BOARD_FONT,
        "-pointsize",
        "22",
        "-fill",
        "#E8E0D2",
        "-background",
        "#20252D",
    ]
    for label, image in image_rows:
        command.extend(["-label", label, image])
    command.extend(
        [
            "-tile",
            tile,
            "-geometry",
            geometry,
            str(body),
        ]
    )
    subprocess.run(command, check=True)
    subprocess.run(
        [
            magick,
            str(body),
            "-gravity",
            "north",
            "-background",
            "#20252D",
            "-splice",
            "0x126",
            "-fill",
            "#F2E6CF",
            "-font",
            BOARD_FONT,
            "-pointsize",
            "36",
            "-annotate",
            "+0+24",
            title,
            "-fill",
            "#B8C4D0",
            "-pointsize",
            "20",
            "-annotate",
            "+0+82",
            subtitle,
            str(output),
        ],
        check=True,
    )
    body.unlink(missing_ok=True)
    return str(output)


def create_boards(
    output: Path,
    six_views: dict[str, str],
    closeups: dict[str, str],
    candidate_id: str,
    source_role: str,
    expected_mouth: str,
) -> dict[str, str]:
    magick = shutil.which("magick")
    if not magick:
        return {}
    boards_dir = output / "boards"
    title_prefix = (
        "PLACEHOLDER TOOL VALIDATION"
        if source_role == "placeholder"
        else "VISUAL GATE 03 — HD GEOMETRY"
    )
    six_order = (
        "front",
        "left",
        "back",
        "right",
        "three_quarter_left",
        "three_quarter_right",
    )
    six_board = create_board(
        magick,
        boards_dir / "vg03_hd_clay_six_view.png",
        [(name.replace("_", " ").upper(), six_views[name]) for name in six_order],
        "3x2",
        "520x520+14+14",
        f"{title_prefix} — SIX VIEWS",
        f"{candidate_id} | neutral clay only | source GLB locked | no texture, rig, or animation",
    )
    mouth_closeups = {
        "closed": (
            "muzzle_and_neutral_mouth",
            "neutral_mouth_three_quarter",
        ),
        "open": (
            "muzzle_and_open_mouth",
            "mouth_interior_three_quarter",
        ),
        "unknown": ("muzzle_and_mouth", "mouth_three_quarter"),
    }
    closeup_order = (
        "eyes",
        *mouth_closeups[expected_mouth],
        "primary_horns",
        "frill_and_knobs",
        "hands_and_fingers",
        "feet_and_toes",
        "tail_side",
    )
    closeup_board = create_board(
        magick,
        boards_dir / "vg03_hd_clay_feature_closeups.png",
        [
            (name.replace("_", " ").upper(), closeups[name])
            for name in closeup_order
        ],
        "4x2",
        "440x440+12+12",
        f"{title_prefix} — FEATURE CLOSE-UPS",
        (
            f"eyes | {expected_mouth} mouth | horns | frill | hands | feet | "
            "tail — inspect geometry, not materials"
        ),
    )
    return {"six_view": six_board, "feature_closeups": closeup_board}


def write_readme(
    output: Path,
    candidate_id: str,
    source_role: str,
    expected_mouth: str,
    decision: dict[str, object],
) -> str:
    readme = output / "README.md"
    role_warning = (
        "\n> **PLACEHOLDER ONLY:** This package validates the evaluator against "
        "P1. It is not H3.1 evidence and can never unlock production.\n"
        if source_role == "placeholder"
        else ""
    )
    readme.write_text(
        f"""# Visual Gate 03 — {candidate_id}

**Decision:** `{decision["state"]}`  
**Expected mouth:** `{expected_mouth}`  
**Source role:** `{source_role}`
{role_warning}
This package evaluates untextured geometry only. The source GLB is imported
into `00_SOURCE_LOCKED_READ_ONLY`, hidden from renders, and never modified.
Every render uses deep mesh duplicates.

For the production Bentosaur candidate, `closed` means a relaxed neutral mouth
seam. A mouth cavity, tongue, delighted open smile, and chewing deformation
system are constructed later during the Blender production rebuild.

## Evidence

- `boards/vg03_hd_clay_six_view.png`
- `boards/vg03_hd_clay_feature_closeups.png`
- `topology-metrics.json`
- `gate-policy.json`
- `gate-decision.json`
- `review-template.json`
- `{candidate_id}_source_locked_evaluation.blend`

## Continuation rule

The pipeline may programmatically continue only when:

1. every machine check in `gate-decision.json` passes;
2. every visual feature receives an integer score of at least `2/3`;
3. the visual-feature average is at least `2.5/3`;
4. every named visual blocker is explicitly `false`;
5. this is a real `candidate`, not a `placeholder`.

A pass authorizes retopology, semantic material authoring, controlled eye
construction, and production mouth construction. It does **not** authorize
rigging, skinning, animation, game integration, or final appearance approval.

Score meaning:

- `0`: missing, fundamentally wrong, or unusable;
- `1`: major visible defects; regeneration is preferable;
- `2`: correct broad volume; repairable during production rebuild;
- `3`: clean intentional source form with only minor cleanup.
""",
        encoding="utf-8",
    )
    return str(readme)


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if args.resolution < 512:
        raise ValueError("Geometry-gate resolution must be at least 512.")

    output.mkdir(parents=True, exist_ok=True)
    clear_scene()
    source_meshes, eval_meshes = import_source_locked(source)
    minimum, maximum = world_bounds(eval_meshes)
    dimensions = maximum - minimum
    if not all(math.isfinite(value) and value > 0 for value in dimensions):
        raise RuntimeError(f"Invalid mesh bounds: {list(dimensions)}")

    configure_render(args.resolution, args.samples)
    create_world()
    camera = create_camera()
    scale = max(dimensions)
    lights = create_lights(scale)
    create_floor(minimum, (minimum + maximum) * 0.5, scale)
    clay = create_clay_material()
    assign_clay_material(eval_meshes, clay)

    directions = view_directions(args.front_axis)
    six_views, closeups = render_views_and_closeups(
        output,
        camera,
        lights,
        minimum,
        maximum,
        directions,
        args.expected_mouth,
    )

    topology = topology_metrics(eval_meshes, dimensions)
    machine = machine_checks(topology, dimensions)
    review_status, supplied_review = validate_visual_review(
        args.review_json, args.candidate_id, args.expected_mouth
    )
    decision = gate_decision(machine, review_status, args.source_role)

    topology_path = output / "topology-metrics.json"
    topology_payload = {
        "candidate_id": args.candidate_id,
        "source_sha256": sha256(source),
        "bounds": {
            "minimum": list(minimum),
            "maximum": list(maximum),
            "dimensions": list(dimensions),
        },
        "topology": topology,
        "source_scene": {
            "mesh_objects": len(source_meshes),
            "armatures": sum(
                obj.type == "ARMATURE"
                for obj in bpy.context.scene.objects
                if obj.get("bentosaur_source_locked")
            ),
            "actions": len(bpy.data.actions),
        },
    }
    topology_path.write_text(
        json.dumps(topology_payload, indent=2) + "\n", encoding="utf-8"
    )

    template = review_template(args.candidate_id, args.expected_mouth)
    template_path = output / "review-template.json"
    template_path.write_text(
        json.dumps(template, indent=2) + "\n", encoding="utf-8"
    )

    policy = {
        "gate_id": GATE_ID,
        "version": POLICY_VERSION,
        "purpose": (
            "Decide whether an H3.1 Detailed clay source is strong enough to "
            "justify production retopology/material/mouth work."
        ),
        "machine_thresholds": MACHINE_THRESHOLDS,
        "visual_thresholds": VISUAL_THRESHOLDS,
        "production_expected_mouth": "closed",
        "visual_features": list(visual_features(args.expected_mouth)),
        "visual_blockers": list(visual_blockers(args.expected_mouth)),
        "mouth_mode_contract": {
            "closed": {
                "features": list(MOUTH_FEATURES["closed"]),
                "blockers": list(MOUTH_BLOCKERS["closed"]),
                "does_not_require": [
                    "open_mouth_volume",
                    "mouth_cavity",
                    "tongue",
                ],
            },
            "open": {
                "features": list(MOUTH_FEATURES["open"]),
                "blockers": list(MOUTH_BLOCKERS["open"]),
            },
            "unknown": {
                "features": list(MOUTH_FEATURES["unknown"]),
                "blockers": list(MOUTH_BLOCKERS["unknown"]),
            },
        },
        "policy_notes": [
            "Raw glTF seam splits are reported but gate decisions use a "
            "non-destructive seam-welded diagnostic at 1e-5 of character scale.",
            "A high-density source is not expected to be deformation topology.",
            "Passing this gate authorizes production rebuild work, not rigging.",
        ],
    }
    policy_path = output / "gate-policy.json"
    policy_path.write_text(
        json.dumps(policy, indent=2) + "\n", encoding="utf-8"
    )

    decision_payload = {
        "candidate_id": args.candidate_id,
        "source_role": args.source_role,
        "machine": {
            "passed": all(check["passed"] for check in machine),
            "checks": machine,
        },
        "visual": review_status,
        "decision": decision,
    }
    decision_path = output / "gate-decision.json"
    decision_path.write_text(
        json.dumps(decision_payload, indent=2) + "\n", encoding="utf-8"
    )

    boards = create_boards(
        output,
        six_views,
        closeups,
        args.candidate_id,
        args.source_role,
        args.expected_mouth,
    )
    readme = write_readme(
        output,
        args.candidate_id,
        args.source_role,
        args.expected_mouth,
        decision,
    )

    blend_path = output / (
        f"{args.candidate_id}_source_locked_evaluation.blend"
    )
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    blend_backup = Path(f"{blend_path}1")
    blend_backup.unlink(missing_ok=True)

    manifest = {
        "schema_version": 1,
        "gate_id": GATE_ID,
        "policy_version": POLICY_VERSION,
        "candidate": {
            "id": args.candidate_id,
            "source_role": args.source_role,
            "expected_mouth": args.expected_mouth,
            "front_axis_after_import": args.front_axis,
        },
        "source": {
            "provider": "tripo",
            "format": "glb",
            "absolute_path": str(source),
            "sha256": sha256(source),
            "bytes": source.stat().st_size,
            "locked_collection": "00_SOURCE_LOCKED_READ_ONLY",
            "source_modified": False,
        },
        "render": {
            "engine": bpy.context.scene.render.engine,
            "resolution": [args.resolution, args.resolution],
            "samples_requested": args.samples,
            "material": "neutral clay override",
            "six_views": {
                key: relative_path(Path(value), output)
                for key, value in six_views.items()
            },
            "closeups": {
                key: relative_path(Path(value), output)
                for key, value in closeups.items()
            },
            "boards": {
                key: relative_path(Path(value), output)
                for key, value in boards.items()
            },
        },
        "artifacts": {
            "topology_metrics": relative_path(topology_path, output),
            "gate_policy": relative_path(policy_path, output),
            "gate_decision": relative_path(decision_path, output),
            "review_template": relative_path(template_path, output),
            "supplied_review": (
                str(args.review_json.expanduser().resolve())
                if args.review_json
                else None
            ),
            "readme": relative_path(Path(readme), output),
            "blend": relative_path(blend_path, output),
        },
        "decision": decision,
        "blender_version": bpy.app.version_string,
    }
    if supplied_review is not None:
        manifest["review_snapshot"] = supplied_review
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "status": "success",
                "candidate_id": args.candidate_id,
                "decision": decision["state"],
                "automatic_continuation_allowed": decision[
                    "automatic_continuation_allowed"
                ],
                "manifest": str(manifest_path),
                "boards": boards,
                "source_modified": False,
            }
        )
    )


if __name__ == "__main__":
    main()
