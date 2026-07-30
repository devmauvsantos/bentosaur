# Faceit Automation Boundary

Status: local installation verified; production pilot blocked by F0 topology

## Verified installation

- Blender: `5.1.2`
- Faceit: `2.3.71`
- Blender extension module: `bl_ext.user_default.faceit`
- Faceit manifest minimum Blender version: `4.2.0`
- License metadata: `GPL-3.0-or-later`

Machine-readable verification:

`tools/blender/faceit/faceit-installation-contract.json`

The installed extension exposes Blender operators for object registration,
group assignment, landmarks, rig generation, binding, shape-key baking, and
Audio2Face import. The live extension registered 174 `bpy.ops.faceit.*`
operators. Important operators found in this version include:

```text
faceit.add_facial_part
faceit.assign_main
faceit.facial_landmarks
faceit.generate_rig
faceit.smart_bind
faceit.generate_shapekeys
faceit.import_a2f_mocap
```

These operator names are an inspectable implementation surface, not a
documented stable external API. Every automation script must pin the Faceit
version and begin with a smoke test.

Landmark creation and placement are modal 3D-view workflows. They depend on
visible area/region and mouse state and are not a safe headless operation. AI
can prepare geometry, propose positions, drive visible tools, and validate the
result, but the landmark checkpoint remains an interactive visual gate.

## Smoke test

From the repository root:

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  --background \
  --python tools/blender/faceit/faceit_smoke_test.py
```

The test:

1. refuses to run in an interactive Blender process;
2. enables Faceit only for the disposable background process;
3. does not save Blender preferences;
4. creates a temporary sphere;
5. registers it through `faceit.add_facial_part`;
6. verifies the required operator contract;
7. prints a JSON report;
8. exits without saving a `.blend`.

It never opens or edits Bentosaur production sources.

The current interactive Blender session has Faceit enabled. The disposable
background test still enables it explicitly because it does not rely on
unsaved Blender preferences.

## Production rule

Do not run Faceit registration, landmark, bind, expression, or bake operators
against r005. That experiment is rejected and frozen.

The first production Faceit operation is allowed only after F0 provides:

- one approved canonical neutral face;
- a closed-mouth Basis with complete cavity and tongue;
- approved delighted-open deformation on identical topology;
- no seams, folds, intersections, or identity drift.

At that point, copy the approved source into a new immutable pilot checkpoint
and run the setup with visible approval gates.
