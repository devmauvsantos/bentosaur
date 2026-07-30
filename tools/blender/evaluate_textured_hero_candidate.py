"""Evaluate a textured Bentosaur hero candidate without editing its geometry.

This Visual Gate 04 evaluator deliberately separates two different questions:

``basecolor``
    What is actually present in the GLB's linked base-colour image?  The image
    is connected directly to an Emission shader and rendered with the Standard
    view transform.  There are no lights, normal/ORM links, colour corrections,
    or floor.

``matte``
    How does that unchanged base colour read on the candidate's form?  The
    image is connected directly to a deliberately matte Principled material
    (metallic 0, roughness .82, specular IOR level .18), with soft lights and
    AgX.  Normal and ORM images remain disconnected.

The imported candidate is locked and hidden.  Renderable meshes are deep data
copies whose only changes are material-slot assignments.  The script never
adds, removes, moves, smooths, retopologizes, or otherwise edits geometry.

Example:

    /Applications/Blender.app/Contents/MacOS/Blender \
      --background --factory-startup \
      --python tools/blender/evaluate_textured_hero_candidate.py -- \
      --input /absolute/path/to/textured/model.glb \
      --reference-geometry /absolute/path/to/untextured/model.glb \
      --task-json /absolute/path/to/task.json \
      --reference-images front.png left.png back.png right.png \
      --output /absolute/path/to/evaluation \
      --candidate-id bentosaur_vg04_h31_extreme_texture \
      --mode both \
      --resolution 512
"""

from __future__ import annotations

import argparse
from array import array
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from typing import Iterable

import bpy
from mathutils import Vector


EVALUATOR_ID = "bentosaur_visual_gate_04_textured_hero"
EVALUATOR_VERSION = "1.0.0"
BOARD_FONT = "/System/Library/Fonts/Helvetica.ttc"
REFERENCE_ROLES = ("front", "left", "back", "right")


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--task-json", type=Path)
    parser.add_argument("--task-id")
    parser.add_argument("--reference-geometry", type=Path)
    parser.add_argument(
        "--reference-images",
        nargs=4,
        type=Path,
        metavar=("FRONT", "LEFT", "BACK", "RIGHT"),
    )
    parser.add_argument(
        "--mode",
        choices=("basecolor", "matte", "both"),
        default="both",
    )
    parser.add_argument(
        "--front-axis",
        choices=("+X", "-X", "+Y", "-Y"),
        default="+X",
    )
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--samples", type=int, default=32)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def link_exclusively(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> None:
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def import_glb(source: Path) -> list[bpy.types.Object]:
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    return [obj for obj in bpy.context.scene.objects if obj not in before]


def import_reference_for_metrics(
    source: Path,
) -> tuple[dict[str, object], list[bpy.types.Object]]:
    imported = import_glb(source)
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("Reference GLB contains no mesh objects.")
    metrics = geometry_metrics(meshes, source)
    return metrics, imported


def remove_import(imported: Iterable[bpy.types.Object]) -> None:
    meshes = {
        obj.data
        for obj in imported
        if obj.type == "MESH" and obj.data is not None
    }
    for obj in list(imported):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def import_locked_and_duplicate(
    source: Path,
) -> tuple[list[bpy.types.Object], list[bpy.types.Object]]:
    locked = bpy.data.collections.new("00_TEXTURED_SOURCE_LOCKED_READ_ONLY")
    bpy.context.scene.collection.children.link(locked)
    evaluation = bpy.data.collections.new("10_TEXTURE_EVALUATION_DUPLICATES")
    bpy.context.scene.collection.children.link(evaluation)

    imported = import_glb(source)
    source_meshes = [obj for obj in imported if obj.type == "MESH"]
    if not source_meshes:
        raise RuntimeError("Textured candidate GLB contains no mesh objects.")

    for obj in imported:
        link_exclusively(obj, locked)
        obj["bentosaur_source_locked"] = True
        obj.hide_render = True
        obj.hide_set(True)
        obj.hide_select = True

    duplicates: list[bpy.types.Object] = []
    for source_obj in source_meshes:
        duplicate = source_obj.copy()
        duplicate.data = source_obj.data.copy()
        duplicate.animation_data_clear()
        duplicate.parent = None
        duplicate.matrix_world = source_obj.matrix_world.copy()
        duplicate.name = f"TEXTURE_EVAL__{source_obj.name}"
        duplicate["bentosaur_texture_evaluation_duplicate"] = True
        duplicate["geometry_edits_applied"] = False
        if "bentosaur_source_locked" in duplicate:
            del duplicate["bentosaur_source_locked"]
        duplicate.hide_render = False
        duplicate.hide_set(False)
        duplicate.hide_select = False
        evaluation.objects.link(duplicate)
        duplicates.append(duplicate)

    return source_meshes, duplicates


def world_bounds(
    mesh_objects: Iterable[bpy.types.Object],
) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in mesh_objects
        for corner in obj.bound_box
    ]
    if not points:
        raise RuntimeError("Cannot calculate bounds without mesh objects.")
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


def _float_array(values: int) -> array:
    return array("f", [0.0]) * values


def _int_array(values: int) -> array:
    return array("i", [0]) * values


def mesh_geometry_signature(obj: bpy.types.Object) -> dict[str, object]:
    mesh = obj.data

    positions = _float_array(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", positions)
    position_hash = hashlib.sha256(memoryview(positions)).hexdigest()

    loop_vertices = _int_array(len(mesh.loops))
    mesh.loops.foreach_get("vertex_index", loop_vertices)
    topology_digest = hashlib.sha256(memoryview(loop_vertices))
    # A texture export commonly duplicates vertices along UV seams.  Raw
    # vertex/index hashes then differ even when every polygon corner remains in
    # the exact same place.  Hash the ordered corner positions as the canonical
    # geometric-surface signature so seam splitting is not mislabeled as a
    # shape edit.
    try:
        import numpy as np
    except ImportError as error:
        raise RuntimeError(
            "Blender's bundled NumPy is required for surface hashing."
        ) from error
    position_matrix = np.frombuffer(positions, dtype=np.float32).reshape(
        (-1, 3)
    )
    loop_index_array = np.frombuffer(loop_vertices, dtype=np.int32)
    corner_digest = hashlib.sha256()
    chunk_size = 500_000
    for start in range(0, len(loop_index_array), chunk_size):
        stop = min(start + chunk_size, len(loop_index_array))
        corner_positions = np.ascontiguousarray(
            position_matrix[loop_index_array[start:stop]]
        )
        corner_digest.update(memoryview(corner_positions))

    loop_starts = _int_array(len(mesh.polygons))
    loop_totals = _int_array(len(mesh.polygons))
    mesh.polygons.foreach_get("loop_start", loop_starts)
    mesh.polygons.foreach_get("loop_total", loop_totals)
    topology_digest.update(memoryview(loop_starts))
    topology_digest.update(memoryview(loop_totals))

    matrix_values = [
        float(obj.matrix_world[row][column])
        for row in range(4)
        for column in range(4)
    ]
    matrix_hash = hashlib.sha256(
        struct.pack("<16d", *matrix_values)
    ).hexdigest()
    minimum, maximum = world_bounds([obj])
    triangles = sum(max(total - 2, 0) for total in loop_totals)

    return {
        "object_name": obj.name,
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "polygons": len(mesh.polygons),
        "loops": len(mesh.loops),
        "triangles": triangles,
        "uv_layers": len(mesh.uv_layers),
        "material_slots": len(obj.material_slots),
        "position_hash_local_float32": position_hash,
        "ordered_corner_position_hash_local_float32": (
            corner_digest.hexdigest()
        ),
        "topology_hash": topology_digest.hexdigest(),
        "matrix_world_hash_float64": matrix_hash,
        "world_bounds": {
            "minimum": [round(float(value), 9) for value in minimum],
            "maximum": [round(float(value), 9) for value in maximum],
            "dimensions": [
                round(float(value), 9) for value in maximum - minimum
            ],
        },
    }


def geometry_metrics(
    mesh_objects: list[bpy.types.Object], source: Path
) -> dict[str, object]:
    signatures = [mesh_geometry_signature(obj) for obj in mesh_objects]
    signatures.sort(
        key=lambda item: (
            int(item["vertices"]),
            int(item["polygons"]),
            str(item["position_hash_local_float32"]),
        )
    )
    minimum, maximum = world_bounds(mesh_objects)
    aggregate = hashlib.sha256()
    surface_aggregate = hashlib.sha256()
    for signature in signatures:
        for key in (
            "vertices",
            "edges",
            "polygons",
            "loops",
            "triangles",
            "position_hash_local_float32",
            "topology_hash",
            "matrix_world_hash_float64",
        ):
            aggregate.update(str(signature[key]).encode("utf-8"))
            aggregate.update(b"\0")
        for key in (
            "polygons",
            "loops",
            "triangles",
            "ordered_corner_position_hash_local_float32",
            "matrix_world_hash_float64",
        ):
            surface_aggregate.update(str(signature[key]).encode("utf-8"))
            surface_aggregate.update(b"\0")
    return {
        "source": str(source),
        "source_sha256": sha256(source),
        "mesh_object_count": len(mesh_objects),
        "vertices": sum(int(item["vertices"]) for item in signatures),
        "edges": sum(int(item["edges"]) for item in signatures),
        "polygons": sum(int(item["polygons"]) for item in signatures),
        "loops": sum(int(item["loops"]) for item in signatures),
        "triangles": sum(int(item["triangles"]) for item in signatures),
        "aggregate_representation_hash": aggregate.hexdigest(),
        "aggregate_surface_hash": surface_aggregate.hexdigest(),
        "world_bounds": {
            "minimum": [round(float(value), 9) for value in minimum],
            "maximum": [round(float(value), 9) for value in maximum],
            "dimensions": [
                round(float(value), 9) for value in maximum - minimum
            ],
        },
        "meshes": signatures,
    }


def compare_geometry(
    candidate: dict[str, object],
    reference: dict[str, object] | None,
) -> dict[str, object]:
    if reference is None:
        return {
            "reference_supplied": False,
            "geometry_match": None,
            "reason": "No reference geometry supplied.",
        }

    representation_count_keys = (
        "mesh_object_count",
        "vertices",
        "edges",
        "polygons",
        "loops",
        "triangles",
    )
    representation_count_matches = {
        key: candidate[key] == reference[key]
        for key in representation_count_keys
    }
    surface_count_keys = (
        "mesh_object_count",
        "polygons",
        "loops",
        "triangles",
    )
    surface_count_matches = {
        key: candidate[key] == reference[key] for key in surface_count_keys
    }
    candidate_dimensions = candidate["world_bounds"]["dimensions"]
    reference_dimensions = reference["world_bounds"]["dimensions"]
    dimension_deltas = [
        abs(float(left) - float(right))
        for left, right in zip(candidate_dimensions, reference_dimensions)
    ]
    bounds_match = max(dimension_deltas, default=0.0) <= 1e-7
    representation_hash_match = (
        candidate["aggregate_representation_hash"]
        == reference["aggregate_representation_hash"]
    )
    surface_hash_match = (
        candidate["aggregate_surface_hash"]
        == reference["aggregate_surface_hash"]
    )
    return {
        "reference_supplied": True,
        "representation_count_matches": representation_count_matches,
        "surface_count_matches": surface_count_matches,
        "vertex_count_delta": (
            int(candidate["vertices"]) - int(reference["vertices"])
        ),
        "edge_count_delta": (
            int(candidate["edges"]) - int(reference["edges"])
        ),
        "world_dimension_absolute_deltas": dimension_deltas,
        "world_dimensions_match_within_1e-7": bounds_match,
        "aggregate_representation_hash_match": representation_hash_match,
        "aggregate_surface_hash_match": surface_hash_match,
        "geometry_match": (
            all(surface_count_matches.values())
            and bounds_match
            and surface_hash_match
        ),
        "note": (
            "The ordered polygon-corner surface hash is authoritative for "
            "shape equivalence. Raw vertex/edge counts and representation "
            "hashes may differ when a texture export splits vertices at UV "
            "seams. Material slots and UV-layer counts are recorded but "
            "deliberately excluded from the geometry-match verdict."
        ),
    }


def front_direction(axis: str) -> Vector:
    return {
        "+X": Vector((1.0, 0.0, 0.0)),
        "-X": Vector((-1.0, 0.0, 0.0)),
        "+Y": Vector((0.0, 1.0, 0.0)),
        "-Y": Vector((0.0, -1.0, 0.0)),
    }[axis]


def view_directions(axis: str) -> dict[str, Vector]:
    front = front_direction(axis)
    up = Vector((0.0, 0.0, 1.0))
    character_left = up.cross(front).normalized()
    character_right = -character_left
    return {
        "front": front,
        "left": character_left,
        "back": -front,
        "right": character_right,
        "three_quarter_left": (
            front + character_left + up * 0.08
        ).normalized(),
        "three_quarter_right": (
            front + character_right + up * 0.08
        ).normalized(),
    }


def linked_base_colour_image(
    material: bpy.types.Material | None,
) -> bpy.types.Image | None:
    if not material or not material.use_nodes or not material.node_tree:
        return None

    nodes = material.node_tree.nodes
    outputs = [
        node
        for node in nodes
        if node.bl_idname == "ShaderNodeOutputMaterial"
        and getattr(node, "is_active_output", True)
    ]
    principled_nodes: list[bpy.types.Node] = []
    for output in outputs:
        surface = output.inputs.get("Surface")
        if surface and surface.is_linked:
            source = surface.links[0].from_node
            if source.bl_idname == "ShaderNodeBsdfPrincipled":
                principled_nodes.append(source)
    principled_nodes.extend(
        node
        for node in nodes
        if node.bl_idname == "ShaderNodeBsdfPrincipled"
        and node not in principled_nodes
    )

    for principled in principled_nodes:
        base_colour = principled.inputs.get("Base Color")
        if not base_colour or not base_colour.is_linked:
            continue
        pending = [link.from_node for link in base_colour.links]
        visited: set[bpy.types.Node] = set()
        while pending:
            node = pending.pop(0)
            if node in visited:
                continue
            visited.add(node)
            if node.bl_idname == "ShaderNodeTexImage" and node.image:
                return node.image
            for input_socket in node.inputs:
                pending.extend(
                    link.from_node for link in input_socket.links
                )

    image_nodes = [
        node
        for node in nodes
        if node.bl_idname == "ShaderNodeTexImage" and node.image
    ]
    preferred = [
        node
        for node in image_nodes
        if node.image.colorspace_settings.name
        in {"sRGB", "Utility - sRGB - Texture"}
        or "base" in node.image.name.lower()
        or "color" in node.image.name.lower()
        or "colour" in node.image.name.lower()
    ]
    return (preferred or image_nodes)[0].image if image_nodes else None


def create_evidence_material(
    source: bpy.types.Material | None,
    mode: str,
) -> tuple[bpy.types.Material, bpy.types.Image]:
    image = linked_base_colour_image(source)
    if image is None:
        source_name = source.name if source else "<empty slot>"
        raise RuntimeError(
            f"No linked base-colour image found in material {source_name!r}."
        )

    source_name = source.name if source else "missing"
    material = bpy.data.materials.new(
        f"VG04_{mode.upper()}__{source_name}"
    )
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.name = "VG04_OUTPUT"
    texture = nodes.new("ShaderNodeTexImage")
    texture.name = "VG04_ACTUAL_LINKED_BASE_COLOR"
    texture.label = "ACTUAL LINKED BASE COLOR — UNCHANGED"
    texture.image = image
    texture.interpolation = "Linear"
    texture.extension = "REPEAT"

    if mode == "basecolor":
        shader = nodes.new("ShaderNodeEmission")
        shader.name = "VG04_BASECOLOR_TRUTH_EMISSION"
        shader.inputs["Strength"].default_value = 1.0
        links.new(texture.outputs["Color"], shader.inputs["Color"])
        links.new(shader.outputs["Emission"], output.inputs["Surface"])
    elif mode == "matte":
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        shader.name = "VG04_MATTE_PRINCIPLED"
        shader.inputs["Metallic"].default_value = 0.0
        shader.inputs["Roughness"].default_value = 0.82
        if "Specular IOR Level" in shader.inputs:
            shader.inputs["Specular IOR Level"].default_value = 0.18
        if "Coat Weight" in shader.inputs:
            shader.inputs["Coat Weight"].default_value = 0.0
        links.new(texture.outputs["Color"], shader.inputs["Base Color"])
        links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    else:
        raise ValueError(mode)

    material["base_color_image_name"] = image.name
    material["normal_map_connected"] = False
    material["orm_map_connected"] = False
    material["colour_corrections_applied"] = False
    return material, image


def assign_mode_materials(
    meshes: Iterable[bpy.types.Object],
    mode: str,
    source_materials: dict[str, list[bpy.types.Material | None]],
) -> tuple[list[str], list[dict[str, object]]]:
    cache: dict[str, tuple[bpy.types.Material, bpy.types.Image]] = {}
    assigned: list[str] = []
    images: dict[str, dict[str, object]] = {}
    for obj in meshes:
        if not obj.material_slots:
            raise RuntimeError(
                f"Renderable mesh {obj.name!r} has no material slot."
            )
        original_slots = source_materials[obj.name]
        if len(original_slots) != len(obj.material_slots):
            raise RuntimeError(
                f"Material-slot count changed on {obj.name!r}."
            )
        for slot_index, slot in enumerate(obj.material_slots):
            source = original_slots[slot_index]
            key = source.name if source else "__missing__"
            if key not in cache:
                cache[key] = create_evidence_material(source, mode)
            evidence, image = cache[key]
            slot.material = evidence
            assigned.append(evidence.name)
            images[image.name] = {
                "name": image.name,
                "size": [int(image.size[0]), int(image.size[1])],
                "colorspace": image.colorspace_settings.name,
                "file_format": image.file_format,
                "packed": bool(image.packed_file),
                "source_material": key,
            }
    return sorted(set(assigned)), list(images.values())


def create_flat_material(
    name: str,
    colour: tuple[float, float, float, float],
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = colour
    principled.inputs["Metallic"].default_value = 0.0
    principled.inputs["Roughness"].default_value = 0.95
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.10
    return material


def create_world(
    name: str,
    colour: tuple[float, float, float, float],
    strength: float,
) -> bpy.types.World:
    world = bpy.data.worlds.new(name)
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = colour
    background.inputs["Strength"].default_value = strength
    return world


def create_area_light(
    name: str,
    energy: float,
    size: float,
    colour: tuple[float, float, float],
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = colour
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_soft_lights(scale: float) -> dict[str, bpy.types.Object]:
    energy_scale = max(scale * scale, 0.01)
    return {
        "key": create_area_light(
            "VG04_MATTE_KEY",
            185.0 * energy_scale,
            scale * 1.9,
            (1.0, 0.97, 0.93),
        ),
        "fill": create_area_light(
            "VG04_MATTE_FILL",
            48.0 * energy_scale,
            scale * 2.5,
            (0.91, 0.95, 1.0),
        ),
        "rim": create_area_light(
            "VG04_MATTE_RIM",
            92.0 * energy_scale,
            scale * 1.5,
            (1.0, 0.93, 0.84),
        ),
        "top": create_area_light(
            "VG04_MATTE_TOP",
            32.0 * energy_scale,
            scale * 2.2,
            (1.0, 0.98, 0.94),
        ),
    }


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


def place_camera_and_lights(
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    target: Vector,
    direction: Vector,
    distance: float,
    scale: float,
) -> None:
    view = direction.normalized()
    up = Vector((0.0, 0.0, 1.0))
    right = view.cross(up)
    if right.length < 0.001:
        right = Vector((0.0, 1.0, 0.0))
    right.normalize()

    camera.location = target + view * distance
    point_at(camera, target)

    lights["key"].location = (
        target
        + view * distance * 0.55
        - right * scale * 1.15
        + up * scale * 1.25
    )
    lights["fill"].location = (
        target
        + view * distance * 0.42
        + right * scale * 1.35
        + up * scale * 0.30
    )
    lights["rim"].location = (
        target
        - view * distance * 0.45
        + right * scale * 0.30
        + up * scale * 1.10
    )
    lights["top"].location = target + up * scale * 2.70
    for light in lights.values():
        point_at(light, target)


def set_lights_visible(
    lights: dict[str, bpy.types.Object], visible: bool
) -> None:
    for light in lights.values():
        light.hide_render = not visible
        light.hide_set(not visible)


def create_camera() -> bpy.types.Object:
    data = bpy.data.cameras.new("VG04_ORTHOGRAPHIC_CAMERA")
    data.type = "ORTHO"
    data.lens = 70.0
    data.dof.use_dof = False
    camera = bpy.data.objects.new("VG04_ORTHOGRAPHIC_CAMERA", data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    return camera


def create_floor(
    minimum: Vector, center: Vector, scale: float
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(
        size=scale * 8.0,
        location=(
            center.x,
            center.y,
            minimum.z - scale * 0.008,
        ),
    )
    floor = bpy.context.active_object
    floor.name = "VG04_MATTE_NEUTRAL_GROUND"
    floor.data.materials.append(
        create_flat_material(
            "VG04_MATTE_NEUTRAL_GROUND_MATERIAL",
            (0.055, 0.065, 0.078, 1.0),
        )
    )
    return floor


def configure_render(resolution: int, samples: int) -> None:
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15
    scene.render.film_transparent = False
    scene.render.filter_size = 0.75
    scene.render.use_file_extension = True
    if hasattr(scene, "eevee") and hasattr(
        scene.eevee, "taa_render_samples"
    ):
        scene.eevee.taa_render_samples = samples


def set_view_transform(mode: str) -> None:
    scene = bpy.context.scene
    if mode == "basecolor":
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0
    elif mode == "matte":
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.exposure = -0.25
        scene.view_settings.gamma = 1.0
    else:
        raise ValueError(mode)
    for look in ("None", "Medium High Contrast", "AgX - Medium High Contrast"):
        try:
            scene.view_settings.look = look
            if mode == "basecolor" or look != "None":
                break
        except (TypeError, ValueError):
            continue


def configure_mode(
    mode: str,
    meshes: list[bpy.types.Object],
    source_materials: dict[str, list[bpy.types.Material | None]],
    lights: dict[str, bpy.types.Object],
    floor: bpy.types.Object,
    basecolor_world: bpy.types.World,
    matte_world: bpy.types.World,
) -> tuple[list[str], list[dict[str, object]]]:
    materials, images = assign_mode_materials(
        meshes, mode, source_materials
    )
    if mode == "basecolor":
        set_lights_visible(lights, False)
        floor.hide_render = True
        floor.hide_set(True)
        bpy.context.scene.world = basecolor_world
    else:
        set_lights_visible(lights, True)
        floor.hide_render = False
        floor.hide_set(False)
        bpy.context.scene.world = matte_world
    set_view_transform(mode)
    return materials, images


def render_still(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def feature_target(
    minimum: Vector,
    maximum: Vector,
    ratio: tuple[float, float, float],
) -> Vector:
    dimensions = maximum - minimum
    return Vector(
        (
            minimum.x + dimensions.x * ratio[0],
            minimum.y + dimensions.y * ratio[1],
            minimum.z + dimensions.z * ratio[2],
        )
    )


def render_views_and_closeups(
    output: Path,
    mode: str,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    minimum: Vector,
    maximum: Vector,
    directions: dict[str, Vector],
) -> tuple[dict[str, str], dict[str, str]]:
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    scale = max(dimensions)
    distance = max(scale * 3.2, 1.0)

    six_views: dict[str, str] = {}
    camera.data.ortho_scale = scale / 0.87
    for name, direction in directions.items():
        place_camera_and_lights(
            camera, lights, center, direction, distance, scale
        )
        six_views[name] = render_still(
            output / "renders" / mode / "six-view" / f"{name}.png"
        )

    closeup_specs = {
        "eyes": {
            "direction": directions["front"],
            "target": (0.52, 0.50, 0.705),
            "scale": 0.50,
        },
        "muzzle_and_neutral_mouth": {
            "direction": directions["front"],
            "target": (0.55, 0.50, 0.585),
            "scale": 0.43,
        },
        "neutral_mouth_three_quarter": {
            "direction": directions["three_quarter_right"],
            "target": (0.56, 0.50, 0.565),
            "scale": 0.44,
        },
        "primary_horns": {
            "direction": directions["three_quarter_left"],
            "target": (0.50, 0.50, 0.735),
            "scale": 0.62,
        },
        "frill_and_knobs": {
            "direction": directions["front"],
            "target": (0.48, 0.50, 0.735),
            "scale": 0.72,
        },
        "hands_and_fingers": {
            "direction": directions["front"],
            "target": (0.55, 0.50, 0.390),
            "scale": 0.62,
        },
        "feet_and_toes": {
            "direction": directions["front"],
            "target": (0.50, 0.50, 0.155),
            "scale": 0.50,
        },
        "tail_side": {
            "direction": directions["left"],
            "target": (0.28, 0.50, 0.34),
            "scale": 0.60,
        },
    }
    closeups: dict[str, str] = {}
    for name, spec in closeup_specs.items():
        target = feature_target(minimum, maximum, spec["target"])
        camera.data.ortho_scale = scale * float(spec["scale"])
        place_camera_and_lights(
            camera,
            lights,
            target,
            spec["direction"],
            distance,
            scale,
        )
        closeups[name] = render_still(
            output / "renders" / mode / "closeups" / f"{name}.png"
        )
    return six_views, closeups


def create_board(
    magick: str,
    output: Path,
    image_rows: list[tuple[str, str]],
    tile: str,
    geometry: str,
    title: str,
    subtitle: str,
) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    body = output.with_name(f"_{output.stem}_body.png")
    command = [
        magick,
        "montage",
        "-font",
        BOARD_FONT,
        "-pointsize",
        "22",
        "-fill",
        "#E8E0D2",
        "-background",
        "#20252D",
    ]
    for label, image in image_rows:
        command.extend(["-label", label, image])
    command.extend(
        ["-tile", tile, "-geometry", geometry, str(body)]
    )
    subprocess.run(command, check=True)
    subprocess.run(
        [
            magick,
            str(body),
            "-gravity",
            "north",
            "-background",
            "#20252D",
            "-splice",
            "0x126",
            "-fill",
            "#F2E6CF",
            "-font",
            BOARD_FONT,
            "-pointsize",
            "34",
            "-annotate",
            "+0+22",
            title,
            "-fill",
            "#B8C4D0",
            "-pointsize",
            "18",
            "-annotate",
            "+0+80",
            subtitle,
            str(output),
        ],
        check=True,
    )
    body.unlink(missing_ok=True)
    return str(output)


def create_mode_boards(
    output: Path,
    mode: str,
    six_views: dict[str, str],
    closeups: dict[str, str],
    candidate_id: str,
    task_id: str,
    reference_images: dict[str, str] | None,
) -> dict[str, str]:
    magick = shutil.which("magick")
    if not magick:
        return {}
    mode_label = (
        "BASE-COLOR TRUTH — EMISSION / STANDARD / NO LIGHTS"
        if mode == "basecolor"
        else "MATTE FORM — UNCHANGED BASE COLOR / SOFT LIGHTS / AGX"
    )
    subtitle = (
        f"{candidate_id} | task {task_id} | NO GEOMETRY EDITS | "
        "normal + ORM disconnected"
    )
    boards_dir = output / "boards"
    six_order = (
        "front",
        "left",
        "back",
        "right",
        "three_quarter_left",
        "three_quarter_right",
    )
    six_board = create_board(
        magick,
        boards_dir / f"vg04_{mode}_six_view.png",
        [
            (name.replace("_", " ").upper(), six_views[name])
            for name in six_order
        ],
        "3x2",
        "520x520+14+14",
        f"VISUAL GATE 04 — {mode_label}",
        subtitle,
    )
    closeup_order = (
        "eyes",
        "muzzle_and_neutral_mouth",
        "neutral_mouth_three_quarter",
        "primary_horns",
        "frill_and_knobs",
        "hands_and_fingers",
        "feet_and_toes",
        "tail_side",
    )
    closeup_board = create_board(
        magick,
        boards_dir / f"vg04_{mode}_feature_closeups.png",
        [
            (name.replace("_", " ").upper(), closeups[name])
            for name in closeup_order
        ],
        "4x2",
        "440x440+12+12",
        f"VISUAL GATE 04 — {mode.upper()} FEATURE CLOSE-UPS",
        subtitle,
    )
    result = {
        "six_view": six_board,
        "feature_closeups": closeup_board,
    }
    if reference_images:
        cardinal = ("front", "left", "back", "right")
        comparison_rows = [
            (f"REFERENCE {role.upper()}", reference_images[role])
            for role in cardinal
        ] + [
            (f"RENDER {role.upper()}", six_views[role])
            for role in cardinal
        ]
        result["reference_comparison"] = create_board(
            magick,
            boards_dir / f"vg04_{mode}_reference_comparison.png",
            comparison_rows,
            "4x2",
            "440x440+12+12",
            f"VISUAL GATE 04 — {mode.upper()} VS CANONICAL REFERENCES",
            subtitle,
        )
    return result


def reference_image_metrics(
    paths: list[Path] | None,
) -> tuple[dict[str, object], dict[str, str] | None]:
    if not paths:
        return {}, None
    metrics: dict[str, object] = {}
    board_paths: dict[str, str] = {}
    for role, path in zip(REFERENCE_ROLES, paths):
        image = bpy.data.images.load(str(path), check_existing=False)
        metrics[role] = {
            "path": str(path),
            "sha256": sha256(path),
            "size": [int(image.size[0]), int(image.size[1])],
            "colorspace": image.colorspace_settings.name,
            "file_format": image.file_format,
        }
        board_paths[role] = str(path)
        bpy.data.images.remove(image)
    return metrics, board_paths


def load_task_metadata(
    task_json: Path | None, explicit_task_id: str | None
) -> tuple[str, dict[str, object]]:
    metadata: dict[str, object] = {}
    if task_json:
        metadata = json.loads(task_json.read_text(encoding="utf-8"))
    task_id = explicit_task_id or str(metadata.get("task_id") or "not-supplied")
    return task_id, metadata


def write_readme(
    output: Path,
    candidate_id: str,
    task_id: str,
    modes: list[str],
    geometry_match: bool | None,
) -> str:
    readme = output / "README.md"
    readme.write_text(
        f"""# Visual Gate 04 — Textured Hero Candidate

**Candidate:** `{candidate_id}`  
**Tripo task:** `{task_id}`  
**Rendered modes:** `{", ".join(modes)}`  
**Geometry matches frozen reference:** `{geometry_match}`

This package separates texture truth from presentation:

- `basecolor`: the actual linked base-colour image goes directly to Emission,
  with Standard view transform, no lights, no floor, no normal/ORM maps, and
  no colour correction.
- `matte`: the same unchanged image goes directly to Principled Base Color,
  with metallic `0`, roughness `.82`, specular IOR level `.18`, no normal/ORM
  maps, soft neutral lights, and AgX.

The source import is locked and hidden. Renderable meshes are deep duplicates.
The evaluator changes material assignments only. It performs **no geometry,
face, mouth, smoothing, retopology, rigging, or animation edits**.

Evidence is in `boards/`, raw renders are in `renders/`, and deterministic
source/reference checks are in `metrics.json`. No `.blend` is saved or packed.

These images are evidence for the user's visual approval. The evaluator does
not approve the character.
""",
        encoding="utf-8",
    )
    return str(readme)


def main() -> None:
    args = parse_args()
    args.input = args.input.expanduser().resolve()
    args.output = args.output.expanduser().resolve()
    if not args.input.exists():
        raise FileNotFoundError(args.input)
    if args.reference_geometry:
        args.reference_geometry = (
            args.reference_geometry.expanduser().resolve()
        )
        if not args.reference_geometry.exists():
            raise FileNotFoundError(args.reference_geometry)
    if args.task_json:
        args.task_json = args.task_json.expanduser().resolve()
        if not args.task_json.exists():
            raise FileNotFoundError(args.task_json)
    if args.reference_images:
        args.reference_images = [
            path.expanduser().resolve() for path in args.reference_images
        ]
        for path in args.reference_images:
            if not path.exists():
                raise FileNotFoundError(path)

    args.output.mkdir(parents=True, exist_ok=True)
    task_id, task_metadata = load_task_metadata(
        args.task_json, args.task_id
    )

    clear_scene()
    reference_geometry = None
    if args.reference_geometry:
        reference_geometry, reference_import = import_reference_for_metrics(
            args.reference_geometry
        )
        remove_import(reference_import)

    source_meshes, render_meshes = import_locked_and_duplicate(args.input)
    source_materials = {
        obj.name: [slot.material for slot in obj.material_slots]
        for obj in render_meshes
    }
    candidate_geometry = geometry_metrics(source_meshes, args.input)
    geometry_comparison = compare_geometry(
        candidate_geometry, reference_geometry
    )
    minimum, maximum = world_bounds(render_meshes)
    center = (minimum + maximum) * 0.5
    scale = max(maximum - minimum)

    reference_metrics, reference_board_paths = reference_image_metrics(
        args.reference_images
    )

    configure_render(args.resolution, args.samples)
    camera = create_camera()
    lights = create_soft_lights(scale)
    floor = create_floor(minimum, center, scale)
    basecolor_world = create_world(
        "VG04_BASECOLOR_WORLD",
        (0.018, 0.022, 0.028, 1.0),
        1.0,
    )
    matte_world = create_world(
        "VG04_MATTE_WORLD",
        (0.035, 0.042, 0.052, 1.0),
        0.12,
    )
    directions = view_directions(args.front_axis)
    modes = (
        ["basecolor", "matte"]
        if args.mode == "both"
        else [args.mode]
    )

    mode_outputs: dict[str, object] = {}
    material_evidence: dict[str, object] = {}
    for mode in modes:
        materials, images = configure_mode(
            mode,
            render_meshes,
            source_materials,
            lights,
            floor,
            basecolor_world,
            matte_world,
        )
        six_views, closeups = render_views_and_closeups(
            args.output,
            mode,
            camera,
            lights,
            minimum,
            maximum,
            directions,
        )
        boards = create_mode_boards(
            args.output,
            mode,
            six_views,
            closeups,
            args.candidate_id,
            task_id,
            reference_board_paths,
        )
        mode_outputs[mode] = {
            "six_views": {
                key: relative_path(Path(value), args.output)
                for key, value in six_views.items()
            },
            "closeups": {
                key: relative_path(Path(value), args.output)
                for key, value in closeups.items()
            },
            "boards": {
                key: relative_path(Path(value), args.output)
                for key, value in boards.items()
            },
        }
        material_evidence[mode] = {
            "materials": materials,
            "base_color_images": images,
            "normal_map_connected": False,
            "orm_map_connected": False,
            "colour_corrections_applied": False,
            "geometry_edits_applied": False,
        }

    readme = write_readme(
        args.output,
        args.candidate_id,
        task_id,
        modes,
        geometry_comparison["geometry_match"],
    )
    metrics = {
        "evaluator": {
            "id": EVALUATOR_ID,
            "version": EVALUATOR_VERSION,
            "blender_version": bpy.app.version_string,
        },
        "candidate_id": args.candidate_id,
        "task": {
            "task_id": task_id,
            "task_json": str(args.task_json) if args.task_json else None,
            "type": task_metadata.get("type"),
            "status": task_metadata.get("status"),
            "credits_consumed": task_metadata.get("credits_consumed"),
        },
        "render_contract": {
            "modes": modes,
            "resolution": args.resolution,
            "samples": args.samples,
            "front_axis": args.front_axis,
            "source_locked": True,
            "render_uses_deep_mesh_duplicates": True,
            "geometry_edits_applied": False,
            "face_or_mouth_edits_applied": False,
            "normal_map_connected": False,
            "orm_map_connected": False,
            "colour_corrections_applied": False,
            "blend_saved": False,
            "blend_packed": False,
        },
        "candidate_geometry": candidate_geometry,
        "reference_geometry": reference_geometry,
        "geometry_comparison": geometry_comparison,
        "reference_images": reference_metrics,
        "materials": material_evidence,
        "outputs": mode_outputs,
        "readme": relative_path(Path(readme), args.output),
    }
    metrics_path = args.output / "metrics.json"
    metrics_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "success",
                "metrics": str(metrics_path),
                "geometry_match": geometry_comparison["geometry_match"],
                "modes": modes,
                "boards": {
                    mode: mode_outputs[mode]["boards"] for mode in modes
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
