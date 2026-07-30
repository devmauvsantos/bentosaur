"""Build and stress-test a temporary Bentosaur deformation rig.

This is deliberately isolated diagnostic work. It does not modify production
assets and it does not claim a final rig, animation set, or topology approval.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


PROBE_ROOT = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/"
    ".tmp/subagents/deformation_rig_probe"
)
STAGES = PROBE_ROOT / "stages"
RENDERS = PROBE_ROOT / "renders"

SOURCE_MESH_NAME = "BENTOSAUR_BOOTSTRAP_SYMMETRIZED_NEGATIVE_Y_NOT_APPROVED"
BODY_NAME = "BENTOSAUR_DEFORMATION_PROBE_BODY"
RIG_NAME = "BENTOSAUR_DEFORMATION_PROBE_RIG"
OVERLAY_COLLECTION = "EVIDENCE_OVERLAY"

# This is the observed coordinate system of the source geometry, not the
# coordinate contract currently written in the production manifest.
FRONT = Vector((1.0, 0.0, 0.0))
BACK = Vector((-1.0, 0.0, 0.0))
LEFT = Vector((0.0, 1.0, 0.0))
RIGHT = Vector((0.0, -1.0, 0.0))
UP = Vector((0.0, 0.0, 1.0))


BONES = {
    "root": {
        "head": (0.0, 0.0, -0.490),
        "tail": (0.0, 0.0, -0.400),
        "parent": None,
        "deform": False,
    },
    "pelvis": {
        "head": (-0.035, 0.0, -0.285),
        "tail": (-0.020, 0.0, -0.185),
        "parent": "root",
    },
    "spine": {
        "head": (-0.020, 0.0, -0.185),
        "tail": (-0.005, 0.0, -0.060),
        "parent": "pelvis",
        "connected": True,
    },
    "chest": {
        "head": (-0.005, 0.0, -0.060),
        "tail": (0.015, 0.0, 0.090),
        "parent": "spine",
        "connected": True,
    },
    "neck": {
        "head": (0.015, 0.0, 0.090),
        "tail": (0.030, 0.0, 0.155),
        "parent": "chest",
        "connected": True,
    },
    "head": {
        "head": (0.030, 0.0, 0.155),
        "tail": (0.110, 0.0, 0.405),
        "parent": "neck",
        "connected": True,
    },
    # Placeholder only: non-deforming because this body source has no approved
    # interior mouth, jaw loop, or facial topology.
    "jaw_placeholder": {
        "head": (0.205, 0.0, 0.195),
        "tail": (0.345, 0.0, 0.195),
        "parent": "head",
        "deform": False,
    },
    "upper_arm.L": {
        "head": (0.025, 0.175, 0.055),
        "tail": (0.060, 0.270, -0.020),
        "parent": "chest",
    },
    "forearm.L": {
        "head": (0.060, 0.270, -0.020),
        "tail": (0.115, 0.350, -0.105),
        "parent": "upper_arm.L",
        "connected": True,
    },
    "hand.L": {
        "head": (0.115, 0.350, -0.105),
        "tail": (0.165, 0.370, -0.105),
        "parent": "forearm.L",
        "connected": True,
    },
    "upper_arm.R": {
        "head": (0.025, -0.175, 0.055),
        "tail": (0.060, -0.270, -0.020),
        "parent": "chest",
    },
    "forearm.R": {
        "head": (0.060, -0.270, -0.020),
        "tail": (0.115, -0.350, -0.105),
        "parent": "upper_arm.R",
        "connected": True,
    },
    "hand.R": {
        "head": (0.115, -0.350, -0.105),
        "tail": (0.165, -0.370, -0.105),
        "parent": "forearm.R",
        "connected": True,
    },
    "thigh.L": {
        "head": (-0.025, 0.105, -0.235),
        "tail": (0.000, 0.130, -0.345),
        "parent": "pelvis",
    },
    "shin.L": {
        "head": (0.000, 0.130, -0.345),
        "tail": (0.035, 0.140, -0.450),
        "parent": "thigh.L",
        "connected": True,
    },
    "foot.L": {
        "head": (0.035, 0.140, -0.450),
        "tail": (0.160, 0.140, -0.470),
        "parent": "shin.L",
        "connected": True,
    },
    "thigh.R": {
        "head": (-0.025, -0.105, -0.235),
        "tail": (0.000, -0.130, -0.345),
        "parent": "pelvis",
    },
    "shin.R": {
        "head": (0.000, -0.130, -0.345),
        "tail": (0.035, -0.140, -0.450),
        "parent": "thigh.R",
        "connected": True,
    },
    "foot.R": {
        "head": (0.035, -0.140, -0.450),
        "tail": (0.160, -0.140, -0.470),
        "parent": "shin.R",
        "connected": True,
    },
    "tail_01": {
        "head": (-0.075, 0.0, -0.205),
        "tail": (-0.155, 0.0, -0.220),
        "parent": "pelvis",
    },
    "tail_02": {
        "head": (-0.155, 0.0, -0.220),
        "tail": (-0.235, 0.0, -0.245),
        "parent": "tail_01",
        "connected": True,
    },
    "tail_03": {
        "head": (-0.235, 0.0, -0.245),
        "tail": (-0.310, 0.0, -0.275),
        "parent": "tail_02",
        "connected": True,
    },
    "tail_04": {
        "head": (-0.310, 0.0, -0.275),
        "tail": (-0.375, 0.0, -0.300),
        "parent": "tail_03",
        "connected": True,
    },
    "tail_05": {
        "head": (-0.375, 0.0, -0.300),
        "tail": (-0.430, 0.0, -0.305),
        "parent": "tail_04",
        "connected": True,
    },
}


POSES = [
    ("neutral", "40_pose_neutral.blend"),
    ("reach_tray_hold", "50_pose_reach_tray_hold.blend"),
    ("squat", "60_pose_squat.blend"),
    ("walk_extreme", "70_pose_walk_extreme.blend"),
    ("tail_bend", "80_pose_tail_bend.blend"),
]


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", default=PROBE_ROOT, type=Path)
    return parser.parse_args(argv)


def save_stage(filename: str) -> str:
    filepath = STAGES / filename
    if filepath.exists():
        raise FileExistsError(
            f"Refusing to overwrite preserved diagnostic stage: {filepath}"
        )
    bpy.ops.wm.save_as_mainfile(filepath=str(filepath), check_existing=False)
    return filepath.as_posix()


def mesh_topology(obj: bpy.types.Object) -> dict:
    mesh = obj.data
    side_counts: dict[str, int] = {}
    for polygon in mesh.polygons:
        key = str(len(polygon.vertices))
        side_counts[key] = side_counts.get(key, 0) + 1
    boundary_edges = 0
    edge_face_count = [0] * len(mesh.edges)
    for polygon in mesh.polygons:
        for edge_key in polygon.edge_keys:
            # Mesh edge lookup by key is not exposed as a direct dictionary.
            pass
    edge_keys = {
        tuple(sorted(edge.vertices)): edge.index for edge in mesh.edges
    }
    for polygon in mesh.polygons:
        for a, b in polygon.edge_keys:
            edge_face_count[edge_keys[tuple(sorted((a, b)))]] += 1
    boundary_edges = sum(count == 1 for count in edge_face_count)
    non_manifold_edges = sum(count != 2 for count in edge_face_count)
    return {
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
        "faces_by_sides": side_counts,
        "boundary_edges": boundary_edges,
        "non_manifold_edges": non_manifold_edges,
    }


def normalize_source(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(
        location=False, rotation=True, scale=True, properties=False
    )
    obj.name = BODY_NAME
    obj.data.name = f"{BODY_NAME}_MESH"
    obj["diagnostic_only"] = True
    obj["source_geometry_preserved_at"] = (
        "stages/00_input_all_quad_exact_copy.blend"
    )
    obj["observed_front_axis"] = "+X"
    obj["observed_bilateral_axis"] = "Y"
    obj["observed_up_axis"] = "+Z"


def create_armature() -> bpy.types.Object:
    armature_data = bpy.data.armatures.new(f"{RIG_NAME}_DATA")
    armature = bpy.data.objects.new(RIG_NAME, armature_data)
    bpy.context.collection.objects.link(armature)
    armature.show_in_front = True
    armature.display_type = "WIRE"
    armature["diagnostic_only"] = True
    armature["rig_purpose"] = "topology deformation stress probe"
    armature["left_side_definition"] = "+Y"
    armature["front_axis_observed"] = "+X"

    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="EDIT")
    for name, spec in BONES.items():
        bone = armature_data.edit_bones.new(name)
        bone.head = Vector(spec["head"])
        bone.tail = Vector(spec["tail"])
        bone.use_deform = spec.get("deform", True)
    for name, spec in BONES.items():
        parent_name = spec.get("parent")
        if not parent_name:
            continue
        bone = armature_data.edit_bones[name]
        bone.parent = armature_data.edit_bones[parent_name]
        bone.use_connect = spec.get("connected", False)
    bpy.ops.object.mode_set(mode="OBJECT")
    return armature


def automatic_parent(
    body: bpy.types.Object, armature: bpy.types.Object
) -> dict:
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    result = bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    bpy.context.view_layer.update()
    return {
        "operator_result": sorted(result),
        "weight_stats": weight_stats(body),
    }


def weight_stats(body: bpy.types.Object) -> dict:
    deform_names = {
        bone.name for bone in bpy.data.objects[RIG_NAME].data.bones
        if bone.use_deform
    }
    group_names = {
        group.index: group.name for group in body.vertex_groups
    }
    influence_counts = []
    unweighted = []
    total_weights = []
    for vertex in body.data.vertices:
        weights = [
            element.weight
            for element in vertex.groups
            if group_names.get(element.group) in deform_names
            and element.weight > 1.0e-6
        ]
        influence_counts.append(len(weights))
        total_weights.append(sum(weights))
        if not weights:
            unweighted.append(vertex.index)
    return {
        "vertex_groups": sorted(group.name for group in body.vertex_groups),
        "unweighted_vertex_count": len(unweighted),
        "unweighted_vertex_sample": unweighted[:30],
        "influences": {
            "minimum": min(influence_counts) if influence_counts else 0,
            "maximum": max(influence_counts) if influence_counts else 0,
            "mean": (
                sum(influence_counts) / len(influence_counts)
                if influence_counts else 0.0
            ),
            "over_four_count": sum(count > 4 for count in influence_counts),
        },
        "weight_sum": {
            "minimum": min(total_weights) if total_weights else 0.0,
            "maximum": max(total_weights) if total_weights else 0.0,
            "mean": (
                sum(total_weights) / len(total_weights)
                if total_weights else 0.0
            ),
        },
    }


def point_segment_distance(
    point: Vector, a: Vector, b: Vector
) -> tuple[float, float]:
    segment = b - a
    length_squared = segment.length_squared
    if length_squared <= 1.0e-12:
        return (point - a).length, 0.0
    t = max(0.0, min(1.0, (point - a).dot(segment) / length_squared))
    nearest = a + segment * t
    return (point - nearest).length, t


def chain_weights(
    point: Vector,
    names: list[str],
    include_parent: str | None = None,
) -> dict[str, float]:
    scored = []
    for name in names:
        spec = BONES[name]
        distance, _ = point_segment_distance(
            point, Vector(spec["head"]), Vector(spec["tail"])
        )
        scored.append((distance, name))
    scored.sort()
    selected = scored[:2]
    weights = {
        name: 1.0 / max(distance * distance, 1.0e-5)
        for distance, name in selected
    }
    if include_parent is not None:
        first_head = Vector(BONES[names[0]]["head"])
        attachment_distance = (point - first_head).length
        if attachment_distance < 0.095:
            blend = max(0.0, 1.0 - attachment_distance / 0.095) * 0.40
            current_sum = sum(weights.values())
            if current_sum > 0.0:
                weights = {
                    name: value / current_sum * (1.0 - blend)
                    for name, value in weights.items()
                }
            weights[include_parent] = blend
    return normalize_weights(weights)


def trunk_weights(point: Vector) -> dict[str, float]:
    anchors = [
        (-0.255, "pelvis"),
        (-0.125, "spine"),
        (0.020, "chest"),
        (0.125, "neck"),
        (0.205, "head"),
    ]
    z = point.z
    if z <= anchors[0][0]:
        return {"pelvis": 1.0}
    if z >= anchors[-1][0]:
        return {"head": 1.0}
    for (za, name_a), (zb, name_b) in zip(anchors, anchors[1:]):
        if za <= z <= zb:
            t = (z - za) / (zb - za)
            return {name_a: 1.0 - t, name_b: t}
    return {"pelvis": 1.0}


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    weights = {
        name: value
        for name, value in weights.items()
        if value > 1.0e-6
    }
    strongest = sorted(
        weights.items(), key=lambda item: item[1], reverse=True
    )[:4]
    total = sum(value for _name, value in strongest)
    if total <= 1.0e-12:
        return {}
    return {name: value / total for name, value in strongest}


def deterministic_core_weights(point: Vector) -> dict[str, float] | None:
    # Order matters: tail and head are distinctive silhouette masses.
    if point.x < -0.110 and point.z < -0.080:
        return chain_weights(
            point,
            ["tail_01", "tail_02", "tail_03", "tail_04", "tail_05"],
            include_parent="pelvis",
        )
    if point.z > 0.180:
        return {"head": 1.0}
    if (
        point.y > 0.205
        and -0.185 < point.z < 0.120
        and point.x > -0.050
    ):
        return chain_weights(
            point,
            ["upper_arm.L", "forearm.L", "hand.L"],
            include_parent="chest",
        )
    if (
        point.y < -0.205
        and -0.185 < point.z < 0.120
        and point.x > -0.050
    ):
        return chain_weights(
            point,
            ["upper_arm.R", "forearm.R", "hand.R"],
            include_parent="chest",
        )
    if (
        point.y > 0.070
        and point.z < -0.270
        and point.x > -0.100
    ):
        return chain_weights(
            point,
            ["thigh.L", "shin.L", "foot.L"],
            include_parent="pelvis",
        )
    if (
        point.y < -0.070
        and point.z < -0.270
        and point.x > -0.100
    ):
        return chain_weights(
            point,
            ["thigh.R", "shin.R", "foot.R"],
            include_parent="pelvis",
        )
    return None


def repair_weights(body: bpy.types.Object, armature: bpy.types.Object) -> dict:
    deform_names = {
        bone.name for bone in armature.data.bones if bone.use_deform
    }
    group_names = {
        group.index: group.name for group in body.vertex_groups
    }
    repaired: list[dict[str, float]] = []
    repair_reasons = {
        "core_override": 0,
        "cross_side_removed": 0,
        "invalid_tail_removed": 0,
        "fallback_trunk": 0,
    }
    for vertex in body.data.vertices:
        point = body.matrix_world @ vertex.co
        weights = {
            group_names[element.group]: element.weight
            for element in vertex.groups
            if group_names.get(element.group) in deform_names
            and element.weight > 1.0e-6
        }

        override = deterministic_core_weights(point)
        if override is not None:
            weights = override
            repair_reasons["core_override"] += 1
        else:
            before = set(weights)
            if point.y > 0.020:
                weights = {
                    name: value
                    for name, value in weights.items()
                    if not name.endswith(".R")
                }
            elif point.y < -0.020:
                weights = {
                    name: value
                    for name, value in weights.items()
                    if not name.endswith(".L")
                }
            if set(weights) != before:
                repair_reasons["cross_side_removed"] += 1

            before_tail = set(weights)
            if point.x > -0.030 or point.z > -0.040:
                weights = {
                    name: value
                    for name, value in weights.items()
                    if not name.startswith("tail_")
                }
            if set(weights) != before_tail:
                repair_reasons["invalid_tail_removed"] += 1

            weights = normalize_weights(weights)
            if not weights:
                weights = trunk_weights(point)
                repair_reasons["fallback_trunk"] += 1
        repaired.append(normalize_weights(weights))

    # Clear all automatic groups only after their weights have been captured.
    for group in list(body.vertex_groups):
        body.vertex_groups.remove(group)
    groups = {
        name: body.vertex_groups.new(name=name)
        for name in sorted(deform_names)
    }
    for vertex_index, weights in enumerate(repaired):
        for name, weight in weights.items():
            groups[name].add([vertex_index], weight, "REPLACE")

    body["weight_repair"] = (
        "automatic bone heat retained outside deterministic gross-repair cores; "
        "tail/head/limb cores overridden; cross-side and invalid-tail leakage "
        "removed; influences normalized and capped at four"
    )
    bpy.context.view_layer.update()
    return {
        "repair_counts": repair_reasons,
        "weight_stats": weight_stats(body),
    }


def reset_pose(armature: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = armature
    for pose_bone in armature.pose.bones:
        pose_bone.rotation_mode = "QUATERNION"
        pose_bone.matrix_basis.identity()
    bpy.context.view_layer.update()


def set_absolute_bone(
    armature: bpy.types.Object,
    bone_name: str,
    head: Vector,
    direction: Vector,
) -> Vector:
    pose_bone = armature.pose.bones[bone_name]
    rest_bone = armature.data.bones[bone_name]
    rest_direction = (rest_bone.tail_local - rest_bone.head_local).normalized()
    target_direction = direction.normalized()
    rotate = rest_direction.rotation_difference(target_direction)
    rest_rotation = rest_bone.matrix_local.to_3x3()
    desired_rotation = rotate.to_matrix() @ rest_rotation
    desired = desired_rotation.to_4x4()
    desired.translation = head
    pose_bone.matrix = desired
    bpy.context.view_layer.update()
    return head + target_direction * rest_bone.length


def translate_axial_pose(
    armature: bpy.types.Object, delta: Vector
) -> None:
    for name in ["pelvis", "spine", "chest", "neck", "head"]:
        rest = armature.data.bones[name]
        direction = rest.tail_local - rest.head_local
        set_absolute_bone(
            armature, name, rest.head_local + delta, direction
        )


def apply_pose(armature: bpy.types.Object, pose_name: str) -> None:
    reset_pose(armature)
    if pose_name == "neutral":
        return

    if pose_name == "reach_tray_hold":
        for side, sign in (("L", 1.0), ("R", -1.0)):
            upper = f"upper_arm.{side}"
            lower = f"forearm.{side}"
            hand = f"hand.{side}"
            shoulder = Vector(BONES[upper]["head"])
            elbow = set_absolute_bone(
                armature,
                upper,
                shoulder,
                Vector((0.84, -0.24 * sign, -0.49)),
            )
            wrist = set_absolute_bone(
                armature,
                lower,
                elbow,
                Vector((0.86, -0.46 * sign, 0.10)),
            )
            set_absolute_bone(
                armature,
                hand,
                wrist,
                Vector((0.98, -0.18 * sign, 0.03)),
            )
        armature["pose_intent"] = (
            "both hands forward and inward for tray-hold stress"
        )
        return

    if pose_name == "squat":
        delta = Vector((0.0, 0.0, -0.055))
        translate_axial_pose(armature, delta)
        for side, sign in (("L", 1.0), ("R", -1.0)):
            upper = f"upper_arm.{side}"
            lower = f"forearm.{side}"
            hand = f"hand.{side}"
            upper_head = Vector(BONES[upper]["head"]) + delta
            upper_tail = set_absolute_bone(
                armature,
                upper,
                upper_head,
                Vector(BONES[upper]["tail"]) - Vector(BONES[upper]["head"]),
            )
            lower_tail = set_absolute_bone(
                armature,
                lower,
                upper_tail,
                Vector(BONES[lower]["tail"]) - Vector(BONES[lower]["head"]),
            )
            set_absolute_bone(
                armature,
                hand,
                lower_tail,
                Vector(BONES[hand]["tail"]) - Vector(BONES[hand]["head"]),
            )

            thigh = f"thigh.{side}"
            shin = f"shin.{side}"
            foot = f"foot.{side}"
            hip = Vector(BONES[thigh]["head"]) + delta
            knee = set_absolute_bone(
                armature,
                thigh,
                hip,
                Vector((0.62, 0.18 * sign, -0.76)),
            )
            ankle = set_absolute_bone(
                armature,
                shin,
                knee,
                Vector((-0.12, -0.06 * sign, -0.99)),
            )
            set_absolute_bone(
                armature,
                foot,
                ankle,
                Vector((0.99, 0.0, -0.12)),
            )
        armature["pose_intent"] = (
            "body lowered 5.5 cm with hips and knees deeply flexed"
        )
        return

    if pose_name == "walk_extreme":
        limb_directions = {
            "L": {
                "thigh": Vector((0.73, 0.05, -0.68)),
                "shin": Vector((-0.15, 0.00, -0.99)),
                "upper_arm": Vector((-0.78, 0.10, -0.62)),
                "forearm": Vector((-0.48, -0.05, -0.88)),
            },
            "R": {
                "thigh": Vector((-0.58, -0.05, -0.81)),
                "shin": Vector((0.28, 0.00, -0.96)),
                "upper_arm": Vector((0.82, -0.10, -0.56)),
                "forearm": Vector((0.58, 0.05, -0.81)),
            },
        }
        for side, sign in (("L", 1.0), ("R", -1.0)):
            directions = limb_directions[side]
            thigh = f"thigh.{side}"
            shin = f"shin.{side}"
            foot = f"foot.{side}"
            hip = Vector(BONES[thigh]["head"])
            knee = set_absolute_bone(
                armature, thigh, hip, directions["thigh"]
            )
            ankle = set_absolute_bone(
                armature, shin, knee, directions["shin"]
            )
            set_absolute_bone(
                armature,
                foot,
                ankle,
                Vector((0.99, 0.0, -0.10)),
            )

            upper = f"upper_arm.{side}"
            lower = f"forearm.{side}"
            hand = f"hand.{side}"
            shoulder = Vector(BONES[upper]["head"])
            elbow = set_absolute_bone(
                armature, upper, shoulder, directions["upper_arm"]
            )
            wrist = set_absolute_bone(
                armature, lower, elbow, directions["forearm"]
            )
            set_absolute_bone(
                armature,
                hand,
                wrist,
                directions["forearm"],
            )
        armature["pose_intent"] = (
            "opposed arm/leg stride at intentionally extreme mobile-game range"
        )
        return

    if pose_name == "tail_bend":
        directions = [
            Vector((-0.98, 0.10, 0.05)),
            Vector((-0.88, 0.45, 0.12)),
            Vector((-0.67, 0.72, 0.16)),
            Vector((-0.42, 0.89, 0.16)),
            Vector((-0.18, 0.98, 0.08)),
        ]
        head = Vector(BONES["tail_01"]["head"])
        for index, direction in enumerate(directions, start=1):
            head = set_absolute_bone(
                armature, f"tail_{index:02d}", head, direction
            )
        armature["pose_intent"] = (
            "five-bone lateral tail curl with mild lift"
        )
        return

    raise ValueError(f"Unknown pose: {pose_name}")


def face_area(vertices: list[Vector]) -> float:
    if len(vertices) < 3:
        return 0.0
    origin = vertices[0]
    total = 0.0
    for index in range(1, len(vertices) - 1):
        total += (
            (vertices[index] - origin)
            .cross(vertices[index + 1] - origin)
            .length
            * 0.5
        )
    return total


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    raw = (len(ordered) - 1) * fraction
    lower = math.floor(raw)
    upper = math.ceil(raw)
    if lower == upper:
        return ordered[lower]
    blend = raw - lower
    return ordered[lower] * (1.0 - blend) + ordered[upper] * blend


def classify_region(point: Vector) -> str:
    if point.x < -0.105 and point.z < -0.075:
        return "tail"
    if point.z > 0.135:
        return "head_neck"
    if point.y > 0.165 and -0.190 < point.z < 0.130:
        return "arm_L"
    if point.y < -0.165 and -0.190 < point.z < 0.130:
        return "arm_R"
    if point.y > 0.040 and point.z < -0.215 and point.x > -0.120:
        return "leg_L"
    if point.y < -0.040 and point.z < -0.215 and point.x > -0.120:
        return "leg_R"
    return "torso"


def evaluated_world_vertices(
    body: bpy.types.Object,
) -> tuple[list[Vector], bpy.types.Mesh]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = body.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(
        evaluated,
        preserve_all_data_layers=True,
        depsgraph=depsgraph,
    )
    points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    return points, mesh


def deformation_metrics(
    body: bpy.types.Object,
    baseline_points: list[Vector],
    baseline_mesh: bpy.types.Mesh,
) -> dict:
    points, posed_mesh = evaluated_world_vertices(body)
    if len(points) != len(baseline_points):
        raise RuntimeError("Armature evaluation changed vertex count")
    baseline_face_areas = []
    posed_face_areas = []
    face_regions = []
    for baseline_polygon, posed_polygon in zip(
        baseline_mesh.polygons, posed_mesh.polygons
    ):
        base_vertices = [
            baseline_points[index] for index in baseline_polygon.vertices
        ]
        posed_vertices = [points[index] for index in posed_polygon.vertices]
        baseline_face_areas.append(face_area(base_vertices))
        posed_face_areas.append(face_area(posed_vertices))
        centroid = sum(base_vertices, Vector()) / len(base_vertices)
        face_regions.append(classify_region(centroid))

    baseline_edge_lengths = [
        (baseline_points[edge.vertices[1]] - baseline_points[edge.vertices[0]]).length
        for edge in baseline_mesh.edges
    ]
    posed_edge_lengths = [
        (points[edge.vertices[1]] - points[edge.vertices[0]]).length
        for edge in posed_mesh.edges
    ]
    edge_regions = [
        classify_region(
            (
                baseline_points[edge.vertices[0]]
                + baseline_points[edge.vertices[1]]
            )
            * 0.5
        )
        for edge in baseline_mesh.edges
    ]

    regions = sorted(set(face_regions) | set(edge_regions))
    report = {}
    for region in regions:
        area_ratios = [
            posed / baseline
            for posed, baseline, candidate in zip(
                posed_face_areas, baseline_face_areas, face_regions
            )
            if candidate == region and baseline > 1.0e-12
        ]
        edge_ratios = [
            posed / baseline
            for posed, baseline, candidate in zip(
                posed_edge_lengths, baseline_edge_lengths, edge_regions
            )
            if candidate == region and baseline > 1.0e-12
        ]
        report[region] = {
            "face_count": len(area_ratios),
            "edge_count": len(edge_ratios),
            "face_area_ratio": {
                "minimum": min(area_ratios) if area_ratios else 0.0,
                "p05": percentile(area_ratios, 0.05),
                "median": percentile(area_ratios, 0.50),
                "p95": percentile(area_ratios, 0.95),
                "maximum": max(area_ratios) if area_ratios else 0.0,
                "collapsed_below_0_10_count": sum(
                    ratio < 0.10 for ratio in area_ratios
                ),
                "severe_stretch_above_3_count": sum(
                    ratio > 3.0 for ratio in area_ratios
                ),
            },
            "edge_length_ratio": {
                "minimum": min(edge_ratios) if edge_ratios else 0.0,
                "p05": percentile(edge_ratios, 0.05),
                "median": percentile(edge_ratios, 0.50),
                "p95": percentile(edge_ratios, 0.95),
                "maximum": max(edge_ratios) if edge_ratios else 0.0,
                "collapsed_below_0_35_count": sum(
                    ratio < 0.35 for ratio in edge_ratios
                ),
                "severe_stretch_above_2_5_count": sum(
                    ratio > 2.5 for ratio in edge_ratios
                ),
            },
        }
    bpy.data.meshes.remove(posed_mesh)
    return report


def clear_evidence_overlay() -> None:
    collection = bpy.data.collections.get(OVERLAY_COLLECTION)
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    emission: bool = False,
) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    principled = result.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Roughness"].default_value = 0.72
        if emission:
            principled.inputs["Emission Color"].default_value = color
            principled.inputs["Emission Strength"].default_value = 2.2
    return result


def evidence_collection() -> bpy.types.Collection:
    collection = bpy.data.collections.new(OVERLAY_COLLECTION)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(
    obj: bpy.types.Object, collection: bpy.types.Collection
) -> None:
    for candidate in list(obj.users_collection):
        candidate.objects.unlink(obj)
    collection.objects.link(obj)


def add_bone_rod(
    head: Vector,
    tail: Vector,
    bone_name: str,
    collection: bpy.types.Collection,
    bone_material: bpy.types.Material,
) -> None:
    vector = tail - head
    length = vector.length
    if length <= 1.0e-8:
        return
    midpoint = (head + tail) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.006,
        depth=length,
        location=midpoint,
    )
    rod = bpy.context.object
    rod.name = f"EVIDENCE_BONE_{bone_name}"
    rod.rotation_mode = "QUATERNION"
    rod.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(
        vector.normalized()
    )
    rod.data.materials.append(bone_material)
    move_to_collection(rod, collection)
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2, radius=0.010, location=head
    )
    joint = bpy.context.object
    joint.name = f"EVIDENCE_JOINT_{bone_name}"
    joint.data.materials.append(bone_material)
    move_to_collection(joint, collection)


def build_evidence_overlay(
    body: bpy.types.Object, armature: bpy.types.Object
) -> None:
    clear_evidence_overlay()
    collection = evidence_collection()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = body.evaluated_get(depsgraph)
    wire_mesh = bpy.data.meshes.new_from_object(
        evaluated,
        preserve_all_data_layers=True,
        depsgraph=depsgraph,
    )
    wire = bpy.data.objects.new("EVIDENCE_DEFORMED_WIRE", wire_mesh)
    collection.objects.link(wire)
    wire_material = material(
        "EVIDENCE_WIRE_MATERIAL", (0.015, 0.025, 0.035, 1.0)
    )
    wire.data.materials.clear()
    wire.data.materials.append(wire_material)
    modifier = wire.modifiers.new("Evidence Wire", "WIREFRAME")
    modifier.thickness = 0.00125
    modifier.use_replace = True

    axial_material = material(
        "EVIDENCE_BONE_AXIAL", (1.0, 0.66, 0.12, 1.0), emission=True
    )
    left_material = material(
        "EVIDENCE_BONE_LEFT", (0.18, 0.60, 1.0, 1.0), emission=True
    )
    right_material = material(
        "EVIDENCE_BONE_RIGHT", (1.0, 0.22, 0.28, 1.0), emission=True
    )
    tail_material = material(
        "EVIDENCE_BONE_TAIL", (0.78, 0.34, 1.0, 1.0), emission=True
    )
    for pose_bone in armature.pose.bones:
        if pose_bone.name == "root":
            continue
        head = armature.matrix_world @ pose_bone.head
        tail = armature.matrix_world @ pose_bone.tail
        if pose_bone.name.endswith(".L"):
            selected_material = left_material
        elif pose_bone.name.endswith(".R"):
            selected_material = right_material
        elif pose_bone.name.startswith("tail_"):
            selected_material = tail_material
        else:
            selected_material = axial_material
        add_bone_rod(
            head,
            tail,
            pose_bone.name,
            collection,
            selected_material,
        )


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


def ensure_render_scene(body: bpy.types.Object) -> bpy.types.Object:
    scene = bpy.context.scene
    # Blender 5.1 exposes Eevee under the legacy enum spelling.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.world.color = (0.018, 0.027, 0.050)
    scene.view_settings.look = "AgX - Medium High Contrast"

    body_material = material(
        "BENTOSAUR_PROBE_GREEN", (0.24, 0.49, 0.39, 1.0)
    )
    body.data.materials.clear()
    body.data.materials.append(body_material)
    for polygon in body.data.polygons:
        polygon.use_smooth = True

    camera_data = bpy.data.cameras.get("PROBE_CAMERA_DATA")
    if camera_data is None:
        camera_data = bpy.data.cameras.new("PROBE_CAMERA_DATA")
    camera = bpy.data.objects.get("PROBE_CAMERA")
    if camera is None:
        camera = bpy.data.objects.new("PROBE_CAMERA", camera_data)
        scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1.30
    scene.camera = camera

    floor = bpy.data.objects.get("PROBE_FLOOR")
    if floor is None:
        bpy.ops.mesh.primitive_plane_add(
            size=3.0, location=(0.0, 0.0, -0.493)
        )
        floor = bpy.context.object
        floor.name = "PROBE_FLOOR"
        floor.data.materials.append(
            material("PROBE_FLOOR_MATERIAL", (0.035, 0.055, 0.085, 1.0))
        )

    if bpy.data.objects.get("PROBE_KEY_LIGHT") is None:
        light_data = bpy.data.lights.new("PROBE_KEY_LIGHT_DATA", "AREA")
        light_data.energy = 900.0
        light_data.shape = "DISK"
        light_data.size = 3.0
        light = bpy.data.objects.new("PROBE_KEY_LIGHT", light_data)
        light.location = (2.2, -2.4, 2.8)
        scene.collection.objects.link(light)
        look_at(light, Vector((0.0, 0.0, -0.03)))
    if bpy.data.objects.get("PROBE_FILL_LIGHT") is None:
        light_data = bpy.data.lights.new("PROBE_FILL_LIGHT_DATA", "AREA")
        light_data.energy = 650.0
        light_data.shape = "DISK"
        light_data.size = 2.0
        light = bpy.data.objects.new("PROBE_FILL_LIGHT", light_data)
        light.location = (0.2, 2.4, 1.5)
        scene.collection.objects.link(light)
        look_at(light, Vector((0.0, 0.0, -0.05)))
    return camera


def render_pose(
    body: bpy.types.Object,
    armature: bpy.types.Object,
    pose_name: str,
) -> dict[str, str]:
    build_evidence_overlay(body, armature)
    camera = ensure_render_scene(body)
    pose_dir = RENDERS / pose_name
    pose_dir.mkdir(parents=True, exist_ok=False)
    views = {
        "front_three_quarter": Vector((1.55, -1.65, 0.55)),
        "front": Vector((2.15, 0.0, 0.05)),
        "side": Vector((0.0, -2.15, 0.05)),
    }
    outputs = {}
    for view_name, location in views.items():
        camera.location = location
        look_at(camera, Vector((0.0, 0.0, -0.03)))
        output = pose_dir / f"{view_name}.png"
        bpy.context.scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        outputs[view_name] = output.as_posix()
    return outputs


def collapse_summary(regions: dict) -> list[dict]:
    failures = []
    for region, metrics in regions.items():
        area = metrics["face_area_ratio"]
        edge = metrics["edge_length_ratio"]
        reasons = []
        if area["collapsed_below_0_10_count"] > 0:
            reasons.append(
                f"{area['collapsed_below_0_10_count']} faces below 10% area"
            )
        if area["severe_stretch_above_3_count"] > 0:
            reasons.append(
                f"{area['severe_stretch_above_3_count']} faces above 3x area"
            )
        if edge["collapsed_below_0_35_count"] > 0:
            reasons.append(
                f"{edge['collapsed_below_0_35_count']} edges below 0.35x length"
            )
        if edge["severe_stretch_above_2_5_count"] > 0:
            reasons.append(
                f"{edge['severe_stretch_above_2_5_count']} edges above 2.5x length"
            )
        if reasons:
            failures.append({"region": region, "reasons": reasons})
    return failures


def main() -> None:
    args = parse_args()
    if args.output.resolve() != PROBE_ROOT.resolve():
        raise RuntimeError(
            "This diagnostic is intentionally locked to its isolated temp root"
        )
    STAGES.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)

    body = bpy.data.objects.get(SOURCE_MESH_NAME)
    if body is None or body.type != "MESH":
        meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        if len(meshes) != 1:
            raise RuntimeError("Could not unambiguously identify source mesh")
        body = meshes[0]
    report = {
        "schema_version": "1.0.0",
        "diagnostic_only": True,
        "blender_version": bpy.app.version_string,
        "source": {
            "requested_path": args.source.resolve().as_posix(),
            "opened_path": Path(bpy.data.filepath).resolve().as_posix(),
            "object_name": body.name,
            "topology": mesh_topology(body),
        },
        "coordinate_audit": {
            "observed_from_orthographic_silhouettes": {
                "front_axis": "+X",
                "back_axis": "-X",
                "bilateral_axis": "Y",
                "up_axis": "+Z",
            },
            "manifest_contract_claim": {
                "front_axis": "-Y",
                "character_left_axis": "+X",
                "up_axis": "+Z",
            },
            "match": False,
            "production_implication": (
                "Resolve orientation before production rig/export. Rotating the "
                "complete character assembly -90 degrees about Z maps observed "
                "+X front to the locked -Y front contract and +Y lateral to +X."
            ),
        },
        "stages": {},
        "poses": {},
    }

    normalize_source(body)
    report["stages"]["05_normalized_source"] = save_stage(
        "05_normalized_source_for_rig.blend"
    )

    armature = create_armature()
    report["armature"] = {
        "name": armature.name,
        "bone_count": len(armature.data.bones),
        "deform_bones": sorted(
            bone.name for bone in armature.data.bones if bone.use_deform
        ),
        "non_deform_bones": sorted(
            bone.name for bone in armature.data.bones if not bone.use_deform
        ),
        "rest_bones": {
            name: {
                "head": spec["head"],
                "tail": spec["tail"],
                "parent": spec.get("parent"),
                "connected": spec.get("connected", False),
                "deform": spec.get("deform", True),
            }
            for name, spec in BONES.items()
        },
    }
    report["stages"]["10_neutral_armature_no_weights"] = save_stage(
        "10_neutral_armature_no_weights.blend"
    )

    report["automatic_weights"] = automatic_parent(body, armature)
    report["stages"]["20_automatic_weights"] = save_stage(
        "20_automatic_weights.blend"
    )

    report["repaired_weights"] = repair_weights(body, armature)
    report["stages"]["30_repaired_weights_neutral"] = save_stage(
        "30_repaired_weights_neutral.blend"
    )

    reset_pose(armature)
    baseline_points, baseline_mesh = evaluated_world_vertices(body)
    report["baseline_vertex_count"] = len(baseline_points)

    for pose_name, filename in POSES:
        apply_pose(armature, pose_name)
        bpy.context.view_layer.update()
        regions = deformation_metrics(body, baseline_points, baseline_mesh)
        renders = render_pose(body, armature, pose_name)
        stage = save_stage(filename)
        collapses = collapse_summary(regions)
        report["poses"][pose_name] = {
            "stage": stage,
            "renders": renders,
            "regions": regions,
            "threshold_flags": collapses,
            "diagnostic_pass": len(collapses) == 0,
        }
        clear_evidence_overlay()

    bpy.data.meshes.remove(baseline_mesh)
    failing_poses = [
        name
        for name, result in report["poses"].items()
        if not result["diagnostic_pass"]
    ]
    report["verdict"] = {
        "rig_probe_pass": len(failing_poses) == 0,
        "failing_poses": failing_poses,
        "topology_approval": False,
        "rig_approval": False,
        "animation_approval": False,
        "mouth_or_face_tested": False,
        "statement": (
            "This result is a deformation diagnostic only. It cannot approve "
            "production topology, the final rig, animation quality, facial "
            "behavior, or the user's visual target."
        ),
    }
    report_path = PROBE_ROOT / "deformation_report.json"
    report_path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print("BENTOSAUR_DEFORMATION_REPORT=" + json.dumps(report["verdict"]))


if __name__ == "__main__":
    main()
