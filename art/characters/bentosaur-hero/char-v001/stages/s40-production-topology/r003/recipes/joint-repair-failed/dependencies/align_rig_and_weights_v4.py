"""Correct limb/tail joint centers, rebuild weights, and rerun stress poses.

The v1-v3 evidence exposed that the first diagnostic arm and tail centerlines
sat visibly outside the source silhouette. This iteration preserves those
failures, moves only the temporary diagnostic armature, rebuilds weights from
the corrected rest bones, smooths them through topology adjacency, and uses
less theatrical but still demanding mobile-game pose targets.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_deformation_rig_probe as probe


V4_POSES = [
    ("neutral", "49_pose_neutral_v4.blend"),
    ("reach_tray_hold", "59_pose_reach_tray_hold_v4.blend"),
    ("squat", "69_pose_squat_v4.blend"),
    ("walk_extreme", "79_pose_walk_extreme_v4.blend"),
    ("tail_bend", "89_pose_tail_bend_v4.blend"),
]


CORRECTED_BONES = {
    "upper_arm.L": ((0.055, 0.150, -0.020), (0.085, 0.205, -0.090)),
    "forearm.L": ((0.085, 0.205, -0.090), (0.135, 0.275, -0.155)),
    "hand.L": ((0.135, 0.275, -0.155), (0.195, 0.310, -0.165)),
    "upper_arm.R": ((0.055, -0.150, -0.020), (0.085, -0.205, -0.090)),
    "forearm.R": ((0.085, -0.205, -0.090), (0.135, -0.275, -0.155)),
    "hand.R": ((0.135, -0.275, -0.155), (0.195, -0.310, -0.165)),
    "tail_01": ((-0.075, 0.0, -0.260), (-0.150, 0.0, -0.305)),
    "tail_02": ((-0.150, 0.0, -0.305), (-0.230, 0.0, -0.340)),
    "tail_03": ((-0.230, 0.0, -0.340), (-0.305, 0.0, -0.365)),
    "tail_04": ((-0.305, 0.0, -0.365), (-0.370, 0.0, -0.375)),
    "tail_05": ((-0.370, 0.0, -0.375), (-0.430, 0.0, -0.365)),
}


def correct_rest_bones(armature: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (head, tail) in CORRECTED_BONES.items():
        bone = armature.data.edit_bones[name]
        bone.use_connect = False
        bone.head = Vector(head)
        bone.tail = Vector(tail)
    for name in [
        "forearm.L",
        "hand.L",
        "forearm.R",
        "hand.R",
        "tail_02",
        "tail_03",
        "tail_04",
        "tail_05",
    ]:
        armature.data.edit_bones[name].use_connect = True
    bpy.ops.object.mode_set(mode="OBJECT")
    probe.reset_pose(armature)
    armature["rest_alignment_v4"] = (
        "Arms lowered/medialized to silhouette center; tail lowered to measured "
        "tail bounds. Previous diagnostic sources remain preserved."
    )


def point_segment_distance(
    point: Vector, a: Vector, b: Vector
) -> float:
    segment = b - a
    if segment.length_squared <= 1.0e-12:
        return (point - a).length
    t = max(
        0.0,
        min(1.0, (point - a).dot(segment) / segment.length_squared),
    )
    return (point - (a + segment * t)).length


def chain_weights(
    point: Vector,
    armature: bpy.types.Object,
    names: list[str],
    parent: str | None = None,
) -> dict[str, float]:
    distances = []
    for name in names:
        bone = armature.data.bones[name]
        distance = point_segment_distance(
            point, bone.head_local, bone.tail_local
        )
        distances.append((distance, name))
    distances.sort()
    weights = {
        name: 1.0 / max(distance * distance, 1.0e-5)
        for distance, name in distances[:2]
    }
    if parent is not None:
        attachment = armature.data.bones[names[0]].head_local
        distance = (point - attachment).length
        if distance < 0.105:
            blend = (1.0 - distance / 0.105) * 0.45
            weights = probe.normalize_weights(weights)
            weights = {
                name: value * (1.0 - blend)
                for name, value in weights.items()
            }
            weights[parent] = blend
    return probe.normalize_weights(weights)


def classify(
    point: Vector, armature: bpy.types.Object
) -> dict[str, float]:
    if point.x < -0.090 and point.z < -0.065:
        return chain_weights(
            point,
            armature,
            ["tail_01", "tail_02", "tail_03", "tail_04", "tail_05"],
            parent="pelvis",
        )
    if point.z > 0.095 or (point.x > 0.100 and point.z > -0.020):
        if point.z < 0.165:
            return probe.trunk_weights(point)
        return {"head": 1.0}
    if (
        point.y > 0.140
        and -0.225 < point.z < 0.105
        and point.x > -0.070
    ):
        return chain_weights(
            point,
            armature,
            ["upper_arm.L", "forearm.L", "hand.L"],
            parent="chest",
        )
    if (
        point.y < -0.140
        and -0.225 < point.z < 0.105
        and point.x > -0.070
    ):
        return chain_weights(
            point,
            armature,
            ["upper_arm.R", "forearm.R", "hand.R"],
            parent="chest",
        )
    if (
        point.y > 0.032
        and point.z < -0.200
        and point.x > -0.115
    ):
        return chain_weights(
            point,
            armature,
            ["thigh.L", "shin.L", "foot.L"],
            parent="pelvis",
        )
    if (
        point.y < -0.032
        and point.z < -0.200
        and point.x > -0.115
    ):
        return chain_weights(
            point,
            armature,
            ["thigh.R", "shin.R", "foot.R"],
            parent="pelvis",
        )
    return probe.trunk_weights(point)


def rebuild_and_smooth(
    body: bpy.types.Object,
    armature: bpy.types.Object,
    iterations: int = 14,
    alpha: float = 0.38,
) -> dict:
    points = [body.matrix_world @ vertex.co for vertex in body.data.vertices]
    weights = [classify(point, armature) for point in points]
    adjacency = [[] for _vertex in body.data.vertices]
    for edge in body.data.edges:
        a, b = edge.vertices
        adjacency[a].append(b)
        adjacency[b].append(a)

    for _iteration in range(iterations):
        updated = []
        for index, own in enumerate(weights):
            accumulator = {
                name: value * (1.0 - alpha)
                for name, value in own.items()
            }
            if adjacency[index]:
                share = alpha / len(adjacency[index])
                for neighbor in adjacency[index]:
                    for name, value in weights[neighbor].items():
                        accumulator[name] = (
                            accumulator.get(name, 0.0) + value * share
                        )
            point = points[index]
            # Strong distal anchors; the joint zones remain free to diffuse.
            if point.z > 0.210 or (
                point.x > 0.185 and point.z > 0.035
            ):
                accumulator = {"head": 1.0}
            elif point.x < -0.225 and point.z < -0.120:
                accumulator = chain_weights(
                    point,
                    armature,
                    ["tail_02", "tail_03", "tail_04", "tail_05"],
                )
            elif (
                abs(point.y) > 0.255
                and -0.195 < point.z < -0.015
                and point.x > -0.025
            ):
                side = "L" if point.y > 0.0 else "R"
                accumulator = chain_weights(
                    point,
                    armature,
                    [
                        f"upper_arm.{side}",
                        f"forearm.{side}",
                        f"hand.{side}",
                    ],
                )
            elif (
                abs(point.y) > 0.075
                and point.z < -0.365
                and point.x > -0.045
            ):
                side = "L" if point.y > 0.0 else "R"
                accumulator = chain_weights(
                    point,
                    armature,
                    [f"shin.{side}", f"foot.{side}"],
                )

            if point.y > 0.020:
                accumulator = {
                    name: value
                    for name, value in accumulator.items()
                    if not name.endswith(".R")
                }
            elif point.y < -0.020:
                accumulator = {
                    name: value
                    for name, value in accumulator.items()
                    if not name.endswith(".L")
                }
            if point.x > -0.010 or point.z > -0.020:
                accumulator = {
                    name: value
                    for name, value in accumulator.items()
                    if not name.startswith("tail_")
                }
            updated.append(probe.normalize_weights(accumulator))
        weights = updated

    for group in list(body.vertex_groups):
        body.vertex_groups.remove(group)
    deform_names = sorted(
        bone.name for bone in armature.data.bones if bone.use_deform
    )
    groups = {
        name: body.vertex_groups.new(name=name) for name in deform_names
    }
    for index, assignment in enumerate(weights):
        for name, weight in assignment.items():
            groups[name].add([index], weight, "REPLACE")
    body["weight_repair_v4"] = (
        "Rebuilt from corrected rest bones and topology-smoothed for 14 "
        "iterations; maximum four influences."
    )
    bpy.context.view_layer.update()
    return {
        "iterations": iterations,
        "alpha": alpha,
        "stats": probe.weight_stats(body),
    }


def rest_head(armature: bpy.types.Object, name: str) -> Vector:
    return armature.data.bones[name].head_local.copy()


def rest_direction(armature: bpy.types.Object, name: str) -> Vector:
    bone = armature.data.bones[name]
    return bone.tail_local - bone.head_local


def rest_limb(
    armature: bpy.types.Object, side: str, delta: Vector = Vector()
) -> None:
    upper = f"upper_arm.{side}"
    lower = f"forearm.{side}"
    hand = f"hand.{side}"
    elbow = probe.set_absolute_bone(
        armature, upper, rest_head(armature, upper) + delta,
        rest_direction(armature, upper)
    )
    wrist = probe.set_absolute_bone(
        armature, lower, elbow, rest_direction(armature, lower)
    )
    probe.set_absolute_bone(
        armature, hand, wrist, rest_direction(armature, hand)
    )


def apply_pose_v4(
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
            shoulder = rest_head(armature, upper)
            elbow = probe.set_absolute_bone(
                armature,
                upper,
                shoulder,
                Vector((0.73, -0.44 * sign, -0.52)),
            )
            wrist = probe.set_absolute_bone(
                armature,
                lower,
                elbow,
                Vector((0.82, -0.50 * sign, 0.04)),
            )
            probe.set_absolute_bone(
                armature,
                hand,
                wrist,
                Vector((0.99, -0.08 * sign, 0.02)),
            )
        return
    if pose_name == "squat":
        delta = Vector((0.0, 0.0, -0.045))
        probe.translate_axial_pose(armature, delta)
        for side, sign in (("L", 1.0), ("R", -1.0)):
            rest_limb(armature, side, delta)
            thigh = f"thigh.{side}"
            shin = f"shin.{side}"
            foot = f"foot.{side}"
            knee = probe.set_absolute_bone(
                armature,
                thigh,
                rest_head(armature, thigh) + delta,
                Vector((0.48, 0.14 * sign, -0.87)),
            )
            ankle = probe.set_absolute_bone(
                armature,
                shin,
                knee,
                Vector((-0.18, -0.03 * sign, -0.98)),
            )
            probe.set_absolute_bone(
                armature,
                foot,
                ankle,
                Vector((0.99, 0.0, -0.08)),
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
                armature, thigh, rest_head(armature, thigh), thigh_dir
            )
            ankle = probe.set_absolute_bone(
                armature, shin, knee, shin_dir
            )
            probe.set_absolute_bone(
                armature, foot, ankle, Vector((0.99, 0.0, -0.08))
            )
            upper = f"upper_arm.{side}"
            lower = f"forearm.{side}"
            hand = f"hand.{side}"
            elbow = probe.set_absolute_bone(
                armature, upper, rest_head(armature, upper), upper_dir
            )
            wrist = probe.set_absolute_bone(
                armature, lower, elbow, forearm_dir
            )
            probe.set_absolute_bone(
                armature, hand, wrist, forearm_dir
            )
        return
    if pose_name == "tail_bend":
        directions = [
            Vector((-0.96, 0.20, 0.02)),
            Vector((-0.82, 0.56, 0.05)),
            Vector((-0.60, 0.78, 0.08)),
            Vector((-0.36, 0.92, 0.08)),
            Vector((-0.12, 0.99, 0.02)),
        ]
        head = rest_head(armature, "tail_01")
        for index, direction in enumerate(directions, start=1):
            head = probe.set_absolute_bone(
                armature, f"tail_{index:02d}", head, direction
            )
        return
    raise ValueError(pose_name)


def main() -> None:
    body = bpy.data.objects.get(probe.BODY_NAME)
    armature = bpy.data.objects.get(probe.RIG_NAME)
    if body is None or armature is None:
        raise RuntimeError("Expected v3 neutral body and armature")
    v3_neutral_input = Path(bpy.data.filepath).resolve().as_posix()
    correct_rest_bones(armature)
    weight_result = rebuild_and_smooth(body, armature)
    stage_39 = probe.save_stage(
        "39_aligned_rig_smoothed_weights_v4.blend"
    )

    probe.reset_pose(armature)
    baseline_points, baseline_mesh = probe.evaluated_world_vertices(body)
    poses = {}
    for pose_name, filename in V4_POSES:
        apply_pose_v4(armature, pose_name)
        bpy.context.view_layer.update()
        regions = probe.deformation_metrics(
            body, baseline_points, baseline_mesh
        )
        renders = probe.render_pose(
            body, armature, f"v4_{pose_name}"
        )
        stage = probe.save_stage(filename)
        flags = probe.collapse_summary(regions)
        poses[pose_name] = {
            "stage": stage,
            "renders": renders,
            "regions": regions,
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
        "schema_version": "4.0.0",
        "diagnostic_only": True,
        "source_identity": {
            "all_quad_input": (
                "/Users/mauvsantos/Workspace/games/Bentosaur/.tmp/"
                "subagents/center_seam_quad_repair/targeted-retile/"
                "40_all_quad_targeted_retile.blend"
            ),
            "v3_neutral_input": v3_neutral_input,
            "topology": probe.mesh_topology(body),
        },
        "coordinate_contract_blocker": {
            "observed": {
                "front": "+X",
                "bilateral": "Y",
                "up": "+Z",
            },
            "locked_manifest": {
                "front": "-Y",
                "character_left": "+X",
                "up": "+Z",
            },
            "match": False,
        },
        "correction": {
            "reason": (
                "V1-v3 arm and tail bone overlays were outside their measured "
                "silhouettes, invalidating part of the earlier stress evidence."
            ),
            "corrected_rest_bones": CORRECTED_BONES,
            "anatomy_measurement_source": "anatomy_region_bounds.json",
            "weight_rebuild": weight_result,
            "neutral_output": stage_39,
        },
        "poses": poses,
        "verdict": {
            "rig_probe_pass": len(failing) == 0,
            "failing_poses": failing,
            "topology_approval": False,
            "rig_approval": False,
            "animation_approval": False,
            "mouth_or_face_tested": False,
            "statement": (
                "This is the first geometrically credible temporary probe. "
                "Any remaining failures indicate scaffold/weight work, but do "
                "not themselves distinguish topology from manual-weight causes."
            ),
        },
    }
    path = probe.PROBE_ROOT / "deformation_report_v4.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("BENTOSAUR_DEFORMATION_V4=" + json.dumps(report["verdict"]))


if __name__ == "__main__":
    main()
