"""Render a compact orthographic preview of one action in an animated Tripo GLB.

The script imports into a factory-startup Blender process and never modifies
the downloaded source file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--action", required=True)
    parser.add_argument(
        "--view",
        choices=("front", "left", "back", "right", "three_quarter"),
        default="front",
    )
    parser.add_argument("--samples", type=int, default=24)
    parser.add_argument("--resolution", type=int, default=384)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def world_bounds(mesh_objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in mesh_objects
        for corner in obj.bound_box
    ]
    minimum = Vector(
        (
            min(point.x for point in points),
            min(point.y for point in points),
            min(point.z for point in points),
        )
    )
    maximum = Vector(
        (
            max(point.x for point in points),
            max(point.y for point in points),
            max(point.z for point in points),
        )
    )
    return minimum, maximum


def point_camera(camera: bpy.types.Object, position: Vector, target: Vector) -> None:
    camera.location = position
    camera.rotation_euler = (target - position).to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    if not source.is_file():
        raise FileNotFoundError(source)
    if args.samples < 2:
        raise ValueError("--samples must be at least 2")

    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(source))

    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if len(armatures) != 1:
        raise RuntimeError(f"Expected one armature, found {len(armatures)}.")
    if not mesh_objects:
        raise RuntimeError("The imported GLB contains no mesh objects.")
    if args.action not in bpy.data.actions:
        raise KeyError(
            f"Action {args.action!r} not found. Available: {list(bpy.data.actions.keys())}"
        )

    armature = armatures[0]
    action = bpy.data.actions[args.action]
    animation_data = armature.animation_data_create()
    animation_data.action = action

    character_mesh_objects = [
        obj
        for obj in mesh_objects
        if any(modifier.type == "ARMATURE" for modifier in obj.modifiers)
    ]
    if not character_mesh_objects:
        character_mesh_objects = mesh_objects
    for obj in mesh_objects:
        if obj not in character_mesh_objects:
            obj.hide_render = True

    start, end = action.frame_range
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.world.color = (0.018, 0.022, 0.032)
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.curvature_ridge_factor = 1.5
    scene.display.shading.curvature_valley_factor = 1.5
    scene.display.shading.background_type = "WORLD"

    for obj in character_mesh_objects:
        if not obj.material_slots:
            obj.color = (0.36, 0.58, 0.46, 1.0)

    scene.frame_set(int(start))
    minimum, maximum = world_bounds(character_mesh_objects)
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    largest_dimension = max(dimensions)
    distance = max(largest_dimension * 3.0, 1.0)

    camera_data = bpy.data.cameras.new("Animation_Preview_Camera")
    camera = bpy.data.objects.new("Animation_Preview_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = largest_dimension * 1.6

    positions = {
        "front": Vector((center.x + distance, center.y, center.z)),
        "left": Vector((center.x, center.y + distance, center.z)),
        "back": Vector((center.x - distance, center.y, center.z)),
        "right": Vector((center.x, center.y - distance, center.z)),
        "three_quarter": Vector(
            (
                center.x + distance * 0.75,
                center.y + distance * 0.75,
                center.z + distance * 0.2,
            )
        ),
    }
    point_camera(camera, positions[args.view], center)

    slug = re.sub(r"[^a-z0-9]+", "-", args.action.lower()).strip("-")
    frame_rows: list[dict[str, object]] = []
    for index in range(args.samples):
        source_frame = start + (end - start) * index / args.samples
        scene.frame_set(round(source_frame))
        render_path = output / f"{slug}-{args.view}-{index:03d}.png"
        scene.render.filepath = str(render_path)
        bpy.ops.render.render(write_still=True)
        frame_rows.append(
            {
                "sample": index,
                "source_frame": source_frame,
                "render": str(render_path),
            }
        )

    metadata = {
        "source_glb": str(source),
        "action": args.action,
        "source_frame_range": [start, end],
        "view": args.view,
        "sample_count": args.samples,
        "frames": frame_rows,
    }
    metadata_path = output / f"{slug}-{args.view}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "success", "metadata": str(metadata_path)}))


if __name__ == "__main__":
    main()
