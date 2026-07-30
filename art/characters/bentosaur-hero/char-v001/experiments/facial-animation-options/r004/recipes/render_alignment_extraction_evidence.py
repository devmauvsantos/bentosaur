"""Render evidence for the frozen alignment/extraction checkpoint.

This opens checkpoint 20 read-only, creates render-only wire and deviation
duplicates in memory, and emits evidence images.  It does not save a new
geometry checkpoint and does not edit the production body or Tripo source.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def repository_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError(f"No Git repository found above {start}")


CANDIDATE = Path(__file__).resolve().parents[1]
ROOT = repository_root(CANDIDATE)
CHECKPOINT = CANDIDATE / "work/20_source_mouth_region_extraction.blend"
RENDERS = CANDIDATE / "evidence/renders"
QA = CANDIDATE / "qa"
BODY = "S40_R003_PRODUCTION_BODY_LOCKED"
SOURCE = "TRIPO_VG06_OPEN_SOURCE_LOCKED"
REGION = "TRIPO_VG06_MOUTH_REGION_SOURCE_LOCKED"


def material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.65,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    principled = result.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    if emission_strength > 0.0:
        principled.inputs["Emission Color"].default_value = color
        principled.inputs["Emission Strength"].default_value = emission_strength
    return result


def assign_only(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.material_index = 0


def look_at(
    obj: bpy.types.Object,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
) -> None:
    obj.location = location
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_scene() -> tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object]:
    bpy.ops.wm.open_mainfile(filepath=str(CHECKPOINT))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("EVIDENCE_WORLD")
    scene.world.color = (0.012, 0.015, 0.022)

    body = bpy.data.objects[BODY]
    source = bpy.data.objects[SOURCE]
    region = bpy.data.objects[REGION]
    for obj in (body, source, region):
        obj.hide_viewport = False
        obj.hide_render = False

    sage = material(
        "RENDER_OPEN_SOURCE_SAGE",
        (0.19, 0.48, 0.34, 1.0),
        0.82,
    )
    assign_only(source, sage)
    body.hide_render = True
    region.hide_render = True

    wire = body.copy()
    wire.data = body.data.copy()
    wire.name = "RENDER_ONLY_S40_BODY_WIRE"
    bpy.context.scene.collection.objects.link(wire)
    wire.location.y -= 0.0016
    wire_material = material(
        "RENDER_BODY_WIRE_CORAL",
        (1.0, 0.22, 0.08, 1.0),
        0.35,
        1.1,
    )
    assign_only(wire, wire_material)
    modifier = wire.modifiers.new("render_only_wire", "WIREFRAME")
    modifier.thickness = 0.0008
    modifier.use_replace = True

    region_wire = region.copy()
    region_wire.data = region.data.copy()
    region_wire.name = "RENDER_ONLY_SOURCE_REGION_WIRE"
    bpy.context.scene.collection.objects.link(region_wire)
    region_wire.location.y -= 0.0018
    region_material = material(
        "RENDER_SOURCE_REGION_GOLD",
        (1.0, 0.62, 0.05, 1.0),
        0.35,
        1.2,
    )
    assign_only(region_wire, region_material)
    region_modifier = region_wire.modifiers.new(
        "render_only_region_wire", "WIREFRAME"
    )
    region_modifier.thickness = 0.00045
    region_modifier.use_replace = True
    region_wire.hide_render = True

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "EVIDENCE_CAMERA"
    camera.data.type = "ORTHO"
    scene.camera = camera

    light_specs = (
        ("KEY", (-1.5, -2.0, 2.3), 900.0, 1.7),
        ("FILL", (1.7, -1.1, 1.3), 650.0, 1.4),
        ("RIM", (0.3, 1.7, 2.0), 850.0, 1.2),
    )
    for name, location, energy, size in light_specs:
        bpy.ops.object.light_add(type="AREA", location=location)
        lamp = bpy.context.object
        lamp.name = f"EVIDENCE_{name}"
        lamp.data.energy = energy
        lamp.data.shape = "DISK"
        lamp.data.size = size
        look_at(lamp, location, (0.0, 0.0, 0.48))

    return camera, wire, region_wire


def render(
    camera: bpy.types.Object,
    filename: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    ortho_scale: float,
) -> None:
    look_at(camera, location, target)
    camera.data.ortho_scale = ortho_scale
    bpy.context.scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)


def deviation_heatmap(source: bpy.types.Object, body: bpy.types.Object) -> dict:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(source.evaluated_get(depsgraph), depsgraph)
    distances: list[float] = []
    vertex_distances: dict[int, float] = {}
    for vertex in body.data.vertices:
        point = body.matrix_world @ vertex.co
        if (
            abs(point.x) <= 0.14
            and -0.46 <= point.y <= -0.17
            and 0.375 <= point.z <= 0.595
        ):
            nearest = bvh.find_nearest(point)
            if nearest is not None:
                value = float(nearest[3])
                vertex_distances[vertex.index] = value
                distances.append(value)

    colors = (
        (0.05, 0.32, 0.10, 1.0),
        (0.20, 0.66, 0.15, 1.0),
        (0.95, 0.78, 0.05, 1.0),
        (1.00, 0.34, 0.03, 1.0),
        (0.90, 0.02, 0.08, 1.0),
    )
    bins = (0.0025, 0.005, 0.010, 0.020)
    materials = [
        material(f"DEVIATION_BIN_{index}", color, 0.72)
        for index, color in enumerate(colors)
    ]
    outside = material(
        "DEVIATION_OUTSIDE_REGION", (0.035, 0.045, 0.055, 1.0), 0.85
    )
    body.data.materials.clear()
    body.data.materials.append(outside)
    for mat in materials:
        body.data.materials.append(mat)
    for polygon in body.data.polygons:
        values = [
            vertex_distances[index]
            for index in polygon.vertices
            if index in vertex_distances
        ]
        if len(values) != len(polygon.vertices):
            polygon.material_index = 0
            continue
        average = sum(values) / len(values)
        bin_index = sum(average > threshold for threshold in bins)
        polygon.material_index = 1 + bin_index

    ordered = sorted(distances)
    return {
        "sampled_body_vertices": len(distances),
        "minimum": min(ordered),
        "maximum": max(ordered),
        "mean": sum(ordered) / len(ordered),
        "p50": ordered[len(ordered) // 2],
        "p95": ordered[round((len(ordered) - 1) * 0.95)],
        "material_bins": list(bins),
        "interpretation": (
            "Nearest-surface distance between the unchanged S40 closed-source "
            "production body and the independently generated open source "
            "inside the broad mouth working region. This is alignment "
            "diagnostic evidence, not a candidate-retopology error map."
        ),
    }


def main() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    camera, wire, region_wire = setup_scene()
    source = bpy.data.objects[SOURCE]
    body = bpy.data.objects[BODY]

    views = (
        (
            "01_front_alignment_overlay.png",
            (0.0, -2.0, 0.50),
            (0.0, 0.0, 0.50),
            1.08,
        ),
        (
            "02_three_quarter_alignment_overlay.png",
            (1.25, -1.75, 0.62),
            (0.0, 0.0, 0.48),
            1.12,
        ),
        (
            "03_profile_alignment_overlay.png",
            (2.0, 0.0, 0.52),
            (0.0, 0.0, 0.50),
            1.08,
        ),
        (
            "04_gameplay_alignment_overlay.png",
            (1.25, -2.05, 1.45),
            (0.0, 0.0, 0.44),
            1.20,
        ),
    )
    for filename, location, target, scale in views:
        render(camera, filename, location, target, scale)

    wire.hide_render = True
    region_wire.hide_render = False
    render(
        camera,
        "05_source_region_wire_closeup.png",
        (0.0, -2.0, 0.49),
        (0.0, 0.0, 0.49),
        0.46,
    )

    region_wire.hide_render = True
    source.hide_render = True
    body.hide_render = False
    report = deviation_heatmap(source, body)
    render(
        camera,
        "06_open_vs_production_deviation_closeup.png",
        (0.0, -2.0, 0.49),
        (0.0, 0.0, 0.49),
        0.46,
    )

    (QA / "open_source_production_body_deviation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
