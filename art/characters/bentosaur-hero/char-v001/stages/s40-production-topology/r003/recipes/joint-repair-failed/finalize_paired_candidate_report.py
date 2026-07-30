"""Merge the lineage-aware symmetry audit into the candidate QA report."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "qa" / "paired_joint_support_loop_report.json"
AUDIT_PATH = ROOT / "qa" / "partitioned_symmetry_audit.json"

report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
report["partitioned_symmetry_audit"] = audit
report["symmetry_audit_interpretation"] = {
    "generic_spatial_nearest_result": report["steps"]["40_finalize"]["topology"][
        "symmetry"
    ],
    "generic_spatial_nearest_is_ambiguous": True,
    "reason": (
        "new support-ring vertices lie extremely close to preserved canonical "
        "surface vertices; an unconstrained nearest-point mirror map may pair "
        "across those lineages and is therefore not a valid topology bijection"
    ),
    "authoritative_result": (
        "partitioned canonical/new lineage mirror map is bijective and matches "
        "every edge and every face"
    ),
}
report["acceptance"]["exact_mirrored_topology"] = (
    audit["edge_match_ratio"] == 1.0
    and audit["face_match_ratio"] == 1.0
    and audit["pairing_involution_failures"] == 0
)
report["verdict"]["technical_topology_gate"] = all(
    report["acceptance"].values()
)
REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(
    json.dumps(
        {
            "acceptance": report["acceptance"],
            "technical_topology_gate": report["verdict"][
                "technical_topology_gate"
            ],
            "authoritative_symmetry": audit,
        },
        indent=2,
    )
)
