"""Build an isolated, explicitly paired joint-support-loop candidate.

This is a diagnostic deformation-topology branch only. It starts from the
canonical r003 body, inserts one local all-quad inset ring per side around the
shoulders, hips, and knees, and saves an editable .blend after every operation.
The left and right source-face sets are paired before any edit so the same
operator is applied independently to corresponding components. Original
vertices are restored byte-coordinate-exactly; only newly inserted vertices
are projected to the immutable canonical surface.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree


ROOT = Path(__file__).resolve().parents[1]
STAGES = ROOT / "stages"
QA = ROOT / "qa"
STAGES.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
SOURCE = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/art/characters/"
    "bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/"
    "bentosaur_hero_s40_production_topology_r003.blend"
)
TARGET = "BENTOSAUR_BODY_RETOPO_WIP_R003"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)]


def source_bvh(obj: bpy.types.Object) -> BVHTree:
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    polygons = [list(poly.vertices) for poly in obj.data.polygons]
    return BVHTree.FromPolygons(points, polygons, all_triangles=False)


def topology(obj: bpy.types.Object, reference: BVHTree) -> dict:
    bm_check = bmesh.new()
    bm_check.from_mesh(obj.data)
    bm_check.verts.ensure_lookup_table()
    bm_check.edges.ensure_lookup_table()
    bm_check.faces.ensure_lookup_table()
    points = [obj.matrix_world @ vert.co for vert in bm_check.verts]

    tree = KDTree(len(points))
    for index, point in enumerate(points):
        tree.insert(point, index)
    tree.balance()
    mirror = {}
    errors = []
    for index, point in enumerate(points):
        _, match, distance = tree.find(Vector((-point.x, point.y, point.z)))
        mirror[index] = match
        errors.append(distance)

    edge_keys = {
        tuple(sorted((edge.verts[0].index, edge.verts[1].index)))
        for edge in bm_check.edges
    }
    edge_matches = sum(
        tuple(
            sorted(
                (
                    mirror[edge.verts[0].index],
                    mirror[edge.verts[1].index],
                )
            )
        )
        in edge_keys
        for edge in bm_check.edges
    )
    face_keys = {
        frozenset(vert.index for vert in face.verts) for face in bm_check.faces
    }
    face_matches = sum(
        frozenset(mirror[vert.index] for vert in face.verts) in face_keys
        for face in bm_check.faces
    )

    distances = sorted(
        nearest[3]
        for point in points
        if (nearest := reference.find_nearest(point)) is not None
    )
    remaining = set(bm_check.faces)
    components = 0
    while remaining:
        components += 1
        seed = remaining.pop()
        stack = [seed]
        while stack:
            face = stack.pop()
            neighbors = {
                other
                for edge in face.edges
                for other in edge.link_faces
                if other in remaining
            }
            for other in neighbors:
                remaining.remove(other)
                stack.append(other)

    result = {
        "vertices": len(bm_check.verts),
        "edges": len(bm_check.edges),
        "faces": len(bm_check.faces),
        "triangles": sum(len(face.verts) == 3 for face in bm_check.faces),
        "quads": sum(len(face.verts) == 4 for face in bm_check.faces),
        "ngons": sum(len(face.verts) > 4 for face in bm_check.faces),
        "boundary_edges": sum(edge.is_boundary for edge in bm_check.edges),
        "non_manifold_edges": sum(
            not edge.is_manifold for edge in bm_check.edges
        ),
        "zero_area_faces": sum(
            face.calc_area() <= 1.0e-12 for face in bm_check.faces
        ),
        "zero_length_edges": sum(
            edge.calc_length() <= 1.0e-12 for edge in bm_check.edges
        ),
        "loose_vertices": sum(not vert.link_edges for vert in bm_check.verts),
        "loose_edges": sum(not edge.link_faces for edge in bm_check.edges),
        "connected_face_components": components,
        "euler_characteristic": (
            len(bm_check.verts) - len(bm_check.edges) + len(bm_check.faces)
        ),
        "signed_volume": bm_check.calc_volume(signed=True),
        "symmetry": {
            "within_1e_6_ratio": (
                sum(error <= 1.0e-6 for error in errors) / len(errors)
            ),
            "p95": percentile(errors, 0.95),
            "maximum": max(errors),
            "edge_match_ratio": edge_matches / len(bm_check.edges),
            "face_match_ratio": face_matches / len(bm_check.faces),
        },
        "surface_deviation": {
            "mean": sum(distances) / len(distances),
            "p95": percentile(distances, 0.95),
            "maximum": max(distances),
            "p95_fraction_of_height": (
                percentile(distances, 0.95) / SOURCE_HEIGHT
            ),
        },
    }
    bm_check.free()
    return result


def save(obj: bpy.types.Object, filename: str, operation: str) -> dict:
    path = STAGES / filename
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {path}")
    obj["bentosaur_pipeline_role"] = "paired_joint_deformation_repair_probe"
    obj["bentosaur_operation"] = operation
    obj["bentosaur_production_ready"] = False
    obj["bentosaur_user_approved"] = False
    bpy.ops.wm.save_as_mainfile(filepath=str(path), check_existing=False)
    return {
        "operation": operation,
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "topology": topology(obj, REFERENCE),
    }


def region_components(faces: list[bmesh.types.BMFace]) -> list[int]:
    face_set = set(faces)
    remaining = set(faces)
    sizes = []
    while remaining:
        seed = remaining.pop()
        component = {seed}
        stack = [seed]
        while stack:
            face = stack.pop()
            neighbors = {
                other
                for edge in face.edges
                for other in edge.link_faces
                if other in remaining and other in face_set
            }
            for other in neighbors:
                remaining.remove(other)
                component.add(other)
                stack.append(other)
        sizes.append(len(component))
    return sorted(sizes, reverse=True)


body = bpy.data.objects.get(TARGET)
if body is None or body.type != "MESH":
    raise RuntimeError(f"Canonical body not found: {TARGET}")
source_path = Path(bpy.data.filepath).resolve()
if source_path != SOURCE:
    raise RuntimeError(f"Wrong input file: {source_path}")

REFERENCE = source_bvh(body)
source_world_points = [
    body.matrix_world @ vertex.co for vertex in body.data.vertices
]
SOURCE_HEIGHT = max(point.z for point in source_world_points) - min(
    point.z for point in source_world_points
)
report = {
    "schema_version": "2.0.0",
    "method": "explicit_left_right_paired_local_quad_inset_support_loops",
    "diagnostic_only": True,
    "production_promotion": False,
    "user_approval": False,
    "lineage": {
        "canonical_source": str(SOURCE),
        "canonical_sha256_before": sha256(SOURCE),
        "canonical_object": TARGET,
        "failed_predecessor": str(
            ROOT
            / "failed-branches"
            / "inset-all-regions-run2-asymmetric"
        ),
    },
    "settings": {
        "shoulder": {
            "positive_x": [0.170, 0.320],
            "y": [-0.260, 0.060],
            "z": [0.320, 0.445],
            "thickness": 0.004,
            "semantic_guard": (
                "surface patch within 0.110 of corrected upper-arm bone "
                "segment, positive x >= 0.170, and every selected face vertex "
                "below measured head-neck-blend minimum z=0.470715"
            ),
        },
        "hip_groin": {
            "positive_x": [0.025, 0.235],
            "y": [-0.275, 0.055],
            "z": [0.185, 0.315],
            "thickness": 0.0035,
        },
        "knee": {
            "positive_x": [0.04, 0.295],
            "y": [-0.275, 0.055],
            "z": [0.115, 0.220],
            "thickness": 0.003,
            "semantic_guard": (
                "largest connected selection only; lower bound excludes feet"
            ),
        },
        "projection": "nearest point on immutable canonical r003 body",
        "pairing": (
            "source faces paired by exact mirrored source-vertex topology; "
            "left and right insets executed independently in paired order"
        ),
        "tail_exclusion": (
            "no selected source face may contain a vertex with y > 0.075 "
            "while z < 0.35; final new-vertex audit uses y > 0.09"
        ),
        "mouth_exclusion": "no edits at z > 0.60",
    },
    "steps": {},
    "regions": {},
}

# Exact full-file checkpoint before isolating the body.
report["steps"]["00_canonical_full_copy"] = save(
    body,
    "00_canonical_r003_full_exact_copy.blend",
    "exact full canonical r003 duplicate",
)

for obj in list(bpy.data.objects):
    if obj is not body:
        bpy.data.objects.remove(obj, do_unlink=True)
body.name = "BENTOSAUR_JOINT_REPAIR_CANDIDATE_NOT_APPROVED"
body.data.name = "BENTOSAUR_JOINT_REPAIR_CANDIDATE_MESH"
report["steps"]["05_body_only"] = save(
    body,
    "05_body_only_working_snapshot.blend",
    "body-only working snapshot; mouth references excluded, not integrated",
)

bm = bmesh.new()
bm.from_mesh(body.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
source_vertices = list(bm.verts)
source_faces = list(bm.faces)
source_by_reference = {vert: vert.co.copy() for vert in source_vertices}
original_vertex_count = len(source_vertices)

# Establish immutable source-side mirror maps before any topology operation.
source_points = [body.matrix_world @ vert.co for vert in source_vertices]
source_tree = KDTree(len(source_points))
for index, point in enumerate(source_points):
    source_tree.insert(point, index)
source_tree.balance()
mirror_vertex = {}
mirror_errors = []
for vert, point in zip(source_vertices, source_points):
    _, mirror_index, distance = source_tree.find(
        Vector((-point.x, point.y, point.z))
    )
    mirror_vertex[vert] = source_vertices[mirror_index]
    mirror_errors.append(distance)

face_by_key = {
    frozenset(face.verts): face
    for face in source_faces
}
mirror_face = {}
for face in source_faces:
    key = frozenset(mirror_vertex[vert] for vert in face.verts)
    partner = face_by_key.get(key)
    if partner is None:
        raise RuntimeError(f"Missing mirrored source face for {face.index}")
    mirror_face[face] = partner

report["source_pairing_audit"] = {
    "source_vertices": len(source_vertices),
    "source_faces": len(source_faces),
    "vertex_mirror_p95": percentile(mirror_errors, 0.95),
    "vertex_mirror_maximum": max(mirror_errors),
    "paired_faces": len(mirror_face),
    "all_faces_paired": len(mirror_face) == len(source_faces),
}

all_new_vertices: set[bmesh.types.BMVert] = set()
region_new_vertices: dict[str, set[bmesh.types.BMVert]] = {}


def face_is_tail_safe(face: bmesh.types.BMFace) -> bool:
    return not any(
        (body.matrix_world @ vert.co).y > 0.075
        and (body.matrix_world @ vert.co).z < 0.35
        for vert in face.verts
    )


def project_new(vertices: set[bmesh.types.BMVert], name: str) -> None:
    inverse = body.matrix_world.inverted()
    for vert in vertices:
        nearest = REFERENCE.find_nearest(body.matrix_world @ vert.co)
        if nearest is None:
            raise RuntimeError(f"Projection failed for {name}")
        vert.co = inverse @ nearest[0]


def inset_one_side(
    faces: list[bmesh.types.BMFace],
    thickness: float,
    label: str,
) -> tuple[dict, set[bmesh.types.BMVert]]:
    face_set = set(faces)
    edges = {edge for face in faces for edge in face.edges}
    boundary = [
        edge
        for edge in edges
        if sum(linked in face_set for linked in edge.link_faces) == 1
    ]
    before = set(bm.verts)
    result = bmesh.ops.inset_region(
        bm,
        faces=faces,
        use_boundary=True,
        use_even_offset=True,
        use_interpolate=False,
        use_relative_offset=False,
        use_edge_rail=False,
        thickness=thickness,
        depth=0.0,
        use_outset=False,
    )
    new_vertices = set(bm.verts) - before
    project_new(new_vertices, label)
    return (
        {
            "selected_faces": len(faces),
            "selected_components": region_components(faces),
            "boundary_edges": len(boundary),
            "operator_result_faces": len(result.get("faces", [])),
            "new_vertices": len(new_vertices),
        },
        new_vertices,
    )


def enforce_paired_positions(
    left_vertices: set[bmesh.types.BMVert],
    right_vertices: set[bmesh.types.BMVert],
    name: str,
) -> dict:
    if len(left_vertices) != len(right_vertices):
        raise RuntimeError(
            f"{name}: paired inset created unequal vertex counts "
            f"{len(left_vertices)} != {len(right_vertices)}"
        )
    inverse = body.matrix_world.inverted()
    right_list = list(right_vertices)
    right_tree = KDTree(len(right_list))
    for index, vert in enumerate(right_list):
        right_tree.insert(body.matrix_world @ vert.co, index)
    right_tree.balance()
    used = set()
    errors = []
    for left in left_vertices:
        left_point = body.matrix_world @ left.co
        _, right_index, distance = right_tree.find(
            Vector((-left_point.x, left_point.y, left_point.z))
        )
        right = right_list[right_index]
        if right in used:
            raise RuntimeError(f"{name}: non-bijective mirrored new-vertex pairing")
        used.add(right)
        right_point = body.matrix_world @ right.co
        magnitude_x = (abs(left_point.x) + abs(right_point.x)) * 0.5
        average_y = (left_point.y + right_point.y) * 0.5
        average_z = (left_point.z + right_point.z) * 0.5
        left.co = inverse @ Vector((magnitude_x, average_y, average_z))
        right.co = inverse @ Vector((-magnitude_x, average_y, average_z))
        errors.append(distance)
    if len(used) != len(right_vertices):
        raise RuntimeError(f"{name}: incomplete mirrored new-vertex pairing")
    return {
        "pre_enforcement_mirror_p95": percentile(errors, 0.95),
        "pre_enforcement_mirror_maximum": max(errors),
        "paired_new_vertices_per_side": len(left_vertices),
    }


def apply_paired_region(name: str, predicate, thickness: float) -> dict:
    left_candidates = [
        face
        for face in source_faces
        if face.is_valid
        and predicate(body.matrix_world @ face.calc_center_median())
        and face_is_tail_safe(face)
        and (
            name != "shoulder"
            or all(
                (body.matrix_world @ vert.co).z < 0.4707
                for vert in face.verts
            )
        )
    ]
    candidate_set = set(left_candidates)
    candidate_components: list[list[bmesh.types.BMFace]] = []
    remaining = set(left_candidates)
    while remaining:
        seed = remaining.pop()
        component = [seed]
        stack = [seed]
        while stack:
            face = stack.pop()
            neighbors = {
                other
                for edge in face.edges
                for other in edge.link_faces
                if other in remaining and other in candidate_set
            }
            for other in neighbors:
                remaining.remove(other)
                component.append(other)
                stack.append(other)
        candidate_components.append(component)
    candidate_components.sort(key=len, reverse=True)
    if not candidate_components:
        raise RuntimeError(f"{name}: empty semantic selection")
    left_faces = candidate_components[0]
    left_faces.sort(key=lambda face: face.index)
    right_faces = [mirror_face[face] for face in left_faces]
    if len(set(left_faces)) != len(left_faces):
        raise RuntimeError(f"{name}: duplicate left faces")
    if len(set(right_faces)) != len(right_faces):
        raise RuntimeError(f"{name}: duplicate right faces")
    if set(left_faces) & set(right_faces):
        raise RuntimeError(f"{name}: left/right source regions overlap")

    left_stats, left_new = inset_one_side(
        left_faces, thickness, f"{name}_left"
    )
    right_stats, right_new = inset_one_side(
        right_faces, thickness, f"{name}_right"
    )
    pairing = enforce_paired_positions(left_new, right_new, name)
    region_new = left_new | right_new
    all_new_vertices.update(region_new)
    region_new_vertices[name] = region_new
    return {
        "candidate_component_sizes": [
            len(component) for component in candidate_components
        ],
        "rejected_faces_outside_largest_component": (
            len(left_candidates) - len(left_faces)
        ),
        "left": left_stats,
        "right": right_stats,
        "pairing": pairing,
        "total_new_vertices": len(region_new),
    }


def point_segment_distance(point: Vector, start: Vector, end: Vector) -> float:
    segment = end - start
    if segment.length_squared <= 1.0e-12:
        return (point - start).length
    fraction = max(
        0.0,
        min(1.0, (point - start).dot(segment) / segment.length_squared),
    )
    return (point - (start + segment * fraction)).length


SHOULDER_BONE_START = Vector((0.150, -0.055, 0.4706151294708252))
SHOULDER_BONE_END = Vector((0.205, -0.085, 0.4006151294708252))


def shoulder(point: Vector) -> bool:
    return (
        0.170 <= point.x <= 0.320
        and -0.260 <= point.y <= 0.060
        and 0.320 <= point.z <= 0.445
        and point_segment_distance(
            point, SHOULDER_BONE_START, SHOULDER_BONE_END
        )
        <= 0.110
    )


def hip_groin(point: Vector) -> bool:
    return (
        0.025 <= point.x <= 0.235
        and -0.275 <= point.y <= 0.055
        and 0.185 <= point.z <= 0.315
    )


def knee(point: Vector) -> bool:
    return (
        0.04 <= point.x <= 0.295
        and -0.275 <= point.y <= 0.055
        and 0.115 <= point.z <= 0.220
    )


report["regions"]["shoulder"] = apply_paired_region(
    "shoulder", shoulder, 0.004
)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(body.data)
body.data.update()
report["steps"]["10_shoulders"] = save(
    body,
    "10_paired_shoulder_armpit_support_ring.blend",
    "explicitly paired left/right shoulder-armpit quad support rings",
)

report["regions"]["hip_groin"] = apply_paired_region(
    "hip_groin", hip_groin, 0.0035
)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(body.data)
body.data.update()
report["steps"]["20_hips"] = save(
    body,
    "20_paired_hip_groin_support_ring.blend",
    "explicitly paired left/right hip-groin quad support rings",
)

report["regions"]["knee"] = apply_paired_region("knee", knee, 0.003)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(body.data)
body.data.update()
report["steps"]["30_knees"] = save(
    body,
    "30_paired_knee_support_ring.blend",
    "explicitly paired left/right knee quad support rings",
)

# Restore every original vertex exactly. This makes all passing tail geometry
# and all mouth/head geometry coordinate-identical to canonical r003.
for vert, source_co in source_by_reference.items():
    if not vert.is_valid:
        raise RuntimeError("An original source vertex was destroyed")
    vert.co = source_co

bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.verts.index_update()
bm.edges.index_update()
bm.faces.index_update()
new_indices = sorted(vert.index for vert in all_new_vertices)
region_indices = {
    name: sorted(vert.index for vert in vertices)
    for name, vertices in region_new_vertices.items()
}
new_world = [body.matrix_world @ vert.co for vert in all_new_vertices]
tail_original_deltas = []
mouth_original_deltas = []
for vert, source_co in source_by_reference.items():
    source_world = body.matrix_world @ source_co
    delta = (vert.co - source_co).length
    if source_world.y > 0.09 and source_world.z < 0.35:
        tail_original_deltas.append(delta)
    if source_world.z > 0.60:
        mouth_original_deltas.append(delta)

report["new_vertex_audit"] = {
    "count": len(all_new_vertices),
    "indices": new_indices,
    "by_region": region_indices,
    "new_vertices_in_passing_tail_zone": sum(
        point.y > 0.09 and point.z < 0.35 for point in new_world
    ),
    "new_vertices_in_mouth_head_zone": sum(point.z > 0.60 for point in new_world),
    "tail_original_vertex_count": len(tail_original_deltas),
    "tail_original_vertex_maximum_delta": max(tail_original_deltas, default=0.0),
    "mouth_original_vertex_count": len(mouth_original_deltas),
    "mouth_original_vertex_maximum_delta": max(
        mouth_original_deltas, default=0.0
    ),
}

bm.to_mesh(body.data)
bm.free()
body.data.update()
report["steps"]["40_finalize"] = save(
    body,
    "40_paired_joint_support_loops_candidate.blend",
    "restore all original vertices exactly; preserve paired new positions; recalc normals",
)

final = report["steps"]["40_finalize"]["topology"]
report["lineage"]["canonical_sha256_after"] = sha256(SOURCE)
report["acceptance"] = {
    "canonical_source_unchanged": (
        report["lineage"]["canonical_sha256_before"]
        == report["lineage"]["canonical_sha256_after"]
    ),
    "all_quads": final["triangles"] == 0 and final["ngons"] == 0,
    "closed_manifold": (
        final["boundary_edges"] == 0 and final["non_manifold_edges"] == 0
    ),
    "nondegenerate": (
        final["zero_area_faces"] == 0 and final["zero_length_edges"] == 0
    ),
    "single_positive_shell": (
        final["connected_face_components"] == 1
        and final["euler_characteristic"] == 2
        and final["signed_volume"] > 0.0
    ),
    "exact_mirrored_topology": (
        final["symmetry"]["edge_match_ratio"] == 1.0
        and final["symmetry"]["face_match_ratio"] == 1.0
    ),
    "source_symmetry_tolerance_preserved": (
        final["symmetry"]["within_1e_6_ratio"] >= 0.9998
    ),
    "p95_deviation_within_0_15_percent_height": (
        final["surface_deviation"]["p95_fraction_of_height"] <= 0.0015
    ),
    "tail_topology_untouched": (
        report["new_vertex_audit"]["new_vertices_in_passing_tail_zone"] == 0
        and report["new_vertex_audit"]["tail_original_vertex_maximum_delta"]
        == 0.0
    ),
    "mouth_zone_untouched": (
        report["new_vertex_audit"]["new_vertices_in_mouth_head_zone"] == 0
        and report["new_vertex_audit"]["mouth_original_vertex_maximum_delta"]
        == 0.0
    ),
}
report["verdict"] = {
    "technical_topology_gate": all(report["acceptance"].values()),
    "deformation_gate": "pending bounded re-probe",
    "production_ready": False,
    "user_approved": False,
}
(QA / "paired_joint_support_loop_report.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)
(QA / "paired_new_vertex_indices.json").write_text(
    json.dumps(
        {
            "all_new_vertex_indices": new_indices,
            "by_region": region_indices,
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(
    json.dumps(
        {
            "regions": report["regions"],
            "new_vertex_audit": report["new_vertex_audit"],
            "acceptance": report["acceptance"],
            "final": final,
        },
        indent=2,
    )
)
