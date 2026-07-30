"""Alternative B: align Y=0 bilateral plane to QuadriFlow's X symmetry axis.

Every material operation is saved:
00 source duplicate
10 rotate mesh data so original Y becomes X
20 symmetric QuadriFlow
30 exact-degenerate cleanup while axis-aligned
40 inverse rotation back to vendor coordinates
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


ROOT = Path(__file__).resolve().parent / "axis-aligned-symmetric-quadriflow"
ROOT.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def mesh_object() -> bpy.types.Object:
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if len(objects) != 1:
        raise RuntimeError(f"Expected exactly one mesh, found {len(objects)}")
    return objects[0]


def source_bvh(obj: bpy.types.Object) -> BVHTree:
    vertices = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    polygons = [list(polygon.vertices) for polygon in obj.data.polygons]
    return BVHTree.FromPolygons(vertices, polygons, all_triangles=False)


def percentile(values: list[float], fraction: float) -> float:
    return values[min(len(values) - 1, math.ceil(len(values) * fraction) - 1)]


def topology(
    obj: bpy.types.Object,
    reference: BVHTree | None,
    mirror_axis: str,
) -> dict:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    points = [obj.matrix_world @ vert.co for vert in bm.verts]
    minimum = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    maximum = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    height = maximum.z - minimum.z
    axis_index = {"X": 0, "Y": 1}[mirror_axis]
    plane = (minimum[axis_index] + maximum[axis_index]) * 0.5

    tree = KDTree(len(points))
    for index, point in enumerate(points):
        mirrored = point.copy()
        mirrored[axis_index] = 2.0 * plane - point[axis_index]
        tree.insert(mirrored, index)
    tree.balance()
    mirror_map = {}
    errors = []
    for index, point in enumerate(points):
        _, match, distance = tree.find(point)
        mirror_map[index] = match
        errors.append(distance)
    errors.sort()

    edge_keys = {
        tuple(sorted((edge.verts[0].index, edge.verts[1].index)))
        for edge in bm.edges
    }
    edge_matches = sum(
        tuple(
            sorted(
                (
                    mirror_map[edge.verts[0].index],
                    mirror_map[edge.verts[1].index],
                )
            )
        )
        in edge_keys
        for edge in bm.edges
    )
    face_keys = {frozenset(vert.index for vert in face.verts) for face in bm.faces}
    face_matches = sum(
        frozenset(mirror_map[vert.index] for vert in face.verts) in face_keys
        for face in bm.faces
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
        "height": height,
        "symmetry": {
            "axis": mirror_axis,
            "plane": plane,
            "vertex_match_ratio_within_1e_6": (
                sum(error <= 1.0e-6 for error in errors) / len(errors)
            ),
            "p95": percentile(errors, 0.95),
            "maximum": max(errors),
            "edge_match_ratio": edge_matches / len(bm.edges),
            "face_match_ratio": face_matches / len(bm.faces),
        },
    }
    if reference is not None:
        distances = sorted(
            nearest[3]
            for point in points
            if (nearest := reference.find_nearest(point)) is not None
        )
        result["deviation"] = {
            "mean": sum(distances) / len(distances),
            "p95": percentile(distances, 0.95),
            "maximum": max(distances),
            "p95_fraction_of_input_height": percentile(distances, 0.95)
            / SOURCE_HEIGHT,
        }
    bm.free()
    return result


def save(
    obj: bpy.types.Object,
    name: str,
    operation: str,
    reference: BVHTree | None,
    mirror_axis: str,
) -> dict:
    obj["bentosaur_experiment"] = "axis_aligned_symmetric_quadriflow"
    obj["bentosaur_operation"] = operation
    obj["bentosaur_production_ready"] = False
    path = ROOT / name
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    return {
        "operation": operation,
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "topology": topology(obj, reference, mirror_axis),
    }


source_path = Path(bpy.data.filepath).resolve()
obj = mesh_object()
reference = source_bvh(obj)
source_points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
SOURCE_HEIGHT = max(point.z for point in source_points) - min(
    point.z for point in source_points
)
report = {
    "schema_version": "1.0.0",
    "method": "rotate_y_symmetry_plane_to_x_then_symmetric_quadriflow",
    "source": {
        "path": str(source_path),
        "sha256": sha256(source_path),
    },
    "steps": {},
}
report["steps"]["00_input"] = save(
    obj,
    "00_input_symmetrized_bootstrap.blend",
    "immutable input duplicate",
    reference,
    "Y",
)

# Bake the source's tiny vendor rotation into mesh data so axis permutation is
# mathematically explicit while preserving world-space geometry.
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
report["steps"]["05_apply_rotation"] = save(
    obj,
    "05_vendor_rotation_applied.blend",
    "apply source rotation to mesh data; world-space shape unchanged",
    reference,
    "Y",
)

# -90 degrees around Z: (x, y, z) -> (y, -x, z).
for vertex in obj.data.vertices:
    x, y, z = vertex.co
    vertex.co = (y, -x, z)
obj.data.update()
report["steps"]["10_axis_align"] = save(
    obj,
    "10_y_plane_aligned_to_x.blend",
    "rotate mesh data -90 degrees around Z so original Y=0 becomes X=0",
    None,
    "X",
)

obj.data.use_mirror_x = True
obj.data.use_mirror_y = False
obj.data.use_mirror_z = False

bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.quadriflow_remesh(
    use_mesh_symmetry=True,
    use_preserve_sharp=True,
    use_preserve_boundary=False,
    preserve_attributes=False,
    smooth_normals=True,
    mode="FACES",
    target_faces=11882,
    seed=0,
)
obj.name = "BENTOSAUR_AXIS_ALIGNED_SYMMETRIC_QUADRIFLOW_EXPERIMENT"
report["steps"]["20_quadriflow"] = save(
    obj,
    "20_axis_aligned_symmetric_quadriflow.blend",
    "QuadriFlow with Blender X-axis mesh symmetry",
    None,
    "X",
)

bm = bmesh.new()
bm.from_mesh(obj.data)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-6)
bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1.0e-6)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(obj.data)
bm.free()
obj.data.update()
report["steps"]["30_cleanup"] = save(
    obj,
    "30_axis_aligned_exact_cleanup.blend",
    "remove exact doubles and degenerate geometry; recalculate normals",
    None,
    "X",
)

# Inverse +90 degrees around Z: (x, y, z) -> (-y, x, z).
for vertex in obj.data.vertices:
    x, y, z = vertex.co
    vertex.co = (-y, x, z)
obj.data.update()
report["steps"]["40_vendor_space"] = save(
    obj,
    "40_vendor_space_all_quad_candidate.blend",
    "inverse-rotate mesh data to original vendor coordinates",
    reference,
    "Y",
)

final = report["steps"]["40_vendor_space"]["topology"]
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
        final["deviation"]["p95_fraction_of_input_height"] <= 0.0015
    ),
}
report["verdict"] = {
    "accepted": all(report["acceptance"].values()),
    "production_files_modified": False,
    "promotion_requires_parent_review": True,
}
report_path = ROOT / "report.json"
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"acceptance": report["acceptance"], "final": final}, indent=2))
