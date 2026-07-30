"""Read-only Faceit installation and operator smoke test.

Run this only in a disposable background Blender process. It enables Faceit
for the lifetime of that process, registers a generated test mesh, prints a
JSON report, and exits without saving a .blend or user preferences.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy


FACEIT_MODULE = "bl_ext.user_default.faceit"
REQUIRED_OPERATORS = (
    "add_facial_part",
    "assign_main",
    "facial_landmarks",
    "generate_rig",
    "smart_bind",
    "generate_shapekeys",
    "import_a2f_mocap",
)


def operator_exists(namespace: str, name: str) -> bool:
    try:
        getattr(getattr(bpy.ops, namespace), name).get_rna_type()
        return True
    except (AttributeError, RuntimeError):
        return False


def main() -> int:
    if not bpy.app.background:
        print(
            json.dumps(
                {
                    "status": "refused",
                    "reason": "Run only with Blender --background.",
                }
            )
        )
        return 2

    initially_enabled = FACEIT_MODULE in bpy.context.preferences.addons
    enable_result = None

    if not initially_enabled:
        enable_result = sorted(
            bpy.ops.preferences.addon_enable(module=FACEIT_MODULE)
        )

    try:
        faceit = __import__(FACEIT_MODULE, fromlist=["bl_info"])
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "phase": "import",
                    "module": FACEIT_MODULE,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                indent=2,
            )
        )
        return 1

    operator_contract = {
        name: operator_exists("faceit", name) for name in REQUIRED_OPERATORS
    }

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        location=(0.0, 0.0, 0.0),
    )
    smoke_head = bpy.context.object
    smoke_head.name = "FACEIT_SMOKE_HEAD"

    registration_result = sorted(
        bpy.ops.faceit.add_facial_part("EXEC_DEFAULT")
    )
    registered_objects = [
        item.name for item in bpy.context.scene.faceit_face_objects
    ]

    manifest = Path(faceit.__file__).with_name("blender_manifest.toml")
    report = {
        "status": (
            "passed"
            if registration_result == ["FINISHED"]
            and registered_objects == ["FACEIT_SMOKE_HEAD"]
            and all(operator_contract.values())
            else "failed"
        ),
        "blender_version": bpy.app.version_string,
        "faceit_module": FACEIT_MODULE,
        "faceit_version": ".".join(
            str(value) for value in faceit.bl_info["version"]
        ),
        "faceit_manifest_found": manifest.is_file(),
        "initially_enabled_in_background_process": initially_enabled,
        "ephemeral_enable_result": enable_result,
        "operator_contract": operator_contract,
        "registration_result": registration_result,
        "registered_objects": registered_objects,
        "blend_saved": False,
        "user_preferences_saved": False,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
