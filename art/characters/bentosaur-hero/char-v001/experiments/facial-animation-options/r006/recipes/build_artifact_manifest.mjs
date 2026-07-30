import { createHash } from "node:crypto";
import { readdir, readFile, stat, writeFile } from "node:fs/promises";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const candidate = dirname(dirname(fileURLToPath(import.meta.url)));
const output = join(candidate, "artifact_manifest.json");

async function walk(directory) {
  const result = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const absolute = join(directory, entry.name);
    if (
      absolute === output ||
      entry.name === "__pycache__" ||
      entry.name.endsWith(".pyc")
    ) {
      continue;
    }
    if (entry.isDirectory()) {
      result.push(...(await walk(absolute)));
    } else if (entry.isFile()) {
      result.push(absolute);
    }
  }
  return result;
}

const files = [];
for (const absolute of (await walk(candidate)).sort()) {
  const bytes = await readFile(absolute);
  const metadata = await stat(absolute);
  files.push({
    path: relative(candidate, absolute),
    bytes: metadata.size,
    sha256: createHash("sha256").update(bytes).digest("hex"),
  });
}

const manifest = {
  candidate: "bentosaur-facial-experiment-r006-f0-broad-face",
  status: "stopped_after_single_attempt_not_production_approved",
  versioned_research_checkpoint: true,
  production_stage_modified: false,
  paid_api_used: false,
  tripo_credits_spent: 0,
  faceit_run: false,
  artifact_count: files.length,
  files,
};

await writeFile(output, `${JSON.stringify(manifest, null, 2)}\n`);
console.log(JSON.stringify({ output, artifact_count: files.length }, null, 2));
