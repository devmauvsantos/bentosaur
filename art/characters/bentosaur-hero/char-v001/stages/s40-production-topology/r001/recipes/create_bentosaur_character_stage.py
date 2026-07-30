"""Create self-contained, versioned Bentosaur character stage sources.

This script only creates production source checkpoints. It never overwrites an
existing .blend and it never changes the historical visual-gate artifacts.

Stages:

S20
    Import and pack the immutable H3.1 Extreme visual source.
S30
    Standardize the repaired Smart LowPoly scaffold and include a locked high
    source for direct comparison.
S40
    Branch the production-topology workfile. Normalize orientation/scale,
    preserve locked high and scaffold collections, append the useful separate
    face/mouth research pieces, and create an editable body WIP object.

Example:

    /Applications/Blender.app/Contents/MacOS/Blender \
      --background --factory-startup \
      --python tools/blender/create_bentosaur_character_stage.py -- \
      --stage S40 \
      --high-source /absolute/model.glb \
      --scaffold-source /absolute/cycle_patch_candidate.blend \
      --face-source /absolute/mouth_diagnostic.blend \
      --output /absolute/bentosaur_hero_s40_production_topology_r001.blend
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector


FACE_REFERENCE_NAMES = {
    "FACE_CHEEK_LEFT_SEPARATE",
    "FACE_CHEEK_RIGHT_SEPARATE",
    "FACE_CONFORMAL_LIP_REPAIR_RING_SAME_MASTER",
    "FACE_EYE_LEFT_SEPARATE",
    "FACE_EYE_RIGHT_SEPARATE",
    "FACE_MOUTH_BAG_AND_LIP_LOOPS_SAME_MASTER",
    "FACE_TONGUE_SEPARATE_SAME_MASTER",
    "HELPER_NON_DESTRUCTIVE_MOUTH_APERTURE_CUTTER",
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=("S20", "S30", "S40"))
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd()
    )
    parser.add_argument("--high-source", required=True, type=Path)
    parser.add_argument("--scaffold-source", type=Path)
    parser.add_argument("--face-source", type=Path)
    parser.add_argument(
        "--work-mesh-source",
        type=Path,
        help=(
            "Optional S40 topology-bootstrap .blend. When supplied, its "
            "single mesh becomes the editable WIP instead of duplicating "
            "the repaired scaffold."
        ),
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--character-id", default="bentosaur-hero")
    parser.add_argument("--character-version", default="char-v001")
    parser.add_argument("--revision", default="r001")
    parser.add_argument("--target-height", type=float, default=1.0)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def portable_path(path: Path, project_root: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def validate_args(args: argparse.Namespace) -> None:
    if args.output.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing stage source: {args.output}"
        )
    if not args.high_source.is_file():
        raise FileNotFoundError(args.high_source)
    if args.stage in {"S30", "S40"}:
        if args.scaffold_source is None or not args.scaffold_source.is_file():
            raise FileNotFoundError(
                args.scaffold_source or "--scaffold-source is required"
            )
    if args.stage == "S40":
        if args.face_source is None or not args.face_source.is_file():
            raise FileNotFoundError(
                args.face_source or "--face-source is required"
            )
    if args.target_height <= 0.0:
        raise ValueError("--target-height must be positive")
    for source in (
        args.high_source,
        args.scaffold_source,
        args.face_source,
        args.work_mesh_source,
        args.output,
    ):
        if source is not None:
            portable_path(source, args.project_root)


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
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def mark_locked(
    obj: bpy.types.Object,
    *,
    role: str,
    render: bool,
    display_type: str = "TEXTURED",
) -> None:
    obj["bentosaur_pipeline_role"] = role
    obj["bentosaur_source_locked"] = True
    obj.hide_select = True
    obj.hide_render = not render
    obj.display_type = display_type


def import_high_source(
    source: Path, collection: bpy.types.Collection
) -> list[bpy.types.Object]:
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = [
        obj for obj in bpy.context.scene.objects if obj not in before
    ]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("H3.1 high source contains no mesh objects")
    for index, obj in enumerate(imported, start=1):
        link_exclusively(obj, collection)
        obj.name = (
            f"SRC_H31_HIGH_LOCKED_{index:02d}"
            if obj.type == "MESH"
            else f"SRC_H31_HIGH_{obj.type}_{index:02d}"
        )
        mark_locked(
            obj,
            role="immutable_h31_high_visual_source",
            render=False,
            display_type="WIRE",
        )
    return meshes


def append_objects(
    blend_path: Path,
    names: set[str] | None = None,
) -> list[bpy.types.Object]:
    with bpy.data.libraries.load(str(blend_path), link=False) as (
        data_from,
        data_to,
    ):
        if names is None:
            selected = list(data_from.objects)
        else:
            selected = [
                name for name in data_from.objects if name in names
            ]
        data_to.objects = selected
    return [obj for obj in data_to.objects if obj is not None]


def append_scaffold(
    source: Path, collection: bpy.types.Collection
) -> bpy.types.Object:
    meshes = [
        obj for obj in append_objects(source) if obj.type == "MESH"
    ]
    if len(meshes) != 1:
        raise RuntimeError(
            f"Expected one scaffold mesh in {source}, found {len(meshes)}"
        )
    scaffold = meshes[0]
    collection.objects.link(scaffold)
    scaffold.name = "SRC_H31_SMART_LOWPOLY_REPAIRED_LOCKED"
    mark_locked(
        scaffold,
        role="approved_bounded_retopology_scaffold",
        render=True,
    )
    return scaffold


def append_face_research(
    source: Path, collection: bpy.types.Collection
) -> list[bpy.types.Object]:
    objects = append_objects(source, FACE_REFERENCE_NAMES)
    missing = FACE_REFERENCE_NAMES - {obj.name for obj in objects}
    if missing:
        raise RuntimeError(
            f"Face source is missing expected objects: {sorted(missing)}"
        )
    for obj in objects:
        collection.objects.link(obj)
        obj.name = f"REF_{obj.name}"
        mark_locked(
            obj,
            role="face_system_research_reference_not_final",
            render=True,
        )
    return objects


def evaluated_world_bounds(
    objects: list[bpy.types.Object],
) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        for corner in obj.bound_box
    ]
    if not points:
        raise RuntimeError("Cannot calculate bounds without objects")
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


def production_transform(
    high_objects: list[bpy.types.Object], target_height: float
) -> tuple[Matrix, dict[str, object]]:
    source_minimum, source_maximum = evaluated_world_bounds(high_objects)
    source_height = source_maximum.z - source_minimum.z
    if source_height <= 0.0:
        raise RuntimeError("High source has invalid height")
    scale = target_height / source_height
    rotate = Matrix.Rotation(math.radians(-90.0), 4, "Z")
    scale_matrix = Matrix.Diagonal((scale, scale, scale, 1.0))
    preliminary = scale_matrix @ rotate

    transformed_corners = [
        preliminary @ (obj.matrix_world @ Vector(corner))
        for obj in high_objects
        for corner in obj.bound_box
    ]
    minimum = Vector(
        (
            min(point.x for point in transformed_corners),
            min(point.y for point in transformed_corners),
            min(point.z for point in transformed_corners),
        )
    )
    maximum = Vector(
        (
            max(point.x for point in transformed_corners),
            max(point.y for point in transformed_corners),
            max(point.z for point in transformed_corners),
        )
    )
    shift = Matrix.Translation(
        Vector((-(minimum.x + maximum.x) * 0.5, 0.0, -minimum.z))
    )
    matrix = shift @ preliminary
    return matrix, {
        "source_bounds_minimum": list(source_minimum),
        "source_bounds_maximum": list(source_maximum),
        "source_height": source_height,
        "rotation_degrees_z": -90.0,
        "uniform_scale": scale,
        "target_height": target_height,
        "floor_shift_z": -minimum.z,
        "symmetry_center_shift_x": -(minimum.x + maximum.x) * 0.5,
    }


def bake_transform_into_mesh(
    obj: bpy.types.Object, shared_transform: Matrix
) -> None:
    if obj.type != "MESH":
        obj.matrix_world = shared_transform @ obj.matrix_world
        return
    obj.data = obj.data.copy()
    obj.data.transform(shared_transform @ obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    obj.data.update()


def duplicate_retopology_wip(
    scaffold: bpy.types.Object,
    collection: bpy.types.Collection,
    revision: str,
) -> bpy.types.Object:
    body = scaffold.copy()
    body.data = scaffold.data.copy()
    body.animation_data_clear()
    body.name = f"BENTOSAUR_BODY_RETOPO_WIP_{revision.upper()}"
    body.hide_select = False
    body.hide_render = False
    body.display_type = "TEXTURED"
    for key in list(body.keys()):
        if key not in {"_RNA_UI"}:
            del body[key]
    body["bentosaur_pipeline_role"] = "production_topology_work_mesh"
    body["production_topology_state"] = "wip_requires_manual_rebuild"
    body["required_rebuild_regions"] = json.dumps(
        [
            "mouth_and_facial_mask",
            "shoulders_and_armpits",
            "elbow_bend_bands",
            "pelvis_and_groin",
            "knee_bend_bands",
        ]
    )
    body["preserve_and_clean_regions"] = json.dumps(
        ["tail", "frill", "head_back", "static_silhouette"]
    )
    collection.objects.link(body)
    return body


def append_retopology_wip(
    source: Path,
    collection: bpy.types.Collection,
    revision: str,
) -> bpy.types.Object:
    meshes = [
        obj for obj in append_objects(source) if obj.type == "MESH"
    ]
    if len(meshes) != 1:
        raise RuntimeError(
            f"Expected one topology bootstrap mesh in {source}, "
            f"found {len(meshes)}"
        )
    body = meshes[0]
    collection.objects.link(body)
    body.name = f"BENTOSAUR_BODY_RETOPO_WIP_{revision.upper()}"
    body.hide_select = False
    body.hide_render = False
    body.display_type = "TEXTURED"
    body["bentosaur_pipeline_role"] = "production_topology_work_mesh"
    body["production_topology_state"] = (
        "hybrid_quadriflow_bootstrap_requires_authored_cleanup"
    )
    body["required_rebuild_regions"] = json.dumps(
        [
            "center_strip",
            "mouth_and_facial_mask",
            "shoulder_loop_routing_review",
            "elbow_bend_band_review",
            "pelvis_and_groin_loop_routing_review",
            "knee_bend_band_review",
        ]
    )
    body["preserve_and_clean_regions"] = json.dumps(
        ["limbs", "torso_panels", "head_back", "tail"]
    )
    return body


def configure_scene(stage: str) -> None:
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene["character_pipeline_stage"] = stage
    scene["human_visual_approval_owner"] = "Mau"
    scene["assistant_may_grant_visual_approval"] = False
    scene["runtime_export_allowed"] = False
    scene["rigging_allowed"] = False


def embed_manifest_text(payload: dict[str, object]) -> None:
    text = bpy.data.texts.new("BENTOSAUR_PIPELINE_STAGE.json")
    text.write(json.dumps(payload, indent=2, sort_keys=True))
    text["do_not_store_credentials"] = True


def main() -> None:
    args = parse_args()
    validate_args(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    clear_scene()
    configure_scene(args.stage)

    high_collection = make_collection("00_HIGH_VISUAL_SOURCE_LOCKED")
    high_objects = import_high_source(args.high_source, high_collection)
    stage_payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "character_id": args.character_id,
        "character_version": args.character_version,
        "stage": args.stage,
        "revision": args.revision,
        "blender_version": bpy.app.version_string,
        "sources": {
            "high": {
                "path": portable_path(
                    args.high_source, args.project_root
                ),
                "sha256": sha256(args.high_source),
            }
        },
    }

    if args.stage == "S20":
        high_collection.name = "00_H31_EXTREME_VISUAL_SOURCE_LOCKED"
        for obj in high_objects:
            obj.hide_render = False
            obj.display_type = "TEXTURED"
        bpy.context.scene["stage_state"] = "frozen"
        bpy.context.scene["rigging_allowed"] = False

    scaffold = None
    if args.stage in {"S30", "S40"}:
        scaffold_collection = make_collection(
            "10_RETOPO_SCAFFOLD_LOCKED"
        )
        scaffold = append_scaffold(
            args.scaffold_source, scaffold_collection
        )
        stage_payload["sources"]["scaffold"] = {
            "path": portable_path(
                args.scaffold_source, args.project_root
            ),
            "sha256": sha256(args.scaffold_source),
        }
        bpy.context.scene["stage_state"] = (
            "frozen" if args.stage == "S30" else "wip"
        )

    if args.stage == "S30":
        high_collection.hide_viewport = True
        scaffold.hide_select = True
        bpy.context.scene["scaffold_scope"] = (
            "approved_only_as_bounded_retopology_scaffold"
        )

    if args.stage == "S40":
        face_collection = make_collection("20_FACE_RESEARCH_LOCKED")
        face_objects = append_face_research(
            args.face_source, face_collection
        )
        stage_payload["sources"]["face_research"] = {
            "path": portable_path(
                args.face_source, args.project_root
            ),
            "sha256": sha256(args.face_source),
        }
        if args.work_mesh_source is not None:
            stage_payload["sources"]["topology_bootstrap"] = {
                "path": portable_path(
                    args.work_mesh_source, args.project_root
                ),
                "sha256": sha256(args.work_mesh_source),
            }
        transform, transform_report = production_transform(
            high_objects, args.target_height
        )
        work_collection = make_collection("30_PRODUCTION_TOPOLOGY_WIP")
        if args.work_mesh_source is None:
            body = duplicate_retopology_wip(
                scaffold, work_collection, args.revision
            )
        else:
            body = append_retopology_wip(
                args.work_mesh_source,
                work_collection,
                args.revision,
            )
        for obj in [
            *high_objects,
            scaffold,
            *face_objects,
            body,
        ]:
            bake_transform_into_mesh(obj, transform)
        stage_payload["production_normalization"] = transform_report
        high_collection.hide_viewport = True
        scaffold.hide_render = True
        scaffold.display_type = "WIRE"
        face_collection.hide_render = True

        body["source_stage"] = "S30/r001"
        body["normalized_front_axis"] = "-Y"
        body["normalized_up_axis"] = "+Z"
        body["normalized_character_left_axis"] = "+X"
        body["normalization_applied"] = True
        bpy.context.scene["production_front_axis"] = "-Y"
        bpy.context.scene["production_up_axis"] = "+Z"
        bpy.context.scene["production_symmetry_plane"] = "local X = 0"
        bpy.context.scene["next_required_gate"] = (
            "G40_DEFORMATION_TOPOLOGY"
        )

        guides = make_collection("90_GUIDES")
        bpy.ops.object.empty_add(
            type="PLAIN_AXES", location=(0.0, 0.0, 0.0)
        )
        origin = bpy.context.object
        origin.name = "GUIDE_ORIGIN_FEET_FLOOR"
        origin.empty_display_size = 0.1
        link_exclusively(origin, guides)

    embed_manifest_text(stage_payload)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(
        filepath=str(args.output), check_existing=False
    )
    print(
        "BENTOSAUR_STAGE_RESULT="
        + json.dumps(
            {
                "stage": args.stage,
                "output": portable_path(
                    args.output, args.project_root
                ),
                "sha256": sha256(args.output),
                "bytes": args.output.stat().st_size,
                "objects": len(bpy.data.objects),
                "meshes": len(bpy.data.meshes),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
