"""Disposable audit of automatic hole-fill strategies for the Tripo FBX.

This script never overwrites its input. It imports the FBX, runs each BMesh
operator on an independent in-memory copy, and records topology/geometry
metrics so an automatic repair can be judged before any production asset is
changed.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--low", required=True, type=Path)
    parser.add_argument("--high", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--save-best", action="store_true")
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_one(path: Path, name: str) -> bpy.types.Object:
    before = set(bpy.context.scene.objects)
    if path.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    elif path.suffix.lower() in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        raise RuntimeError(path.suffix)
    meshes = [
        obj
        for obj in bpy.context.scene.objects
        if obj not in before and obj.type == "MESH"
    ]
    if len(meshes) != 1:
        raise RuntimeError(f"{path}: expected one mesh, got {len(meshes)}")
    meshes[0].name = name
    return meshes[0]


def boundary_graphs(bm: bmesh.types.BMesh) -> list[dict[str, object]]:
    remaining = {edge for edge in bm.edges if edge.is_boundary}
    rows: list[dict[str, object]] = []
    while remaining:
        seed = remaining.pop()
        edges = {seed}
        verts = set(seed.verts)
        frontier = list(seed.verts)
        while frontier:
            vert = frontier.pop()
            for edge in vert.link_edges:
                if edge not in remaining:
                    continue
                remaining.remove(edge)
                edges.add(edge)
                for linked in edge.verts:
                    if linked not in verts:
                        verts.add(linked)
                        frontier.append(linked)
        degrees = {
            vert: sum(edge in edges for edge in vert.link_edges) for vert in verts
        }
        rows.append(
            {
                "edges": edges,
                "verts": verts,
                "edge_count": len(edges),
                "vertex_count": len(verts),
                "degree_histogram": {
                    str(degree): list(degrees.values()).count(degree)
                    for degree in sorted(set(degrees.values()))
                },
                "cycle_rank": len(edges) - len(verts) + 1,
                "simple_loop": all(degree == 2 for degree in degrees.values()),
            }
        )
    return sorted(rows, key=lambda row: row["edge_count"], reverse=True)


def boundary_cycles(
    bm: bmesh.types.BMesh,
) -> list[dict[str, object]]:
    """Decompose the observed degree-2/degree-4 boundary graph into face cycles."""
    cycles: list[dict[str, object]] = []
    for graph in boundary_graphs(bm):
        unused = set(graph["edges"])
        graph_verts = set(graph["verts"])
        hubs = [
            vert
            for vert in graph_verts
            if sum(edge in graph["edges"] for edge in vert.link_edges) > 2
        ]
        while unused:
            if hubs:
                start = next(
                    (
                        hub
                        for hub in hubs
                        if any(edge in unused for edge in hub.link_edges)
                    ),
                    next(iter(unused)).verts[0],
                )
            else:
                start = next(iter(unused)).verts[0]
            current = start
            ordered_verts = [start]
            ordered_edges: list[bmesh.types.BMEdge] = []
            for _ in range(len(unused) + 1):
                candidates = [
                    edge for edge in current.link_edges if edge in unused
                ]
                if not candidates:
                    break
                edge = candidates[0]
                unused.remove(edge)
                ordered_edges.append(edge)
                current = edge.other_vert(current)
                if current == start:
                    break
                ordered_verts.append(current)
            cycles.append(
                {
                    "verts": ordered_verts,
                    "edges": ordered_edges,
                    "closed": current == start,
                }
            )
    return cycles


def base_metrics(bm: bmesh.types.BMesh) -> dict[str, object]:
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    boundary = [edge for edge in bm.edges if edge.is_boundary]
    return {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "triangles_evaluated": sum(max(len(face.verts) - 2, 1) for face in bm.faces),
        "boundary_edges": len(boundary),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "zero_area_faces_lt_1e_12": sum(face.calc_area() < 1.0e-12 for face in bm.faces),
        "boundary_graphs": [
            {
                key: value
                for key, value in row.items()
                if key not in {"edges", "verts"}
            }
            for row in boundary_graphs(bm)
        ],
    }


def face_metrics(
    faces: list[bmesh.types.BMFace],
    bm: bmesh.types.BMesh | None = None,
) -> dict[str, object]:
    areas = sorted(face.calc_area() for face in faces if face.is_valid)
    sides: dict[str, int] = {}
    for face in faces:
        if not face.is_valid:
            continue
        key = str(len(face.verts))
        sides[key] = sides.get(key, 0) + 1
    result: dict[str, object] = {
        "count": len(areas),
        "side_histogram": sides,
        "area_min": areas[0] if areas else None,
        "area_median": areas[len(areas) // 2] if areas else None,
        "area_max": areas[-1] if areas else None,
        "zero_area_lt_1e_12": sum(area < 1.0e-12 for area in areas),
    }
    result["zero_area_face_details"] = [
        {
            "sides": len(face.verts),
            "centroid_local": list(face.calc_center_median()),
            "vertices_local": [list(vert.co) for vert in face.verts],
        }
        for face in faces
        if face.is_valid and face.calc_area() < 1.0e-12
    ]
    if bm is not None:
        uv_layer = bm.loops.layers.uv.active
        if uv_layer is not None:
            uvs = [
                tuple(loop[uv_layer].uv)
                for face in faces
                if face.is_valid
                for loop in face.loops
            ]
            result["uv_loops"] = len(uvs)
            result["uv_loops_at_origin"] = sum(
                abs(uv[0]) < 1.0e-9 and abs(uv[1]) < 1.0e-9 for uv in uvs
            )
            result["uv_unique_rounded_6dp"] = len(
                {(round(uv[0], 6), round(uv[1], 6)) for uv in uvs}
            )
    return result


def clone_bmesh(source: bpy.types.Object) -> bmesh.types.BMesh:
    bm = bmesh.new()
    bm.from_mesh(source.data)
    return bm


def fill_until_stable(
    bm: bmesh.types.BMesh, max_passes: int = 8
) -> tuple[list[bmesh.types.BMFace], list[dict[str, int]]]:
    created: list[bmesh.types.BMFace] = []
    passes: list[dict[str, int]] = []
    for pass_index in range(max_passes):
        boundary = [edge for edge in bm.edges if edge.is_boundary]
        if not boundary:
            break
        result = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
        faces = list(result.get("faces", []))
        created.extend(faces)
        remaining = sum(edge.is_boundary for edge in bm.edges)
        passes.append(
            {
                "pass": pass_index + 1,
                "input_boundary_edges": len(boundary),
                "created_faces": len(faces),
                "remaining_boundary_edges": remaining,
            }
        )
        if not faces:
            break
    return created, passes


def high_world_bvh(high: bpy.types.Object) -> BVHTree:
    high_vertices = [
        high.matrix_world @ vertex.co for vertex in high.data.vertices
    ]
    high_polygons = [
        tuple(vertex for vertex in polygon.vertices)
        for polygon in high.data.polygons
    ]
    return BVHTree.FromPolygons(
        high_vertices, high_polygons, all_triangles=True
    )


def project_degenerate_cycles(
    bm: bmesh.types.BMesh,
    source: bpy.types.Object,
    high: bpy.types.Object,
) -> list[dict[str, object]]:
    bvh = high_world_bvh(high)
    inverse = source.matrix_world.inverted()
    rows: list[dict[str, object]] = []
    already_projected: set[bmesh.types.BMVert] = set()
    for cycle in boundary_cycles(bm):
        verts = list(cycle["verts"])
        if not cycle["closed"] or len(verts) != 3:
            continue
        world_before = [source.matrix_world @ vert.co for vert in verts]
        area_before = (
            (world_before[1] - world_before[0])
            .cross(world_before[2] - world_before[0])
            .length
            * 0.5
        )
        # Blender's face-area calculation treats some almost-collinear
        # triangles as zero even when the raw cross product is a few e-12.
        # Keep the threshold far below any visible patch, but above that
        # numerical-noise band.
        if area_before >= 1.0e-9:
            continue
        moves: list[float] = []
        for vert, world in zip(verts, world_before):
            if vert in already_projected:
                moves.append(0.0)
                continue
            nearest = bvh.find_nearest(world)
            if nearest is None:
                moves.append(0.0)
                continue
            location = nearest[0]
            moves.append((location - world).length)
            vert.co = inverse @ location
            already_projected.add(vert)
        world_after = [source.matrix_world @ vert.co for vert in verts]
        area_after = (
            (world_after[1] - world_after[0])
            .cross(world_after[2] - world_after[0])
            .length
            * 0.5
        )
        rows.append(
            {
                "area_before": area_before,
                "area_after": area_after,
                "max_vertex_move": max(moves),
                "mean_vertex_move": sum(moves) / len(moves),
            }
        )
    return rows


def attempt(
    source: bpy.types.Object,
    high: bpy.types.Object,
    method: str,
) -> dict[str, object]:
    bm = clone_bmesh(source)
    before_faces = set(bm.faces)
    boundary = [edge for edge in bm.edges if edge.is_boundary]
    error = None
    returned: list[bmesh.types.BMFace] = []
    extra: dict[str, object] = {}
    try:
        if method == "holes_fill_all":
            result = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
            returned = list(result.get("faces", []))
        elif method == "edgenet_fill_all":
            result = bmesh.ops.edgenet_fill(
                bm, edges=boundary, mat_nr=0, use_smooth=True, sides=0
            )
            returned = list(result.get("faces", []))
        elif method == "triangle_fill_all":
            result = bmesh.ops.triangle_fill(
                bm,
                edges=boundary,
                use_beauty=True,
                use_dissolve=False,
                normal=Vector((0.0, 0.0, 0.0)),
            )
            returned = [
                item
                for item in result.get("geom", [])
                if isinstance(item, bmesh.types.BMFace)
            ]
        elif method == "holes_fill_simple_only":
            returned = []
            for row in boundary_graphs(bm):
                if not row["simple_loop"]:
                    continue
                result = bmesh.ops.holes_fill(
                    bm, edges=list(row["edges"]), sides=0
                )
                returned.extend(result.get("faces", []))
        elif method == "holes_fill_iterative":
            returned, passes = fill_until_stable(bm)
            extra["passes"] = passes
        elif method == "project_degenerate_then_iterative_fill":
            projected = project_degenerate_cycles(bm, source, high)
            returned, passes = fill_until_stable(bm)
            extra["projected_degenerate_loops"] = projected
            extra["passes"] = passes
        elif method in {
            "cycles_project_degenerate_ngons",
            "cycles_project_degenerate_ngons_attributes",
            "cycles_project_degenerate_triangles",
        }:
            projected = project_degenerate_cycles(bm, source, high)
            extra["projected_degenerate_loops"] = projected
            for cycle in boundary_cycles(bm):
                if not cycle["closed"]:
                    continue
                if method in {
                    "cycles_project_degenerate_ngons",
                    "cycles_project_degenerate_ngons_attributes",
                }:
                    try:
                        returned.append(bm.faces.new(list(cycle["verts"])))
                    except ValueError:
                        pass
                else:
                    result = bmesh.ops.triangle_fill(
                        bm,
                        edges=list(cycle["edges"]),
                        use_beauty=True,
                        use_dissolve=False,
                        normal=Vector((0.0, 0.0, 0.0)),
                    )
                    returned.extend(
                        item
                        for item in result.get("geom", [])
                        if isinstance(item, bmesh.types.BMFace)
                    )
            if (
                method == "cycles_project_degenerate_ngons_attributes"
                and returned
            ):
                attribute_result = bmesh.ops.face_attribute_fill(
                    bm, faces=returned, use_normals=True, use_data=True
                )
                extra["attribute_fill_faces_failed"] = len(
                    attribute_result.get("faces_fail", [])
                )
        else:
            raise ValueError(method)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

    bm.faces.ensure_lookup_table()
    actually_new = [face for face in bm.faces if face not in before_faces]
    if actually_new:
        bmesh.ops.recalc_face_normals(bm, faces=actually_new)
    result = {
        "method": method,
        "error": error,
        **extra,
        "operator_returned_faces": face_metrics(returned, bm),
        "actually_new_faces": face_metrics(actually_new, bm),
        "after": base_metrics(bm),
    }
    bm.free()
    return result


def build_best_candidate(
    source: bpy.types.Object,
    high: bpy.types.Object,
) -> dict[str, object]:
    bm = clone_bmesh(source)
    before = base_metrics(bm)
    projected = project_degenerate_cycles(bm, source, high)
    cycles = boundary_cycles(bm)
    created: list[bmesh.types.BMFace] = []
    unclosed_cycles = 0
    for cycle in cycles:
        if not cycle["closed"]:
            unclosed_cycles += 1
            continue
        created.append(bm.faces.new(list(cycle["verts"])))
    bm.verts.index_update()
    created_vertex_sets = {
        frozenset(vert.index for vert in face.verts) for face in created
    }
    attribute_result = bmesh.ops.face_attribute_fill(
        bm, faces=created, use_normals=True, use_data=True
    )
    created_after_attribute_fill = [
        face
        for face in bm.faces
        if frozenset(vert.index for vert in face.verts) in created_vertex_sets
    ]
    created_metrics = face_metrics(created_after_attribute_fill, bm)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.normal_update()
    after = base_metrics(bm)
    signed_volume = bm.calc_volume(signed=True)
    bm.to_mesh(source.data)
    source.data.update()
    bm.free()
    source.name = "EXPERIMENT_ONLY__H31_CYCLE_PATCH"
    source["experiment_only"] = True
    source["source_fbx_untouched"] = True
    source["repair_method"] = (
        "boundary-cycle decomposition; project near-degenerate triangle "
        "cycles to accepted high surface; ngon patch; adjacent attribute "
        "fill; recalculate normals"
    )
    source["production_topology_approved"] = False
    source["requires_visual_uv_and_deformation_review"] = True
    return {
        "before": before,
        "cycle_count": len(cycles),
        "unclosed_cycles": unclosed_cycles,
        "projected_near_degenerate_cycle_count": len(projected),
        "projected_near_degenerate_cycles": projected,
        "created_faces": created_metrics,
        "attribute_fill_faces_failed": len(
            attribute_result.get("faces_fail", [])
        ),
        "signed_volume_after_recalculate_normals": signed_volume,
        "after": after,
    }


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    clear_scene()
    low = import_one(args.low.resolve(), "LOW")
    high = import_one(args.high.resolve(), "HIGH")
    high.hide_render = True
    high.hide_set(True)

    source_bm = clone_bmesh(low)
    source = base_metrics(source_bm)
    source_bm.free()
    methods = [
        "holes_fill_all",
        "holes_fill_simple_only",
        "holes_fill_iterative",
        "project_degenerate_then_iterative_fill",
        "cycles_project_degenerate_ngons",
        "cycles_project_degenerate_ngons_attributes",
        "cycles_project_degenerate_triangles",
        "edgenet_fill_all",
        "triangle_fill_all",
    ]
    report = {
        "low": str(args.low.resolve()),
        "high": str(args.high.resolve()),
        "source": source,
        "attempts": [attempt(low, high, method) for method in methods],
    }
    out = args.output / "automatic_fill_audit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.save_best:
        candidate_report = build_best_candidate(low, high)
        candidate_report["source_low"] = str(args.low.resolve())
        candidate_report["source_high"] = str(args.high.resolve())
        candidate_report["guardrail"] = (
            "Geometric closure is not approval of UV quality, deformation "
            "topology, animation readiness, or production use."
        )
        candidate_report_path = args.output / "cycle_patch_report.json"
        candidate_report_path.write_text(
            json.dumps(candidate_report, indent=2), encoding="utf-8"
        )
        bpy.data.objects.remove(high, do_unlink=True)
        bpy.ops.wm.save_as_mainfile(
            filepath=str(args.output / "cycle_patch_candidate.blend")
        )
        report["saved_candidate"] = str(
            args.output / "cycle_patch_candidate.blend"
        )
        report["saved_candidate_report"] = str(candidate_report_path)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
