"""Build a small, disposable Bentosaur facial-animation proof.

This is deliberately a *control and export proof*, not production facial
topology. It keeps the S40 r003 body geometry unchanged and layers a tiny
mobile-budget face module over the muzzle:

* one conforming mouth-aperture patch with named morph targets;
* separate upper/lower lip ribbons;
* separate left/right eye patches with blink and happy-eye morphs;
* a separate tongue;
* root, jaw, and tongue bones;
* deterministic Blender checkpoints, renders, and a GLB round-trip audit.

The output root is supplied explicitly. Historical source files are never
modified, and no paid APIs are used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Callable, Iterable

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


BODY_OBJECT = "BENTOSAUR_BODY_RETOPO_WIP_R003"
OPEN_KEY = "Mouth_DelightedOpen"
CLOSE_KEY = "Mouth_CloseCorrective"
CHEW_KEY = "Chew_Compress"
BLINK_L_KEY = "Blink_L"
BLINK_R_KEY = "Blink_R"
HAPPY_EYES_KEY = "HappyEyes"
TONGUE_RETRACT_KEY = "Tongue_Retract"
TONGUE_CHEW_KEY = "Tongue_Chew"

# Canonical S40 space: +X character-left, -Y front, +Z up.
MOUTH_CENTER_Z = 0.468
MOUTH_HALF_WIDTH = 0.072
JAW_OPEN_DEGREES = 10.0

OPEN_BEZIERS = (
    ((-0.072, 0.502), (-0.052, 0.504), (-0.026, 0.486), (0.000, 0.486)),
    ((0.000, 0.486), (0.026, 0.486), (0.052, 0.504), (0.072, 0.502)),
    ((0.072, 0.502), (0.079, 0.474), (0.046, 0.428), (0.000, 0.428)),
    ((0.000, 0.428), (-0.046, 0.428), (-0.079, 0.474), (-0.072, 0.502)),
)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=640)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_checkpoint(path: Path) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def ensure_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def link_exclusively(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> None:
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def make_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    specular: float = 0.25,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = specular
    return material


def material_set() -> dict[str, bpy.types.Material]:
    return {
        "sage": make_material(
            "MAT_BENTOSAUR_PROOF_SAGE", (0.245, 0.535, 0.385, 1.0), 0.72
        ),
        "lip": make_material(
            "MAT_BENTOSAUR_PROOF_LIP_SAGE",
            (0.185, 0.405, 0.290, 1.0),
            0.68,
        ),
        "ink": make_material(
            "MAT_BENTOSAUR_PROOF_FACE_INK",
            (0.022, 0.010, 0.016, 1.0),
            0.58,
            0.16,
        ),
        "eye": make_material(
            "MAT_BENTOSAUR_PROOF_EYE_BROWN",
            (0.060, 0.018, 0.022, 1.0),
            0.60,
            0.14,
        ),
        "tongue": make_material(
            "MAT_BENTOSAUR_PROOF_TONGUE_CORAL",
            (0.92, 0.26, 0.34, 1.0),
            0.52,
            0.30,
        ),
        "blush": make_material(
            "MAT_BENTOSAUR_PROOF_BLUSH",
            (0.96, 0.39, 0.37, 1.0),
            0.64,
        ),
        "floor": make_material(
            "MAT_BENTOSAUR_PROOF_FLOOR",
            (0.045, 0.060, 0.070, 1.0),
            0.90,
            0.05,
        ),
    }


def clean_to_r003_body() -> bpy.types.Object:
    body = bpy.data.objects.get(BODY_OBJECT)
    if body is None:
        raise RuntimeError(f"Missing required S40 r003 body: {BODY_OBJECT}")
    body.data = body.data.copy()
    for obj in list(bpy.data.objects):
        if obj is not body:
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if collection.users == 0:
            bpy.data.collections.remove(collection)
    body.name = "BENTOSAUR_R003_BODY_FACIAL_PROOF_STATIC"
    body["source_stage"] = "S40 r003"
    body["geometry_modified"] = False
    body["facial_proof_only"] = True
    body["production_approved"] = False
    return body


def purge_orphans() -> None:
    """Drop heavy locked-source datablocks after their objects are removed."""

    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.armatures,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.images,
        bpy.data.textures,
        bpy.data.materials,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def body_bvh(body: bpy.types.Object) -> BVHTree:
    return BVHTree.FromPolygons(
        [vertex.co.copy() for vertex in body.data.vertices],
        [tuple(poly.vertices) for poly in body.data.polygons],
        all_triangles=False,
    )


def surface_y(bvh: BVHTree, x: float, z: float) -> float:
    hit, _normal, _face, _distance = bvh.ray_cast(
        Vector((x, -1.5, z)), Vector((0.0, 1.0, 0.0)), 3.0
    )
    if hit is None:
        return -0.295
    mirrored, _n2, _f2, _d2 = bvh.ray_cast(
        Vector((-x, -1.5, z)), Vector((0.0, 1.0, 0.0)), 3.0
    )
    if mirrored is None:
        return hit.y
    return 0.5 * (hit.y + mirrored.y)


def cubic(
    points: tuple[
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
    ],
    t: float,
) -> tuple[float, float]:
    inverse = 1.0 - t
    weights = (
        inverse**3,
        3.0 * inverse * inverse * t,
        3.0 * inverse * t * t,
        t**3,
    )
    return (
        sum(weight * point[0] for weight, point in zip(weights, points)),
        sum(weight * point[1] for weight, point in zip(weights, points)),
    )


def sample_closed_beziers(
    segments: tuple[
        tuple[
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
        ],
        ...,
    ],
    samples_per_segment: int,
) -> list[tuple[float, float]]:
    result = []
    for segment in segments:
        for index in range(samples_per_segment):
            result.append(cubic(segment, index / samples_per_segment))
    return result


def mouth_boundaries() -> dict[str, list[tuple[float, float]]]:
    opened = sample_closed_beziers(OPEN_BEZIERS, 16)
    closed = []
    closed_corrective = []
    for index, (x, _z) in enumerate(opened):
        upper = index < len(opened) // 2
        x_ratio = min(1.0, abs(x) / MOUTH_HALF_WIDTH)
        center = 0.484 + 0.007 * (x_ratio**1.65)
        corrective_center = 0.482 + 0.011 * (x_ratio**1.55)
        side = 1.0 if upper else -1.0
        closed.append((x * 0.94, center + side * 0.0016))
        closed_corrective.append(
            (x * 0.96, corrective_center + side * 0.00135)
        )
    compressed = [
        (
            x * 0.94,
            MOUTH_CENTER_Z + (z - MOUTH_CENTER_Z) * 0.61 + 0.002,
        )
        for x, z in opened
    ]
    return {
        "Basis": closed,
        OPEN_KEY: opened,
        CLOSE_KEY: closed_corrective,
        CHEW_KEY: compressed,
    }


def radial_vertices(
    boundary: list[tuple[float, float]],
    bvh: BVHTree,
    rings: int,
    front_offset: float,
) -> list[Vector]:
    center_x = sum(x for x, _z in boundary) / len(boundary)
    center_z = sum(z for _x, z in boundary) / len(boundary)
    vertices = [
        Vector(
            (
                center_x,
                surface_y(bvh, center_x, center_z) - front_offset,
                center_z,
            )
        )
    ]
    for ring in range(1, rings + 1):
        fraction = ring / rings
        for x, z in boundary:
            px = center_x + (x - center_x) * fraction
            pz = center_z + (z - center_z) * fraction
            vertices.append(
                Vector((px, surface_y(bvh, px, pz) - front_offset, pz))
            )
    return vertices


def radial_faces(boundary_count: int, rings: int) -> list[tuple[int, ...]]:
    faces: list[tuple[int, ...]] = []
    first_start = 1
    for index in range(boundary_count):
        nxt = (index + 1) % boundary_count
        faces.append((0, first_start + index, first_start + nxt))
    for ring in range(1, rings):
        inner = 1 + (ring - 1) * boundary_count
        outer = 1 + ring * boundary_count
        for index in range(boundary_count):
            nxt = (index + 1) % boundary_count
            faces.append(
                (
                    inner + index,
                    outer + index,
                    outer + nxt,
                    inner + nxt,
                )
            )
    return faces


def create_radial_shape_patch(
    name: str,
    boundaries: dict[str, list[tuple[float, float]]],
    bvh: BVHTree,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    rings: int = 3,
    front_offset: float = 0.006,
) -> bpy.types.Object:
    basis = boundaries["Basis"]
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(
        radial_vertices(basis, bvh, rings, front_offset),
        [],
        radial_faces(len(basis), rings),
    )
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.shape_key_add(name="Basis")
    for key_name, boundary in boundaries.items():
        if key_name == "Basis":
            continue
        key = obj.shape_key_add(name=key_name)
        target = radial_vertices(boundary, bvh, rings, front_offset)
        for point, coordinate in zip(key.data, target, strict=True):
            point.co = coordinate
    obj["facial_proof_only"] = True
    obj["mobile_proxy"] = True
    obj["production_topology"] = False
    return obj


def eye_boundaries(
    center_x: float, center_z: float, blink_name: str
) -> dict[str, list[tuple[float, float]]]:
    count = 32
    radius_x = 0.030
    radius_z = 0.044
    basis = []
    blink = []
    happy = []
    for index in range(count):
        angle = 2.0 * math.pi * index / count
        cosine = math.cos(angle)
        sine = math.sin(angle)
        x = center_x + radius_x * cosine
        basis.append((x, center_z + radius_z * sine))
        blink_curve = center_z - 0.0025 * (1.0 - cosine * cosine)
        blink.append((x, blink_curve + 0.0024 * sine))
        happy_curve = center_z - 0.006 + 0.018 * (
            1.0 - cosine * cosine
        )
        happy.append((x, happy_curve + 0.0027 * sine))
    return {"Basis": basis, blink_name: blink, HAPPY_EYES_KEY: happy}


def line_state(
    t: float, state: str, lower: bool
) -> tuple[float, float]:
    boundaries = mouth_boundaries()
    if state == "Basis":
        x = -0.068 + 0.136 * t
        ratio = min(1.0, abs(x) / 0.068)
        center = 0.484 + 0.007 * (ratio**1.65)
        return x, center + (-0.0022 if lower else 0.0022)
    if state == CLOSE_KEY:
        x = -0.069 + 0.138 * t
        ratio = min(1.0, abs(x) / 0.069)
        center = 0.482 + 0.011 * (ratio**1.55)
        return x, center + (-0.0020 if lower else 0.0020)
    if lower:
        if t <= 0.5:
            base = cubic(
                (
                    OPEN_BEZIERS[3][3],
                    OPEN_BEZIERS[3][2],
                    OPEN_BEZIERS[3][1],
                    OPEN_BEZIERS[3][0],
                ),
                t * 2.0,
            )
        else:
            base = cubic(
                (
                    OPEN_BEZIERS[2][3],
                    OPEN_BEZIERS[2][2],
                    OPEN_BEZIERS[2][1],
                    OPEN_BEZIERS[2][0],
                ),
                (t - 0.5) * 2.0,
            )
    else:
        base = (
            cubic(OPEN_BEZIERS[0], t * 2.0)
            if t <= 0.5
            else cubic(OPEN_BEZIERS[1], (t - 0.5) * 2.0)
        )
    if state == CHEW_KEY:
        return (
            base[0] * 0.94,
            MOUTH_CENTER_Z
            + (base[1] - MOUTH_CENTER_Z) * 0.61
            + 0.002,
        )
    return base


def ribbon_vertices(
    state: str,
    lower: bool,
    bvh: BVHTree,
    samples: int = 25,
) -> list[Vector]:
    points = [line_state(i / (samples - 1), state, lower) for i in range(samples)]
    result = []
    for x, z in points:
        for side in (-1.0, 1.0):
            pz = z + side * 0.0014
            result.append(
                Vector((x, surface_y(bvh, x, pz) - 0.009, pz))
            )
    return result


def ribbon_faces(samples: int) -> list[tuple[int, int, int, int]]:
    return [
        (2 * i, 2 * (i + 1), 2 * (i + 1) + 1, 2 * i + 1)
        for i in range(samples - 1)
    ]


def create_lip_ribbon(
    name: str,
    lower: bool,
    bvh: BVHTree,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    samples = 25
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(
        ribbon_vertices("Basis", lower, bvh, samples),
        [],
        ribbon_faces(samples),
    )
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.shape_key_add(name="Basis")
    for key_name in (OPEN_KEY, CLOSE_KEY, CHEW_KEY):
        key = obj.shape_key_add(name=key_name)
        coordinates = ribbon_vertices(key_name, lower, bvh, samples)
        for point, coordinate in zip(key.data, coordinates, strict=True):
            point.co = coordinate
    obj["facial_proof_only"] = True
    obj["lower_lip_jaw_skinned"] = lower
    return obj


def create_blush(
    name: str,
    center_x: float,
    bvh: BVHTree,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    center_z = 0.525
    boundary = [
        (
            center_x + 0.024 * math.cos(2.0 * math.pi * i / 24),
            center_z + 0.010 * math.sin(2.0 * math.pi * i / 24),
        )
        for i in range(24)
    ]
    return create_radial_shape_patch(
        name,
        {"Basis": boundary},
        bvh,
        material,
        collection,
        rings=2,
        front_offset=0.0065,
    )


def create_tongue(
    bvh: BVHTree,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    tongue_y = surface_y(bvh, 0.0, 0.447) - 0.015
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20,
        ring_count=10,
        location=(0.0, tongue_y, 0.447),
        scale=(0.034, 0.009, 0.011),
    )
    tongue = bpy.context.object
    tongue.name = "FACE_TONGUE_MOBILE_PROXY"
    link_exclusively(tongue, collection)
    # Identity transforms are mandatory before skinning/export. r001 applied
    # only scale, which Blender could round-trip but Godot interpreted with an
    # offset bind matrix, placing the tongue vertically near the nose.
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    tongue.data.materials.append(material)
    for polygon in tongue.data.polygons:
        polygon.use_smooth = True
    tongue.shape_key_add(name="Basis")
    retract = tongue.shape_key_add(name=TONGUE_RETRACT_KEY)
    chew = tongue.shape_key_add(name=TONGUE_CHEW_KEY)
    for basis_point, retract_point, chew_point in zip(
        tongue.data.shape_keys.key_blocks["Basis"].data,
        retract.data,
        chew.data,
        strict=True,
    ):
        retract_point.co = basis_point.co + Vector((0.0, 0.125, 0.018))
        center = Vector((0.0, 0.0, 0.0))
        local = basis_point.co - center
        chew_point.co = Vector((local.x * 0.92, local.y, local.z * 0.55))
    tongue["facial_proof_only"] = True
    tongue["separate_closed_mesh"] = True
    return tongue


def create_armature(
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    armature_data = bpy.data.armatures.new("BENTOSAUR_FACE_RIG_DATA")
    armature = bpy.data.objects.new(
        "BENTOSAUR_FACE_RIG_MOBILE_PROOF", armature_data
    )
    collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    root = armature_data.edit_bones.new("root")
    root.head = (0.0, 0.0, 0.0)
    root.tail = (0.0, 0.0, 0.20)
    root.use_deform = False
    jaw = armature_data.edit_bones.new("jaw")
    jaw.head = (-0.090, -0.300, 0.500)
    jaw.tail = (0.090, -0.300, 0.500)
    jaw.parent = root
    jaw.use_connect = False
    tongue = armature_data.edit_bones.new("tongue")
    tongue.head = (-0.048, -0.315, 0.448)
    tongue.tail = (0.048, -0.315, 0.448)
    tongue.parent = jaw
    tongue.use_connect = False
    bpy.ops.object.mode_set(mode="POSE")
    armature.pose.bones["jaw"].rotation_mode = "XYZ"
    armature.pose.bones["tongue"].rotation_mode = "XYZ"
    bpy.ops.object.mode_set(mode="OBJECT")
    armature.select_set(False)
    armature.show_in_front = True
    armature["facial_proof_only"] = True
    armature["control_contract"] = (
        "jaw and tongue bones plus named small-mesh morph targets"
    )
    armature["jaw_open_degrees"] = JAW_OPEN_DEGREES
    return armature


def bind_single_bone(
    obj: bpy.types.Object, armature: bpy.types.Object, bone_name: str
) -> None:
    group = obj.vertex_groups.new(name=bone_name)
    group.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    modifier = obj.modifiers.new("FACE_ARMATURE", "ARMATURE")
    modifier.object = armature
    obj.parent = armature


def set_shape(obj: bpy.types.Object, name: str, value: float) -> None:
    if obj.data.shape_keys and name in obj.data.shape_keys.key_blocks:
        obj.data.shape_keys.key_blocks[name].value = value


def reset_shapes(objects: Iterable[bpy.types.Object]) -> None:
    for obj in objects:
        if not obj.data.shape_keys:
            continue
        for key in obj.data.shape_keys.key_blocks:
            if key.name != "Basis":
                key.value = 0.0


def set_state(
    state: str,
    mouth: bpy.types.Object,
    upper_lip: bpy.types.Object,
    lower_lip: bpy.types.Object,
    eye_l: bpy.types.Object,
    eye_r: bpy.types.Object,
    tongue: bpy.types.Object,
    armature: bpy.types.Object,
) -> None:
    shaped = (mouth, upper_lip, lower_lip, eye_l, eye_r, tongue)
    reset_shapes(shaped)
    jaw_degrees = 0.0
    tongue_degrees = 0.0
    if state == "neutral":
        for obj in (mouth, upper_lip, lower_lip):
            set_shape(obj, CLOSE_KEY, 1.0)
        set_shape(tongue, TONGUE_RETRACT_KEY, 1.0)
    elif state == "partial":
        for obj in (mouth, upper_lip, lower_lip):
            set_shape(obj, OPEN_KEY, 0.50)
        set_shape(tongue, TONGUE_RETRACT_KEY, 0.48)
        # Keep the interpolation frame purely morph-driven. The full-open
        # and chew frames prove jaw skinning without letting the lower lip
        # outrun the half-open aperture.
        jaw_degrees = 0.0
    elif state == "open":
        for obj in (mouth, upper_lip, lower_lip):
            set_shape(obj, OPEN_KEY, 1.0)
        jaw_degrees = JAW_OPEN_DEGREES
    elif state == "blink":
        for obj in (mouth, upper_lip, lower_lip):
            set_shape(obj, CLOSE_KEY, 1.0)
        set_shape(eye_l, BLINK_L_KEY, 1.0)
        set_shape(eye_r, BLINK_R_KEY, 1.0)
        set_shape(tongue, TONGUE_RETRACT_KEY, 1.0)
    elif state == "happy":
        for obj in (mouth, upper_lip, lower_lip):
            set_shape(obj, OPEN_KEY, 1.0)
        set_shape(eye_l, HAPPY_EYES_KEY, 1.0)
        set_shape(eye_r, HAPPY_EYES_KEY, 1.0)
        jaw_degrees = JAW_OPEN_DEGREES
        tongue_degrees = -3.0
    elif state == "chew":
        for obj in (mouth, upper_lip, lower_lip):
            set_shape(obj, CHEW_KEY, 1.0)
        set_shape(tongue, TONGUE_CHEW_KEY, 1.0)
        jaw_degrees = JAW_OPEN_DEGREES * 0.55
        tongue_degrees = 4.0
    else:
        raise ValueError(state)
    jaw = armature.pose.bones["jaw"]
    tongue_bone = armature.pose.bones["tongue"]
    jaw.rotation_euler = (0.0, math.radians(jaw_degrees), 0.0)
    tongue_bone.rotation_euler = (
        0.0,
        math.radians(tongue_degrees),
        0.0,
    )
    bpy.context.view_layer.update()


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    color: tuple[float, float, float],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    point_at(obj, Vector((0.0, -0.02, 0.53)))
    return obj


def configure_render(
    output: Path,
    resolution: int,
    materials: dict[str, bpy.types.Material],
) -> bpy.types.Object:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.6
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.020, 0.030, 0.038, 1.0)
    background.inputs["Strength"].default_value = 0.30
    render_collection = ensure_collection("80_RENDER")
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0.0, 0.0, -0.006))
    floor = bpy.context.object
    floor.name = "FACIAL_PROOF_FLOOR"
    floor.data.materials.append(materials["floor"])
    link_exclusively(floor, render_collection)
    camera_data = bpy.data.cameras.new("FACIAL_PROOF_CAMERA_DATA")
    camera_data.type = "ORTHO"
    camera = bpy.data.objects.new("FACIAL_PROOF_CAMERA", camera_data)
    render_collection.objects.link(camera)
    scene.camera = camera
    add_area_light(
        "FACIAL_PROOF_KEY_WARM",
        (-1.4, -2.0, 2.0),
        240.0,
        1.8,
        (1.0, 0.78, 0.62),
        render_collection,
    )
    add_area_light(
        "FACIAL_PROOF_FILL_COOL",
        (1.4, -1.1, 1.4),
        130.0,
        1.7,
        (0.56, 0.74, 1.0),
        render_collection,
    )
    add_area_light(
        "FACIAL_PROOF_RIM",
        (0.4, 1.7, 1.9),
        180.0,
        1.3,
        (0.72, 0.96, 1.0),
        render_collection,
    )
    output.mkdir(parents=True, exist_ok=True)
    return camera


def set_camera(
    camera: bpy.types.Object,
    view: str,
    closeup: bool,
) -> None:
    target = Vector((0.0, -0.03, 0.56 if closeup else 0.50))
    distance = 1.45
    if view == "front":
        camera.location = Vector((0.0, -distance, target.z))
    elif view == "three_quarter":
        camera.location = Vector((0.40, -distance, target.z + 0.02))
    else:
        raise ValueError(view)
    camera.data.ortho_scale = 0.60 if closeup else 1.12
    point_at(camera, target)


def render(
    path: Path,
    camera: bpy.types.Object,
    view: str = "front",
    closeup: bool = True,
) -> dict[str, object]:
    set_camera(camera, view, closeup)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def topology(obj: bpy.types.Object) -> dict[str, int]:
    mesh = obj.data
    return {
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
        "triangles_after_export": sum(
            max(1, len(poly.vertices) - 2) for poly in mesh.polygons
        ),
        "shape_keys": (
            len(mesh.shape_keys.key_blocks) - 1 if mesh.shape_keys else 0
        ),
    }


def export_glb(
    path: Path,
    export_objects: Iterable[bpy.types.Object],
) -> dict[str, object]:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in export_objects:
        obj.hide_set(False)
        obj.hide_render = False
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_morph=True,
        export_morph_normal=False,
        export_morph_tangent=False,
        export_skins=True,
        export_extras=True,
        export_apply=False,
    )
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def audit_glb_round_trip(
    glb_path: Path, qa_blend: Path
) -> dict[str, object]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    meshes = {}
    armatures = {}
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            meshes[obj.name] = {
                "vertices": len(obj.data.vertices),
                "shape_keys": (
                    [key.name for key in obj.data.shape_keys.key_blocks]
                    if obj.data.shape_keys
                    else []
                ),
                "armature_modifiers": [
                    modifier.object.name
                    for modifier in obj.modifiers
                    if modifier.type == "ARMATURE" and modifier.object
                ],
            }
        elif obj.type == "ARMATURE":
            armatures[obj.name] = [bone.name for bone in obj.data.bones]
    bpy.ops.wm.save_as_mainfile(filepath=str(qa_blend))
    return {
        "meshes": meshes,
        "armatures": armatures,
        "required_morphs_found": {
            OPEN_KEY: any(
                OPEN_KEY in entry["shape_keys"] for entry in meshes.values()
            ),
            CLOSE_KEY: any(
                CLOSE_KEY in entry["shape_keys"] for entry in meshes.values()
            ),
            CHEW_KEY: any(
                CHEW_KEY in entry["shape_keys"] for entry in meshes.values()
            ),
            BLINK_L_KEY: any(
                BLINK_L_KEY in entry["shape_keys"]
                for entry in meshes.values()
            ),
            BLINK_R_KEY: any(
                BLINK_R_KEY in entry["shape_keys"]
                for entry in meshes.values()
            ),
            HAPPY_EYES_KEY: any(
                HAPPY_EYES_KEY in entry["shape_keys"]
                for entry in meshes.values()
            ),
        },
        "required_bones_found": {
            bone: any(
                bone in bones for bones in armatures.values()
            )
            for bone in ("root", "jaw", "tongue")
        },
        "qa_blend": {
            "path": str(qa_blend),
            "bytes": qa_blend.stat().st_size,
            "sha256": sha256(qa_blend),
        },
    }


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    work = output / "work"
    renders = output / "evidence" / "renders"
    exports = output / "exports"
    qa = output / "qa"
    for directory in (work, renders, exports, qa):
        directory.mkdir(parents=True, exist_ok=True)
    source_path = Path(bpy.data.filepath).resolve()
    source_hash = sha256(source_path)
    bpy.context.preferences.filepaths.save_version = 0
    checkpoints: dict[str, object] = {}
    body = clean_to_r003_body()
    body.data.materials.clear()
    purge_orphans()
    materials = material_set()
    body.data.materials.append(materials["sage"])
    for polygon in body.data.polygons:
        polygon.material_index = 0
        polygon.use_smooth = True
    model_collection = ensure_collection("20_FACIAL_PROOF_MODEL")
    link_exclusively(body, model_collection)
    checkpoints["00_r003_body_snapshot"] = save_checkpoint(
        work / "00_r003_body_snapshot.blend"
    )
    bvh = body_bvh(body)
    mouth = create_radial_shape_patch(
        "FACE_MOUTH_APERTURE_MOBILE_PROXY",
        mouth_boundaries(),
        bvh,
        materials["ink"],
        model_collection,
        rings=3,
        front_offset=0.006,
    )
    upper_lip = create_lip_ribbon(
        "FACE_UPPER_LIP_MOBILE_PROXY",
        False,
        bvh,
        materials["ink"],
        model_collection,
    )
    lower_lip = create_lip_ribbon(
        "FACE_LOWER_LIP_JAW_SKINNED_PROXY",
        True,
        bvh,
        materials["ink"],
        model_collection,
    )
    # The tiny ribbons exist only to validate jaw skinning and GLB round-trip.
    # They are hidden in beauty evidence because they are not final lip art.
    upper_lip.hide_render = True
    lower_lip.hide_render = True
    upper_lip["hidden_from_beauty_evidence"] = True
    lower_lip["hidden_from_beauty_evidence"] = True
    eye_l = create_radial_shape_patch(
        "FACE_EYE_L_MOBILE_PROXY",
        eye_boundaries(0.0954, 0.611, BLINK_L_KEY),
        bvh,
        materials["eye"],
        model_collection,
        rings=3,
        front_offset=0.006,
    )
    eye_r = create_radial_shape_patch(
        "FACE_EYE_R_MOBILE_PROXY",
        eye_boundaries(-0.0954, 0.611, BLINK_R_KEY),
        bvh,
        materials["eye"],
        model_collection,
        rings=3,
        front_offset=0.006,
    )
    blush_l = create_blush(
        "FACE_BLUSH_L_STATIC_PROXY",
        0.151,
        bvh,
        materials["blush"],
        model_collection,
    )
    blush_r = create_blush(
        "FACE_BLUSH_R_STATIC_PROXY",
        -0.151,
        bvh,
        materials["blush"],
        model_collection,
    )
    tongue = create_tongue(bvh, materials["tongue"], model_collection)
    checkpoints["10_face_modules"] = save_checkpoint(
        work / "10_small_face_modules.blend"
    )
    checkpoints["20_named_morph_targets"] = save_checkpoint(
        work / "20_named_morph_targets.blend"
    )
    rig_collection = ensure_collection("30_FACIAL_PROOF_RIG")
    armature = create_armature(rig_collection)
    bind_single_bone(lower_lip, armature, "jaw")
    bind_single_bone(tongue, armature, "tongue")
    checkpoints["30_jaw_tongue_skeleton"] = save_checkpoint(
        work / "30_jaw_tongue_skeleton.blend"
    )
    camera = configure_render(renders, args.resolution, materials)
    checkpoints["40_render_ready"] = save_checkpoint(
        work / "40_render_ready.blend"
    )
    render_report = {}
    for index, state in enumerate(
        ("neutral", "partial", "open", "blink", "happy", "chew"), start=1
    ):
        set_state(
            state,
            mouth,
            upper_lip,
            lower_lip,
            eye_l,
            eye_r,
            tongue,
            armature,
        )
        render_report[state] = render(
            renders / f"{index:02d}_{state}_face.png",
            camera,
            view="front",
            closeup=True,
        )
    set_state(
        "neutral",
        mouth,
        upper_lip,
        lower_lip,
        eye_l,
        eye_r,
        tongue,
        armature,
    )
    render_report["neutral_full"] = render(
        renders / "07_neutral_three_quarter_full.png",
        camera,
        view="three_quarter",
        closeup=False,
    )
    set_state(
        "happy",
        mouth,
        upper_lip,
        lower_lip,
        eye_l,
        eye_r,
        tongue,
        armature,
    )
    render_report["happy_full"] = render(
        renders / "08_happy_three_quarter_full.png",
        camera,
        view="three_quarter",
        closeup=False,
    )
    set_state(
        "neutral",
        mouth,
        upper_lip,
        lower_lip,
        eye_l,
        eye_r,
        tongue,
        armature,
    )
    export_objects = (
        body,
        mouth,
        upper_lip,
        lower_lip,
        eye_l,
        eye_r,
        blush_l,
        blush_r,
        tongue,
        armature,
    )
    glb_report = export_glb(
        exports / "bentosaur_facial_mobile_proof_v002.glb",
        export_objects,
    )
    upper_lip.hide_render = True
    lower_lip.hide_render = True
    checkpoints["50_export_ready"] = save_checkpoint(
        work / "50_export_ready_neutral.blend"
    )
    source_unchanged = sha256(source_path) == source_hash
    topology_report = {
        obj.name: topology(obj)
        for obj in export_objects
        if obj.type == "MESH"
    }
    triangle_total = sum(
        entry["triangles_after_export"] for entry in topology_report.values()
    )
    round_trip = audit_glb_round_trip(
        Path(glb_report["path"]),
        qa / "60_glb_roundtrip_import.blend",
    )
    report = {
        "schema_version": "1.0.0",
        "status": "disposable_mobile_facial_control_proof",
        "production_approved": False,
        "paid_api_usage": {
            "used": False,
            "credits_spent": 0,
        },
        "source": {
            "path": str(source_path),
            "sha256": source_hash,
            "unchanged_after_run": source_unchanged,
            "body_object": BODY_OBJECT,
            "body_geometry_modified": False,
        },
        "contract": {
            "axes": {
                "front": "-Y",
                "character_left": "+X",
                "up": "+Z",
            },
            "morph_targets": [
                OPEN_KEY,
                CLOSE_KEY,
                CHEW_KEY,
                BLINK_L_KEY,
                BLINK_R_KEY,
                HAPPY_EYES_KEY,
                TONGUE_RETRACT_KEY,
                TONGUE_CHEW_KEY,
            ],
            "bones": ["root", "jaw", "tongue"],
            "jaw_open_degrees": JAW_OPEN_DEGREES,
            "states_rendered": [
                "neutral",
                "partial",
                "open",
                "blink",
                "happy",
                "chew",
            ],
        },
        "mobile_budget": {
            "mesh_count": len(topology_report),
            "triangles_total_estimate": triangle_total,
            "topology": topology_report,
            "note": (
                "Morph targets live only on tiny face parts; the full body "
                "is not duplicated per expression."
            ),
        },
        "checkpoints": checkpoints,
        "renders": render_report,
        "glb": glb_report,
        "round_trip": round_trip,
        "limitations": [
            "This is a layered visual/control proxy, not welded production facial topology.",
            "The mouth is a conforming dark aperture patch over the unchanged r003 muzzle, not a cut mouth bag.",
            "The tongue and a beauty-hidden lower-lip helper prove bone skinning, but final lip art, deformation weights, and jaw volume require authored production retopology.",
            "The eye patches prove independent blink and happy-eye states; final art may use an atlas swap or refined curved patches.",
            "No UV unwrap, final textures, LODs, collision, or production animation clips are claimed.",
        ],
    }
    report_path = qa / "facial_mobile_proof_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
