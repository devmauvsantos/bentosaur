import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  mkdir,
  mkdtemp,
  readFile,
  rm,
  writeFile,
} from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  createRevision,
  formatStatusTable,
  hashArtifacts,
  pipelineStatus,
  registerArtifact,
} from "../character_pipeline.mjs";

const TEST_DIRECTORY = path.dirname(fileURLToPath(import.meta.url));
const REPOSITORY_ROOT = path.resolve(TEST_DIRECTORY, "../../..");
const TEMPORARY_TEST_ROOT = path.join(
  REPOSITORY_ROOT,
  ".tmp",
  "character-pipeline-tests",
);
const PIPELINE_PATH =
  "art/characters/test-hero/char-v001/pipeline.json";
const S10_MANIFEST_PATH =
  "art/characters/test-hero/char-v001/stages/s10-reference-lock/r001/manifest.json";

function serialized(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

async function writeJson(filePath, value) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, serialized(value), "utf8");
}

async function readJson(root, repoPath) {
  return JSON.parse(await readFile(path.join(root, repoPath), "utf8"));
}

async function createFixture() {
  await mkdir(TEMPORARY_TEST_ROOT, { recursive: true });
  const root = await mkdtemp(path.join(TEMPORARY_TEST_ROOT, "run-"));
  const s10Manifest = {
    schema_version: "1.0.0",
    character_id: "test-hero",
    character_version: "char-v001",
    stage: {
      code: "S10",
      slug: "reference-lock",
      revision: "r001",
      state: "frozen",
      created_at: "2026-07-29T12:00:00.000Z",
      frozen_at: "2026-07-29T12:05:00.000Z",
    },
    lineage: { parent_manifests: [], supersedes: null },
    coordinate_contract: {
      front_axis: "+X",
      up_axis: "+Z",
      character_left_axis: "+Y",
      unit_system: "METRIC",
      unit_scale: 1,
      origin: "source",
    },
    inputs: [],
    editable_sources: [],
    toolchain: [],
    recipes: [],
    vendor_jobs: [],
    outputs: [],
    qa: { reports: [], requirements: {}, results: {} },
    approval: {
      gate_id: "G10_IDENTITY_LOCK",
      decision_path: null,
      technical_state: "pass",
      human_state: "approved",
    },
  };
  const pipeline = {
    schema_version: "1.0.0",
    pipeline_id: "test-hero-char-v001",
    character_id: "test-hero",
    character_version: "char-v001",
    status: "test",
    active_stage: "S10",
    source_coordinate_contract: {
      front_axis: "+X",
      up_axis: "+Z",
      character_left_axis: "+Y",
      unit_system: "METRIC",
      unit_scale: 1,
      origin: "source",
    },
    production_coordinate_contract: {
      effective_from_stage: "S40",
      front_axis: "-Y",
      up_axis: "+Z",
      character_left_axis: "+X",
      unit_system: "METRIC",
      unit_scale: 1,
      origin: "feet",
    },
    stages: [
      {
        code: "S10",
        slug: "reference-lock",
        active_revision: "r001",
        manifest: S10_MANIFEST_PATH,
        state: "frozen",
      },
      {
        code: "S20",
        slug: "high-visual-source",
        active_revision: null,
        manifest: null,
        state: "pending",
      },
    ],
  };
  await writeJson(path.join(root, S10_MANIFEST_PATH), s10Manifest);
  await writeJson(path.join(root, PIPELINE_PATH), pipeline);
  return root;
}

test("creates, hashes, protects, supersedes, and reports revisions", async () => {
  const root = await createFixture();
  try {
    const first = await createRevision({
      root,
      pipelinePath: PIPELINE_PATH,
      stageCode: "S20",
      activate: true,
      createdAt: "2026-07-29T13:00:00.000Z",
    });
    assert.equal(first.revision, "r001");
    const r001ManifestPath = first.manifest_path;
    const r001Manifest = await readJson(root, r001ManifestPath);
    assert.equal(
      r001Manifest.$schema,
      "../../../../../_pipeline/v1/schemas/stage-manifest.schema.json",
    );
    assert.equal(
      r001Manifest.lineage.parent_manifests[0].path,
      S10_MANIFEST_PATH,
    );

    const sourcePath =
      "art/characters/test-hero/char-v001/stages/s20-high-visual-source/r001/source/test_hero_s20_r001.blend";
    await writeFile(path.join(root, sourcePath), "blend-v1", "utf8");
    await registerArtifact({
      root,
      manifestPath: r001ManifestPath,
      group: "editable_sources",
      artifactId: "s20-source-r001",
      role: "canonical_blender_master",
      artifactPath: sourcePath,
      format: "blend",
      immutable: false,
    });
    assert.equal(
      (await hashArtifacts({ root, manifestPath: r001ManifestPath })).valid,
      true,
    );

    await writeFile(path.join(root, sourcePath), "blend-v2", "utf8");
    const changed = await hashArtifacts({
      root,
      manifestPath: r001ManifestPath,
    });
    assert.equal(changed.valid, false);
    assert.equal(changed.changed_mutable_artifacts.length, 1);
    await hashArtifacts({
      root,
      manifestPath: r001ManifestPath,
      write: true,
    });
    assert.equal(
      (await hashArtifacts({ root, manifestPath: r001ManifestPath })).valid,
      true,
    );

    const recipePath =
      "art/characters/test-hero/char-v001/stages/s20-high-visual-source/r001/recipes/build.py";
    await writeFile(path.join(root, recipePath), "print('locked')\n", "utf8");
    await registerArtifact({
      root,
      manifestPath: r001ManifestPath,
      group: "recipes",
      artifactId: "locked-recipe",
      role: "deterministic_recipe",
      artifactPath: recipePath,
      format: "py",
      immutable: true,
    });
    await writeFile(path.join(root, recipePath), "print('changed')\n", "utf8");
    await assert.rejects(
      hashArtifacts({
        root,
        manifestPath: r001ManifestPath,
        write: true,
      }),
      /immutable artifact content changed/,
    );
    await writeFile(path.join(root, recipePath), "print('locked')\n", "utf8");

    await assert.rejects(
      createRevision({
        root,
        pipelinePath: PIPELINE_PATH,
        stageCode: "S20",
      }),
      /is wip/,
    );
    const second = await createRevision({
      root,
      pipelinePath: PIPELINE_PATH,
      stageCode: "S20",
      activate: true,
      supersedeActive: true,
      createdAt: "2026-07-29T14:00:00.000Z",
    });
    assert.equal(second.revision, "r002");

    const superseded = await readJson(root, r001ManifestPath);
    assert.equal(superseded.stage.state, "superseded");
    assert.equal(superseded.stage.frozen_at, "2026-07-29T14:00:00.000Z");
    assert.equal(superseded.editable_sources[0].immutable, true);
    const child = await readJson(root, second.manifest_path);
    const parentRecord = child.lineage.parent_manifests[0];
    assert.equal(parentRecord.path, r001ManifestPath);
    const actualParentBytes = Buffer.from(serialized(superseded));
    assert.equal(parentRecord.bytes, actualParentBytes.length);
    assert.equal(
      parentRecord.sha256,
      createHash("sha256").update(actualParentBytes).digest("hex"),
    );

    const activePipeline = await readJson(root, PIPELINE_PATH);
    assert.equal(activePipeline.stages[1].active_revision, "r002");
    assert.equal(activePipeline.stages[1].manifest, second.manifest_path);
    await assert.rejects(
      registerArtifact({
        root,
        manifestPath: r001ManifestPath,
        group: "outputs",
        artifactId: "forbidden-edit",
        role: "forbidden",
        artifactPath: sourcePath,
      }),
      /Refusing to edit/,
    );

    const status = await pipelineStatus({
      root,
      pipelinePath: PIPELINE_PATH,
    });
    assert.equal(status.active_stage, "S20");
    assert.equal(status.rows[1].active_revision, "r002");
    assert.equal(status.rows[1].revisions, "r001, r002");
    assert.match(formatStatusTable(status), /\| S20 \| r002 \|/);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
