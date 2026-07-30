"""Audit mirror topology while respecting canonical/new-vertex lineage.

The generic nearest-point audit can map a newly inset point to a nearby
canonical point. This partitioned audit prevents that ambiguity by pairing the
first 10,050 preserved canonical vertices only with canonical vertices and the
subsequent inserted vertices only with inserted vertices.
"""

from __future__ import annotations

import json
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "qa" / "partitioned_symmetry_audit.json"
TARGET = "BENTOSAUR_JOINT_REPAIR_CANDIDATE_NOT_APPROVED"
ORIGINAL_VERTEX_COUNT = 10050

obj = bpy.data.objects.get(TARGET)
if obj is None or obj.type != "MESH":
    raise RuntimeError(f"Missing candidate mesh: {TARGET}")

bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
points = [obj.matrix_world @ vert.co for vert in bm.verts]


def pair_partition(indices: list[int]) -> tuple[dict[int, int], list[float]]:
    tree = KDTree(len(indices))
    for slot, index in enumerate(indices):
        tree.insert(points[index], slot)
    tree.balance()
    pairing = {}
    errors = []
    for index in indices:
        point = points[index]
        _, slot, distance = tree.find(Vector((-point.x, point.y, point.z)))
        pairing[index] = indices[slot]
        errors.append(distance)
    return pairing, errors


original_indices = list(range(ORIGINAL_VERTEX_COUNT))
new_indices = list(range(ORIGINAL_VERTEX_COUNT, len(bm.verts)))
original_pairing, original_errors = pair_partition(original_indices)
new_pairing, new_errors = pair_partition(new_indices)
mirror = original_pairing | new_pairing

edge_keys = {
    tuple(sorted((edge.verts[0].index, edge.verts[1].index)))
    for edge in bm.edges
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
    for edge in bm.edges
)
face_keys = {frozenset(vert.index for vert in face.verts) for face in bm.faces}
face_matches = sum(
    frozenset(mirror[vert.index] for vert in face.verts) in face_keys
    for face in bm.faces
)
involution_failures = sum(mirror.get(mirror[index]) != index for index in mirror)
report = {
    "candidate": bpy.data.filepath,
    "method": "nearest mirrored point constrained by canonical/new lineage",
    "canonical_vertices": len(original_indices),
    "new_vertices": len(new_indices),
    "edge_count": len(bm.edges),
    "face_count": len(bm.faces),
    "edge_matches": edge_matches,
    "face_matches": face_matches,
    "edge_match_ratio": edge_matches / len(bm.edges),
    "face_match_ratio": face_matches / len(bm.faces),
    "pairing_involution_failures": involution_failures,
    "canonical_mirror_maximum": max(original_errors),
    "new_mirror_maximum": max(new_errors),
}
OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
bm.free()
