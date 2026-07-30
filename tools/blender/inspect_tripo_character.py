"""Import a Tripo GLB into a disposable Blender scene and render QA views.

Run with:

    blender --background --factory-startup \
      --python tools/blender/inspect_tripo_character.py -- \
      --input /absolute/path/model.glb \
      --output /absolute/path/inspection

The source GLB is never modified. The script writes a separate inspection
Blend file, mesh metrics, and orthographic PNG renders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=512)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


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


def mesh_metrics(
    source: Path,
    mesh_objects: list[bpy.types.Object],
    minimum: Vector,
    maximum: Vector,
) -> dict[str, object]:
    object_rows: list[dict[str, object]] = []
    total_vertices = 0
    total_polygons = 0
    total_triangles = 0

    for obj in mesh_objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        vertices = len(mesh.vertices)
        polygons = len(mesh.polygons)
        triangles = len(mesh.loop_triangles)
        total_vertices += vertices
        total_polygons += polygons
        total_triangles += triangles
        armature_modifiers = [
            modifier
            for modifier in obj.modifiers
            if modifier.type == "ARMATURE"
        ]
        object_rows.append(
            {
                "name": obj.name,
                "vertices": vertices,
                "polygons": polygons,
                "triangles": triangles,
                "materials": [slot.material.name for slot in obj.material_slots if slot.material],
                "vertex_group_count": len(obj.vertex_groups),
                "armature_modifiers": [
                    modifier.object.name if modifier.object else None
                    for modifier in armature_modifiers
                ],
            }
        )

    dimensions = maximum - minimum
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    return {
        "source_glb": str(source.resolve()),
        "mesh_object_count": len(mesh_objects),
        "armature_count": len(armatures),
        "armatures": [
            {
                "name": armature.name,
                "bone_count": len(armature.data.bones),
                "bones": [bone.name for bone in armature.data.bones],
            }
            for armature in armatures
        ],
        "actions": [action.name for action in bpy.data.actions],
        "totals": {
            "vertices": total_vertices,
            "polygons": total_polygons,
            "triangles": total_triangles,
        },
        "bounds": {
            "minimum": list(minimum),
            "maximum": list(maximum),
            "dimensions": list(dimensions),
        },
        "objects": object_rows,
    }


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()

    if not source.is_file():
        raise FileNotFoundError(source)

    output.mkdir(parents=True, exist_ok=True)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(source))

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError("The imported GLB contains no mesh objects.")

    minimum, maximum = world_bounds(mesh_objects)
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    largest_dimension = max(dimensions)
    distance = max(largest_dimension * 3.0, 1.0)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.color = (0.018, 0.022, 0.032)

    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.curvature_ridge_factor = 1.5
    scene.display.shading.curvature_valley_factor = 1.5
    scene.display.shading.background_type = "WORLD"

    for obj in mesh_objects:
        if not obj.material_slots:
            obj.color = (0.36, 0.58, 0.46, 1.0)

    camera_data = bpy.data.cameras.new("QA_Ortho_Camera")
    camera = bpy.data.objects.new("QA_Ortho_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = largest_dimension * 1.35

    # Tripo's downloaded GLB faces Blender +X after glTF import.
    views = {
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

    render_paths: dict[str, str] = {}
    for name, position in views.items():
        point_camera(camera, position, center)
        render_path = output / f"{name}.png"
        scene.render.filepath = str(render_path)
        bpy.ops.render.render(write_still=True)
        render_paths[name] = str(render_path)

    metrics = mesh_metrics(source, mesh_objects, minimum, maximum)
    metrics["renders"] = render_paths
    metrics_path = output / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    blend_path = output / "inspection.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    print(
        json.dumps(
            {
                "status": "success",
                "metrics": str(metrics_path),
                "blend": str(blend_path),
                "renders": render_paths,
            }
        )
    )


if __name__ == "__main__":
    main()
