"""Inspect candidate existing S40 face boundaries without editing the mesh."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "work/20_source_mouth_region_extraction.blend"
OUTPUT = ROOT / "qa/body_patch_boundary_candidates.json"


def components(face_indices, face_neighbors):
    pending = set(face_indices)
    result = []
    while pending:
        seed = min(pending)
        pending.remove(seed)
        queue = deque([seed])
        component = [seed]
        while queue:
            face = queue.popleft()
            for neighbor in face_neighbors[face]:
                if neighbor in pending:
                    pending.remove(neighbor)
                    queue.append(neighbor)
                    component.append(neighbor)
        result.append(sorted(component))
    return sorted(result, key=len, reverse=True)


def boundary_cycles(mesh, selected):
    selected = set(selected)
    edge_faces = defaultdict(list)
    for polygon in mesh.polygons:
        for edge_key in polygon.edge_keys:
            edge_faces[tuple(sorted(edge_key))].append(polygon.index)
    boundary = []
    for edge_key, linked in edge_faces.items():
        selected_linked = sum(index in selected for index in linked)
        if selected_linked == 1:
            boundary.append(edge_key)

    adjacency = defaultdict(list)
    for a, b in boundary:
        adjacency[a].append(b)
        adjacency[b].append(a)
    cycles = []
    remaining = set(boundary)
    while remaining:
        start_edge = min(remaining)
        remaining.remove(start_edge)
        start, current = start_edge
        cycle = [start, current]
        previous = start
        while current != start:
            candidates = [
                neighbor
                for neighbor in adjacency[current]
                if neighbor != previous
                and tuple(sorted((current, neighbor))) in remaining
            ]
            if not candidates:
                break
            next_vertex = min(candidates)
            remaining.remove(tuple(sorted((current, next_vertex))))
            previous, current = current, next_vertex
            cycle.append(current)
        cycles.append(cycle)
    return cycles


def inspect(mesh, spec):
    selected = []
    for polygon in mesh.polygons:
        center = polygon.center
        if (
            abs(center.x) <= spec["half_width"]
            and spec["z_min"] <= center.z <= spec["z_max"]
            and center.y <= spec["front_y_max"]
        ):
            selected.append(polygon.index)

    edge_faces = defaultdict(list)
    for polygon in mesh.polygons:
        for edge_key in polygon.edge_keys:
            edge_faces[tuple(sorted(edge_key))].append(polygon.index)
    neighbors = defaultdict(set)
    for linked in edge_faces.values():
        for face in linked:
            neighbors[face].update(other for other in linked if other != face)
    groups = components(selected, neighbors)
    primary = groups[0] if groups else []
    cycles = boundary_cycles(mesh, primary)
    cycle_reports = []
    for cycle in cycles:
        points = [mesh.vertices[index].co for index in cycle]
        cycle_reports.append(
            {
                "vertices": len(cycle) - int(cycle[-1] == cycle[0]),
                "closed": bool(cycle and cycle[-1] == cycle[0]),
                "degree_all_two": all(
                    len(
                        {
                            edge
                            for edge in mesh.vertices[index].link_edges
                        }
                    )
                    >= 2
                    for index in set(cycle)
                )
                if False
                else None,
                "x_range": [min(p.x for p in points), max(p.x for p in points)],
                "y_range": [min(p.y for p in points), max(p.y for p in points)],
                "z_range": [min(p.z for p in points), max(p.z for p in points)],
                "indices": cycle,
            }
        )
    return {
        "spec": spec,
        "selected_faces": len(selected),
        "components": [len(group) for group in groups],
        "primary_faces": len(primary),
        "boundary_cycles": cycle_reports,
    }


def inspect_ellipse(mesh, spec):
    selected = []
    for polygon in mesh.polygons:
        center = polygon.center
        inside = (
            (center.x / spec["radius_x"]) ** 2
            + ((center.z - spec["center_z"]) / spec["radius_z"]) ** 2
            <= 1.0
        )
        if inside and center.y <= spec["front_y_max"]:
            selected.append(polygon.index)

    edge_faces = defaultdict(list)
    for polygon in mesh.polygons:
        for edge_key in polygon.edge_keys:
            edge_faces[tuple(sorted(edge_key))].append(polygon.index)
    neighbors = defaultdict(set)
    for linked in edge_faces.values():
        for face in linked:
            neighbors[face].update(other for other in linked if other != face)
    groups = components(selected, neighbors)
    primary = groups[0] if groups else []
    cycles = boundary_cycles(mesh, primary)
    return {
        "spec": spec,
        "selected_faces": len(selected),
        "components": [len(group) for group in groups],
        "primary_faces": len(primary),
        "boundary_cycles": [
            {
                "vertices": len(cycle) - int(cycle[-1] == cycle[0]),
                "closed": bool(cycle and cycle[-1] == cycle[0]),
                "x_range": [
                    min(mesh.vertices[index].co.x for index in cycle),
                    max(mesh.vertices[index].co.x for index in cycle),
                ],
                "y_range": [
                    min(mesh.vertices[index].co.y for index in cycle),
                    max(mesh.vertices[index].co.y for index in cycle),
                ],
                "z_range": [
                    min(mesh.vertices[index].co.z for index in cycle),
                    max(mesh.vertices[index].co.z for index in cycle),
                ],
                "indices": cycle,
            }
            for cycle in cycles
        ],
    }


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(CHECKPOINT))
    body = bpy.data.objects["S40_R003_PRODUCTION_BODY_LOCKED"]
    specs = []
    for half_width in (0.115, 0.125, 0.135):
        for z_min, z_max in (
            (0.375, 0.555),
            (0.385, 0.555),
            (0.395, 0.565),
        ):
            for front_y_max in (-0.30, -0.26, -0.22, -0.18):
                specs.append(
                    {
                        "half_width": half_width,
                        "z_min": z_min,
                        "z_max": z_max,
                        "front_y_max": front_y_max,
                    }
                )
    report = {
        "body": body.name,
        "vertices": len(body.data.vertices),
        "faces": len(body.data.polygons),
        "candidates": [inspect(body.data, spec) for spec in specs],
        "ellipse_candidates": [
            inspect_ellipse(
                body.data,
                {
                    "radius_x": radius_x,
                    "radius_z": radius_z,
                    "center_z": 0.475,
                    "front_y_max": front_y,
                },
            )
            for radius_x, radius_z in ((0.115, 0.078), (0.125, 0.085))
            for front_y in (-0.30, -0.26, -0.22, -0.18, 0.0)
        ],
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
