"""Render close reference views of the locked VG06 open-mouth source.

This is an inspection-only recipe. It opens checkpoint 20 and never saves the
scene, so the production body and locked source remain untouched.
"""

from __future__ import annotations

from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "work/20_source_mouth_region_extraction.blend"
OUT = ROOT / "evidence/source_reference"


def look_at(obj: bpy.types.Object, location, target) -> None:
    obj.location = location
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def material(name, color, roughness=0.75):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    return mat


def render(camera, filename, location, target, scale) -> None:
    look_at(camera, location, target)
    camera.data.ortho_scale = scale
    bpy.context.scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(CHECKPOINT))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -1.35
    if scene.world is None:
        scene.world = bpy.data.worlds.new("SOURCE_REFERENCE_WORLD")
    scene.world.color = (0.006, 0.008, 0.012)

    source = bpy.data.objects["TRIPO_VG06_OPEN_SOURCE_LOCKED"]
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj != source
    source.hide_render = False
    source.data.materials.clear()
    source.data.materials.append(
        material("VG06_REFERENCE_SAGE", (0.055, 0.19, 0.10, 1.0))
    )
    for polygon in source.data.polygons:
        polygon.material_index = 0

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.lens = 70
    scene.camera = camera

    lights = (
        ((-0.8, -1.2, 1.3), 180.0, 0.75),
        ((0.9, -0.8, 0.8), 110.0, 0.60),
        ((0.0, 0.6, 1.2), 160.0, 0.55),
        ((0.0, -0.8, 0.15), 55.0, 0.40),
    )
    for index, (location, energy, size) in enumerate(lights):
        bpy.ops.object.light_add(type="AREA", location=location)
        lamp = bpy.context.object
        lamp.name = f"SOURCE_REFERENCE_LIGHT_{index:02d}"
        lamp.data.energy = energy
        lamp.data.shape = "DISK"
        lamp.data.size = size
        look_at(lamp, location, (0.0, -0.18, 0.50))

    render(
        camera,
        "01_front_head.png",
        (0.0, -2.0, 0.57),
        (0.0, -0.06, 0.57),
        0.52,
    )
    render(
        camera,
        "02_front_mouth.png",
        (0.0, -2.0, 0.49),
        (0.0, -0.15, 0.49),
        0.24,
    )
    render(
        camera,
        "03_three_quarter_mouth.png",
        (0.75, -1.5, 0.52),
        (0.0, -0.12, 0.49),
        0.26,
    )
    render(
        camera,
        "04_profile_mouth.png",
        (1.7, -0.02, 0.52),
        (0.0, -0.08, 0.49),
        0.28,
    )


if __name__ == "__main__":
    main()
