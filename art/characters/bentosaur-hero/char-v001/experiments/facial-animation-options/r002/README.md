# Bentosaur Facial Animation Options — r002

Status: **structural contract passed; Godot visual gate failed; frozen for
diagnosis; not production approved**.

## Why this revision exists

`r001` proved that Blender could export the named facial morphs and the
root/jaw/tongue skeleton, but Godot displayed the tongue vertically near the
nose. `r002` changes one thing in the deterministic Blender recipe: the tongue
object's location, rotation, and scale are applied before armature skinning and
GLB export.

`r001` remains unchanged and recoverable. `r002` preserves its own source,
numbered Blender checkpoints, render evidence, export, round-trip QA scene,
Godot captures, and hashes.

## Checkpoint result

The repair improved the engine import but did not pass the visual gate:

- Godot imports all 9 meshes, 21,336 triangles, 8 facial morph bindings, and
  the root/jaw/tongue bones.
- The neutral, mouth morph, blink, happy-eye, and chew controls run.
- The tongue no longer appears at the nose.
- In morph-only and hybrid opening, most of the tongue is still below or
  behind the mouth and only a small lower edge is visible.
- In bone-only mode, the mouth remains essentially closed; with consistent
  tongue drivers, the tongue remains occluded behind the uncut muzzle.
- Morph-only and hybrid are visually almost identical in this proxy because
  the jaw bone mostly affects a beauty-hidden helper rather than authored lip
  and jaw volume.

This is useful evidence, not a character approval candidate.

## Stop rule

No blind `r003` transform tweak follows this result. Two engine attempts have
isolated the problem far enough to require a deliberate topology/rigging
decision.

The next facial-art attempt must start with a real authored mouth unit:

1. cut or retopologize an actual mouth aperture and recessed cavity;
2. author the tongue as a clean separate mesh in its neutral in-mouth pose;
3. apply transforms before binding;
4. bind and inspect the tongue plus jaw in Godot before adding expressions;
5. only then author the open-smile corrective, blinks, happy eyes, and chew.

## Evidence

- Blender state sheet:
  `evidence/facial_states_contact_sheet.png`
- Godot runtime states:
  `evidence/godot-runtime/facial_states_runtime_contact_sheet.png`
- Same-pose architecture comparison:
  `evidence/godot-runtime/mouth_mode_comparison.png`
- Automated engine report:
  `qa/godot-runtime/facial_rig_contract_report.json`
- Human visual-gate record:
  `qa/godot-runtime/runtime_visual_gate.json`

The runtime comparison is ordered:

```text
morph-only | bone-only | hybrid
```

## Reproduce

From the repository root:

```sh
EXPERIMENT=art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r002

/Applications/Blender.app/Contents/MacOS/Blender \
  --background \
  art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/bentosaur_hero_s40_production_topology_r003.blend \
  --python "$EXPERIMENT/recipes/build_facial_rig_proof.py" -- \
  --output "$EXPERIMENT" \
  --resolution 640

python3 "$EXPERIMENT/recipes/make_contact_sheet.py" \
  --root "$EXPERIMENT"

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --import \
  --quit

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/facial_rig_contract_test.gd
```

This revision used no paid API calls. Tripo credits spent: `0`; recorded
account balance remains `4,695`.
