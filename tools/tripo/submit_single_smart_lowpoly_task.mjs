#!/usr/bin/env node

import { pathToFileURL } from "node:url";

const clientModuleUrl = pathToFileURL(
  "/opt/homebrew/lib/node_modules/tripo-cli/dist/core/client.js",
).href;

const { TripoClient } = await import(clientModuleUrl);

const sourceTaskId = "26811821-3e6d-4b62-a695-679275c04f60";
const endpoint = "/v3/mesh/decimate";
const creditCap = 30;
const payload = {
  input: sourceTaskId,
  model: "v2.0",
  face_limit: 10_000,
  quad: true,
  bake: true,
};
const validateOnly = process.argv.includes("--validate-only");

const fail = (message) => {
  throw new Error(`Smart LowPoly submission preflight failed: ${message}`);
};

if (payload.input !== sourceTaskId) {
  fail("source task changed");
}
if (payload.model !== "v2.0") {
  fail("retopology model is not locked to v2.0");
}
if (payload.face_limit !== 10_000 || payload.quad !== true) {
  fail("target is not exactly 10,000 quad faces");
}
if (payload.bake !== true) {
  fail("source appearance baking is not enabled");
}

if (validateOnly) {
  process.stdout.write(
    `${JSON.stringify({
      validated: true,
      endpoint,
      payload,
      network_calls: 0,
      paid_calls: 0,
      credit_cap: creditCap,
      max_retries_on_submission: 0,
    })}\n`,
  );
  process.exit(0);
}

// Tripo exposes no idempotency key. Never automatically retry the paid POST.
const client = new TripoClient({
  maxRetries: 0,
  timeoutMs: 60_000,
});

const [balance, sourceTask] = await Promise.all([
  client.getBalance(),
  client.getTask(sourceTaskId),
]);

if (sourceTask?.status !== "success") {
  fail(`source task status is ${sourceTask?.status ?? "unknown"}`);
}
if (sourceTask?.type !== "texture_model") {
  fail(`source task type is ${sourceTask?.type ?? "unknown"}`);
}
if ((balance?.balance ?? 0) < creditCap) {
  fail(
    `available balance ${balance?.balance ?? 0} is below the ${creditCap}-credit cap`,
  );
}
if ((balance?.frozen ?? 0) !== 0) {
  fail(`account already has ${balance.frozen} frozen credits`);
}

const taskId = await client.createTask(endpoint, payload);
if (typeof taskId !== "string" || taskId.length < 8) {
  fail("Tripo returned no usable task ID");
}

process.stdout.write(
  `${JSON.stringify({
    task_id: taskId,
    endpoint,
    payload,
    balance_before: balance.balance,
    frozen_before: balance.frozen,
    max_retries: 0,
    submitted_once: true,
  })}\n`,
);
