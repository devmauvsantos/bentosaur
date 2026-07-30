#!/usr/bin/env node

import { createHash } from "node:crypto";
import { readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const args = { root: process.cwd(), pipeline: null, report: null };
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    const value = argv[index + 1];
    if (flag === "--root") args.root = value;
    if (flag === "--pipeline") args.pipeline = value;
    if (flag === "--report") args.report = value;
    if (flag.startsWith("--")) index += 1;
  }
  if (!args.pipeline) {
    throw new Error("--pipeline is required");
  }
  return args;
}

function isSafeRepoRelative(value) {
  return (
    typeof value === "string" &&
    !path.isAbsolute(value) &&
    !value.split(/[\\/]/).includes("..")
  );
}

async function sha256(filePath) {
  const digest = createHash("sha256");
  digest.update(await readFile(filePath));
  return digest.digest("hex");
}

async function verifyArtifact(root, artifact, context, errors) {
  if (!isSafeRepoRelative(artifact.path)) {
    errors.push(`${context}: unsafe repository path ${artifact.path}`);
    return;
  }
  const absolute = path.resolve(root, artifact.path);
  let details;
  try {
    details = await stat(absolute);
  } catch {
    errors.push(`${context}: missing artifact ${artifact.path}`);
    return;
  }
  if (!details.isFile()) {
    errors.push(`${context}: artifact is not a file ${artifact.path}`);
    return;
  }
  if (details.size !== artifact.bytes) {
    errors.push(
      `${context}: byte mismatch for ${artifact.path}; expected ${artifact.bytes}, received ${details.size}`,
    );
  }
  const actualHash = await sha256(absolute);
  if (actualHash !== artifact.sha256) {
    errors.push(
      `${context}: SHA-256 mismatch for ${artifact.path}; expected ${artifact.sha256}, received ${actualHash}`,
    );
  }
}

async function validateManifest(root, manifestPath, stage, errors) {
  if (!isSafeRepoRelative(manifestPath)) {
    errors.push(`${stage.code}: unsafe manifest path ${manifestPath}`);
    return null;
  }
  const absolute = path.resolve(root, manifestPath);
  let manifest;
  try {
    manifest = JSON.parse(await readFile(absolute, "utf8"));
  } catch (error) {
    errors.push(`${stage.code}: cannot read manifest ${manifestPath}: ${error.message}`);
    return null;
  }

  if (manifest.stage?.code !== stage.code) {
    errors.push(
      `${stage.code}: manifest stage code is ${manifest.stage?.code ?? "missing"}`,
    );
  }

  const artifactGroups = [
    ["lineage.parent_manifests", manifest.lineage?.parent_manifests ?? []],
    ["inputs", manifest.inputs ?? []],
    ["editable_sources", manifest.editable_sources ?? []],
    ["recipes", manifest.recipes ?? []],
    ["vendor_jobs", manifest.vendor_jobs ?? []],
    ["outputs", manifest.outputs ?? []],
    ["qa.reports", manifest.qa?.reports ?? []],
  ];
  for (const [groupName, artifacts] of artifactGroups) {
    for (const artifact of artifacts) {
      await verifyArtifact(
        root,
        artifact,
        `${stage.code}.${groupName}.${artifact.artifact_id ?? "unknown"}`,
        errors,
      );
    }
  }

  if (Number(stage.code.slice(1)) >= 20) {
    const blends = (manifest.editable_sources ?? []).filter(
      (artifact) => artifact.format === "blend",
    );
    if (blends.length !== 1) {
      errors.push(
        `${stage.code}: expected exactly one canonical editable Blender source, found ${blends.length}`,
      );
    }
  }
  return manifest;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = path.resolve(args.root);
  const pipelinePath = path.resolve(root, args.pipeline);
  const pipeline = JSON.parse(await readFile(pipelinePath, "utf8"));
  const errors = [];
  const checkedStages = [];

  for (const stage of pipeline.stages ?? []) {
    if (!stage.manifest) continue;
    const manifest = await validateManifest(root, stage.manifest, stage, errors);
    if (manifest) {
      checkedStages.push({
        code: stage.code,
        revision: manifest.stage.revision,
        state: manifest.stage.state,
      });
    }
  }

  const report = {
    schema_version: "1.0.0",
    pipeline: args.pipeline,
    checked_at: new Date().toISOString(),
    checked_stages: checkedStages,
    valid: errors.length === 0,
    errors,
  };
  if (args.report) {
    await writeFile(
      path.resolve(root, args.report),
      `${JSON.stringify(report, null, 2)}\n`,
      "utf8",
    );
  }
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  if (errors.length > 0) process.exitCode = 1;
}

await main();
