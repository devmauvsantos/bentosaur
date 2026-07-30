"""Independent final closed-shell integrity audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bmesh
import bpy


ROOT = Path(__file__).resolve().parent / "axis-qf-seam-stitch"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


path = Path(bpy.data.filepath).resolve()
obj = next(obj for obj in bpy.context.scene.objects if obj.type == "MESH")
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
remaining = set(bm.faces)
component_sizes = []
while remaining:
    seed = remaining.pop()
    component = {seed}
    stack = [seed]
    while stack:
        face = stack.pop()
        neighbors = {
            other
            for edge in face.edges
            for other in edge.link_faces
            if other in remaining
        }
        for other in neighbors:
            remaining.remove(other)
            component.add(other)
            stack.append(other)
    component_sizes.append(len(component))
report = {
    "candidate": str(path),
    "sha256": sha256(path),
    "vertices": len(bm.verts),
    "edges": len(bm.edges),
    "faces": len(bm.faces),
    "euler_characteristic": len(bm.verts) - len(bm.edges) + len(bm.faces),
    "connected_face_components": len(component_sizes),
    "component_face_counts": sorted(component_sizes, reverse=True),
    "loose_vertices": sum(not vert.link_edges for vert in bm.verts),
    "loose_edges": sum(not edge.link_faces for edge in bm.edges),
    "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
    "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
    "zero_length_edges": sum(edge.calc_length() <= 1.0e-12 for edge in bm.edges),
    "zero_area_faces": sum(face.calc_area() <= 1.0e-12 for face in bm.faces),
    "signed_volume": bm.calc_volume(signed=True),
    "absolute_volume": bm.calc_volume(signed=False),
}
bm.free()
report["acceptance"] = {
    "single_shell": report["connected_face_components"] == 1,
    "sphere_euler_characteristic": report["euler_characteristic"] == 2,
    "no_loose_geometry": report["loose_vertices"] == 0 and report["loose_edges"] == 0,
    "closed_manifold": report["boundary_edges"] == 0
    and report["non_manifold_edges"] == 0,
    "nondegenerate": report["zero_length_edges"] == 0
    and report["zero_area_faces"] == 0,
    "positive_orientation": report["signed_volume"] > 0.0,
}
(ROOT / "final_integrity_audit.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(report, indent=2))
