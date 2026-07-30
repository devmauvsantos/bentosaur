"""Build the single approved a02 Checkpoint 30 true mouth retopology.

The S40 copy loses exactly the locked 320-face facial disk. Its exact ordered
86-vertex outer boundary is preserved and welded to:

* three equal-count skin support rings plus the 86-vertex VG06 aperture;
* seven equal-count recessed cavity-wall segments;
* a 22 x 21 all-quad Coons cap whose 86-edge perimeter is the back loop.

The visible aperture is an explicit right-mid/CCW artist trace of VG06.  No
ellipse, Bezier, Boolean, inferred contour, rig, shape key, or animation is
created. The tongue is a separate closed mesh.
"""

from __future__ import annotations

import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "recipes/build_checkpoint30_static_transfer.py"
spec = importlib.util.spec_from_file_location("cp30_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

CHECKPOINT_20 = ROOT / "work/20_source_mouth_region_extraction.blend"
CHECKPOINT_30 = ROOT / "work/30_TRIPO_OPEN_MOUTH_TRANSFER_STATIC.blend"
CHECKPOINT_A02 = ROOT / "work/30a02_TRIPO_OPEN_MOUTH_TRANSFER_STATIC.blend"
SOURCE_COPY = ROOT / "source/bentosaur_tripo_open_mouth_cp30_static.blend"
REPORT_PATH = ROOT / "qa/checkpoint30_static_transfer_report.json"
REPORT_A02 = ROOT / "qa/checkpoint30_static_transfer_report_a02.json"

SUPPORT_RING_T = (0.18, 0.46, 0.73, 1.0)
WALL_SEGMENTS = 7
WALL_TOTAL_DEPTH = 0.046
BACK_SHRINK = 0.90
CAP_CELLS_U = 22
CAP_CELLS_V = 21
CAP_CENTER_DEPTH = 0.040


def polyline_lengths(points):
    return [
        math.dist(points[index], points[index + 1])
        for index in range(len(points) - 1)
    ]


def sample_open_polyline(points, edge_count):
    """Sample an open trace with exact endpoints and requested edge count."""
    lengths = polyline_lengths(points)
    total = sum(lengths)
    result = []
    for step in range(edge_count + 1):
        target = total * step / edge_count
        running = 0.0
        for index, length in enumerate(lengths):
            if target <= running + length or index == len(lengths) - 1:
                local = (
                    0.0 if length <= 1.0e-12
                    else (target - running) / length
                )
                first = points[index]
                second = points[index + 1]
                result.append(
                    (
                        first[0] * (1.0 - local) + second[0] * local,
                        first[1] * (1.0 - local) + second[1] * local,
                    )
                )
                break
            running += length
    return result


def build_cardinal_aperture_loop():
    trace = base.APERTURE_TRACE_CCW
    # Symmetric 86-edge topology loop, rotated to the upper-right corner:
    # 0 upper-right, 11 top-center, 22 upper-left, 43 lower-left,
    # 54 bottom-center, 65 lower-right.  Top/bottom have 22 edges and
    # left/right have 21, exactly matching the 22x21 cap grid.
    upper_right_to_top = sample_open_polyline(trace[3:10], 11)
    top_to_upper_left = [
        (-x, z) for x, z in reversed(upper_right_to_top)
    ]
    upper_left_to_lower_left = sample_open_polyline(trace[15:24], 21)
    lower_left_to_bottom = sample_open_polyline(trace[23:27], 11)
    bottom_to_lower_right = [
        (-x, z) for x, z in reversed(lower_left_to_bottom)
    ]
    lower_right_to_upper_right = [
        (-x, z) for x, z in reversed(upper_left_to_lower_left)
    ]

    loop = (
        upper_right_to_top[:-1]
        + top_to_upper_left[:-1]
        + upper_left_to_lower_left[:-1]
        + lower_left_to_bottom[:-1]
        + bottom_to_lower_right[:-1]
        + lower_right_to_upper_right[:-1]
    )
    if len(loop) != 86:
        raise RuntimeError(f"Expected 86 aperture points, got {len(loop)}")
    if base.signed_area(loop) <= 0.0:
        raise RuntimeError("Aperture loop is not upper-right/CCW")
    cardinal = {
        "upper_right": loop[0],
        "top_center": loop[11],
        "upper_left": loop[22],
        "lower_left": loop[43],
        "bottom_center": loop[54],
        "lower_right": loop[65],
    }
    return loop, cardinal


def mirrored_loop_index(index):
    if 0 <= index <= 22:
        return 22 - index
    return (108 - index) % 86


def enforce_mirrored_vectors(vectors):
    result = [vector.copy() for vector in vectors]
    for index in range(len(result)):
        mirror = mirrored_loop_index(index)
        if index > mirror:
            continue
        if index == mirror:
            result[index].x = 0.0
            continue
        first = result[index]
        second = result[mirror]
        magnitude = 0.5 * (abs(first.x) + abs(second.x))
        y = 0.5 * (first.y + second.y)
        z = 0.5 * (first.z + second.z)
        first_sign = 1.0 if first.x >= 0.0 else -1.0
        result[index] = Vector((first_sign * magnitude, y, z))
        result[mirror] = Vector((-first_sign * magnitude, y, z))
    return result


def symmetric_source_lip_y(source_bvh, point):
    center_x, center_z = base.MOUTH_CENTER
    direction = Vector(
        (point[0] - center_x, 0.0, point[1] - center_z)
    )
    length = math.hypot(direction.x, direction.z)
    if length > 1.0e-12:
        direction.x /= length
        direction.z /= length
    sample_x = point[0] + direction.x * 0.0024
    sample_z = point[1] + direction.z * 0.0024
    return base.symmetric_front_y(source_bvh, sample_x, sample_z)


def role_face_indices(mesh):
    attribute = mesh.attributes.get("cp30_role")
    if attribute is None:
        raise RuntimeError("cp30_role face attribute missing")
    result = defaultdict(list)
    for polygon in mesh.polygons:
        result[int(attribute.data[polygon.index].value)].append(polygon.index)
    return result


def coordinate_key(vector):
    return tuple(round(float(value), 9) for value in vector)


def face_signature(mesh, polygon):
    return tuple(
        sorted(coordinate_key(mesh.vertices[index].co) for index in polygon.vertices)
    )


def surface_symmetry_error(obj, indices):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(obj.evaluated_get(depsgraph), depsgraph)
    distances = []
    for index in indices:
        point = obj.data.vertices[index].co
        mirrored = Vector((-point.x, point.y, point.z))
        nearest = bvh.find_nearest(mirrored)
        if nearest is not None:
            distances.append(float(nearest[3]))
    return distances


def main():
    bpy.ops.wm.open_mainfile(filepath=str(CHECKPOINT_20))
    locked_body = bpy.data.objects[base.LOCKED_BODY_NAME]
    locked_source = bpy.data.objects[base.LOCKED_SOURCE_NAME]
    locked_region = bpy.data.objects[base.LOCKED_REGION_NAME]
    for obj in (locked_body, locked_source, locked_region):
        obj.hide_select = True
        obj.hide_render = True
        obj["immutable_in_cp30"] = True

    body = locked_body.copy()
    body.data = locked_body.data.copy()
    body.name = base.BODY_NAME
    body.data.name = f"{base.BODY_NAME}_MESH"
    body.hide_select = False
    body.hide_render = False
    bpy.context.scene.collection.objects.link(body)
    mesh = body.data

    selected_faces = base.selected_disk(mesh)
    boundary_cycle, boundary_edges = base.ordered_boundary(
        mesh, selected_faces
    )
    if len(selected_faces) != 320 or len(boundary_cycle) != 86:
        raise RuntimeError(
            f"Locked disk drift: {len(selected_faces)} faces / "
            f"{len(boundary_cycle)} boundary vertices"
        )
    axis_positions = [
        position
        for position, index in enumerate(boundary_cycle)
        if abs(mesh.vertices[index].co.x) <= 1.0e-5
    ]
    if len(axis_positions) < 2:
        raise RuntimeError("Could not locate top/bottom centerline boundary vertices")
    top_position = max(
        axis_positions,
        key=lambda position: mesh.vertices[boundary_cycle[position]].co.z,
    )
    bottom_position = min(
        axis_positions,
        key=lambda position: mesh.vertices[boundary_cycle[position]].co.z,
    )
    if (bottom_position - top_position) % 86 != 43:
        raise RuntimeError(
            "Outer boundary centerline halves are not 43 edges each"
        )
    upper_right_start = (top_position - 11) % 86
    boundary_cycle = (
        boundary_cycle[upper_right_start:]
        + boundary_cycle[:upper_right_start]
    )
    boundary_set = set(boundary_cycle)
    selected_vertices = {
        index
        for face_index in selected_faces
        for index in mesh.polygons[face_index].vertices
    }
    interior_indices = selected_vertices - boundary_set
    if len(interior_indices) != 278:
        raise RuntimeError(
            f"Expected 278 deleted interior vertices, got {len(interior_indices)}"
        )

    outside_face_signatures_before = {
        face_signature(mesh, polygon)
        for polygon in mesh.polygons
        if polygon.index not in selected_faces
    }
    boundary_coordinates_before = [
        mesh.vertices[index].co.copy() for index in boundary_cycle
    ]

    aperture_xz, cardinal_points = build_cardinal_aperture_loop()

    depsgraph = bpy.context.evaluated_depsgraph_get()
    source_bvh = BVHTree.FromObject(
        locked_source.evaluated_get(depsgraph), depsgraph
    )
    body_bvh = BVHTree.FromObject(
        locked_body.evaluated_get(depsgraph), depsgraph
    )
    aperture_positions = enforce_mirrored_vectors(
        [
            Vector((x, symmetric_source_lip_y(source_bvh, (x, z)), z))
            for x, z in aperture_xz
        ]
    )

    cavity_material = base.make_material(
        "CP30_MOUTH_CAVITY_DEEP_WARM",
        (0.055, 0.010, 0.014, 1.0),
        0.76,
    )
    mesh.materials.append(cavity_material)
    cavity_material_index = len(mesh.materials) - 1

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    role_layer = bm.faces.layers.int.get("cp30_role")
    if role_layer is None:
        role_layer = bm.faces.layers.int.new("cp30_role")
    boundary_verts = [bm.verts[index] for index in boundary_cycle]
    selected_bm_faces = [bm.faces[index] for index in selected_faces]
    interior_bm_verts = [bm.verts[index] for index in interior_indices]
    bmesh.ops.delete(bm, geom=selected_bm_faces, context="FACES")
    remaining_interior = [
        vertex for vertex in interior_bm_verts if vertex.is_valid
    ]
    if remaining_interior:
        bmesh.ops.delete(bm, geom=remaining_interior, context="VERTS")

    rings = [boundary_verts]
    annulus_faces = []
    outer_positions = [
        vertex.co.copy() for vertex in boundary_verts
    ]
    for ring_t in SUPPORT_RING_T:
        ring_positions = []
        blend = base.smoothstep(ring_t)
        for index, (outer, aperture) in enumerate(
            zip(outer_positions, aperture_positions)
        ):
            x = outer.x * (1.0 - ring_t) + aperture.x * ring_t
            z = outer.z * (1.0 - ring_t) + aperture.z * ring_t
            if ring_t >= 0.999999:
                y = aperture.y
            else:
                body_y = base.symmetric_front_y(body_bvh, x, z)
                source_y = base.symmetric_front_y(source_bvh, x, z)
                y = body_y * (1.0 - blend) + source_y * blend
            ring_positions.append(Vector((x, y, z)))
        ring_positions = enforce_mirrored_vectors(ring_positions)
        ring = [bm.verts.new(position) for position in ring_positions]
        rings.append(ring)

    for outer_ring, inner_ring in zip(rings, rings[1:]):
        for index in range(86):
            next_index = (index + 1) % 86
            face = bm.faces.new(
                (
                    outer_ring[index],
                    outer_ring[next_index],
                    inner_ring[next_index],
                    inner_ring[index],
                )
            )
            face.material_index = 0
            face.smooth = True
            face[role_layer] = 1
            annulus_faces.append(face)

    aperture_ring = rings[-1]
    wall_rings = [aperture_ring]
    wall_faces = []
    center_x, center_z = base.MOUTH_CENTER
    for segment in range(1, WALL_SEGMENTS + 1):
        wall_t = segment / WALL_SEGMENTS
        eased = base.smoothstep(wall_t)
        scale = 1.0 - (1.0 - BACK_SHRINK) * eased
        ring_positions = []
        for aperture in aperture_positions:
            x = center_x + (aperture.x - center_x) * scale
            z = center_z + (aperture.z - center_z) * scale
            y = aperture.y + WALL_TOTAL_DEPTH * wall_t
            ring_positions.append(Vector((x, y, z)))
        ring_positions = enforce_mirrored_vectors(ring_positions)
        ring = [bm.verts.new(position) for position in ring_positions]
        wall_rings.append(ring)

    for outer_ring, inner_ring in zip(wall_rings, wall_rings[1:]):
        for index in range(86):
            next_index = (index + 1) % 86
            face = bm.faces.new(
                (
                    outer_ring[index],
                    outer_ring[next_index],
                    inner_ring[next_index],
                    inner_ring[index],
                )
            )
            face.material_index = cavity_material_index
            face.smooth = True
            face[role_layer] = 2
            wall_faces.append(face)

    back_loop = wall_rings[-1]
    grid = [
        [None for _i in range(CAP_CELLS_U + 1)]
        for _j in range(CAP_CELLS_V + 1)
    ]
    # Symmetric corner mapping:
    # loop 0 upper-right, 11 top-center, 22 upper-left,
    # 43 lower-left, 54 bottom-center, 65 lower-right.
    for i in range(CAP_CELLS_U + 1):
        grid[0][i] = back_loop[22 - i]  # upper-left -> upper-right
        grid[CAP_CELLS_V][i] = back_loop[43 + i]  # lower-left -> lower-right
    for j in range(CAP_CELLS_V + 1):
        grid[j][0] = back_loop[22 + j]  # upper-left -> lower-left
        grid[j][CAP_CELLS_U] = back_loop[-j % 86]  # upper-right -> lower-right

    top = [grid[0][i].co.copy() for i in range(CAP_CELLS_U + 1)]
    bottom = [
        grid[CAP_CELLS_V][i].co.copy()
        for i in range(CAP_CELLS_U + 1)
    ]
    left = [grid[j][0].co.copy() for j in range(CAP_CELLS_V + 1)]
    right = [
        grid[j][CAP_CELLS_U].co.copy()
        for j in range(CAP_CELLS_V + 1)
    ]
    corner_tl = top[0]
    corner_tr = top[-1]
    corner_bl = bottom[0]
    corner_br = bottom[-1]

    for j in range(1, CAP_CELLS_V):
        v = j / CAP_CELLS_V
        for i in range(1, CAP_CELLS_U):
            u = i / CAP_CELLS_U
            blended = (
                top[i] * (1.0 - v)
                + bottom[i] * v
                + left[j] * (1.0 - u)
                + right[j] * u
                - (
                    corner_tl * ((1.0 - u) * (1.0 - v))
                    + corner_tr * (u * (1.0 - v))
                    + corner_bl * ((1.0 - u) * v)
                    + corner_br * (u * v)
                )
            )
            blended.y += (
                CAP_CENTER_DEPTH
                * math.sin(math.pi * u)
                * math.sin(math.pi * v)
            )
            grid[j][i] = bm.verts.new(blended)

    # Enforce the exact X-mirror pairing of the rectangular cap grid.
    for j in range(CAP_CELLS_V + 1):
        for i in range((CAP_CELLS_U // 2) + 1):
            mirror_i = CAP_CELLS_U - i
            first = grid[j][i]
            second = grid[j][mirror_i]
            if i == mirror_i:
                first.co.x = 0.0
                continue
            magnitude = 0.5 * (abs(first.co.x) + abs(second.co.x))
            y = 0.5 * (first.co.y + second.co.y)
            z = 0.5 * (first.co.z + second.co.z)
            first.co = (-magnitude, y, z)
            second.co = (magnitude, y, z)

    cap_faces = []
    for j in range(CAP_CELLS_V):
        for i in range(CAP_CELLS_U):
            face = bm.faces.new(
                (
                    grid[j][i],
                    grid[j][i + 1],
                    grid[j + 1][i + 1],
                    grid[j + 1][i],
                )
            )
            face.material_index = cavity_material_index
            face.smooth = True
            face[role_layer] = 3
            cap_faces.append(face)

    bm.normal_update()
    if mean(face.normal.y for face in cap_faces) > 0.0:
        for face in cap_faces:
            face.normal_flip()
    bm.normal_update()
    if mean(face.normal.y for face in annulus_faces) > 0.0:
        raise RuntimeError("Annulus winding is reversed")

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    body["checkpoint"] = "30_TRIPO_OPEN_MOUTH_TRANSFER_STATIC"
    body["implementation"] = "a02_true_86_column_quad_retopology"
    body["source_geometry_authority"] = base.LOCKED_SOURCE_NAME
    body["production_topology_authority"] = base.LOCKED_BODY_NAME
    body["disk_selection_predicate"] = json.dumps(
        {
            "center_z": base.DISK_CENTER_Z,
            "radius_x": base.DISK_RX,
            "radius_z": base.DISK_RZ,
            "front_y_max": base.DISK_FRONT_Y_MAX,
        },
        sort_keys=True,
    )
    body["source_trace_start_orientation"] = "right-mid_ccw"
    body["topology_loop_start_orientation"] = "upper-right_ccw"
    body["aperture_trace_xz_ccw"] = json.dumps(aperture_xz)
    body["support_ring_t"] = json.dumps(SUPPORT_RING_T)
    body["wall_segments"] = WALL_SEGMENTS
    body["cap_grid_cells"] = f"{CAP_CELLS_U}x{CAP_CELLS_V}"
    body["outer_boundary_preserved"] = True
    body["topology_changed_only_inside_locked_boundary"] = True
    body["rigged"] = False
    body["shape_keys"] = False

    tongue = base.create_tongue(bpy.context.scene.collection)

    roles = role_face_indices(mesh)
    if (
        len(roles[1]) != 344
        or len(roles[2]) != 602
        or len(roles[3]) != 462
    ):
        raise RuntimeError(
            "Role face count drift: "
            f"annulus={len(roles[1])}, wall={len(roles[2])}, "
            f"cap={len(roles[3])}"
        )

    outside_face_signatures_after = {
        face_signature(mesh, mesh.polygons[index]) for index in roles[0]
    }
    outside_connectivity_exact = (
        outside_face_signatures_after == outside_face_signatures_before
    )
    boundary_coordinate_error = 0.0
    for coordinate in boundary_coordinates_before:
        nearest = min(
            (
                (vertex.co - coordinate).length
                for vertex in mesh.vertices
            ),
            default=math.inf,
        )
        boundary_coordinate_error = max(boundary_coordinate_error, nearest)

    patch_face_indices = roles[1] + roles[2] + roles[3]
    patch_vertex_indices = {
        index
        for face_index in patch_face_indices
        for index in mesh.polygons[face_index].vertices
    }
    aspects = base.quad_aspects(mesh, patch_face_indices)
    areas = [mesh.polygons[index].area for index in patch_face_indices]
    manifold = base.edge_manifold_report(mesh)
    components = base.connected_face_components(mesh)
    euler = len(mesh.vertices) - len(mesh.edges) + len(mesh.polygons)

    # The new boundary indices differ after deletion/rebuild. Identify the
    # 86 preserved coordinates, then measure the true outside seam.
    coordinate_to_index = {
        coordinate_key(vertex.co): vertex.index for vertex in mesh.vertices
    }
    final_boundary_indices = [
        coordinate_to_index[coordinate_key(coordinate)]
        for coordinate in boundary_coordinates_before
    ]
    final_edge_faces = base.build_edge_faces(mesh)
    seam_edges = []
    boundary_index_set = set(final_boundary_indices)
    for edge, linked in final_edge_faces.items():
        if (
            edge[0] in boundary_index_set
            and edge[1] in boundary_index_set
            and len(linked) == 2
            and any(index in roles[1] for index in linked)
            and any(index in roles[0] for index in linked)
        ):
            seam_edges.append(edge)
    seam_angles = []
    for edge in seam_edges:
        linked = final_edge_faces[edge]
        patch_face = next(index for index in linked if index in roles[1])
        outside_face = next(index for index in linked if index in roles[0])
        seam_angles.append(
            math.degrees(
                mesh.polygons[patch_face].normal.angle(
                    mesh.polygons[outside_face].normal
                )
            )
        )

    depsgraph.update()
    final_source_bvh = BVHTree.FromObject(
        locked_source.evaluated_get(depsgraph), depsgraph
    )
    annulus_vertex_indices = {
        index
        for face_index in roles[1]
        for index in mesh.polygons[face_index].vertices
    }
    source_fit = []
    for index in annulus_vertex_indices:
        nearest = final_source_bvh.find_nearest(mesh.vertices[index].co)
        if nearest is not None:
            source_fit.append(float(nearest[3]))

    # Aperture is the shared annulus/wall loop.
    annulus_vertices = annulus_vertex_indices
    wall_vertices = {
        index
        for face_index in roles[2]
        for index in mesh.polygons[face_index].vertices
    }
    aperture_indices = annulus_vertices & wall_vertices
    upper_corner_fit = []
    for index in aperture_indices:
        point = mesh.vertices[index].co
        if point.z >= 0.493 or abs(point.x) >= 0.068:
            nearest = final_source_bvh.find_nearest(point)
            if nearest is not None:
                upper_corner_fit.append(float(nearest[3]))

    symmetry = surface_symmetry_error(body, patch_vertex_indices)
    body_triangles = sum(len(face.vertices) - 2 for face in mesh.polygons)
    tongue_triangles = sum(
        len(face.vertices) - 2 for face in tongue.data.polygons
    )

    report = {
        "status": "a02_true_retopology_complete_pending_visual_review",
        "attempt": "a02_single_allowed_correction",
        "a01_verdict": (
            "rejected: radial disk morph collapsed topology and failed "
            "aspect/seam gates"
        ),
        "inputs": {
            "checkpoint_20": {
                "path": str(CHECKPOINT_20),
                "sha256": base.sha256(CHECKPOINT_20),
            },
            "body_object": base.LOCKED_BODY_NAME,
            "source_object": base.LOCKED_SOURCE_NAME,
        },
        "selection": {
            "removed_faces": len(selected_faces),
            "removed_interior_vertices": len(interior_indices),
            "preserved_boundary_vertices": len(boundary_cycle),
            "predicate": {
                "center_z": base.DISK_CENTER_Z,
                "radius_x": base.DISK_RX,
                "radius_z": base.DISK_RZ,
                "front_y_max": base.DISK_FRONT_Y_MAX,
            },
        },
        "authored_transfer": {
            "method": (
                "86-column welded quad annulus + seven-segment cavity wall "
                "+ 22x21 all-quad Coons cap"
            ),
            "source_trace_start_orientation": "right-mid_ccw",
            "topology_loop_start_orientation": "upper-right_ccw",
            "aperture_trace_xz_ccw": aperture_xz,
            "cardinal_indices": {
                "upper_right": 0,
                "top_center": 11,
                "upper_left": 22,
                "lower_left": 43,
                "bottom_center": 54,
                "lower_right": 65,
            },
            "cardinal_points": cardinal_points,
            "support_ring_t": SUPPORT_RING_T,
            "annulus_quads": len(roles[1]),
            "wall_segments": WALL_SEGMENTS,
            "wall_quads": len(roles[2]),
            "back_shrink": BACK_SHRINK,
            "wall_total_depth": WALL_TOTAL_DEPTH,
            "cap_grid_cells": [CAP_CELLS_U, CAP_CELLS_V],
            "cap_quads": len(roles[3]),
            "cap_center_depth": CAP_CENTER_DEPTH,
            "separate_tongue": tongue.name,
            "forbidden_methods_used": [],
        },
        "integrity": {
            "outside_face_connectivity_exact": outside_connectivity_exact,
            "boundary_coordinate_max_error": boundary_coordinate_error,
            "body_vertices": len(mesh.vertices),
            "body_edges": len(mesh.edges),
            "body_faces": len(mesh.polygons),
            "body_all_quads": all(
                len(face.vertices) == 4 for face in mesh.polygons
            ),
            "body_euler_characteristic": euler,
            "body_face_components": components,
            **manifold,
            "zero_area_patch_faces": sum(area <= 1.0e-12 for area in areas),
            "tongue": base.tongue_manifold(tongue.data),
            "surface_symmetry_mean_error": mean(symmetry),
            "surface_symmetry_p95_error": base.percentile(symmetry, 0.95),
            "surface_symmetry_max_error": max(symmetry),
        },
        "topology_quality": {
            "patch_aspect_mean": mean(aspects),
            "patch_aspect_p95": base.percentile(aspects, 0.95),
            "patch_aspect_max": max(aspects),
            "seam_edges_measured": len(seam_angles),
            "seam_normal_angle_mean_deg": mean(seam_angles),
            "seam_normal_angle_p95_deg": base.percentile(
                seam_angles, 0.95
            ),
            "seam_normal_angle_max_deg": max(seam_angles),
        },
        "source_fit": {
            "visible_annulus_vertices": len(source_fit),
            "mean": mean(source_fit),
            "p95": base.percentile(source_fit, 0.95),
            "max": max(source_fit),
            "upper_lip_corner_vertices": len(upper_corner_fit),
            "upper_lip_corner_mean": mean(upper_corner_fit),
            "upper_lip_corner_max": max(upper_corner_fit),
        },
        "render_budget": {
            "body_triangles": body_triangles,
            "tongue_triangles": tongue_triangles,
            "candidate_triangles": body_triangles + tongue_triangles,
            "limit": 24000,
        },
        "scope": {
            "rigging": False,
            "shape_keys": False,
            "animation": False,
            "canonical_files_modified": False,
            "paid_api_used": False,
            "tripo_credits_spent": 0,
            "further_corrections_authorized": False,
        },
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    REPORT_A02.write_text(json.dumps(report, indent=2) + "\n")
    bpy.ops.wm.save_as_mainfile(filepath=str(CHECKPOINT_30), copy=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(CHECKPOINT_A02), copy=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_COPY), copy=True)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
