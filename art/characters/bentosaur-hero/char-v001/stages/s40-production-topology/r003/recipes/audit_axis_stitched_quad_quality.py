"""Quad quality audit for the closed axis-aligned symmetric QF candidate."""

from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent / "axis-qf-seam-stitch"


def percentile(values: list[float], fraction: float) -> float:
    values = sorted(values)
    return values[min(len(values) - 1, math.ceil(len(values) * fraction) - 1)]


def distribution(values: list[float]) -> dict:
    return {
        "count": len(values),
        "minimum": min(values),
        "mean": sum(values) / len(values),
        "median": percentile(values, 0.5),
        "p95": percentile(values, 0.95),
        "maximum": max(values),
    }


def angle(first: Vector, second: Vector) -> float:
    if first.length <= 1.0e-12 or second.length <= 1.0e-12:
        return 0.0
    return math.degrees(first.angle(second))


def metrics(face: bmesh.types.BMFace, obj: bpy.types.Object) -> dict:
    points = [obj.matrix_world @ vert.co for vert in face.verts]
    lengths = [
        (points[(index + 1) % 4] - points[index]).length for index in range(4)
    ]
    angles = [
        angle(
            points[(index - 1) % 4] - points[index],
            points[(index + 1) % 4] - points[index],
        )
        for index in range(4)
    ]
    first = (points[1] - points[0]).cross(points[2] - points[0])
    second = (points[2] - points[0]).cross(points[3] - points[0])
    return {
        "aspect_ratio": max(lengths) / max(min(lengths), 1.0e-12),
        "maximum_corner_skew_degrees": max(abs(value - 90.0) for value in angles),
        "minimum_corner_angle_degrees": min(angles),
        "maximum_corner_angle_degrees": max(angles),
        "diagonal_warpage_degrees": angle(first, second),
        "area": face.calc_area(),
    }


obj = next(obj for obj in bpy.context.scene.objects if obj.type == "MESH")
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
if any(len(face.verts) != 4 for face in bm.faces):
    raise RuntimeError("Candidate is not all-quads")
seam_faces = [
    face
    for face in bm.faces
    if any(abs((obj.matrix_world @ vert.co).y) <= 1.0e-6 for vert in face.verts)
]
seam_set = set(seam_faces)
off_seam_faces = [face for face in bm.faces if face not in seam_set]
groups = {
    "all_quads": [metrics(face, obj) for face in bm.faces],
    "seam_quads": [metrics(face, obj) for face in seam_faces],
    "off_seam_quads": [metrics(face, obj) for face in off_seam_faces],
}
metric_names = list(groups["all_quads"][0])
seam_rows_with_faces = [
    (face, metrics(face, obj))
    for face in seam_faces
]
valence_all = Counter(len(vert.link_edges) for vert in bm.verts)
seam_vertices = {vert for face in seam_faces for vert in face.verts}
valence_seam = Counter(len(vert.link_edges) for vert in seam_vertices)
report = {
    "schema_version": "1.0.0",
    "candidate": bpy.data.filepath,
    "counts": {
        "vertices": len(bm.verts),
        "faces": len(bm.faces),
        "seam_faces": len(seam_faces),
        "seam_vertices": len(seam_vertices),
    },
    "seam_face_indices": sorted(face.index for face in seam_faces),
    "quality": {
        group: {
            metric: distribution([row[metric] for row in rows])
            for metric in metric_names
        }
        for group, rows in groups.items()
    },
    "seam_outliers": {
        "highest_aspect_ratio": [
            {
                "face": face.index,
                "center": list(obj.matrix_world @ face.calc_center_median()),
                **row,
            }
            for face, row in sorted(
                seam_rows_with_faces,
                key=lambda item: -item[1]["aspect_ratio"],
            )[:12]
        ],
        "highest_warpage": [
            {
                "face": face.index,
                "center": list(obj.matrix_world @ face.calc_center_median()),
                **row,
            }
            for face, row in sorted(
                seam_rows_with_faces,
                key=lambda item: -item[1]["diagonal_warpage_degrees"],
            )[:12]
        ],
        "valence_2_vertices": [
            {
                "vertex": vert.index,
                "coordinate": list(obj.matrix_world @ vert.co),
            }
            for vert in bm.verts
            if len(vert.link_edges) == 2
        ],
    },
    "valence": {
        "all_vertices": {str(key): value for key, value in sorted(valence_all.items())},
        "seam_vertices": {str(key): value for key, value in sorted(valence_seam.items())},
        "all_valence_3_to_5_ratio": (
            sum(valence_all.get(value, 0) for value in (3, 4, 5)) / len(bm.verts)
        ),
        "seam_valence_3_to_5_ratio": (
            sum(valence_seam.get(value, 0) for value in (3, 4, 5))
            / len(seam_vertices)
        ),
    },
}
bm.free()
path = ROOT / "quad_quality_audit.json"
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(
    json.dumps(
        {
            "counts": report["counts"],
            "seam_quality": report["quality"]["seam_quads"],
            "valence": report["valence"],
        },
        indent=2,
    )
)
