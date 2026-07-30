"""Render read-only evidence for the frozen F0 r006 failed checkpoint."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


REPO = Path("/Users/mauvsantos/Workspace/games/Bentosaur")
ROOT = REPO / ".tmp/root/f0_broad_face_r006"
INPUT = ROOT / "work/10_broad_open_topology.blend"
OUT = ROOT / "evidence"
BODY = "BENTOSAUR_BODY_CANONICAL_FACE_F0"
TONGUE = "BENTOSAUR_TONGUE_F0"


def material(name, color, roughness=0.72, emission=0.0):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    if emission:
        shader.inputs["Emission Color"].default_value = color
        shader.inputs["Emission Strength"].default_value = emission
    return result


def look_at(obj, location, target):
    obj.location = location
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render(camera, filename, location, target, scale):
    look_at(camera, location, target)
    camera.data.ortho_scale = scale
    bpy.context.scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(INPUT))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.65
    if scene.world is None:
        scene.world = bpy.data.worlds.new("F0_R006_WORLD")
    scene.world.color = (0.006, 0.009, 0.014)

    body = bpy.data.objects[BODY]
    tongue = bpy.data.objects[TONGUE]
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj not in (body, tongue)

    cavity_index = next(
        (
            index
            for index, value in enumerate(body.data.materials)
            if value and value.name.startswith("F0_MOUTH_CAVITY")
        ),
        None,
    )
    cavity_faces = {
        polygon.index
        for polygon in body.data.polygons
        if cavity_index is not None
        and polygon.material_index == cavity_index
    }
    skin = material("F0_RENDER_SKIN", (0.12, 0.39, 0.24, 1.0), 0.76)
    cavity = material(
        "F0_RENDER_CAVITY", (0.025, 0.003, 0.006, 1.0), 0.88
    )
    body.data.materials.clear()
    body.data.materials.append(skin)
    body.data.materials.append(cavity)
    for polygon in body.data.polygons:
        polygon.material_index = 1 if polygon.index in cavity_faces else 0
        polygon.use_smooth = True
    tongue.data.materials.clear()
    tongue.data.materials.append(
        material("F0_RENDER_TONGUE", (0.82, 0.16, 0.20, 1.0), 0.54)
    )

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    scene.camera = camera
    for index, (location, energy, size) in enumerate(
        (
            ((-1.2, -1.7, 1.7), 190.0, 1.0),
            ((1.1, -1.0, 0.9), 115.0, 0.8),
            ((0.4, 1.1, 1.4), 205.0, 0.7),
            ((0.0, -0.8, 0.2), 58.0, 0.5),
        )
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        lamp = bpy.context.object
        lamp.name = f"F0_R006_LIGHT_{index:02d}"
        lamp.data.energy = energy
        lamp.data.shape = "DISK"
        lamp.data.size = size
        look_at(lamp, location, (0.0, -0.05, 0.50))

    render(
        camera,
        "01_front_full.png",
        (0.0, -2.0, 0.50),
        (0.0, 0.0, 0.50),
        1.08,
    )
    render(
        camera,
        "02_three_quarter_full.png",
        (1.25, -1.75, 0.62),
        (0.0, 0.0, 0.48),
        1.12,
    )
    render(
        camera,
        "03_front_mouth_close.png",
        (0.0, -2.0, 0.49),
        (0.0, -0.05, 0.49),
        0.36,
    )
    render(
        camera,
        "04_three_quarter_mouth_close.png",
        (0.65, -1.9, 0.54),
        (0.0, -0.04, 0.48),
        0.38,
    )

    wire = body.copy()
    wire.data = body.data.copy()
    wire.name = "F0_R006_WIRE"
    scene.collection.objects.link(wire)
    wire.data.materials.clear()
    wire.data.materials.append(
        material(
            "F0_R006_WIRE_MAT",
            (0.02, 0.90, 1.0, 1.0),
            0.25,
            0.75,
        )
    )
    modifier = wire.modifiers.new("F0_R006_WIREFRAME", "WIREFRAME")
    modifier.thickness = 0.00044
    modifier.use_replace = True
    wire.hide_render = False
    render(
        camera,
        "05_front_mouth_wire.png",
        (0.0, -2.0, 0.49),
        (0.0, -0.05, 0.49),
        0.36,
    )


if __name__ == "__main__":
    main()
