import { createHash } from "node:crypto";
import { readdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(process.argv[2] ?? ".");
const manifestPath = path.join(root, "manifest.json");

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walk(absolute)));
    } else if (entry.isFile() && absolute !== manifestPath) {
      files.push(absolute);
    }
  }
  return files;
}

async function artifact(absolute) {
  const bytes = await readFile(absolute);
  return {
    path: path.relative(root, absolute).split(path.sep).join("/"),
    bytes: bytes.byteLength,
    sha256: createHash("sha256").update(bytes).digest("hex"),
  };
}

const files = await walk(root);
const artifacts = await Promise.all(files.map(artifact));
const manifest = {
  schema_version: "1.0.0",
  experiment_id: "bentosaur-hero-facial-animation-options-r001",
  status: "verified_method_proof_not_production_approved",
  parent: {
    path: "art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/bentosaur_hero_s40_production_topology_r003.blend",
    sha256: "181d93014f1667d9044d12e24fa297f4b391c9eb8d1164ddc5f45f3971f7caf9",
  },
  visual_references: [
    {
      state: "closed",
      path: "art/candidates/tripo/visual-gate-03/h31-detailed-neutral/tripo-out/model.glb",
      sha256: "4b9ad1cc5562986ff587718c0dbd1f00a5fdf99b33de3c905c3cc0e87ce69607",
    },
    {
      state: "delighted_open",
      path: "art/candidates/tripo/visual-gate-06/h31-detailed-open-mouth/tripo-out/model.glb",
      sha256: "7c0d7e2e1e4ee8fb4db320880f6f4b5c82c470bce37437ce28d26efa171b01d4",
    },
  ],
  decision: {
    recommended_method: "hybrid_jaw_bone_plus_mouth_corrective",
    eye_method: "small_independent_blend_shape_meshes",
    tongue_method: "separate_skinned_mesh_and_bone",
    visual_approval_owner: "Mau",
    production_approved: false,
  },
  paid_api_usage: {
    tripo_credits_spent: 0,
    recorded_tripo_balance: 4695,
  },
  artifacts,
};

await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
const result = await stat(manifestPath);
console.log(`${manifestPath} (${result.size} bytes, ${artifacts.length} artifacts)`);
