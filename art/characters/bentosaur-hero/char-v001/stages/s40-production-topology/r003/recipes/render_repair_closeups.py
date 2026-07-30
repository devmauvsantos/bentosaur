"""Render full and close wire QA views with edited quads highlighted amber."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


SCRIPT_ROOT = Path(
    "/Users/mauvsantos/Workspace/games/Bentosaur/art/characters/"
    "bentosaur-hero/char-v001/stages/s40-production-topology/r002/recipes"
)
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))
import evaluate_tripo_visual_candidate as visual


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="mirrored-final-pair")
    parser.add_argument("--quality", default="edited_quad_quality_audit.json")
    parser.add_argument("--indices-key", default="edited_face_indices")
    parser.add_argument("--output", default="repair-wire-closeups")
    return parser.parse_args(argv)


args = parse_args()
ROOT = Path(__file__).resolve().parent / args.root
OUTPUT = ROOT / args.output
OUTPUT.mkdir(parents=True, exist_ok=True)
QUALITY = json.loads((ROOT / args.quality).read_text())
edited_indices = set(QUALITY[args.indices_key])


def wire_material(
    name: str,
    fill: tuple[float, float, float, float],
    line: tuple[float, float, float, float],
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    wire = nodes.new("ShaderNodeWireframe")
    wire.use_pixel_size = True
    wire.inputs["Size"].default_value = 0.8
    mix = nodes.new("ShaderNodeMixRGB")
    mix.inputs[1].default_value = fill
    mix.inputs[2].default_value = line
    links.new(wire.outputs["Fac"], mix.inputs[0])
    links.new(mix.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


obj = next(obj for obj in bpy.context.scene.objects if obj.type == "MESH")
for current in bpy.context.scene.objects:
    current.hide_render = current is not obj
obj.hide_render = False
obj.hide_set(False)

base = wire_material(
    "QA_UNTOUCHED_QUADS",
    (0.42, 0.46, 0.44, 1.0),
    (0.018, 0.022, 0.026, 1.0),
)
edited = wire_material(
    "QA_EDITED_QUADS",
    (0.96, 0.49, 0.10, 1.0),
    (0.12, 0.018, 0.006, 1.0),
)
obj.data.materials.clear()
obj.data.materials.append(base)
obj.data.materials.append(edited)
for polygon in obj.data.polygons:
    polygon.material_index = 1 if polygon.index in edited_indices else 0

minimum, maximum = visual.world_bounds([obj])
full_center = (minimum + maximum) * 0.5
dimensions = maximum - minimum
full_scale = max(dimensions)
visual.configure_world()
visual.configure_render(900)
camera, _, distance = visual.create_camera(full_center, dimensions)
lights = visual.create_lights(full_scale)
bpy.context.scene.view_layers[0].material_override = None

views = {
    # True character front/back are +/-X in this vendor-space source.
    "01_true_front_full": {
        "center": full_center,
        "direction": Vector((1.0, 0.0, 0.0)),
        "ortho": full_scale * 1.08,
    },
    "02_true_back_full": {
        "center": full_center,
        "direction": Vector((-1.0, 0.0, 0.0)),
        "ortho": full_scale * 1.08,
    },
    "03_profile_full": {
        "center": full_center,
        "direction": Vector((0.0, -1.0, 0.0)),
        "ortho": full_scale * 1.08,
    },
    "04_mouth_front_close": {
        "center": Vector((0.31, 0.0, 0.18)),
        "direction": Vector((1.0, 0.0, 0.0)),
        "ortho": 0.46,
    },
    "05_feet_front_close": {
        "center": Vector((-0.04, 0.0, -0.34)),
        "direction": Vector((1.0, 0.0, 0.0)),
        "ortho": 0.42,
    },
    "06_tail_profile_close": {
        "center": Vector((-0.25, 0.0, -0.22)),
        "direction": Vector((0.0, -1.0, 0.0)),
        "ortho": 0.46,
    },
}
rendered = {}
for name, settings in views.items():
    camera.data.ortho_scale = settings["ortho"]
    visual.place_camera_and_lights(
        camera,
        lights,
        settings["center"],
        settings["direction"],
        distance,
        full_scale,
    )
    path = OUTPUT / f"{name}.png"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    rendered[name] = str(path)

report = {
    "source": bpy.data.filepath,
    "edited_quads_highlighted": len(edited_indices),
    "legend": {
        "gray": "untouched QuadriFlow quads",
        "amber": f"selected QA quads from {args.indices_key}",
    },
    "renders": rendered,
}
(OUTPUT / "render_report.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(report, indent=2))
