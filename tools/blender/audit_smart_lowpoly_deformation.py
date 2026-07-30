"""Read-only deformation-topology audit for the Bentosaur Smart LowPoly FBX.

The source file is only imported into a disposable Blender process. This script
measures symmetry, valence, triangle/quad flow, boundary defects, and local face
quality in semantic deformation zones. It also renders close-up topology plates
where orange edges touch triangles and magenta edges are open boundaries.

Run with Blender in background mode and pass arguments after ``--``.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import statistics
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=1024)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def import_mesh(path: Path) -> bpy.types.Object:
    if path.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    elif path.suffix.lower() in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif path.suffix.lower() == ".blend":
        current = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
        if current != path.resolve():
            bpy.ops.wm.open_mainfile(filepath=str(path))
    else:
        raise RuntimeError(f"Unsupported mesh format: {path.suffix}")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"Expected one mesh, found {len(meshes)}")
    return meshes[0]


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[i] for point in points) for i in range(3))),
        Vector(tuple(max(point[i] for point in points) for i in range(3))),
    )


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = min(
        len(ordered) - 1,
        max(0, math.ceil(quantile * len(ordered)) - 1),
    )
    return ordered[position]


def summarize(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"count": 0, "mean": 0.0, "median": 0.0, "p95": 0.0, "maximum": 0.0}
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p95": percentile(values, 0.95),
        "maximum": max(values),
    }


def in_zone(name: str, point: Vector) -> bool:
    x, y, z = point
    ay = abs(y)
    if name == "face":
        return x >= 0.19 and z >= 0.015 and ay <= 0.255
    if name == "mouth":
        return x >= 0.34 and -0.065 <= z <= 0.065 and ay <= 0.135
    if name == "left_eye":
        return x >= 0.27 and 0.045 <= y <= 0.175 and 0.075 <= z <= 0.225
    if name == "right_eye":
        return x >= 0.27 and -0.175 <= y <= -0.045 and 0.075 <= z <= 0.225
    if name == "left_shoulder":
        return 0.03 <= x <= 0.30 and 0.105 <= y <= 0.225 and -0.18 <= z <= 0.025
    if name == "right_shoulder":
        return 0.03 <= x <= 0.30 and -0.225 <= y <= -0.105 and -0.18 <= z <= 0.025
    if name == "left_elbow":
        return 0.02 <= x <= 0.29 and 0.19 <= y <= 0.315 and -0.27 <= z <= -0.07
    if name == "right_elbow":
        return 0.02 <= x <= 0.29 and -0.315 <= y <= -0.19 and -0.27 <= z <= -0.07
    if name == "left_hip":
        return -0.02 <= x <= 0.27 and 0.055 <= y <= 0.21 and -0.34 <= z <= -0.18
    if name == "right_hip":
        return -0.02 <= x <= 0.27 and -0.21 <= y <= -0.055 and -0.34 <= z <= -0.18
    if name == "left_knee":
        return 0.00 <= x <= 0.30 and 0.07 <= y <= 0.235 and -0.455 <= z <= -0.30
    if name == "right_knee":
        return 0.00 <= x <= 0.30 and -0.235 <= y <= -0.07 and -0.455 <= z <= -0.30
    if name == "tail_base":
        return -0.20 <= x <= 0.035 and ay <= 0.185 and -0.32 <= z <= -0.08
    if name == "tail_mid_tip":
        return x <= -0.16 and ay <= 0.17 and -0.40 <= z <= -0.10
    raise KeyError(name)


ZONE_NAMES = (
    "face",
    "mouth",
    "left_eye",
    "right_eye",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "tail_base",
    "tail_mid_tip",
)


def face_aspect_ratio(face: bmesh.types.BMFace, obj: bpy.types.Object) -> float:
    lengths = [
        (
            obj.matrix_world @ edge.verts[0].co
            - obj.matrix_world @ edge.verts[1].co
        ).length
        for edge in face.edges
    ]
    shortest = min(lengths)
    return max(lengths) / shortest if shortest > 1e-12 else math.inf


def analyze_zones(obj: bpy.types.Object) -> tuple[dict[str, object], dict[str, set[int]]]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    world_vertices = {vert.index: obj.matrix_world @ vert.co for vert in bm.verts}
    face_centers = {
        face.index: sum((world_vertices[v.index] for v in face.verts), Vector())
        / len(face.verts)
        for face in bm.faces
    }
    result: dict[str, object] = {}
    zone_edges: dict[str, set[int]] = {}

    for zone in ZONE_NAMES:
        faces = [face for face in bm.faces if in_zone(zone, face_centers[face.index])]
        face_set = set(faces)
        vertices = {vert for face in faces for vert in face.verts}
        edges = {edge for face in faces for edge in face.edges}
        zone_edges[zone] = {edge.index for edge in edges}
        triangles = [face for face in faces if len(face.verts) == 3]
        quads = [face for face in faces if len(face.verts) == 4]
        boundary_edges = [edge for edge in edges if edge.is_boundary]
        triangle_touch_edges = [
            edge for edge in edges if any(len(face.verts) == 3 for face in edge.link_faces)
        ]
        triangle_touch_vertices = {
            vert for face in triangles for vert in face.verts
        }
        valence = Counter(len(vert.link_edges) for vert in vertices)
        regular_interior = [
            vert
            for vert in vertices
            if not any(edge.is_boundary for edge in vert.link_edges)
            and len(vert.link_edges) == 4
            and all(len(face.verts) == 4 for face in vert.link_faces)
        ]
        aspects = [face_aspect_ratio(face, obj) for face in faces]
        result[zone] = {
            "faces": len(faces),
            "triangles": len(triangles),
            "quads": len(quads),
            "quad_ratio": len(quads) / len(faces) if faces else 0.0,
            "vertices": len(vertices),
            "edges": len(edges),
            "boundary_edges": len(boundary_edges),
            "triangle_touch_edges": len(triangle_touch_edges),
            "triangle_touch_edge_ratio": (
                len(triangle_touch_edges) / len(edges) if edges else 0.0
            ),
            "triangle_touch_vertices": len(triangle_touch_vertices),
            "triangle_touch_vertex_ratio": (
                len(triangle_touch_vertices) / len(vertices) if vertices else 0.0
            ),
            "regular_all_quad_valence4_vertices": len(regular_interior),
            "regular_all_quad_valence4_ratio": (
                len(regular_interior) / len(vertices) if vertices else 0.0
            ),
            "valence_distribution": {
                str(key): value for key, value in sorted(valence.items())
            },
            "face_aspect_ratio": summarize(aspects),
            "faces_aspect_ratio_over_3": sum(value > 3.0 for value in aspects),
            "faces_aspect_ratio_over_5": sum(value > 5.0 for value in aspects),
        }

    bm.free()
    return result, zone_edges


def analyze_symmetry(obj: bpy.types.Object, y_center: float, height: float) -> dict[str, object]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    world = [obj.matrix_world @ vert.co for vert in bm.verts]
    tree = KDTree(len(world))
    for index, point in enumerate(world):
        tree.insert(point, index)
    tree.balance()

    distances: list[float] = []
    matched_valence = 0
    matched_triangle_incidence = 0
    matched_boundary_state = 0
    strict_matches = 0
    tolerance = height * 0.0005
    pairs: list[tuple[int, int, float]] = []
    for index, point in enumerate(world):
        reflected = Vector((point.x, 2.0 * y_center - point.y, point.z))
        _coordinate, other_index, distance = tree.find(reflected)
        distances.append(distance)
        pairs.append((index, other_index, distance))
        if distance <= tolerance:
            strict_matches += 1
            left = bm.verts[index]
            right = bm.verts[other_index]
            matched_valence += len(left.link_edges) == len(right.link_edges)
            matched_triangle_incidence += (
                sum(len(face.verts) == 3 for face in left.link_faces)
                == sum(len(face.verts) == 3 for face in right.link_faces)
            )
            matched_boundary_state += (
                any(edge.is_boundary for edge in left.link_edges)
                == any(edge.is_boundary for edge in right.link_edges)
            )

    strict_denominator = strict_matches or 1
    result = {
        "mirror_plane_y": y_center,
        "distance": summarize(distances),
        "normalized_to_height": {
            key: value / height
            for key, value in summarize(distances).items()
            if key != "count"
        },
        "match_tolerance": tolerance,
        "vertices_matching_within_0_05_percent_height": strict_matches,
        "match_ratio_within_0_05_percent_height": strict_matches / len(world),
        "matched_topology_at_that_tolerance": {
            "same_valence_ratio": matched_valence / strict_denominator,
            "same_triangle_incidence_ratio": (
                matched_triangle_incidence / strict_denominator
            ),
            "same_boundary_state_ratio": matched_boundary_state / strict_denominator,
        },
        "threshold_counts": {
            "within_0_01_percent_height": sum(
                distance <= height * 0.0001 for distance in distances
            ),
            "within_0_05_percent_height": strict_matches,
            "within_0_10_percent_height": sum(
                distance <= height * 0.001 for distance in distances
            ),
            "within_0_20_percent_height": sum(
                distance <= height * 0.002 for distance in distances
            ),
        },
    }
    bm.free()
    return result


def analyze_mouth_depth(obj: bpy.types.Object) -> dict[str, object]:
    points = [
        obj.matrix_world @ vertex.co
        for vertex in obj.data.vertices
        if in_zone("mouth", obj.matrix_world @ vertex.co)
    ]
    x_values = [point.x for point in points]
    front_band = [point for point in points if point.x >= percentile(x_values, 0.8)]
    recessed_band = [point for point in points if point.x <= percentile(x_values, 0.2)]
    return {
        "sample_vertices": len(points),
        "x_depth_distribution": summarize(x_values),
        "front_20_percent_mean_x": (
            statistics.fmean(point.x for point in front_band) if front_band else 0.0
        ),
        "recessed_20_percent_mean_x": (
            statistics.fmean(point.x for point in recessed_band)
            if recessed_band
            else 0.0
        ),
        "front_to_recessed_depth": (
            statistics.fmean(point.x for point in front_band)
            - statistics.fmean(point.x for point in recessed_band)
            if front_band and recessed_band
            else 0.0
        ),
        "note": (
            "This measures geometric depth only; it does not prove production-ready "
            "oral anatomy or animation loops."
        ),
    }


def analyze_connected_shells(obj: bpy.types.Object) -> dict[str, object]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    remaining = set(bm.verts)
    components: list[dict[str, object]] = []
    while remaining:
        seed = remaining.pop()
        vertices = {seed}
        frontier = [seed]
        while frontier:
            vertex = frontier.pop()
            for edge in vertex.link_edges:
                for linked in edge.verts:
                    if linked in remaining:
                        remaining.remove(linked)
                        vertices.add(linked)
                        frontier.append(linked)
        faces = {face for vertex in vertices for face in vertex.link_faces}
        edges = {edge for vertex in vertices for edge in vertex.link_edges}
        points = [obj.matrix_world @ vertex.co for vertex in vertices]
        minimum = Vector(
            tuple(min(point[index] for point in points) for index in range(3))
        )
        maximum = Vector(
            tuple(max(point[index] for point in points) for index in range(3))
        )
        centroid = sum(points, Vector()) / len(points)
        components.append(
            {
                "vertices": len(vertices),
                "edges": len(edges),
                "faces": len(faces),
                "triangles": sum(len(face.verts) == 3 for face in faces),
                "boundary_edges": sum(edge.is_boundary for edge in edges),
                "centroid": list(centroid),
                "minimum": list(minimum),
                "maximum": list(maximum),
                "dimensions": list(maximum - minimum),
            }
        )
    bm.free()
    components.sort(key=lambda row: row["faces"], reverse=True)
    return {
        "count": len(components),
        "largest_shell_face_ratio": (
            components[0]["faces"] / sum(row["faces"] for row in components)
            if components
            else 0.0
        ),
        "shells_with_open_boundaries": sum(
            row["boundary_edges"] > 0 for row in components
        ),
        "components": components,
    }


def material(
    name: str, color: tuple[float, float, float, float], emission: bool = False
) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    nodes = result.node_tree.nodes
    links = result.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    if emission:
        shader = nodes.new("ShaderNodeEmission")
        shader.inputs["Color"].default_value = color
        shader.inputs["Strength"].default_value = 2.0
        links.new(shader.outputs["Emission"], output.inputs["Surface"])
    else:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        shader.inputs["Base Color"].default_value = color
        shader.inputs["Roughness"].default_value = 0.72
        shader.inputs["Metallic"].default_value = 0.0
        links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return result


def create_edge_curves(
    obj: bpy.types.Object,
    zone_edge_indices: set[int],
    thickness: float,
) -> list[bpy.types.Object]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    categories = {
        "QUAD_FLOW": (
            (0.018, 0.055, 0.085, 1.0),
            lambda edge: not edge.is_boundary
            and not any(len(face.verts) == 3 for face in edge.link_faces),
        ),
        "TRIANGLE_TOUCH": (
            (1.0, 0.22, 0.025, 1.0),
            lambda edge: not edge.is_boundary
            and any(len(face.verts) == 3 for face in edge.link_faces),
        ),
        "OPEN_BOUNDARY": (
            (1.0, 0.0, 0.42, 1.0),
            lambda edge: edge.is_boundary,
        ),
    }
    objects: list[bpy.types.Object] = []
    normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
    for category, (color, predicate) in categories.items():
        selected = [
            edge
            for edge in bm.edges
            if edge.index in zone_edge_indices and predicate(edge)
        ]
        if not selected:
            continue
        curve_data = bpy.data.curves.new(category, type="CURVE")
        curve_data.dimensions = "3D"
        curve_data.resolution_u = 1
        curve_data.bevel_depth = thickness * (1.45 if category != "QUAD_FLOW" else 1.0)
        curve_data.bevel_resolution = 0
        for edge in selected:
            spline = curve_data.splines.new("POLY")
            spline.points.add(1)
            for index, vert in enumerate(edge.verts):
                world_normal = (normal_matrix @ vert.normal).normalized()
                world_point = obj.matrix_world @ vert.co + world_normal * thickness * 1.5
                spline.points[index].co = (*world_point, 1.0)
        overlay = bpy.data.objects.new(category, curve_data)
        bpy.context.scene.collection.objects.link(overlay)
        overlay.data.materials.append(material(f"{category}_MAT", color, emission=True))
        objects.append(overlay)
    bm.free()
    return objects


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def configure_scene(resolution: int) -> tuple[bpy.types.Object, list[bpy.types.Object]]:
    world = bpy.data.worlds.new("AUDIT_WORLD")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.064, 0.078, 1.0)
    background.inputs["Strength"].default_value = 0.35

    camera_data = bpy.data.cameras.new("AUDIT_CAMERA")
    camera_data.type = "ORTHO"
    camera = bpy.data.objects.new("AUDIT_CAMERA", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera

    lights: list[bpy.types.Object] = []
    for name, energy, size, location in (
        ("KEY", 700.0, 1.3, (1.5, -1.7, 1.9)),
        ("FILL", 260.0, 1.8, (1.0, 1.8, 0.5)),
        ("RIM", 500.0, 1.1, (-1.4, 0.2, 1.3)),
    ):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(light)
        light.location = location
        point_at(light, Vector((0.0, 0.0, -0.05)))
        lights.append(light)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filter_size = 0.01
    try:
        scene.view_settings.view_transform = "AgX"
    except TypeError:
        pass
    return camera, lights


def render_plate(
    obj: bpy.types.Object,
    camera: bpy.types.Object,
    output: Path,
    zone_edges: set[int],
    target: Vector,
    direction: Vector,
    ortho_scale: float,
) -> str:
    overlays = create_edge_curves(obj, zone_edges, thickness=0.00052)
    camera.data.ortho_scale = ortho_scale
    camera.location = target + direction.normalized() * 2.4
    point_at(camera, target)
    bpy.context.scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    for overlay in overlays:
        bpy.data.objects.remove(overlay, do_unlink=True)
    return str(output)


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    render_dir = args.output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    if args.input.suffix.lower() != ".blend":
        clear_scene()
    obj = import_mesh(args.input)
    obj.data.materials.clear()
    obj.data.materials.append(material("AUDIT_CLAY", (0.70, 0.79, 0.75, 1.0)))

    minimum, maximum = world_bounds(obj)
    dimensions = maximum - minimum
    y_center = (minimum.y + maximum.y) / 2.0
    zones, zone_edges = analyze_zones(obj)
    report = {
        "source": str(args.input),
        "source_is_modified": False,
        "coordinate_convention": {
            "front": "+X",
            "left_right": "+/-Y",
            "up": "+Z",
        },
        "bounds": {
            "minimum": list(minimum),
            "maximum": list(maximum),
            "dimensions": list(dimensions),
        },
        "semantic_zone_definitions_are_heuristic": True,
        "zones": zones,
        "connected_shells": analyze_connected_shells(obj),
        "symmetry": analyze_symmetry(obj, y_center, dimensions.z),
        "mouth_geometry_depth": analyze_mouth_depth(obj),
        "legend": {
            "dark_lines": "edges belonging only to quads in the selected region",
            "orange_lines": "edges touching at least one triangle; quad-loop interruption risk",
            "magenta_lines": "open boundary edges; mesh defect",
        },
        "renders": {},
    }

    camera, _lights = configure_scene(args.resolution)
    render_specs = {
        "mouth_front": (
            "mouth",
            Vector((0.405, y_center, 0.000)),
            Vector((1.0, 0.0, 0.0)),
            0.22,
        ),
        "mouth_three_quarter": (
            "face",
            Vector((0.30, 0.0, 0.145)),
            Vector((1.0, 0.8, 0.05)),
            0.52,
        ),
        "shoulders_front": (
            "face",
            Vector((0.16, y_center, -0.095)),
            Vector((1.0, 0.0, 0.0)),
            0.62,
        ),
        "hips_knees_front": (
            "left_hip",
            Vector((0.13, y_center, -0.325)),
            Vector((1.0, 0.0, 0.0)),
            0.47,
        ),
        "tail_side": (
            "tail_base",
            Vector((-0.15, y_center, -0.235)),
            Vector((0.0, 1.0, 0.0)),
            0.64,
        ),
    }
    render_edge_groups = {
        "shoulders_front": (
            zone_edges["left_shoulder"]
            | zone_edges["right_shoulder"]
            | zone_edges["left_elbow"]
            | zone_edges["right_elbow"]
        ),
        "hips_knees_front": (
            zone_edges["left_hip"]
            | zone_edges["right_hip"]
            | zone_edges["left_knee"]
            | zone_edges["right_knee"]
        ),
        "tail_side": zone_edges["tail_base"] | zone_edges["tail_mid_tip"],
    }
    for name, (zone, target, direction, scale) in render_specs.items():
        edges = render_edge_groups.get(name, zone_edges[zone])
        path = render_dir / f"{name}.png"
        report["renders"][name] = render_plate(
            obj, camera, path, edges, target, direction, scale
        )

    report_path = args.output / "deformation_topology_audit.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output / "deformation_topology_audit.blend"))
    print(json.dumps({"report": str(report_path), "renders": report["renders"]}, indent=2))


if __name__ == "__main__":
    main()
