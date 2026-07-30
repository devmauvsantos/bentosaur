"""Resume canonical R003 confirmation with one bounded head-mass lock.

Input is the preserved automatic-weight stage. This is not a weight-polishing
loop: it changes only the lower head/frill threshold that visibly contaminated
the arm pose in pass one, then repeats the identical stress poses.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import bpy

ROOT = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/.tmp/subagents/"
    "deformation_rig_probe/r003-confirmation"
)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

import run_deformation_rig_probe as probe
import run_r003_confirmation as confirm


POSES = [
    ("neutral", "41_pose_neutral_headlock.blend"),
    ("reach_tray_hold", "51_pose_reach_tray_hold_headlock.blend"),
    ("squat", "61_pose_squat_headlock.blend"),
    ("walk_extreme", "71_pose_walk_extreme_headlock.blend"),
    ("tail_bend", "81_pose_tail_bend_headlock.blend"),
]


def main() -> None:
    body = bpy.data.objects.get(probe.BODY_NAME)
    armature = bpy.data.objects.get(probe.RIG_NAME)
    if body is None or armature is None:
        raise RuntimeError("Expected preserved R003 automatic-weight stage")

    prior = json.loads(
        (ROOT / "r003_confirmation_report_v1.json").read_text(
            encoding="utf-8"
        )
    )
    cleanup = confirm.minimal_weight_cleanup(body, armature)
    stage_31 = confirm.save_stage(
        "31_minimal_confirmation_weights_headlock.blend"
    )

    probe.reset_pose(armature)
    baseline_points, baseline_mesh = probe.evaluated_world_vertices(body)
    probe.classify_region = confirm.canonical_region
    poses = {}
    for pose_name, filename in POSES:
        confirm.apply_pose(armature, pose_name)
        bpy.context.view_layer.update()
        metrics = probe.deformation_metrics(
            body, baseline_points, baseline_mesh
        )
        renders = confirm.render_pose(
            body, armature, f"headlock_{pose_name}"
        )
        stage = confirm.save_stage(filename)
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
        "schema_version": "2.0.0",
        "diagnostic_only": True,
        "candidate": "S40_r003_axis_qf_winner",
        "fallback_result_applies_to_this_candidate": False,
        "source": prior["source"],
        "coordinate_audit": prior["coordinate_audit"],
        "input_checkpoint": (
            ROOT / "stages/20_automatic_weights.blend"
        ).as_posix(),
        "headlock_checkpoint": stage_31,
        "weights": {
            "automatic": prior["weights"]["automatic"],
            "single_bounded_cleanup": cleanup,
            "polish_iterations": 0,
            "change_from_pass_one": (
                "Head/frill rigid-mass lock lowered from Z>0.67 to Z>0.54 "
                "after direct visual evidence of frill-to-arm bone heat."
            ),
        },
        "poses": poses,
        "verdict": {
            "r003_confirmation_pass": len(failing) == 0,
            "failing_poses": failing,
            "topology_approval": False,
            "rig_approval": False,
            "scope": (
                "Canonical R003 confirmation after removing obvious lower-"
                "frill arm-weight contamination; no weight polish iterations."
            ),
        },
    }
    (ROOT / "r003_confirmation_report_v2.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print("R003_HEADLOCK_CONFIRMATION=" + json.dumps(report["verdict"]))


if __name__ == "__main__":
    main()
