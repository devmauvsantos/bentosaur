# G40 bounded deformation-validation harness

This directory contains a reusable, isolated Blender CLI harness for screening
a surfaced character mesh through a small set of deformation stress poses.

It is deliberately narrower than production rigging:

- it creates a disposable diagnostic skeleton;
- it starts from Blender automatic weights;
- it permits exactly one configured cleanup pass;
- it caps every vertex at a configured maximum of four influences;
- it measures face-area and edge-length change by configured body region;
- it saves the exact input, the rig/weight stages, and every pose as `.blend`;
- it renders contact and neutral-versus-pose comparison boards;
- it emits JSON reports and a SHA-256 manifest.

A pass is **not** production approval. The harness has no animator-facing
controls, final constraints, corrective shapes, facial system, authored
production weights, animation polish, runtime test, or art-direction judgment.
Visual review and explicit user approval remain mandatory.

## Proven environment

- macOS
- Blender `5.1.2`
- Python `3.14.6`
- Pillow `12.3.0`

The launcher accepts another Blender executable with `--blender`. Blender's
version is recorded in every report because bone-heat results can differ across
versions.

## Exact Bentosaur reference command

Run from the repository root:

```bash
cd /Users/mauvsantos/Workspace/games/Bentosaur

python3 tools/blender/g40_validation/g40_validate.py \
  --input art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/bentosaur_hero_s40_production_topology_r003.blend \
  --body-object BENTOSAUR_BODY_RETOPO_WIP_R003 \
  --config tools/blender/g40_validation/configs/bentosaur_r003.sample.json \
  --output .tmp/g40-validation-runs/my_fresh_r003_run
```

The output directory must be new or empty. The launcher refuses to overwrite a
prior run so that evidence and checkpoints cannot be silently replaced.

The launcher defaults to:

```text
/Applications/Blender.app/Contents/MacOS/Blender
```

Override it explicitly when needed:

```bash
python3 tools/blender/g40_validation/g40_validate.py \
  ... \
  --blender /path/to/Blender
```

## Pipeline and preserved sources

The launcher and Blender driver execute these stages:

| Stage | Preserved file | Meaning |
|---|---|---|
| `00` | `stages/00_input_exact_copy.blend` | Byte-for-byte copy of the input before Blender processing |
| `05` | `stages/05_body_isolated.blend` | Configured body isolated; world transform preserved |
| `10` | `stages/10_diagnostic_rig_neutral_no_weights.blend` | Disposable neutral diagnostic armature |
| `20` | `stages/20_automatic_weights.blend` | Blender bone-heat result before cleanup |
| `30` | `stages/30_bounded_diagnostic_weights.blend` | One configured cleanup pass, normalized and influence-capped |
| `40+` | `stages/{number}_pose_{name}.blend` | One source checkpoint per configured pose |

The input and stage `00` hashes must match. The launcher stops if they do not.
No file is written into the source asset directory.

The frozen inputs used for a run live in:

```text
run_inputs/config.json
run_inputs/invocation.json
```

`invocation.json` records the source/config/recipe hashes and exact Blender
command context.

## Output contract

Every completed run contains:

```text
stages/                 numbered .blend checkpoints
renders/<pose>/         one PNG per configured view
metrics/                coordinate, weight, and per-pose JSON
reports/
  validation_report.json
  evidence_index.json
  run_status.json
  hash_manifest.json
evidence/
  pose_contact_sheet.png
  neutral_vs_poses.png
logs/
run_inputs/
```

`validation_report.json` is the canonical machine-readable result.

The final hash manifest covers the frozen inputs, checkpoints, renders,
metrics, reports, evidence, recipes captured by invocation, and stable logs.
`logs/manifest.log` and the manifest itself are intentionally excluded because
they are being written while hashing.

Verify a completed run at any time:

```bash
python3 tools/blender/g40_validation/tools/g40_artifacts.py \
  verify \
  --run .tmp/g40-validation-runs/my_fresh_r003_run
```

Verification checks every manifest hash, the exact source copy, all checkpoint
and render paths, zero unweighted vertices, the influence cap, and both boards.

## Configuration model

The sample is:

```text
configs/bentosaur_r003.sample.json
```

The machine-readable schema is:

```text
schema/g40_config.schema.json
```

All character-specific assumptions are data:

- candidate ID and label;
- coordinate contract and expected bounds;
- symmetry plane/tolerances and morphology probes;
- complete diagnostic bone heads/tails/parents;
- left/right/tail naming conventions;
- bounded weight cleanup selectors;
- ordered measurement-region selectors;
- pose names, checkpoint numbers, intent, angles, and operations;
- collapse/stretch thresholds;
- camera views, render scale, colors, and lights.

The body object name remains a command argument so the same configuration can
be pointed at a repaired candidate with a different object name.

### Coordinate selectors

Selectors can use world space or normalized bounding-box space.

An axis constraint:

```json
{
  "axis": "+Z",
  "min": 0.54
}
```

An axis-aligned box:

```json
{
  "space": "normalized_bbox",
  "bounds": {
    "x": [0.7, 1.0],
    "y": [null, 0.6],
    "z": [0.0, 0.35]
  }
}
```

Boolean composition:

```json
{
  "all": [
    {
      "axis": "+Y",
      "min": 0.1
    },
    {
      "not": {
        "axis": "+Z",
        "min": 0.5
      }
    }
  ]
}
```

`all`, `any`, and `not` can be nested. Ordered regions use the first matching
selector; everything else receives the configured fallback region.

Normalized coordinates run from `0` to `1` independently on X/Y/Z, which makes
region definitions more portable between similarly proportioned characters.
World-space selectors are more exact for repaired variants of one locked model.

### Pose operations and angles

The driver supports four operations:

- `translate_bones`: move listed bones by one world-space delta while keeping
  each rest direction;
- `translate_chain`: move a connected chain root, then reconstruct the chain
  with its rest directions;
- `aim_chain`: reconstruct a connected chain from explicit world-space
  directions and an optional root offset;
- `rotate_local`: apply XYZ Euler degrees to one pose bone.

`aim_chain` is the most reproducible operation for topology stress poses. Each
action can declare the intended angles in `declared_angles_degrees`; the driver
also calculates and records the actual angle between every rest and target
direction. This lets a reviewer audit intent without hiding the exact vectors
used by Blender.

Every run resets the armature before applying the next pose. Poses are
independent, not cumulative.

### Weight cleanup boundary

The configured pass can:

- rigidly assign selected masses to one bone;
- remove opposite-side suffix leakage across one bilateral axis;
- remove named, prefixed, or suffixed influences in selected zones;
- assign any remaining unweighted vertex to its nearest deform bone;
- normalize and keep the strongest one-to-four influences.

The driver reports the exact number of affected vertices per rule. It performs
zero iterative polishing. If the diagnostic only passes after repeated manual
weight tuning, that work belongs in a production rigging stage—not in this
harness.

### Thresholds

For every baseline face and edge, the harness measures:

```text
posed size / neutral size
```

The Bentosaur reference uses:

- face collapse below `0.10x`;
- face severe stretch above `3.0x`;
- edge collapse below `0.35x`;
- edge severe stretch above `2.5x`;
- zero allowed occurrences per region.

The report also preserves minimum, P05, median, P95, maximum, and counts. A
threshold is a screening policy, not a substitute for looking at the rendered
silhouette and deformation flow.

## Comparing a repaired candidate

Use the completed R003 reference as `--compare-to` while giving the repaired
mesh a fresh output directory:

```bash
python3 tools/blender/g40_validation/g40_validate.py \
  --input /absolute/path/to/repaired_candidate.blend \
  --body-object REPAIRED_BODY_OBJECT \
  --config /absolute/path/to/repaired_candidate_config.json \
  --output /Users/mauvsantos/Workspace/games/Bentosaur/.tmp/g40-validation-runs/repaired_candidate_run \
  --compare-to /Users/mauvsantos/Workspace/games/Bentosaur/.tmp/subagents/g40_validation_harness/runs/bentosaur_r003_reference_final_20260729
```

This adds:

```text
evidence/cross_run_comparison.png
evidence/cross_run_comparison.json
```

The JSON preserves compact per-region P05/P95 metrics for every shared pose.
Cross-run comparisons are meaningful only when the region and pose contracts
are equivalent.

The comparison tool can also be called directly:

```bash
python3 tools/blender/g40_validation/tools/g40_artifacts.py \
  compare \
  --baseline /absolute/path/to/baseline_run \
  --candidate /absolute/path/to/candidate_run \
  --output /absolute/path/to/candidate_run/evidence/cross_run_comparison.png
```

Run `manifest` again afterward if evidence is added to an already completed
run.

## Adapting it to another character

Do not merely swap the mesh. Make a new config and check, in order:

1. Confirm front, character-left, up, floor, scale, symmetry plane, and expected
   bounds.
2. Place a diagnostic skeleton in the new character's neutral anatomy.
3. Define ordered regions that isolate actual shoulder, hip, knee, tail, head,
   and torso transition zones.
4. Keep cleanup rules minimal and explain every rigid override or prohibited
   influence zone.
5. Define poses at the character's intended gameplay motion envelope, including
   their declared angles.
6. Set render views that expose the silhouette and joint transitions.
7. Use a fresh run directory.
8. Inspect JSON **and** both evidence boards.
9. Ask for visual/user approval outside this harness.

For a repaired S40 Bentosaur candidate, the existing bones/poses can be reused
only if the coordinate contract, scale, and anatomical landmarks remain
unchanged. Update candidate metadata, expected bounds, selectors, and bone
placement whenever the repair changes them.

## Failure and recovery

The launcher never resumes into a non-empty run. If Blender stops after stage
`20` or `30`, those files remain valid forensic checkpoints and
`reports/run_status.json` records the last completed phase. Diagnose the issue,
then rerun into a new output directory.

This behavior is intentional: a single run should describe one immutable input,
one frozen configuration, one Blender version, and one uninterrupted recipe.

## Reference result

The verified Bentosaur R003 run should reproduce the prior bounded confirmation:

- coordinate contract: pass;
- neutral: pass;
- reach/tray hold: fail;
- squat: fail;
- extreme walk: fail;
- tail bend: pass;
- final topology, rig, animation, visual, and user approval: all false.

The point of the reference is reproducibility. It does not turn the known R003
failure into an approved asset.
