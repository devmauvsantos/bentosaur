import bpy
import json
from pathlib import Path
import sys

from mathutils import Vector

ROOT = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/.tmp/subagents/"
    "deformation_rig_probe/r003-confirmation"
)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))
import run_r003_confirmation as confirm
import upgrade_repair_and_resume_v2 as old_regions

body = bpy.data.objects.get("BENTOSAUR_DEFORMATION_PROBE_BODY")
if body is None:
    body = bpy.data.objects.get(confirm.SOURCE_OBJECT)
if body is None:
    raise RuntimeError("R003 body not found")

regions = {}
for vertex in body.data.vertices:
    point = body.matrix_world @ vertex.co
    _weights, region = old_regions.classify_weights(
        confirm.canonical_to_old(point)
    )
    regions.setdefault(region, []).append(point)

payload = {}
for name, points in regions.items():
    payload[name] = {
        "count": len(points),
        "min": [min(point[axis] for point in points) for axis in range(3)],
        "max": [max(point[axis] for point in points) for axis in range(3)],
        "mean": [
            sum(point[axis] for point in points) / len(points)
            for axis in range(3)
        ],
    }
(ROOT / "region_bounds.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(payload, indent=2))
