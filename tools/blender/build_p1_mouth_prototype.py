"""Build a non-destructive P1 mouth-construction prototype.

This is a geometry and look-development diagnostic, not production
retopology. The source GLB is imported into a locked collection and is never
modified. The script works on deep mesh copies and produces:

* an untouched neutral P1 reference;
* an open, toothless mouth carved into a P1 duplicate;
* a genuinely recessed dark mouth cavity;
* a separate coral tongue mesh;
* a separate three-dimensional lip-rim diagnostic;
* front, three-quarter, side, and mouth close-up renders.

Run with:

    /Applications/Blender.app/Contents/MacOS/Blender \
      --background --factory-startup \
      --python tools/blender/build_p1_mouth_prototype.py -- \
      --input /absolute/path/model.glb \
      --output /absolute/path/mouth-prototype
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


FRONT = Vector((1.0, 0.0, 0.0))
THREE_QUARTER = Vector((1.0, 1.0, 0.08)).normalized()
SIDE = Vector((0.0, 1.0, 0.0))

# P1 faces Blender +X after glTF import. These coordinates were measured from
# the evaluation blend and are deliberately confined to the existing muzzle.
MOUTH_CENTER = Vector((0.390, 0.0, -0.018))
MOUTH_RADIUS_DEPTH = 0.132
MOUTH_RADIUS_HORIZONTAL = 0.070
MOUTH_RADIUS_VERTICAL = 0.043
LIP_TUBE_RADIUS = 0.0040


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=768)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
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


def make_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def import_source_locked(
    source: Path,
) -> tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object]:
    source_collection = make_collection("00_SOURCE_LOCKED_DO_NOT_EDIT")
    neutral_collection = make_collection("10_NEUTRAL_REFERENCE")
    prototype_collection = make_collection("20_MOUTH_PROTOTYPE_NOT_PRODUCTION")

    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = list(bpy.context.selected_objects)
    source_meshes = [obj for obj in imported if obj.type == "MESH"]
    if len(source_meshes) != 1:
        raise RuntimeError(
            f"Expected exactly one source mesh, found {len(source_meshes)}."
        )

    source_obj = source_meshes[0]
    for obj in imported:
        link_exclusively(obj, source_collection)
        obj.hide_render = True
        obj.hide_set(True)

    neutral = source_obj.copy()
    neutral.data = source_obj.data.copy()
    neutral.animation_data_clear()
    neutral.parent = None
    neutral.matrix_world = source_obj.matrix_world.copy()
    neutral.name = "P1_NEUTRAL_REFERENCE_UNMODIFIED"
    neutral_collection.objects.link(neutral)

    prototype = source_obj.copy()
    prototype.data = source_obj.data.copy()
    prototype.animation_data_clear()
    prototype.parent = None
    prototype.matrix_world = source_obj.matrix_world.copy()
    prototype.name = "P1_MOUTH_PROTOTYPE_REQUIRES_RETOPOLOGY"
    prototype_collection.objects.link(prototype)

    return source_obj, neutral, prototype


def make_principled_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.78,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.24
    return material


def make_matte_source_material(
    source: bpy.types.Material | None,
) -> bpy.types.Material:
    if source is None:
        return make_principled_material(
            "MAT_P1_MATTE_FALLBACK", (0.36, 0.49, 0.38, 1.0)
        )

    material = source.copy()
    material.name = "MAT_P1_SOURCE_COLOR_MATTE"
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Roughness"].default_value = 0.82
        principled.inputs["Metallic"].default_value = 0.0
        if "Specular IOR Level" in principled.inputs:
            principled.inputs["Specular IOR Level"].default_value = 0.20

        # Keep Tripo's packed base-color image, but disconnect the automatic
        # normal and ORM paths so this diagnostic is not washed out by the
        # generated PBR response.
        for input_name in ("Normal", "Metallic"):
            socket = principled.inputs.get(input_name)
            if socket:
                for link in list(socket.links):
                    material.node_tree.links.remove(link)
        principled.inputs["Metallic"].default_value = 0.0
    return material


def prepare_prototype_mesh(obj: bpy.types.Object) -> dict[str, int]:
    """Weld only coincident glTF seam duplicates on the disposable copy."""

    before_vertices = len(obj.data.vertices)
    before_faces = len(obj.data.polygons)
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return {
        "before_vertices": before_vertices,
        "after_weld_vertices": len(mesh.vertices),
        "before_faces": before_faces,
        "after_weld_faces": len(mesh.polygons),
    }


def create_uv_sphere(
    name: str,
    location: Vector,
    scale: Vector,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    segments: int = 64,
    rings: int = 32,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    link_exclusively(obj, collection)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def carve_mouth(
    prototype: bpy.types.Object,
    mouth_material: bpy.types.Material,
    helper_collection: bpy.types.Collection,
) -> dict[str, int | bool]:
    """Subtract an ellipsoid, yielding a real open concavity in the duplicate."""

    # The cutter is assigned the mouth material. Exact Boolean transfers that
    # slot to its newly generated cavity faces on the target.
    cutter = create_uv_sphere(
        "HELPER_MOUTH_BOOLEAN_CUTTER",
        MOUTH_CENTER,
        Vector(
            (
                MOUTH_RADIUS_DEPTH,
                MOUTH_RADIUS_HORIZONTAL,
                MOUTH_RADIUS_VERTICAL,
            )
        ),
        mouth_material,
        helper_collection,
    )

    if mouth_material.name not in prototype.data.materials:
        prototype.data.materials.append(mouth_material)
    mouth_slot = prototype.data.materials.find(mouth_material.name)

    # Align the cutter's material index with the target's cavity slot.
    while len(cutter.data.materials) <= mouth_slot:
        cutter.data.materials.append(mouth_material)
    for polygon in cutter.data.polygons:
        polygon.material_index = mouth_slot

    before_vertices = len(prototype.data.vertices)
    before_faces = len(prototype.data.polygons)

    bpy.context.view_layer.objects.active = prototype
    prototype.select_set(True)
    modifier = prototype.modifiers.new(
        name="PROTOTYPE_OPEN_MOUTH_BOOLEAN", type="BOOLEAN"
    )
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    if hasattr(modifier, "material_mode"):
        modifier.material_mode = "TRANSFER"
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    prototype.select_set(False)

    cutter.hide_render = True
    cutter.hide_set(True)

    # Boolean material transfer is version-dependent and can tag tiny
    # triangulation fragments on the aperture boundary. Reset the disposable
    # mesh to skin first, then assign only the genuinely recessed portion of
    # the cavity. This keeps diagnostic material from leaking onto the cheeks.
    for polygon in prototype.data.polygons:
        polygon.material_index = 0

    assigned = 0
    for polygon in prototype.data.polygons:
        center = polygon.center
        relative = Vector(
            (
                (center.x - MOUTH_CENTER.x) / MOUTH_RADIUS_DEPTH,
                (center.y - MOUTH_CENTER.y) / MOUTH_RADIUS_HORIZONTAL,
                (center.z - MOUTH_CENTER.z) / MOUTH_RADIUS_VERTICAL,
            )
        )
        near_cutter_surface = 0.78 <= relative.length <= 1.20
        inside_mouth_box = (
            center.x > MOUTH_CENTER.x - MOUTH_RADIUS_DEPTH * 1.12
            and abs(center.y) < MOUTH_RADIUS_HORIZONTAL * 1.14
            and abs(center.z - MOUTH_CENTER.z)
            < MOUTH_RADIUS_VERTICAL * 1.16
        )
        # Restrict the dark material to the rear half of the carved volume.
        # The forward Boolean wall stays skin-colored as a temporary lip
        # interior; production retopology will replace this entire boundary.
        deep_cavity = center.x < MOUTH_CENTER.x - 0.100
        if near_cutter_surface and inside_mouth_box and deep_cavity:
            polygon.material_index = mouth_slot
            assigned += 1

    return {
        "before_vertices": before_vertices,
        "after_vertices": len(prototype.data.vertices),
        "before_faces": before_faces,
        "after_faces": len(prototype.data.polygons),
        "cavity_material_faces": assigned,
        "boolean_changed_mesh": (
            len(prototype.data.vertices) != before_vertices
            or len(prototype.data.polygons) != before_faces
        ),
    }


def front_surface_x(
    bvh: BVHTree, y: float, z: float, fallback: float
) -> float:
    location, _normal, _index, _distance = bvh.ray_cast(
        Vector((1.0, y, z)), Vector((-1.0, 0.0, 0.0)), 2.0
    )
    return location.x if location is not None else fallback


def create_mouth_insert(
    neutral: bpy.types.Object,
    lip_material: bpy.types.Material,
    mouth_material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Create a fitted 3D lip flange and recessed mouth-bag diagnostic.

    The outer ring is sampled against the untouched muzzle, hiding the raw
    Boolean edge. Three smaller rings recede into the head and terminate in a
    cap, so the visible dark region has genuine depth from oblique views.
    """

    bm = bmesh.new()
    bm.from_mesh(neutral.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-6)
    bm.normal_update()
    bvh = BVHTree.FromBMesh(bm)

    segments = 64
    outer_horizontal = MOUTH_RADIUS_HORIZONTAL * 1.10
    outer_vertical = MOUTH_RADIUS_VERTICAL * 1.12
    inner_horizontal = MOUTH_RADIUS_HORIZONTAL * 0.90
    inner_vertical = MOUTH_RADIUS_VERTICAL * 0.88

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    material_indices: list[int] = []

    rings: list[list[tuple[float, float, float]]] = []
    for ring_index, (horizontal, vertical, fixed_x) in enumerate(
        (
            (outer_horizontal, outer_vertical, None),
            (inner_horizontal, inner_vertical, None),
            (inner_horizontal * 0.93, inner_vertical * 0.91, 0.337),
            (inner_horizontal * 0.67, inner_vertical * 0.68, 0.276),
        )
    ):
        ring: list[tuple[float, float, float]] = []
        for segment in range(segments):
            theta = 2.0 * math.pi * segment / segments
            y = MOUTH_CENTER.y + horizontal * math.cos(theta)
            z = MOUTH_CENTER.z + vertical * math.sin(theta)
            if fixed_x is None:
                surface_x = front_surface_x(
                    bvh, y, z, MOUTH_CENTER.x - 0.025
                )
                # The outer ring hugs the face. The inner ring moves a little
                # inward, creating a rounded-looking skin flange without a
                # large tubular "pacifier" silhouette.
                x = surface_x + (0.0010 if ring_index == 0 else -0.0030)
            else:
                x = fixed_x
            ring.append((x, y, z))
        rings.append(ring)
        vertices.extend(ring)

    for ring_index in range(len(rings) - 1):
        for segment in range(segments):
            next_segment = (segment + 1) % segments
            a = ring_index * segments + segment
            b = ring_index * segments + next_segment
            c = (ring_index + 1) * segments + next_segment
            d = (ring_index + 1) * segments + segment
            faces.append((a, b, c, d))
            material_indices.append(0 if ring_index == 0 else 1)

    cap_index = len(vertices)
    vertices.append(
        (
            0.252,
            MOUTH_CENTER.y,
            MOUTH_CENTER.z,
        )
    )
    final_ring_start = (len(rings) - 1) * segments
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append(
            (
                final_ring_start + segment,
                final_ring_start + next_segment,
                cap_index,
            )
        )
        material_indices.append(1)

    mesh = bpy.data.meshes.new("P1_PROTOTYPE_MOUTH_INSERT_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(
        "P1_PROTOTYPE_MOUTH_INSERT_REQUIRES_RETOPOLOGY", mesh
    )
    collection.objects.link(obj)
    obj.data.materials.append(lip_material)
    obj.data.materials.append(mouth_material)
    for polygon, material_index in zip(
        obj.data.polygons, material_indices, strict=True
    ):
        polygon.material_index = material_index
        polygon.use_smooth = True
    bm.free()
    return obj


def create_tongue(
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    # A separate, volumetric tongue. It sits on the cavity floor and is
    # intentionally simple because this pass validates construction, not final
    # oral anatomy or deformation topology.
    tongue = create_uv_sphere(
        "P1_PROTOTYPE_TONGUE_SEPARATE_MESH",
        # Keep the tongue safely behind the aperture. The earlier diagnostic
        # used a wider/frontward ellipsoid and honestly revealed intersections
        # with the low-poly cheek shell at oblique angles.
        Vector((0.304, 0.0, MOUTH_CENTER.z - 0.026)),
        Vector((0.034, 0.036, 0.012)),
        material,
        collection,
        segments=48,
        rings=20,
    )
    tongue.rotation_euler[1] = math.radians(-7.0)
    return tongue


def object_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        for corner in obj.bound_box
    ]
    return (
        Vector(
            (
                min(point.x for point in points),
                min(point.y for point in points),
                min(point.z for point in points),
            )
        ),
        Vector(
            (
                max(point.x for point in points),
                max(point.y for point in points),
                max(point.z for point in points),
            )
        ),
    )


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_camera() -> bpy.types.Object:
    data = bpy.data.cameras.new("PROTOTYPE_ORTHO_CAMERA")
    camera = bpy.data.objects.new("PROTOTYPE_ORTHO_CAMERA", data)
    bpy.context.scene.collection.objects.link(camera)
    data.type = "ORTHO"
    bpy.context.scene.camera = camera
    return camera


def make_area_light(name: str, energy: float, size: float) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_lights() -> dict[str, bpy.types.Object]:
    return {
        "key": make_area_light("PROTOTYPE_KEY", 115.0, 1.7),
        "fill": make_area_light("PROTOTYPE_FILL", 42.0, 2.2),
        "rim": make_area_light("PROTOTYPE_RIM", 70.0, 1.4),
    }


def place_camera_and_lights(
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    target: Vector,
    direction: Vector,
    distance: float,
) -> None:
    view = direction.normalized()
    camera.location = target + view * distance
    point_at(camera, target)

    up = Vector((0.0, 0.0, 1.0))
    right = view.cross(up)
    if right.length < 0.001:
        right = Vector((0.0, 1.0, 0.0))
    right.normalize()

    lights["key"].location = target + view * 1.8 - right * 0.75 + up * 0.9
    lights["fill"].location = target + view * 1.3 + right * 0.9 + up * 0.2
    lights["rim"].location = target - view * 1.2 + right * 0.2 + up * 0.8
    for light in lights.values():
        point_at(light, target)


def configure_scene(resolution: int) -> None:
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
    scene.render.image_settings.color_depth = "8"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        scene.view_settings.look = "Medium High Contrast"
    scene.render.resolution_percentage = 100

    world = bpy.data.worlds.new("PROTOTYPE_NEUTRAL_WORLD")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.115, 0.125, 0.14, 1.0)
    background.inputs["Strength"].default_value = 0.28
    scene.world = world


def set_variant_visibility(
    source: bpy.types.Object,
    neutral: bpy.types.Object,
    prototype: bpy.types.Object,
    lip: bpy.types.Object,
    tongue: bpy.types.Object,
    variant: str,
) -> None:
    source.hide_render = True
    if variant == "neutral":
        neutral.hide_render = False
        prototype.hide_render = True
        lip.hide_render = True
        tongue.hide_render = True
    elif variant == "open":
        neutral.hide_render = True
        prototype.hide_render = False
        lip.hide_render = False
        tongue.hide_render = False
    else:
        raise ValueError(f"Unknown variant: {variant}")


def render(
    path: Path,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    target: Vector,
    direction: Vector,
    ortho_scale: float,
    distance: float = 2.4,
) -> None:
    camera.data.ortho_scale = ortho_scale
    place_camera_and_lights(camera, lights, target, direction, distance)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def count_components(obj: bpy.types.Object) -> int:
    mesh = obj.data
    adjacency: list[set[int]] = [set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)

    visited: set[int] = set()
    components = 0
    for start in range(len(mesh.vertices)):
        if start in visited:
            continue
        components += 1
        stack = [start]
        visited.add(start)
        while stack:
            vertex = stack.pop()
            for neighbor in adjacency[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
    return components


def main() -> None:
    args = parse_args()
    source_path = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    renders = output / "renders"
    open_renders = renders / "open"
    neutral_renders = renders / "neutral"
    open_renders.mkdir(parents=True, exist_ok=True)
    neutral_renders.mkdir(parents=True, exist_ok=True)

    if not source_path.exists():
        raise FileNotFoundError(source_path)
    source_hash_before = sha256(source_path)

    clear_scene()
    configure_scene(args.resolution)
    source, neutral, prototype = import_source_locked(source_path)

    source_material = source.data.materials[0] if source.data.materials else None
    matte_material = make_matte_source_material(source_material)
    mouth_material = make_principled_material(
        "MAT_MOUTH_CAVITY_DARK_WINE", (0.075, 0.018, 0.022, 1.0), 0.88
    )
    tongue_material = make_principled_material(
        "MAT_TONGUE_CORAL", (0.80, 0.205, 0.17, 1.0), 0.72
    )
    lip_material = make_principled_material(
        "MAT_PROTOTYPE_LIP_SAGE", (0.20, 0.33, 0.22, 1.0), 0.82
    )

    for obj in (neutral, prototype):
        obj.data.materials.clear()
        obj.data.materials.append(matte_material)

    weld_metrics = prepare_prototype_mesh(prototype)
    helper_collection = make_collection("90_HIDDEN_CONSTRUCTION_HELPERS")
    helper_collection.hide_render = True
    prototype_collection = bpy.data.collections["20_MOUTH_PROTOTYPE_NOT_PRODUCTION"]
    boolean_metrics = carve_mouth(
        prototype, mouth_material, helper_collection
    )
    lip = create_mouth_insert(
        neutral, lip_material, mouth_material, prototype_collection
    )
    tongue = create_tongue(tongue_material, prototype_collection)

    if not boolean_metrics["boolean_changed_mesh"]:
        raise RuntimeError(
            "Mouth Boolean did not change the duplicate mesh; refusing to "
            "render misleading evidence."
        )
    if int(boolean_metrics["cavity_material_faces"]) < 8:
        raise RuntimeError(
            "Too few cavity faces were identified; refusing to render "
            "misleading evidence."
        )

    camera = make_camera()
    lights = make_lights()
    full_target = Vector((0.0, 0.0, 0.0))
    mouth_target = Vector((0.30, 0.0, -0.005))

    set_variant_visibility(
        source, neutral, prototype, lip, tongue, "neutral"
    )
    render(
        neutral_renders / "front_closed_reference.png",
        camera,
        lights,
        full_target,
        FRONT,
        1.14,
    )

    set_variant_visibility(source, neutral, prototype, lip, tongue, "open")
    render(
        open_renders / "front_open_smile_prototype.png",
        camera,
        lights,
        full_target,
        FRONT,
        1.14,
    )
    render(
        open_renders / "three_quarter_open_smile_prototype.png",
        camera,
        lights,
        full_target,
        THREE_QUARTER,
        1.14,
    )
    render(
        open_renders / "side_open_smile_prototype.png",
        camera,
        lights,
        full_target,
        SIDE,
        1.14,
    )
    render(
        open_renders / "mouth_closeup_geometry_prototype.png",
        camera,
        lights,
        mouth_target,
        THREE_QUARTER,
        0.34,
        distance=1.2,
    )

    source_hash_after = sha256(source_path)
    if source_hash_after != source_hash_before:
        raise RuntimeError("Source GLB hash changed during prototype build.")

    # Restore the open diagnostic as the visible state when the .blend opens.
    set_variant_visibility(source, neutral, prototype, lip, tongue, "open")
    camera.data.ortho_scale = 1.14
    place_camera_and_lights(
        camera, lights, full_target, THREE_QUARTER, distance=2.4
    )

    blend_path = output / "p1_mouth_construction_prototype.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    source_min, source_max = object_bounds([neutral])
    prototype_min, prototype_max = object_bounds([prototype, lip, tongue])
    metrics = {
        "schema_version": "1.0.0",
        "status": "geometry_prototype_not_production_retopology",
        "source": {
            "path": str(source_path),
            "sha256_before": source_hash_before,
            "sha256_after": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
        },
        "construction": {
            "source_locked": True,
            "uses_tripo_generation": False,
            "full_body_rig_created": False,
            "mouth_is_flat_card_or_decal": False,
            "boolean_cavity": boolean_metrics,
            "weld_on_duplicate_only": weld_metrics,
            "tongue": {
                "separate_object": tongue.name,
                "vertices": len(tongue.data.vertices),
                "faces": len(tongue.data.polygons),
            },
            "lip_rim": {
                "separate_object": lip.name,
                "vertices": len(lip.data.vertices),
                "faces": len(lip.data.polygons),
            },
            "prototype_mesh_components": count_components(prototype),
        },
        "bounds": {
            "neutral_reference": {
                "minimum": list(source_min),
                "maximum": list(source_max),
            },
            "mouth_prototype_visible_objects": {
                "minimum": list(prototype_min),
                "maximum": list(prototype_max),
            },
        },
        "limitations": [
            "This validates a real cavity, separate tongue, and toothless open-smile volume.",
            "The Boolean edge and separate lip rim are diagnostic construction, not production topology.",
            "The close-up may expose thin fitting seams where the smooth insert meets P1's irregular triangulated muzzle; those seams are a known retopology blocker, not an approved facial finish.",
            "Production requires a clean retopology pass with concentric lip loops, a connected mouth bag, deformation weights, and expression tests.",
            "No full-body rig or animation was created in this prototype.",
            "The neutral reference is an untouched deep copy of the source mesh with diagnostic matte shading.",
        ],
        "outputs": {
            "blend": str(blend_path),
            "neutral_front": str(
                neutral_renders / "front_closed_reference.png"
            ),
            "open_front": str(
                open_renders / "front_open_smile_prototype.png"
            ),
            "open_three_quarter": str(
                open_renders / "three_quarter_open_smile_prototype.png"
            ),
            "open_side": str(
                open_renders / "side_open_smile_prototype.png"
            ),
            "mouth_closeup": str(
                open_renders / "mouth_closeup_geometry_prototype.png"
            ),
        },
    }
    metrics_path = output / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n")

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
