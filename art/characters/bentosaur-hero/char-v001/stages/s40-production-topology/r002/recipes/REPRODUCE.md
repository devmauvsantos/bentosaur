# Hybrid Bootstrap V1 — Reproduction Record

This directory is evidence only. It is not user-approved and has not been
promoted to the production character tree.

## Exact command

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background \
  /Users/mauvsantos/Workspace/games/Bentosaur/art/candidates/tripo/visual-gate-05/h31-smart-lowpoly-10k-quad/repair-test-v1/subagent-cycle-audit/cycle_patch_candidate.blend \
  --python \
  /Users/mauvsantos/Workspace/games/Bentosaur/.tmp/subagents/retopo_execution/build_hybrid_bootstrap_probe.py \
  -- \
  --output \
  /Users/mauvsantos/Workspace/games/Bentosaur/.tmp/subagents/retopo_execution/hybrid-bootstrap-v1 \
  --target-faces 12000
```

The generator is append-only and refuses to overwrite any expected output.
Choose a new output directory to reproduce it again.

## Generator

- File: `../build_hybrid_bootstrap_probe.py`
- SHA-256: `2dde4148310270482e64370aa036a07436536aea3bd632c5ce1dc16cb8d12a37`
- Blender: `5.1.2`

## Input

- Repaired scaffold SHA-256:
  `41a48a1edecb9ace84cef6284e0d17c1355199cc3570af0f1fede78e87d37e7f`

## Saved source files

| Step | SHA-256 |
| --- | --- |
| `00_input_repaired_scaffold_snapshot.blend` | `afd1d32430b8ab3918859db38858f50aacbcb26ff19b66fb96bcd9557878e0f2` |
| `10_quadriflow_unsym_12000.blend` | `d9c698181f9003d65634d42d4febefc37e79928380cee82caa9cd2dc88f38d44` |
| `20_exact_degenerate_cleanup.blend` | `201e2b3046bb6b885bd72c36413cbb7da111467e9bb8cb4f49a4cdf9e1558c5d` |
| `30_symmetrized_negative_y_candidate_not_approved.blend` | `f690e66b6d4d744eb75bcab00af18ef73a1d692d72e8600916528cc7dd571894` |
| `pipeline_report.json` | `e25dc5f162b43bf83c937c6155b6237a346484ef6f2bdd062f3eeb36477c3e79` |
| `qa/deformation-audit/deformation_topology_audit.json` | `2241d4c236c14683e632e5438306b5f0b9fe81b123d1bbc004c6dab86e90b9b2` |

## Final candidate status

- one connected shell;
- 11,884 vertices;
- 11,888 faces;
- 11,636 quads;
- 132 triangles;
- 120 ngons;
- 0 boundary edges;
- 0 non-manifold edges;
- 0 zero-area faces;
- exact bilateral symmetry;
- P95 deviation from the repaired scaffold: 0.0924% of character height;
- maximum deviation: 0.9834% of character height.

This candidate is a topology bootstrap only. Its center strip, mouth, and
deformation loops require authored production work before rigging.
