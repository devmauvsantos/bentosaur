"""Inspect a Tripo Smart LowPoly result without changing the source asset.

The script:

* measures boundary components and their positions;
* tests whether merge-by-distance closes them;
* compares low-poly vertices against the high-poly source surface;
* renders boundary edges in magenta for visual diagnosis.

Run with Blender in background mode and pass arguments after ``--``.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


VIEW_DIRECTIONS = {
    "front": Vector((1.0, 0.0, 0.0)),
    "three_quarter_left": Vector((1.0, 1.0, 0.12)).normalized(),
    "left": Vector((0.0, 1.0, 0.0)),
    "three_quarter_right": Vector((1.0, -1.0, 0.12)).normalized(),
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--low", required=True, type=Path)
    parser.add_argument("--high", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=1024)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def import_mesh(path: Path, label: str) -> bpy.types.Object:
    before = set(bpy.context.scene.objects)
    suffix = path.suffix.lower()
    if suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise RuntimeError(f"Unsupported format: {suffix}")
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"{label}: expected one mesh, found {len(meshes)}")
    mesh = meshes[0]
    mesh.name = label
    return mesh


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[i] for point in points) for i in range(3))),
        Vector(tuple(max(point[i] for point in points) for i in range(3))),
    )


def boundary_components(obj: bpy.types.Object) -> list[dict[str, object]]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    boundary = {edge for edge in bm.edges if edge.is_boundary}
    remaining = set(boundary)
    components: list[dict[str, object]] = []
    while remaining:
        seed = remaining.pop()
        component_edges = {seed}
        component_vertices = set(seed.verts)
        frontier = list(seed.verts)
        while frontier:
            vert = frontier.pop()
            for edge in vert.link_edges:
                if edge not in boundary or edge in component_edges:
                    continue
                component_edges.add(edge)
                remaining.discard(edge)
                for linked_vert in edge.verts:
                    if linked_vert not in component_vertices:
                        component_vertices.add(linked_vert)
                        frontier.append(linked_vert)

        world_points = [obj.matrix_world @ vert.co for vert in component_vertices]
        minimum = Vector(
            tuple(min(point[i] for point in world_points) for i in range(3))
        )
        maximum = Vector(
            tuple(max(point[i] for point in world_points) for i in range(3))
        )
        centroid = sum(world_points, Vector()) / len(world_points)
        length = sum(
            (
                obj.matrix_world @ edge.verts[0].co
                - obj.matrix_world @ edge.verts[1].co
            ).length
            for edge in component_edges
        )
        degrees = {
            vert: sum(edge in component_edges for edge in vert.link_edges)
            for vert in component_vertices
        }
        components.append(
            {
                "edge_count": len(component_edges),
                "vertex_count": len(component_vertices),
                "closed_loop": all(degree == 2 for degree in degrees.values()),
                "centroid": list(centroid),
                "minimum": list(minimum),
                "maximum": list(maximum),
                "dimensions": list(maximum - minimum),
                "perimeter": length,
            }
        )
    bm.free()
    return sorted(components, key=lambda row: row["edge_count"], reverse=True)


def merge_test(obj: bpy.types.Object, distance: float) -> dict[str, int | float]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    before_vertices = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=distance)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    result = {
        "distance": distance,
        "vertices_before": before_vertices,
        "vertices_after": len(bm.verts),
        "vertices_merged": before_vertices - len(bm.verts),
        "boundary_edges_after": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges_after": sum(not edge.is_manifold for edge in bm.edges),
    }
    bm.free()
    return result


def percentile(sorted_values: list[float], quantile: float) -> float:
    if not sorted_values:
        return 0.0
    index = min(
        len(sorted_values) - 1,
        max(0, math.ceil(quantile * len(sorted_values)) - 1),
    )
    return sorted_values[index]


def low_to_high_distances(
    low: bpy.types.Object, high: bpy.types.Object
) -> dict[str, float | int]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    high_bvh = BVHTree.FromObject(high, depsgraph)
    distances: list[float] = []
    for vertex in low.data.vertices:
        world = low.matrix_world @ vertex.co
        nearest = high_bvh.find_nearest(world)
        if nearest is not None:
            distances.append(nearest[3])
    distances.sort()
    return {
        "samples": len(distances),
        "mean": sum(distances) / len(distances),
        "median": percentile(distances, 0.5),
        "p95": percentile(distances, 0.95),
        "p99": percentile(distances, 0.99),
        "maximum": distances[-1],
    }


def make_material(
    name: str, color: tuple[float, float, float, float], emission: bool = False
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    if emission:
        shader = nodes.new("ShaderNodeEmission")
        shader.inputs["Color"].default_value = color
        shader.inputs["Strength"].default_value = 3.5
        links.new(shader.outputs["Emission"], output.inputs["Surface"])
    else:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        shader.inputs["Base Color"].default_value = color
        shader.inputs["Roughness"].default_value = 0.62
        links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def create_boundary_overlay(obj: bpy.types.Object) -> bpy.types.Object:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    boundary_edges = [edge for edge in bm.edges if edge.is_boundary]
    curve_data = bpy.data.curves.new("BOUNDARY_EDGES", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 1
    curve_data.bevel_depth = 0.0032
    curve_data.bevel_resolution = 1
    for edge in boundary_edges:
        spline = curve_data.splines.new("POLY")
        spline.points.add(1)
        for index, vert in enumerate(edge.verts):
            world = obj.matrix_world @ vert.co
            spline.points[index].co = (*world, 1.0)
    overlay = bpy.data.objects.new("BOUNDARY_EDGES_MAGENTA", curve_data)
    bpy.context.scene.collection.objects.link(overlay)
    overlay.data.materials.append(
        make_material("BOUNDARY_MAGENTA", (1.0, 0.0, 0.24, 1.0), emission=True)
    )
    bm.free()
    return overlay


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_camera_and_lights(
    center: Vector, dimensions: Vector
) -> tuple[bpy.types.Object, dict[str, bpy.types.Object], float]:
    scale = max(dimensions)
    camera_data = bpy.data.cameras.new("DIAGNOSTIC_CAMERA")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale / 0.875
    camera = bpy.data.objects.new("DIAGNOSTIC_CAMERA", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera

    lights: dict[str, bpy.types.Object] = {}
    for name, energy, size in (
        ("KEY", 850.0 * scale * scale, 2.0 * scale),
        ("FILL", 350.0 * scale * scale, 2.6 * scale),
        ("RIM", 650.0 * scale * scale, 1.5 * scale),
    ):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(light)
        lights[name] = light
    return camera, lights, max(scale * 3.2, 1.0)


def place_view(
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    center: Vector,
    direction: Vector,
    distance: float,
    scale: float,
) -> None:
    view = direction.normalized()
    up = Vector((0.0, 0.0, 1.0))
    right = view.cross(up).normalized()
    camera.location = center + view * distance
    point_at(camera, center)
    lights["KEY"].location = (
        center + view * distance * 0.58 - right * scale * 1.3 + up * scale * 1.35
    )
    lights["FILL"].location = (
        center + view * distance * 0.42 + right * scale * 1.45 + up * scale * 0.35
    )
    lights["RIM"].location = (
        center - view * distance * 0.5 + right * scale * 0.25 + up * scale * 1.2
    )
    for light in lights.values():
        point_at(light, center)


def configure_render(resolution: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("DIAGNOSTIC_WORLD")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.07,
        0.08,
        0.1,
        1.0,
    )
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
    scene.world = world


def main() -> None:
    args = parse_args()
    low_path = args.low.expanduser().resolve()
    high_path = args.high.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    clear_scene()
    low = import_mesh(low_path, "SMART_LOWPOLY_10K_QUAD")
    high = import_mesh(high_path, "HIGH_REFERENCE")
    high.hide_render = True
    high.hide_set(True)

    components = boundary_components(low)
    tests = [
        merge_test(low, distance)
        for distance in (1e-7, 1e-6, 1e-5, 1e-4, 5e-4, 1e-3, 5e-3)
    ]
    deviation = low_to_high_distances(low, high)

    high.hide_set(False)
    high.hide_render = True
    low.data.materials.clear()
    low.data.materials.append(
        make_material("DIAGNOSTIC_CLAY", (0.55, 0.72, 0.65, 1.0))
    )
    create_boundary_overlay(low)
    minimum, maximum = world_bounds(low)
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    scale = max(dimensions)
    camera, lights, distance = create_camera_and_lights(center, dimensions)
    configure_render(args.resolution)

    render_paths: dict[str, str] = {}
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    for name, direction in VIEW_DIRECTIONS.items():
        place_view(camera, lights, center, direction, distance, scale)
        path = render_dir / f"boundary_{name}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        render_paths[name] = str(path)

    report = {
        "source_low": str(low_path),
        "source_high": str(high_path),
        "boundary_edge_count": sum(row["edge_count"] for row in components),
        "boundary_component_count": len(components),
        "boundary_components": components,
        "merge_by_distance_tests": tests,
        "low_vertex_to_high_surface_distance": deviation,
        "normalization_reference": {
            "character_height": dimensions.z,
            "distance_values_are_in_normalized_model_units": True,
        },
        "renders": render_paths,
    }
    report_path = output / "topology_diagnostic.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "topology_diagnostic.blend"))
    print(json.dumps({"status": "success", "report": str(report_path)}))


if __name__ == "__main__":
    main()
