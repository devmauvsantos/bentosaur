"""Read-only integrity diagnosis for the frozen Checkpoint 30 a02 candidate."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

import bpy
from mathutils.bvhtree import BVHTree


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "work/30a02_TRIPO_OPEN_MOUTH_TRANSFER_STATIC.blend"
OUTPUT = ROOT / "qa/checkpoint30_a02_readonly_integrity.json"
BODY = "BENTOSAUR_BODY_TRIPO_OPEN_MOUTH_CP30"
TONGUE = "BENTOSAUR_TONGUE_SEPARATE_CLOSED_CP30"


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return float(ordered[round((len(ordered) - 1) * fraction)])


def face_aspect(mesh, polygon):
    vertices = list(polygon.vertices)
    lengths = [
        (
            mesh.vertices[vertices[index]].co
            - mesh.vertices[vertices[(index + 1) % len(vertices)]].co
        ).length
        for index in range(len(vertices))
    ]
    return max(lengths) / min(lengths)


def directed_edge(face_vertices, edge):
    vertices = list(face_vertices)
    for index, first in enumerate(vertices):
        second = vertices[(index + 1) % len(vertices)]
        if {first, second} == set(edge):
            return (first, second)
    raise RuntimeError("Edge not found in polygon")


def main():
    bpy.ops.wm.open_mainfile(filepath=str(INPUT))
    body = bpy.data.objects[BODY]
    tongue = bpy.data.objects[TONGUE]
    mesh = body.data
    mesh.calc_loop_triangles()
    roles = mesh.attributes["cp30_role"]
    role = {
        polygon.index: int(roles.data[polygon.index].value)
        for polygon in mesh.polygons
    }

    aspects = []
    for polygon in mesh.polygons:
        if role[polygon.index] > 0:
            aspects.append(
                {
                    "face": polygon.index,
                    "role": role[polygon.index],
                    "aspect": face_aspect(mesh, polygon),
                    "center": list(polygon.center),
                    "area": polygon.area,
                }
            )
    aspects.sort(key=lambda item: item["aspect"], reverse=True)

    edge_faces = defaultdict(list)
    for polygon in mesh.polygons:
        for edge in polygon.edge_keys:
            edge_faces[tuple(sorted(edge))].append(polygon.index)
    inconsistent = []
    seam_angles = []
    for edge, linked in edge_faces.items():
        if len(linked) != 2:
            continue
        first, second = linked
        first_direction = directed_edge(mesh.polygons[first].vertices, edge)
        second_direction = directed_edge(mesh.polygons[second].vertices, edge)
        if first_direction == second_direction:
            inconsistent.append(
                {
                    "edge": edge,
                    "faces": linked,
                    "roles": [role[first], role[second]],
                }
            )
        if sorted((role[first], role[second])) == [0, 1]:
            angle = math.degrees(
                mesh.polygons[first].normal.angle(mesh.polygons[second].normal)
            )
            seam_angles.append(
                {
                    "edge": edge,
                    "faces": linked,
                    "angle_deg": angle,
                    "midpoint": list(
                        0.5
                        * (
                            mesh.vertices[edge[0]].co
                            + mesh.vertices[edge[1]].co
                        )
                    ),
                }
            )
    seam_angles.sort(key=lambda item: item["angle_deg"], reverse=True)

    triangles = [tuple(loop.vertices) for loop in mesh.loop_triangles]
    triangle_polygons = [
        int(loop.polygon_index) for loop in mesh.loop_triangles
    ]
    bvh = BVHTree.FromPolygons(
        [vertex.co for vertex in mesh.vertices],
        triangles,
        all_triangles=True,
    )
    candidate_intersections = []
    seen = set()
    for first, second in bvh.overlap(bvh):
        if first == second:
            continue
        pair = tuple(sorted((int(first), int(second))))
        if pair in seen:
            continue
        seen.add(pair)
        first_vertices = set(triangles[pair[0]])
        second_vertices = set(triangles[pair[1]])
        if first_vertices & second_vertices:
            continue
        first_polygon = triangle_polygons[pair[0]]
        second_polygon = triangle_polygons[pair[1]]
        if role[first_polygon] == 0 and role[second_polygon] == 0:
            continue
        candidate_intersections.append(
            {
                "triangles": pair,
                "polygons": [first_polygon, second_polygon],
                "roles": [role[first_polygon], role[second_polygon]],
            }
        )

    cap_vertices = {
        index
        for polygon in mesh.polygons
        if role[polygon.index] == 3
        for index in polygon.vertices
    }
    wall_vertices = {
        index
        for polygon in mesh.polygons
        if role[polygon.index] == 2
        for index in polygon.vertices
    }
    annulus_vertices = {
        index
        for polygon in mesh.polygons
        if role[polygon.index] == 1
        for index in polygon.vertices
    }
    aperture_vertices = annulus_vertices & wall_vertices
    back_vertices = wall_vertices & cap_vertices
    aperture_y = [mesh.vertices[index].co.y for index in aperture_vertices]
    cap_y = [mesh.vertices[index].co.y for index in cap_vertices]

    tongue_center_x = mean(vertex.co.x for vertex in tongue.data.vertices)
    report = {
        "status": "frozen_a02_readonly_diagnosis",
        "candidate": str(INPUT),
        "patch_roles": {
            "annulus": sum(value == 1 for value in role.values()),
            "wall": sum(value == 2 for value in role.values()),
            "cap": sum(value == 3 for value in role.values()),
        },
        "aspect": {
            "mean": mean(item["aspect"] for item in aspects),
            "p95": percentile(
                [item["aspect"] for item in aspects], 0.95
            ),
            "max": aspects[0]["aspect"],
            "over_6": sum(item["aspect"] > 6.0 for item in aspects),
            "worst_20": aspects[:20],
        },
        "orientation": {
            "inconsistent_directed_edges": len(inconsistent),
            "inconsistent_by_role_pair": {
                str(pair): sum(
                    sorted(item["roles"]) == list(pair)
                    for item in inconsistent
                )
                for pair in ((0, 1), (1, 2), (2, 3))
            },
            "examples": inconsistent[:20],
        },
        "seam": {
            "count": len(seam_angles),
            "mean_angle_deg": mean(
                item["angle_deg"] for item in seam_angles
            ),
            "p95_angle_deg": percentile(
                [item["angle_deg"] for item in seam_angles], 0.95
            ),
            "max_angle_deg": seam_angles[0]["angle_deg"],
            "over_30_deg": sum(
                item["angle_deg"] > 30.0 for item in seam_angles
            ),
            "worst_20": seam_angles[:20],
        },
        "self_intersection": {
            "vertex_disjoint_patch_involved_triangle_pairs": len(
                candidate_intersections
            ),
            "examples": candidate_intersections[:50],
            "interpretation": (
                "BVH triangle-overlap candidates after excluding shared-vertex "
                "adjacency and outside/outside pairs."
            ),
        },
        "profile_concavity": {
            "aperture_y_range": [min(aperture_y), max(aperture_y)],
            "back_perimeter_y_range": [
                min(mesh.vertices[index].co.y for index in back_vertices),
                max(mesh.vertices[index].co.y for index in back_vertices),
            ],
            "cap_y_range": [min(cap_y), max(cap_y)],
            "deepest_positive_y_delta_from_aperture_front": (
                max(cap_y) - min(aperture_y)
            ),
        },
        "tongue": {
            "center_x": tongue_center_x,
            "absolute_center_x": abs(tongue_center_x),
        },
        "verdict": {
            "visual_shape": "promising_tripo_like_open_smile",
            "production_gate": "fail",
            "blockers": [
                "outer seam fold/tear visible below both mouth corners",
                "patch aspect P95/max exceed gate",
                "seam normal P95/max exceed gate",
            ],
            "further_attempt_made": False,
        },
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
