"""Build a disposable, non-destructive visual QA scene for a Tripo model.

The source GLB is imported into a locked collection and never modified. A
deep mesh copy is used for all renders. The script produces matching surfaced,
clay, toon, wireframe, and native 64 px views plus mesh/material diagnostics.

Run with:

    /Applications/Blender.app/Contents/MacOS/Blender \
      --background --factory-startup \
      --python tools/blender/evaluate_tripo_visual_candidate.py -- \
      --input /absolute/path/model.glb-or-fbx \
      --output /absolute/path/evaluation \
      --candidate-id candidate_id
"""

from __future__ import annotations

import argparse
import bmesh
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


VIEW_DIRECTIONS = {
    # Tripo's GLB faces Blender +X after glTF import.
    "front": Vector((1.0, 0.0, 0.0)),
    "left": Vector((0.0, 1.0, 0.0)),
    "back": Vector((-1.0, 0.0, 0.0)),
    "right": Vector((0.0, -1.0, 0.0)),
    "three_quarter_left": Vector((1.0, 1.0, 0.12)).normalized(),
    "three_quarter_right": Vector((1.0, -1.0, 0.12)).normalized(),
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--resolution", type=int, default=768)
    parser.add_argument("--pixel-resolution", type=int, default=64)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def link_exclusively(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def import_source_locked(source: Path) -> tuple[list[bpy.types.Object], list[bpy.types.Object]]:
    source_collection = bpy.data.collections.new("00_SOURCE_LOCKED")
    bpy.context.scene.collection.children.link(source_collection)
    eval_collection = bpy.data.collections.new("10_EVAL_SURFACED")
    bpy.context.scene.collection.children.link(eval_collection)

    suffix = source.suffix.lower()
    if suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(source))
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(source))
    else:
        raise RuntimeError(
            f"Unsupported source format {suffix!r}; expected GLB, glTF, or FBX."
        )
    imported = list(bpy.context.selected_objects)
    source_meshes = [obj for obj in imported if obj.type == "MESH"]
    if not source_meshes:
        source_meshes = [
            obj for obj in bpy.context.scene.objects if obj.type == "MESH"
        ]
    if not source_meshes:
        raise RuntimeError("The imported model contains no mesh objects.")

    for obj in imported:
        link_exclusively(obj, source_collection)
        obj.hide_render = True
        obj.hide_set(True)

    eval_meshes: list[bpy.types.Object] = []
    for source_obj in source_meshes:
        duplicate = source_obj.copy()
        duplicate.data = source_obj.data.copy()
        duplicate.animation_data_clear()
        duplicate.parent = None
        duplicate.matrix_world = source_obj.matrix_world.copy()
        duplicate.name = f"EVAL_{source_obj.name}"
        eval_collection.objects.link(duplicate)
        duplicate.hide_render = False
        duplicate.hide_set(False)
        eval_meshes.append(duplicate)

    return source_meshes, eval_meshes


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


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(
    center: Vector, dimensions: Vector
) -> tuple[bpy.types.Object, float, float]:
    camera_data = bpy.data.cameras.new("QA_ORTHO_CAMERA")
    camera = bpy.data.objects.new("QA_ORTHO_CAMERA", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    camera.data.type = "ORTHO"

    maximum_cross_section = max(dimensions.x, dimensions.y, dimensions.z)
    # At 64 px this puts the largest projected extent at roughly 56 px.
    camera.data.ortho_scale = maximum_cross_section / 0.875
    distance = max(maximum_cross_section * 3.2, 1.0)
    return camera, camera.data.ortho_scale, distance


def configure_world() -> None:
    world = bpy.data.worlds.new("QA_WORLD")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.115, 0.13, 0.155, 1.0)
    background.inputs["Strength"].default_value = 0.55


def create_area_light(
    name: str, energy: float, size: float
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_lights(scale: float) -> dict[str, bpy.types.Object]:
    return {
        "key": create_area_light("QA_KEY", 850.0 * scale * scale, scale * 2.0),
        "fill": create_area_light("QA_FILL", 350.0 * scale * scale, scale * 2.6),
        "rim": create_area_light("QA_RIM", 650.0 * scale * scale, scale * 1.5),
    }


def place_camera_and_lights(
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    center: Vector,
    direction: Vector,
    distance: float,
    scale: float,
) -> None:
    view = direction.normalized()
    camera.location = center + view * distance
    point_at(camera, center)

    up = Vector((0.0, 0.0, 1.0))
    right = view.cross(up)
    if right.length < 0.001:
        right = Vector((0.0, 1.0, 0.0))
    right.normalize()

    lights["key"].location = (
        center + view * distance * 0.58 - right * scale * 1.3 + up * scale * 1.35
    )
    lights["fill"].location = (
        center + view * distance * 0.42 + right * scale * 1.45 + up * scale * 0.35
    )
    lights["rim"].location = (
        center - view * distance * 0.5 + right * scale * 0.25 + up * scale * 1.2
    )
    for light in lights.values():
        point_at(light, center)


def configure_render(resolution: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filter_size = 0.01
    scene.render.use_file_extension = True
    try:
        scene.view_settings.view_transform = "AgX"
    except TypeError:
        pass


def make_principled_material(
    name: str,
    base_color: tuple[float, float, float, float],
    roughness: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Roughness"].default_value = roughness
    return material


def find_base_color_image(material: bpy.types.Material) -> bpy.types.Image | None:
    if not material or not material.use_nodes:
        return None
    image_nodes = [
        node
        for node in material.node_tree.nodes
        if node.bl_idname == "ShaderNodeTexImage" and node.image
    ]
    for node in image_nodes:
        if node.image.colorspace_settings.name in {"sRGB", "Utility - sRGB - Texture"}:
            return node.image
    return image_nodes[0].image if image_nodes else None


def make_toon_material(source: bpy.types.Material | None) -> bpy.types.Material:
    source_name = source.name if source else "none"
    material = bpy.data.materials.new(f"QA_TOON__{source_name}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 1.0

    image = find_base_color_image(source) if source else None
    if image:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = image
        texture.interpolation = "Closest"
        links.new(texture.outputs["Color"], multiply.inputs[1])
    else:
        base = source.diffuse_color if source else (0.36, 0.56, 0.45, 1.0)
        multiply.inputs[1].default_value = base

    geometry = nodes.new("ShaderNodeNewGeometry")
    dot = nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = Vector((0.52, -0.34, 0.78)).normalized()
    map_range = nodes.new("ShaderNodeMapRange")
    map_range.inputs["From Min"].default_value = -1.0
    map_range.inputs["From Max"].default_value = 1.0
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0
    map_range.clamp = True
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.52, 0.52, 0.52, 1.0)
    ramp.color_ramp.elements[1].position = 0.68
    ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    middle = ramp.color_ramp.elements.new(0.42)
    middle.color = (0.78, 0.78, 0.78, 1.0)

    links.new(geometry.outputs["Normal"], dot.inputs[0])
    links.new(dot.outputs["Value"], map_range.inputs["Value"])
    links.new(map_range.outputs["Result"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def make_wireframe_material() -> bpy.types.Material:
    material = bpy.data.materials.new("QA_WIREFRAME")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    wire = nodes.new("ShaderNodeWireframe")
    wire.use_pixel_size = True
    wire.inputs["Size"].default_value = 0.65
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MIX"
    mix.inputs[1].default_value = (0.54, 0.58, 0.56, 1.0)
    mix.inputs[2].default_value = (0.025, 0.03, 0.035, 1.0)
    links.new(wire.outputs["Fac"], mix.inputs[0])
    links.new(mix.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def save_original_materials(
    mesh_objects: list[bpy.types.Object],
) -> dict[str, list[bpy.types.Material | None]]:
    return {
        obj.name: [slot.material for slot in obj.material_slots]
        for obj in mesh_objects
    }


def assign_toon_materials(
    mesh_objects: list[bpy.types.Object],
    originals: dict[str, list[bpy.types.Material | None]],
) -> None:
    cache: dict[str, bpy.types.Material] = {}
    for obj in mesh_objects:
        for index, source in enumerate(originals[obj.name]):
            key = source.name if source else "__none__"
            if key not in cache:
                cache[key] = make_toon_material(source)
            obj.material_slots[index].material = cache[key]


def restore_materials(
    mesh_objects: list[bpy.types.Object],
    originals: dict[str, list[bpy.types.Material | None]],
) -> None:
    for obj in mesh_objects:
        for index, material in enumerate(originals[obj.name]):
            obj.material_slots[index].material = material


def render_views(
    directory: Path,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    center: Vector,
    distance: float,
    scale: float,
) -> dict[str, str]:
    directory.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, str] = {}
    scene = bpy.context.scene
    for name, direction in VIEW_DIRECTIONS.items():
        place_camera_and_lights(camera, lights, center, direction, distance, scale)
        path = directory / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rendered[name] = str(path)
    return rendered


def source_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def topology_metrics(mesh_objects: list[bpy.types.Object]) -> dict[str, object]:
    totals = {
        "objects": len(mesh_objects),
        "vertices": 0,
        "edges": 0,
        "polygons": 0,
        "evaluated_triangles": 0,
        "triangle_faces": 0,
        "quad_faces": 0,
        "ngons": 0,
        "boundary_edges": 0,
        "non_manifold_edges": 0,
        "loose_edges": 0,
        "loose_vertices": 0,
        "uv_layers": 0,
        "shape_keys": 0,
    }
    rows: list[dict[str, object]] = []
    for obj in mesh_objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        face_sizes = [len(poly.vertices) for poly in mesh.polygons]
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        row = {
            "name": obj.name,
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "evaluated_triangles": len(mesh.loop_triangles),
            "triangle_faces": sum(size == 3 for size in face_sizes),
            "quad_faces": sum(size == 4 for size in face_sizes),
            "ngons": sum(size > 4 for size in face_sizes),
            "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
            "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
            "loose_edges": sum(not edge.link_faces for edge in bm.edges),
            "loose_vertices": sum(not vert.link_faces for vert in bm.verts),
            "uv_layers": len(mesh.uv_layers),
            "shape_keys": len(mesh.shape_keys.key_blocks) if mesh.shape_keys else 0,
            "material_slots": [
                slot.material.name if slot.material else None
                for slot in obj.material_slots
            ],
            "vertex_groups": len(obj.vertex_groups),
        }
        bm.free()
        for key in totals:
            if key != "objects" and key in row and isinstance(row[key], int):
                totals[key] += row[key]
        rows.append(row)
    return {"totals": totals, "objects": rows}


def material_metrics() -> dict[str, object]:
    materials: list[dict[str, object]] = []
    images_seen: dict[str, dict[str, object]] = {}
    for material in bpy.data.materials:
        if material.name.startswith("QA_"):
            continue
        image_names: list[str] = []
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.bl_idname != "ShaderNodeTexImage" or not node.image:
                    continue
                image = node.image
                image_names.append(image.name)
                images_seen[image.name] = {
                    "name": image.name,
                    "width": image.size[0],
                    "height": image.size[1],
                    "colorspace": image.colorspace_settings.name,
                    "packed": image.packed_file is not None,
                    "filepath": image.filepath,
                }
        materials.append(
            {
                "name": material.name,
                "images": image_names,
                "blend_method": getattr(material, "surface_render_method", None),
            }
        )
    return {
        "material_count": len(materials),
        "materials": materials,
        "images": list(images_seen.values()),
    }


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    output.mkdir(parents=True, exist_ok=True)
    clear_scene()
    source_meshes, eval_meshes = import_source_locked(source)

    minimum, maximum = world_bounds(eval_meshes)
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    scale = max(dimensions)

    configure_world()
    configure_render(args.resolution)
    camera, ortho_scale, distance = create_camera(center, dimensions)
    lights = create_lights(scale)
    originals = save_original_materials(eval_meshes)
    view_layer = bpy.context.scene.view_layers[0]

    renders: dict[str, dict[str, str]] = {}
    renders["surfaced"] = render_views(
        output / "renders" / "surfaced",
        camera,
        lights,
        center,
        distance,
        scale,
    )

    clay = make_principled_material(
        "QA_CLAY", (0.46, 0.40, 0.34, 1.0), roughness=0.68
    )
    view_layer.material_override = clay
    renders["clay"] = render_views(
        output / "renders" / "clay",
        camera,
        lights,
        center,
        distance,
        scale,
    )
    view_layer.material_override = None

    assign_toon_materials(eval_meshes, originals)
    renders["toon"] = render_views(
        output / "renders" / "toon",
        camera,
        lights,
        center,
        distance,
        scale,
    )

    configure_render(args.pixel_resolution)
    renders["pixel64"] = render_views(
        output / "renders" / "pixel64",
        camera,
        lights,
        center,
        distance,
        scale,
    )
    configure_render(args.resolution)
    restore_materials(eval_meshes, originals)

    wireframe = make_wireframe_material()
    view_layer.material_override = wireframe
    renders["wireframe"] = render_views(
        output / "renders" / "wireframe",
        camera,
        lights,
        center,
        distance,
        scale,
    )
    view_layer.material_override = None

    metrics = {
        "candidate_id": args.candidate_id,
        "source": {
            "provider": "tripo",
            "format": source.suffix.lower().lstrip("."),
            "path": str(source),
            "sha256": source_hash(source),
            "bytes": source.stat().st_size,
        },
        "blender_version": bpy.app.version_string,
        "visual_gate": {
            "status": "awaiting_user_approval",
            "assistant_may_approve": False,
            "rigging_or_animation_performed": False,
        },
        "bounds": {
            "minimum": list(minimum),
            "maximum": list(maximum),
            "dimensions": list(dimensions),
        },
        "camera": {
            "type": "orthographic",
            "ortho_scale": ortho_scale,
            "facing_axis_after_import": "+X",
            "views": list(VIEW_DIRECTIONS),
            "high_resolution": args.resolution,
            "native_pixel_resolution": args.pixel_resolution,
        },
        "topology": topology_metrics(eval_meshes),
        "materials": material_metrics(),
        "source_armature_count": sum(
            obj.type == "ARMATURE" for obj in bpy.context.scene.objects
        ),
        "source_action_count": len(bpy.data.actions),
        "renders": renders,
    }
    metrics_path = output / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    restore_materials(eval_meshes, originals)
    blend_path = output / f"{args.candidate_id}_evaluation.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    print(
        json.dumps(
            {
                "status": "success",
                "candidate_id": args.candidate_id,
                "metrics": str(metrics_path),
                "blend": str(blend_path),
                "render_modes": list(renders),
            }
        )
    )


if __name__ == "__main__":
    main()
