"""Build Bentosaur P1 Lookdev Preview 0 without modifying the source GLB.

This script intentionally produces a *provisional* appearance preview. It is
not a production character master, a rig, or an animation test. It answers a
single visual question: what does the accepted P1 geometry and its existing
Tripo base-colour texture look like under controlled, matte lighting?

The source GLB is imported into a locked collection and hidden. Every render
uses a deep mesh duplicate. The Tripo ORM and normal map are deliberately not
connected because the earlier QA scene overexposed the material and amplified
surface noise. No network or Tripo API calls are made.

Run with:

    /Applications/Blender.app/Contents/MacOS/Blender \
      --background --factory-startup \
      --python tools/blender/build_p1_lookdev_preview_zero.py -- \
      --input /absolute/path/to/model.glb \
      --output /absolute/path/to/lookdev-preview-0
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Iterable

import bpy
from mathutils import Vector


PREVIEW_ID = "bentosaur_p1_lookdev_preview_0"
PREVIEW_LABEL = "LOOKDEV PREVIEW 0 — PROVISIONAL / NOT FINAL"
BOARD_FONT = "/System/Library/Fonts/Helvetica.ttc"

VIEW_DIRECTIONS = {
    # Tripo's P1 GLB faces Blender +X after glTF import.
    "front": Vector((1.0, 0.0, 0.0)),
    "left": Vector((0.0, 1.0, 0.0)),
    "back": Vector((-1.0, 0.0, 0.0)),
    "right": Vector((0.0, -1.0, 0.0)),
    "three_quarter_left": Vector((1.0, 1.0, 0.08)).normalized(),
    "three_quarter_right": Vector((1.0, -1.0, 0.08)).normalized(),
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resolution", type=int, default=768)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def import_locked_and_duplicate(
    source: Path,
) -> tuple[list[bpy.types.Object], list[bpy.types.Object]]:
    raw_collection = bpy.data.collections.new("00_RAW_P1_IMPORT_LOCKED")
    bpy.context.scene.collection.children.link(raw_collection)
    preview_collection = bpy.data.collections.new("10_LOOKDEV_PREVIEW_ZERO")
    bpy.context.scene.collection.children.link(preview_collection)

    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    source_meshes = [obj for obj in imported if obj.type == "MESH"]
    if not source_meshes:
        raise RuntimeError("The P1 source GLB contains no mesh objects.")

    for obj in imported:
        link_exclusively(obj, raw_collection)
        obj.hide_render = True
        obj.hide_set(True)
        obj["bentosaur_source_locked"] = True

    preview_meshes: list[bpy.types.Object] = []
    for source_obj in source_meshes:
        duplicate = source_obj.copy()
        duplicate.data = source_obj.data.copy()
        duplicate.animation_data_clear()
        duplicate.parent = None
        duplicate.matrix_world = source_obj.matrix_world.copy()
        duplicate.name = f"PREVIEW0_{source_obj.name}"
        if "bentosaur_source_locked" in duplicate:
            del duplicate["bentosaur_source_locked"]
        duplicate["provisional_lookdev_preview"] = True
        preview_collection.objects.link(duplicate)
        duplicate.hide_render = False
        duplicate.hide_set(False)
        for polygon in duplicate.data.polygons:
            polygon.use_smooth = True
        preview_meshes.append(duplicate)

    return source_meshes, preview_meshes


def world_bounds(
    mesh_objects: Iterable[bpy.types.Object],
) -> tuple[Vector, Vector]:
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


def find_base_colour_image(
    material: bpy.types.Material | None,
) -> bpy.types.Image | None:
    if not material or not material.use_nodes:
        return None
    image_nodes = [
        node
        for node in material.node_tree.nodes
        if node.bl_idname == "ShaderNodeTexImage" and node.image
    ]
    for node in image_nodes:
        if node.image.colorspace_settings.name in {
            "sRGB",
            "Utility - sRGB - Texture",
        }:
            return node.image
    return image_nodes[0].image if image_nodes else None


def make_matte_albedo_material(
    source: bpy.types.Material | None,
) -> bpy.types.Material:
    source_name = source.name if source else "missing"
    material = bpy.data.materials.new(
        f"PREVIEW0_MATTE_ALBEDO__{source_name}"
    )
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.name = "PREVIEW0_MATTE_PRINCIPLED"
    principled.inputs["Metallic"].default_value = 0.0
    principled.inputs["Roughness"].default_value = 0.79
    principled.inputs["IOR"].default_value = 1.45
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.24
    if "Coat Weight" in principled.inputs:
        principled.inputs["Coat Weight"].default_value = 0.0

    image = find_base_colour_image(source)
    if image:
        texture = nodes.new("ShaderNodeTexImage")
        texture.name = "P1_EXISTING_BASE_COLOUR_ONLY"
        texture.image = image
        texture.interpolation = "Linear"
        texture.extension = "REPEAT"

        # The source albedo already contains the approved sage/cream/coral/ink
        # families. A tiny saturation/value correction counters the pale Tripo
        # preview without pretending this is an authored final texture.
        colour = nodes.new("ShaderNodeHueSaturation")
        colour.name = "PREVIEW0_SUBTLE_ALBEDO_CORRECTION"
        colour.inputs["Hue"].default_value = 0.5
        colour.inputs["Saturation"].default_value = 1.06
        colour.inputs["Value"].default_value = 0.96
        colour.inputs["Fac"].default_value = 1.0
        links.new(texture.outputs["Color"], colour.inputs["Color"])
        links.new(colour.outputs["Color"], principled.inputs["Base Color"])
    else:
        principled.inputs["Base Color"].default_value = (
            0.166,
            0.250,
            0.184,
            1.0,
        )

    # Intentionally omit ORM and normal-map links. This preview is for colour
    # and broad form, and the generated normal map created noisy facets.
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    return material


def assign_preview_materials(
    preview_meshes: list[bpy.types.Object],
) -> list[str]:
    cache: dict[str, bpy.types.Material] = {}
    assigned: list[str] = []
    for obj in preview_meshes:
        for slot in obj.material_slots:
            source = slot.material
            key = source.name if source else "__missing__"
            if key not in cache:
                cache[key] = make_matte_albedo_material(source)
            slot.material = cache[key]
            assigned.append(cache[key].name)
    return sorted(set(assigned))


def make_flat_material(
    name: str,
    colour: tuple[float, float, float, float],
    roughness: float = 0.85,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    if emission_strength > 0.0:
        shader = nodes.new("ShaderNodeEmission")
        shader.inputs["Color"].default_value = colour
        shader.inputs["Strength"].default_value = emission_strength
        links.new(shader.outputs["Emission"], output.inputs["Surface"])
    else:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        shader.inputs["Base Color"].default_value = colour
        shader.inputs["Metallic"].default_value = 0.0
        shader.inputs["Roughness"].default_value = roughness
        if "Specular IOR Level" in shader.inputs:
            shader.inputs["Specular IOR Level"].default_value = 0.18
        links.new(shader.outputs["BSDF"], output.inputs["Surface"])
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


def configure_render(width: int, height: int, filter_size: float = 1.0) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.filter_size = filter_size
    scene.render.use_file_extension = True
    scene.render.image_settings.compression = 15
    try:
        scene.view_settings.view_transform = "AgX"
    except (TypeError, ValueError):
        pass
    scene.view_settings.exposure = -0.35


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(
    center: Vector, dimensions: Vector
) -> tuple[bpy.types.Object, float]:
    camera_data = bpy.data.cameras.new("PREVIEW0_ORTHO_CAMERA")
    camera = bpy.data.objects.new("PREVIEW0_ORTHO_CAMERA", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    camera.data.type = "ORTHO"
    maximum = max(dimensions)
    camera.data.ortho_scale = maximum / 0.86
    return camera, max(maximum * 3.2, 1.0)


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


def create_light_rig(scale: float) -> dict[str, bpy.types.Object]:
    # Deliberately far below the previous 850/350/650 QA rig.
    return {
        "key": create_area_light(
            "PREVIEW0_KEY", 185.0 * scale * scale, scale * 1.9, (1.0, 0.97, 0.93)
        ),
        "fill": create_area_light(
            "PREVIEW0_FILL", 48.0 * scale * scale, scale * 2.5, (0.91, 0.95, 1.0)
        ),
        "rim": create_area_light(
            "PREVIEW0_RIM", 92.0 * scale * scale, scale * 1.5, (1.0, 0.93, 0.84)
        ),
    }


def configure_light_rig(
    lights: dict[str, bpy.types.Object],
    scale: float,
    mode: str,
) -> None:
    if mode == "neutral":
        values = {
            "key": (185.0 * scale * scale, (1.0, 0.97, 0.93)),
            "fill": (48.0 * scale * scale, (0.91, 0.95, 1.0)),
            "rim": (92.0 * scale * scale, (1.0, 0.93, 0.84)),
        }
    elif mode == "rainy":
        values = {
            "key": (245.0 * scale * scale, (1.0, 0.60, 0.28)),
            "fill": (42.0 * scale * scale, (0.28, 0.46, 1.0)),
            "rim": (125.0 * scale * scale, (0.36, 0.58, 1.0)),
        }
    else:
        raise ValueError(mode)
    for name, (energy, colour) in values.items():
        lights[name].data.energy = energy
        lights[name].data.color = colour


def place_camera_and_lights(
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    target: Vector,
    direction: Vector,
    distance: float,
    scale: float,
) -> None:
    view = direction.normalized()
    camera.location = target + view * distance
    point_at(camera, target)
    up = Vector((0.0, 0.0, 1.0))
    right = view.cross(up)
    if right.length < 0.001:
        right = Vector((0.0, 1.0, 0.0))
    right.normalize()
    lights["key"].location = (
        target + view * distance * 0.55 - right * scale * 1.15 + up * scale * 1.25
    )
    lights["fill"].location = (
        target + view * distance * 0.42 + right * scale * 1.35 + up * scale * 0.30
    )
    lights["rim"].location = (
        target - view * distance * 0.45 + right * scale * 0.30 + up * scale * 1.10
    )
    for light in lights.values():
        point_at(light, target)


def create_neutral_floor(
    minimum: Vector, scale: float
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=scale * 5.0)
    floor = bpy.context.active_object
    floor.name = "PREVIEW0_NEUTRAL_FLOOR"
    floor.location = (0.0, 0.0, minimum.z - scale * 0.012)
    floor.data.materials.append(
        make_flat_material(
            "PREVIEW0_NEUTRAL_FLOOR_MATERIAL",
            (0.115, 0.128, 0.145, 1.0),
            roughness=0.92,
        )
    )
    return floor


def move_to_collection(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> None:
    link_exclusively(obj, collection)


def create_rainy_stall_proxy(
    minimum: Vector,
    maximum: Vector,
    scale: float,
) -> list[bpy.types.Object]:
    collection = bpy.data.collections.new("90_RAINY_STALL_CAMERA_PROXY")
    bpy.context.scene.collection.children.link(collection)
    objects: list[bpy.types.Object] = []

    navy = make_flat_material(
        "PREVIEW0_RAINY_BACKDROP",
        (0.012, 0.025, 0.085, 1.0),
        roughness=0.95,
    )
    wood = make_flat_material(
        "PREVIEW0_COUNTER_PROXY",
        (0.22, 0.075, 0.035, 1.0),
        roughness=0.84,
    )
    rain = make_flat_material(
        "PREVIEW0_RAIN_STREAK",
        (0.15, 0.42, 1.0, 1.0),
        emission_strength=1.25,
    )
    amber = make_flat_material(
        "PREVIEW0_LANTERN_GLOW",
        (1.0, 0.26, 0.045, 1.0),
        emission_strength=2.1,
    )

    bpy.ops.mesh.primitive_cube_add()
    backdrop = bpy.context.active_object
    backdrop.name = "PREVIEW0_RAINY_BACKDROP_PROXY"
    backdrop.location = (
        minimum.x - scale * 0.10,
        0.0,
        (minimum.z + maximum.z) * 0.5,
    )
    backdrop.dimensions = (scale * 0.035, scale * 2.2, scale * 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    backdrop.data.materials.append(navy)
    move_to_collection(backdrop, collection)
    objects.append(backdrop)

    bpy.ops.mesh.primitive_cube_add()
    counter = bpy.context.active_object
    counter.name = "PREVIEW0_COUNTER_PROXY"
    counter.location = (
        maximum.x + scale * 0.10,
        0.0,
        minimum.z + scale * 0.24,
    )
    counter.dimensions = (scale * 0.18, scale * 1.45, scale * 0.28)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    counter.data.materials.append(wood)
    move_to_collection(counter, collection)
    objects.append(counter)

    streak_data = [
        (-0.62, 0.34, 0.12),
        (-0.48, -0.05, 0.08),
        (-0.33, 0.20, 0.10),
        (-0.18, -0.22, 0.14),
        (-0.04, 0.42, 0.08),
        (0.10, 0.06, 0.11),
        (0.24, -0.30, 0.09),
        (0.38, 0.31, 0.13),
        (0.52, -0.08, 0.10),
        (0.64, 0.18, 0.08),
    ]
    backdrop_x = minimum.x - scale * 0.075
    for index, (y_factor, z_factor, length_factor) in enumerate(streak_data):
        bpy.ops.mesh.primitive_cube_add()
        streak = bpy.context.active_object
        streak.name = f"PREVIEW0_RAIN_STREAK_{index:02d}"
        streak.location = (
            backdrop_x,
            y_factor * scale,
            minimum.z + (z_factor + 0.52) * scale,
        )
        streak.dimensions = (
            scale * 0.018,
            scale * 0.012,
            scale * length_factor,
        )
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        streak.data.materials.append(rain)
        move_to_collection(streak, collection)
        objects.append(streak)

    for index, y_factor in enumerate((-0.56, 0.56)):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=24,
            ring_count=12,
            radius=scale * 0.055,
            location=(
                backdrop_x + scale * 0.015,
                y_factor * scale,
                minimum.z + scale * 0.70,
            ),
        )
        glow = bpy.context.active_object
        glow.name = f"PREVIEW0_LANTERN_GLOW_{index:02d}"
        glow.data.materials.append(amber)
        move_to_collection(glow, collection)
        objects.append(glow)

    for obj in objects:
        obj.hide_render = True
    return objects


def set_render_visibility(objects: Iterable[bpy.types.Object], visible: bool) -> None:
    for obj in objects:
        obj.hide_render = not visible


def render_still(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def render_neutral_views(
    output: Path,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    center: Vector,
    distance: float,
    scale: float,
    full_ortho_scale: float,
    resolution: int,
) -> dict[str, str]:
    configure_render(resolution, resolution, filter_size=0.75)
    camera.data.ortho_scale = full_ortho_scale
    rendered: dict[str, str] = {}
    for name, direction in VIEW_DIRECTIONS.items():
        place_camera_and_lights(
            camera, lights, center, direction, distance, scale
        )
        rendered[name] = render_still(
            output / "renders" / "neutral" / f"{name}.png"
        )
    return rendered


def render_face_closeup(
    output: Path,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    center: Vector,
    minimum: Vector,
    dimensions: Vector,
    distance: float,
    scale: float,
    resolution: int,
) -> str:
    configure_render(resolution, resolution, filter_size=0.75)
    head_target = Vector(
        (
            center.x,
            center.y,
            minimum.z + dimensions.z * 0.77,
        )
    )
    camera.data.ortho_scale = dimensions.z * 0.82
    place_camera_and_lights(
        camera,
        lights,
        head_target,
        VIEW_DIRECTIONS["front"],
        distance,
        scale,
    )
    return render_still(
        output / "renders" / "face" / "front_face_closeup.png"
    )


def render_native_scale(
    output: Path,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    center: Vector,
    distance: float,
    scale: float,
    full_ortho_scale: float,
    resolution: int,
) -> str:
    configure_render(resolution, resolution, filter_size=0.01)
    camera.data.ortho_scale = full_ortho_scale
    place_camera_and_lights(
        camera,
        lights,
        center,
        VIEW_DIRECTIONS["front"],
        distance,
        scale,
    )
    return render_still(
        output
        / "renders"
        / f"pixel{resolution}"
        / f"front_native_{resolution}px.png"
    )


def render_rainy_camera(
    output: Path,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    center: Vector,
    minimum: Vector,
    dimensions: Vector,
    distance: float,
    scale: float,
    proxy: list[bpy.types.Object],
    neutral_floor: bpy.types.Object,
    rainy_world: bpy.types.World,
) -> str:
    scene = bpy.context.scene
    set_render_visibility(proxy, True)
    neutral_floor.hide_render = True
    scene.world = rainy_world
    scene.view_settings.exposure = -0.55
    configure_light_rig(lights, scale, "rainy")
    configure_render(768, 1024, filter_size=0.75)
    scene.view_settings.exposure = -0.55

    target = Vector(
        (
            center.x,
            center.y,
            minimum.z + dimensions.z * 0.62,
        )
    )
    camera.data.ortho_scale = dimensions.z * 1.02
    direction = Vector((1.0, -0.12, 0.035)).normalized()
    place_camera_and_lights(
        camera, lights, target, direction, distance, scale
    )
    path = render_still(
        output
        / "renders"
        / "rainy_stall_like"
        / "rainy_stall_lighting_camera.png"
    )

    set_render_visibility(proxy, False)
    neutral_floor.hide_render = False
    return path


def add_board_header(
    magick: str,
    body: Path,
    output: Path,
    subtitle: str,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        magick,
        str(body),
        "-gravity",
        "north",
        "-background",
        "#20252D",
        "-splice",
        "0x112",
        "-fill",
        "#F4E9D1",
        "-font",
        BOARD_FONT,
        "-pointsize",
        "36",
        "-annotate",
        "+0+24",
        PREVIEW_LABEL,
        "-fill",
        "#B9C6D3",
        "-pointsize",
        "21",
        "-annotate",
        "+0+75",
        subtitle,
        str(output),
    ]
    subprocess.run(command, check=True)


def create_review_boards(
    output: Path,
    neutral: dict[str, str],
    face: str,
    pixel64: str,
    pixel96: str,
    rainy: str,
) -> dict[str, str]:
    magick = shutil.which("magick")
    if not magick:
        return {}

    boards = output / "boards"
    boards.mkdir(parents=True, exist_ok=True)

    six_body = boards / "_six_view_body.png"
    six_board = boards / "lookdev_preview0_six_view_board.png"
    subprocess.run(
        [
            magick,
            "montage",
            "-font",
            BOARD_FONT,
            neutral["front"],
            neutral["left"],
            neutral["back"],
            neutral["right"],
            neutral["three_quarter_left"],
            neutral["three_quarter_right"],
            "-tile",
            "3x2",
            "-geometry",
            "520x520+12+12",
            "-background",
            "#20252D",
            str(six_body),
        ],
        check=True,
    )
    add_board_header(
        magick,
        six_body,
        six_board,
        "P1 geometry + existing Tripo albedo under controlled matte lighting; no rig or animation",
    )
    six_body.unlink(missing_ok=True)

    focus_body = boards / "_focus_body.png"
    focus_board = boards / "lookdev_preview0_face_and_rainy_board.png"
    subprocess.run(
        [
            magick,
            "montage",
            "-font",
            BOARD_FONT,
            face,
            rainy,
            "-tile",
            "2x1",
            "-geometry",
            "700x900+14+14",
            "-background",
            "#20252D",
            str(focus_body),
        ],
        check=True,
    )
    add_board_header(
        magick,
        focus_body,
        focus_board,
        "Neutral face close-up | rainy-stall-like lighting/camera proxy (pose remains neutral)",
    )
    focus_body.unlink(missing_ok=True)

    pixel_body = boards / "_pixel_body.png"
    pixel_board = boards / "lookdev_preview0_native_scale_board.png"
    subprocess.run(
        [
            magick,
            "montage",
            "-font",
            BOARD_FONT,
            pixel64,
            pixel96,
            "-filter",
            "point",
            "-tile",
            "2x1",
            "-geometry",
            "576x576+18+18",
            "-background",
            "#20252D",
            str(pixel_body),
        ],
        check=True,
    )
    add_board_header(
        magick,
        pixel_body,
        pixel_board,
        "Native 64 px | native 96 px readability diagnostics enlarged with nearest-neighbour",
    )
    pixel_body.unlink(missing_ok=True)

    return {
        "six_view": str(six_board),
        "face_and_rainy": str(focus_board),
        "native_scale": str(pixel_board),
    }


def write_readme(output: Path) -> None:
    readme = output / "README.md"
    readme.write_text(
        f"""# Bentosaur P1 Lookdev Preview 0

**Status:** PROVISIONAL LOOKDEV PREVIEW — NOT FINAL

This package uses the accepted P1 geometry and its existing packed Tripo
base-colour image under corrected, matte Blender lighting.

It is truthful evidence of:

- the current P1 shape;
- the current sage, cream, coral, and ink texture information;
- neutral multi-angle readability;
- native 64 px and 96 px readability;
- a fixed rainy-stall-like lighting/camera test.

It is **not** evidence of:

- final authored materials or final palette calibration;
- clean or deformation-ready topology;
- a production eye or mouth system;
- an open mouth or mouth interior;
- retopology, skinning, rigging, animation, or a gameplay shader.

The rainy-stall image contains only a disposable backdrop, counter, rain, and
lighting proxy. The P1 character remains in its neutral unrigged pose.

No Tripo API request was made and no Tripo credits were consumed.
""",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    output.mkdir(parents=True, exist_ok=True)

    clear_scene()
    source_meshes, preview_meshes = import_locked_and_duplicate(source)
    assigned_materials = assign_preview_materials(preview_meshes)

    minimum, maximum = world_bounds(preview_meshes)
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    scale = max(dimensions)

    neutral_world = create_world(
        "PREVIEW0_NEUTRAL_WORLD",
        (0.055, 0.070, 0.095, 1.0),
        0.18,
    )
    rainy_world = create_world(
        "PREVIEW0_RAINY_WORLD",
        (0.005, 0.012, 0.055, 1.0),
        0.10,
    )
    bpy.context.scene.world = neutral_world

    camera, distance = create_camera(center, dimensions)
    full_ortho_scale = camera.data.ortho_scale
    lights = create_light_rig(scale)
    configure_light_rig(lights, scale, "neutral")
    neutral_floor = create_neutral_floor(minimum, scale)
    rainy_proxy = create_rainy_stall_proxy(
        minimum, maximum, scale
    )

    neutral = render_neutral_views(
        output,
        camera,
        lights,
        center,
        distance,
        scale,
        full_ortho_scale,
        args.resolution,
    )
    face = render_face_closeup(
        output,
        camera,
        lights,
        center,
        minimum,
        dimensions,
        distance,
        scale,
        args.resolution,
    )
    pixel64 = render_native_scale(
        output,
        camera,
        lights,
        center,
        distance,
        scale,
        full_ortho_scale,
        64,
    )
    pixel96 = render_native_scale(
        output,
        camera,
        lights,
        center,
        distance,
        scale,
        full_ortho_scale,
        96,
    )
    rainy = render_rainy_camera(
        output,
        camera,
        lights,
        center,
        minimum,
        dimensions,
        distance,
        scale,
        rainy_proxy,
        neutral_floor,
        rainy_world,
    )

    # Restore a neutral, reproducible saved scene.
    set_render_visibility(rainy_proxy, False)
    neutral_floor.hide_render = False
    bpy.context.scene.world = neutral_world
    configure_light_rig(lights, scale, "neutral")
    configure_render(args.resolution, args.resolution, filter_size=0.75)
    bpy.context.scene.view_settings.exposure = -0.35
    camera.data.ortho_scale = full_ortho_scale
    place_camera_and_lights(
        camera,
        lights,
        center,
        VIEW_DIRECTIONS["front"],
        distance,
        scale,
    )

    blend_path = output / "bentosaur_p1_lookdev_preview0.blend"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    boards = create_review_boards(
        output, neutral, face, pixel64, pixel96, rainy
    )
    write_readme(output)

    topology = {
        "objects": len(preview_meshes),
        "vertices": sum(len(obj.data.vertices) for obj in preview_meshes),
        "polygons": sum(len(obj.data.polygons) for obj in preview_meshes),
        "triangles": 0,
        "uv_layers": sum(len(obj.data.uv_layers) for obj in preview_meshes),
        "shape_keys": sum(
            len(obj.data.shape_keys.key_blocks)
            if obj.data.shape_keys
            else 0
            for obj in preview_meshes
        ),
    }
    for obj in preview_meshes:
        obj.data.calc_loop_triangles()
        topology["triangles"] += len(obj.data.loop_triangles)

    manifest = {
        "schema_version": "1.0.0",
        "preview_id": PREVIEW_ID,
        "label": PREVIEW_LABEL,
        "status": "provisional_lookdev_preview_not_final",
        "source": {
            "path": str(source),
            "sha256": sha256(source),
            "bytes": source.stat().st_size,
            "modified": False,
            "source_mesh_objects": [obj.name for obj in source_meshes],
        },
        "truthful_scope": [
            "accepted P1 geometry",
            "existing packed Tripo base-colour image",
            "controlled neutral matte Blender lighting",
            "native 64 px and 96 px readability",
            "rainy-stall-like fixed lighting and camera proxy",
        ],
        "not_approved_or_proven": [
            "final authored materials",
            "final palette calibration",
            "clean deformation-ready topology",
            "production eyes",
            "production mouth or mouth interior",
            "retopology",
            "rigging",
            "skinning",
            "animation",
            "final Godot shader",
        ],
        "material_preview": {
            "source_base_colour_used": True,
            "source_orm_used": False,
            "source_normal_used": False,
            "hue": 0.5,
            "saturation": 1.06,
            "value": 0.96,
            "metallic": 0.0,
            "roughness": 0.79,
            "specular_ior_level": 0.24,
            "materials": assigned_materials,
        },
        "blender": {
            "version": bpy.app.version_string,
            "script": str(Path(__file__).resolve()),
            "blend": str(blend_path),
            "render_engine": bpy.context.scene.render.engine,
            "neutral_exposure": -0.35,
            "normal_map_intentionally_disconnected": True,
        },
        "topology_unchanged_from_preview_copy": topology,
        "tripo_usage": {
            "api_calls": 0,
            "credits_consumed": 0,
            "usd_consumed": 0.0,
        },
        "rigging_or_animation": {
            "armature_created": False,
            "shape_keys_created": False,
            "animation_created": False,
        },
        "renders": {
            "neutral": neutral,
            "face_closeup": face,
            "pixel64": pixel64,
            "pixel96": pixel96,
            "rainy_stall_like": rainy,
            "boards": boards,
        },
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "status": "success",
                "preview_id": PREVIEW_ID,
                "output": str(output),
                "blend": str(blend_path),
                "manifest": str(manifest_path),
                "boards": boards,
                "tripo_credits_consumed": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
