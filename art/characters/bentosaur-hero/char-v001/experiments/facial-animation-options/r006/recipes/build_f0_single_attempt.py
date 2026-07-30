"""Build the one authorized F0 broad-face topology candidate.

This is a bounded production experiment, not an iterative correction loop.
It starts from the exact r004 locked inputs, removes one measured 496-quad
cheek/muzzle mask, preserves the 112-edge outer boundary bit-for-bit, and
authors one continuous all-quad open-mouth shell.

The first two transition rings stay on the original S40 body surface.  This
is the key difference from r005: no skin-support ray is allowed to fall
through the open mouth and hit the Tripo cavity.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from collections import defaultdict, deque
from pathlib import Path
from statistics import mean

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


REPO = Path("/Users/mauvsantos/Workspace/games/Bentosaur")
ROOT = REPO / ".tmp/root/f0_broad_face_r006"
INPUT = ROOT / "work/00_locked_inputs.blend"
OPEN_OUTPUT = ROOT / "work/10_broad_open_topology.blend"
FINAL_OUTPUT = ROOT / "work/20_same_topology_open_neutral.blend"
REPORT = ROOT / "qa/f0_single_attempt_report.json"

BASE_PATH = (
    REPO
    / "art/characters/bentosaur-hero/char-v001/experiments/"
    "facial-animation-options/r005/recipes/"
    "build_checkpoint30_static_transfer.py"
)
spec = importlib.util.spec_from_file_location("f0_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

LOCKED_BODY = "S40_R003_PRODUCTION_BODY_LOCKED"
LOCKED_SOURCE = "TRIPO_VG06_OPEN_SOURCE_LOCKED"
LOCKED_REGION = "TRIPO_VG06_MOUTH_REGION_SOURCE_LOCKED"
BODY = "BENTOSAUR_BODY_CANONICAL_FACE_F0"
TONGUE = "BENTOSAUR_TONGUE_F0"

BOUNDARY_COUNT = 112
SUPPORT_T = (0.17, 0.36, 0.68, 1.0)
WALL_SEGMENTS = 4
WALL_DEPTH = 0.046
BACK_SHRINK = 0.90
CAP_CELLS = 28
CAP_DEPTH = 0.026


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return float(ordered[round((len(ordered) - 1) * fraction)])


def sample_open_polyline(points, edge_count):
    lengths = [
        math.dist(points[index], points[index + 1])
        for index in range(len(points) - 1)
    ]
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


def build_aperture_112():
    trace = base.APERTURE_TRACE_CCW
    upper_right_to_top = sample_open_polyline(trace[3:10], 14)
    top_to_upper_left = [
        (-x, z) for x, z in reversed(upper_right_to_top)
    ]
    upper_left_to_lower_left = sample_open_polyline(trace[15:24], 28)
    lower_left_to_bottom = sample_open_polyline(trace[23:27], 14)
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
    if len(loop) != BOUNDARY_COUNT:
        raise RuntimeError(f"Expected 112 aperture points, got {len(loop)}")
    if base.signed_area(loop) <= 0.0:
        raise RuntimeError("Aperture loop winding drift")
    return loop


def mirror_index(index):
    if 0 <= index <= 28:
        return 28 - index
    return (140 - index) % BOUNDARY_COUNT


def enforce_symmetry(vectors):
    result = [value.copy() for value in vectors]
    for index in range(len(result)):
        partner = mirror_index(index)
        if index > partner:
            continue
        if index == partner:
            result[index].x = 0.0
            continue
        first = result[index]
        second = result[partner]
        magnitude = 0.5 * (abs(first.x) + abs(second.x))
        y = 0.5 * (first.y + second.y)
        z = 0.5 * (first.z + second.z)
        sign = 1.0 if first.x >= 0.0 else -1.0
        result[index] = Vector((sign * magnitude, y, z))
        result[partner] = Vector((-sign * magnitude, y, z))
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


def face_signature(mesh, polygon):
    return tuple(
        sorted(
            tuple(round(float(value), 9) for value in mesh.vertices[index].co)
            for index in polygon.vertices
        )
    )


def broad_faces(mesh):
    candidates = {
        polygon.index
        for polygon in mesh.polygons
        if abs(polygon.center.x) <= 0.135
        and 0.385 <= polygon.center.z <= 0.555
        and polygon.center.y <= -0.18
    }
    face_neighbors = defaultdict(set)
    edge_faces = defaultdict(list)
    for polygon in mesh.polygons:
        if polygon.index not in candidates:
            continue
        for edge in polygon.edge_keys:
            edge_faces[tuple(sorted(edge))].append(polygon.index)
    for linked in edge_faces.values():
        if len(linked) == 2:
            first, second = linked
            face_neighbors[first].add(second)
            face_neighbors[second].add(first)
    components = []
    unseen = set(candidates)
    while unseen:
        start = unseen.pop()
        component = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in face_neighbors[current]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        components.append(component)
    selected = max(components, key=len)
    if len(selected) != 496:
        raise RuntimeError(
            f"Broad mask drift: expected 496 faces, got {len(selected)}"
        )
    return selected


def edge_face_map(mesh):
    result = defaultdict(list)
    for polygon in mesh.polygons:
        for edge in polygon.edge_keys:
            result[tuple(sorted(edge))].append(polygon.index)
    return result


def ordered_boundary(mesh, selected_faces):
    edge_faces = edge_face_map(mesh)
    edges = [
        edge
        for edge, linked in edge_faces.items()
        if sum(face in selected_faces for face in linked) == 1
    ]
    adjacency = defaultdict(list)
    for first, second in edges:
        adjacency[first].append(second)
        adjacency[second].append(first)
    if any(len(values) != 2 for values in adjacency.values()):
        raise RuntimeError("Broad boundary is not one degree-2 cycle")
    start = max(
        adjacency,
        key=lambda index: (
            mesh.vertices[index].co.x,
            -abs(mesh.vertices[index].co.z - 0.475),
        ),
    )
    cycle = [start]
    previous = None
    current = start
    while True:
        options = [value for value in adjacency[current] if value != previous]
        following = options[0]
        if following == start:
            break
        if following in cycle:
            raise RuntimeError("Broad boundary repeats before closing")
        cycle.append(following)
        previous, current = current, following
    if len(cycle) != len(adjacency):
        raise RuntimeError("Broad boundary has multiple cycles")
    points = [
        (mesh.vertices[index].co.x, mesh.vertices[index].co.z)
        for index in cycle
    ]
    if base.signed_area(points) < 0.0:
        cycle = [cycle[0], *reversed(cycle[1:])]

    axis = [
        position
        for position, index in enumerate(cycle)
        if abs(mesh.vertices[index].co.x) <= 1.0e-5
    ]
    top = max(axis, key=lambda value: mesh.vertices[cycle[value]].co.z)
    bottom = min(axis, key=lambda value: mesh.vertices[cycle[value]].co.z)
    if (bottom - top) % len(cycle) != 56:
        raise RuntimeError(
            "Broad boundary is not the expected symmetric 56/56 split"
        )
    upper_right = (top - 14) % len(cycle)
    cycle = cycle[upper_right:] + cycle[:upper_right]
    if len(cycle) != BOUNDARY_COUNT:
        raise RuntimeError(
            f"Expected 112 boundary vertices, got {len(cycle)}"
        )
    if mesh.vertices[cycle[0]].co.x <= 0.0:
        raise RuntimeError("Boundary start is not upper-right")
    return cycle, edges


def directed_edge(polygon, edge):
    values = list(polygon.vertices)
    for index, first in enumerate(values):
        second = values[(index + 1) % len(values)]
        if {first, second} == set(edge):
            return first, second
    raise RuntimeError("Edge missing from face")


def face_aspect(mesh, polygon):
    values = list(polygon.vertices)
    lengths = [
        (
            mesh.vertices[values[index]].co
            - mesh.vertices[values[(index + 1) % len(values)]].co
        ).length
        for index in range(len(values))
    ]
    minimum = min(lengths)
    return math.inf if minimum <= 1.0e-12 else max(lengths) / minimum


def build_report(
    body,
    tongue,
    locked_body,
    locked_source,
    selected_faces,
    outside_before,
    boundary_before,
):
    mesh = body.data
    role_attribute = mesh.attributes["f0_role"]
    roles = defaultdict(set)
    for polygon in mesh.polygons:
        roles[int(role_attribute.data[polygon.index].value)].add(polygon.index)

    outside_after = {
        face_signature(mesh, mesh.polygons[index]) for index in roles[0]
    }
    coordinate_to_index = {
        tuple(round(float(value), 9) for value in vertex.co): vertex.index
        for vertex in mesh.vertices
    }
    final_boundary = [
        coordinate_to_index[
            tuple(round(float(value), 9) for value in coordinate)
        ]
        for coordinate in boundary_before
    ]
    links = edge_face_map(mesh)
    boundary_set = set(final_boundary)
    seam_angles = []
    inconsistent = []
    for edge, linked in links.items():
        if len(linked) != 2:
            continue
        first, second = linked
        if directed_edge(mesh.polygons[first], edge) == directed_edge(
            mesh.polygons[second], edge
        ):
            inconsistent.append((edge, linked))
        if (
            edge[0] in boundary_set
            and edge[1] in boundary_set
            and {int(role_attribute.data[index].value) for index in linked}
            == {0, 1}
        ):
            seam_angles.append(
                math.degrees(
                    mesh.polygons[first].normal.angle(
                        mesh.polygons[second].normal
                    )
                )
            )

    patch_faces = roles[1] | roles[2] | roles[3]
    aspects = [
        face_aspect(mesh, mesh.polygons[index]) for index in patch_faces
    ]
    manifold = base.edge_manifold_report(mesh)
    components = base.connected_face_components(mesh)
    euler = len(mesh.vertices) - len(mesh.edges) + len(mesh.polygons)

    annulus_vertices = {
        index
        for face in roles[1]
        for index in mesh.polygons[face].vertices
    }
    wall_vertices = {
        index
        for face in roles[2]
        for index in mesh.polygons[face].vertices
    }
    aperture = annulus_vertices & wall_vertices
    depsgraph = bpy.context.evaluated_depsgraph_get()
    source_bvh = BVHTree.FromObject(
        locked_source.evaluated_get(depsgraph), depsgraph
    )
    aperture_fit = []
    for index in aperture:
        nearest = source_bvh.find_nearest(mesh.vertices[index].co)
        if nearest is not None:
            aperture_fit.append(float(nearest[3]))

    mesh.calc_loop_triangles()
    triangles = [tuple(item.vertices) for item in mesh.loop_triangles]
    triangle_polygons = [
        int(item.polygon_index) for item in mesh.loop_triangles
    ]
    bvh = BVHTree.FromPolygons(
        [vertex.co for vertex in mesh.vertices],
        triangles,
        all_triangles=True,
    )
    overlaps = []
    seen = set()
    for first, second in bvh.overlap(bvh):
        if first == second:
            continue
        pair = tuple(sorted((int(first), int(second))))
        if pair in seen:
            continue
        seen.add(pair)
        if set(triangles[pair[0]]) & set(triangles[pair[1]]):
            continue
        first_polygon = triangle_polygons[pair[0]]
        second_polygon = triangle_polygons[pair[1]]
        first_role = int(role_attribute.data[first_polygon].value)
        second_role = int(role_attribute.data[second_polygon].value)
        if first_role == 0 and second_role == 0:
            continue
        overlaps.append(
            {
                "triangles": pair,
                "polygons": [first_polygon, second_polygon],
                "roles": [first_role, second_role],
            }
        )

    body_triangles = sum(
        len(polygon.vertices) - 2 for polygon in mesh.polygons
    )
    tongue_triangles = sum(
        len(polygon.vertices) - 2 for polygon in tongue.data.polygons
    )
    boundary_error = max(
        min(
            (vertex.co - coordinate).length for vertex in mesh.vertices
        )
        for coordinate in boundary_before
    )
    report = {
        "status": "f0_open_topology_built",
        "attempt": "r006_f0_single_authorized_attempt",
        "input": {
            "path": str(INPUT),
            "sha256": sha256(INPUT),
            "locked_body": LOCKED_BODY,
            "locked_source": LOCKED_SOURCE,
        },
        "selection": {
            "removed_faces": len(selected_faces),
            "preserved_boundary_vertices": len(boundary_before),
            "predicate": {
                "abs_x_max": 0.135,
                "z_min": 0.385,
                "z_max": 0.555,
                "front_y_max": -0.18,
            },
        },
        "topology": {
            "skin_support_t": SUPPORT_T,
            "skin_quads": len(roles[1]),
            "wall_segments": WALL_SEGMENTS,
            "wall_quads": len(roles[2]),
            "cap_grid": [CAP_CELLS, CAP_CELLS],
            "cap_quads": len(roles[3]),
            "body_vertices": len(mesh.vertices),
            "body_edges": len(mesh.edges),
            "body_faces": len(mesh.polygons),
            "body_all_quads": all(
                len(polygon.vertices) == 4 for polygon in mesh.polygons
            ),
            "body_euler_characteristic": euler,
            "body_face_components": components,
            **manifold,
            "inconsistent_directed_edges": len(inconsistent),
        },
        "preservation": {
            "outside_connectivity_exact": outside_after == outside_before,
            "boundary_coordinate_max_error": boundary_error,
        },
        "quality": {
            "patch_aspect_mean": mean(aspects),
            "patch_aspect_p95": percentile(aspects, 0.95),
            "patch_aspect_max": max(aspects),
            "seam_edges": len(seam_angles),
            "seam_normal_mean_deg": mean(seam_angles),
            "seam_normal_p95_deg": percentile(seam_angles, 0.95),
            "seam_normal_max_deg": max(seam_angles),
            "patch_involved_vertex_disjoint_overlap_pairs": len(overlaps),
            "overlap_examples": overlaps[:30],
        },
        "source_fit": {
            "aperture_vertices": len(aperture_fit),
            "aperture_mean": mean(aperture_fit),
            "aperture_p95": percentile(aperture_fit, 0.95),
            "aperture_max": max(aperture_fit),
        },
        "render_budget": {
            "body_triangles": body_triangles,
            "tongue_triangles": tongue_triangles,
            "candidate_triangles": body_triangles + tongue_triangles,
            "working_limit": 24000,
        },
        "scope": {
            "paid_api_used": False,
            "tripo_credits_spent": 0,
            "faceit_run": False,
            "godot_work": False,
            "canonical_files_modified": False,
            "second_attempt_authorized": False,
        },
    }
    blockers = []
    if not report["topology"]["body_all_quads"]:
        blockers.append("body is not all quads")
    if report["topology"]["body_euler_characteristic"] != 2:
        blockers.append("body Euler characteristic is not 2")
    if any(
        report["topology"][key] != 0
        for key in (
            "nonmanifold_edges",
            "boundary_edges",
            "overfull_edges",
            "loose_vertices",
            "inconsistent_directed_edges",
        )
    ):
        blockers.append("body topology integrity gate failed")
    if not report["preservation"]["outside_connectivity_exact"]:
        blockers.append("outside connectivity changed")
    if report["preservation"]["boundary_coordinate_max_error"] > 1.0e-8:
        blockers.append("outer boundary coordinates changed")
    if report["quality"]["seam_normal_p95_deg"] > 30.0:
        blockers.append("seam normal P95 exceeds 30 degrees")
    if report["quality"]["seam_normal_max_deg"] > 60.0:
        blockers.append("seam normal max exceeds 60 degrees")
    if report["quality"]["patch_aspect_p95"] > 6.0:
        blockers.append("patch aspect P95 exceeds 6")
    if report["quality"]["patch_aspect_max"] > 30.0:
        blockers.append("patch aspect max exceeds 30")
    if report["quality"]["patch_involved_vertex_disjoint_overlap_pairs"] > 0:
        blockers.append("patch has vertex-disjoint overlap candidates")
    if report["source_fit"]["aperture_max"] > 0.005:
        blockers.append("aperture source-fit max exceeds 5 mm")
    if report["render_budget"]["candidate_triangles"] > 24000:
        blockers.append("candidate exceeds 24K working triangle limit")
    report["verdict"] = {
        "technical_gate": "pass" if not blockers else "fail",
        "blockers": blockers,
        "next_if_pass": (
            "author same-topology neutral Basis and render expression sweep"
        ),
        "next_if_fail": "freeze this attempt and stop before Faceit",
    }
    return report


def main():
    bpy.ops.wm.open_mainfile(filepath=str(INPUT))
    scene = bpy.context.scene
    locked_body = bpy.data.objects[LOCKED_BODY]
    locked_source = bpy.data.objects[LOCKED_SOURCE]
    locked_region = bpy.data.objects[LOCKED_REGION]
    for obj in (locked_body, locked_source, locked_region):
        obj.hide_select = True
        obj.hide_render = True
        obj["immutable_in_f0_r006"] = True

    body = locked_body.copy()
    body.data = locked_body.data.copy()
    body.name = BODY
    body.data.name = f"{BODY}_MESH"
    body.hide_select = False
    body.hide_render = False
    scene.collection.objects.link(body)
    mesh = body.data

    selected_faces = broad_faces(mesh)
    boundary_cycle, _boundary_edges = ordered_boundary(mesh, selected_faces)
    boundary_set = set(boundary_cycle)
    selected_vertices = {
        index
        for face in selected_faces
        for index in mesh.polygons[face].vertices
    }
    interior = selected_vertices - boundary_set
    outside_before = {
        face_signature(mesh, polygon)
        for polygon in mesh.polygons
        if polygon.index not in selected_faces
    }
    boundary_before = [
        mesh.vertices[index].co.copy() for index in boundary_cycle
    ]

    depsgraph = bpy.context.evaluated_depsgraph_get()
    body_bvh = BVHTree.FromObject(
        locked_body.evaluated_get(depsgraph), depsgraph
    )
    source_bvh = BVHTree.FromObject(
        locked_source.evaluated_get(depsgraph), depsgraph
    )
    aperture_xz = build_aperture_112()
    aperture_positions = enforce_symmetry(
        [
            Vector(
                (
                    x,
                    symmetric_source_lip_y(source_bvh, (x, z)),
                    z,
                )
            )
            for x, z in aperture_xz
        ]
    )

    cavity_material = base.make_material(
        "F0_MOUTH_CAVITY_WARM",
        (0.055, 0.010, 0.014, 1.0),
        0.76,
    )
    mesh.materials.append(cavity_material)
    cavity_material_index = len(mesh.materials) - 1

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    role_layer = bm.faces.layers.int.new("f0_role")
    boundary_verts = [bm.verts[index] for index in boundary_cycle]
    selected_bm_faces = [bm.faces[index] for index in selected_faces]
    interior_bm_verts = [bm.verts[index] for index in interior]
    bmesh.ops.delete(bm, geom=selected_bm_faces, context="FACES")
    remaining = [vertex for vertex in interior_bm_verts if vertex.is_valid]
    if remaining:
        bmesh.ops.delete(bm, geom=remaining, context="VERTS")

    outer_positions = [vertex.co.copy() for vertex in boundary_verts]
    skin_rings = [boundary_verts]
    skin_faces = []
    for ring_t in SUPPORT_T:
        positions = []
        for outer, aperture in zip(outer_positions, aperture_positions):
            x = outer.x * (1.0 - ring_t) + aperture.x * ring_t
            z = outer.z * (1.0 - ring_t) + aperture.z * ring_t
            if ring_t <= 0.36:
                y = base.symmetric_front_y(body_bvh, x, z)
            elif ring_t < 1.0:
                body_y = base.symmetric_front_y(body_bvh, x, z)
                normalized = (ring_t - 0.36) / (1.0 - 0.36)
                influence = base.smoothstep(normalized)
                y = body_y * (1.0 - influence) + aperture.y * influence
            else:
                y = aperture.y
            positions.append(Vector((x, y, z)))
        positions = enforce_symmetry(positions)
        skin_rings.append([bm.verts.new(value) for value in positions])

    for outer_ring, inner_ring in zip(skin_rings, skin_rings[1:]):
        for index in range(BOUNDARY_COUNT):
            following = (index + 1) % BOUNDARY_COUNT
            face = bm.faces.new(
                (
                    outer_ring[index],
                    outer_ring[following],
                    inner_ring[following],
                    inner_ring[index],
                )
            )
            face.material_index = 0
            face.smooth = True
            face[role_layer] = 1
            skin_faces.append(face)

    aperture_ring = skin_rings[-1]
    wall_rings = [aperture_ring]
    wall_faces = []
    mouth_center = Vector((0.0, 0.0, 0.475))
    for segment in range(1, WALL_SEGMENTS + 1):
        fraction = segment / WALL_SEGMENTS
        eased = base.smoothstep(fraction)
        scale = 1.0 - (1.0 - BACK_SHRINK) * eased
        positions = []
        for aperture in aperture_positions:
            x = mouth_center.x + (aperture.x - mouth_center.x) * scale
            z = mouth_center.z + (aperture.z - mouth_center.z) * scale
            y = aperture.y + WALL_DEPTH * fraction
            positions.append(Vector((x, y, z)))
        positions = enforce_symmetry(positions)
        wall_rings.append([bm.verts.new(value) for value in positions])

    for outer_ring, inner_ring in zip(wall_rings, wall_rings[1:]):
        for index in range(BOUNDARY_COUNT):
            following = (index + 1) % BOUNDARY_COUNT
            face = bm.faces.new(
                (
                    outer_ring[index],
                    outer_ring[following],
                    inner_ring[following],
                    inner_ring[index],
                )
            )
            face.material_index = cavity_material_index
            face.smooth = True
            face[role_layer] = 2
            wall_faces.append(face)

    back_loop = wall_rings[-1]
    grid = [
        [None for _column in range(CAP_CELLS + 1)]
        for _row in range(CAP_CELLS + 1)
    ]
    for column in range(CAP_CELLS + 1):
        grid[0][column] = back_loop[28 - column]
        grid[CAP_CELLS][column] = back_loop[56 + column]
    for row in range(CAP_CELLS + 1):
        grid[row][0] = back_loop[28 + row]
        grid[row][CAP_CELLS] = back_loop[-row % BOUNDARY_COUNT]

    top = [grid[0][column].co.copy() for column in range(CAP_CELLS + 1)]
    bottom = [
        grid[CAP_CELLS][column].co.copy()
        for column in range(CAP_CELLS + 1)
    ]
    left = [grid[row][0].co.copy() for row in range(CAP_CELLS + 1)]
    right = [
        grid[row][CAP_CELLS].co.copy()
        for row in range(CAP_CELLS + 1)
    ]
    top_left, top_right = top[0], top[-1]
    bottom_left, bottom_right = bottom[0], bottom[-1]
    for row in range(1, CAP_CELLS):
        v = row / CAP_CELLS
        for column in range(1, CAP_CELLS):
            u = column / CAP_CELLS
            value = (
                top[column] * (1.0 - v)
                + bottom[column] * v
                + left[row] * (1.0 - u)
                + right[row] * u
                - (
                    top_left * ((1.0 - u) * (1.0 - v))
                    + top_right * (u * (1.0 - v))
                    + bottom_left * ((1.0 - u) * v)
                    + bottom_right * (u * v)
                )
            )
            value.y += (
                CAP_DEPTH
                * math.sin(math.pi * u)
                * math.sin(math.pi * v)
            )
            grid[row][column] = bm.verts.new(value)

    for row in range(CAP_CELLS + 1):
        for column in range((CAP_CELLS // 2) + 1):
            mirror_column = CAP_CELLS - column
            first = grid[row][column]
            second = grid[row][mirror_column]
            if first == second:
                first.co.x = 0.0
                continue
            magnitude = 0.5 * (abs(first.co.x) + abs(second.co.x))
            y = 0.5 * (first.co.y + second.co.y)
            z = 0.5 * (first.co.z + second.co.z)
            first.co = (-magnitude, y, z)
            second.co = (magnitude, y, z)

    cap_faces = []
    for row in range(CAP_CELLS):
        for column in range(CAP_CELLS):
            face = bm.faces.new(
                (
                    grid[row][column],
                    grid[row][column + 1],
                    grid[row + 1][column + 1],
                    grid[row + 1][column],
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
    if mean(face.normal.y for face in skin_faces) > 0.0:
        raise RuntimeError("Skin patch winding reversed")

    bm.verts.index_update()
    bm.faces.index_update()
    skin_ring_indices = [
        [vertex.index for vertex in ring] for ring in skin_rings
    ]
    wall_ring_indices = [
        [vertex.index for vertex in ring] for ring in wall_rings
    ]
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    body["pipeline_stage"] = "F0_BROAD_FACE_SINGLE_ATTEMPT"
    body["source_geometry_authority"] = LOCKED_SOURCE
    body["production_body_authority"] = LOCKED_BODY
    body["outer_boundary_preserved"] = True
    body["rigged"] = False
    body["faceit_run"] = False
    body["paid_api_used"] = False

    tongue = base.create_tongue(scene.collection)
    tongue.name = TONGUE
    tongue.data.name = f"{TONGUE}_MESH"

    bpy.ops.wm.save_as_mainfile(filepath=str(OPEN_OUTPUT), copy=True)
    report = build_report(
        body,
        tongue,
        locked_body,
        locked_source,
        selected_faces,
        outside_before,
        boundary_before,
    )
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    if report["verdict"]["technical_gate"] == "pass":
        basis = body.shape_key_add(name="Basis", from_mix=False)
        open_key = body.shape_key_add(
            name="EXPR_DelightedOpen", from_mix=False
        )
        open_key.value = 0.0
        body.active_shape_key_index = 0

        aperture_neutral = []
        for value in aperture_positions:
            target_x = value.x * 0.88
            normalized_x = min(1.0, abs(target_x) / 0.078)
            smile_z = 0.475 + 0.010 * normalized_x**1.6
            vertical = max(-1.0, min(1.0, (value.z - 0.475) / 0.040))
            target_z = smile_z + 0.0018 * vertical
            target_y = (
                base.symmetric_front_y(body_bvh, target_x, target_z) - 0.001
            )
            aperture_neutral.append(
                Vector((target_x, target_y, target_z))
            )
        aperture_neutral = enforce_symmetry(aperture_neutral)

        for ring_index, vertex_indices in enumerate(skin_ring_indices):
            if ring_index == 0:
                continue
            if ring_index == 1:
                influence = 0.0
            elif ring_index == 2:
                influence = 0.12
            elif ring_index == 3:
                influence = 0.48
            else:
                influence = 1.0
            for column, vertex_index in enumerate(vertex_indices):
                if influence <= 0.0:
                    continue
                current = basis.data[vertex_index].co.copy()
                target = aperture_neutral[column]
                basis.data[vertex_index].co = current.lerp(
                    target, influence
                )

        report["shape_keys"] = {
            "basis": "neutral_shallow_smile",
            "open": "EXPR_DelightedOpen",
            "same_vertex_count": len(basis.data) == len(open_key.data),
            "expression_sweep_requested": [0.0, 0.25, 0.5, 0.75, 1.0],
            "faceit_generated": False,
        }
        body["neutral_basis_authored"] = True
        body["open_expression_authored"] = True
        bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_OUTPUT), copy=True)
        report["status"] = "f0_same_topology_open_neutral_built"
        report["final_output"] = str(FINAL_OUTPUT)
    else:
        report["status"] = "f0_open_topology_failed_frozen"
        report["final_output"] = None

    report["open_output"] = str(OPEN_OUTPUT)
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
