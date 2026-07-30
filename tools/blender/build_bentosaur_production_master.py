"""Build a non-destructive Bentosaur production-master lookdev stage.

This script does not rig, skin, or animate the character. It prepares the
static character-appearance approval package that must precede rigging:

* imports an HD GLB into a locked, hidden source collection;
* creates a disposable, deterministic lookdev topology proxy;
* replaces baked facial features with separate eye and cheek objects;
* registers semantic sage, cream, coral, and ink materials;
* builds a genuinely recessed mouth bag, tongue, and concentric lip loops;
* drives neutral-closed and delighted-open states on the same master;
* renders state comparisons and critical closeups;
* emits provenance, topology, construction, and approval-gate metadata.

The automatic ``voxel_proxy`` is deliberately labelled lookdev-only. It is
not joint-loop retopology and must not be sent to rigging. The facial module is
clean, parameterized geometry that can be transferred to the manually
retopologized production surface.

Run:

    /Applications/Blender.app/Contents/MacOS/Blender \
      --background --factory-startup \
      --python tools/blender/build_bentosaur_production_master.py -- \
      --input /absolute/path/model.glb \
      --output /absolute/path/production-master-stage \
      --candidate-id bentosaur_vg03_h31_detailed_neutral
"""

from __future__ import annotations

import argparse
import bmesh
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Iterable

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROFILE = (
    SCRIPT_DIR / "config" / "bentosaur_production_master_v1.json"
)
BOARD_FONT = "/System/Library/Fonts/Helvetica.ttc"
SHAPE_KEY_NAME = "EXPR_DelightedOpen"

VIEW_DIRECTIONS = {
    # Tripo H3.1 multiview GLBs are expected to face Blender +X.
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
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument(
        "--rebuild-mode",
        choices=("source_copy", "voxel_proxy"),
        default=None,
        help="Override profile rebuild.default_mode.",
    )
    parser.add_argument("--resolution", type=int, default=768)
    parser.add_argument("--pixel-resolution", type=int, default=64)
    parser.add_argument(
        "--render-scope",
        choices=("full", "mouth"),
        default="full",
        help="Render the full approval package or a focused mouth diagnostic.",
    )
    parser.add_argument(
        "--hide-lip-repair",
        action="store_true",
        help=(
            "Keep the repair-ring topology in the blend but hide it from "
            "renders when Boolean intersection creates a visible fringe."
        ),
    )
    parser.add_argument(
        "--landmarks-confirmed",
        action="store_true",
        help=(
            "Assert that a human fitted the profile landmarks to this exact "
            "candidate. This does not grant visual approval."
        ),
    )
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_profile(path: Path) -> dict[str, object]:
    profile = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "profile_id",
        "coordinate_contract",
        "rebuild",
        "palette",
        "landmarks_normalized_to_source_bounds",
        "eyes",
        "cheeks",
        "mouth",
        "render",
        "approval",
    }
    missing = required - set(profile)
    if missing:
        raise ValueError(
            f"Profile {path} is missing required fields: {sorted(missing)}"
        )
    if profile["coordinate_contract"]["front_axis"] != "+X":
        raise ValueError("Only the audited +X front-axis contract is supported.")
    if profile["coordinate_contract"]["up_axis"] != "+Z":
        raise ValueError("Only the audited +Z up-axis contract is supported.")
    return profile


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def make_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def link_exclusively(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> None:
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def import_source_locked(
    source: Path,
) -> tuple[list[bpy.types.Object], bpy.types.Collection]:
    source_collection = make_collection("00_SOURCE_LOCKED_DO_NOT_EDIT")
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = [
        obj for obj in bpy.context.scene.objects if obj not in before
    ]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("The source GLB contains no mesh objects.")

    for obj in imported:
        link_exclusively(obj, source_collection)
        obj["bentosaur_source_locked"] = True
        obj.hide_render = True
        obj.hide_select = True
        obj.hide_set(True)
    source_collection["bentosaur_source_locked"] = True
    return meshes, source_collection


def duplicate_joined_surface(
    source_meshes: list[bpy.types.Object],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    copies: list[bpy.types.Object] = []
    for source in source_meshes:
        duplicate = source.copy()
        duplicate.data = source.data.copy()
        duplicate.animation_data_clear()
        duplicate.parent = None
        duplicate.matrix_world = source.matrix_world.copy()
        duplicate.name = f"PROXY_SOURCE_COPY__{source.name}"
        if "bentosaur_source_locked" in duplicate:
            del duplicate["bentosaur_source_locked"]
        collection.objects.link(duplicate)
        duplicate.hide_render = False
        duplicate.hide_set(False)
        duplicate.hide_select = False
        copies.append(duplicate)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in copies:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    if len(copies) > 1:
        bpy.ops.object.join()
    proxy = bpy.context.view_layer.objects.active
    proxy.name = "BENTOSAUR_LOOKDEV_SURFACE_PROXY_NOT_FINAL_RETOPOLOGY"
    bpy.ops.object.transform_apply(
        location=False, rotation=True, scale=True
    )
    proxy["production_topology_status"] = (
        "lookdev_proxy_not_deformation_ready"
    )
    proxy["source_preserved"] = True
    return proxy


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


def weld_mesh(obj: bpy.types.Object, distance: float) -> dict[str, int]:
    mesh = obj.data
    before = len(mesh.vertices)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=distance)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return {
        "vertices_before": before,
        "vertices_after": len(mesh.vertices),
    }


def evaluated_triangle_count(obj: bpy.types.Object) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def build_surface_proxy(
    obj: bpy.types.Object,
    mode: str,
    profile: dict[str, object],
    height: float,
) -> dict[str, object]:
    rebuild = profile["rebuild"]
    metrics: dict[str, object] = {
        "mode": mode,
        "input_vertices": len(obj.data.vertices),
        "input_faces": len(obj.data.polygons),
        "input_triangles": evaluated_triangle_count(obj),
    }
    weld_distance = (
        height * rebuild["weld_distance_fraction_of_height"]
    )
    metrics["weld"] = weld_mesh(obj, weld_distance)

    if mode == "voxel_proxy":
        divisions = rebuild["voxel_divisions_per_character_height"]
        voxel_size = height / divisions
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        modifier = obj.modifiers.new(
            "LOOKDEV_VOXEL_PROXY_REBUILD", type="REMESH"
        )
        modifier.mode = "VOXEL"
        modifier.voxel_size = voxel_size
        modifier.use_smooth_shade = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
        metrics["voxel_size"] = voxel_size
        metrics["voxel_divisions_per_height"] = divisions

        iterations = int(rebuild["smooth_iterations"])
        factor = float(rebuild["smooth_factor"])
        if iterations > 0:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            for _ in range(iterations):
                bmesh.ops.smooth_vert(
                    bm,
                    verts=list(bm.verts),
                    factor=factor,
                    use_axis_x=True,
                    use_axis_y=True,
                    use_axis_z=True,
                )
            bm.to_mesh(obj.data)
            bm.free()
            obj.data.update()

        current_triangles = evaluated_triangle_count(obj)
        target = int(rebuild["decimate_target_triangles"])
        if current_triangles > target:
            ratio = max(0.02, min(1.0, target / current_triangles))
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            decimate = obj.modifiers.new(
                "LOOKDEV_TRIANGLE_BUDGET", type="DECIMATE"
            )
            decimate.decimate_type = "COLLAPSE"
            decimate.ratio = ratio
            decimate.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=decimate.name)
            obj.select_set(False)
            metrics["decimate_ratio"] = ratio

    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    metrics.update(
        {
            "output_vertices": len(obj.data.vertices),
            "output_faces": len(obj.data.polygons),
            "output_triangles": evaluated_triangle_count(obj),
            "deformation_ready": False,
            "manual_joint_loop_retopology_required": True,
        }
    )
    return metrics


def hex_to_rgba_linear(hex_value: str) -> tuple[float, float, float, float]:
    value = hex_value.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB, received {hex_value}")

    def convert(channel: int) -> float:
        srgb = channel / 255.0
        if srgb <= 0.04045:
            return srgb / 12.92
        return ((srgb + 0.055) / 1.055) ** 2.4

    return (
        convert(int(value[0:2], 16)),
        convert(int(value[2:4], 16)),
        convert(int(value[4:6], 16)),
        1.0,
    )


def make_flat_material(
    name: str,
    hex_value: str,
    profile: dict[str, object],
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    rgba = hex_to_rgba_linear(hex_value)
    material.diffuse_color = rgba
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = rgba
    principled.inputs["Metallic"].default_value = float(
        profile["materials"]["metallic"]
    )
    principled.inputs["Roughness"].default_value = float(
        profile["materials"]["roughness"]
    )
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = float(
            profile["materials"]["specular_ior_level"]
        )
    material["semantic_hex_srgb"] = hex_value.upper()
    material["semantic_role"] = name
    return material


def create_semantic_materials(
    profile: dict[str, object],
) -> dict[str, bpy.types.Material]:
    palette = profile["palette"]
    return {
        "body_sage": make_flat_material(
            "MAT_BENTOSAUR_BODY_SAGE",
            palette["body_sage"],
            profile,
        ),
        "feature_cream": make_flat_material(
            "MAT_BENTOSAUR_FEATURE_CREAM",
            palette["feature_cream"],
            profile,
        ),
        "accent_coral": make_flat_material(
            "MAT_BENTOSAUR_ACCENT_CORAL",
            palette["accent_coral"],
            profile,
        ),
        "face_ink": make_flat_material(
            "MAT_BENTOSAUR_FACE_INK",
            palette["face_ink"],
            profile,
        ),
    }


def assign_surface_material_slots(
    obj: bpy.types.Object,
    materials: dict[str, bpy.types.Material],
) -> None:
    obj.data.materials.clear()
    for role in (
        "body_sage",
        "feature_cream",
        "accent_coral",
        "face_ink",
    ):
        obj.data.materials.append(materials[role])
    for polygon in obj.data.polygons:
        polygon.material_index = 0


def create_head_interior_clip_volume(
    surface: bpy.types.Object,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Duplicate the uncut proxy for containment-only Boolean operations."""

    clip = surface.copy()
    clip.data = surface.data.copy()
    clip.animation_data_clear()
    clip.parent = None
    clip.matrix_world = surface.matrix_world.copy()
    clip.name = "HEAD_INTERIOR_CLIP_VOLUME_UNCUT_NOT_RENDERED"
    clip.modifiers.clear()
    collection.objects.link(clip)
    clip.display_type = "WIRE"
    clip.hide_render = True
    clip.hide_select = True
    clip["helper_only"] = True
    clip["purpose"] = "contain_mouth_and_tongue_inside_head_silhouette"
    return clip


def normalized_landmark(
    normalized: list[float], minimum: Vector, maximum: Vector
) -> Vector:
    dimensions = maximum - minimum
    return minimum + Vector(
        (
            dimensions.x * normalized[0],
            dimensions.y * normalized[1],
            dimensions.z * normalized[2],
        )
    )


def build_surface_bvh(obj: bpy.types.Object) -> BVHTree:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    return bvh


def front_surface_point(
    bvh: BVHTree,
    guess: Vector,
    maximum_x: float,
    height: float,
) -> tuple[Vector, Vector, bool]:
    origin = Vector((maximum_x + height, guess.y, guess.z))
    location, normal, _index, _distance = bvh.ray_cast(
        origin, Vector((-1.0, 0.0, 0.0)), height * 3.0
    )
    if location is None or normal is None:
        return Vector((guess.x, guess.y, guess.z)), Vector((1, 0, 0)), False
    if normal.x < 0.0:
        normal = -normal
    return location, normal.normalized(), True


def create_uv_ellipsoid(
    name: str,
    center: Vector,
    radii: Vector,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    segments: int,
    rings: int,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        location=center,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = radii
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True
    )
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    link_exclusively(obj, collection)
    return obj


def create_face_components(
    profile: dict[str, object],
    minimum: Vector,
    maximum: Vector,
    bvh: BVHTree,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> tuple[list[bpy.types.Object], dict[str, object]]:
    height = maximum.z - minimum.z
    landmark_data = profile["landmarks_normalized_to_source_bounds"]
    objects: list[bpy.types.Object] = []
    ray_hits: dict[str, bool] = {}

    eye_cfg = profile["eyes"]
    for side in ("left", "right"):
        key = f"eye_{side}_center"
        guess = normalized_landmark(
            landmark_data[key], minimum, maximum
        )
        surface, normal, hit = front_surface_point(
            bvh, guess, maximum.x, height
        )
        ray_hits[key] = hit
        center = surface + normal * (
            height * eye_cfg["surface_offset_fraction_of_height"]
        )
        eye = create_uv_ellipsoid(
            f"FACE_EYE_{side.upper()}_SEPARATE",
            center,
            Vector(
                (
                    height * eye_cfg["half_depth_fraction_of_height"],
                    height * eye_cfg["half_width_fraction_of_height"],
                    height * eye_cfg["half_height_fraction_of_height"],
                )
            ),
            materials["face_ink"],
            collection,
            int(eye_cfg["segments"]),
            int(eye_cfg["rings"]),
        )
        eye["bentosaur_face_role"] = "replaceable_eye"
        eye["catchlight_geometry"] = False
        objects.append(eye)

    cheek_cfg = profile["cheeks"]
    for side in ("left", "right"):
        key = f"cheek_{side}_center"
        guess = normalized_landmark(
            landmark_data[key], minimum, maximum
        )
        surface, normal, hit = front_surface_point(
            bvh, guess, maximum.x, height
        )
        ray_hits[key] = hit
        center = surface + normal * (
            height * cheek_cfg["surface_offset_fraction_of_height"]
        )
        cheek = create_uv_ellipsoid(
            f"FACE_CHEEK_{side.upper()}_SEPARATE",
            center,
            Vector(
                (
                    height * cheek_cfg["half_depth_fraction_of_height"],
                    height * cheek_cfg["half_width_fraction_of_height"],
                    height * cheek_cfg["half_height_fraction_of_height"],
                )
            ),
            materials["accent_coral"],
            collection,
            int(cheek_cfg["segments"]),
            int(cheek_cfg["rings"]),
        )
        cheek["bentosaur_face_role"] = "replaceable_cheek"
        objects.append(cheek)

    return objects, {
        "surface_ray_hits": ray_hits,
        "eyes_separate_objects": True,
        "eye_catchlights": False,
        "cheeks_separate_objects": True,
    }


def create_surface_overlay_from_polygon_mask(
    surface: bpy.types.Object,
    name: str,
    predicate,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    offset: float,
    semantic_regions: list[str],
) -> bpy.types.Object | None:
    """Extract a fitted visual-material overlay from accepted source faces.

    These overlays are deliberately non-destructive. They follow the accepted
    H3.1 surface exactly and sit a hair above it for the static lookdev gate.
    They are not a substitute for the final retopologist assigning semantic
    material zones on the deformation-ready production mesh.
    """

    mesh = surface.data
    mesh.update()
    dimensions = Vector(
        (
            max(vertex.co.x for vertex in mesh.vertices)
            - min(vertex.co.x for vertex in mesh.vertices),
            max(vertex.co.y for vertex in mesh.vertices)
            - min(vertex.co.y for vertex in mesh.vertices),
            max(vertex.co.z for vertex in mesh.vertices)
            - min(vertex.co.z for vertex in mesh.vertices),
        )
    )
    local_minimum = Vector(
        (
            min(vertex.co.x for vertex in mesh.vertices),
            min(vertex.co.y for vertex in mesh.vertices),
            min(vertex.co.z for vertex in mesh.vertices),
        )
    )

    selected_polygons: list[bpy.types.MeshPolygon] = []
    for polygon in mesh.polygons:
        normalized_center = Vector(
            (
                (polygon.center.x - local_minimum.x) / dimensions.x,
                (polygon.center.y - local_minimum.y) / dimensions.y,
                (polygon.center.z - local_minimum.z) / dimensions.z,
            )
        )
        if predicate(normalized_center, polygon.normal):
            selected_polygons.append(polygon)

    if not selected_polygons:
        return None

    source_indices = sorted(
        {
            vertex_index
            for polygon in selected_polygons
            for vertex_index in polygon.vertices
        }
    )
    remap = {
        source_index: overlay_index
        for overlay_index, source_index in enumerate(source_indices)
    }
    vertices = [
        tuple(
            mesh.vertices[source_index].co
            + mesh.vertices[source_index].normal * offset
        )
        for source_index in source_indices
    ]
    faces = [
        tuple(remap[index] for index in polygon.vertices)
        for polygon in selected_polygons
    ]
    overlay_mesh = bpy.data.meshes.new(f"{name}_MESH")
    overlay_mesh.from_pydata(vertices, [], faces)
    overlay_mesh.update()
    overlay = bpy.data.objects.new(name, overlay_mesh)
    collection.objects.link(overlay)
    overlay.matrix_world = surface.matrix_world.copy()
    overlay.data.materials.append(material)
    for polygon in overlay.data.polygons:
        polygon.use_smooth = True
    overlay["bentosaur_semantic_role"] = "feature_cream_fitted_overlay"
    overlay["anatomical_regions"] = semantic_regions
    overlay["lookdev_only"] = True
    overlay["final_retopology"] = False
    overlay["source_surface_object"] = surface.name
    overlay["surface_offset"] = offset
    overlay["selected_source_polygon_count"] = len(selected_polygons)
    return overlay


def ellipsoid_mask(
    point: Vector,
    center: tuple[float, float, float],
    radii: tuple[float, float, float],
) -> bool:
    return sum(
        ((point[index] - center[index]) / radii[index]) ** 2
        for index in range(3)
    ) <= 1.0


def create_fitted_cone(
    name: str,
    center: Vector,
    direction: Vector,
    radius: float,
    depth: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(
        vertices=48,
        radius1=radius,
        radius2=radius * 0.08,
        depth=depth,
        location=center,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(
        direction.normalized()
    )
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True
    )
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    link_exclusively(obj, collection)
    obj["bentosaur_semantic_role"] = "feature_cream_fitted_primitive"
    obj["lookdev_only"] = True
    obj["final_retopology"] = False
    return obj


def create_semantic_feature_overlays(
    surface: bpy.types.Object,
    height: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> tuple[list[bpy.types.Object], dict[str, object]]:
    """Create fitted cream lookdev zones without altering the source proxy."""

    offset = height * 0.0012

    def any_region(
        point: Vector,
        regions: list[
            tuple[
                tuple[float, float, float],
                tuple[float, float, float],
            ]
        ],
    ) -> bool:
        return any(
            ellipsoid_mask(point, center, radii)
            for center, radii in regions
        )

    # The accepted H3.1 candidate faces +X. Requiring front-facing normals on
    # the belly keeps the cream patch on the torso instead of spilling onto
    # the arms or side silhouette.
    belly_regions = [
        ((0.79, 0.50, 0.29), (0.12, 0.20, 0.20)),
    ]
    definitions = [
        (
            "SEMANTIC_CREAM_BELLY_FITTED_OVERLAY",
            lambda point, normal: (
                any_region(point, belly_regions)
                and normal.x > 0.28
                and 0.28 < point.y < 0.72
            ),
            ["belly"],
        ),
    ]

    objects: list[bpy.types.Object] = []
    for name, predicate, regions in definitions:
        overlay = create_surface_overlay_from_polygon_mask(
            surface,
            name,
            predicate,
            material,
            collection,
            offset,
            regions,
        )
        if overlay is not None:
            objects.append(overlay)

    # Discrete anatomy is represented with individually fitted, slightly
    # oversized primitives. This is cleaner than a broad source-polygon mask:
    # the latter contaminates the frill membrane and palms. These objects are
    # static art-direction proxies that will be rebuilt/integrated by the
    # retopologist after the user approves the silhouette and material rhythm.
    dimensions = Vector(
        (
            max(vertex.co.x for vertex in surface.data.vertices)
            - min(vertex.co.x for vertex in surface.data.vertices),
            max(vertex.co.y for vertex in surface.data.vertices)
            - min(vertex.co.y for vertex in surface.data.vertices),
            max(vertex.co.z for vertex in surface.data.vertices)
            - min(vertex.co.z for vertex in surface.data.vertices),
        )
    )
    minimum = Vector(
        (
            min(vertex.co.x for vertex in surface.data.vertices),
            min(vertex.co.y for vertex in surface.data.vertices),
            min(vertex.co.z for vertex in surface.data.vertices),
        )
    )
    maximum = minimum + dimensions

    horn_specs = [
        (
            "SEMANTIC_CREAM_HORN_NOSE_FITTED",
            (0.955, 0.500, 0.595),
            Vector((0.99, 0.00, 0.14)),
            0.052,
            0.145,
        ),
        (
            "SEMANTIC_CREAM_HORN_BROW_LEFT_FITTED",
            (0.895, 0.315, 0.785),
            Vector((0.34, -0.10, 0.94)),
            0.052,
            0.165,
        ),
        (
            "SEMANTIC_CREAM_HORN_BROW_RIGHT_FITTED",
            (0.895, 0.685, 0.785),
            Vector((0.34, 0.10, 0.94)),
            0.052,
            0.165,
        ),
    ]
    for name, normalized_center, direction, radius, depth in horn_specs:
        horn = create_fitted_cone(
            name,
            normalized_landmark(
                list(normalized_center), minimum, maximum
            ),
            direction,
            height * radius,
            height * depth,
            material,
            collection,
        )
        horn["anatomical_regions"] = ["primary_horns"]
        objects.append(horn)

    frill_specs = [
        (0.50, 0.965),
        (0.31, 0.945),
        (0.69, 0.945),
        (0.18, 0.885),
        (0.82, 0.885),
        (0.09, 0.795),
        (0.91, 0.795),
        (0.055, 0.680),
        (0.945, 0.680),
    ]
    for index, (normalized_y, normalized_z) in enumerate(
        frill_specs, start=1
    ):
        knob = create_uv_ellipsoid(
            f"SEMANTIC_CREAM_FRILL_KNOB_{index:02d}_FITTED",
            normalized_landmark(
                [0.515, normalized_y, normalized_z], minimum, maximum
            ),
            Vector((height * 0.044, height * 0.044, height * 0.046)),
            material,
            collection,
            32,
            20,
        )
        knob["bentosaur_semantic_role"] = (
            "feature_cream_fitted_primitive"
        )
        knob["anatomical_regions"] = ["frill_knobs"]
        knob["lookdev_only"] = True
        knob["final_retopology"] = False
        objects.append(knob)

    dorsal_specs = [
        (0.53, 0.395, 0.030, 0.026),
        (0.43, 0.325, 0.034, 0.024),
        (0.33, 0.260, 0.037, 0.022),
        (0.23, 0.205, 0.039, 0.020),
        (0.14, 0.165, 0.040, 0.018),
    ]
    for index, (normalized_x, normalized_z, radius_y, radius_z) in (
        enumerate(dorsal_specs, start=1)
    ):
        knob = create_uv_ellipsoid(
            f"SEMANTIC_CREAM_DORSAL_KNOB_{index:02d}_FITTED",
            normalized_landmark(
                [normalized_x, 0.50, normalized_z],
                minimum,
                maximum,
            ),
            Vector(
                (
                    height * 0.025,
                    height * radius_y,
                    height * radius_z,
                )
            ),
            material,
            collection,
            28,
            18,
        )
        knob["bentosaur_semantic_role"] = (
            "feature_cream_fitted_primitive"
        )
        knob["anatomical_regions"] = ["dorsal_knobs"]
        knob["lookdev_only"] = True
        knob["final_retopology"] = False
        objects.append(knob)

    hand_claw_specs = [
        (0.925, 0.095, 0.265),
        (0.935, 0.140, 0.255),
        (0.925, 0.185, 0.265),
        (0.925, 0.815, 0.265),
        (0.935, 0.860, 0.255),
        (0.925, 0.905, 0.265),
    ]
    toe_specs = [
        (0.865, 0.285, 0.055),
        (0.885, 0.345, 0.050),
        (0.865, 0.405, 0.055),
        (0.865, 0.595, 0.055),
        (0.885, 0.655, 0.050),
        (0.865, 0.715, 0.055),
    ]
    for anatomical_role, specs, radii in (
        ("hand_claws", hand_claw_specs, (0.023, 0.018, 0.017)),
        ("foot_claws", toe_specs, (0.035, 0.027, 0.020)),
    ):
        for index, normalized_center in enumerate(specs, start=1):
            claw = create_uv_ellipsoid(
                (
                    f"SEMANTIC_CREAM_{anatomical_role.upper()}_"
                    f"{index:02d}_FITTED"
                ),
                normalized_landmark(
                    list(normalized_center), minimum, maximum
                ),
                Vector(
                    (
                        height * radii[0],
                        height * radii[1],
                        height * radii[2],
                    )
                ),
                material,
                collection,
                24,
                14,
            )
            claw["bentosaur_semantic_role"] = (
                "feature_cream_fitted_primitive"
            )
            claw["anatomical_regions"] = [anatomical_role]
            claw["lookdev_only"] = True
            claw["final_retopology"] = False
            objects.append(claw)

    return objects, {
        "implementation": (
            "source_surface_fitted_belly_overlay_plus_individually_fitted_"
            "discrete_primitives"
        ),
        "lookdev_only": True,
        "final_retopology": False,
        "surface_offset_fraction_of_height": 0.0012,
        "requested_regions": [
            "belly",
            "nose_horn",
            "brow_horns",
            "frill_knobs",
            "hand_claws",
            "foot_claws",
            "dorsal_knobs",
        ],
        "created_objects": [obj.name for obj in objects],
        "source_polygon_counts": {
            obj.name: obj["selected_source_polygon_count"]
            for obj in objects
            if "selected_source_polygon_count" in obj
        },
    }


def create_muzzle_repair_patch(
    profile: dict[str, object],
    center: Vector,
    bvh: BVHTree,
    maximum_x: float,
    height: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Cover the generated angular seam before cutting the authored aperture.

    The H3.1 source has useful head volume but an angular neutral mouth seam.
    A thin, smooth body-colour muzzle patch hides that source artifact. The
    same non-destructive cutter used on the surface also cuts this patch, so
    it does not cover the authored neutral or open mouth states.
    """

    cfg = profile["mouth"]
    half_width = (
        height * cfg["muzzle_patch_half_width_fraction_of_height"]
    )
    half_height = (
        height * cfg["muzzle_patch_half_height_fraction_of_height"]
    )
    radial_rings = 6
    segments = 64
    vertices: list[Vector] = []
    center_surface, _normal, _hit = front_surface_point(
        bvh, center, maximum_x, height
    )
    vertices.append(
        center_surface + Vector((height * 0.0032, 0.0, 0.0))
    )
    for ring in range(1, radial_rings + 1):
        radius = ring / radial_rings
        # The center floats just over the generated seam; the boundary tapers
        # almost flush so the repair patch does not read as a separate muzzle
        # pill or moustache.
        offset = height * (
            0.00045 + 0.00275 * ((1.0 - radius) ** 2)
        )
        for segment in range(segments):
            theta = 2.0 * math.pi * segment / segments
            guess = Vector(
                (
                    center.x,
                    center.y
                    + half_width * radius * math.cos(theta),
                    center.z
                    + half_height * radius * math.sin(theta),
                )
            )
            surface, _normal, _hit = front_surface_point(
                bvh, guess, maximum_x, height
            )
            vertices.append(surface + Vector((offset, 0.0, 0.0)))

    faces: list[tuple[int, ...]] = []
    first_ring_start = 1
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append(
            (
                0,
                first_ring_start + segment,
                first_ring_start + next_segment,
            )
        )
    for ring in range(radial_rings - 1):
        current = 1 + ring * segments
        next_ring = current + segments
        for segment in range(segments):
            next_segment = (segment + 1) % segments
            faces.append(
                (
                    current + segment,
                    next_ring + segment,
                    next_ring + next_segment,
                    current + next_segment,
                )
            )

    mesh = bpy.data.meshes.new("BENTOSAUR_CONFORMAL_MUZZLE_PATCH_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    patch = bpy.data.objects.new(
        "FACE_MUZZLE_REPAIR_PATCH_SAME_MASTER", mesh
    )
    collection.objects.link(patch)
    patch.data.materials.append(materials["body_sage"])
    for polygon in patch.data.polygons:
        polygon.use_smooth = True
    solidify = patch.modifiers.new(
        "MUZZLE_PATCH_MICRO_THICKNESS", type="SOLIDIFY"
    )
    solidify.thickness = (
        height * cfg["muzzle_patch_half_depth_fraction_of_height"] * 0.45
    )
    solidify.offset = -0.2
    solidify.use_even_offset = True
    patch["bentosaur_face_role"] = "smooth_generated_mouth_seam_repair"
    patch["final_topology"] = False
    return patch


def ring_coordinates(
    center: Vector,
    surface_x: float,
    half_width: float,
    half_height: float,
    lip_width: float,
    cavity_depth: float,
    corner_lift: float,
    segments: int,
    bvh: BVHTree,
    maximum_x: float,
    character_height: float,
) -> list[Vector]:
    # Five concentric rings, all behind the facial surface. The first three
    # remain explicit topology loops but are not rendered as an external
    # gasket; the Boolean-cut body surface owns the visible lip boundary.
    definitions = (
        (
            surface_x - character_height * 0.025,
            half_width + lip_width * 1.20,
            half_height + lip_width * 0.75,
        ),
        (
            surface_x - character_height * 0.032,
            half_width + lip_width * 0.70,
            half_height + lip_width * 0.42,
        ),
        (
            surface_x - character_height * 0.040,
            half_width,
            half_height,
        ),
        (
            surface_x - cavity_depth * 0.42,
            half_width * 0.76,
            half_height * 0.74,
        ),
        (
            surface_x - cavity_depth * 0.84,
            half_width * 0.48,
            max(half_height * 0.50, lip_width * 0.22),
        ),
    )
    coordinates: list[Vector] = []
    for ring_index, (base_x, width, ring_height) in enumerate(definitions):
        for segment in range(segments):
            theta = 2.0 * math.pi * segment / segments
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)
            smile = corner_lift * (abs(cos_theta) ** 7)
            y = center.y + width * cos_theta
            z = center.z + ring_height * sin_theta + smile
            x = base_x
            coordinates.append(Vector((x, y, z)))
    coordinates.append(
        Vector(
            (
                surface_x - cavity_depth,
                center.y,
                center.z,
            )
        )
    )
    return coordinates


def create_mouth_bag_and_lips(
    profile: dict[str, object],
    center: Vector,
    surface_x: float,
    height: float,
    bvh: BVHTree,
    maximum_x: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    cfg = profile["mouth"]
    segments = int(cfg["segments"])
    cavity_depth = (
        height * cfg["cavity_depth_fraction_of_height"]
    )
    lip_width = height * cfg["lip_width_fraction_of_height"]

    neutral_coords = ring_coordinates(
        center,
        surface_x - height * 0.014,
        height * cfg["neutral_half_width_fraction_of_height"],
        height * cfg["neutral_half_height_fraction_of_height"],
        lip_width,
        cavity_depth,
        0.0,
        segments,
        bvh,
        maximum_x,
        height,
    )
    open_coords = ring_coordinates(
        center,
        surface_x,
        height * cfg["open_half_width_fraction_of_height"],
        height * cfg["open_half_height_fraction_of_height"],
        lip_width,
        cavity_depth,
        height * cfg["open_corner_lift_fraction_of_height"],
        segments,
        bvh,
        maximum_x,
        height,
    )
    # The accepted H3.1 source already carries the neutral seam. Collapse the
    # authored open-mouth module deep inside the head at rest; at value 1 the
    # same topology expands into the delighted-open state. This prevents a
    # second neutral rim from being drawn over the approved source seam.
    collapsed = Vector(
        (
            surface_x - cavity_depth * 1.25,
            center.y,
            center.z,
        )
    )
    neutral_coords = [collapsed.copy() for _ in open_coords]

    faces: list[tuple[int, ...]] = []
    material_indices: list[int] = []
    ring_count = 5
    for ring_index in range(ring_count - 1):
        for segment in range(segments):
            next_segment = (segment + 1) % segments
            a = ring_index * segments + segment
            b = ring_index * segments + next_segment
            c = (ring_index + 1) * segments + next_segment
            d = (ring_index + 1) * segments + segment
            faces.append((a, b, c, d))
            # The aperture outline and cavity share the face-ink material.
            # Skin-coloured detached rim geometry reads like a gasket at
            # oblique views; final retopology will integrate the lip loops
            # directly into the muzzle.
            material_indices.append(0)

    cap_index = ring_count * segments
    throat_start = (ring_count - 1) * segments
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append(
            (
                throat_start + segment,
                throat_start + next_segment,
                cap_index,
            )
        )
        material_indices.append(0)

    mesh = bpy.data.meshes.new("BENTOSAUR_MOUTH_BAG_LIP_LOOPS_MESH")
    mesh.from_pydata(neutral_coords, [], faces)
    mesh.update()
    mouth = bpy.data.objects.new(
        "FACE_MOUTH_BAG_AND_LIP_LOOPS_SAME_MASTER", mesh
    )
    collection.objects.link(mouth)
    mouth.data.materials.append(materials["face_ink"])
    for polygon, material_index in zip(
        mouth.data.polygons, material_indices, strict=True
    ):
        polygon.material_index = material_index
        polygon.use_smooth = True

    mouth.shape_key_add(name="Basis")
    open_key = mouth.shape_key_add(name=SHAPE_KEY_NAME)
    for index, coordinate in enumerate(open_coords):
        open_key.data[index].co = coordinate
    mouth["mouth_bag_is_volumetric"] = True
    mouth["lip_loop_count"] = 3
    mouth["total_ring_count"] = ring_count
    mouth["teeth"] = False
    return mouth


def create_conformal_lip_repair_ring(
    profile: dict[str, object],
    center: Vector,
    minimum: Vector,
    maximum: Vector,
    height: float,
    bvh: BVHTree,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Build a smooth inset annulus that masks the disposable Boolean edge.

    Sampling every annulus vertex against a voxel proxy copies its tiny edge
    noise into the repair ring. Instead this uses one audited center-surface
    plane, placed inside the muzzle and later intersected against the uncut
    head volume. The result stays smooth and cannot escape the silhouette.
    """

    cfg = profile["mouth"]
    segments = 96
    outer_width = (
        height * cfg["open_half_width_fraction_of_height"] * 1.10
    )
    outer_height = (
        height * cfg["open_half_height_fraction_of_height"] * 1.10
    )
    ring_width = height * 0.0075
    inner_width = outer_width - ring_width
    inner_height = outer_height - ring_width
    corner_lift = (
        height * cfg["open_corner_lift_fraction_of_height"]
    )
    open_coordinates: list[Vector] = []
    plane_x = center.x - height * 0.003
    for width, ring_height in (
        (outer_width, outer_height),
        (inner_width, inner_height),
    ):
        for segment in range(segments):
            theta = 2.0 * math.pi * segment / segments
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)
            y = center.y + width * cos_theta
            z = (
                center.z
                + ring_height * sin_theta
                + corner_lift * (abs(cos_theta) ** 7)
            )
            open_coordinates.append(
                Vector((plane_x, y, z))
            )

    collapsed = Vector(
        (
            minimum.x + (maximum.x - minimum.x) * 0.55,
            center.y,
            center.z,
        )
    )
    vertices = [collapsed.copy() for _ in open_coordinates]
    faces: list[tuple[int, int, int, int]] = []
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append(
            (
                segment,
                next_segment,
                segments + next_segment,
                segments + segment,
            )
        )

    mesh = bpy.data.meshes.new("BENTOSAUR_CONFORMAL_LIP_REPAIR_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    ring = bpy.data.objects.new(
        "FACE_CONFORMAL_LIP_REPAIR_RING_SAME_MASTER", mesh
    )
    collection.objects.link(ring)
    ring.data.materials.append(materials["body_sage"])
    for polygon in ring.data.polygons:
        polygon.use_smooth = True
    ring.shape_key_add(name="Basis")
    open_key = ring.shape_key_add(name=SHAPE_KEY_NAME)
    for index, coordinate in enumerate(open_coordinates):
        open_key.data[index].co = coordinate
    ring["bentosaur_face_role"] = "boolean_edge_mask_smooth_inset_lip"
    ring["surface_ray_hit_ratio"] = 1.0
    ring["final_topology"] = False
    return ring


def create_mouth_cutter(
    profile: dict[str, object],
    center: Vector,
    surface_x: float,
    height: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    cfg = profile["mouth"]
    neutral_width = height * 0.040
    neutral_height = height * 0.0025
    open_width = (
        height * cfg["open_half_width_fraction_of_height"] * 1.05
    )
    open_height = (
        height * cfg["open_half_height_fraction_of_height"] * 1.05
    )
    depth = height * cfg["cavity_depth_fraction_of_height"] * 0.72
    neutral_depth = height * 0.008
    cutter_center = Vector(
        (
            surface_x - depth * 0.65,
            center.y,
            center.z,
        )
    )
    cutter = create_uv_ellipsoid(
        "HELPER_NON_DESTRUCTIVE_MOUTH_APERTURE_CUTTER",
        cutter_center,
        Vector((neutral_depth, neutral_width, neutral_height)),
        materials["face_ink"],
        collection,
        48,
        24,
    )
    cutter.data.materials.clear()
    for role in (
        "body_sage",
        "feature_cream",
        "accent_coral",
        "face_ink",
    ):
        cutter.data.materials.append(materials[role])
    for polygon in cutter.data.polygons:
        polygon.material_index = 3
    cutter.shape_key_add(name="Basis")
    open_key = cutter.shape_key_add(name=SHAPE_KEY_NAME)
    for index, vertex in enumerate(cutter.data.vertices):
        local = vertex.co
        open_key.data[index].co = Vector(
            (
                local.x,
                # The neutral helper sits completely behind the source
                # surface. Expanding its depth in the open shape is what
                # activates the Boolean aperture; the accepted source seam
                # remains untouched in the neutral state.
                #
                # This is a static shape-state mechanism, not animation.
                #
                # x is replaced below rather than duplicated.
                local.y * (open_width / neutral_width),
                local.z * (open_height / neutral_height),
            )
        )
        open_key.data[index].co.x = local.x * (
            depth / neutral_depth
        )
    cutter.display_type = "WIRE"
    cutter.hide_render = True
    cutter["helper_only"] = True
    cutter["drives_non_destructive_boolean"] = True
    return cutter


def create_tongue(
    profile: dict[str, object],
    center: Vector,
    surface_x: float,
    height: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    cfg = profile["mouth"]
    open_radii = Vector(
        (
            height * cfg["tongue_half_depth_fraction_of_height"],
            height * cfg["tongue_half_width_fraction_of_height"],
            height * cfg["tongue_half_height_fraction_of_height"],
        )
    )
    cavity_depth = (
        height * cfg["cavity_depth_fraction_of_height"]
    )
    tongue = create_uv_ellipsoid(
        "FACE_TONGUE_SEPARATE_SAME_MASTER",
        Vector(
            (
                surface_x - cavity_depth * 0.52,
                center.y,
                center.z
                - height * cfg["open_half_height_fraction_of_height"] * 0.45,
            )
        ),
        open_radii,
        materials["accent_coral"],
        collection,
        40,
        20,
    )
    basis = tongue.shape_key_add(name="Basis")
    open_key = tongue.shape_key_add(name=SHAPE_KEY_NAME)
    for index, vertex in enumerate(tongue.data.vertices):
        open_key.data[index].co = vertex.co.copy()
        basis.data[index].co = Vector(
            (-cavity_depth * 0.72, 0.0, 0.0)
        )
    tongue["bentosaur_face_role"] = "separate_volumetric_tongue"
    tongue["teeth"] = False
    return tongue


def create_master_controller(
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    root = bpy.data.objects.new(
        "BENTOSAUR_PRODUCTION_MASTER_STATIC_CONTROLLER", None
    )
    collection.objects.link(root)
    root.empty_display_type = "SPHERE"
    root.empty_display_size = 0.06
    root["expression_open"] = 0.0
    root.id_properties_ui("expression_open").update(
        min=0.0,
        max=1.0,
        soft_min=0.0,
        soft_max=1.0,
        description=(
            "0 = neutral closed, 1 = delighted open. Static lookdev only."
        ),
    )
    root["rigging_allowed"] = False
    root["animation_allowed"] = False
    root["visual_approval"] = False
    return root


def add_expression_driver(
    obj: bpy.types.Object, root: bpy.types.Object
) -> None:
    if not obj.data.shape_keys:
        raise RuntimeError(f"{obj.name} has no shape keys.")
    key = obj.data.shape_keys.key_blocks.get(SHAPE_KEY_NAME)
    if not key:
        raise RuntimeError(
            f"{obj.name} has no {SHAPE_KEY_NAME} shape key."
        )
    driver = key.driver_add("value").driver
    driver.type = "SCRIPTED"
    variable = driver.variables.new()
    variable.name = "expression"
    target = variable.targets[0]
    target.id_type = "OBJECT"
    target.id = root
    target.data_path = '["expression_open"]'
    driver.expression = "min(max(expression, 0.0), 1.0)"


def add_non_destructive_mouth_boolean(
    surface: bpy.types.Object, cutter: bpy.types.Object
) -> bpy.types.Modifier:
    modifier = surface.modifiers.new(
        f"NON_DESTRUCTIVE_MOUTH_APERTURE__{surface.name}",
        type="BOOLEAN",
    )
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    if hasattr(modifier, "material_mode"):
        modifier.material_mode = "TRANSFER"
    surface["mouth_boolean_applied_to_mesh"] = False
    return modifier


def add_head_interior_containment(
    mouth: bpy.types.Object,
    lip_repair: bpy.types.Object,
    clip_volume: bpy.types.Object,
    height: float,
) -> dict[str, str]:
    """Clip facial interior geometry to the uncut character volume.

    The open mouth bag is a cup with an aperture boundary. A micro-Solidify
    closes that shell for a robust Boolean, then INTERSECT removes every part
    that would extend outside the original head silhouette. The tongue is a
    smaller closed ellipsoid fitted inside the cavity without a Boolean, which
    avoids the visible clipping dents produced by intersecting its surface.
    """

    solidify = mouth.modifiers.new(
        "MOUTH_BAG_MICRO_SOLIDIFY_FOR_CONTAINMENT",
        type="SOLIDIFY",
    )
    solidify.thickness = height * 0.0015
    solidify.offset = -0.5
    solidify.use_even_offset = True
    solidify.use_rim = True

    mouth_clip = mouth.modifiers.new(
        "MOUTH_BAG_INTERSECT_HEAD_INTERIOR",
        type="BOOLEAN",
    )
    mouth_clip.operation = "INTERSECT"
    mouth_clip.solver = "EXACT"
    mouth_clip.object = clip_volume

    lip_solidify = lip_repair.modifiers.new(
        "LIP_REPAIR_MICRO_SOLIDIFY_FOR_CONTAINMENT",
        type="SOLIDIFY",
    )
    lip_solidify.thickness = height * 0.0008
    lip_solidify.offset = -0.5
    lip_solidify.use_even_offset = True
    lip_solidify.use_rim = True

    lip_clip = lip_repair.modifiers.new(
        "LIP_REPAIR_INTERSECT_HEAD_INTERIOR",
        type="BOOLEAN",
    )
    lip_clip.operation = "INTERSECT"
    lip_clip.solver = "EXACT"
    lip_clip.object = clip_volume

    return {
        "mouth_solidify": solidify.name,
        "mouth_intersect": mouth_clip.name,
        "lip_solidify": lip_solidify.name,
        "lip_intersect": lip_clip.name,
        "clip_volume": clip_volume.name,
        "tongue_intersect": "not_used_closed_tongue_fitted_inside_cavity",
    }


def set_expression(root: bpy.types.Object, value: float) -> None:
    root["expression_open"] = float(value)
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)
    bpy.context.view_layer.update()


def point_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (
        target - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def make_camera() -> bpy.types.Object:
    camera_data = bpy.data.cameras.new("APPROVAL_ORTHO_CAMERA")
    camera = bpy.data.objects.new(
        "APPROVAL_ORTHO_CAMERA", camera_data
    )
    bpy.context.scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    bpy.context.scene.camera = camera
    return camera


def make_area_light(
    name: str, energy: float, size: float
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_lights(scale: float) -> dict[str, bpy.types.Object]:
    return {
        "key": make_area_light(
            "APPROVAL_KEY", 105.0 * scale * scale, scale * 1.8
        ),
        "fill": make_area_light(
            "APPROVAL_FILL", 38.0 * scale * scale, scale * 2.2
        ),
        "rim": make_area_light(
            "APPROVAL_RIM", 68.0 * scale * scale, scale * 1.4
        ),
    }


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
        target
        + view * distance * 0.52
        - right * scale * 1.25
        + up * scale * 1.25
    )
    lights["fill"].location = (
        target
        + view * distance * 0.38
        + right * scale * 1.40
        + up * scale * 0.20
    )
    lights["rim"].location = (
        target
        - view * distance * 0.42
        + right * scale * 0.15
        + up * scale * 1.05
    )
    for light in lights.values():
        point_at(light, target)


def configure_scene(
    profile: dict[str, object], resolution: int
) -> None:
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.filter_size = 0.45
    scene.render.use_file_extension = True
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass

    world = bpy.data.worlds.new("BENTOSAUR_APPROVAL_WORLD")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = hex_to_rgba_linear(
        profile["render"]["world_color"]
    )
    background.inputs["Strength"].default_value = float(
        profile["render"]["world_strength"]
    )
    scene.world = world


def create_ground(
    minimum: Vector,
    scale: float,
    profile: dict[str, object],
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(
        size=scale * 4.0,
        location=(0.0, 0.0, minimum.z - scale * 0.007),
    )
    plane = bpy.context.object
    plane.name = "APPROVAL_GROUND_NOT_CHARACTER"
    material = make_flat_material(
        "MAT_APPROVAL_GROUND",
        profile["render"]["ground_color"],
        profile,
    )
    plane.data.materials.append(material)
    return plane


def render_still(
    path: Path,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    target: Vector,
    direction: Vector,
    ortho_scale: float,
    distance: float,
    scale: float,
    resolution: int,
) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    camera.data.ortho_scale = ortho_scale
    place_camera_and_lights(
        camera, lights, target, direction, distance, scale
    )
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def render_package(
    output: Path,
    root: bpy.types.Object,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    minimum: Vector,
    maximum: Vector,
    mouth_center: Vector,
    profile: dict[str, object],
    resolution: int,
    pixel_resolution: int,
) -> dict[str, object]:
    dimensions = maximum - minimum
    center = (minimum + maximum) * 0.5
    scale = max(dimensions)
    height = dimensions.z
    distance = max(scale * 3.1, 1.0)
    full_scale = scale / float(profile["render"]["orthographic_fill"])
    neutral: dict[str, str] = {}
    opened: dict[str, str] = {}

    set_expression(root, 0.0)
    for name, direction in VIEW_DIRECTIONS.items():
        neutral[name] = render_still(
            output / "renders" / "neutral" / f"{name}.png",
            camera,
            lights,
            center,
            direction,
            full_scale,
            distance,
            scale,
            resolution,
        )
    neutral_face = render_still(
        output / "renders" / "neutral" / "face_closeup.png",
        camera,
        lights,
        Vector((mouth_center.x, mouth_center.y, mouth_center.z + height * 0.08)),
        VIEW_DIRECTIONS["front"],
        height * 0.46,
        distance,
        scale,
        resolution,
    )
    neutral_mouth = render_still(
        output / "renders" / "neutral" / "mouth_closeup.png",
        camera,
        lights,
        mouth_center,
        VIEW_DIRECTIONS["three_quarter_left"],
        height * 0.30,
        distance,
        scale,
        resolution,
    )

    set_expression(root, 1.0)
    for name in ("front", "three_quarter_left", "right"):
        opened[name] = render_still(
            output / "renders" / "delighted_open" / f"{name}.png",
            camera,
            lights,
            center,
            VIEW_DIRECTIONS[name],
            full_scale,
            distance,
            scale,
            resolution,
        )
    open_face = render_still(
        output / "renders" / "delighted_open" / "face_closeup.png",
        camera,
        lights,
        Vector((mouth_center.x, mouth_center.y, mouth_center.z + height * 0.08)),
        VIEW_DIRECTIONS["front"],
        height * 0.46,
        distance,
        scale,
        resolution,
    )
    open_mouth = render_still(
        output
        / "renders"
        / "delighted_open"
        / "mouth_interior_three_quarter.png",
        camera,
        lights,
        mouth_center,
        VIEW_DIRECTIONS["three_quarter_left"],
        height * 0.30,
        distance,
        scale,
        resolution,
    )
    native = render_still(
        output
        / "renders"
        / "native_scale"
        / f"front_open_{pixel_resolution}px.png",
        camera,
        lights,
        center,
        VIEW_DIRECTIONS["front"],
        full_scale,
        distance,
        scale,
        pixel_resolution,
    )

    set_expression(root, 0.0)
    return {
        "neutral": neutral,
        "delighted_open": opened,
        "neutral_face_closeup": neutral_face,
        "neutral_mouth_closeup": neutral_mouth,
        "open_face_closeup": open_face,
        "open_mouth_closeup": open_mouth,
        "native_scale": native,
    }


def render_mouth_diagnostic(
    output: Path,
    root: bpy.types.Object,
    camera: bpy.types.Object,
    lights: dict[str, bpy.types.Object],
    minimum: Vector,
    maximum: Vector,
    mouth_center: Vector,
    profile: dict[str, object],
    resolution: int,
) -> dict[str, str]:
    dimensions = maximum - minimum
    center = (minimum + maximum) * 0.5
    scale = max(dimensions)
    height = dimensions.z
    distance = max(scale * 3.1, 1.0)
    full_scale = scale / float(profile["render"]["orthographic_fill"])
    face_target = Vector(
        (
            mouth_center.x,
            mouth_center.y,
            mouth_center.z + height * 0.08,
        )
    )

    set_expression(root, 0.0)
    neutral_face = render_still(
        output / "renders" / "diagnostic" / "neutral_face_front.png",
        camera,
        lights,
        face_target,
        VIEW_DIRECTIONS["front"],
        height * 0.46,
        distance,
        scale,
        resolution,
    )
    neutral_profile = render_still(
        output / "renders" / "diagnostic" / "neutral_right_profile.png",
        camera,
        lights,
        center,
        VIEW_DIRECTIONS["right"],
        full_scale,
        distance,
        scale,
        resolution,
    )

    set_expression(root, 1.0)
    open_face = render_still(
        output / "renders" / "diagnostic" / "open_face_front.png",
        camera,
        lights,
        face_target,
        VIEW_DIRECTIONS["front"],
        height * 0.46,
        distance,
        scale,
        resolution,
    )
    open_profile = render_still(
        output / "renders" / "diagnostic" / "open_right_profile.png",
        camera,
        lights,
        center,
        VIEW_DIRECTIONS["right"],
        full_scale,
        distance,
        scale,
        resolution,
    )
    open_three_quarter = render_still(
        output
        / "renders"
        / "diagnostic"
        / "open_mouth_three_quarter.png",
        camera,
        lights,
        mouth_center,
        VIEW_DIRECTIONS["three_quarter_left"],
        height * 0.30,
        distance,
        scale,
        resolution,
    )
    set_expression(root, 0.0)
    return {
        "neutral_face_front": neutral_face,
        "neutral_right_profile": neutral_profile,
        "open_face_front": open_face,
        "open_right_profile": open_profile,
        "open_mouth_three_quarter": open_three_quarter,
    }


def create_mouth_diagnostic_board(
    output: Path,
    renders: dict[str, str],
) -> dict[str, str]:
    magick = shutil.which("magick")
    if not magick:
        return {}
    boards = output / "boards"
    boards.mkdir(parents=True, exist_ok=True)
    body = boards / "_mouth_diagnostic_body.png"
    board = boards / "mouth_front_profile_diagnostic.png"
    subprocess.run(
        [
            magick,
            "montage",
            "-font",
            BOARD_FONT,
            renders["neutral_face_front"],
            renders["open_face_front"],
            renders["neutral_right_profile"],
            renders["open_right_profile"],
            renders["open_mouth_three_quarter"],
            "-tile",
            "2x3",
            "-geometry",
            "620x620+14+14",
            "-background",
            "#20252D",
            str(body),
        ],
        check=True,
    )
    add_board_header(
        magick,
        body,
        board,
        "Focused neutral/open mouth containment diagnostic; no final approval",
    )
    body.unlink(missing_ok=True)
    return {"mouth_front_profile_diagnostic": str(board)}


def add_board_header(
    magick: str,
    body: Path,
    output: Path,
    subtitle: str,
) -> None:
    subprocess.run(
        [
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
            "34",
            "-annotate",
            "+0+23",
            "BENTOSAUR STATIC MASTER — USER APPROVAL REQUIRED",
            "-fill",
            "#B9C6D3",
            "-pointsize",
            "20",
            "-annotate",
            "+0+74",
            subtitle,
            str(output),
        ],
        check=True,
    )


def create_review_boards(
    output: Path,
    renders: dict[str, object],
    profile: dict[str, object],
) -> dict[str, str]:
    magick = shutil.which("magick")
    if not magick:
        return {}
    boards = output / "boards"
    boards.mkdir(parents=True, exist_ok=True)
    result: dict[str, str] = {}

    neutral = renders["neutral"]
    six_body = boards / "_neutral_six_body.png"
    six_board = boards / "neutral_closed_six_view_board.png"
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
            "480x480+12+12",
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
        "Neutral closed state | same unrigged master | source remains locked",
    )
    six_body.unlink(missing_ok=True)
    result["neutral_six_view"] = str(six_board)

    expression_body = boards / "_expression_body.png"
    expression_board = boards / "face_and_mouth_state_board.png"
    subprocess.run(
        [
            magick,
            "montage",
            "-font",
            BOARD_FONT,
            renders["neutral_face_closeup"],
            renders["open_face_closeup"],
            renders["neutral_mouth_closeup"],
            renders["open_mouth_closeup"],
            "-tile",
            "2x2",
            "-geometry",
            "620x620+14+14",
            "-background",
            "#20252D",
            str(expression_body),
        ],
        check=True,
    )
    add_board_header(
        magick,
        expression_body,
        expression_board,
        "Neutral face | delighted open | closed/open mouth geometry closeups",
    )
    expression_body.unlink(missing_ok=True)
    result["face_and_mouth_states"] = str(expression_board)

    side_body = boards / "_side_body.png"
    side_board = boards / "side_closed_open_comparison.png"
    subprocess.run(
        [
            magick,
            "montage",
            "-font",
            BOARD_FONT,
            neutral["right"],
            renders["delighted_open"]["right"],
            "-tile",
            "2x1",
            "-geometry",
            "620x620+14+14",
            "-background",
            "#20252D",
            str(side_body),
        ],
        check=True,
    )
    add_board_header(
        magick,
        side_body,
        side_board,
        "Right profile: neutral closed | delighted open static shape",
    )
    side_body.unlink(missing_ok=True)
    result["side_state_comparison"] = str(side_board)

    palette = profile["palette"]
    swatch_body = boards / "_swatches_body.png"
    swatch_board = boards / "semantic_material_swatches.png"
    # Create the swatches individually because ImageMagick's montage parser
    # does not retain per-input annotations from one compound command.
    swatches: list[str] = []
    for role in (
        "body_sage",
        "feature_cream",
        "accent_coral",
        "face_ink",
    ):
        path = boards / f"_swatch_{role}.png"
        text_color = "#FFFFFF" if role == "face_ink" else "#1B110C"
        subprocess.run(
            [
                magick,
                "-size",
                "440x220",
                f"xc:{palette[role]}",
                "-fill",
                text_color,
                "-gravity",
                "south",
                "-font",
                BOARD_FONT,
                "-pointsize",
                "28",
                "-annotate",
                "+0+20",
                f"{role}  {palette[role]}",
                str(path),
            ],
            check=True,
        )
        swatches.append(str(path))
    subprocess.run(
        [
            magick,
            "montage",
            "-font",
            BOARD_FONT,
            *swatches,
            "-tile",
            "2x2",
            "-geometry",
            "+12+12",
            "-background",
            "#20252D",
            str(swatch_body),
        ],
        check=True,
    )
    add_board_header(
        magick,
        swatch_body,
        swatch_board,
        "Semantic flat-material contract; cream feature zoning still needs manual fit",
    )
    swatch_body.unlink(missing_ok=True)
    for path in swatches:
        Path(path).unlink(missing_ok=True)
    result["semantic_material_swatches"] = str(swatch_board)
    return result


def topology_metrics(obj: bpy.types.Object) -> dict[str, object]:
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    row = {
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "polygons": len(mesh.polygons),
        "evaluated_triangles": len(mesh.loop_triangles),
        "triangle_faces": sum(
            len(poly.vertices) == 3 for poly in mesh.polygons
        ),
        "quad_faces": sum(
            len(poly.vertices) == 4 for poly in mesh.polygons
        ),
        "ngons": sum(
            len(poly.vertices) > 4 for poly in mesh.polygons
        ),
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges": sum(
            not edge.is_manifold for edge in bm.edges
        ),
        "loose_edges": sum(not edge.link_faces for edge in bm.edges),
        "loose_vertices": sum(
            not vertex.link_faces for vertex in bm.verts
        ),
        "shape_keys": (
            [key.name for key in mesh.shape_keys.key_blocks]
            if mesh.shape_keys
            else []
        ),
        "material_slots": [
            slot.material.name if slot.material else None
            for slot in obj.material_slots
        ],
        "modifiers": [
            {
                "name": modifier.name,
                "type": modifier.type,
                "applied": False,
            }
            for modifier in obj.modifiers
        ],
    }
    bm.free()
    return row


def write_semantic_zone_template(
    output: Path,
    surface: bpy.types.Object,
    semantic_overlay_metrics: dict[str, object],
) -> Path:
    path = output / "semantic-zones-template.json"
    payload = {
        "schema_version": "1.0.0",
        "surface_object": surface.name,
        "status": (
            "fitted_static_lookdev_overlays_created;"
            "manual_final_retopology_zones_required"
        ),
        "default_material": "MAT_BENTOSAUR_BODY_SAGE",
        "zones": {
            "feature_cream": {
                "material": "MAT_BENTOSAUR_FEATURE_CREAM",
                "anatomical_regions": [
                    "belly",
                    "primary_horns",
                    "frill_knobs",
                    "dorsal_knobs",
                    "hand_claws",
                    "foot_claws",
                ],
                "polygon_indices": [],
                "implemented_for_static_visual_gate_as": (
                    "fitted_belly_surface_overlay_plus_individually_fitted_"
                    "discrete_feature_primitives"
                ),
                "overlay_objects": semantic_overlay_metrics[
                    "created_objects"
                ],
                "final_retopology_assignment_complete": False,
            },
            "accent_coral": {
                "material": "MAT_BENTOSAUR_ACCENT_CORAL",
                "anatomical_regions": ["cheeks"],
                "polygon_indices": [],
                "implemented_as_separate_geometry": True,
            },
            "face_ink": {
                "material": "MAT_BENTOSAUR_FACE_INK",
                "anatomical_regions": ["eyes", "mouth_cavity"],
                "polygon_indices": [],
                "implemented_as_separate_geometry": True,
            },
        },
        "warning": (
            "The fitted overlays are visual-gate scaffolding, not deformation "
            "topology. A character artist must transfer the approved region "
            "boundaries to the final retopologized production surface."
        ),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_readme(output: Path) -> Path:
    path = output / "README.md"
    path.write_text(
        """# Bentosaur static production-master stage

**Status: USER APPROVAL REQUIRED — RIGGING BLOCKED**

This package is a non-destructive static look-development stage. The original
GLB is hash-checked before and after execution and remains hidden in
`00_SOURCE_LOCKED_DO_NOT_EDIT`.

What is real in this package:

- separate controlled eye and cheek geometry;
- exact semantic sage, cream, coral, and ink material definitions;
- fitted, separate cream lookdev overlays for the belly, horns, frill knobs,
  and claws;
- a recessed mouth bag with three explicit lip loops;
- a separate volumetric tongue;
- one master property driving both neutral-closed and delighted-open states;
- a non-destructive Boolean aperture on the disposable surface proxy.

What is deliberately not claimed:

- the automatic body proxy is not deformation-ready retopology;
- cream zones are static lookdev overlays and still need transfer to the final
  deformation-ready retopology;
- no rig, skinning, bones, weights, animation clips, or gameplay export exist;
- no visual decision has been made for the user.

The static controller property is:
`BENTOSAUR_PRODUCTION_MASTER_STATIC_CONTROLLER["expression_open"]`

- `0.0` = neutral closed
- `1.0` = delighted open

Only explicit user approval of the rendered appearance package can unlock the
manual retopology/rigging stage.
""",
        encoding="utf-8",
    )
    return path


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    profile_path = args.profile.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if not profile_path.is_file():
        raise FileNotFoundError(profile_path)
    output.mkdir(parents=True, exist_ok=True)
    source_hash_before = sha256(source)
    profile_hash = sha256(profile_path)
    profile = load_profile(profile_path)
    rebuild_mode = (
        args.rebuild_mode or profile["rebuild"]["default_mode"]
    )

    clear_scene()
    configure_scene(profile, args.resolution)
    source_meshes, _source_collection = import_source_locked(source)
    production_collection = make_collection("10_PRODUCTION_MASTER_STATIC")
    face_collection = make_collection("20_FACE_MODULE_SAME_MASTER")
    semantic_collection = make_collection(
        "30_SEMANTIC_FITTED_OVERLAYS_LOOKDEV_ONLY"
    )
    helper_collection = make_collection("90_HELPERS_NOT_RENDERED")

    surface = duplicate_joined_surface(
        source_meshes, production_collection
    )
    minimum_before, maximum_before = world_bounds([surface])
    dimensions_before = maximum_before - minimum_before
    height = dimensions_before.z
    expected_height = profile["coordinate_contract"][
        "expected_source_height_range"
    ]
    height_warning = not (
        expected_height[0] <= height <= expected_height[1]
    )

    proxy_metrics = build_surface_proxy(
        surface, rebuild_mode, profile, height
    )
    minimum, maximum = world_bounds([surface])
    dimensions = maximum - minimum
    height = dimensions.z

    materials = create_semantic_materials(profile)
    assign_surface_material_slots(surface, materials)
    clip_volume = create_head_interior_clip_volume(
        surface, helper_collection
    )
    bvh = build_surface_bvh(surface)
    face_objects, face_metrics = create_face_components(
        profile,
        minimum,
        maximum,
        bvh,
        materials,
        face_collection,
    )
    semantic_objects, semantic_overlay_metrics = (
        create_semantic_feature_overlays(
            surface,
            height,
            materials["feature_cream"],
            semantic_collection,
        )
    )

    mouth_guess = normalized_landmark(
        profile["landmarks_normalized_to_source_bounds"]["mouth_center"],
        minimum,
        maximum,
    )
    mouth_surface, mouth_normal, mouth_hit = front_surface_point(
        bvh, mouth_guess, maximum.x, height
    )
    mouth_surface_x = mouth_surface.x + (
        height
        * profile["mouth"]["surface_offset_fraction_of_height"]
    )
    mouth_center = Vector(
        (mouth_surface_x, mouth_guess.y, mouth_guess.z)
    )

    mouth = create_mouth_bag_and_lips(
        profile,
        mouth_center,
        mouth_surface_x,
        height,
        bvh,
        maximum.x,
        materials,
        face_collection,
    )
    lip_repair = create_conformal_lip_repair_ring(
        profile,
        mouth_center,
        minimum,
        maximum,
        height,
        bvh,
        materials,
        face_collection,
    )
    lip_repair.hide_render = bool(args.hide_lip_repair)
    tongue = create_tongue(
        profile,
        mouth_center,
        mouth_surface_x,
        height,
        materials,
        face_collection,
    )
    cutter = create_mouth_cutter(
        profile,
        mouth_center,
        mouth_surface_x,
        height,
        materials,
        helper_collection,
    )
    controller = create_master_controller(production_collection)
    for obj in (mouth, lip_repair, tongue, cutter):
        add_expression_driver(obj, controller)
        obj.parent = controller
    for obj in face_objects:
        obj.parent = controller
    for obj in semantic_objects:
        obj.parent = controller
    surface.parent = controller
    boolean = add_non_destructive_mouth_boolean(surface, cutter)
    containment = add_head_interior_containment(
        mouth, lip_repair, clip_volume, height
    )

    scale = max(dimensions)
    camera = make_camera()
    lights = make_lights(scale)
    ground = create_ground(minimum, scale, profile)
    if args.render_scope == "mouth":
        renders = render_mouth_diagnostic(
            output,
            controller,
            camera,
            lights,
            minimum,
            maximum,
            mouth_center,
            profile,
            args.resolution,
        )
        boards = create_mouth_diagnostic_board(output, renders)
    else:
        renders = render_package(
            output,
            controller,
            camera,
            lights,
            minimum,
            maximum,
            mouth_center,
            profile,
            args.resolution,
            args.pixel_resolution,
        )
        boards = create_review_boards(output, renders, profile)
    zone_template = write_semantic_zone_template(
        output, surface, semantic_overlay_metrics
    )
    readme = write_readme(output)

    source_hash_after = sha256(source)
    if source_hash_after != source_hash_before:
        raise RuntimeError("The locked source GLB changed during the build.")

    set_expression(controller, 0.0)
    blend_path = output / (
        f"{args.candidate_id}_static_master_user_approval_required.blend"
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    manifest = {
        "schema_version": "1.0.0",
        "candidate_id": args.candidate_id,
        "status": "static_appearance_package_awaiting_user_approval",
        "source": {
            "path": str(source),
            "sha256_before": source_hash_before,
            "sha256_after": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
            "locked_collection": "00_SOURCE_LOCKED_DO_NOT_EDIT",
        },
        "profile": {
            "path": str(profile_path),
            "sha256": profile_hash,
            "profile_id": profile["profile_id"],
            "landmarks_confirmed_for_candidate": args.landmarks_confirmed,
        },
        "bounds": {
            "source_copy_before_proxy": {
                "minimum": list(minimum_before),
                "maximum": list(maximum_before),
                "dimensions": list(dimensions_before),
            },
            "lookdev_proxy": {
                "minimum": list(minimum),
                "maximum": list(maximum),
                "dimensions": list(dimensions),
            },
            "source_height_outside_expected_range": height_warning,
        },
        "surface_proxy": {
            **proxy_metrics,
            "object": surface.name,
            "topology": topology_metrics(surface),
            "semantic_material_slots_registered": True,
            "body_sage_assigned": True,
            "cream_feature_polygon_zones_complete": False,
            "cream_feature_static_visual_overlays_complete": True,
            "cream_feature_overlays": semantic_overlay_metrics,
            "cream_zone_template": str(zone_template),
        },
        "face_system": {
            **face_metrics,
            "mouth_landmark_surface_ray_hit": mouth_hit,
            "mouth_surface_normal": list(mouth_normal),
            "mouth_object": mouth.name,
            "mouth_topology": topology_metrics(mouth),
            "conformal_lip_repair": {
                "object": lip_repair.name,
                "topology": topology_metrics(lip_repair),
                "surface_ray_hit_ratio": lip_repair[
                    "surface_ray_hit_ratio"
                ],
                "final_topology": False,
                "hidden_from_render": lip_repair.hide_render,
            },
            "tongue_object": tongue.name,
            "tongue_topology": topology_metrics(tongue),
            "cutter_object": cutter.name,
            "cutter_topology": topology_metrics(cutter),
            "body_aperture_boolean": {
                "modifier": boolean.name,
                "applied_to_mesh": False,
                "solver": boolean.solver,
            },
            "head_interior_containment": {
                **containment,
                "non_destructive": True,
                "purpose": "prevent_cavity_or_tongue_outside_head_silhouette",
            },
            "same_master_static_states": True,
            "controller": controller.name,
            "controller_property": "expression_open",
            "neutral_value": 0.0,
            "delighted_open_value": 1.0,
            "shape_key": SHAPE_KEY_NAME,
            "lip_loop_count": 3,
            "real_recessed_mouth_bag": True,
            "separate_volumetric_tongue": True,
            "teeth": False,
        },
        "materials": {
            role: {
                "name": material.name,
                "hex_srgb": profile["palette"][role],
                "roughness": profile["materials"]["roughness"],
                "metallic": profile["materials"]["metallic"],
            }
            for role, material in materials.items()
        },
        "approval_gate": {
            "assistant_may_approve": False,
            "visual_approval": False,
            "user_approval_required": True,
            "rigging_allowed": False,
            "skinning_performed": False,
            "armature_created": False,
            "animation_performed": False,
            "manual_retopology_required_before_rigging": True,
        },
        "limitations": [
            "The voxel/source-copy surface is a lookdev proxy, not deformation-ready joint-loop retopology.",
            "Fitted cream lookdev overlays are not final deformation-topology material zones; their approved boundaries must be transferred during manual retopology.",
            "Landmark placement must be reviewed against the exact H3.1 candidate before this package can be shown as final appearance evidence.",
            "The non-destructive mouth Boolean is retained for lookdev; the final retopology must integrate the aperture and lip loops cleanly.",
            "No rig, skinning, weights, animation, or gameplay export was created.",
        ],
        "outputs": {
            "blend": str(blend_path),
            "manifest": str(output / "manifest.json"),
            "readme": str(readme),
            "semantic_zone_template": str(zone_template),
            "renders": renders,
            "boards": boards,
        },
        "cost": {
            "paid_api_calls_made_by_this_stage": 0,
            "tripo_credits_consumed_by_this_stage": 0,
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
                "manifest": str(manifest_path),
                "blend": str(blend_path),
                "boards": boards,
                "rigging_allowed": False,
                "visual_approval": False,
            }
        )
    )


if __name__ == "__main__":
    main()
