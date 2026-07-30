#!/usr/bin/env node

import { createHash, randomUUID } from "node:crypto";
import { createReadStream } from "node:fs";
import {
  lstat,
  mkdir,
  readFile,
  readdir,
  rename,
  rm,
  writeFile,
} from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";

const DEFAULT_PIPELINE =
  "art/characters/bentosaur-hero/char-v001/pipeline.json";
const MANIFEST_SCHEMA =
  "art/characters/_pipeline/v1/schemas/stage-manifest.schema.json";
const REVISION_PATTERN = /^r([0-9]{3})$/;
const STAGE_PATTERN = /^S[0-9]{2}$/;
const ARTIFACT_ID_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const EDITABLE_GROUPS = new Set([
  "inputs",
  "editable_sources",
  "recipes",
  "vendor_jobs",
  "outputs",
  "qa.reports",
]);
const GATE_IDS = {
  S10: "G10_IDENTITY_LOCK",
  S20: "G20_HIGH_VISUAL_SOURCE",
  S30: "G30_SCAFFOLD_ACCEPTANCE",
  S40: "G40_DEFORMATION_TOPOLOGY",
  S50: "G50_BAKE_INTEGRITY",
  S60: "G60_FINAL_APPEARANCE",
  S70: "G70_RIG_DEFORMATION",
  S80: "G80_ANIMATION_PERFORMANCE",
  S90: "G90_MOBILE_RUNTIME",
};

function serializeJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function sha256Buffer(value) {
  return createHash("sha256").update(value).digest("hex");
}

export async function sha256File(filePath) {
  const digest = createHash("sha256");
  for await (const chunk of createReadStream(filePath)) {
    digest.update(chunk);
  }
  return digest.digest("hex");
}

function assertNonEmptyString(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${label} must be a non-empty string`);
  }
}

export function assertRepoRelative(value, label = "path") {
  assertNonEmptyString(value, label);
  if (path.isAbsolute(value)) {
    throw new Error(`${label} must be repository-relative: ${value}`);
  }
  if (value.includes("\\")) {
    throw new Error(`${label} must use forward slashes: ${value}`);
  }
  const segments = value.split("/");
  if (segments.includes("..") || segments.includes(".") || segments.includes("")) {
    throw new Error(`${label} is not a normalized repository path: ${value}`);
  }
  if (path.posix.normalize(value) !== value) {
    throw new Error(`${label} is not a normalized repository path: ${value}`);
  }
  return value;
}

export function resolveRepoPath(root, repoPath, label = "path") {
  assertRepoRelative(repoPath, label);
  const absoluteRoot = path.resolve(root);
  const absolute = path.resolve(absoluteRoot, repoPath);
  if (
    absolute !== absoluteRoot &&
    !absolute.startsWith(`${absoluteRoot}${path.sep}`)
  ) {
    throw new Error(`${label} escapes the repository root: ${repoPath}`);
  }
  return absolute;
}

async function readJson(filePath, label) {
  let source;
  try {
    source = await readFile(filePath, "utf8");
  } catch (error) {
    throw new Error(`Cannot read ${label} ${filePath}: ${error.message}`);
  }
  try {
    return JSON.parse(source);
  } catch (error) {
    throw new Error(`Cannot parse ${label} ${filePath}: ${error.message}`);
  }
}

async function pathExists(filePath) {
  try {
    await lstat(filePath);
    return true;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
}

async function atomicWriteJson(filePath, value) {
  const temporary = `${filePath}.tmp-${process.pid}-${randomUUID()}`;
  await writeFile(temporary, serializeJson(value), {
    encoding: "utf8",
    flag: "wx",
  });
  await rename(temporary, filePath);
}

function getArtifactCollections(manifest) {
  return [
    ["lineage.parent_manifests", manifest.lineage?.parent_manifests ?? []],
    ["inputs", manifest.inputs ?? []],
    ["editable_sources", manifest.editable_sources ?? []],
    ["recipes", manifest.recipes ?? []],
    ["vendor_jobs", manifest.vendor_jobs ?? []],
    ["outputs", manifest.outputs ?? []],
    ["qa.reports", manifest.qa?.reports ?? []],
  ];
}

function markAllArtifactsImmutable(manifest) {
  for (const [, artifacts] of getArtifactCollections(manifest)) {
    for (const artifact of artifacts) artifact.immutable = true;
  }
}

function getEditableCollection(manifest, group) {
  if (!EDITABLE_GROUPS.has(group)) {
    throw new Error(
      `Unsupported artifact group ${group}; expected one of ${[
        ...EDITABLE_GROUPS,
      ].join(", ")}`,
    );
  }
  if (group === "qa.reports") {
    manifest.qa ??= { reports: [], requirements: {}, results: {} };
    manifest.qa.reports ??= [];
    return manifest.qa.reports;
  }
  manifest[group] ??= [];
  return manifest[group];
}

function assertManifestEditable(manifest, manifestPath) {
  const state = manifest.stage?.state;
  if (state !== "wip") {
    throw new Error(
      `Refusing to edit ${manifestPath}: revision state is ${state ?? "missing"}, not wip`,
    );
  }
}

async function inspectArtifact(root, repoPath) {
  const absolute = resolveRepoPath(root, repoPath, "artifact path");
  const details = await lstat(absolute);
  if (details.isSymbolicLink()) {
    throw new Error(`Artifact paths may not be symbolic links: ${repoPath}`);
  }
  if (!details.isFile()) {
    throw new Error(`Artifact is not a file: ${repoPath}`);
  }
  return {
    bytes: details.size,
    sha256: await sha256File(absolute),
  };
}

function normalizeCoordinateContract(contract) {
  if (!contract) {
    throw new Error("Pipeline is missing a coordinate contract");
  }
  return {
    front_axis: contract.front_axis,
    up_axis: contract.up_axis,
    character_left_axis: contract.character_left_axis,
    unit_system: contract.unit_system,
    unit_scale: contract.unit_scale,
    origin: contract.origin,
  };
}

function selectCoordinateContract(pipeline, stageCode) {
  const effectiveCode =
    pipeline.production_coordinate_contract?.effective_from_stage ?? "S40";
  const selected =
    Number(stageCode.slice(1)) >= Number(effectiveCode.slice(1))
      ? pipeline.production_coordinate_contract
      : pipeline.source_coordinate_contract;
  return normalizeCoordinateContract(selected);
}

function artifactIdForManifest(manifest, fallbackIndex) {
  const code = manifest.stage?.code?.toLowerCase();
  const revision = manifest.stage?.revision;
  if (code && REVISION_PATTERN.test(revision ?? "")) {
    return `${code}-${revision}-manifest`;
  }
  return `parent-manifest-${String(fallbackIndex).padStart(2, "0")}`;
}

async function parentArtifactFromFile(
  root,
  repoPath,
  role,
  fallbackIndex,
  overrideSource = null,
) {
  const absolute = resolveRepoPath(root, repoPath, "parent manifest path");
  const parentManifest =
    overrideSource ?? (await readJson(absolute, "parent manifest"));
  const serialized = serializeJson(parentManifest);
  const details = overrideSource
    ? {
        bytes: Buffer.byteLength(serialized),
        sha256: sha256Buffer(serialized),
      }
    : await inspectArtifact(root, repoPath);
  return {
    artifact: {
      artifact_id: artifactIdForManifest(parentManifest, fallbackIndex),
      role,
      path: repoPath,
      format: "json",
      bytes: details.bytes,
      sha256: details.sha256,
      immutable: true,
      derived_from: [],
    },
    manifest: parentManifest,
  };
}

function nextRevisionFromNames(names) {
  const values = names
    .map((name) => REVISION_PATTERN.exec(name))
    .filter(Boolean)
    .map((match) => Number(match[1]));
  const next = (values.length === 0 ? 0 : Math.max(...values)) + 1;
  if (next > 999) throw new Error("Revision counter exhausted at r999");
  return `r${String(next).padStart(3, "0")}`;
}

async function listRevisionNames(stageRoot) {
  try {
    const entries = await readdir(stageRoot, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isDirectory() && REVISION_PATTERN.test(entry.name))
      .map((entry) => entry.name);
  } catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  }
}

function inferPreviousParent(pipeline, stageIndex) {
  for (let index = stageIndex - 1; index >= 0; index -= 1) {
    if (pipeline.stages[index]?.manifest) return pipeline.stages[index].manifest;
  }
  return null;
}

function relativeSchemaPath(revisionRepoPath) {
  return path.posix.relative(revisionRepoPath, MANIFEST_SCHEMA);
}

function buildManifestSkeleton({
  pipeline,
  stage,
  revision,
  revisionRepoPath,
  createdAt,
  parentArtifacts,
  supersedes,
  gateId,
}) {
  return {
    $schema: relativeSchemaPath(revisionRepoPath),
    schema_version: "1.0.0",
    character_id: pipeline.character_id,
    character_version: pipeline.character_version,
    stage: {
      code: stage.code,
      slug: stage.slug,
      revision,
      state: "wip",
      created_at: createdAt,
      frozen_at: null,
    },
    lineage: {
      parent_manifests: parentArtifacts,
      supersedes,
    },
    coordinate_contract: selectCoordinateContract(pipeline, stage.code),
    inputs: [],
    editable_sources: [],
    toolchain: [],
    recipes: [],
    vendor_jobs: [],
    outputs: [],
    qa: {
      reports: [],
      requirements: {},
      results: {},
    },
    approval: {
      gate_id:
        gateId ??
        GATE_IDS[stage.code] ??
        `G${stage.code.slice(1)}_${stage.slug
          .replaceAll("-", "_")
          .toUpperCase()}`,
      decision_path: null,
      technical_state: "pending",
      human_state: "pending",
    },
  };
}

export async function createRevision({
  root,
  pipelinePath = DEFAULT_PIPELINE,
  stageCode,
  parentPaths = [],
  gateId = null,
  activate = false,
  supersedeActive = false,
  dryRun = false,
  createdAt = new Date().toISOString(),
}) {
  if (!STAGE_PATTERN.test(stageCode ?? "")) {
    throw new Error(`--stage must match S00 format; received ${stageCode}`);
  }
  if (Number.isNaN(Date.parse(createdAt))) {
    throw new Error(`createdAt is not an ISO date-time: ${createdAt}`);
  }
  if (supersedeActive && !activate) {
    throw new Error("--supersede-active requires --activate");
  }

  const absoluteRoot = path.resolve(root);
  const normalizedPipelinePath = assertRepoRelative(
    pipelinePath,
    "pipeline path",
  );
  const absolutePipeline = resolveRepoPath(
    absoluteRoot,
    normalizedPipelinePath,
    "pipeline path",
  );
  const pipeline = await readJson(absolutePipeline, "pipeline");
  const stageIndex = (pipeline.stages ?? []).findIndex(
    (candidate) => candidate.code === stageCode,
  );
  if (stageIndex < 0) {
    throw new Error(`Pipeline does not define stage ${stageCode}`);
  }
  const stage = pipeline.stages[stageIndex];
  const characterRoot = path.posix.dirname(normalizedPipelinePath);
  const stageRepoPath = `${characterRoot}/stages/${stage.code.toLowerCase()}-${stage.slug}`;
  const stageRoot = resolveRepoPath(absoluteRoot, stageRepoPath, "stage path");
  const revision = nextRevisionFromNames(await listRevisionNames(stageRoot));
  const revisionRepoPath = `${stageRepoPath}/${revision}`;
  const revisionPath = resolveRepoPath(
    absoluteRoot,
    revisionRepoPath,
    "revision path",
  );
  if (await pathExists(revisionPath)) {
    throw new Error(`Refusing to overwrite existing revision ${revisionRepoPath}`);
  }

  const activeManifestPath = stage.manifest
    ? assertRepoRelative(stage.manifest, `${stageCode} active manifest`)
    : null;
  let transitionedParent = null;
  let originalParent = null;
  if (activeManifestPath) {
    const absoluteParent = resolveRepoPath(
      absoluteRoot,
      activeManifestPath,
      "active manifest path",
    );
    originalParent = await readJson(absoluteParent, "active manifest");
    if (originalParent.stage?.state === "wip") {
      if (!supersedeActive) {
        throw new Error(
          `${stageCode} ${originalParent.stage?.revision ?? "active revision"} is wip; use --activate --supersede-active to seal its lineage before creating ${revision}`,
        );
      }
      const integrity = await hashArtifacts({
        root: absoluteRoot,
        manifestPath: activeManifestPath,
        write: false,
      });
      if (!integrity.valid) {
        throw new Error(
          `${activeManifestPath} has changed mutable artifacts; run hash-artifacts --write and review the diff before superseding it`,
        );
      }
      transitionedParent = structuredClone(originalParent);
      transitionedParent.stage.state = "superseded";
      transitionedParent.stage.frozen_at ??= createdAt;
      markAllArtifactsImmutable(transitionedParent);
    } else if (
      !["frozen", "superseded"].includes(originalParent.stage?.state)
    ) {
      throw new Error(
        `Cannot use active manifest in state ${originalParent.stage?.state ?? "missing"} as lineage`,
      );
    }
  }

  const automaticParent =
    activeManifestPath ?? inferPreviousParent(pipeline, stageIndex);
  const uniqueParentPaths = [
    ...new Set(
      [automaticParent, ...parentPaths]
        .filter(Boolean)
        .map((value) => assertRepoRelative(value, "parent manifest path")),
    ),
  ];
  const parentArtifacts = [];
  const parentArtifactIds = new Set();
  for (const [index, parentPath] of uniqueParentPaths.entries()) {
    const isSameStageParent = parentPath === activeManifestPath;
    const parent = await parentArtifactFromFile(
      absoluteRoot,
      parentPath,
      isSameStageParent
        ? "previous_stage_revision_manifest"
        : "parent_stage_manifest",
      index + 1,
      isSameStageParent ? transitionedParent : null,
    );
    if (parentArtifactIds.has(parent.artifact.artifact_id)) {
      throw new Error(
        `Parent manifests resolve to duplicate artifact id ${parent.artifact.artifact_id}; use manifests with distinct stage revisions`,
      );
    }
    parentArtifactIds.add(parent.artifact.artifact_id);
    if (!["frozen", "superseded"].includes(parent.manifest.stage?.state)) {
      throw new Error(
        `Parent manifest ${parentPath} is ${parent.manifest.stage?.state ?? "missing"}; lineage parents must be frozen or superseded`,
      );
    }
    parentArtifacts.push(parent.artifact);
  }

  const supersedes = activeManifestPath;
  const manifest = buildManifestSkeleton({
    pipeline,
    stage,
    revision,
    revisionRepoPath,
    createdAt,
    parentArtifacts,
    supersedes,
    gateId:
      gateId ??
      (originalParent?.stage?.code === stageCode
        ? originalParent.approval?.gate_id
        : null),
  });
  const manifestRepoPath = `${revisionRepoPath}/manifest.json`;
  const nextPipeline = structuredClone(pipeline);
  const nextStage = nextPipeline.stages[stageIndex];
  if (activate) {
    nextStage.active_revision = revision;
    nextStage.manifest = manifestRepoPath;
    nextStage.state = "wip";
    nextPipeline.active_stage = stageCode;
  }

  const result = {
    dry_run: dryRun,
    stage: stageCode,
    revision,
    revision_path: revisionRepoPath,
    manifest_path: manifestRepoPath,
    activate,
    superseded_manifest: transitionedParent ? activeManifestPath : null,
    parent_manifests: parentArtifacts.map((artifact) => artifact.path),
  };
  if (dryRun) return { ...result, manifest };

  await mkdir(stageRoot, { recursive: true });
  const temporaryRevision = path.join(
    stageRoot,
    `.${revision}.create-${randomUUID()}`,
  );
  let revisionCreated = false;
  let parentTransitionWritten = false;
  try {
    await mkdir(temporaryRevision, { recursive: false });
    for (const directory of [
      "source",
      "work",
      "recipes",
      "evidence",
      "qa",
      "provenance",
    ]) {
      await mkdir(path.join(temporaryRevision, directory));
    }
    await writeFile(
      path.join(temporaryRevision, "manifest.json"),
      serializeJson(manifest),
      { encoding: "utf8", flag: "wx" },
    );
    await rename(temporaryRevision, revisionPath);
    revisionCreated = true;

    if (transitionedParent) {
      await atomicWriteJson(
        resolveRepoPath(absoluteRoot, activeManifestPath),
        transitionedParent,
      );
      parentTransitionWritten = true;
    }
    if (activate) {
      await atomicWriteJson(absolutePipeline, nextPipeline);
    }
  } catch (error) {
    if (parentTransitionWritten && originalParent && activeManifestPath) {
      await atomicWriteJson(
        resolveRepoPath(absoluteRoot, activeManifestPath),
        originalParent,
      ).catch(() => {});
    }
    if (revisionCreated) {
      await rm(revisionPath, { recursive: true, force: false }).catch(() => {});
    } else {
      await rm(temporaryRevision, { recursive: true, force: true }).catch(
        () => {},
      );
    }
    throw error;
  }
  return result;
}

export async function registerArtifact({
  root,
  manifestPath,
  group,
  artifactId,
  role,
  artifactPath,
  format = null,
  immutable = false,
  derivedFrom = [],
}) {
  assertRepoRelative(manifestPath, "manifest path");
  if (!ARTIFACT_ID_PATTERN.test(artifactId ?? "")) {
    throw new Error(`Invalid artifact id: ${artifactId}`);
  }
  assertNonEmptyString(role, "artifact role");
  assertRepoRelative(artifactPath, "artifact path");
  if (artifactPath === manifestPath) {
    throw new Error("A manifest cannot register itself as an artifact");
  }
  const absoluteRoot = path.resolve(root);
  const absoluteManifest = resolveRepoPath(absoluteRoot, manifestPath);
  const manifest = await readJson(absoluteManifest, "manifest");
  assertManifestEditable(manifest, manifestPath);
  const targetCollection = getEditableCollection(manifest, group);

  for (const [, artifacts] of getArtifactCollections(manifest)) {
    if (artifacts.some((artifact) => artifact.artifact_id === artifactId)) {
      throw new Error(`Artifact id is already registered: ${artifactId}`);
    }
    if (artifacts.some((artifact) => artifact.path === artifactPath)) {
      throw new Error(`Artifact path is already registered: ${artifactPath}`);
    }
  }
  const details = await inspectArtifact(absoluteRoot, artifactPath);
  const extension = path.posix.extname(artifactPath).slice(1).toLowerCase();
  const artifact = {
    artifact_id: artifactId,
    role,
    path: artifactPath,
    format: (format ?? extension) || "binary",
    bytes: details.bytes,
    sha256: details.sha256,
    immutable,
    derived_from: [...new Set(derivedFrom)],
  };
  targetCollection.push(artifact);
  await atomicWriteJson(absoluteManifest, manifest);
  return { group, artifact };
}

export async function hashArtifacts({
  root,
  manifestPath,
  write = false,
}) {
  assertRepoRelative(manifestPath, "manifest path");
  const absoluteRoot = path.resolve(root);
  const absoluteManifest = resolveRepoPath(absoluteRoot, manifestPath);
  const manifest = await readJson(absoluteManifest, "manifest");
  if (write) assertManifestEditable(manifest, manifestPath);

  const checked = [];
  const mutableChanges = [];
  const integrityErrors = [];
  for (const [group, artifacts] of getArtifactCollections(manifest)) {
    for (const artifact of artifacts) {
      let actual;
      try {
        actual = await inspectArtifact(absoluteRoot, artifact.path);
      } catch (error) {
        integrityErrors.push(
          `${group}.${artifact.artifact_id}: ${error.message}`,
        );
        continue;
      }
      const changed =
        artifact.bytes !== actual.bytes || artifact.sha256 !== actual.sha256;
      checked.push({
        group,
        artifact_id: artifact.artifact_id,
        path: artifact.path,
        changed,
      });
      if (!changed) continue;
      if (artifact.immutable) {
        integrityErrors.push(
          `${group}.${artifact.artifact_id}: immutable artifact content changed`,
        );
      } else {
        mutableChanges.push({
          group,
          artifact_id: artifact.artifact_id,
          previous: { bytes: artifact.bytes, sha256: artifact.sha256 },
          actual,
        });
        if (write) {
          artifact.bytes = actual.bytes;
          artifact.sha256 = actual.sha256;
        }
      }
    }
  }
  if (integrityErrors.length > 0) {
    throw new Error(
      `Artifact integrity check failed:\n- ${integrityErrors.join("\n- ")}`,
    );
  }
  if (write && mutableChanges.length > 0) {
    await atomicWriteJson(absoluteManifest, manifest);
  }
  return {
    manifest: manifestPath,
    mode: write ? "write" : "check",
    checked: checked.length,
    changed_mutable_artifacts: mutableChanges,
    valid: !write ? mutableChanges.length === 0 : true,
  };
}

async function discoveredRevisionSummary(root, characterRoot, stage) {
  const stageRepoPath = `${characterRoot}/stages/${stage.code.toLowerCase()}-${stage.slug}`;
  const stageRoot = resolveRepoPath(root, stageRepoPath);
  const names = await listRevisionNames(stageRoot);
  return names.sort().join(", ") || "—";
}

export async function pipelineStatus({
  root,
  pipelinePath = DEFAULT_PIPELINE,
}) {
  assertRepoRelative(pipelinePath, "pipeline path");
  const absoluteRoot = path.resolve(root);
  const absolutePipeline = resolveRepoPath(absoluteRoot, pipelinePath);
  const pipeline = await readJson(absolutePipeline, "pipeline");
  const characterRoot = path.posix.dirname(pipelinePath);
  const rows = [];
  for (const stage of pipeline.stages ?? []) {
    let manifestState = "—";
    let technical = "—";
    let human = "—";
    let artifactCount = 0;
    let pointer = stage.manifest ? "ok" : "—";
    if (stage.manifest) {
      try {
        const manifest = await readJson(
          resolveRepoPath(absoluteRoot, stage.manifest),
          `${stage.code} manifest`,
        );
        manifestState = manifest.stage?.state ?? "missing";
        technical = manifest.approval?.technical_state ?? "—";
        human = manifest.approval?.human_state ?? "—";
        artifactCount = getArtifactCollections(manifest).reduce(
          (sum, [, artifacts]) => sum + artifacts.length,
          0,
        );
        if (
          manifest.stage?.code !== stage.code ||
          manifest.stage?.revision !== stage.active_revision
        ) {
          pointer = "mismatch";
        }
      } catch {
        pointer = "missing";
        manifestState = "missing";
      }
    }
    rows.push({
      stage: stage.code,
      slug: stage.slug,
      active_revision: stage.active_revision ?? "—",
      pipeline_state: stage.state,
      manifest_state: manifestState,
      technical,
      human,
      artifacts: artifactCount,
      pointer,
      revisions: await discoveredRevisionSummary(
        absoluteRoot,
        characterRoot,
        stage,
      ),
    });
  }
  return {
    pipeline_id: pipeline.pipeline_id,
    active_stage: pipeline.active_stage,
    rows,
  };
}

export function formatStatusTable(status) {
  const headers = [
    "Stage",
    "Revision",
    "Pipeline",
    "Manifest",
    "Technical",
    "Human",
    "Files",
    "Pointer",
    "On disk",
  ];
  const rows = status.rows.map((row) => [
    row.stage,
    row.active_revision,
    row.pipeline_state,
    row.manifest_state,
    row.technical,
    row.human,
    String(row.artifacts),
    row.pointer,
    row.revisions,
  ]);
  return [
    `Pipeline: ${status.pipeline_id} · active stage: ${status.active_stage}`,
    "",
    `| ${headers.join(" | ")} |`,
    `| ${headers.map(() => "---").join(" | ")} |`,
    ...rows.map((row) => `| ${row.join(" | ")} |`),
  ].join("\n");
}

function parseCli(argv) {
  const command = argv[0];
  const options = {
    root: process.cwd(),
    pipelinePath: DEFAULT_PIPELINE,
    parentPaths: [],
    derivedFrom: [],
  };
  const booleanFlags = new Set([
    "--activate",
    "--supersede-active",
    "--dry-run",
    "--immutable",
    "--write",
    "--json",
  ]);
  const repeatedFlags = new Map([
    ["--parent", "parentPaths"],
    ["--derived-from", "derivedFrom"],
  ]);
  const valueFlags = new Map([
    ["--root", "root"],
    ["--pipeline", "pipelinePath"],
    ["--stage", "stageCode"],
    ["--gate-id", "gateId"],
    ["--created-at", "createdAt"],
    ["--manifest", "manifestPath"],
    ["--group", "group"],
    ["--id", "artifactId"],
    ["--role", "role"],
    ["--path", "artifactPath"],
    ["--format", "format"],
  ]);
  for (let index = 1; index < argv.length; index += 1) {
    const flag = argv[index];
    if (booleanFlags.has(flag)) {
      const key = flag
        .slice(2)
        .replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      options[key] = true;
      continue;
    }
    const value = argv[index + 1];
    if (value === undefined || value.startsWith("--")) {
      throw new Error(`Missing value for ${flag}`);
    }
    if (repeatedFlags.has(flag)) {
      options[repeatedFlags.get(flag)].push(value);
    } else if (valueFlags.has(flag)) {
      options[valueFlags.get(flag)] = value;
    } else {
      throw new Error(`Unknown option: ${flag}`);
    }
    index += 1;
  }
  return { command, options };
}

function helpText() {
  return `Bentosaur character pipeline harness

Commands:
  create-revision  Create the next versioned stage directory and manifest
  register         Register and hash one artifact in a WIP manifest
  hash-artifacts   Check hashes, or refresh mutable records with --write
  status           Print the concise pipeline status table

Common:
  --root PATH
  --pipeline REPO_RELATIVE_PATH

create-revision:
  --stage S40 [--parent PATH ...] [--gate-id ID]
  [--activate] [--supersede-active] [--dry-run]

register:
  --manifest PATH --group GROUP --id ID --role ROLE --path PATH
  [--format FORMAT] [--derived-from ID ...] [--immutable]

hash-artifacts:
  --manifest PATH [--write]

status:
  [--json]
`;
}

export async function runCli(argv = process.argv.slice(2)) {
  const { command, options } = parseCli(argv);
  if (!command || ["help", "--help", "-h"].includes(command)) {
    process.stdout.write(helpText());
    return;
  }
  let result;
  if (command === "create-revision") {
    result = await createRevision(options);
  } else if (command === "register") {
    result = await registerArtifact(options);
  } else if (command === "hash-artifacts") {
    result = await hashArtifacts(options);
    if (!result.valid) process.exitCode = 1;
  } else if (command === "status") {
    result = await pipelineStatus(options);
    if (!options.json) {
      process.stdout.write(`${formatStatusTable(result)}\n`);
      return;
    }
  } else {
    throw new Error(`Unknown command: ${command}\n\n${helpText()}`);
  }
  process.stdout.write(`${serializeJson(result)}`);
}

const invokedPath = process.argv[1]
  ? pathToFileURL(path.resolve(process.argv[1])).href
  : null;
if (invokedPath === import.meta.url) {
  runCli().catch((error) => {
    process.stderr.write(`Error: ${error.message}\n`);
    process.exitCode = 1;
  });
}
