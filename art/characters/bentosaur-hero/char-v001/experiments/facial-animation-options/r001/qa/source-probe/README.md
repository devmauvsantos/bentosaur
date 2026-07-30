# Bentosaur open/closed facial source probe

Date: 2026-07-29
Scope: read-only inspection; no Tripo calls, no durable repository edits.

## Inputs

| State | Source | SHA-256 |
|---|---|---|
| Closed neutral | `art/candidates/tripo/visual-gate-03/h31-detailed-neutral/tripo-out/model.glb` | `4b9ad1cc5562986ff587718c0dbd1f00a5fdf99b33de3c905c3cc0e87ce69607` |
| Delighted open | `art/candidates/tripo/visual-gate-06/h31-detailed-open-mouth/tripo-out/model.glb` | `7c0d7e2e1e4ee8fb4db320880f6f4b5c82c470bce37437ce28d26efa171b01d4` |

## Findings

### Coordinate alignment

Both files arrive at identity transform and use the established source-space
contract:

- front: `+X`;
- character left: `+Y`;
- up: `+Z`;
- origin: effectively the character bounds center.

The open source is `99.75%`, `99.68%`, and `100.02%` of the closed source on
X, Y, and Z respectively. Their centers differ by less than `0.00021` source
units. They can therefore be overlaid as visual references without a rigid
registration pass.

This geometric alignment does **not** make the meshes morph compatible. They
were independently generated and differ over the whole surface.

### Topology and separability

| Property | Closed | Open |
|---|---:|---:|
| Mesh objects | 1 | 1 |
| Connected components | 1 | 1 |
| Vertices | 987,461 | 960,234 |
| Triangles | 1,974,918 | 1,920,464 |
| UV layers | 0 | 0 |
| Shape keys | 0 | 0 |
| Vertex groups | 0 | 0 |

Each model is a single closed, watertight shell. The head, neutral/open eye
forms, lips, mouth cavity floor, visible tongue volume, horns, claws, and body
are fused. The tongue and eyes are not independently selectable animation
parts.

The vertex-count difference is `27,227`. More importantly, vertex order and
connectivity are unrelated. The two GLBs cannot be used directly as two shape
keys.

### Useful facial bounds

Coordinates below use each source's normalized bounds:

```text
normalized = (world - bounds_minimum) / bounds_dimensions
```

The visible open-mouth recession measured from a front `+X` depth comparison
occupies:

```text
Y: 0.3542 .. 0.6458
Z: 0.4326 .. 0.5141
```

On the open source that is approximately:

```text
world Y: -0.09560 .. +0.09541
world Z: -0.06562 .. +0.01424
```

Most first-hit mouth-interior depth lies at world `X 0.297 .. 0.352`; the
outer muzzle is farther forward. This is a useful aperture/cavity envelope,
not a clean lip or tongue segmentation.

The existing fitted eye landmarks transfer safely because the two sources
share alignment:

| Feature | Approximate center XYZ | Conservative world XYZ bounds |
|---|---|---|
| Character-left eye | `(0.40657, 0.09163, 0.10821)` | `(0.39481, 0.05440, 0.05725)` to `(0.41833, 0.12887, 0.15916)` |
| Character-right eye | `(0.40657, -0.09182, 0.10821)` | `(0.39481, -0.12905, 0.05725)` to `(0.41833, -0.05458, 0.15916)` |

Those eye bounds are placement windows for replacement face components, not
topological islands in the Tripo source.

The depth comparison validates that the intentional change is concentrated in
the mouth. Absolute normalized front-depth difference at the 95th percentile:

| Region | P95 |
|---|---:|
| Mouth | 0.06596 |
| Character-left eye window | 0.01480 |
| Character-right eye window | 0.01448 |
| Body below face | 0.00677 |

The open source also deliberately changes the eyes from neutral raised ovals to
delighted raised crescents. Those forms are visual references only.

## Safest small facial proof

Do not try to morph, shrinkwrap, or vertex-transfer one Tripo source into the
other. Do not retopologize the full body before this proof passes.

1. Lock both H3.1 GLBs as immutable visual sources.
2. Retopologize only a small front-head/facial mask against the **open** source.
   Preserve a wider-than-tall lip aperture, three or four lip loops, a recessed
   mouth bag, cheek support, and a jaw-ready lower muzzle. Keep this proof mesh
   separate from the body so failure is cheap.
3. Make the tongue a separate closed low-poly mesh.
4. Duplicate the completed facial topology without changing vertex count or
   order. Sculpt the duplicate closed against the neutral source. Use the
   closed duplicate as `Basis` and the open vertex positions as
   `Mouth_DelightedOpen`.
5. Add one jaw bone and one optional tongue bone. Let jaw rotation provide the
   main opening arc; use the open shape as the lip-corner/cheek/chin corrective.
   A single radial “O” morph is explicitly rejected.
6. Remove the fused Tripo eye forms from the production retopology. Place two
   separate shallow eye patches in the measured windows. For the first proof:
   use a lightweight oval-to-blink shape key per eye and a separate happy-eye
   crescent state. A tiny mesh/atlas swap for oval versus crescent is safer than
   forcing those unrelated silhouettes through the head topology.
7. Author only these proof controls:
   - `Mouth_DelightedOpen`;
   - `Mouth_CloseCorrective`;
   - `Chew_Compress`;
   - `Blink_L`;
   - `Blink_R`;
   - `HappyEyes`;
   - `Jaw`;
   - optional `Tongue`.
8. Export this head-only proof as GLB and verify in Godot Mobile:
   neutral → blink → delighted open → two chews → closed. Test the gameplay
   orthographic camera and phone-scale readability before integrating the body.

For mobile, keeping facial morphs on a small head/mask mesh prevents every
shape key from duplicating the entire body vertex buffer. A practical proof
budget is a few thousand face vertices, a few hundred mouth-interior/tongue
vertices, and very small eye patches. Final triangle limits remain governed by
the project's G40 gate.

## Evidence

- `facial_probe_report.json` — numeric result and recommendation inputs.
- `source_probe_raw.json` — transforms, bounds, and topology.
- `open_closed_front_depth_comparison.png` — normalized depth comparison.
- `closed_front_depth.npz` and `open_front_depth.npz` — lossless sampled maps.
- `open_closed_source_locked_overlay.blend` — both untouched sources, in
  locked collections; closed visible and open hidden by default.
- `inspect_sources.py` and `analyze_depth.py` — exact reproducible recipes.

No paid API usage occurred.
