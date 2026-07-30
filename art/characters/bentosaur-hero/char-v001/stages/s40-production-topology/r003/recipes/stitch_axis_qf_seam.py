"""Stitch the open mirrored seam emitted by axis-aligned symmetric QuadriFlow.

The input is already all-quads and exactly mirrored, but QuadriFlow returns
two open half-shell boundaries close to Y=0. This experiment snaps boundary
vertices to the symmetry plane and welds coincident mirror pairs.
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


ROOT = Path(__file__).resolve().parent / "axis-qf-seam-stitch"
ROOT.mkdir(parents=True, exist_ok=True)
PRESERVED_SOURCE = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/art/characters/"
    "bentosaur-hero/char-v001/stages/s40-production-topology/r002/work/"
    "30_symmetrized_negative_y_bootstrap.blend"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    return sorted(values)[min(len(values) - 1, math.ceil(len(values) * fraction) - 1)]


def source_reference() -> tuple[BVHTree, float]:
    with bpy.data.libraries.load(str(PRESERVED_SOURCE), link=False) as (available, loaded):
        loaded.objects = list(available.objects)
    objects = [obj for obj in loaded.objects if obj is not None and obj.type == "MESH"]
    if len(objects) != 1:
        raise RuntimeError(f"Expected one preserved source object, found {len(objects)}")
    source = objects[0]
    points = [source.matrix_world @ vertex.co for vertex in source.data.vertices]
    polygons = [list(poly.vertices) for poly in source.data.polygons]
    return (
        BVHTree.FromPolygons(points, polygons, all_triangles=False),
        max(point.z for point in points) - min(point.z for point in points),
    )


REFERENCE, SOURCE_HEIGHT = source_reference()


def topology(obj: bpy.types.Object) -> dict:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    points = [obj.matrix_world @ vert.co for vert in bm.verts]
    plane_y = (
        min(point.y for point in points) + max(point.y for point in points)
    ) * 0.5
    tree = KDTree(len(points))
    for index, point in enumerate(points):
        tree.insert(Vector((point.x, 2.0 * plane_y - point.y, point.z)), index)
    tree.balance()
    mirror = {}
    errors = []
    for index, point in enumerate(points):
        _, match, distance = tree.find(point)
        mirror[index] = match
        errors.append(distance)
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
    distances = sorted(
        nearest[3]
        for point in points
        if (nearest := REFERENCE.find_nearest(point)) is not None
    )
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "triangles": sum(len(face.verts) == 3 for face in bm.faces),
        "quads": sum(len(face.verts) == 4 for face in bm.faces),
        "ngons": sum(len(face.verts) > 4 for face in bm.faces),
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "zero_area_faces": sum(face.calc_area() <= 1.0e-12 for face in bm.faces),
        "symmetry": {
            "vertex_match_ratio_within_1e_6": (
                sum(error <= 1.0e-6 for error in errors) / len(errors)
            ),
            "vertex_p95": percentile(errors, 0.95),
            "vertex_maximum": max(errors),
            "edge_match_ratio": edge_matches / len(bm.edges),
            "face_match_ratio": face_matches / len(bm.faces),
        },
        "deviation_from_preserved_s40": {
            "mean": sum(distances) / len(distances),
            "p95": percentile(distances, 0.95),
            "maximum": max(distances),
            "p95_fraction_of_height": percentile(distances, 0.95) / SOURCE_HEIGHT,
        },
    }
    bm.free()
    return result


def save(obj: bpy.types.Object, name: str, operation: str) -> dict:
    obj["bentosaur_experiment"] = "axis_qf_seam_stitch"
    obj["bentosaur_operation"] = operation
    obj["bentosaur_production_ready"] = False
    path = ROOT / name
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    return {
        "operation": operation,
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "topology": topology(obj),
    }


input_path = Path(bpy.data.filepath).resolve()
objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if len(objects) != 1:
    raise RuntimeError(f"Expected one candidate mesh, found {len(objects)}")
obj = objects[0]
report = {
    "schema_version": "1.0.0",
    "method": "snap_symmetric_quadriflow_boundaries_to_y0_and_weld",
    "lineage": {
        "input": {"path": str(input_path), "sha256": sha256(input_path)},
        "preserved_s40": {
            "path": str(PRESERVED_SOURCE),
            "sha256": sha256(PRESERVED_SOURCE),
        },
    },
    "steps": {},
}
report["steps"]["00_input"] = save(
    obj,
    "00_input_axis_qf_open_all_quad.blend",
    "immutable axis-aligned symmetric QuadriFlow duplicate",
)

bm = bmesh.new()
bm.from_mesh(obj.data)
boundary_edges = [edge for edge in bm.edges if edge.is_boundary]
boundary_vertices = {vert for edge in boundary_edges for vert in edge.verts}
before_abs_y = sorted(abs((obj.matrix_world @ vert.co).y) for vert in boundary_vertices)
if not obj.matrix_world.is_identity:
    raise RuntimeError("Expected identity transform for vendor-space seam snap")
for vert in boundary_vertices:
    vert.co.y = 0.0
bm.normal_update()
bm.to_mesh(obj.data)
obj.data.update()
report["boundary_snap"] = {
    "edge_count": len(boundary_edges),
    "vertex_count": len(boundary_vertices),
    "abs_y_before": {
        "mean": sum(before_abs_y) / len(before_abs_y),
        "p95": percentile(before_abs_y, 0.95),
        "maximum": max(before_abs_y),
    },
}
report["steps"]["10_snap"] = save(
    obj,
    "10_boundary_vertices_snapped_to_y0.blend",
    "snap all open symmetric-boundary vertices to Y=0",
)

bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-7)
bm.normal_update()
bm.to_mesh(obj.data)
obj.data.update()
report["steps"]["20_weld"] = save(
    obj,
    "20_coincident_mirror_boundary_weld.blend",
    "weld coincident mirror-boundary vertices at 1e-7",
)

bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1.0e-9)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.normal_update()
bm.to_mesh(obj.data)
bm.free()
obj.data.update()
report["steps"]["30_cleanup"] = save(
    obj,
    "30_axis_qf_closed_cleanup.blend",
    "dissolve exact degenerates and recalculate normals",
)

final = report["steps"]["30_cleanup"]["topology"]
report["acceptance"] = {
    "all_quads": final["triangles"] == 0 and final["ngons"] == 0,
    "closed_manifold": (
        final["boundary_edges"] == 0 and final["non_manifold_edges"] == 0
    ),
    "zero_area_free": final["zero_area_faces"] == 0,
    "exact_vertex_symmetry": (
        final["symmetry"]["vertex_match_ratio_within_1e_6"] == 1.0
    ),
    "exact_topology_symmetry": (
        final["symmetry"]["edge_match_ratio"] == 1.0
        and final["symmetry"]["face_match_ratio"] == 1.0
    ),
    "p95_deviation_within_0_15_percent_height": (
        final["deviation_from_preserved_s40"]["p95_fraction_of_height"] <= 0.0015
    ),
}
report["verdict"] = {
    "accepted": all(report["acceptance"].values()),
    "production_files_modified": False,
}
path = ROOT / "report.json"
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"acceptance": report["acceptance"], "final": final}, indent=2))
