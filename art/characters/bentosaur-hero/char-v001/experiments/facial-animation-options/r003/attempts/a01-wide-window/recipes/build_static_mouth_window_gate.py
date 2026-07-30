"""Build Bentosaur r003's bounded static mouth-window visual gate.

This script starts from the frozen r002 facial proof, duplicates it through
numbered checkpoints, and changes only a small mouth window on the duplicated
body. It stops before morph targets or new skinning:

00 frozen parent
10 mouth window cut
20 flush skin transition and static aperture
30 recessed cavity and contained tongue
40 render ready
50 static GLB export

The purpose is visual approval at front, three-quarter, and profile angles.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from types import ModuleType
from typing import Iterable

import bpy
from mathutils import Vector


BODY_OBJECT = "BENTOSAUR_R003_BODY_FACIAL_PROOF_STATIC"
RIG_OBJECT = "BENTOSAUR_FACE_RIG_MOBILE_PROOF"
OLD_MOUTH_OBJECTS = (
    "FACE_MOUTH_APERTURE_MOBILE_PROXY",
    "FACE_UPPER_LIP_MOBILE_PROXY",
    "FACE_LOWER_LIP_JAW_SKINNED_PROXY",
    "FACE_TONGUE_MOBILE_PROXY",
)
SKIN_MODULE_OBJECT = "FACE_MOUTH_WINDOW_SKIN_STATIC_GATE"
CAVITY_WALL_OBJECT = "FACE_MOUTH_CAVITY_WALL_STATIC_GATE"
CAVITY_BACK_OBJECT = "FACE_MOUTH_CAVITY_BACK_STATIC_GATE"
TONGUE_OBJECT = "FACE_TONGUE_CONTAINED_STATIC_GATE"

EXPECTED_PARENT_SHA256 = (
    "938178537d96f1196e686fbd56a8f0bebc93e8877f83be7d6b7f5e14415d5bea"
)
REPORT_ROOT: Path | None = None


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=720)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError(f"No Git repository found above {path}")


def report_path(path: Path) -> str:
    resolved = path.resolve()
    if REPORT_ROOT is not None:
        try:
            return resolved.relative_to(REPORT_ROOT).as_posix()
        except ValueError:
            pass
    return resolved.as_posix()


def load_parent_recipe(root: Path) -> ModuleType:
    recipe = (
        root
        / "art/characters/bentosaur-hero/char-v001/experiments"
        / "facial-animation-options/r002/recipes/build_facial_rig_proof.py"
    )
    spec = importlib.util.spec_from_file_location(
        "bentosaur_r002_facial_recipe", recipe
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {recipe}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def artifact(path: Path) -> dict[str, object]:
    return {
        "path": report_path(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def save_checkpoint(path: Path) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
    return artifact(path)


def outside_window_signature(
    body: bpy.types.Object,
) -> dict[str, object]:
    coordinates = []
    for vertex in body.data.vertices:
        x, y, z = vertex.co
        if abs(x) <= 0.105 and 0.405 <= z <= 0.525:
            continue
        coordinates.append(
            f"{x:.7f},{y:.7f},{z:.7f}"
        )
    coordinates.sort()
    encoded = "\n".join(coordinates).encode("utf-8")
    return {
        "vertex_count": len(coordinates),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


def remove_old_mouth_objects() -> None:
    for name in OLD_MOUTH_OBJECTS:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)


def open_boundary(parent: ModuleType) -> list[tuple[float, float]]:
    return parent.sample_closed_beziers(parent.OPEN_BEZIERS, 32)


def scale_boundary(
    boundary: list[tuple[float, float]],
    scale_x: float,
    scale_z: float,
) -> list[tuple[float, float]]:
    center_x = sum(x for x, _z in boundary) / len(boundary)
    center_z = sum(z for _x, z in boundary) / len(boundary)
    return [
        (
            center_x + (x - center_x) * scale_x,
            center_z + (z - center_z) * scale_z,
        )
        for x, z in boundary
    ]


def interpolate_boundary(
    outer: list[tuple[float, float]],
    inner: list[tuple[float, float]],
    fraction: float,
) -> list[tuple[float, float]]:
    return [
        (
            outer_x + (inner_x - outer_x) * fraction,
            outer_z + (inner_z - outer_z) * fraction,
        )
        for (outer_x, outer_z), (inner_x, inner_z) in zip(
            outer, inner, strict=True
        )
    ]


def make_prism_cutter(
    name: str,
    boundary: list[tuple[float, float]],
    y_front: float,
    y_back: float,
) -> bpy.types.Object:
    count = len(boundary)
    vertices = [
        Vector((x, y_front, z)) for x, z in boundary
    ] + [
        Vector((x, y_back, z)) for x, z in boundary
    ]
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, 2 * count)),
    ]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def apply_mouth_window_cut(
    body: bpy.types.Object,
    outer_boundary: list[tuple[float, float]],
    parent: ModuleType,
    bvh,
) -> None:
    center_y = parent.surface_y(bvh, 0.0, 0.468)
    cutter = make_prism_cutter(
        "R003_MOUTH_WINDOW_CUTTER",
        outer_boundary,
        center_y - 0.14,
        center_y + 0.12,
    )
    modifier = body.modifiers.new(
        "R003_STATIC_MOUTH_WINDOW_BOOLEAN", "BOOLEAN"
    )
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    body.select_set(False)
    bpy.data.objects.remove(cutter, do_unlink=True)
    body.name = "BENTOSAUR_R003_BODY_STATIC_MOUTH_WINDOW_GATE"
    body["parent_body"] = BODY_OBJECT
    body["localized_mouth_window_cut"] = True
    body["production_approved"] = False


def loop_vertices(
    boundary: list[tuple[float, float]],
    bvh,
    parent: ModuleType,
    inward: float,
) -> list[Vector]:
    return [
        Vector((x, parent.surface_y(bvh, x, z) + inward, z))
        for x, z in boundary
    ]


def bridge_faces(
    loop_count: int,
    points_per_loop: int,
) -> list[tuple[int, int, int, int]]:
    faces = []
    for loop in range(loop_count - 1):
        current = loop * points_per_loop
        following = (loop + 1) * points_per_loop
        for index in range(points_per_loop):
            nxt = (index + 1) % points_per_loop
            faces.append(
                (
                    current + index,
                    current + nxt,
                    following + nxt,
                    following + index,
                )
            )
    return faces


def create_skin_transition(
    outer: list[tuple[float, float]],
    aperture: list[tuple[float, float]],
    bvh,
    parent: ModuleType,
    body_material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    fractions = (0.0, 0.34, 0.68, 1.0)
    inwards = (-0.0008, -0.0003, 0.0005, 0.0018)
    loops = [
        loop_vertices(
            interpolate_boundary(outer, aperture, fraction),
            bvh,
            parent,
            inward,
        )
        for fraction, inward in zip(fractions, inwards, strict=True)
    ]
    vertices = [vertex for loop in loops for vertex in loop]
    mesh = bpy.data.meshes.new(SKIN_MODULE_OBJECT + "_MESH")
    mesh.from_pydata(
        vertices,
        [],
        bridge_faces(len(loops), len(outer)),
    )
    mesh.update()
    obj = bpy.data.objects.new(SKIN_MODULE_OBJECT, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(body_material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj["fixed_outer_seam"] = True
    obj["static_visual_gate_only"] = True
    obj["production_approved"] = False
    return obj


def create_cavity_wall(
    aperture: list[tuple[float, float]],
    bvh,
    parent: ModuleType,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> tuple[bpy.types.Object, list[tuple[float, float]]]:
    back_boundary = scale_boundary(aperture, 0.84, 0.79)
    front = loop_vertices(aperture, bvh, parent, 0.0017)
    back = loop_vertices(back_boundary, bvh, parent, 0.031)
    mesh = bpy.data.meshes.new(CAVITY_WALL_OBJECT + "_MESH")
    mesh.from_pydata(
        front + back,
        [],
        bridge_faces(2, len(aperture)),
    )
    mesh.update()
    obj = bpy.data.objects.new(CAVITY_WALL_OBJECT, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj["recessed_depth"] = 0.031
    obj["static_visual_gate_only"] = True
    obj["production_approved"] = False
    return obj, back_boundary


def cavity_back_vertices(
    boundary: list[tuple[float, float]],
    bvh,
    parent: ModuleType,
    rings: int,
) -> list[Vector]:
    center_x = sum(x for x, _z in boundary) / len(boundary)
    center_z = sum(z for _x, z in boundary) / len(boundary)
    vertices = [
        Vector(
            (
                center_x,
                parent.surface_y(bvh, center_x, center_z) + 0.035,
                center_z,
            )
        )
    ]
    for ring in range(1, rings + 1):
        fraction = ring / rings
        for x, z in boundary:
            point_x = center_x + (x - center_x) * fraction
            point_z = center_z + (z - center_z) * fraction
            vertices.append(
                Vector(
                    (
                        point_x,
                        parent.surface_y(bvh, point_x, point_z) + 0.034,
                        point_z,
                    )
                )
            )
    return vertices


def create_cavity_back(
    boundary: list[tuple[float, float]],
    bvh,
    parent: ModuleType,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    rings = 3
    mesh = bpy.data.meshes.new(CAVITY_BACK_OBJECT + "_MESH")
    mesh.from_pydata(
        cavity_back_vertices(boundary, bvh, parent, rings),
        [],
        parent.radial_faces(len(boundary), rings),
    )
    mesh.update()
    obj = bpy.data.objects.new(CAVITY_BACK_OBJECT, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj["static_visual_gate_only"] = True
    obj["production_approved"] = False
    return obj


def create_tongue(
    bvh,
    parent: ModuleType,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    tongue_y = parent.surface_y(bvh, 0.0, 0.448) + 0.006
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        location=(0.0, tongue_y, 0.448),
        scale=(0.040, 0.012, 0.017),
    )
    tongue = bpy.context.object
    tongue.name = TONGUE_OBJECT
    for current_collection in list(tongue.users_collection):
        current_collection.objects.unlink(tongue)
    collection.objects.link(tongue)
    bpy.ops.object.transform_apply(
        location=True,
        rotation=True,
        scale=True,
    )
    tongue.data.materials.append(material)
    for polygon in tongue.data.polygons:
        polygon.use_smooth = True
    tongue["static_visual_gate_only"] = True
    tongue["unskinned_until_visual_approval"] = True
    tongue["production_approved"] = False
    return tongue


def make_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.16
    return material


def point_camera(
    camera: bpy.types.Object,
    view: str,
    closeup: bool,
) -> None:
    target = Vector((0.0, -0.02, 0.49 if closeup else 0.50))
    if view == "front":
        camera.location = Vector((0.0, -1.45, target.z))
    elif view == "three_quarter":
        camera.location = Vector((0.42, -1.45, target.z + 0.02))
    elif view == "profile":
        camera.location = Vector((1.45, -0.02, target.z + 0.01))
    else:
        raise ValueError(view)
    camera.data.ortho_scale = 0.54 if closeup else 1.12
    camera.rotation_euler = (
        target - camera.location
    ).to_track_quat("-Z", "Y").to_euler()


def configure_render(resolution: int) -> bpy.types.Object:
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
    camera = bpy.data.objects.get("FACIAL_PROOF_CAMERA")
    if camera is None:
        raise RuntimeError("The r002 camera is missing.")
    scene.camera = camera
    return camera


def render(
    path: Path,
    camera: bpy.types.Object,
    view: str,
    closeup: bool,
) -> dict[str, object]:
    point_camera(camera, view, closeup)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return artifact(path)


def topology(obj: bpy.types.Object) -> dict[str, int]:
    return {
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
        "triangles_after_export": sum(
            max(1, len(polygon.vertices) - 2)
            for polygon in obj.data.polygons
        ),
    }


def export_glb(
    path: Path,
    objects: Iterable[bpy.types.Object],
) -> dict[str, object]:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
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
        export_morph=False,
        export_skins=True,
        export_extras=True,
        export_apply=False,
    )
    return artifact(path)


def audit_round_trip(
    glb_path: Path,
    qa_path: Path,
) -> dict[str, object]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    meshes = {
        obj.name: topology(obj)
        for obj in bpy.data.objects
        if obj.type == "MESH"
    }
    armatures = {
        obj.name: [bone.name for bone in obj.data.bones]
        for obj in bpy.data.objects
        if obj.type == "ARMATURE"
    }
    bpy.ops.wm.save_as_mainfile(filepath=str(qa_path))
    return {
        "meshes": meshes,
        "armatures": armatures,
        "qa_blend": artifact(qa_path),
    }


def main() -> None:
    global REPORT_ROOT
    args = parse_args()
    output = args.output.resolve()
    REPORT_ROOT = repository_root(output)
    parent = load_parent_recipe(REPORT_ROOT)

    work = output / "work"
    source = output / "source"
    renders = output / "evidence" / "renders"
    exports = output / "exports"
    qa = output / "qa"
    for directory in (work, source, renders, exports, qa):
        directory.mkdir(parents=True, exist_ok=True)

    parent_source = Path(bpy.data.filepath).resolve()
    parent_hash = sha256(parent_source)
    if parent_hash != EXPECTED_PARENT_SHA256:
        raise RuntimeError(
            f"Unexpected parent hash {parent_hash}; expected "
            f"{EXPECTED_PARENT_SHA256}"
        )

    bpy.context.preferences.filepaths.save_version = 0
    checkpoints: dict[str, object] = {}
    checkpoints["00_r002_frozen_parent"] = save_checkpoint(
        work / "00_r002_frozen_parent.blend"
    )

    body = bpy.data.objects.get(BODY_OBJECT)
    rig = bpy.data.objects.get(RIG_OBJECT)
    eye_left = bpy.data.objects.get("FACE_EYE_L_MOBILE_PROXY")
    eye_right = bpy.data.objects.get("FACE_EYE_R_MOBILE_PROXY")
    blush_left = bpy.data.objects.get("FACE_BLUSH_L_STATIC_PROXY")
    blush_right = bpy.data.objects.get("FACE_BLUSH_R_STATIC_PROXY")
    if any(
        obj is None
        for obj in (
            body,
            rig,
            eye_left,
            eye_right,
            blush_left,
            blush_right,
        )
    ):
        raise RuntimeError("The frozen parent is missing a required object.")

    original_outside = outside_window_signature(body)
    original_bvh = parent.body_bvh(body)
    aperture = open_boundary(parent)
    outer_window = scale_boundary(aperture, 1.18, 1.20)
    remove_old_mouth_objects()
    apply_mouth_window_cut(
        body,
        outer_window,
        parent,
        original_bvh,
    )
    post_cut_outside = outside_window_signature(body)
    checkpoints["10_mouth_window_cut"] = save_checkpoint(
        work / "10_mouth_window_cut.blend"
    )

    model_collection = bpy.data.collections.get("20_FACIAL_PROOF_MODEL")
    if model_collection is None:
        raise RuntimeError("The parent model collection is missing.")
    body_material = body.data.materials[0]
    skin_transition = create_skin_transition(
        outer_window,
        aperture,
        original_bvh,
        parent,
        body_material,
        model_collection,
    )
    checkpoints["20_static_rounded_aperture"] = save_checkpoint(
        work / "20_static_rounded_aperture.blend"
    )

    cavity_material = make_material(
        "MAT_BENTOSAUR_MOUTH_CAVITY_R003",
        (0.030, 0.006, 0.012, 1.0),
        0.88,
    )
    tongue_material = make_material(
        "MAT_BENTOSAUR_TONGUE_CORAL_R003",
        (0.90, 0.18, 0.25, 1.0),
        0.68,
    )
    cavity_wall, back_boundary = create_cavity_wall(
        aperture,
        original_bvh,
        parent,
        cavity_material,
        model_collection,
    )
    cavity_back = create_cavity_back(
        back_boundary,
        original_bvh,
        parent,
        cavity_material,
        model_collection,
    )
    tongue = create_tongue(
        original_bvh,
        parent,
        tongue_material,
        model_collection,
    )
    checkpoints["30_static_cavity_and_tongue"] = save_checkpoint(
        work / "30_static_cavity_and_tongue.blend"
    )

    camera = configure_render(args.resolution)
    checkpoints["40_render_ready"] = save_checkpoint(
        work / "40_render_ready.blend"
    )
    render_report = {}
    for index, (view, closeup) in enumerate(
        (
            ("front", True),
            ("three_quarter", True),
            ("profile", True),
            ("front", False),
            ("three_quarter", False),
            ("profile", False),
        ),
        start=1,
    ):
        suffix = "close" if closeup else "full"
        key = f"{view}_{suffix}"
        render_report[key] = render(
            renders / f"{index:02d}_{view}_{suffix}.png",
            camera,
            view,
            closeup,
        )

    export_objects = (
        body,
        skin_transition,
        cavity_wall,
        cavity_back,
        tongue,
        eye_left,
        eye_right,
        blush_left,
        blush_right,
        rig,
    )
    topology_report = {
        obj.name: topology(obj)
        for obj in export_objects
        if obj.type == "MESH"
    }
    triangle_total = sum(
        item["triangles_after_export"]
        for item in topology_report.values()
    )
    glb_path = exports / "bentosaur_static_smooth_mouth_v003.glb"
    glb_report = export_glb(glb_path, export_objects)
    checkpoints["50_static_glb_export"] = save_checkpoint(
        work / "50_static_glb_export.blend"
    )
    source_path = source / "bentosaur_static_smooth_mouth_v003.blend"
    source_report = save_checkpoint(source_path)
    parent_unchanged = sha256(parent_source) == parent_hash
    round_trip = audit_round_trip(
        glb_path,
        qa / "60_static_glb_roundtrip.blend",
    )

    outside_preserved = (
        original_outside["vertex_count"]
        == post_cut_outside["vertex_count"]
        and original_outside["sha256"]
        == post_cut_outside["sha256"]
    )
    report = {
        "schema_version": "1.0.0",
        "status": "static_mouth_window_visual_gate_pending_mau_approval",
        "production_approved": False,
        "visual_approval_owner": "Mau",
        "paid_api_usage": {
            "used": False,
            "tripo_credits_spent": 0,
            "recorded_tripo_balance": 4695,
        },
        "parent": {
            "path": report_path(parent_source),
            "sha256": parent_hash,
            "unchanged_after_run": parent_unchanged,
        },
        "scope": {
            "body_outside_window_preserved": outside_preserved,
            "outside_window_before": original_outside,
            "outside_window_after": post_cut_outside,
            "changed": [
                "small duplicated-body mouth window",
                "flush skin-colored transition",
                "recessed cavity wall and back",
                "contained static tongue",
            ],
            "preserved": [
                "parent source",
                "proportions",
                "horns",
                "frill",
                "eyes",
                "blush",
                "armature",
            ],
        },
        "stage_gate": {
            "static_only": True,
            "morphs_added": False,
            "new_skinning_added": False,
            "next_step_requires_mau_approval": True,
            "acceptance_criteria": [
                "soft rounded mouth transition",
                "no body-colored leak or central notch",
                "no floating sticker in profile",
                "recessed dark cavity",
                "coral tongue contained inside the aperture",
            ],
        },
        "checkpoints": checkpoints,
        "renders": render_report,
        "source": source_report,
        "glb": glb_report,
        "mobile_budget": {
            "mesh_count": len(topology_report),
            "triangles_total_estimate": triangle_total,
            "topology": topology_report,
        },
        "round_trip": round_trip,
    }
    report_path_value = qa / "static_mouth_window_gate_report.json"
    report_path_value.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
