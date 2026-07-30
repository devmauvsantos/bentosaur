import bpy
import json
from pathlib import Path

ROOT = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/.tmp/subagents/"
    "deformation_rig_probe/r003-confirmation"
)
TARGET = "BENTOSAUR_BODY_RETOPO_WIP_R003"

objects = []
for obj in bpy.data.objects:
    entry = {
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions),
        "hidden_render": obj.hide_render,
        "hidden_viewport": obj.hide_get(),
    }
    if obj.type == "MESH":
        counts = {}
        for face in obj.data.polygons:
            key = str(len(face.vertices))
            counts[key] = counts.get(key, 0) + 1
        points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        entry.update(
            vertices=len(obj.data.vertices),
            edges=len(obj.data.edges),
            faces=len(obj.data.polygons),
            faces_by_sides=counts,
            world_bounds={
                "min": [
                    min(point[axis] for point in points)
                    for axis in range(3)
                ],
                "max": [
                    max(point[axis] for point in points)
                    for axis in range(3)
                ],
            },
            vertex_groups=[group.name for group in obj.vertex_groups],
            modifiers=[
                {"name": modifier.name, "type": modifier.type}
                for modifier in obj.modifiers
            ],
        )
    objects.append(entry)

payload = {
    "source": bpy.data.filepath,
    "target": TARGET,
    "target_found": bpy.data.objects.get(TARGET) is not None,
    "objects": objects,
}
(ROOT / "source_inspection.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({
    "target": next(
        (item for item in objects if item["name"] == TARGET), None
    ),
    "object_count": len(objects),
}, indent=2))
