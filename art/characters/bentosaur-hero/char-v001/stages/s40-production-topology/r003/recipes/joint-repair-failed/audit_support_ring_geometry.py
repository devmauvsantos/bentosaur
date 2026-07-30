"""Measure rest-shape quality of the newly inserted support-ring geometry."""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "qa" / "support_ring_geometry_audit.json"
INDEX_REPORT = ROOT / "qa" / "paired_new_vertex_indices.json"
TARGET = "BENTOSAUR_JOINT_REPAIR_CANDIDATE_NOT_APPROVED"
ORIGINAL_VERTEX_COUNT = 10050


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)]


def stats(values: list[float]) -> dict:
    return {
        "count": len(values),
        "minimum": min(values),
        "p01": percentile(values, 0.01),
        "p05": percentile(values, 0.05),
        "median": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
        "maximum": max(values),
    }


obj = bpy.data.objects.get(TARGET)
if obj is None or obj.type != "MESH":
    raise RuntimeError(f"Missing candidate: {TARGET}")
mesh = obj.data
points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
edge_lengths = [
    (points[edge.vertices[0]] - points[edge.vertices[1]]).length
    for edge in mesh.edges
]
new_edge_lengths = [
    (points[edge.vertices[0]] - points[edge.vertices[1]]).length
    for edge in mesh.edges
    if any(index >= ORIGINAL_VERTEX_COUNT for index in edge.vertices)
]
old_edge_lengths = [
    (points[edge.vertices[0]] - points[edge.vertices[1]]).length
    for edge in mesh.edges
    if all(index < ORIGINAL_VERTEX_COUNT for index in edge.vertices)
]

new_faces = [
    poly
    for poly in mesh.polygons
    if any(index >= ORIGINAL_VERTEX_COUNT for index in poly.vertices)
]
old_faces = [
    poly
    for poly in mesh.polygons
    if all(index < ORIGINAL_VERTEX_COUNT for index in poly.vertices)
]


def face_aspect(poly) -> float:
    verts = list(poly.vertices)
    lengths = [
        (points[verts[index]] - points[verts[(index + 1) % len(verts)]]).length
        for index in range(len(verts))
    ]
    return max(lengths) / max(min(lengths), 1.0e-12)


indices = json.loads(INDEX_REPORT.read_text(encoding="utf-8"))
region_results = {}
for name, region_indices in indices["by_region"].items():
    region_set = set(region_indices)
    faces = [
        poly
        for poly in mesh.polygons
        if any(index in region_set for index in poly.vertices)
    ]
    edges = [
        edge
        for edge in mesh.edges
        if any(index in region_set for index in edge.vertices)
    ]
    region_results[name] = {
        "incident_faces": len(faces),
        "incident_edges": len(edges),
        "face_area": stats([poly.area for poly in faces]),
        "face_edge_aspect": stats([face_aspect(poly) for poly in faces]),
        "edge_length": stats(
            [
                (points[edge.vertices[0]] - points[edge.vertices[1]]).length
                for edge in edges
            ]
        ),
    }

report = {
    "candidate": bpy.data.filepath,
    "interpretation": (
        "Rest-shape geometry only; deformation verdict remains authoritative "
        "in bounded_deformation_reprobe_report.json"
    ),
    "all_edge_length": stats(edge_lengths),
    "preserved_edge_length": stats(old_edge_lengths),
    "new_incident_edge_length": stats(new_edge_lengths),
    "preserved_face_area": stats([poly.area for poly in old_faces]),
    "new_incident_face_area": stats([poly.area for poly in new_faces]),
    "preserved_face_edge_aspect": stats([face_aspect(poly) for poly in old_faces]),
    "new_incident_face_edge_aspect": stats([face_aspect(poly) for poly in new_faces]),
    "new_incident_faces_with_aspect_above_10": sum(
        face_aspect(poly) > 10.0 for poly in new_faces
    ),
    "new_incident_edges_below_35_percent_preserved_median": sum(
        length < 0.35 * percentile(old_edge_lengths, 0.50)
        for length in new_edge_lengths
    ),
    "regions": region_results,
}
OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
