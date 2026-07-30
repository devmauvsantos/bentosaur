"""Generic Blender driver for bounded G40 deformation validation.

All character-specific assumptions live in JSON. The generated armature and
weights are disposable diagnostic instruments, not a production rig.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree


DIAGNOSTIC_BODY_NAME = "G40_DIAGNOSTIC_BODY"
DIAGNOSTIC_RIG_NAME = "G40_BOUNDED_DIAGNOSTIC_RIG"
OVERLAY_COLLECTION = "G40_EVIDENCE_OVERLAY"


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--body-object", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args(argv)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def axis_vector(token: str) -> Vector:
    normalized = token.strip().upper()
    values = {
        "+X": Vector((1.0, 0.0, 0.0)),
        "X": Vector((1.0, 0.0, 0.0)),
        "-X": Vector((-1.0, 0.0, 0.0)),
        "+Y": Vector((0.0, 1.0, 0.0)),
        "Y": Vector((0.0, 1.0, 0.0)),
        "-Y": Vector((0.0, -1.0, 0.0)),
        "+Z": Vector((0.0, 0.0, 1.0)),
        "Z": Vector((0.0, 0.0, 1.0)),
        "-Z": Vector((0.0, 0.0, -1.0)),
    }
    if normalized not in values:
        raise ValueError(f"Unsupported axis token: {token}")
    return values[normalized]


def point_axis(point: Vector, token: str) -> float:
    return point.dot(axis_vector(token))


def world_bounds(body: bpy.types.Object) -> dict[str, Any]:
    points = [body.matrix_world @ vertex.co for vertex in body.data.vertices]
    minimum = Vector(
        min(point[axis] for point in points) for axis in range(3)
    )
    maximum = Vector(
        max(point[axis] for point in points) for axis in range(3)
    )
    return {
        "minimum": list(minimum),
        "maximum": list(maximum),
        "dimensions": list(maximum - minimum),
        "center": list((minimum + maximum) * 0.5),
    }


def normalized_point(point: Vector, bounds: dict[str, Any]) -> Vector:
    minimum = Vector(bounds["minimum"])
    dimensions = Vector(bounds["dimensions"])
    return Vector(
        (
            (point[index] - minimum[index]) / dimensions[index]
            if abs(dimensions[index]) > 1.0e-12
            else 0.5
        )
        for index in range(3)
    )


def atomic_selector_matches(
    selector: dict[str, Any],
    point: Vector,
    bounds: dict[str, Any],
    default_space: str = "world",
) -> bool:
    space = selector.get("space", default_space)
    sample = normalized_point(point, bounds) if space == "normalized_bbox" else point
    if "bounds" in selector:
        for axis_name, limits in selector["bounds"].items():
            value = sample["XYZ".index(axis_name.upper())]
            if limits[0] is not None and value < float(limits[0]):
                return False
            if limits[1] is not None and value > float(limits[1]):
                return False
    if "axis" in selector:
        value = point_axis(sample, selector["axis"])
        if selector.get("min") is not None and value < float(selector["min"]):
            return False
        if selector.get("max") is not None and value > float(selector["max"]):
            return False
    return True


def selector_matches(
    selector: dict[str, Any],
    point: Vector,
    bounds: dict[str, Any],
    default_space: str = "world",
) -> bool:
    if "all" in selector:
        return all(
            selector_matches(item, point, bounds, default_space)
            for item in selector["all"]
        )
    if "any" in selector:
        return any(
            selector_matches(item, point, bounds, default_space)
            for item in selector["any"]
        )
    if "not" in selector:
        return not selector_matches(
            selector["not"],
            point,
            bounds,
            default_space,
        )
    return atomic_selector_matches(
        selector,
        point,
        bounds,
        default_space,
    )


def mesh_topology(body: bpy.types.Object) -> dict[str, Any]:
    mesh = body.data
    side_counts: dict[str, int] = {}
    for polygon in mesh.polygons:
        key = str(len(polygon.vertices))
        side_counts[key] = side_counts.get(key, 0) + 1
    edge_keys = {
        tuple(sorted(edge.vertices)): edge.index for edge in mesh.edges
    }
    edge_face_count = [0] * len(mesh.edges)
    for polygon in mesh.polygons:
        for a, b in polygon.edge_keys:
            edge_face_count[edge_keys[tuple(sorted((a, b)))]] += 1
    return {
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
        "faces_by_sides": side_counts,
        "boundary_edges": sum(count == 1 for count in edge_face_count),
        "non_manifold_edges": sum(count != 2 for count in edge_face_count),
    }


def mirror_audit(
    body: bpy.types.Object,
    axis: str,
    plane: float,
    tolerance: float,
) -> dict[str, Any]:
    normal = axis_vector(axis)
    points = [body.matrix_world @ vertex.co for vertex in body.data.vertices]
    tree = KDTree(len(points))
    for index, point in enumerate(points):
        tree.insert(point, index)
    tree.balance()
    errors = []
    for point in points:
        distance_from_plane = point.dot(normal) - plane
        mirrored = point - 2.0 * distance_from_plane * normal
        errors.append(tree.find(mirrored)[2])
    errors.sort()
    p95_index = max(0, math.ceil(len(errors) * 0.95) - 1)
    return {
        "axis": axis,
        "plane": plane,
        "tolerance": tolerance,
        "within_tolerance_ratio": (
            sum(error <= tolerance for error in errors) / len(errors)
        ),
        "p95": errors[p95_index],
        "maximum": max(errors),
    }


def coordinate_audit(
    body: bpy.types.Object,
    config: dict[str, Any],
    bounds: dict[str, Any],
) -> dict[str, Any]:
    contract = config["coordinate_contract"]
    floor = contract["floor"]
    up = axis_vector(contract["up"])
    points = [body.matrix_world @ vertex.co for vertex in body.data.vertices]
    floor_projection = min(point.dot(up) for point in points)
    floor_error = abs(floor_projection - float(floor["value"]))
    floor_pass = floor_error <= float(floor["tolerance"])

    mirror_config = contract["mirror"]
    mirror = mirror_audit(
        body,
        mirror_config["axis"],
        float(mirror_config.get("plane", 0.0)),
        float(mirror_config["tolerance"]),
    )
    mirror_pass = (
        mirror["p95"] <= float(mirror_config["p95_max"])
        and mirror["within_tolerance_ratio"]
        >= float(mirror_config["minimum_ratio"])
    )

    bounds_checks = []
    for axis_name, expectation in contract.get("expected_bounds", {}).items():
        index = "XYZ".index(axis_name.upper())
        actual_min = bounds["minimum"][index]
        actual_max = bounds["maximum"][index]
        tolerance = float(expectation.get("tolerance", 0.0))
        minimum_pass = (
            expectation.get("min") is None
            or abs(actual_min - float(expectation["min"])) <= tolerance
        )
        maximum_pass = (
            expectation.get("max") is None
            or abs(actual_max - float(expectation["max"])) <= tolerance
        )
        bounds_checks.append(
            {
                "axis": axis_name.upper(),
                "actual_min": actual_min,
                "actual_max": actual_max,
                "expected": expectation,
                "pass": minimum_pass and maximum_pass,
            }
        )

    probes = []
    for probe in contract.get("orientation_probes", []):
        selected = [
            point
            for point in points
            if selector_matches(probe["selector"], point, bounds)
        ]
        projection_axis = probe["projection_axis"]
        projections = [point_axis(point, projection_axis) for point in selected]
        mean = sum(projections) / len(projections) if projections else None
        expected = probe.get("expected_mean", {})
        passed = bool(projections)
        if mean is not None and expected.get("min") is not None:
            passed = passed and mean >= float(expected["min"])
        if mean is not None and expected.get("max") is not None:
            passed = passed and mean <= float(expected["max"])
        probes.append(
            {
                "name": probe["name"],
                "count": len(selected),
                "projection_axis": projection_axis,
                "minimum": min(projections) if projections else None,
                "mean": mean,
                "maximum": max(projections) if projections else None,
                "expected_mean": expected,
                "pass": passed,
            }
        )

    return {
        "declared_contract": {
            "front": contract["front"],
            "character_left": contract["character_left"],
            "up": contract["up"],
        },
        "bounds": bounds,
        "floor": {
            "projection": floor_projection,
            "expected": floor["value"],
            "absolute_error": floor_error,
            "pass": floor_pass,
        },
        "mirror": {**mirror, "pass": mirror_pass},
        "bounds_checks": bounds_checks,
        "orientation_probes": probes,
        "contract_pass": (
            floor_pass
            and mirror_pass
            and all(item["pass"] for item in bounds_checks)
            and all(item["pass"] for item in probes)
        ),
    }


def isolate_body(
    source_name: str,
    coordinate_config: dict[str, Any],
) -> tuple[bpy.types.Object, dict[str, Any]]:
    target = bpy.data.objects.get(source_name)
    if target is None or target.type != "MESH":
        meshes = sorted(
            obj.name for obj in bpy.data.objects if obj.type == "MESH"
        )
        raise RuntimeError(
            f"Configured body object {source_name!r} was not found as a mesh. "
            f"Available meshes: {meshes}"
        )
    removed_armature_modifiers = []
    for modifier in list(target.modifiers):
        if modifier.type == "ARMATURE":
            removed_armature_modifiers.append(modifier.name)
            target.modifiers.remove(modifier)
    target.parent = None
    for obj in list(bpy.data.objects):
        if obj != target:
            bpy.data.objects.remove(obj, do_unlink=True)
    if not target.users_collection:
        bpy.context.scene.collection.objects.link(target)
    source_data_name = target.data.name
    target.name = DIAGNOSTIC_BODY_NAME
    target.data.name = f"{DIAGNOSTIC_BODY_NAME}_MESH"
    target["g40_diagnostic_only"] = True
    target["g40_source_object"] = source_name
    target["g40_source_mesh_data"] = source_data_name
    target["g40_coordinate_contract"] = (
        f"front {coordinate_config['front']}; "
        f"left {coordinate_config['character_left']}; "
        f"up {coordinate_config['up']}"
    )
    bpy.context.scene["g40_diagnostic_only"] = True
    bpy.context.scene["g40_non_approval_notice"] = (
        "Temporary deformation stress rig; not a production rig or approval."
    )
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.view_layer.update()
    return target, {
        "removed_prior_armature_modifiers": removed_armature_modifiers,
        "object_transform_preserved": {
            "location": list(target.location),
            "rotation_euler": list(target.rotation_euler),
            "scale": list(target.scale),
        },
    }


def create_armature(config: dict[str, Any]) -> bpy.types.Object:
    rig_config = config["rig"]
    data = bpy.data.armatures.new(f"{DIAGNOSTIC_RIG_NAME}_DATA")
    armature = bpy.data.objects.new(DIAGNOSTIC_RIG_NAME, data)
    bpy.context.scene.collection.objects.link(armature)
    armature.show_in_front = True
    armature.display_type = "WIRE"
    armature["g40_diagnostic_only"] = True
    armature["g40_rig_scope"] = rig_config.get(
        "scope",
        "Bounded deformation diagnostic only; no production controls.",
    )

    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="EDIT")
    for name, spec in rig_config["bones"].items():
        bone = data.edit_bones.new(name)
        bone.head = Vector(spec["head"])
        bone.tail = Vector(spec["tail"])
        bone.use_deform = spec.get("deform", True)
    for name, spec in rig_config["bones"].items():
        parent_name = spec.get("parent")
        if parent_name:
            bone = data.edit_bones[name]
            bone.parent = data.edit_bones[parent_name]
            bone.use_connect = spec.get("connected", False)
    bpy.ops.object.mode_set(mode="OBJECT")
    return armature


def weight_stats(
    body: bpy.types.Object,
    armature: bpy.types.Object,
    max_influences: int,
) -> dict[str, Any]:
    deform_names = {
        bone.name for bone in armature.data.bones if bone.use_deform
    }
    group_names = {
        group.index: group.name for group in body.vertex_groups
    }
    influence_counts = []
    unweighted = []
    totals = []
    for vertex in body.data.vertices:
        weights = [
            element.weight
            for element in vertex.groups
            if group_names.get(element.group) in deform_names
            and element.weight > 1.0e-6
        ]
        influence_counts.append(len(weights))
        totals.append(sum(weights))
        if not weights:
            unweighted.append(vertex.index)
    return {
        "vertex_groups": sorted(group.name for group in body.vertex_groups),
        "unweighted_vertex_count": len(unweighted),
        "unweighted_vertex_sample": unweighted[:30],
        "influences": {
            "minimum": min(influence_counts) if influence_counts else 0,
            "maximum": max(influence_counts) if influence_counts else 0,
            "mean": (
                sum(influence_counts) / len(influence_counts)
                if influence_counts
                else 0.0
            ),
            "configured_maximum": max_influences,
            "over_configured_maximum_count": sum(
                count > max_influences for count in influence_counts
            ),
        },
        "weight_sum": {
            "minimum": min(totals) if totals else 0.0,
            "maximum": max(totals) if totals else 0.0,
            "mean": sum(totals) / len(totals) if totals else 0.0,
        },
    }


def automatic_parent(
    body: bpy.types.Object,
    armature: bpy.types.Object,
    max_influences: int,
) -> dict[str, Any]:
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    result = bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    bpy.context.view_layer.update()
    return {
        "operator_result": sorted(result),
        "weight_stats": weight_stats(body, armature, max_influences),
    }


def point_segment_distance(
    point: Vector,
    a: Vector,
    b: Vector,
) -> float:
    segment = b - a
    if segment.length_squared <= 1.0e-12:
        return (point - a).length
    amount = max(
        0.0,
        min(1.0, (point - a).dot(segment) / segment.length_squared),
    )
    return (point - (a + segment * amount)).length


def nearest_deform_bone(
    world_point: Vector,
    armature: bpy.types.Object,
) -> str:
    local_point = armature.matrix_world.inverted() @ world_point
    scored = [
        (
            point_segment_distance(
                local_point,
                bone.head_local,
                bone.tail_local,
            ),
            bone.name,
        )
        for bone in armature.data.bones
        if bone.use_deform
    ]
    return min(scored)[1]


def normalize_weights(
    weights: dict[str, float],
    max_influences: int,
) -> dict[str, float]:
    strongest = sorted(
        (
            (name, value)
            for name, value in weights.items()
            if value > 1.0e-6
        ),
        key=lambda item: item[1],
        reverse=True,
    )[:max_influences]
    total = sum(value for _name, value in strongest)
    if total <= 1.0e-12:
        return {}
    return {name: value / total for name, value in strongest}


def bounded_weight_cleanup(
    body: bpy.types.Object,
    armature: bpy.types.Object,
    config: dict[str, Any],
    bounds: dict[str, Any],
) -> dict[str, Any]:
    weight_config = config["weights"]
    max_influences = int(weight_config["max_influences"])
    group_names = {
        group.index: group.name for group in body.vertex_groups
    }
    deform_names = {
        bone.name for bone in armature.data.bones if bone.use_deform
    }
    assignments: list[dict[str, float]] = []
    counters = {
        "rigid_override_vertices": 0,
        "cross_side_vertices": 0,
        "removal_rule_vertices": 0,
        "fallback_nearest_bone_vertices": 0,
        "capped_or_normalized_vertices": 0,
    }
    rule_counts = {
        rule["name"]: 0 for rule in weight_config.get("removal_rules", [])
    }
    override_counts = {
        rule["name"]: 0 for rule in weight_config.get("rigid_overrides", [])
    }
    side_rule = weight_config.get("cross_side_filter")

    for vertex in body.data.vertices:
        point = body.matrix_world @ vertex.co
        weights = {
            group_names[element.group]: element.weight
            for element in vertex.groups
            if group_names.get(element.group) in deform_names
            and element.weight > 1.0e-6
        }
        overridden = False
        for rule in weight_config.get("rigid_overrides", []):
            if selector_matches(rule["selector"], point, bounds):
                bone_name = rule["bone"]
                if bone_name not in deform_names:
                    raise RuntimeError(
                        f"Rigid override references non-deform bone: {bone_name}"
                    )
                weights = {bone_name: 1.0}
                overridden = True
                counters["rigid_override_vertices"] += 1
                override_counts[rule["name"]] += 1
                break

        if not overridden and side_rule:
            before = set(weights)
            side_value = point_axis(point, side_rule["axis"])
            dead_zone = float(side_rule.get("dead_zone", 0.0))
            if side_value > dead_zone:
                prohibited = side_rule["negative_side_suffix"]
                weights = {
                    name: value
                    for name, value in weights.items()
                    if not name.endswith(prohibited)
                }
            elif side_value < -dead_zone:
                prohibited = side_rule["positive_side_suffix"]
                weights = {
                    name: value
                    for name, value in weights.items()
                    if not name.endswith(prohibited)
                }
            if set(weights) != before:
                counters["cross_side_vertices"] += 1

        if not overridden:
            any_removal = False
            for rule in weight_config.get("removal_rules", []):
                if not selector_matches(rule["when"], point, bounds):
                    continue
                before = set(weights)
                if rule.get("bone_prefix"):
                    weights = {
                        name: value
                        for name, value in weights.items()
                        if not name.startswith(rule["bone_prefix"])
                    }
                if rule.get("bone_suffix"):
                    weights = {
                        name: value
                        for name, value in weights.items()
                        if not name.endswith(rule["bone_suffix"])
                    }
                for name in rule.get("bones", []):
                    weights.pop(name, None)
                if set(weights) != before:
                    any_removal = True
                    rule_counts[rule["name"]] += 1
            if any_removal:
                counters["removal_rule_vertices"] += 1

        original = dict(weights)
        weights = normalize_weights(weights, max_influences)
        if not weights:
            weights = {nearest_deform_bone(point, armature): 1.0}
            counters["fallback_nearest_bone_vertices"] += 1
        if (
            len(original) > max_influences
            or abs(sum(original.values()) - 1.0) > 1.0e-5
        ):
            counters["capped_or_normalized_vertices"] += 1
        assignments.append(weights)

    for group in list(body.vertex_groups):
        body.vertex_groups.remove(group)
    groups = {
        name: body.vertex_groups.new(name=name)
        for name in sorted(deform_names)
    }
    for vertex_index, weights in enumerate(assignments):
        for name, weight in weights.items():
            groups[name].add([vertex_index], weight, "REPLACE")
    body["g40_weight_scope"] = (
        f"One bounded cleanup pass, maximum {max_influences} influences; "
        "not production weight painting."
    )
    bpy.context.view_layer.update()
    return {
        "operations": counters,
        "rigid_override_rule_counts": override_counts,
        "removal_rule_counts": rule_counts,
        "stats": weight_stats(body, armature, max_influences),
        "polish_iterations": 0,
    }


def reset_pose(armature: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = armature
    for pose_bone in armature.pose.bones:
        pose_bone.rotation_mode = "QUATERNION"
        pose_bone.matrix_basis.identity()
    bpy.context.view_layer.update()


def rest_head(armature: bpy.types.Object, bone_name: str) -> Vector:
    return armature.data.bones[bone_name].head_local.copy()


def rest_direction(
    armature: bpy.types.Object,
    bone_name: str,
) -> Vector:
    bone = armature.data.bones[bone_name]
    return bone.tail_local - bone.head_local


def set_absolute_bone(
    armature: bpy.types.Object,
    bone_name: str,
    head: Vector,
    direction: Vector,
) -> Vector:
    pose_bone = armature.pose.bones[bone_name]
    rest_bone = armature.data.bones[bone_name]
    rest_vector = (
        rest_bone.tail_local - rest_bone.head_local
    ).normalized()
    target = direction.normalized()
    rotation = rest_vector.rotation_difference(target)
    desired_rotation = rotation.to_matrix() @ rest_bone.matrix_local.to_3x3()
    desired = desired_rotation.to_4x4()
    desired.translation = head
    pose_bone.matrix = desired
    bpy.context.view_layer.update()
    return head + target * rest_bone.length


def angle_between_degrees(a: Vector, b: Vector) -> float:
    if a.length <= 1.0e-12 or b.length <= 1.0e-12:
        return 0.0
    return math.degrees(a.normalized().angle(b.normalized()))


def apply_pose(
    armature: bpy.types.Object,
    pose: dict[str, Any],
) -> list[dict[str, Any]]:
    reset_pose(armature)
    applied = []
    for action in pose.get("actions", []):
        operation = action["operation"]
        if operation == "translate_bones":
            delta = Vector(action["delta"])
            for bone_name in action["bones"]:
                set_absolute_bone(
                    armature,
                    bone_name,
                    rest_head(armature, bone_name) + delta,
                    rest_direction(armature, bone_name),
                )
            applied.append(
                {
                    "operation": operation,
                    "bones": action["bones"],
                    "delta": list(delta),
                }
            )
        elif operation == "translate_chain":
            delta = Vector(action["delta"])
            names = action["bones"]
            head = rest_head(armature, names[0]) + delta
            for bone_name in names:
                head = set_absolute_bone(
                    armature,
                    bone_name,
                    head,
                    rest_direction(armature, bone_name),
                )
            applied.append(
                {
                    "operation": operation,
                    "bones": names,
                    "delta": list(delta),
                }
            )
        elif operation == "aim_chain":
            names = action["bones"]
            directions = [Vector(value) for value in action["directions"]]
            if len(names) != len(directions):
                raise RuntimeError(
                    f"Pose {pose['name']} aim_chain has unequal bones/directions."
                )
            head = rest_head(armature, names[0]) + Vector(
                action.get("root_offset", (0.0, 0.0, 0.0))
            )
            computed_angles = []
            for bone_name, direction in zip(names, directions):
                computed_angles.append(
                    angle_between_degrees(
                        rest_direction(armature, bone_name),
                        direction,
                    )
                )
                head = set_absolute_bone(
                    armature,
                    bone_name,
                    head,
                    direction,
                )
            applied.append(
                {
                    "operation": operation,
                    "bones": names,
                    "directions": [list(value) for value in directions],
                    "computed_rest_angle_degrees": computed_angles,
                    "declared_angles_degrees": action.get(
                        "declared_angles_degrees"
                    ),
                }
            )
        elif operation == "rotate_local":
            pose_bone = armature.pose.bones[action["bone"]]
            pose_bone.rotation_mode = "XYZ"
            angles = [math.radians(float(value)) for value in action["euler_deg"]]
            pose_bone.rotation_euler = angles
            bpy.context.view_layer.update()
            applied.append(
                {
                    "operation": operation,
                    "bone": action["bone"],
                    "euler_deg": action["euler_deg"],
                }
            )
        else:
            raise ValueError(f"Unknown pose operation: {operation}")
    armature["g40_pose_name"] = pose["name"]
    armature["g40_pose_intent"] = pose.get("intent", "")
    return applied


def face_area(vertices: list[Vector]) -> float:
    if len(vertices) < 3:
        return 0.0
    origin = vertices[0]
    return sum(
        (
            (vertices[index] - origin)
            .cross(vertices[index + 1] - origin)
            .length
            * 0.5
        )
        for index in range(1, len(vertices) - 1)
    )


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    raw = (len(ordered) - 1) * fraction
    lower = math.floor(raw)
    upper = math.ceil(raw)
    if lower == upper:
        return ordered[lower]
    blend = raw - lower
    return ordered[lower] * (1.0 - blend) + ordered[upper] * blend


def classify_region(
    point: Vector,
    config: dict[str, Any],
    bounds: dict[str, Any],
) -> str:
    for region in config["regions"]["ordered"]:
        if selector_matches(
            region["selector"],
            point,
            bounds,
            config["regions"].get("space", "world"),
        ):
            return region["name"]
    return config["regions"]["fallback"]


def evaluated_world_vertices(
    body: bpy.types.Object,
) -> tuple[list[Vector], bpy.types.Mesh]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = body.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(
        evaluated,
        preserve_all_data_layers=True,
        depsgraph=depsgraph,
    )
    points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    return points, mesh


def deformation_metrics(
    body: bpy.types.Object,
    baseline_points: list[Vector],
    baseline_mesh: bpy.types.Mesh,
    config: dict[str, Any],
    bounds: dict[str, Any],
) -> dict[str, Any]:
    points, posed_mesh = evaluated_world_vertices(body)
    if len(points) != len(baseline_points):
        raise RuntimeError("Armature evaluation changed vertex count.")

    baseline_face_areas = []
    posed_face_areas = []
    face_regions = []
    for baseline_polygon, posed_polygon in zip(
        baseline_mesh.polygons,
        posed_mesh.polygons,
    ):
        base_vertices = [
            baseline_points[index] for index in baseline_polygon.vertices
        ]
        posed_vertices = [
            points[index] for index in posed_polygon.vertices
        ]
        baseline_face_areas.append(face_area(base_vertices))
        posed_face_areas.append(face_area(posed_vertices))
        centroid = sum(base_vertices, Vector()) / len(base_vertices)
        face_regions.append(classify_region(centroid, config, bounds))

    baseline_edge_lengths = [
        (
            baseline_points[edge.vertices[1]]
            - baseline_points[edge.vertices[0]]
        ).length
        for edge in baseline_mesh.edges
    ]
    posed_edge_lengths = [
        (points[edge.vertices[1]] - points[edge.vertices[0]]).length
        for edge in posed_mesh.edges
    ]
    edge_regions = [
        classify_region(
            (
                baseline_points[edge.vertices[0]]
                + baseline_points[edge.vertices[1]]
            )
            * 0.5,
            config,
            bounds,
        )
        for edge in baseline_mesh.edges
    ]

    thresholds = config["thresholds"]
    area_collapse = float(thresholds["face_area_ratio"]["collapse_below"])
    area_stretch = float(
        thresholds["face_area_ratio"]["severe_stretch_above"]
    )
    edge_collapse = float(
        thresholds["edge_length_ratio"]["collapse_below"]
    )
    edge_stretch = float(
        thresholds["edge_length_ratio"]["severe_stretch_above"]
    )
    report = {}
    for region in sorted(set(face_regions) | set(edge_regions)):
        area_ratios = [
            posed / baseline
            for posed, baseline, candidate in zip(
                posed_face_areas,
                baseline_face_areas,
                face_regions,
            )
            if candidate == region and baseline > 1.0e-12
        ]
        edge_ratios = [
            posed / baseline
            for posed, baseline, candidate in zip(
                posed_edge_lengths,
                baseline_edge_lengths,
                edge_regions,
            )
            if candidate == region and baseline > 1.0e-12
        ]
        report[region] = {
            "face_count": len(area_ratios),
            "edge_count": len(edge_ratios),
            "face_area_ratio": {
                "minimum": min(area_ratios) if area_ratios else 0.0,
                "p05": percentile(area_ratios, 0.05),
                "median": percentile(area_ratios, 0.50),
                "p95": percentile(area_ratios, 0.95),
                "maximum": max(area_ratios) if area_ratios else 0.0,
                "collapse_below": area_collapse,
                "collapsed_count": sum(
                    ratio < area_collapse for ratio in area_ratios
                ),
                "severe_stretch_above": area_stretch,
                "severe_stretch_count": sum(
                    ratio > area_stretch for ratio in area_ratios
                ),
            },
            "edge_length_ratio": {
                "minimum": min(edge_ratios) if edge_ratios else 0.0,
                "p05": percentile(edge_ratios, 0.05),
                "median": percentile(edge_ratios, 0.50),
                "p95": percentile(edge_ratios, 0.95),
                "maximum": max(edge_ratios) if edge_ratios else 0.0,
                "collapse_below": edge_collapse,
                "collapsed_count": sum(
                    ratio < edge_collapse for ratio in edge_ratios
                ),
                "severe_stretch_above": edge_stretch,
                "severe_stretch_count": sum(
                    ratio > edge_stretch for ratio in edge_ratios
                ),
            },
        }
    bpy.data.meshes.remove(posed_mesh)
    return report


def threshold_flags(
    regions: dict[str, Any],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    allowed = int(config["thresholds"].get("allowed_count_per_flag", 0))
    failures = []
    for region, metrics in regions.items():
        reasons = []
        area = metrics["face_area_ratio"]
        edge = metrics["edge_length_ratio"]
        if area["collapsed_count"] > allowed:
            reasons.append(
                {
                    "metric": "face_area_ratio",
                    "kind": "collapse",
                    "count": area["collapsed_count"],
                    "threshold": area["collapse_below"],
                }
            )
        if area["severe_stretch_count"] > allowed:
            reasons.append(
                {
                    "metric": "face_area_ratio",
                    "kind": "severe_stretch",
                    "count": area["severe_stretch_count"],
                    "threshold": area["severe_stretch_above"],
                }
            )
        if edge["collapsed_count"] > allowed:
            reasons.append(
                {
                    "metric": "edge_length_ratio",
                    "kind": "collapse",
                    "count": edge["collapsed_count"],
                    "threshold": edge["collapse_below"],
                }
            )
        if edge["severe_stretch_count"] > allowed:
            reasons.append(
                {
                    "metric": "edge_length_ratio",
                    "kind": "severe_stretch",
                    "count": edge["severe_stretch_count"],
                    "threshold": edge["severe_stretch_above"],
                }
            )
        if reasons:
            failures.append({"region": region, "reasons": reasons})
    return failures


def material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    emission: bool = False,
) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    principled = result.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Roughness"].default_value = 0.72
        if emission:
            principled.inputs["Emission Color"].default_value = color
            principled.inputs["Emission Strength"].default_value = 2.2
    return result


def clear_evidence_overlay() -> None:
    collection = bpy.data.collections.get(OVERLAY_COLLECTION)
    if collection is None:
        return
    for obj in list(collection.objects):
        if obj.type == "MESH" and obj.data:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        else:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def evidence_collection() -> bpy.types.Collection:
    clear_evidence_overlay()
    collection = bpy.data.collections.new(OVERLAY_COLLECTION)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    for candidate in list(obj.users_collection):
        candidate.objects.unlink(obj)
    collection.objects.link(obj)


def add_bone_rod(
    head: Vector,
    tail: Vector,
    name: str,
    collection: bpy.types.Collection,
    selected_material: bpy.types.Material,
    radius: float,
) -> None:
    vector = tail - head
    if vector.length <= 1.0e-8:
        return
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=radius,
        depth=vector.length,
        location=(head + tail) * 0.5,
    )
    rod = bpy.context.object
    rod.name = f"G40_EVIDENCE_BONE_{name}"
    rod.rotation_mode = "QUATERNION"
    rod.rotation_quaternion = Vector(
        (0.0, 0.0, 1.0)
    ).rotation_difference(vector.normalized())
    rod.data.materials.append(selected_material)
    move_to_collection(rod, collection)


def build_evidence_overlay(
    body: bpy.types.Object,
    armature: bpy.types.Object,
    config: dict[str, Any],
    bounds: dict[str, Any],
) -> None:
    collection = evidence_collection()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = body.evaluated_get(depsgraph)
    wire_mesh = bpy.data.meshes.new_from_object(
        evaluated,
        preserve_all_data_layers=True,
        depsgraph=depsgraph,
    )
    wire = bpy.data.objects.new("G40_EVIDENCE_DEFORMED_WIRE", wire_mesh)
    collection.objects.link(wire)
    wire.data.materials.append(
        material("G40_WIRE", (0.012, 0.020, 0.030, 1.0))
    )
    modifier = wire.modifiers.new("G40 Evidence Wire", "WIREFRAME")
    longest = max(bounds["dimensions"])
    modifier.thickness = longest * float(
        config["render"].get("wire_thickness_factor", 0.00125)
    )
    modifier.use_replace = True

    colors = {
        "left": material(
            "G40_BONE_LEFT",
            (0.18, 0.60, 1.0, 1.0),
            emission=True,
        ),
        "right": material(
            "G40_BONE_RIGHT",
            (1.0, 0.22, 0.28, 1.0),
            emission=True,
        ),
        "tail": material(
            "G40_BONE_TAIL",
            (0.78, 0.34, 1.0, 1.0),
            emission=True,
        ),
        "axial": material(
            "G40_BONE_AXIAL",
            (1.0, 0.66, 0.12, 1.0),
            emission=True,
        ),
    }
    names = config["rig"].get("naming", {})
    left_suffix = names.get("left_suffix", ".L")
    right_suffix = names.get("right_suffix", ".R")
    tail_prefix = names.get("tail_prefix", "tail_")
    radius = longest * float(
        config["render"].get("bone_radius_factor", 0.006)
    )
    for pose_bone in armature.pose.bones:
        if not pose_bone.bone.use_deform:
            continue
        if pose_bone.name.endswith(left_suffix):
            selected = colors["left"]
        elif pose_bone.name.endswith(right_suffix):
            selected = colors["right"]
        elif pose_bone.name.startswith(tail_prefix):
            selected = colors["tail"]
        else:
            selected = colors["axial"]
        add_bone_rod(
            armature.matrix_world @ pose_bone.head,
            armature.matrix_world @ pose_bone.tail,
            pose_bone.name,
            collection,
            selected,
            radius,
        )


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (
        target - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def ensure_render_scene(
    body: bpy.types.Object,
    config: dict[str, Any],
    bounds: dict[str, Any],
) -> bpy.types.Object:
    render = config["render"]
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = int(render["resolution"][0])
    scene.render.resolution_y = int(render["resolution"][1])
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.world.color = tuple(render["world_color"][:3])
    try:
        scene.view_settings.look = render.get(
            "view_look",
            "AgX - Medium High Contrast",
        )
    except TypeError:
        pass

    body.data.materials.clear()
    body.data.materials.append(
        material("G40_DIAGNOSTIC_BODY_MATERIAL", tuple(render["body_color"]))
    )
    for polygon in body.data.polygons:
        polygon.use_smooth = True

    camera_data = bpy.data.cameras.get("G40_CAMERA_DATA")
    if camera_data is None:
        camera_data = bpy.data.cameras.new("G40_CAMERA_DATA")
    camera = bpy.data.objects.get("G40_CAMERA")
    if camera is None:
        camera = bpy.data.objects.new("G40_CAMERA", camera_data)
        scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(bounds["dimensions"]) * float(
        render.get("ortho_scale_factor", 1.30)
    )
    scene.camera = camera

    floor = bpy.data.objects.get("G40_FLOOR")
    if floor is None:
        contract = config["coordinate_contract"]
        up = axis_vector(contract["up"])
        floor_value = float(contract["floor"]["value"])
        floor_point = up * floor_value
        bpy.ops.mesh.primitive_plane_add(
            size=max(bounds["dimensions"]) * 3.0,
            location=floor_point - up * max(bounds["dimensions"]) * 0.003,
        )
        floor = bpy.context.object
        floor.name = "G40_FLOOR"
        floor.rotation_mode = "QUATERNION"
        floor.rotation_quaternion = Vector(
            (0.0, 0.0, 1.0)
        ).rotation_difference(up)
        floor.data.materials.append(
            material("G40_FLOOR_MATERIAL", tuple(render["floor_color"]))
        )

    target = Vector(render.get("target", bounds["center"]))
    longest = max(bounds["dimensions"])
    for index, light in enumerate(render.get("lights", [])):
        name = f"G40_LIGHT_{index:02d}"
        if bpy.data.objects.get(name) is not None:
            continue
        light_data = bpy.data.lights.new(f"{name}_DATA", "AREA")
        light_data.energy = float(light["energy"])
        light_data.shape = "DISK"
        light_data.size = longest * float(light["size_factor"])
        light_object = bpy.data.objects.new(name, light_data)
        light_object.location = target + Vector(light["offset"]) * longest
        scene.collection.objects.link(light_object)
        look_at(light_object, target)
    return camera


def render_pose(
    body: bpy.types.Object,
    armature: bpy.types.Object,
    pose_name: str,
    config: dict[str, Any],
    bounds: dict[str, Any],
    output: Path,
) -> dict[str, str]:
    build_evidence_overlay(body, armature, config, bounds)
    camera = ensure_render_scene(body, config, bounds)
    pose_dir = output / "renders" / slug(pose_name)
    pose_dir.mkdir(parents=True, exist_ok=False)
    target = Vector(config["render"].get("target", bounds["center"]))
    longest = max(bounds["dimensions"])
    distance = longest * float(
        config["render"].get("camera_distance_factor", 2.25)
    )
    results = {}
    for view in config["render"]["views"]:
        direction = Vector(view["direction"]).normalized()
        camera.location = target + direction * distance
        look_at(camera, target)
        path = pose_dir / f"{slug(view['name'])}.png"
        bpy.context.scene.render.filepath = path.as_posix()
        bpy.ops.render.render(write_still=True)
        results[view["name"]] = path.as_posix()
    clear_evidence_overlay()
    return results


def save_stage(output: Path, filename: str) -> str:
    path = output / "stages" / filename
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {path}")
    bpy.ops.wm.save_as_mainfile(filepath=path.as_posix(), check_existing=False)
    return path.as_posix()


def write_status(
    output: Path,
    state: str,
    detail: dict[str, Any] | None = None,
) -> None:
    write_json(
        output / "reports" / "run_status.json",
        {
            "schema_version": "1.0.0",
            "state": state,
            "diagnostic_only": True,
            "detail": detail or {},
        },
    )


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    config_path = args.config.expanduser().resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("diagnostic_only") is not True:
        raise RuntimeError("Config must mark this run diagnostic_only.")
    opened = Path(bpy.data.filepath).resolve()
    if opened != source:
        raise RuntimeError(f"Opened .blend mismatch: {opened} != {source}")

    write_status(output, "blender_started")
    source_body = bpy.data.objects.get(args.body_object)
    if source_body is None or source_body.type != "MESH":
        raise RuntimeError(f"Body mesh not found: {args.body_object}")
    original_topology = mesh_topology(source_body)
    original_bounds = world_bounds(source_body)
    coordinate = coordinate_audit(
        source_body,
        config,
        original_bounds,
    )
    write_json(output / "metrics" / "coordinate_audit.json", coordinate)

    body, isolation = isolate_body(
        args.body_object,
        config["coordinate_contract"],
    )
    body_stage = save_stage(output, "05_body_isolated.blend")
    write_status(output, "body_isolated", {"stage": body_stage})

    armature = create_armature(config)
    rig_stage = save_stage(
        output,
        "10_diagnostic_rig_neutral_no_weights.blend",
    )
    write_status(output, "diagnostic_rig_created", {"stage": rig_stage})

    max_influences = int(config["weights"]["max_influences"])
    automatic = automatic_parent(body, armature, max_influences)
    automatic_stage = save_stage(output, "20_automatic_weights.blend")
    write_status(output, "automatic_weights", {"stage": automatic_stage})

    cleanup = bounded_weight_cleanup(
        body,
        armature,
        config,
        original_bounds,
    )
    weight_stage = save_stage(
        output,
        "30_bounded_diagnostic_weights.blend",
    )
    weights_payload = {
        "schema_version": "1.0.0",
        "diagnostic_only": True,
        "automatic": automatic,
        "bounded_cleanup": cleanup,
        "checkpoints": {
            "automatic": automatic_stage,
            "bounded_cleanup": weight_stage,
        },
    }
    write_json(output / "metrics" / "weight_audit.json", weights_payload)
    write_status(output, "bounded_weights", {"stage": weight_stage})

    reset_pose(armature)
    baseline_points, baseline_mesh = evaluated_world_vertices(body)
    poses: dict[str, Any] = {}
    used_stages = set()
    for pose in config["poses"]:
        checkpoint = int(pose["checkpoint"])
        if checkpoint in used_stages:
            raise RuntimeError(f"Duplicate pose checkpoint: {checkpoint}")
        used_stages.add(checkpoint)
        applied = apply_pose(armature, pose)
        bpy.context.view_layer.update()
        regions = deformation_metrics(
            body,
            baseline_points,
            baseline_mesh,
            config,
            original_bounds,
        )
        flags = threshold_flags(regions, config)
        renders = render_pose(
            body,
            armature,
            pose["name"],
            config,
            original_bounds,
            output,
        )
        stage_name = f"{checkpoint:02d}_pose_{slug(pose['name'])}.blend"
        stage = save_stage(output, stage_name)
        result = {
            "intent": pose.get("intent", ""),
            "is_neutral": bool(pose.get("is_neutral", False)),
            "declared_angles_degrees": pose.get(
                "declared_angles_degrees",
                {},
            ),
            "applied_actions": applied,
            "stage": stage,
            "renders": renders,
            "regions": regions,
            "threshold_flags": flags,
            "diagnostic_pass": len(flags) == 0,
        }
        poses[pose["name"]] = result
        write_json(
            output / "metrics" / f"pose_{slug(pose['name'])}.json",
            {
                "schema_version": "1.0.0",
                "diagnostic_only": True,
                "pose": pose["name"],
                **result,
            },
        )
        write_status(
            output,
            "pose_complete",
            {
                "pose": pose["name"],
                "stage": stage,
                "diagnostic_pass": result["diagnostic_pass"],
            },
        )
    bpy.data.meshes.remove(baseline_mesh)

    failing = [
        name
        for name, result in poses.items()
        if not result["diagnostic_pass"]
    ]
    report = {
        "schema_version": "1.0.0",
        "harness": "G40 bounded deformation validation",
        "diagnostic_only": True,
        "blender_version": bpy.app.version_string,
        "candidate": {
            "id": config.get("candidate_id", source.stem),
            "label": config.get("candidate_label", source.stem),
        },
        "source": {
            "requested_path": source.as_posix(),
            "opened_path": opened.as_posix(),
            "body_object": args.body_object,
            "topology": original_topology,
            "bounds": original_bounds,
            "isolation": isolation,
        },
        "coordinate_audit": coordinate,
        "rig": {
            "name": armature.name,
            "bone_count": len(armature.data.bones),
            "deform_bones": sorted(
                bone.name
                for bone in armature.data.bones
                if bone.use_deform
            ),
            "non_deform_bones": sorted(
                bone.name
                for bone in armature.data.bones
                if not bone.use_deform
            ),
            "bounded_diagnostic_rig": True,
            "production_rig": False,
            "scope": config["rig"].get("scope", ""),
        },
        "checkpoints": {
            "exact_input": (
                output / "stages" / "00_input_exact_copy.blend"
            ).as_posix(),
            "body_isolated": body_stage,
            "neutral_rig_no_weights": rig_stage,
            "automatic_weights": automatic_stage,
            "bounded_weights": weight_stage,
        },
        "weights": weights_payload,
        "regions": config["regions"],
        "thresholds": config["thresholds"],
        "poses": poses,
        "render": {
            "views": config["render"]["views"],
            "comparison_view": config["render"]["comparison_view"],
            "resolution": config["render"]["resolution"],
        },
        "verdict": {
            "diagnostic_pass": len(failing) == 0,
            "failing_poses": failing,
            "coordinate_contract_pass": coordinate["contract_pass"],
            "topology_approval": False,
            "rig_approval": False,
            "animation_approval": False,
            "visual_approval": False,
            "user_approval_required": True,
            "statement": (
                "This run exercises a disposable bounded diagnostic rig. "
                "Passing metrics would not approve production topology, final "
                "weights, animation quality, art direction, or visual fidelity."
            ),
        },
    }
    report_path = output / "reports" / "validation_report.json"
    write_json(report_path, report)
    write_status(
        output,
        "blender_complete",
        {
            "report": report_path.as_posix(),
            "diagnostic_pass": len(failing) == 0,
            "failing_poses": failing,
        },
    )
    print(
        "G40_BLENDER_REPORT="
        + json.dumps(report["verdict"], sort_keys=True)
    )


if __name__ == "__main__":
    main()
