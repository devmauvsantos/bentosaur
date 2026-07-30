"""Repair and rebake a Tripo Smart LowPoly mesh without touching its source.

This is an evidence-gathering utility, not the locked production pipeline. It:

1. imports the Smart LowPoly FBX and the original surfaced H3.1 GLB;
2. closes boundary loops on a disposable in-memory copy;
3. creates a fresh UV atlas;
4. bakes base colour from H3.1 onto that atlas; and
5. exports a new GLB plus a JSON report.

The conservative fill deliberately leaves any generated n-gons intact. The
VG05 experiment showed that automatic triangulation of these unusual boundary
networks can create a non-manifold edge. Inspect and manually retopologize the
reported n-gons before treating an output as production-ready.
"""

from __future__ import annotations

import argparse
import bmesh
import bpy
import hashlib
import json
from pathlib import Path
import sys
import time


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--low", required=True, type=Path)
    parser.add_argument("--high", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=1024)
    parser.add_argument("--save-blend", action="store_true")
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def import_single_mesh(path: Path, label: str) -> bpy.types.Object:
    before = set(bpy.context.scene.objects)
    suffix = path.suffix.lower()
    if suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise RuntimeError(f"Unsupported format: {suffix}")
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"{label}: expected one mesh, found {len(meshes)}")
    obj = meshes[0]
    obj.name = label
    return obj


def topology_metrics(obj: bpy.types.Object) -> dict[str, int]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "triangles": sum(max(1, len(face.verts) - 2) for face in bm.faces),
        "quad_faces": sum(len(face.verts) == 4 for face in bm.faces),
        "triangle_faces": sum(len(face.verts) == 3 for face in bm.faces),
        "ngons": sum(len(face.verts) > 4 for face in bm.faces),
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "uv_layers": len(obj.data.uv_layers),
    }
    bm.free()
    return result


def conservative_fill(obj: bpy.types.Object) -> dict[str, int]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    boundary = [edge for edge in bm.edges if edge.is_boundary]
    holes = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
    remaining = [edge for edge in bm.edges if edge.is_boundary]
    contextual = bmesh.ops.contextual_create(
        bm, geom=remaining, mat_nr=0, use_smooth=True
    )
    generated_faces = holes.get("faces", []) + contextual.get("faces", [])
    for face in generated_faces:
        if face.is_valid:
            face.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return {
        "boundary_edges_before": len(boundary),
        "holes_fill_faces": len(holes.get("faces", [])),
        "boundary_edges_after_holes_fill": len(remaining),
        "contextual_fill_faces": len(contextual.get("faces", [])),
    }


def create_fresh_uv_atlas(obj: bpy.types.Object) -> str:
    while obj.data.uv_layers:
        obj.data.uv_layers.remove(obj.data.uv_layers[0])
    obj.data.uv_layers.new(name="UV_REBAKE")
    obj.data.uv_layers.active = obj.data.uv_layers["UV_REBAKE"]
    obj.data.uv_layers["UV_REBAKE"].active_render = True
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(
        angle_limit=1.1519173,
        margin_method="SCALED",
        rotate_method="AXIS_ALIGNED",
        island_margin=0.01,
        area_weight=0.0,
        correct_aspect=True,
        scale_to_bounds=False,
    )
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj.data.uv_layers.active.name


def make_bake_target(
    obj: bpy.types.Object, output: Path, resolution: int
) -> tuple[
    bpy.types.Image,
    bpy.types.Material,
    bpy.types.ShaderNodeTexImage,
    bpy.types.ShaderNodeBsdfPrincipled,
]:
    image = bpy.data.images.new(
        "BENTOSAUR_REPAIR_BASECOLOR",
        width=resolution,
        height=resolution,
        alpha=False,
        float_buffer=False,
    )
    image.generated_color = (0.45, 0.50, 0.45, 1.0)
    image.file_format = "PNG"
    image.filepath_raw = str(output / "repaired_basecolor_1k.png")

    material = bpy.data.materials.new("BENTOSAUR_REPAIR_REBAKED")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Roughness"].default_value = 0.68
    target = nodes.new("ShaderNodeTexImage")
    target.name = "BAKE_TARGET"
    target.image = image
    target.interpolation = "Linear"
    nodes.active = target
    target.select = True

    obj.data.materials.clear()
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.material_index = 0
        polygon.use_smooth = True
    return image, material, target, principled


def bake_base_color(
    high: bpy.types.Object, low: bpy.types.Object, image: bpy.types.Image
) -> float:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.render.bake.use_selected_to_active = True
    scene.render.bake.use_cage = False
    scene.render.bake.cage_extrusion = 0.006
    scene.render.bake.max_ray_distance = 0.025
    scene.render.bake.margin = 12
    scene.render.bake.margin_type = "EXTEND"
    scene.render.bake.use_pass_direct = False
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_pass_color = True

    bpy.ops.object.select_all(action="DESELECT")
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    started = time.monotonic()
    bpy.ops.object.bake(type="DIFFUSE")
    elapsed = time.monotonic() - started
    image.save()
    image.pack()
    return elapsed


def export_glb(obj: bpy.types.Object, output: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_materials="EXPORT",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    low_path = args.low.expanduser().resolve()
    high_path = args.high.expanduser().resolve()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    clear_scene()
    low = import_single_mesh(low_path, "LOW_REPAIRED_REBAKE")
    high = import_single_mesh(high_path, "HIGH_BAKE_SOURCE")
    before = topology_metrics(low)
    fill = conservative_fill(low)
    after_fill = topology_metrics(low)
    uv_name = create_fresh_uv_atlas(low)
    image, material, target, principled = make_bake_target(
        low, output, args.resolution
    )
    elapsed = bake_base_color(high, low, image)
    material.node_tree.links.new(
        target.outputs["Color"], principled.inputs["Base Color"]
    )
    high.hide_render = True

    glb_path = output / "repaired_rebaked.glb"
    export_glb(low, glb_path)
    if args.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(output / "rebake_proof.blend"))

    report = {
        "status": "experiment_only_manual_ngon_review_required",
        "inputs": {"low": str(low_path), "high": str(high_path)},
        "topology_before": before,
        "fill_operation": fill,
        "topology_after_fill": after_fill,
        "bake": {
            "map": "base_color_only",
            "resolution": args.resolution,
            "uv_layer": uv_name,
            "seconds": elapsed,
            "cage_extrusion": 0.006,
            "max_ray_distance": 0.025,
            "margin_pixels": 12,
        },
        "output": {
            "glb": str(glb_path),
            "glb_bytes": glb_path.stat().st_size,
            "glb_sha256": sha256(glb_path),
            "base_color": str(output / "repaired_basecolor_1k.png"),
        },
        "known_limitations": [
            "Six generated n-gons still require manual retopology or controlled triangulation.",
            "Only base colour was baked; normal, roughness, metallic, AO and final Painter work remain.",
            "Smart UV Project is sufficient for this proof but is not the approved character UV layout.",
        ],
    }
    (output / "rebake_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
