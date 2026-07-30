"""Fold practical geometry and bounded deformation results into final QA."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "qa" / "paired_joint_support_loop_report.json"
GEOMETRY_PATH = ROOT / "qa" / "support_ring_geometry_audit.json"
DEFORMATION_PATH = (
    ROOT / "deformation-reprobe" / "bounded_deformation_reprobe_report.json"
)

report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
geometry = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
deformation = json.loads(DEFORMATION_PATH.read_text(encoding="utf-8"))

practical_geometry_pass = (
    geometry["new_incident_faces_with_aspect_above_10"] == 0
    and geometry["new_incident_edges_below_35_percent_preserved_median"] == 0
)
deformation_pass = deformation["verdict"]["bounded_reprobe_pass"]
formal_gate = report["verdict"]["technical_topology_gate"]

report["practical_rest_geometry_gate"] = {
    "pass": practical_geometry_pass,
    "new_incident_faces_with_aspect_above_10": geometry[
        "new_incident_faces_with_aspect_above_10"
    ],
    "new_incident_edges_below_35_percent_preserved_median": geometry[
        "new_incident_edges_below_35_percent_preserved_median"
    ],
    "new_incident_edge_minimum": geometry["new_incident_edge_length"][
        "minimum"
    ],
    "new_incident_face_aspect_p95": geometry[
        "new_incident_face_edge_aspect"
    ]["p95"],
    "root_cause": (
        "nearest-surface projection collapsed many inset boundary vertices "
        "onto nearly coincident canonical positions, producing sliver/near-"
        "zero support-ring geometry"
    ),
    "source": str(GEOMETRY_PATH),
}
report["bounded_deformation_gate"] = {
    "pass": deformation_pass,
    "failing_poses": deformation["verdict"]["failing_poses"],
    "baseline_comparison": deformation["baseline_comparison"],
    "source": str(DEFORMATION_PATH),
}
report["verdict"] = {
    "formal_manifold_quad_gate": formal_gate,
    "practical_rest_geometry_gate": practical_geometry_pass,
    "deformation_gate": deformation_pass,
    "technical_topology_gate": (
        formal_gate and practical_geometry_pass and deformation_pass
    ),
    "production_ready": False,
    "user_approved": False,
    "promotion_allowed": False,
    "final_status": (
        "FAILED_DIAGNOSTIC_BRANCH_RETAINED_FOR_EVIDENCE"
    ),
}
report["next_iteration_constraint"] = (
    "Do not reuse nearest-point projection for newly inset support loops. "
    "A future authorized iteration must construct well-spaced manual quad "
    "rings in tangent/geodesic flow and validate rest edge/face quality before "
    "running deformation."
)
REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report["verdict"], indent=2))
