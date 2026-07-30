"""Build Bentosaur Checkpoint 30: static Tripo-matched open-mouth transfer.

The recipe deliberately edits only a copy of the S40 r003 body contained in
r004 checkpoint 20.  The chosen 320-quad facial disk keeps its complete
connectivity: the outer 86-edge boundary is unchanged, while the 278 interior
vertices are repositioned into a source-conformed lip and a recessed welded
mouth bag.  The aperture is an explicit artist trace of VG06, not a generated
ellipse/Bezier/cutter.  A separate closed tongue is authored as its own mesh.

There is intentionally no rigging, shape key, animation, Boolean, spline, or
canonical-file write in this checkpoint.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict, deque
from pathlib import Path
from statistics import mean

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_20 = ROOT / "work/20_source_mouth_region_extraction.blend"
CHECKPOINT_30 = ROOT / "work/30_TRIPO_OPEN_MOUTH_TRANSFER_STATIC.blend"
SOURCE_COPY = ROOT / "source/bentosaur_tripo_open_mouth_cp30_static.blend"
REPORT_PATH = ROOT / "qa/checkpoint30_static_transfer_report.json"

LOCKED_BODY_NAME = "S40_R003_PRODUCTION_BODY_LOCKED"
LOCKED_SOURCE_NAME = "TRIPO_VG06_OPEN_SOURCE_LOCKED"
LOCKED_REGION_NAME = "TRIPO_VG06_MOUTH_REGION_SOURCE_LOCKED"
BODY_NAME = "BENTOSAUR_BODY_TRIPO_OPEN_MOUTH_CP30"
TONGUE_NAME = "BENTOSAUR_TONGUE_SEPARATE_CLOSED_CP30"

DISK_RX = 0.115
DISK_RZ = 0.078
DISK_CENTER_Z = 0.475
DISK_FRONT_Y_MAX = -0.22
LIP_Q = 0.60
MOUTH_CENTER = (0.0, 0.475)
CAVITY_BACK_Y = -0.284

# Explicit counter-clockwise trace in canonical front X/Z space.  The trace
# starts at the right-side midpoint, follows the raised smiling upper edge
# through the center dip, then returns around the artist-resolved lower lip.
# Values were read from the locked VG06 front/three-quarter reference.
APERTURE_TRACE_CCW = (
    (0.0870, 0.4865),
    (0.0862, 0.4975),
    (0.0820, 0.5075),
    (0.0750, 0.5135),
    (0.0640, 0.5150),
    (0.0520, 0.5120),
    (0.0400, 0.5070),
    (0.0270, 0.5020),
    (0.0140, 0.4985),
    (0.0000, 0.4965),
    (-0.0140, 0.4985),
    (-0.0270, 0.5020),
    (-0.0400, 0.5070),
    (-0.0520, 0.5120),
    (-0.0640, 0.5150),
    (-0.0750, 0.5135),
    (-0.0820, 0.5075),
    (-0.0862, 0.4975),
    (-0.0870, 0.4865),
    (-0.0865, 0.4750),
    (-0.0825, 0.4620),
    (-0.0740, 0.4510),
    (-0.0620, 0.4430),
    (-0.0470, 0.4380),
    (-0.0300, 0.4350),
    (-0.0150, 0.4335),
    (0.0000, 0.4330),
    (0.0150, 0.4335),
    (0.0300, 0.4350),
    (0.0470, 0.4380),
    (0.0620, 0.4430),
    (0.0740, 0.4510),
    (0.0825, 0.4620),
    (0.0865, 0.4750),
)


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
    index = round((len(ordered) - 1) * fraction)
    return float(ordered[index])


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def cross_2d(a, b):
    return a[0] * b[1] - a[1] * b[0]


def signed_area(points):
    return 0.5 * sum(
        points[index][0] * points[(index + 1) % len(points)][1]
        - points[(index + 1) % len(points)][0] * points[index][1]
        for index in range(len(points))
    )


def ray_polygon_radius(points, direction):
    """Return the positive ray distance to a star-shaped polygon."""
    origin = MOUTH_CENTER
    hits = []
    for index, first in enumerate(points):
        second = points[(index + 1) % len(points)]
        segment = (second[0] - first[0], second[1] - first[1])
        denominator = cross_2d(direction, segment)
        if abs(denominator) <= 1.0e-12:
            continue
        relative = (first[0] - origin[0], first[1] - origin[1])
        ray_t = cross_2d(relative, segment) / denominator
        segment_t = cross_2d(relative, direction) / denominator
        if ray_t >= -1.0e-9 and -1.0e-9 <= segment_t <= 1.0 + 1.0e-9:
            hits.append(ray_t)
    positive = [value for value in hits if value > 1.0e-8]
    if not positive:
        raise RuntimeError(f"No polygon ray hit for direction {direction}")
    return min(positive)


def build_edge_faces(mesh):
    edge_faces = defaultdict(list)
    for polygon in mesh.polygons:
        for edge_key in polygon.edge_keys:
            edge_faces[tuple(sorted(edge_key))].append(polygon.index)
    return edge_faces


def selected_disk(mesh):
    selected = set()
    for polygon in mesh.polygons:
        center = polygon.center
        inside = (
            (center.x / DISK_RX) ** 2
            + ((center.z - DISK_CENTER_Z) / DISK_RZ) ** 2
            <= 1.0
        )
        if inside and center.y <= DISK_FRONT_Y_MAX:
            selected.add(polygon.index)
    return selected


def ordered_boundary(mesh, selected_faces):
    edge_faces = build_edge_faces(mesh)
    boundary_edges = [
        edge
        for edge, linked in edge_faces.items()
        if sum(index in selected_faces for index in linked) == 1
    ]
    adjacency = defaultdict(list)
    for first, second in boundary_edges:
        adjacency[first].append(second)
        adjacency[second].append(first)
    if not adjacency or any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise RuntimeError("Facial disk boundary is not one degree-2 loop")

    start = max(
        adjacency,
        key=lambda index: (
            mesh.vertices[index].co.x,
            -abs(mesh.vertices[index].co.z - DISK_CENTER_Z),
        ),
    )
    cycle = [start]
    previous = None
    current = start
    while True:
        options = [
            index for index in adjacency[current] if index != previous
        ]
        if not options:
            raise RuntimeError("Open facial disk boundary")
        next_index = options[0]
        if next_index == start:
            break
        if next_index in cycle:
            raise RuntimeError("Facial disk boundary self-repeats")
        cycle.append(next_index)
        previous, current = current, next_index
    if len(cycle) != len(adjacency):
        raise RuntimeError("Facial disk boundary has multiple cycles")

    points = [
        (mesh.vertices[index].co.x, mesh.vertices[index].co.z)
        for index in cycle
    ]
    if signed_area(points) < 0.0:
        cycle = [cycle[0], *reversed(cycle[1:])]
    start_position = max(
        range(len(cycle)),
        key=lambda position: (
            mesh.vertices[cycle[position]].co.x,
            -abs(mesh.vertices[cycle[position]].co.z - DISK_CENTER_Z),
        ),
    )
    return cycle[start_position:] + cycle[:start_position], boundary_edges


def front_y(bvh, x, z):
    location, _normal, _index, _distance = bvh.ray_cast(
        Vector((x, -0.65, z)), Vector((0.0, 1.0, 0.0))
    )
    if location is None:
        raise RuntimeError(f"Front ray missed at x={x:.6f}, z={z:.6f}")
    return float(location.y)


def symmetric_front_y(bvh, x, z):
    absolute = abs(x)
    return 0.5 * (
        front_y(bvh, absolute, z) + front_y(bvh, -absolute, z)
    )


def make_material(name, color, roughness):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    return material


def create_tongue(collection):
    segments = 32
    latitudes = 12
    scale_x = 0.050
    scale_y = 0.018
    scale_z = 0.026
    center = Vector((0.0, -0.329, 0.461))
    vertices = []
    faces = []

    bottom = len(vertices)
    vertices.append(tuple(center + Vector((0.0, 0.0, -scale_z))))
    rings = []
    for latitude in range(1, latitudes):
        phi = -math.pi * 0.5 + math.pi * latitude / latitudes
        radius = math.cos(phi)
        z_local = scale_z * math.sin(phi)
        ring = []
        for segment in range(segments):
            theta = 2.0 * math.pi * segment / segments
            x_local = scale_x * radius * math.cos(theta)
            y_local = scale_y * radius * math.sin(theta)
            notch = 0.0
            if z_local > 0.0 and abs(x_local) < 0.012:
                notch = (
                    0.0038
                    * (1.0 - abs(x_local) / 0.012)
                    * (z_local / scale_z)
                )
            ring.append(len(vertices))
            vertices.append(
                (
                    center.x + x_local,
                    center.y + y_local,
                    center.z + z_local - notch,
                )
            )
        rings.append(ring)
    top = len(vertices)
    vertices.append(tuple(center + Vector((0.0, 0.0, scale_z - 0.0038))))

    first_ring = rings[0]
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append((bottom, first_ring[next_segment], first_ring[segment]))
    for first_ring, second_ring in zip(rings, rings[1:]):
        for segment in range(segments):
            next_segment = (segment + 1) % segments
            faces.append(
                (
                    first_ring[segment],
                    first_ring[next_segment],
                    second_ring[next_segment],
                    second_ring[segment],
                )
            )
    last_ring = rings[-1]
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append((last_ring[segment], last_ring[next_segment], top))

    mesh = bpy.data.meshes.new(f"{TONGUE_NAME}_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    tongue = bpy.data.objects.new(TONGUE_NAME, mesh)
    collection.objects.link(tongue)
    tongue.data.materials.append(
        make_material("CP30_TONGUE_WARM_CORAL", (0.62, 0.12, 0.13, 1.0), 0.58)
    )
    for polygon in mesh.polygons:
        polygon.use_smooth = True
        polygon.material_index = 0
    tongue["geometry_role"] = "separate_closed_tongue_static_only"
    tongue["centerline_x"] = 0.0
    tongue["rigged"] = False
    tongue["shape_keys"] = False
    return tongue


def connected_face_components(mesh):
    edge_faces = build_edge_faces(mesh)
    neighbors = defaultdict(set)
    for linked in edge_faces.values():
        for face in linked:
            neighbors[face].update(other for other in linked if other != face)
    pending = set(range(len(mesh.polygons)))
    sizes = []
    while pending:
        seed = pending.pop()
        queue = deque([seed])
        size = 1
        while queue:
            current = queue.popleft()
            for neighbor in neighbors[current]:
                if neighbor in pending:
                    pending.remove(neighbor)
                    queue.append(neighbor)
                    size += 1
        sizes.append(size)
    return sorted(sizes, reverse=True)


def edge_manifold_report(mesh):
    counts = defaultdict(int)
    for polygon in mesh.polygons:
        for edge in polygon.edge_keys:
            counts[tuple(sorted(edge))] += 1
    used_vertices = {index for edge in counts for index in edge}
    return {
        "nonmanifold_edges": sum(value != 2 for value in counts.values()),
        "boundary_edges": sum(value == 1 for value in counts.values()),
        "overfull_edges": sum(value > 2 for value in counts.values()),
        "loose_vertices": sum(
            vertex.index not in used_vertices for vertex in mesh.vertices
        ),
    }


def quad_aspects(mesh, face_indices):
    aspects = []
    for index in face_indices:
        polygon = mesh.polygons[index]
        lengths = []
        vertices = list(polygon.vertices)
        for position, first in enumerate(vertices):
            second = vertices[(position + 1) % len(vertices)]
            lengths.append(
                (mesh.vertices[first].co - mesh.vertices[second].co).length
            )
        shortest = min(lengths)
        aspects.append(max(lengths) / shortest if shortest > 1.0e-12 else math.inf)
    return aspects


def symmetry_error(mesh, indices):
    tree = KDTree(len(mesh.vertices))
    for vertex in mesh.vertices:
        tree.insert(vertex.co, vertex.index)
    tree.balance()
    errors = []
    for index in indices:
        point = mesh.vertices[index].co
        mirrored = Vector((-point.x, point.y, point.z))
        _co, _nearest_index, distance = tree.find(mirrored)
        errors.append(distance)
    return errors


def seam_normal_angles(mesh, selected_faces, boundary_edges):
    mesh.calc_loop_triangles()
    edge_faces = build_edge_faces(mesh)
    angles = []
    for edge in boundary_edges:
        linked = edge_faces[tuple(sorted(edge))]
        if len(linked) != 2:
            continue
        selected = [index for index in linked if index in selected_faces]
        outside = [index for index in linked if index not in selected_faces]
        if len(selected) == 1 and len(outside) == 1:
            angle = mesh.polygons[selected[0]].normal.angle(
                mesh.polygons[outside[0]].normal
            )
            angles.append(math.degrees(angle))
    return angles


def tongue_manifold(mesh):
    report = edge_manifold_report(mesh)
    return report | {
        "connected_components": connected_face_components(mesh),
        "euler_characteristic": (
            len(mesh.vertices) - len(mesh.edges) + len(mesh.polygons)
        ),
    }


def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_30.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_COPY.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(CHECKPOINT_20))

    locked_body = bpy.data.objects[LOCKED_BODY_NAME]
    locked_source = bpy.data.objects[LOCKED_SOURCE_NAME]
    locked_region = bpy.data.objects[LOCKED_REGION_NAME]
    for locked in (locked_body, locked_source, locked_region):
        locked.hide_select = True
        locked.hide_render = True
        locked["immutable_in_cp30"] = True

    body = locked_body.copy()
    body.data = locked_body.data.copy()
    body.name = BODY_NAME
    body.data.name = f"{BODY_NAME}_MESH"
    body.hide_select = False
    body.hide_render = False
    bpy.context.scene.collection.objects.link(body)

    selected_faces = selected_disk(body.data)
    boundary_cycle, boundary_edges = ordered_boundary(body.data, selected_faces)
    if len(selected_faces) != 320 or len(boundary_cycle) != 86:
        raise RuntimeError(
            f"Locked disk drift: {len(selected_faces)} faces, "
            f"{len(boundary_cycle)} boundary vertices"
        )
    boundary_set = set(boundary_cycle)
    selected_vertices = {
        index
        for face_index in selected_faces
        for index in body.data.polygons[face_index].vertices
    }
    interior_vertices = selected_vertices - boundary_set
    if len(interior_vertices) != 278:
        raise RuntimeError(
            f"Expected 278 disk interior vertices, got {len(interior_vertices)}"
        )

    before = [vertex.co.copy() for vertex in body.data.vertices]
    boundary_before = {
        index: body.data.vertices[index].co.copy() for index in boundary_cycle
    }
    outside_indices = set(range(len(body.data.vertices))) - interior_vertices

    boundary_points = [
        (body.data.vertices[index].co.x, body.data.vertices[index].co.z)
        for index in boundary_cycle
    ]
    if signed_area(boundary_points) <= 0.0:
        raise RuntimeError("Boundary orientation is not counter-clockwise")
    if signed_area(APERTURE_TRACE_CCW) <= 0.0:
        raise RuntimeError("Aperture trace orientation is not counter-clockwise")

    depsgraph = bpy.context.evaluated_depsgraph_get()
    source_bvh = BVHTree.FromObject(
        locked_source.evaluated_get(depsgraph), depsgraph
    )
    body_bvh = BVHTree.FromObject(
        locked_body.evaluated_get(depsgraph), depsgraph
    )

    q_by_vertex = {}
    target_meta = {}
    for index in interior_vertices:
        point = before[index]
        offset = (point.x - MOUTH_CENTER[0], point.z - MOUTH_CENTER[1])
        radial = math.hypot(*offset)
        if radial <= 1.0e-12:
            direction = (1.0, 0.0)
        else:
            direction = (offset[0] / radial, offset[1] / radial)
        boundary_radius = ray_polygon_radius(boundary_points, direction)
        aperture_radius = ray_polygon_radius(APERTURE_TRACE_CCW, direction)
        q = max(0.0, min(0.999999, radial / boundary_radius))
        q_by_vertex[index] = q

        if q >= LIP_Q:
            interpolation = (q - LIP_Q) / (1.0 - LIP_Q)
            target_radius = (
                aperture_radius * (1.0 - interpolation)
                + boundary_radius * interpolation
            )
            x = MOUTH_CENTER[0] + direction[0] * target_radius
            z = MOUTH_CENTER[1] + direction[1] * target_radius
            source_weight = smoothstep(1.0 - interpolation)
            outward_epsilon = 0.0024 * smoothstep(
                (source_weight - 0.62) / 0.38
            )
            sample_x = x + direction[0] * outward_epsilon
            sample_z = z + direction[1] * outward_epsilon
            source_y = symmetric_front_y(source_bvh, sample_x, sample_z)
            body_y = symmetric_front_y(body_bvh, x, z)
            y = body_y * (1.0 - source_weight) + source_y * source_weight
            role = "lip_support"
        else:
            interpolation = q / LIP_Q
            target_radius = aperture_radius * interpolation
            x = MOUTH_CENTER[0] + direction[0] * target_radius
            z = MOUTH_CENTER[1] + direction[1] * target_radius
            lip_sample_x = (
                MOUTH_CENTER[0]
                + direction[0] * (aperture_radius + 0.0024)
            )
            lip_sample_z = (
                MOUTH_CENTER[1]
                + direction[1] * (aperture_radius + 0.0024)
            )
            lip_y = symmetric_front_y(
                source_bvh, lip_sample_x, lip_sample_z
            )
            lip_weight = smoothstep(interpolation)
            y = (
                CAVITY_BACK_Y * (1.0 - lip_weight)
                + lip_y * lip_weight
            )
            role = "recessed_welded_bag"

        body.data.vertices[index].co = (x, y, z)
        target_meta[index] = {
            "q": q,
            "role": role,
            "target": [x, y, z],
        }

    cavity_material = make_material(
        "CP30_MOUTH_CAVITY_DEEP_WARM",
        (0.055, 0.010, 0.014, 1.0),
        0.76,
    )
    body.data.materials.append(cavity_material)
    cavity_material_index = len(body.data.materials) - 1
    cavity_faces = []
    for face_index in selected_faces:
        polygon = body.data.polygons[face_index]
        values = [
            q_by_vertex.get(index, 1.0) for index in polygon.vertices
        ]
        average_q = sum(values) / len(values)
        if average_q < LIP_Q:
            polygon.material_index = cavity_material_index
            cavity_faces.append(face_index)
        polygon.use_smooth = True

    body.data.update()
    body["checkpoint"] = "30_TRIPO_OPEN_MOUTH_TRANSFER_STATIC"
    body["source_geometry_authority"] = LOCKED_SOURCE_NAME
    body["production_topology_authority"] = LOCKED_BODY_NAME
    body["disk_selection_predicate"] = json.dumps(
        {
            "center_z": DISK_CENTER_Z,
            "radius_x": DISK_RX,
            "radius_z": DISK_RZ,
            "front_y_max": DISK_FRONT_Y_MAX,
        },
        sort_keys=True,
    )
    body["aperture_trace_xz_ccw"] = json.dumps(APERTURE_TRACE_CCW)
    body["lip_q"] = LIP_Q
    body["topology_changed"] = False
    body["rigged"] = False
    body["shape_keys"] = False

    tongue = create_tongue(bpy.context.scene.collection)

    outside_coordinate_error = max(
        (body.data.vertices[index].co - before[index]).length
        for index in outside_indices
    )
    boundary_coordinate_error = max(
        (body.data.vertices[index].co - boundary_before[index]).length
        for index in boundary_cycle
    )
    body_manifold = edge_manifold_report(body.data)
    components = connected_face_components(body.data)
    euler = (
        len(body.data.vertices)
        - len(body.data.edges)
        + len(body.data.polygons)
    )
    aspects = quad_aspects(body.data, selected_faces)
    symmetry = symmetry_error(body.data, selected_vertices)
    seam_angles = seam_normal_angles(
        body.data, selected_faces, boundary_edges
    )

    surface_fit = []
    upper_corner_fit = []
    for index in interior_vertices:
        meta = target_meta[index]
        if meta["q"] < LIP_Q:
            continue
        point = body.data.vertices[index].co
        nearest = source_bvh.find_nearest(point)
        if nearest is not None:
            surface_fit.append(float(nearest[3]))
            if point.z >= 0.493 or abs(point.x) >= 0.068:
                upper_corner_fit.append(float(nearest[3]))

    body_triangles = sum(len(face.vertices) - 2 for face in body.data.polygons)
    tongue_triangles = sum(
        len(face.vertices) - 2 for face in tongue.data.polygons
    )

    report = {
        "status": "single_static_implementation_complete_pending_visual_review",
        "inputs": {
            "checkpoint_20": {
                "path": str(CHECKPOINT_20),
                "sha256": sha256(CHECKPOINT_20),
            },
            "body_object": LOCKED_BODY_NAME,
            "source_object": LOCKED_SOURCE_NAME,
        },
        "selection": {
            "predicate": {
                "center_z": DISK_CENTER_Z,
                "radius_x": DISK_RX,
                "radius_z": DISK_RZ,
                "front_y_max": DISK_FRONT_Y_MAX,
            },
            "faces": len(selected_faces),
            "vertices_total": len(selected_vertices),
            "interior_vertices_repositioned": len(interior_vertices),
            "boundary_vertices_preserved": len(boundary_cycle),
            "boundary_x_range": [
                min(before[index].x for index in boundary_cycle),
                max(before[index].x for index in boundary_cycle),
            ],
            "boundary_z_range": [
                min(before[index].z for index in boundary_cycle),
                max(before[index].z for index in boundary_cycle),
            ],
        },
        "authored_transfer": {
            "method": (
                "topology-preserving localized quad-disk retopositioning "
                "into source-conformed lip and recessed welded bag"
            ),
            "aperture_trace_xz_ccw": APERTURE_TRACE_CCW,
            "lip_q": LIP_Q,
            "support_bands_q": [0.68, 0.76, 0.84, 0.92],
            "cavity_back_y": CAVITY_BACK_Y,
            "cavity_material_faces": len(cavity_faces),
            "separate_tongue": tongue.name,
            "forbidden_methods_used": [],
        },
        "integrity": {
            "outside_coordinate_max_error": outside_coordinate_error,
            "boundary_coordinate_max_error": boundary_coordinate_error,
            "body_vertices": len(body.data.vertices),
            "body_edges": len(body.data.edges),
            "body_faces": len(body.data.polygons),
            "body_all_quads": all(
                len(face.vertices) == 4 for face in body.data.polygons
            ),
            "body_euler_characteristic": euler,
            "body_face_components": components,
            **body_manifold,
            "tongue": tongue_manifold(tongue.data),
            "symmetry_max_error": max(symmetry),
            "symmetry_p95_error": percentile(symmetry, 0.95),
        },
        "topology_quality": {
            "patch_aspect_mean": mean(aspects),
            "patch_aspect_p95": percentile(aspects, 0.95),
            "patch_aspect_max": max(aspects),
            "seam_normal_angle_mean_deg": mean(seam_angles),
            "seam_normal_angle_p95_deg": percentile(seam_angles, 0.95),
            "seam_normal_angle_max_deg": max(seam_angles),
        },
        "source_fit": {
            "visible_skin_vertices": len(surface_fit),
            "mean": mean(surface_fit),
            "p95": percentile(surface_fit, 0.95),
            "max": max(surface_fit),
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
        },
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    bpy.ops.wm.save_as_mainfile(filepath=str(CHECKPOINT_30), copy=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_COPY), copy=True)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
