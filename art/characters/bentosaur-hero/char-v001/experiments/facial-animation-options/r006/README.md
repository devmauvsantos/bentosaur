# Bentosaur Facial Experiment r006

Status: frozen rejected F0 checkpoint

Production approval: no

Rigging or Faceit authorization: no

This revision preserves the one bounded broad-face topology attempt authorized
after r005. It tested whether a larger cheek/muzzle replacement and two
original-surface transition rings could turn the approved Tripo
delighted-open mouth into one clean mobile all-quad shell.

The attempt was stopped at its first real gate. No correction candidate,
neutral shape, Faceit setup, rig, animation, Godot export, paid API call, or
Tripo generation followed.

## Exact input

The immutable input remains the already-versioned r004 checkpoint:

`../r004/work/20_source_mouth_region_extraction.blend`

SHA-256:

`9f9ca58f34dc46037e7c3bcadd2e8c399ba7e12f62a9551322c1a2c4dde3951f`

It contains:

- `S40_R003_PRODUCTION_BODY_LOCKED`;
- `TRIPO_VG06_OPEN_SOURCE_LOCKED`;
- `TRIPO_VG06_MOUTH_REGION_SOURCE_LOCKED`.

The input is referenced rather than duplicated in r006.

## What was attempted once

The recipe:

`recipes/build_f0_single_attempt.py`

performed one deterministic build:

1. duplicate the locked S40 body;
2. remove one measured 496-quad broad cheek/muzzle region;
3. preserve its complete 112-vertex boundary exactly;
4. keep the first two transition rings on the original S40 surface;
5. approach the validated Tripo aperture with two further rings;
6. build a four-segment recessed mouth bag and all-quad cap;
7. keep the tongue as a separate closed object;
8. run the technical gate before creating neutral/open shape keys.

The resulting frozen Blender source is:

`work/10_F0_BROAD_OPEN_TOPOLOGY_FAILED_FROZEN.blend`

## What passed

- exact upstream input hash;
- unchanged body topology outside the selected broad region;
- exact outer-boundary coordinates;
- one connected closed all-quad body shell;
- Euler characteristic `2`;
- zero boundary, non-manifold, overfull, or loose elements;
- zero inconsistent directed edges;
- separate closed tongue;
- aperture-to-Tripo fit:
  - mean `0.00143`;
  - P95 `0.00216`;
  - maximum `0.00253`;
- mobile working budget:
  - body `22,464` rendered triangles;
  - tongue `704` rendered triangles;
  - total `23,168`, below the `24,000` checkpoint limit.

## Why it failed

The broad cut did not solve the topology-flow problem:

- seam-normal P95 `162.95°`;
- seam-normal maximum `177.18°`;
- patch aspect P95 `8.45`;
- patch aspect maximum `49.19`;
- `117` vertex-disjoint patch-involved overlap candidates;
- visible pinches and tears extend across both lower cheeks.

The mouth silhouette and cavity remain promising. The failure is the
one-to-one loop bridge between an existing body boundary and a very different
stylized mouth loop. A radial or column bridge cannot decide where facial
edge flow must split, turn, and terminate. Making the cut larger merely moves
the failure outward.

The complete machine-readable report is:

`qa/f0_single_attempt_report.json`

## Stop decision

The user's one-attempt limit was honored. The technical gate failed, so the
recipe deliberately did not create:

- a neutral Basis;
- an open expression shape key;
- intermediate expression states;
- a Faceit registration or bind;
- a rig or animation;
- a GLB or Godot import.

This candidate must not be promoted, rigged, or exported.

## What this establishes

Automated concentric bridging is retired for this character.

The next viable topology operation must explicitly author facial flow:

- Blender Mirror plus Poly Build plus Shrinkwrap against the locked Tripo
  target; or
- a dedicated topology-transfer/retopology tool evaluated as its own gated
  experiment.

For the installed toolset, the first option is available now. It is an
interactive retopology task, not a Faceit or AI-generation task. Faceit
remains the next stage only after that topology is approved.

## Evidence

- `evidence/f0_r006_stop_board.png`;
- `evidence/01_front_full.png`;
- `evidence/02_three_quarter_full.png`;
- `evidence/03_front_mouth_close.png`;
- `evidence/04_three_quarter_mouth_close.png`;
- `evidence/05_front_mouth_wire.png`.

Mau did not approve this candidate.
