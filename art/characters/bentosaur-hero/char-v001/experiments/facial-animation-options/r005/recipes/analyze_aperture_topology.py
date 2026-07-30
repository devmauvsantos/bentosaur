"""Read-only probe for an existing-edge aperture loop in the S40 face disk."""

from __future__ import annotations

import importlib.util
import json
from collections import defaultdict, deque
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "work/20_source_mouth_region_extraction.blend"
BUILDER = ROOT / "recipes/build_checkpoint30_static_transfer.py"
OUTPUT = ROOT / "qa/aperture_topology_probe.json"

spec = importlib.util.spec_from_file_location("cp30_builder", BUILDER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TRACE = module.APERTURE_TRACE_CCW


def inside_polygon(x, z, points, expand_x=0.0, expand_z=0.0):
    # Scaling about the authored mouth center gives bounded support probes.
    cx, cz = module.MOUTH_CENTER
    sx = 1.0 + expand_x
    sz = 1.0 + expand_z
    polygon = [
        (cx + (px - cx) * sx, cz + (pz - cz) * sz)
        for px, pz in points
    ]
    inside = False
    previous = polygon[-1]
    for current in polygon:
        x1, z1 = previous
        x2, z2 = current
        if ((z1 > z) != (z2 > z)) and (
            x < (x2 - x1) * (z - z1) / (z2 - z1) + x1
        ):
            inside = not inside
        previous = current
    return inside


def probe(mesh, scale):
    selected = {
        face.index
        for face in mesh.polygons
        if face.center.y <= -0.22
        and inside_polygon(
            face.center.x,
            face.center.z,
            TRACE,
            scale - 1.0,
            scale - 1.0,
        )
    }
    edge_faces = defaultdict(list)
    for face in mesh.polygons:
        for edge in face.edge_keys:
            edge_faces[tuple(sorted(edge))].append(face.index)
    neighbors = defaultdict(set)
    for linked in edge_faces.values():
        for face in linked:
            neighbors[face].update(other for other in linked if other != face)
    pending = set(selected)
    components = []
    while pending:
        seed = pending.pop()
        queue = deque([seed])
        group = {seed}
        while queue:
            current = queue.popleft()
            for neighbor in neighbors[current]:
                if neighbor in pending:
                    pending.remove(neighbor)
                    queue.append(neighbor)
                    group.add(neighbor)
        components.append(group)
    components.sort(key=len, reverse=True)
    primary = components[0] if components else set()
    boundary_edges = [
        edge
        for edge, linked in edge_faces.items()
        if sum(face in primary for face in linked) == 1
    ]
    adjacency = defaultdict(list)
    for first, second in boundary_edges:
        adjacency[first].append(second)
        adjacency[second].append(first)
    return {
        "scale": scale,
        "faces": len(selected),
        "components": [len(group) for group in components],
        "primary_faces": len(primary),
        "boundary_edges": len(boundary_edges),
        "boundary_vertices": len(adjacency),
        "degree_histogram": {
            str(degree): sum(
                len(neighbors) == degree for neighbors in adjacency.values()
            )
            for degree in sorted({len(v) for v in adjacency.values()})
        },
        "boundary_x_range": [
            min(mesh.vertices[index].co.x for index in adjacency),
            max(mesh.vertices[index].co.x for index in adjacency),
        ]
        if adjacency
        else [],
        "boundary_z_range": [
            min(mesh.vertices[index].co.z for index in adjacency),
            max(mesh.vertices[index].co.z for index in adjacency),
        ]
        if adjacency
        else [],
    }


def main():
    bpy.ops.wm.open_mainfile(filepath=str(CHECKPOINT))
    mesh = bpy.data.objects["S40_R003_PRODUCTION_BODY_LOCKED"].data
    report = {
        "probes": [
            probe(mesh, scale)
            for scale in (0.86, 0.90, 0.94, 0.98, 1.00, 1.04, 1.08)
        ]
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
