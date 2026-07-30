#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const projectRoot = resolve(
  new URL("../../", import.meta.url).pathname,
);
const payloadPath = resolve(
  projectRoot,
  "art/jobs/tripo-visual-gate-04-h31-extreme-texture-payload.json",
);
const manifestPath = resolve(
  projectRoot,
  "art/jobs/tripo-visual-gate-04-h31-extreme-texture.json",
);
const clientModuleUrl = pathToFileURL(
  "/opt/homebrew/lib/node_modules/tripo-cli/dist/core/client.js",
).href;

const [payloadText, manifestText, clientModule] = await Promise.all([
  readFile(payloadPath, "utf8"),
  readFile(manifestPath, "utf8"),
  import(clientModuleUrl),
]);

const payload = JSON.parse(payloadText);
const manifest = JSON.parse(manifestText);
const { TripoClient } = clientModule;
const validateOnly = process.argv.includes("--validate-only");

const fail = (message) => {
  throw new Error(`Submission preflight failed: ${message}`);
};

if (manifest.authorization?.authorized_by !== "user") {
  fail("manifest does not record explicit user authorization");
}
if (manifest.authorization?.credit_cap !== 30) {
  fail("credit cap is not exactly 30");
}
if (manifest.authorization?.rerolls_allowed !== false) {
  fail("rerolls are not explicitly disabled");
}
if (manifest.authorization?.new_geometry_allowed !== false) {
  fail("new geometry is not explicitly disabled");
}

const expectedKeys = [
  "bake",
  "input",
  "model",
  "pbr",
  "texture_alignment",
  "texture_prompt",
  "texture_quality",
  "texture_seed",
].sort();
const actualKeys = Object.keys(payload).sort();
if (JSON.stringify(actualKeys) !== JSON.stringify(expectedKeys)) {
  fail(`unexpected payload keys: ${actualKeys.join(", ")}`);
}

if (payload.input !== manifest.source?.generation_task_id) {
  fail("payload source task does not match the frozen manifest");
}
if (payload.model !== "v3.0-20250812") {
  fail("texture model is not the H3.1-compatible v3 texture model");
}
if (payload.texture_quality !== "extreme") {
  fail("texture quality is not Extreme/8K");
}
if (payload.texture_alignment !== "original_image") {
  fail("texture alignment is not original_image");
}
if (payload.pbr !== true || payload.bake !== false) {
  fail("PBR/bake contract changed");
}
if (payload.texture_seed !== 29072026) {
  fail("texture seed changed");
}

const images = payload.texture_prompt?.images;
if (!Array.isArray(images) || images.length !== 4) {
  fail("texture_prompt.images is not exactly four references");
}
const fileTokens = images.map((image) => image?.file_token);
if (
  fileTokens.some(
    (token) =>
      typeof token !== "string" ||
      !/^file_[0-9a-f]{8}-[0-9a-f-]{27}$/.test(token),
  )
) {
  fail("one or more reference file tokens are malformed");
}
if (new Set(fileTokens).size !== 4) {
  fail("reference file tokens are not unique");
}

const expectedTokens = [
  manifest.texture_references?.front?.file_token,
  manifest.texture_references?.left?.file_token,
  manifest.texture_references?.back?.file_token,
  manifest.texture_references?.right?.file_token,
];
if (JSON.stringify(fileTokens) !== JSON.stringify(expectedTokens)) {
  fail("reference order differs from [front, left, back, right]");
}

if (validateOnly) {
  process.stdout.write(
    `${JSON.stringify({
      validated: true,
      network_calls: 0,
      paid_calls: 0,
      credit_cap: manifest.authorization.credit_cap,
      image_count: fileTokens.length,
      reference_order: ["front", "left", "back", "right"],
      max_retries_on_submission: 0,
    })}\n`,
  );
  process.exit(0);
}

// Paid task-creating POSTs must never be automatically retried because Tripo
// exposes no idempotency key. GET preflight/polling can safely be repeated later.
const client = new TripoClient({
  maxRetries: 0,
  timeoutMs: 60_000,
});

const [balance, sourceTask] = await Promise.all([
  client.getBalance(),
  client.getTask(payload.input),
]);
if (sourceTask?.status !== "success") {
  fail(`source task status is ${sourceTask?.status ?? "unknown"}`);
}
if ((balance?.balance ?? 0) < 30) {
  fail(`available balance ${balance?.balance ?? 0} is below the 30-credit cap`);
}

const taskId = await client.createTask("/v3/models/texture", payload);
if (typeof taskId !== "string" || taskId.length < 8) {
  fail("Tripo returned no usable task ID");
}

process.stdout.write(
  `${JSON.stringify({
    task_id: taskId,
    balance_before: balance.balance,
    frozen_before: balance.frozen,
    max_retries: 0,
    submitted_once: true,
  })}\n`,
);
