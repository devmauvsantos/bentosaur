"""Create a disposable Blender repair candidate from a Tripo Smart LowPoly FBX.

This script never modifies the input FBX. It preserves a hidden copy of the
imported source, performs conservative BMesh hole filling on a deep duplicate,
records before/after topology, and saves a Blender inspection file.

The first stage intentionally does not pretend that automatic filling creates
production topology. Its purpose is to discover which defects can be closed
mechanically before any manual retopology decision.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--passes", type=int, default=1)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def import_fbx(path: Path) -> bpy.types.Object:
    bpy.ops.import_scene.fbx(filepath=str(path))
    meshes = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if len(meshes) != 1:
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"Expected one FBX mesh, found {len(meshes)}")
    return meshes[0]


def deep_duplicate(obj: bpy.types.Object, name: str) -> bpy.types.Object:
    duplicate = obj.copy()
    duplicate.data = obj.data.copy()
    duplicate.animation_data_clear()
    duplicate.name = name
    bpy.context.scene.collection.objects.link(duplicate)
    return duplicate


def topology(obj: bpy.types.Object) -> dict[str, int]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    face_sizes = [len(face.verts) for face in bm.faces]
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "triangles": sum(size == 3 for size in face_sizes),
        "quads": sum(size == 4 for size in face_sizes),
        "ngons": sum(size > 4 for size in face_sizes),
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "loose_edges": sum(not edge.link_faces for edge in bm.edges),
        "loose_vertices": sum(not vert.link_faces for vert in bm.verts),
    }
    bm.free()
    return result


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
        edges = {seed}
        vertices = set(seed.verts)
        frontier = list(seed.verts)
        while frontier:
            vertex = frontier.pop()
            for edge in vertex.link_edges:
                if edge not in boundary or edge in edges:
                    continue
                edges.add(edge)
                remaining.discard(edge)
                for linked in edge.verts:
                    if linked not in vertices:
                        vertices.add(linked)
                        frontier.append(linked)

        points = [obj.matrix_world @ vertex.co for vertex in vertices]
        minimum = Vector(
            tuple(min(point[index] for point in points) for index in range(3))
        )
        maximum = Vector(
            tuple(max(point[index] for point in points) for index in range(3))
        )
        centroid = sum(points, Vector()) / len(points)
        degrees = {
            vertex: sum(edge in edges for edge in vertex.link_edges)
            for vertex in vertices
        }
        components.append(
            {
                "edge_count": len(edges),
                "vertex_count": len(vertices),
                "closed_loop": all(degree == 2 for degree in degrees.values()),
                "degrees": sorted(degrees.values()),
                "centroid": list(centroid),
                "minimum": list(minimum),
                "maximum": list(maximum),
                "dimensions": list(maximum - minimum),
            }
        )
    bm.free()
    return sorted(components, key=lambda row: row["edge_count"], reverse=True)


def world_bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector(
        tuple(min(point[index] for point in points) for index in range(3))
    )
    maximum = Vector(
        tuple(max(point[index] for point in points) for index in range(3))
    )
    return {
        "minimum": list(minimum),
        "maximum": list(maximum),
        "dimensions": list(maximum - minimum),
    }


def conservative_hole_fill(obj: bpy.types.Object) -> dict[str, object]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    boundary_before = [edge for edge in bm.edges if edge.is_boundary]
    existing_faces = set(bm.faces)
    fill_result = bmesh.ops.holes_fill(bm, edges=boundary_before, sides=0)
    returned_faces = list(fill_result.get("faces", []))
    new_faces = [face for face in bm.faces if face not in existing_faces]
    for face in new_faces:
        face.material_index = 0
        face.smooth = True
    if new_faces:
        bmesh.ops.recalc_face_normals(bm, faces=new_faces)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    new_face_sizes = [len(face.verts) for face in new_faces]
    result = {
        "boundary_edges_before": len(boundary_before),
        "operator_returned_faces": len(returned_faces),
        "new_faces": len(new_faces),
        "new_triangles": sum(size == 3 for size in new_face_sizes),
        "new_quads": sum(size == 4 for size in new_face_sizes),
        "new_ngons": sum(size > 4 for size in new_face_sizes),
        "new_face_vertex_counts": sorted(new_face_sizes),
        "boundary_edges_after": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges_after": sum(not edge.is_manifold for edge in bm.edges),
    }
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.free()
    return result


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    if not source.is_file():
        raise FileNotFoundError(source)

    clear_scene()
    imported = import_fbx(source)
    imported.name = "00_TRIPO_RAW_LOCKED"
    imported.hide_render = True
    imported.hide_set(True)

    repaired = deep_duplicate(imported, "10_REPAIR_AUTO_FILL_CANDIDATE")
    repaired.hide_render = False
    repaired.hide_set(False)

    before = topology(repaired)
    repair_passes: list[dict[str, object]] = []
    for pass_index in range(max(1, args.passes)):
        pass_result = conservative_hole_fill(repaired)
        pass_result["pass"] = pass_index + 1
        repair_passes.append(pass_result)
        if pass_result["boundary_edges_after"] == 0:
            break
        if (
            pass_result["boundary_edges_after"]
            >= pass_result["boundary_edges_before"]
        ):
            break
    after = topology(repaired)
    report = {
        "source": str(source),
        "operation": "iterative_conservative_bmesh_holes_fill",
        "raw_source_modified": False,
        "before": before,
        "requested_passes": args.passes,
        "repair_passes": repair_passes,
        "after": after,
        "remaining_boundary_components": boundary_components(repaired),
        "bounds_after": world_bounds(repaired),
        "interpretation_guardrail": (
            "A closed mesh after automatic filling is not evidence of "
            "deformation-ready topology or valid UVs on the inserted faces."
        ),
    }
    report_path = output / "repair_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    blend_path = output / "repair_candidate.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(
        json.dumps(
            {
                "status": "success",
                "report": str(report_path),
                "blend": str(blend_path),
            }
        )
    )


if __name__ == "__main__":
    main()
