"""Render Checkpoint 30 static approval evidence without saving scene edits."""

from __future__ import annotations

import math
import os
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(
    os.environ.get(
        "CP30_INPUT",
        str(ROOT / "work/30_TRIPO_OPEN_MOUTH_TRANSFER_STATIC.blend"),
    )
)
ATTEMPT = os.environ.get("CP30_ATTEMPT", "final")
OUT = ROOT / "evidence" / ATTEMPT
BODY_NAME = "BENTOSAUR_BODY_TRIPO_OPEN_MOUTH_CP30"
TONGUE_NAME = "BENTOSAUR_TONGUE_SEPARATE_CLOSED_CP30"
SOURCE_NAME = "TRIPO_VG06_OPEN_SOURCE_LOCKED"
REGION_NAME = "TRIPO_VG06_MOUTH_REGION_SOURCE_LOCKED"


def look_at(obj, location, target):
    obj.location = location
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def material(name, color, roughness=0.70, emission=0.0, alpha=1.0):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Alpha"].default_value = alpha
    if emission:
        shader.inputs["Emission Color"].default_value = color
        shader.inputs["Emission Strength"].default_value = emission
    if alpha < 1.0:
        try:
            result.surface_render_method = "DITHERED"
        except Exception:
            pass
    return result


def assign_candidate_materials(body, tongue):
    cavity_index = next(
        (
            index
            for index, mat in enumerate(body.data.materials)
            if mat and mat.name.startswith("CP30_MOUTH_CAVITY")
        ),
        None,
    )
    cavity_faces = {
        polygon.index
        for polygon in body.data.polygons
        if cavity_index is not None and polygon.material_index == cavity_index
    }
    skin = material("RENDER_CP30_SKIN", (0.12, 0.39, 0.24, 1.0), 0.78)
    cavity = material(
        "RENDER_CP30_CAVITY", (0.030, 0.004, 0.007, 1.0), 0.88
    )
    body.data.materials.clear()
    body.data.materials.append(skin)
    body.data.materials.append(cavity)
    for polygon in body.data.polygons:
        polygon.material_index = 1 if polygon.index in cavity_faces else 0
        polygon.use_smooth = True

    tongue.data.materials.clear()
    tongue.data.materials.append(
        material("RENDER_CP30_TONGUE", (0.82, 0.18, 0.20, 1.0), 0.55)
    )
    for polygon in tongue.data.polygons:
        polygon.material_index = 0
        polygon.use_smooth = True


def render(camera, filename, location, target, scale):
    look_at(camera, location, target)
    camera.data.ortho_scale = scale
    bpy.context.scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)


def set_mesh_visibility(objects, visible):
    for obj in objects:
        obj.hide_render = not visible


def make_wire(source, name, color, thickness):
    wire = source.copy()
    wire.data = source.data.copy()
    wire.name = name
    bpy.context.scene.collection.objects.link(wire)
    wire.data.materials.clear()
    wire.data.materials.append(material(f"{name}_MAT", color, 0.3, 0.7))
    for polygon in wire.data.polygons:
        polygon.material_index = 0
    modifier = wire.modifiers.new("approval_wire", "WIREFRAME")
    modifier.thickness = thickness
    modifier.use_replace = True
    return wire


def make_patch_wire(body):
    selected = []
    for polygon in body.data.polygons:
        center = polygon.center
        if (
            (center.x / 0.115) ** 2
            + ((center.z - 0.475) / 0.078) ** 2
            <= 1.0
            and center.y <= -0.22
        ):
            selected.append(polygon.index)
    vertex_indices = sorted(
        {
            index
            for face_index in selected
            for index in body.data.polygons[face_index].vertices
        }
    )
    remap = {
        old_index: new_index
        for new_index, old_index in enumerate(vertex_indices)
    }
    faces = [
        tuple(remap[index] for index in body.data.polygons[face_index].vertices)
        for face_index in selected
    ]
    mesh = bpy.data.meshes.new("CP30_PATCH_WIRE_MESH")
    mesh.from_pydata(
        [body.data.vertices[index].co for index in vertex_indices], [], faces
    )
    mesh.update()
    patch = bpy.data.objects.new("CP30_PATCH_WIRE", mesh)
    bpy.context.scene.collection.objects.link(patch)
    patch.hide_render = True
    return make_wire(patch, "CP30_PATCH_WIRE_RENDER", (0.03, 0.85, 0.95, 1.0), 0.00055)


def make_deviation_copy(body, source):
    duplicate = body.copy()
    duplicate.data = body.data.copy()
    duplicate.name = "CP30_DEVIATION_RENDER"
    bpy.context.scene.collection.objects.link(duplicate)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(source.evaluated_get(depsgraph), depsgraph)
    bins = (0.0025, 0.005, 0.010, 0.020)
    colors = (
        (0.02, 0.25, 0.06, 1.0),
        (0.14, 0.65, 0.15, 1.0),
        (0.95, 0.77, 0.04, 1.0),
        (1.00, 0.31, 0.02, 1.0),
        (0.86, 0.01, 0.08, 1.0),
    )
    outside = material("DEVIATION_OUTSIDE", (0.025, 0.03, 0.04, 1.0), 0.9)
    duplicate.data.materials.clear()
    duplicate.data.materials.append(outside)
    for index, color in enumerate(colors):
        duplicate.data.materials.append(
            material(f"DEVIATION_{index}", color, 0.74)
        )
    distances = {}
    for vertex in duplicate.data.vertices:
        if (
            abs(vertex.co.x) <= 0.122
            and 0.390 <= vertex.co.z <= 0.558
            and vertex.co.y <= -0.20
        ):
            nearest = bvh.find_nearest(vertex.co)
            if nearest is not None:
                distances[vertex.index] = float(nearest[3])
    for polygon in duplicate.data.polygons:
        values = [distances.get(index) for index in polygon.vertices]
        if any(value is None for value in values):
            polygon.material_index = 0
            continue
        average = sum(values) / len(values)
        polygon.material_index = 1 + sum(average > value for value in bins)
    return duplicate


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
    scene.view_settings.exposure = -1.0
    if scene.world is None:
        scene.world = bpy.data.worlds.new("CP30_APPROVAL_WORLD")
    scene.world.color = (0.004, 0.006, 0.010)

    body = bpy.data.objects[BODY_NAME]
    tongue = bpy.data.objects[TONGUE_NAME]
    source = bpy.data.objects[SOURCE_NAME]
    region = bpy.data.objects[REGION_NAME]
    all_meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    set_mesh_visibility(all_meshes, False)
    set_mesh_visibility([body, tongue], True)
    assign_candidate_materials(body, tongue)

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    scene.camera = camera
    for index, (location, energy, size) in enumerate(
        (
            ((-1.2, -1.7, 1.7), 180.0, 1.0),
            ((1.1, -1.0, 0.9), 105.0, 0.8),
            ((0.4, 1.1, 1.4), 190.0, 0.7),
            ((0.0, -0.8, 0.2), 50.0, 0.5),
        )
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        lamp = bpy.context.object
        lamp.name = f"CP30_APPROVAL_LIGHT_{index:02d}"
        lamp.data.energy = energy
        lamp.data.shape = "DISK"
        lamp.data.size = size
        look_at(lamp, location, (0.0, -0.05, 0.50))

    views = (
        ("01_front.png", (0.0, -2.0, 0.50), (0.0, 0.0, 0.50), 1.08),
        (
            "02_three_quarter.png",
            (1.25, -1.75, 0.62),
            (0.0, 0.0, 0.48),
            1.12,
        ),
        ("03_profile.png", (2.0, 0.0, 0.52), (0.0, 0.0, 0.50), 1.08),
        (
            "04_gameplay.png",
            (1.25, -2.05, 1.45),
            (0.0, 0.0, 0.44),
            1.20,
        ),
        (
            "05_front_mouth_close.png",
            (0.0, -2.0, 0.49),
            (0.0, -0.05, 0.49),
            0.30,
        ),
    )
    for args in views:
        render(camera, *args)

    body_wire = make_wire(
        body, "CP30_BODY_WIRE_RENDER", (0.02, 0.08, 0.10, 1.0), 0.00042
    )
    tongue_wire = make_wire(
        tongue, "CP30_TONGUE_WIRE_RENDER", (0.35, 0.02, 0.03, 1.0), 0.00042
    )
    set_mesh_visibility([body_wire, tongue_wire], True)
    render(
        camera,
        "06_wire_front_close.png",
        (0.0, -2.0, 0.49),
        (0.0, -0.05, 0.49),
        0.30,
    )
    set_mesh_visibility([body_wire, tongue_wire], False)

    patch_wire = make_patch_wire(body)
    set_mesh_visibility([body, tongue, patch_wire], True)
    render(
        camera,
        "07_boundary_patch_wire.png",
        (0.0, -2.0, 0.49),
        (0.0, -0.05, 0.49),
        0.34,
    )
    set_mesh_visibility([patch_wire], False)

    source_material = material(
        "RENDER_SOURCE_OVERLAY_GOLD",
        (1.0, 0.50, 0.03, 1.0),
        0.38,
        0.35,
        0.35,
    )
    region.data.materials.clear()
    region.data.materials.append(source_material)
    for polygon in region.data.polygons:
        polygon.material_index = 0
    set_mesh_visibility([body, tongue, region], True)
    render(
        camera,
        "08_source_overlay.png",
        (0.0, -2.0, 0.49),
        (0.0, -0.05, 0.49),
        0.30,
    )
    set_mesh_visibility([body, tongue, region], False)

    deviation = make_deviation_copy(body, source)
    set_mesh_visibility([deviation], True)
    render(
        camera,
        "09_deviation.png",
        (0.0, -2.0, 0.49),
        (0.0, -0.05, 0.49),
        0.34,
    )


if __name__ == "__main__":
    main()
