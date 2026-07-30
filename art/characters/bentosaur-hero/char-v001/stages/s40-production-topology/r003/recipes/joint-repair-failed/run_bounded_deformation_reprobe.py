"""Run one bounded deformation re-probe on the best paired-loop candidate.

The harness deliberately reuses the exact head-lock rig, weight cleanup,
stress-pose definitions, region metrics, and thresholds from the canonical
r003 confirmation. It saves a compact editable .blend at each rig/weight/pose
step, renders matched evidence views, and compares the result to the preserved
r003 baseline. It is diagnostic only and cannot promote or approve topology.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
REPROBE = ROOT / "deformation-reprobe"
STAGES = REPROBE / "stages"
RENDERS = REPROBE / "renders"
STAGES.mkdir(parents=True, exist_ok=True)
RENDERS.mkdir(parents=True, exist_ok=True)
CANDIDATE = ROOT / "stages" / "40_paired_joint_support_loops_candidate.blend"
CANDIDATE_OBJECT = "BENTOSAUR_JOINT_REPAIR_CANDIDATE_NOT_APPROVED"
BASELINE_REPORT = (
    ROOT.parent
    / "deformation_rig_probe"
    / "r003-confirmation"
    / "r003_confirmation_report_v2.json"
)
CONFIRM_PATH = (
    ROOT.parent
    / "deformation_rig_probe"
    / "r003-confirmation"
    / "recipes"
    / "run_r003_confirmation_headlock.py"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(
        "joint_repair_confirmation_harness", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load confirmation harness: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


confirm = load_module(CONFIRM_PATH)
probe = confirm.probe
confirm.ROOT = REPROBE
confirm.STAGES = STAGES
confirm.RENDERS = RENDERS
confirm.SOURCE_PATH = CANDIDATE
confirm.SOURCE_SHA256 = sha256(CANDIDATE)
confirm.SOURCE_OBJECT = CANDIDATE_OBJECT


def save_stage(filename: str) -> dict:
    path = STAGES / filename
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {path}")
    bpy.ops.wm.save_as_mainfile(filepath=str(path), check_existing=False)
    return {
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


if Path(bpy.data.filepath).resolve() != CANDIDATE.resolve():
    raise RuntimeError(f"Wrong re-probe input: {bpy.data.filepath}")

body = confirm.isolate_body()
# Remove unused packed source/reference datablocks before the diagnostic saves.
# This affects file size only; the live candidate mesh is retained.
for _unused in range(4):
    result = bpy.ops.outliner.orphans_purge(
        do_local_ids=True,
        do_linked_ids=True,
        do_recursive=True,
    )
    if result == {"CANCELLED"}:
        break

source_topology = probe.mesh_topology(body)
coordinate_audit = {
    "contract": {
        "front": "-Y",
        "character_left": "+X",
        "up": "+Z",
        "floor": "Z=0",
    },
    "bounds_and_morphology": confirm.bounds(body),
    "mirror": confirm.mirror_audit(body),
}

armature = confirm.create_armature()
stage_60 = save_stage("60_reprobe_armature_no_weights.blend")

automatic = probe.automatic_parent(body, armature)
stage_65 = save_stage("65_reprobe_automatic_weights.blend")

cleanup = confirm.minimal_weight_cleanup(body, armature)
probe.reset_pose(armature)
stage_70 = save_stage("70_reprobe_headlock_weights_neutral.blend")

baseline_points, baseline_mesh = probe.evaluated_world_vertices(body)
probe.classify_region = confirm.canonical_region
pose_specs = [
    ("neutral", "80_pose_neutral.blend"),
    ("reach_tray_hold", "81_pose_reach_tray_hold.blend"),
    ("squat", "82_pose_squat.blend"),
    ("walk_extreme", "83_pose_walk_extreme.blend"),
    ("tail_bend", "84_pose_tail_bend.blend"),
]
poses = {}
for pose_name, filename in pose_specs:
    confirm.apply_pose(armature, pose_name)
    bpy.context.view_layer.update()
    metrics = probe.deformation_metrics(body, baseline_points, baseline_mesh)
    renders = confirm.render_pose(body, armature, pose_name)
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

baseline = json.loads(BASELINE_REPORT.read_text(encoding="utf-8"))
baseline_comparison = {}
for pose_name, result in poses.items():
    old = baseline["poses"][pose_name]
    baseline_comparison[pose_name] = {
        "canonical_r003_pass": old["diagnostic_pass"],
        "canonical_r003_flags": old["threshold_flags"],
        "paired_candidate_pass": result["diagnostic_pass"],
        "paired_candidate_flags": result["threshold_flags"],
        "changed_pass_state": (
            old["diagnostic_pass"] != result["diagnostic_pass"]
        ),
    }

failing = [
    name for name, result in poses.items() if not result["diagnostic_pass"]
]
report = {
    "schema_version": "1.0.0",
    "diagnostic_only": True,
    "production_promotion": False,
    "user_approval": False,
    "method": (
        "one bounded rerun of preserved r003 head-lock rig/weights/stress poses"
    ),
    "source": {
        "candidate_blend": str(CANDIDATE),
        "candidate_sha256": sha256(CANDIDATE),
        "candidate_object": CANDIDATE_OBJECT,
        "topology": source_topology,
    },
    "coordinate_audit": coordinate_audit,
    "checkpoints": {
        "armature_no_weights": stage_60,
        "automatic_weights": stage_65,
        "headlock_weights_neutral": stage_70,
    },
    "weights": {
        "automatic": automatic,
        "single_bounded_headlock_cleanup": cleanup,
        "polish_iterations": 0,
    },
    "poses": poses,
    "baseline_report": str(BASELINE_REPORT),
    "baseline_comparison": baseline_comparison,
    "verdict": {
        "bounded_reprobe_pass": len(failing) == 0,
        "failing_poses": failing,
        "topology_approval": False,
        "rig_approval": False,
        "scope": (
            "Diagnostic comparison only; no further topology or weight repair "
            "is authorized in this branch."
        ),
    },
}
output = REPROBE / "bounded_deformation_reprobe_report.json"
output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(
    "JOINT_REPAIR_BOUNDED_REPROBE="
    + json.dumps(report["verdict"], sort_keys=True)
)
