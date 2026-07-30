# VG05 repair and rebake proof

Status: **successful geometry/material proof, not production-approved**

This experiment repaired a disposable copy of the Tripo Smart LowPoly FBX and
rebaked base colour from the H3.1 Extreme source. It made no Tripo API calls
and consumed no credits.

## Result

- The visible belly and underarm openings are closed.
- Native Blender topology reaches zero boundary edges and zero non-manifold
  edges.
- A fresh UV atlas and selected-to-active bake remove the black/garbage texture
  samples that appear when generated faces inherit the Tripo atlas.
- The repaired silhouette remains visually aligned with H3.1.

## Exact native topology

| Metric | Raw Smart LowPoly | Repaired copy |
| --- | ---: | ---: |
| Vertices | 12,059 | 12,059 |
| Edges | 25,079 | 25,079 |
| Faces | 12,996 | 13,020 |
| Evaluated triangles | 24,071 | 24,118 |
| Quad faces | 11,075 | 11,075 |
| Triangle faces | 1,921 | 1,939 |
| N-gons | 0 | 6 |
| Boundary edges | 95 | 0 |
| Non-manifold edges | 95 | 0 |

The conservative repair added 22 faces through Blender's hole fill, which
left 12 boundary edges in two loops. Contextual fill added two more faces and
closed the remaining boundaries.

`rebake_report.json` is authoritative for repair topology. The visual
evaluator re-imports the exported GLB; glTF splits vertices along UV/material
seams, so its BMesh boundary count describes serialized vertex splits rather
than the watertight native Blender mesh tested immediately before export.

## Bake proof

- Map: base colour only
- Resolution: 1,024 × 1,024
- UV: new `UV_REBAKE` Smart UV atlas
- Bake time: 4.429 seconds on this machine
- Cage extrusion: 0.006
- Maximum ray distance: 0.025
- Margin: 12 px
- Exported GLB: 1,902,712 bytes
- SHA-256:
  `b9d80ab6c2e1362a14aa4703c270f7fda2b0b33b5586148e7c4f884c8f99811a`

## Decision

The repair route is viable, but it is not entirely one-click. The six
generated n-gons need a small manual retopology/controlled triangulation pass.
Automatic subdivision, center projection and blanket triangulation were tested
and rejected because they created folded patches or a non-manifold edge.

Before production use, also create the approved UV layout and bake final
base-colour, normal, roughness, metallic and AO maps. Painter work comes after
that.

## Files

- `repaired_rebaked.glb` — surfaced proof export
- `repaired_basecolor_1k.png` — proof base-colour atlas
- `rebake_report.json` — machine-readable native metrics and bake settings
- `evaluation/metrics.json` — post-export visual-evaluation report
- `comparison/` — labeled high/raw/repaired comparison boards
