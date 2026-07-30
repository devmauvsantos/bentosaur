"""Read-only topology diagnostics for the frozen r005 a02 candidate."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Vector


REPO = Path("/Users/mauvsantos/Workspace/games/Bentosaur")
INPUT = (
    REPO
    / "art/characters/bentosaur-hero/char-v001/experiments/"
    "facial-animation-options/r005/work/"
    "30a02_TRIPO_OPEN_MOUTH_TRANSFER_STATIC.blend"
)
OUTPUT = (
    REPO
    / ".tmp/root/f0_broad_face_r006/qa/a02_geometry_diagnostic.json"
)
BODY = "BENTOSAUR_BODY_TRIPO_OPEN_MOUTH_CP30"


def edge_faces(mesh):
    result = defaultdict(list)
    for polygon in mesh.polygons:
        for edge in polygon.edge_keys:
            result[tuple(sorted(edge))].append(polygon.index)
    return result


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)] if ordered else 0.0


def main():
    bpy.ops.wm.open_mainfile(filepath=str(INPUT))
    obj = bpy.data.objects[BODY]
    mesh = obj.data
    role = mesh.attributes["cp30_role"]
    roles = defaultdict(set)
    for polygon in mesh.polygons:
        roles[int(role.data[polygon.index].value)].add(polygon.index)

    links = edge_faces(mesh)
    annulus_vertices = {
        vertex
        for face_index in roles[1]
        for vertex in mesh.polygons[face_index].vertices
    }
    cavity_vertices = {
        vertex
        for face_index in roles[2]
        for vertex in mesh.polygons[face_index].vertices
    }
    outside_vertices = {
        vertex
        for face_index in roles[0]
        for vertex in mesh.polygons[face_index].vertices
    }
    boundary_vertices = annulus_vertices & outside_vertices
    aperture_vertices = annulus_vertices & cavity_vertices
    adjacency = defaultdict(set)
    for edge in mesh.edges:
        a, b = edge.vertices
        if a in annulus_vertices and b in annulus_vertices:
            adjacency[a].add(b)
            adjacency[b].add(a)
    distances = {index: 0 for index in boundary_vertices}
    frontier = list(boundary_vertices)
    while frontier:
        current = frontier.pop(0)
        for neighbor in adjacency[current]:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                frontier.append(neighbor)
    ring_stats = {}
    for distance in sorted(set(distances.values())):
        indices = [index for index, value in distances.items() if value == distance]
        ring_stats[str(distance)] = {
            "count": len(indices),
            "x": [
                min(mesh.vertices[index].co.x for index in indices),
                max(mesh.vertices[index].co.x for index in indices),
            ],
            "y": [
                min(mesh.vertices[index].co.y for index in indices),
                max(mesh.vertices[index].co.y for index in indices),
            ],
            "z": [
                min(mesh.vertices[index].co.z for index in indices),
                max(mesh.vertices[index].co.z for index in indices),
            ],
        }
    seam = []
    for edge, faces in links.items():
        if len(faces) != 2:
            continue
        outer = next((index for index in faces if index in roles[0]), None)
        patch = next((index for index in faces if index in roles[1]), None)
        if outer is None or patch is None:
            continue
        angle = math.degrees(
            mesh.polygons[outer].normal.angle(mesh.polygons[patch].normal)
        )
        patch_inner = [
            index
            for index in mesh.polygons[patch].vertices
            if index not in edge
        ]
        midpoint = sum(
            (mesh.vertices[index].co for index in edge), Vector()
        ) / 2.0
        seam.append(
            {
                "edge": edge,
                "outer_face": outer,
                "patch_face": patch,
                "angle_deg": angle,
                "midpoint": list(midpoint),
                "outer_edge_coords": [
                    list(mesh.vertices[index].co) for index in edge
                ],
                "first_inner_coords": [
                    list(mesh.vertices[index].co) for index in patch_inner
                ],
            }
        )

    patch_faces = roles[1] | roles[2] | roles[3]
    inverted_y = [
        {
            "face": index,
            "role": int(role.data[index].value),
            "normal": list(mesh.polygons[index].normal),
            "center": list(mesh.polygons[index].center),
        }
        for index in patch_faces
        if int(role.data[index].value) == 1
        and mesh.polygons[index].normal.y > 0.0
    ]

    report = {
        "input": str(INPUT),
        "annulus_ring_stats": ring_stats,
        "aperture_distance_values": sorted(
            {distances[index] for index in aperture_vertices}
        ),
        "seam_count": len(seam),
        "seam_mean": sum(item["angle_deg"] for item in seam) / len(seam),
        "seam_p95": percentile([item["angle_deg"] for item in seam], 0.95),
        "seam_max": max(item["angle_deg"] for item in seam),
        "seam_worst": sorted(
            seam, key=lambda item: item["angle_deg"], reverse=True
        )[:24],
        "skin_annulus_positive_y_normals": inverted_y,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
