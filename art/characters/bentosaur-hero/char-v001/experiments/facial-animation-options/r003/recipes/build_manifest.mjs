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
  experiment_id: "bentosaur-hero-facial-animation-options-r003",
  status: "static_visual_gate_failed_stop_rule_reached",
  parent: {
    path: "art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r002/manifest.json",
    sha256: "bfaa0e84daada3620dbe19b880392a2240774ced59a1912780eda2259c6b16bd",
  },
  visual_reference: {
    path: "art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/evidence/mouth-expression-contract-v1-notion.jpg",
  },
  decision: {
    best_attempt: "attempts/a01-wide-window",
    best_attempt_production_approved: false,
    second_attempt: "attempts/a02-narrow-window-normal-transfer",
    second_attempt_rejected: true,
    third_automated_attempt_allowed: false,
    blender_gate_passed: false,
    godot_gate_run: false,
    morph_or_skinning_work_allowed_before_user_choice: false,
    next_options: [
      "manual_localized_blender_retopology_and_welding",
      "2d_atlas_or_sdf_facial_surface_on_reusable_3d_character",
    ],
    visual_approval_owner: "Mau",
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
