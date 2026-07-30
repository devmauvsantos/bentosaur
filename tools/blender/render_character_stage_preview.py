"""Render deterministic clay and wire previews from a character stage .blend.

Run Blender with the stage source already opened:

    blender --background stage.blend \
      --python tools/blender/render_character_stage_preview.py -- \
      --object BENTOSAUR_BODY_RETOPO_WIP_R002 \
      --output /absolute/output
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import evaluate_tripo_visual_candidate as visual


VIEW_DIRECTIONS = {
    "front": Vector((0.0, -1.0, 0.0)),
    "left": Vector((1.0, 0.0, 0.0)),
    "back": Vector((0.0, 1.0, 0.0)),
    "right": Vector((-1.0, 0.0, 0.0)),
    "three_quarter_left": Vector((1.0, -1.0, 0.1)).normalized(),
    "three_quarter_right": Vector((-1.0, -1.0, 0.1)).normalized(),
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--object", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd()
    )
    parser.add_argument("--resolution", type=int, default=768)
    return parser.parse_args(argv)


def isolate_object(obj: bpy.types.Object) -> None:
    for current in bpy.context.scene.objects:
        current.hide_render = current != obj
    for collection in bpy.data.collections:
        collection.hide_render = False
        collection.hide_viewport = False
    obj.hide_render = False
    obj.hide_set(False)


def topology(obj: bpy.types.Object) -> dict[str, int]:
    mesh = obj.data
    mesh.calc_loop_triangles()
    return {
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
        "triangles_evaluated": len(mesh.loop_triangles),
        "quad_faces": sum(
            1 for polygon in mesh.polygons if len(polygon.vertices) == 4
        ),
        "triangle_faces": sum(
            1 for polygon in mesh.polygons if len(polygon.vertices) == 3
        ),
        "ngon_faces": sum(
            1 for polygon in mesh.polygons if len(polygon.vertices) > 4
        ),
    }


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    obj = bpy.data.objects.get(args.object)
    if obj is None or obj.type != "MESH":
        raise RuntimeError(f"Mesh object not found: {args.object}")
    isolate_object(obj)
    visual.VIEW_DIRECTIONS = VIEW_DIRECTIONS

    minimum, maximum = visual.world_bounds([obj])
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    scale = max(dimensions)
    visual.configure_world()
    visual.configure_render(args.resolution)
    camera, _ortho_scale, distance = visual.create_camera(
        center, dimensions
    )
    lights = visual.create_lights(scale)
    view_layer = bpy.context.scene.view_layers[0]

    clay = visual.make_principled_material(
        "STAGE_PREVIEW_CLAY",
        (0.46, 0.55, 0.48, 1.0),
        roughness=0.78,
    )
    view_layer.material_override = clay
    clay_renders = visual.render_views(
        args.output / "clay",
        camera,
        lights,
        center,
        distance,
        scale,
    )

    wire = visual.make_wireframe_material()
    view_layer.material_override = wire
    wire_renders = visual.render_views(
        args.output / "wire",
        camera,
        lights,
        center,
        distance,
        scale,
    )
    view_layer.material_override = None

    report = {
        "schema_version": "1.0.0",
        "blender_version": bpy.app.version_string,
        "source_blend": Path(bpy.data.filepath)
        .resolve()
        .relative_to(args.project_root.resolve())
        .as_posix(),
        "object": obj.name,
        "bounds": {
            "minimum": list(minimum),
            "maximum": list(maximum),
            "dimensions": list(dimensions),
        },
        "topology": topology(obj),
        "renders": {
            "clay": clay_renders,
            "wire": wire_renders,
        },
    }
    (args.output / "preview_report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print("BENTOSAUR_STAGE_PREVIEW=" + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
