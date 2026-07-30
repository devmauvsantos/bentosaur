"""Narrow deformation confirmation for canonical S40 r003.

This script is intentionally independent from the rejected zero-motion fallback
probe. It extracts only BENTOSAUR_BODY_RETOPO_WIP_R003 from the canonical stage,
uses the locked -Y-front/+X-left/+Z-up contract, preserves checkpoints, runs one
automatic-weight baseline plus one minimal normalization/leak cleanup, and
evaluates five fixed stress poses. It does not polish or approve a rig.
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/.tmp/subagents/"
    "deformation_rig_probe/r003-confirmation"
)
PARENT = ROOT.parent
sys.path.insert(0, str(PARENT))

import run_deformation_rig_probe as probe
import align_rig_and_weights_v4 as v4


SOURCE_PATH = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/art/characters/"
    "bentosaur-hero/char-v001/stages/s40-production-topology/r003/"
    "source/bentosaur_hero_s40_production_topology_r003.blend"
)
SOURCE_SHA256 = (
    "181d93014f1667d9044d12e24fa297f4b391c9eb8d1164ddc5f45f3971f7caf9"
)
SOURCE_OBJECT = "BENTOSAUR_BODY_RETOPO_WIP_R003"
STAGES = ROOT / "stages"
RENDERS = ROOT / "renders"
Z_OFFSET = 0.4906151294708252


def old_point_to_canonical(value: tuple[float, float, float]) -> Vector:
    old = Vector(value)
    return Vector((old.y, -old.x, old.z + Z_OFFSET))


def old_direction_to_canonical(value: Vector) -> Vector:
    return Vector((value.y, -value.x, value.z))


def canonical_to_old(point: Vector) -> Vector:
    return Vector((-point.y, point.x, point.z - Z_OFFSET))


def canonical_bone_specs() -> dict:
    old = copy.deepcopy(probe.BONES)
    for name, (head, tail) in v4.CORRECTED_BONES.items():
        old[name]["head"] = head
        old[name]["tail"] = tail
    result = {}
    for name, spec in old.items():
        result[name] = {
            **spec,
            "head": tuple(old_point_to_canonical(spec["head"])),
            "tail": tuple(old_point_to_canonical(spec["tail"])),
        }
    return result


BONES = canonical_bone_specs()
POSES = [
    ("neutral", "40_pose_neutral.blend"),
    ("reach_tray_hold", "50_pose_reach_tray_hold.blend"),
    ("squat", "60_pose_squat.blend"),
    ("walk_extreme", "70_pose_walk_extreme.blend"),
    ("tail_bend", "80_pose_tail_bend.blend"),
]


def save_stage(filename: str) -> str:
    path = STAGES / filename
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {path}")
    bpy.ops.wm.save_as_mainfile(filepath=str(path), check_existing=False)
    return path.as_posix()


def isolate_body() -> bpy.types.Object:
    target = bpy.data.objects.get(SOURCE_OBJECT)
    if target is None or target.type != "MESH":
        raise RuntimeError(f"Canonical body not found: {SOURCE_OBJECT}")
    for obj in list(bpy.data.objects):
        if obj != target:
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if target.name not in collection.objects:
            bpy.data.collections.remove(collection)
    if not target.users_collection:
        bpy.context.scene.collection.objects.link(target)
    for material in list(bpy.data.materials):
        if material.users == 0:
            bpy.data.materials.remove(material)
    for image in list(bpy.data.images):
        if image.users == 0:
            bpy.data.images.remove(image)
    target.name = probe.BODY_NAME
    target.data.name = f"{probe.BODY_NAME}_R003_MESH"
    target["diagnostic_only"] = True
    target["canonical_source_object"] = SOURCE_OBJECT
    target["coordinate_contract"] = "front -Y; left +X; up +Z; floor Z=0"
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.view_layer.update()
    return target


def create_armature() -> bpy.types.Object:
    data = bpy.data.armatures.new(f"{probe.RIG_NAME}_R003_DATA")
    armature = bpy.data.objects.new(probe.RIG_NAME, data)
    bpy.context.scene.collection.objects.link(armature)
    armature.show_in_front = True
    armature["diagnostic_only"] = True
    armature["coordinate_contract"] = "front -Y; left +X; up +Z"

    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="EDIT")
    for name, spec in BONES.items():
        bone = data.edit_bones.new(name)
        bone.head = Vector(spec["head"])
        bone.tail = Vector(spec["tail"])
        bone.use_deform = spec.get("deform", True)
    for name, spec in BONES.items():
        parent = spec.get("parent")
        if parent:
            bone = data.edit_bones[name]
            bone.parent = data.edit_bones[parent]
            bone.use_connect = spec.get("connected", False)
    bpy.ops.object.mode_set(mode="OBJECT")
    return armature


def mirror_audit(body: bpy.types.Object) -> dict:
    points = [body.matrix_world @ vertex.co for vertex in body.data.vertices]
    tree = KDTree(len(points))
    for index, point in enumerate(points):
        tree.insert(point, index)
    tree.balance()
    errors = sorted(
        tree.find(Vector((-point.x, point.y, point.z)))[2]
        for point in points
    )
    index = max(0, math.ceil(len(errors) * 0.95) - 1)
    return {
        "plane": "X=0",
        "within_1e_6_ratio": (
            sum(error <= 1.0e-6 for error in errors) / len(errors)
        ),
        "p95": errors[index],
        "maximum": max(errors),
    }


def bounds(body: bpy.types.Object) -> dict:
    points = [body.matrix_world @ vertex.co for vertex in body.data.vertices]
    minimum = Vector(
        min(point[axis] for point in points) for axis in range(3)
    )
    maximum = Vector(
        max(point[axis] for point in points) for axis in range(3)
    )
    tail = [
        point for point in points if point.y > 0.08 and point.z < 0.45
    ]
    front = [
        point for point in points if point.y < -0.08 and point.z > 0.45
    ]
    return {
        "minimum": list(minimum),
        "maximum": list(maximum),
        "dimensions": list(maximum - minimum),
        "floor_absolute_error": abs(minimum.z),
        "tail_region": {
            "count": len(tail),
            "mean_y": sum(point.y for point in tail) / len(tail),
            "maximum_y": max(point.y for point in tail),
        },
        "front_head_region": {
            "count": len(front),
            "mean_y": sum(point.y for point in front) / len(front),
            "minimum_y": min(point.y for point in front),
        },
    }


def nearest_deform_bone(
    point: Vector, armature: bpy.types.Object
) -> str:
    scored = []
    for bone in armature.data.bones:
        if not bone.use_deform:
            continue
        distance, _t = probe.point_segment_distance(
            point, bone.head_local, bone.tail_local
        )
        scored.append((distance, bone.name))
    return min(scored)[1]


def minimal_weight_cleanup(
    body: bpy.types.Object, armature: bpy.types.Object
) -> dict:
    names = {group.index: group.name for group in body.vertex_groups}
    deform = {
        bone.name for bone in armature.data.bones if bone.use_deform
    }
    assignments = []
    counters = {
        "head_core_locked": 0,
        "cross_side_removed": 0,
        "tail_leak_removed": 0,
        "fallback_nearest_bone": 0,
        "capped_or_normalized": 0,
    }
    for vertex in body.data.vertices:
        point = body.matrix_world @ vertex.co
        weights = {
            names[element.group]: element.weight
            for element in vertex.groups
            if names.get(element.group) in deform
            and element.weight > 1.0e-6
        }
        # The lower frill is part of the rigid head mass. Bone heat otherwise
        # assigns its side lobes to the nearby upper-arm bones, which creates a
        # false shoulder failure before the limb topology is even exercised.
        if point.z > 0.54 or (
            point.y < -0.17 and point.z > 0.47
        ):
            weights = {"head": 1.0}
            counters["head_core_locked"] += 1
        else:
            before = set(weights)
            if point.x > 0.015:
                weights = {
                    name: value
                    for name, value in weights.items()
                    if not name.endswith(".R")
                }
            elif point.x < -0.015:
                weights = {
                    name: value
                    for name, value in weights.items()
                    if not name.endswith(".L")
                }
            if set(weights) != before:
                counters["cross_side_removed"] += 1

            before = set(weights)
            if point.y < 0.025 or point.z > 0.52:
                weights = {
                    name: value
                    for name, value in weights.items()
                    if not name.startswith("tail_")
                }
            if set(weights) != before:
                counters["tail_leak_removed"] += 1
        original = dict(weights)
        weights = probe.normalize_weights(weights)
        if not weights:
            weights = {nearest_deform_bone(point, armature): 1.0}
            counters["fallback_nearest_bone"] += 1
        if len(original) > 4 or abs(sum(original.values()) - 1.0) > 1.0e-5:
            counters["capped_or_normalized"] += 1
        assignments.append(weights)

    for group in list(body.vertex_groups):
        body.vertex_groups.remove(group)
    groups = {
        name: body.vertex_groups.new(name=name) for name in sorted(deform)
    }
    for index, weights in enumerate(assignments):
        for name, weight in weights.items():
            groups[name].add([index], weight, "REPLACE")
    body["r003_confirmation_weight_cleanup"] = (
        "Single minimal pass only: lock head core, remove opposite-side and "
        "impossible tail leakage, normalize/cap four, nearest-bone fallback."
    )
    bpy.context.view_layer.update()
    return {
        "operations": counters,
        "stats": probe.weight_stats(body),
    }


def rest_head(armature: bpy.types.Object, name: str) -> Vector:
    return armature.data.bones[name].head_local.copy()


def rest_direction(armature: bpy.types.Object, name: str) -> Vector:
    bone = armature.data.bones[name]
    return bone.tail_local - bone.head_local


def translate_axial(
    armature: bpy.types.Object, delta: Vector
) -> None:
    for name in ["pelvis", "spine", "chest", "neck", "head"]:
        probe.set_absolute_bone(
            armature,
            name,
            rest_head(armature, name) + delta,
            rest_direction(armature, name),
        )


def rest_arm(
    armature: bpy.types.Object, side: str, delta: Vector
) -> None:
    upper = f"upper_arm.{side}"
    lower = f"forearm.{side}"
    hand = f"hand.{side}"
    elbow = probe.set_absolute_bone(
        armature,
        upper,
        rest_head(armature, upper) + delta,
        rest_direction(armature, upper),
    )
    wrist = probe.set_absolute_bone(
        armature, lower, elbow, rest_direction(armature, lower)
    )
    probe.set_absolute_bone(
        armature, hand, wrist, rest_direction(armature, hand)
    )


def apply_pose(
    armature: bpy.types.Object, pose_name: str
) -> None:
    probe.reset_pose(armature)
    if pose_name == "neutral":
        return
    if pose_name == "reach_tray_hold":
        for side, sign in (("L", 1.0), ("R", -1.0)):
            upper = f"upper_arm.{side}"
            lower = f"forearm.{side}"
            hand = f"hand.{side}"
            elbow = probe.set_absolute_bone(
                armature,
                upper,
                rest_head(armature, upper),
                old_direction_to_canonical(
                    Vector((0.73, -0.44 * sign, -0.52))
                ),
            )
            wrist = probe.set_absolute_bone(
                armature,
                lower,
                elbow,
                old_direction_to_canonical(
                    Vector((0.82, -0.50 * sign, 0.04))
                ),
            )
            probe.set_absolute_bone(
                armature,
                hand,
                wrist,
                old_direction_to_canonical(
                    Vector((0.99, -0.08 * sign, 0.02))
                ),
            )
        return
    if pose_name == "squat":
        delta = Vector((0.0, 0.0, -0.045))
        translate_axial(armature, delta)
        for side, sign in (("L", 1.0), ("R", -1.0)):
            rest_arm(armature, side, delta)
            thigh = f"thigh.{side}"
            shin = f"shin.{side}"
            foot = f"foot.{side}"
            knee = probe.set_absolute_bone(
                armature,
                thigh,
                rest_head(armature, thigh) + delta,
                old_direction_to_canonical(
                    Vector((0.48, 0.14 * sign, -0.87))
                ),
            )
            ankle = probe.set_absolute_bone(
                armature,
                shin,
                knee,
                old_direction_to_canonical(
                    Vector((-0.18, -0.03 * sign, -0.98))
                ),
            )
            probe.set_absolute_bone(
                armature,
                foot,
                ankle,
                old_direction_to_canonical(Vector((0.99, 0.0, -0.08))),
            )
        return
    if pose_name == "walk_extreme":
        directions = {
            "L": (
                Vector((0.60, 0.03, -0.80)),
                Vector((-0.10, 0.00, -1.00)),
                Vector((-0.56, 0.04, -0.83)),
                Vector((-0.35, -0.03, -0.94)),
            ),
            "R": (
                Vector((-0.48, -0.03, -0.88)),
                Vector((0.20, 0.00, -0.98)),
                Vector((0.65, -0.04, -0.76)),
                Vector((0.42, 0.03, -0.91)),
            ),
        }
        for side in ("L", "R"):
            thigh_dir, shin_dir, upper_dir, forearm_dir = directions[side]
            thigh = f"thigh.{side}"
            shin = f"shin.{side}"
            foot = f"foot.{side}"
            knee = probe.set_absolute_bone(
                armature,
                thigh,
                rest_head(armature, thigh),
                old_direction_to_canonical(thigh_dir),
            )
            ankle = probe.set_absolute_bone(
                armature,
                shin,
                knee,
                old_direction_to_canonical(shin_dir),
            )
            probe.set_absolute_bone(
                armature,
                foot,
                ankle,
                old_direction_to_canonical(Vector((0.99, 0.0, -0.08))),
            )
            upper = f"upper_arm.{side}"
            lower = f"forearm.{side}"
            hand = f"hand.{side}"
            elbow = probe.set_absolute_bone(
                armature,
                upper,
                rest_head(armature, upper),
                old_direction_to_canonical(upper_dir),
            )
            wrist = probe.set_absolute_bone(
                armature,
                lower,
                elbow,
                old_direction_to_canonical(forearm_dir),
            )
            probe.set_absolute_bone(
                armature,
                hand,
                wrist,
                old_direction_to_canonical(forearm_dir),
            )
        return
    if pose_name == "tail_bend":
        old_directions = [
            Vector((-0.96, 0.20, 0.02)),
            Vector((-0.82, 0.56, 0.05)),
            Vector((-0.60, 0.78, 0.08)),
            Vector((-0.36, 0.92, 0.08)),
            Vector((-0.12, 0.99, 0.02)),
        ]
        head = rest_head(armature, "tail_01")
        for index, direction in enumerate(old_directions, start=1):
            head = probe.set_absolute_bone(
                armature,
                f"tail_{index:02d}",
                head,
                old_direction_to_canonical(direction),
            )
        return
    raise ValueError(pose_name)


OLD_REGION_CLASSIFIER = probe.classify_region


def canonical_region(point: Vector) -> str:
    return OLD_REGION_CLASSIFIER(canonical_to_old(point))


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


def ensure_render_scene(body: bpy.types.Object) -> bpy.types.Object:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.color = (0.018, 0.027, 0.050)
    scene.view_settings.look = "AgX - Medium High Contrast"

    body.data.materials.clear()
    body.data.materials.append(
        probe.material(
            "R003_CONFIRMATION_GREEN", (0.24, 0.49, 0.39, 1.0)
        )
    )
    for polygon in body.data.polygons:
        polygon.use_smooth = True

    camera_data = bpy.data.cameras.get("R003_CONFIRM_CAMERA_DATA")
    if camera_data is None:
        camera_data = bpy.data.cameras.new("R003_CONFIRM_CAMERA_DATA")
    camera = bpy.data.objects.get("R003_CONFIRM_CAMERA")
    if camera is None:
        camera = bpy.data.objects.new("R003_CONFIRM_CAMERA", camera_data)
        scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1.30
    scene.camera = camera

    if bpy.data.objects.get("R003_CONFIRM_FLOOR") is None:
        bpy.ops.mesh.primitive_plane_add(
            size=3.0, location=(0.0, 0.0, -0.003)
        )
        floor = bpy.context.object
        floor.name = "R003_CONFIRM_FLOOR"
        floor.data.materials.append(
            probe.material(
                "R003_CONFIRM_FLOOR_MATERIAL",
                (0.035, 0.055, 0.085, 1.0),
            )
        )

    for name, location, energy, size in [
        ("R003_KEY", (1.8, -2.3, 2.4), 900.0, 3.0),
        ("R003_FILL", (-2.0, -0.3, 1.6), 600.0, 2.0),
    ]:
        if bpy.data.objects.get(name) is None:
            light_data = bpy.data.lights.new(f"{name}_DATA", "AREA")
            light_data.energy = energy
            light_data.shape = "DISK"
            light_data.size = size
            light = bpy.data.objects.new(name, light_data)
            light.location = location
            scene.collection.objects.link(light)
            look_at(light, Vector((0.0, 0.0, 0.48)))
    return camera


def render_pose(
    body: bpy.types.Object,
    armature: bpy.types.Object,
    pose_name: str,
) -> dict:
    probe.build_evidence_overlay(body, armature)
    camera = ensure_render_scene(body)
    output = RENDERS / pose_name
    output.mkdir(parents=True, exist_ok=False)
    views = {
        "front_three_quarter": Vector((1.55, -1.80, 1.05)),
        "front": Vector((0.0, -2.25, 0.52)),
        "side": Vector((2.25, 0.0, 0.52)),
    }
    results = {}
    for name, location in views.items():
        camera.location = location
        look_at(camera, Vector((0.0, 0.0, 0.48)))
        path = output / f"{name}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        results[name] = path.as_posix()
    return results


def main() -> None:
    STAGES.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    body = isolate_body()
    source_topology = probe.mesh_topology(body)
    coordinate_audit = {
        "contract": {
            "front": "-Y",
            "character_left": "+X",
            "up": "+Z",
            "floor": "Z=0",
        },
        "bounds_and_morphology": bounds(body),
        "mirror": mirror_audit(body),
    }
    stage_05 = save_stage("05_body_only_snapshot.blend")

    armature = create_armature()
    stage_10 = save_stage("10_neutral_armature_no_weights.blend")

    automatic = probe.automatic_parent(body, armature)
    stage_20 = save_stage("20_automatic_weights.blend")

    cleanup = minimal_weight_cleanup(body, armature)
    stage_30 = save_stage("30_minimal_confirmation_weights.blend")

    probe.reset_pose(armature)
    baseline_points, baseline_mesh = probe.evaluated_world_vertices(body)
    probe.classify_region = canonical_region
    poses = {}
    for pose_name, filename in POSES:
        apply_pose(armature, pose_name)
        bpy.context.view_layer.update()
        metrics = probe.deformation_metrics(
            body, baseline_points, baseline_mesh
        )
        renders = render_pose(body, armature, pose_name)
        stage = save_stage(filename)
        flags = probe.collapse_summary(metrics)
        poses[pose_name] = {
            "stage": stage,
            "renders": renders,
            "regions": metrics,
            "threshold_flags": flags,
            "diagnostic_pass": len(flags) == 0,
        }
        probe.clear_evidence_overlay()
    bpy.data.meshes.remove(baseline_mesh)
    failing = [
        name
        for name, result in poses.items()
        if not result["diagnostic_pass"]
    ]
    report = {
        "schema_version": "1.0.0",
        "diagnostic_only": True,
        "candidate": "S40_r003_axis_qf_winner",
        "fallback_result_applies_to_this_candidate": False,
        "source": {
            "canonical_blend": SOURCE_PATH.as_posix(),
            "canonical_sha256": SOURCE_SHA256,
            "canonical_object": SOURCE_OBJECT,
            "topology": source_topology,
        },
        "coordinate_audit": coordinate_audit,
        "checkpoints": {
            "body_only": stage_05,
            "neutral_armature": stage_10,
            "automatic_weights": stage_20,
            "minimal_confirmation_weights": stage_30,
        },
        "weights": {
            "automatic": automatic,
            "minimal_cleanup": cleanup,
            "polish_iterations": 0,
        },
        "poses": poses,
        "verdict": {
            "r003_confirmation_pass": len(failing) == 0,
            "failing_poses": failing,
            "topology_approval": False,
            "rig_approval": False,
            "scope": (
                "Confirmation only: whether promoted r003 reproduces gross "
                "shoulder/hip/knee/tail deformation failures."
            ),
        },
    }
    (ROOT / "r003_confirmation_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print("R003_CONFIRMATION=" + json.dumps(report["verdict"]))


if __name__ == "__main__":
    main()
