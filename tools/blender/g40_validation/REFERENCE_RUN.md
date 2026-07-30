# Verified Bentosaur R003 reference run

Preserved local Tier C run:

```text
.tmp/subagents/g40_validation_harness/runs/bentosaur_r003_reference_final_20260729
```

The compact reports and evidence snapshot is checked into the R003 QA directory
at `art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/qa/g40-validation-reference`.

Environment:

- Blender `5.1.2`
- source object `BENTOSAUR_BODY_RETOPO_WIP_R003`
- source and exact-copy SHA-256
  `181d93014f1667d9044d12e24fa297f4b391c9eb8d1164ddc5f45f3971f7caf9`

Preservation:

- ten `.blend` checkpoints;
- five independently reset poses;
- three rendered views per pose;
- 41 stable files in the final manifest;
- 1,080,432,795 manifested bytes;
- every recorded hash independently rechecked;
- wrapper, Blender driver, and artifact recipe hashes match the current files;
- frozen config matches `configs/bentosaur_r003.sample.json`.

Result:

- coordinate contract: pass;
- neutral: pass;
- reach/tray hold: fail;
- squat: fail;
- extreme walk: fail;
- tail bend: pass;
- overall diagnostic: fail;
- topology, rig, animation, visual, and user approval: false.

The complete per-region deformation distributions match the selected prior R003
confirmation report exactly: maximum numeric delta across every shared
minimum/P05/median/P95/maximum face-area and edge-length statistic was `0.0`.

This reference proves the harness reproduces the known diagnostic. It does not
approve R003 or elevate the generated armature to a production rig.
