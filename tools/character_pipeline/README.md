# Character Pipeline Automation Harness

This harness manages the versioned filesystem and manifest layer of the
Bentosaur character pipeline. It does not model, retopologize, rig, animate,
export, approve, or overwrite Blender work.

## Guarantees

- The next revision is calculated from the revision directories actually on
  disk.
- A revision directory is assembled in a temporary sibling and renamed into
  place; an existing revision is never reused or overwritten.
- A same-stage WIP cannot silently become lineage. It must be explicitly
  superseded while the new revision is activated.
- Before a WIP is superseded, every registered file is hashed and checked.
- Superseding a WIP makes all of its artifact records immutable.
- `register` and `hash-artifacts --write` refuse frozen or superseded
  manifests.
- Immutable artifact drift is an error; the tool never updates its recorded
  hash to hide the change.
- All repository paths are normalized, repository-relative, non-symlink file
  paths.
- JSON writes use a temporary file and an atomic rename.

The tool only changes:

- a new revision directory;
- the previous same-stage manifest when
  `--activate --supersede-active` is explicitly supplied;
- `pipeline.json` when `--activate` is explicitly supplied;
- a WIP manifest when `register` or `hash-artifacts --write` is explicitly
  supplied.

## Status

From the repository root:

```bash
node tools/character_pipeline/character_pipeline.mjs status \
  --root "$PWD" \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json
```

Add `--json` for machine-readable output.

## Preview the next revision

S40 is currently WIP, so previewing its successor must explicitly describe the
intended transition:

```bash
node tools/character_pipeline/character_pipeline.mjs create-revision \
  --root "$PWD" \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json \
  --stage S40 \
  --activate \
  --supersede-active \
  --dry-run
```

`--dry-run` does not write anything. The output includes the proposed
revision, paths, parent lineage, gate, coordinate contract, and full manifest
skeleton.

## Create and activate the next revision

Only remove `--dry-run` after reviewing the preview and confirming that all
current work is saved:

```bash
node tools/character_pipeline/character_pipeline.mjs create-revision \
  --root "$PWD" \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json \
  --stage S40 \
  --activate \
  --supersede-active
```

This operation:

1. verifies every artifact registered by the active S40 manifest;
2. changes the old WIP manifest to `superseded`, sets `frozen_at`, and marks
   all of its artifacts immutable;
3. creates the next `rNNN` directory with `source/`, `work/`, `recipes/`,
   `evidence/`, `qa/`, and `provenance/`;
4. creates a schema-shaped WIP `manifest.json` with the exact previous
   manifest as hashed lineage;
5. points `pipeline.json` to the new revision.

For the first revision of a pending stage, the nearest earlier active stage is
selected automatically:

```bash
node tools/character_pipeline/character_pipeline.mjs create-revision \
  --root "$PWD" \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json \
  --stage S50 \
  --activate \
  --dry-run
```

The parent must already be `frozen` or `superseded`. Additional parent
manifests can be declared with repeated `--parent REPO_RELATIVE_PATH`.

## Register a saved source or checkpoint

Every source file is first saved by its authoring tool, then registered in the
current WIP manifest. The default is mutable because a canonical WIP source
can still change:

```bash
node tools/character_pipeline/character_pipeline.mjs register \
  --root "$PWD" \
  --manifest art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/manifest.json \
  --group editable_sources \
  --id s40-topology-assembly-r003 \
  --role canonical_blender_master \
  --path art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/bentosaur_hero_s40_production_topology_r003.blend \
  --format blend \
  --derived-from s40-r002-manifest
```

Register operation checkpoints as immutable immediately:

```bash
node tools/character_pipeline/character_pipeline.mjs register \
  --root "$PWD" \
  --manifest art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/manifest.json \
  --group outputs \
  --id center-seam-repair-checkpoint \
  --role intermediate_blender_checkpoint \
  --path art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/work/10_center_seam_quad_repair.blend \
  --format blend \
  --derived-from s40-topology-assembly-r003 \
  --immutable
```

Supported groups are:

- `inputs`
- `editable_sources`
- `recipes`
- `vendor_jobs`
- `outputs`
- `qa.reports`

Artifact IDs must be unique within the entire manifest, not just within one
group.

## Check or refresh artifact hashes

Check every registered parent, input, source, recipe, vendor record, output,
and QA report without writing:

```bash
node tools/character_pipeline/character_pipeline.mjs hash-artifacts \
  --root "$PWD" \
  --manifest art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/manifest.json
```

If a mutable WIP source changed intentionally, refresh only its recorded byte
size and SHA-256:

```bash
node tools/character_pipeline/character_pipeline.mjs hash-artifacts \
  --root "$PWD" \
  --manifest art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/manifest.json \
  --write
```

The write command still refuses:

- a frozen or superseded manifest;
- a changed artifact already marked immutable;
- a missing file, directory, symlink, absolute path, traversal path, or path
  outside the repository.

Review source changes before accepting a new mutable hash. The command records
integrity; it does not decide whether the artistic change is correct.

## Full pipeline validation

After updating a stage manifest:

```bash
node tools/character_pipeline/validate_character_pipeline.mjs \
  --root "$PWD" \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json \
  --report art/characters/bentosaur-hero/char-v001/pipeline-validation.json
```

## Tests

The test fixture exists only under `.tmp/character-pipeline-tests/` and is
deleted after the run:

```bash
node --test tools/character_pipeline/tests/character_pipeline.test.mjs
```

The test covers revision creation, automatic parent lineage, correct schema
path generation, registration, mutable hash refresh, immutable drift refusal,
WIP supersession, frozen-manifest edit refusal, active-pointer updates, and
status output.
