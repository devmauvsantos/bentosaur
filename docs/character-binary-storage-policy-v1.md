# Bentosaur Character Binary Storage Policy V1

Status: required before the first production push  
Applies to: native DCC sources, vendor packages, textures, renders, and runtime exports

## Why this exists

The character pipeline intentionally saves an editable source at every
meaningful rollback point. On July 29, 2026, the local working set already
measured approximately:

- `art/`: 5.0 GB;
- `.tmp/`: 8.1 GB;
- multiple individual `.blend` files larger than 100 MB.

Those files must remain recoverable, but committing every binary revision to
ordinary Git would make the repository unpushable and increasingly expensive
to clone.

GitHub blocks ordinary Git objects larger than 100 MiB and recommends Git LFS
for binary files. Git LFS stores every changed binary version as a complete
object, so indiscriminately tracking every Blender checkpoint also consumes
storage quickly.

## Storage tiers

| Tier | Contents | Authority | Remote requirement |
|---|---|---|---|
| A — Git | code, schemas, manifests, recipes, Markdown, small QA evidence | repository | normal Git |
| B — Canonical binaries | frozen stage masters and the reviewed successful checkpoint chain | native `.blend` / `.spp` | Git LFS or versioned object storage |
| C — Experiment archive | every meaningful WIP checkpoint, rejected branch, and diagnostic scene | hashed local archive | second backup required before cleanup |
| D — Rebuildable derivatives | temporary renders, caches, Godot imports, generated intermediates | recipe + source | not required unless used as gate evidence |

## Non-negotiable rules

1. Nothing in Tier B or C is deleted merely to make Git smaller.
2. A stage cannot freeze until its canonical native source exists in two
   independently recoverable locations and both copies match the manifest
   SHA-256.
3. Every Tier C experiment has an inventory that records path, bytes,
   SHA-256, branch/result status, and the best checkpoint.
4. Only the reviewed successful checkpoint chain is promoted from Tier C into
   Tier B.
5. Failed branches remain recoverable but do not enter ordinary Git history.
6. Generated derivatives never replace the native source or its recipe.
7. API keys, vendor authorization headers, and signed URLs never enter any
   storage tier.
8. `.tmp/` means “working archive, not yet remotely durable,” not “safe to
   delete.”

## Recommended repository boundary

Track in ordinary Git:

- `docs/`;
- `tools/`;
- `game/`;
- JSON schemas and manifests;
- small PNG/JPEG approval boards;
- hashes and provenance receipts without secrets.

Track through the selected binary backend:

- canonical `.blend` and `.spp` masters;
- approved GLB delivery files;
- irreplaceable high-resolution texture sources;
- the reviewed successful native checkpoint chain.

Keep out of Git while preserving and backing up separately:

- `.tmp/subagents/**`;
- discarded vendor variants;
- failed Boolean/remesh/rig branches;
- render caches and other reproducible intermediates.

## Current implementation

Git LFS `3.7.1` is installed and configured locally. The repository routes
native 3D sources, interchange files, raster evidence, audio, video, and
packaged binary deliverables through LFS. The first production baseline and
facial-proof revisions are committed locally.

This solves local version history; it does not yet prove remote durability:

- no binary commit has been pushed from this workstation;
- the GitHub account's LFS quota and billing ownership have not been accepted;
- the separate Tier C archive backup has not been configured;
- a clean-directory restore test has not been completed.

Until those checks pass, Git is a local recoverable history—not the second
independent copy required to freeze a production stage.

## Recommended next storage decision

For the one-person vertical slice:

1. keep ordinary Git for code, manifests, documentation, and small evidence;
2. use Git LFS only for frozen canonical masters and the reviewed successful
   checkpoint chain;
3. use a separate versioned object-storage/archive backup for the full
   experiment inventory;
4. set a hard monthly storage/bandwidth budget before the first binary push;
5. test restore on a clean directory before treating the backup as valid.

This gives fast code clones, traceable canonical art, and complete rollback
history without paying to store every experimental Blender save as Git
history.

## Primary references

- GitHub repository limits:
  https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits
- GitHub large-file limits:
  https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- Git LFS behavior and plan limits:
  https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage
- Git LFS billing:
  https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-git-large-file-storage/about-billing-for-git-large-file-storage
