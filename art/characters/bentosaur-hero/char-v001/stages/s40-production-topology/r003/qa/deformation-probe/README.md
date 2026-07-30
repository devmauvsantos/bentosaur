# S40 R003 canonical deformation confirmation

## Result

**R003 is materially better than the rejected zero-motion fallback, but it
still fails the bounded deformation confirmation.**

- Neutral: **pass**
- Reach/tray hold: **fail — shoulder/armpit transition**
- Squat: **fail — hip/groin compression and isolated knee/leg outliers**
- Walk extreme: **fail — shoulder plus hip/knee transition**
- Tail bend: **pass**

This result belongs only to the promoted S40 R003 axis-QuadriFlow candidate.
The previous fallback report does not identify or measure this mesh.

## Exact input

- Canonical file:
  `/Users/mauvsantos/Workspace/games/Bentosaur/art/characters/bentosaur-hero/char-v001/stages/s40-production-topology/r003/source/bentosaur_hero_s40_production_topology_r003.blend`
- Object: `BENTOSAUR_BODY_RETOPO_WIP_R003`
- SHA-256:
  `181d93014f1667d9044d12e24fa297f4b391c9eb8d1164ddc5f45f3971f7caf9`
- Topology: 10,050 vertices, 20,096 edges, 10,048 quad faces,
  zero boundary edges, zero non-manifold edges.

`stages/00_canonical_source_exact_copy.blend` is byte-identical to the
canonical source.

## Coordinate contract: confirmed

R003 is already in the production contract:

- front `-Y`;
- character-left `+X`;
- up `+Z`;
- floor `Z=0`;
- approximately one meter high.

Measurements:

- bounds X: `-0.3351316154` to `+0.3351316154`;
- bounds Y: `-0.4419375658` to `+0.4384065270`;
- bounds Z: `0.0` to `0.9995938540`;
- X-mirror P95 error: `6.664e-8`;
- 99.990% of vertices mirrored within `1e-6`; maximum error
  `1.0117e-6`, effectively the tolerance boundary;
- tail sample mean Y `+0.26118`, maximum `+0.43841`;
- front/head sample mean Y `-0.23034`, minimum `-0.44194`.

Unlike the rejected fallback, no axis remapping is required.

## Test setup

The previous diagnostic skeleton was transformed into the canonical coordinate
system and applied as a temporary stress rig:

- root, pelvis, spine, chest, neck, head;
- non-deforming jaw placeholder;
- upper arm, forearm, hand per side;
- thigh, shin, foot per side;
- five tail bones.

Blender automatic weights were preserved before edits:

- zero unweighted vertices;
- maximum 14 influences;
- 2,632 vertices over four influences;
- mean 3.934 influences;
- weight sums from 0.8224 to 0.9999.

One bounded cleanup pass was allowed:

- rigidly lock the head/frill mass after the first pass visibly assigned lower
  frill vertices to the arm chain;
- remove opposite-side limb leakage;
- remove impossible tail leakage;
- normalize and cap at four influences.

There were **zero iterative weight-polish passes**. The selected weights have
zero unweighted vertices, maximum four influences, and normalized sums.

## Objective pose findings

### Reach/tray hold — fail

Each arm region had:

- one face below `0.10x` neutral area;
- 23 faces above `3x` area;
- 30 edges above `2.5x` length;
- P95 face-area ratio `2.666x`;
- P95 edge-length ratio `1.428x`.

The head/neck core remained exactly stable, but a visible lower
frill/shoulder transition sheet remains. This establishes a shoulder-region
problem under minimally cleaned weights; it does not by itself prove whether
the final correction belongs entirely to topology or authored weights.

### Squat — fail

The broad leg distributions were much healthier than the fallback:

- leg P05/P95 area: `0.746x` / `1.210x`;
- leg P05/P95 edge: `0.852x` / `1.197x`.

However, the groin/torso attachment still produced:

- one face at `0.079x` area;
- 19 edges below `0.35x` length.

Both leg regions also retained isolated stretch outliers. Hip/groin compression
therefore reproduces; knee/leg failure is localized rather than global.

### Walk extreme — fail

- right leg: four faces below `0.10x` area and two edges below `0.35x`;
- torso/attachment: two faces below `0.10x` and 12 edges below `0.35x`;
- both arms retained shoulder stretch outliers;
- head/neck remained stable.

This reproduces the shoulder and hip/knee concern on R003, although at a much
smaller scale than the fallback.

### Tail bend — pass

R003 does **not** reproduce the fallback tail failure:

- tail P05/P95 area: `0.689x` / `1.268x`;
- tail P05/P95 edge: `0.754x` / `1.187x`;
- minimum area `0.532x`;
- minimum edge `0.471x`;
- no collapse or severe-stretch threshold flags.

The five-bone tail concept is viable on R003 under this test.

## Preserved checkpoints

- `stages/00_canonical_source_exact_copy.blend`
- `stages/05_body_only_snapshot.blend`
- `stages/10_neutral_armature_no_weights.blend`
- `stages/20_automatic_weights.blend`
- `stages/30_minimal_confirmation_weights.blend` — first-pass evidence
- `stages/31_minimal_confirmation_weights_headlock.blend` — selected bounded
  confirmation
- `stages/40/50/60/70/80_*.blend` — first-pass pose sources
- `stages/41/51/61/71/81_*_headlock.blend` — selected pose sources

The first pass and its exact recipe/report remain preserved. Nothing under the
canonical R003 production directory was modified.

## Evidence

- `evidence/r003_headlock_pose_contact_sheet.png`
- `evidence/fallback_vs_r003_failure_zones.png`
- `evidence/r003_coordinate_contract_views.png`
- `r003_confirmation_report_v2.json` — selected objective metrics
- `r003_confirmation_report_v1.json` — preserved first pass

## Decision

Do not revert to the fallback, and do not discard R003. R003 is the correct
candidate to continue from.

Do not call it deformation-ready yet. The next bounded work should be:

1. manually inspect/route the shoulder-armpit transition;
2. manually inspect/route the pelvis-groin and knee transition;
3. author production weights on those regions;
4. rerun reach, squat, and walk;
5. retain the existing tail topology unless later animation reveals a new
   problem.

This confirmation does not test the mouth, face, materials, final animation
quality, or Godot runtime.

