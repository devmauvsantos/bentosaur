"""Analyze independent boundary cycles in a Tripo mesh.

Unlike connected-component counts, a cycle basis separates figure-eight
boundary networks where two holes share one vertex. This is a read-only tool.
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


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_mesh(path: Path) -> bpy.types.Object:
    if path.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    elif path.suffix.lower() in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        raise RuntimeError(f"Unsupported input: {path.suffix}")
    meshes = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if len(meshes) != 1:
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"Expected one mesh, found {len(meshes)}")
    return meshes[0]


def cycle_basis(
    vertices: set[bmesh.types.BMVert],
    adjacency: dict[bmesh.types.BMVert, set[bmesh.types.BMVert]],
) -> list[list[bmesh.types.BMVert]]:
    remaining = set(vertices)
    cycles: list[list[bmesh.types.BMVert]] = []
    while remaining:
        root = remaining.pop()
        stack = [root]
        predecessor = {root: root}
        used: dict[bmesh.types.BMVert, set[bmesh.types.BMVert]] = {root: set()}
        while stack:
            current = stack.pop()
            current_used = used[current]
            for neighbor in adjacency[current]:
                if neighbor not in used:
                    predecessor[neighbor] = current
                    stack.append(neighbor)
                    used[neighbor] = {current}
                elif neighbor == current:
                    cycles.append([current])
                elif neighbor not in current_used:
                    neighbor_used = used[neighbor]
                    cycle = [neighbor, current]
                    parent = predecessor[current]
                    while parent not in neighbor_used:
                        cycle.append(parent)
                        parent = predecessor[parent]
                    cycle.append(parent)
                    cycles.append(cycle)
                    used[neighbor].add(current)
        remaining.difference_update(predecessor)
    return cycles


def polygon_area(points: list[Vector]) -> float:
    area_vector = Vector()
    for index, point in enumerate(points):
        area_vector += point.cross(points[(index + 1) % len(points)])
    return 0.5 * area_vector.length


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    clear_scene()
    obj = import_mesh(source)

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    boundary_edges = [edge for edge in bm.edges if edge.is_boundary]
    boundary_vertices = {vert for edge in boundary_edges for vert in edge.verts}
    adjacency = {vert: set() for vert in boundary_vertices}
    edge_by_pair: dict[frozenset[bmesh.types.BMVert], bmesh.types.BMEdge] = {}
    for edge in boundary_edges:
        first, second = edge.verts
        adjacency[first].add(second)
        adjacency[second].add(first)
        edge_by_pair[frozenset((first, second))] = edge

    cycles = cycle_basis(boundary_vertices, adjacency)
    rows: list[dict[str, object]] = []
    for cycle_index, cycle in enumerate(cycles, start=1):
        points = [obj.matrix_world @ vert.co for vert in cycle]
        edge_lengths = [
            (
                points[index] - points[(index + 1) % len(points)]
            ).length
            for index in range(len(points))
        ]
        centroid = sum(points, Vector()) / len(points)
        area = polygon_area(points)
        rows.append(
            {
                "cycle": cycle_index,
                "vertex_count": len(cycle),
                "vertex_indices": [vert.index for vert in cycle],
                "area": area,
                "degenerate": area <= 1e-10,
                "centroid": list(centroid),
                "edge_lengths": edge_lengths,
                "minimum_edge_length": min(edge_lengths),
                "maximum_edge_length": max(edge_lengths),
                "perimeter": sum(edge_lengths),
            }
        )

    zero_area_faces = 0
    minimum_face_area = math.inf
    for face in bm.faces:
        area = face.calc_area()
        minimum_face_area = min(minimum_face_area, area)
        if area <= 1e-12:
            zero_area_faces += 1

    report = {
        "source": str(source),
        "boundary_edges": len(boundary_edges),
        "boundary_vertices": len(boundary_vertices),
        "boundary_cycle_rank": (
            len(boundary_edges) - len(boundary_vertices)
            + sum(
                1
                for _ in _connected_roots(boundary_vertices, adjacency)
            )
        ),
        "cycle_count": len(cycles),
        "degenerate_cycle_count": sum(row["degenerate"] for row in rows),
        "cycles": sorted(rows, key=lambda row: row["area"], reverse=True),
        "existing_zero_area_faces": zero_area_faces,
        "minimum_existing_face_area": minimum_face_area,
    }
    bm.free()
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "success", "report": str(output)}))


def _connected_roots(
    vertices: set[bmesh.types.BMVert],
    adjacency: dict[bmesh.types.BMVert, set[bmesh.types.BMVert]],
):
    remaining = set(vertices)
    while remaining:
        root = remaining.pop()
        yield root
        stack = [root]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)


if __name__ == "__main__":
    main()
