"""Build the reproducible Bentosaur hybrid retopology bootstrap.

This is an evidence generator, not an approval or production promotion. It
opens the repaired Smart LowPoly scaffold, saves an immutable input snapshot,
runs a no-symmetry QuadriFlow pass, cleans exact degenerates, then replaces
one side using BMesh symmetry. Every material step is saved as a separate
Blender source file.

Run by opening the repaired scaffold blend:

    Blender --background /absolute/path/cycle_patch_candidate.blend \
      --python /absolute/path/build_hybrid_bootstrap_probe.py -- \
      --output /absolute/path/hybrid-bootstrap-v1 \
      --target-faces 12000
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--target-faces", type=int, default=12000)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def topology(obj: bpy.types.Object) -> dict[str, object]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    world_vertices = [obj.matrix_world @ vert.co for vert in bm.verts]
    minimum = Vector(
        tuple(min(point[i] for point in world_vertices) for i in range(3))
    )
    maximum = Vector(
        tuple(max(point[i] for point in world_vertices) for i in range(3))
    )
    height = maximum.z - minimum.z
    y_center = (minimum.y + maximum.y) / 2.0
    tree = KDTree(len(world_vertices))
    for index, point in enumerate(world_vertices):
        tree.insert(
            Vector((point.x, -point.y + 2.0 * y_center, point.z)),
            index,
        )
    tree.balance()
    mirror_errors = sorted(tree.find(point)[2] for point in world_vertices)
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "quads": sum(len(face.verts) == 4 for face in bm.faces),
        "triangles": sum(len(face.verts) == 3 for face in bm.faces),
        "ngons": sum(len(face.verts) > 4 for face in bm.faces),
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "zero_area_faces": sum(face.calc_area() <= 1.0e-12 for face in bm.faces),
        "bounds": {
            "minimum": list(minimum),
            "maximum": list(maximum),
            "height": height,
            "mirror_plane_y": y_center,
        },
        "symmetry": {
            "match_ratio_within_0_05_percent_height": (
                sum(error <= height * 0.0005 for error in mirror_errors)
                / len(mirror_errors)
            ),
            "mean_error": sum(mirror_errors) / len(mirror_errors),
            "p95_error": mirror_errors[
                min(len(mirror_errors) - 1, math.ceil(len(mirror_errors) * 0.95) - 1)
            ],
            "maximum_error": max(mirror_errors),
        },
    }
    bm.free()
    return result


def source_bvh(obj: bpy.types.Object) -> BVHTree:
    vertices = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    polygons = [list(polygon.vertices) for polygon in obj.data.polygons]
    return BVHTree.FromPolygons(vertices, polygons, all_triangles=False)


def deviation(obj: bpy.types.Object, bvh: BVHTree, height: float) -> dict[str, float]:
    distances = []
    for vertex in obj.data.vertices:
        nearest = bvh.find_nearest(obj.matrix_world @ vertex.co)
        if nearest:
            distances.append(nearest[3])
    distances.sort()
    p95_index = min(
        len(distances) - 1,
        math.ceil(len(distances) * 0.95) - 1,
    )
    return {
        "samples": len(distances),
        "mean": sum(distances) / len(distances),
        "p95": distances[p95_index],
        "maximum": max(distances),
        "mean_fraction_of_character_height": (
            sum(distances) / len(distances) / height
        ),
        "p95_fraction_of_character_height": distances[p95_index] / height,
        "maximum_fraction_of_character_height": max(distances) / height,
    }


def save_step(
    obj: bpy.types.Object,
    output: Path,
    filename: str,
    step: str,
    source_sha: str,
) -> dict[str, object]:
    obj["bentosaur_pipeline_role"] = "retopology_bootstrap_probe"
    obj["bentosaur_pipeline_step"] = step
    obj["bentosaur_source_sha256"] = source_sha
    obj["bentosaur_user_approved"] = False
    obj["bentosaur_production_ready"] = False
    path = output / filename
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    return {
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "topology": topology(obj),
    }


args = parse_args()
output = args.output.expanduser().resolve()
output.mkdir(parents=True, exist_ok=True)
expected_outputs = (
    "00_input_repaired_scaffold_snapshot.blend",
    "10_quadriflow_unsym_12000.blend",
    "20_exact_degenerate_cleanup.blend",
    "30_symmetrized_negative_y_candidate_not_approved.blend",
    "pipeline_report.json",
)
existing = [output / name for name in expected_outputs if (output / name).exists()]
if existing:
    raise FileExistsError(
        "Refusing to overwrite bootstrap evidence: "
        + ", ".join(str(path) for path in existing)
    )

source_path = Path(bpy.data.filepath).resolve()
if not source_path.is_file():
    raise RuntimeError("Open the repaired Smart LowPoly source blend first.")
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if len(meshes) != 1:
    raise RuntimeError(f"Expected exactly one source mesh, found {len(meshes)}.")
obj = meshes[0]
source_sha = sha256(source_path)
source_topology = topology(obj)
source_height = source_topology["bounds"]["height"]
reference_bvh = source_bvh(obj)

report: dict[str, object] = {
    "schema_version": "1.0.0",
    "purpose": "reproducible hybrid retopology bootstrap evidence",
    "production_approval": False,
    "user_approval": False,
    "blender_version": bpy.app.version_string,
    "source": {
        "path": str(source_path),
        "sha256": source_sha,
        "bytes": source_path.stat().st_size,
        "topology": source_topology,
    },
    "settings": {
        "quadriflow_target_faces": args.target_faces,
        "quadriflow_use_mesh_symmetry": False,
        "quadriflow_use_preserve_sharp": True,
        "quadriflow_use_preserve_boundary": False,
        "quadriflow_preserve_attributes": False,
        "quadriflow_seed": 0,
        "remove_doubles_distance": 1.0e-6,
        "dissolve_degenerate_distance": 1.0e-6,
        "bmesh_symmetrize_direction": "-Y",
        "bmesh_symmetrize_distance": 1.0e-4,
        "post_symmetry_remove_doubles_distance": 1.0e-5,
    },
    "steps": {},
}

report["steps"]["00_input_snapshot"] = save_step(
    obj,
    output,
    "00_input_repaired_scaffold_snapshot.blend",
    "00_input_snapshot",
    source_sha,
)

bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.quadriflow_remesh(
    use_mesh_symmetry=False,
    use_preserve_sharp=True,
    use_preserve_boundary=False,
    preserve_attributes=False,
    smooth_normals=True,
    mode="FACES",
    target_faces=args.target_faces,
    seed=0,
)
obj.name = "BENTOSAUR_BOOTSTRAP_QUADRIFLOW_UNSYM_NOT_APPROVED"
report["steps"]["10_quadriflow_unsym"] = save_step(
    obj,
    output,
    "10_quadriflow_unsym_12000.blend",
    "10_quadriflow_unsym",
    source_sha,
)
report["steps"]["10_quadriflow_unsym"]["surface_deviation"] = deviation(
    obj, reference_bvh, source_height
)

bm = bmesh.new()
bm.from_mesh(obj.data)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-6)
bmesh.ops.dissolve_degenerate(
    bm,
    edges=list(bm.edges),
    dist=1.0e-6,
)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(obj.data)
bm.free()
obj.data.update()
obj.name = "BENTOSAUR_BOOTSTRAP_CLEANED_NOT_APPROVED"
report["steps"]["20_exact_degenerate_cleanup"] = save_step(
    obj,
    output,
    "20_exact_degenerate_cleanup.blend",
    "20_exact_degenerate_cleanup",
    source_sha,
)
report["steps"]["20_exact_degenerate_cleanup"]["surface_deviation"] = deviation(
    obj, reference_bvh, source_height
)

bm = bmesh.new()
bm.from_mesh(obj.data)
bmesh.ops.symmetrize(
    bm,
    input=list(bm.verts) + list(bm.edges) + list(bm.faces),
    direction="-Y",
    dist=1.0e-4,
)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-5)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(obj.data)
bm.free()
obj.data.update()
obj.name = "BENTOSAUR_BOOTSTRAP_SYMMETRIZED_NEGATIVE_Y_NOT_APPROVED"
report["steps"]["30_symmetrized_negative_y"] = save_step(
    obj,
    output,
    "30_symmetrized_negative_y_candidate_not_approved.blend",
    "30_symmetrized_negative_y",
    source_sha,
)
report["steps"]["30_symmetrized_negative_y"]["surface_deviation"] = deviation(
    obj, reference_bvh, source_height
)

report["verdict"] = {
    "role": "production_retopology_bootstrap_only",
    "manual_center_strip_cleanup_required": True,
    "manual_mouth_topology_required": True,
    "manual_joint_loop_review_required": True,
    "safe_to_rig": False,
}
report_path = output / "pipeline_report.json"
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"report": str(report_path), "steps": report["steps"]}, indent=2))
