import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const destination = path.join(root, "artifact_manifest.json");

function walk(directory) {
  return fs
    .readdirSync(directory, { withFileTypes: true })
    .flatMap((entry) => {
      const absolute = path.join(directory, entry.name);
      if (entry.isDirectory()) return walk(absolute);
      if (absolute === destination || entry.name === ".DS_Store") return [];
      return [absolute];
    });
}

function sha256(file) {
  const digest = crypto.createHash("sha256");
  digest.update(fs.readFileSync(file));
  return digest.digest("hex");
}

const artifacts = walk(root)
  .sort()
  .map((file) => ({
    path: path.relative(root, file),
    bytes: fs.statSync(file).size,
    sha256: sha256(file),
  }));

const manifest = {
  schema_version: "1.0.0",
  candidate_id: "tripo-mouth-transfer-candidate",
  status: "stopped_at_locked_alignment_extraction_checkpoint_20",
  retopology_authored: false,
  production_body_modified: false,
  paid_api_usage: {
    tripo_credits_spent: 0,
    recorded_balance: 4695,
  },
  artifact_count: artifacts.length,
  artifacts,
};

fs.writeFileSync(destination, `${JSON.stringify(manifest, null, 2)}\n`);
console.log(JSON.stringify(manifest, null, 2));
