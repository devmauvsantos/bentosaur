# Bentosaur Documentation

Status: canonical documentation home

Effective: 2026-07-30

Repository: `devmauvsantos/bentosaur`

This directory is the source of truth for Bentosaur. The former Notion pages
are historical snapshots and are no longer maintained. Decisions, status,
research, pipelines, approval evidence, and rollback instructions must be
recorded in this repository before work is treated as durable.

## Current project snapshot

| Area | Locked or current state |
|---|---|
| Game | Cozy mobile bento-stall game populated by cute upright dinosaur characters |
| Engine | Godot 4.7.1 Standard, Mobile renderer, typed GDScript |
| Active art authority | Editable registered 2D layer/vector masters; generated screens are targets only |
| Preserved 3D authority | Blender and deterministic GLB |
| Visual direction | Founder-selected flat-cel 2D; production lock pending one bounded Godot proof |
| Hero source | H3.1 Extreme is the immutable appearance and silhouette authority |
| Production stage | First playable v1: complete one-shift loop in Godot |
| Current blocker | Founder playtest of the functional serving loop |
| 3D fallback | S40 facial topology and Faceit research are preserved but paused |
| Approval owner | Mau approves all visual character, material, expression, animation, and gameplay gates |

## Start here

1. [Current project status](current-status.md)
2. [First playable v1](first-playable-v1.md)
3. [Mobile display quality contract](mobile-display-quality-contract-v001.md)
4. [Home Village rain lab](home-village-rain-lab-v001.md)
5. [Home Village Rain V002 checkpoint](checkpoints/2026-07-31-home-village-rain-v002.md)
6. [2D menu alternatives and idle proof](visual-explorations/2d-menu-alternatives-and-idle-proof-v3.md)
7. [2D flat-cel animation and screen proof](visual-explorations/2d-flat-cel-animation-and-screen-proof-v2.md)
8. [2D flat-cel production feasibility](visual-explorations/2d-flat-cel-production-feasibility-v1.md)
9. [Preserved live-3D engine lock](engine-decision-live-3d-godot-v1.md)
10. [Character production pipeline](character-production-pipeline-v1.md)
11. [Faceit and AI facial-animation strategy](facial-animation-faceit-ai-pipeline-v1.md)
12. [F0 r006 topology stop report](facial-topology-f0-r006-stop-report.md)
13. [Binary storage and recovery policy](character-binary-storage-policy-v1.md)
14. [3D/UI/animation ownership](hybrid-3d-ui-and-animation-ownership-v1.md)

## Active work queue

- [x] Select the flat-cel gameplay language as the leading direction for now.
- [x] Prove visual continuity across neutral/happy, home/menu, and book.
- [x] Separate the three laugh marks from the character face.
- [x] Compare icon-grid, diegetic, dock, and classic text home menus.
- [x] Generate neutral, blink, wave, and delighted mascot source states.
- [x] Render one grounded breathing-and-blink idle prototype.
- [x] Freeze the first-playable scope.
- [x] Implement the Home → three customers → Summary loop in Godot.
- [x] Move order content into a validated JSON contract.
- [x] Add local coin saving and deterministic model coverage.
- [x] Lock native-resolution canvas, ultratall expansion, Metal, and ProMotion
  project settings.
- [x] Add an automated mobile display-quality contract.
- [ ] Outpaint and upscale the approved Home Village to its production
  `1440 × 3200` layered ultratall master.
- [ ] Mau plays and approves or rejects the core loop.
- [ ] Replace the baked counter customer with one registered animated character.
- [ ] Redraw one front character into registered production layers.
- [ ] Author open, blink, and happy eyes plus soft, open, and chew mouths.
- [ ] Build front idle, blink, delight, and chew in Godot.
- [ ] Build one side walk and mirror it for the opposite direction.
- [ ] Validate a separate prop socket.
- [ ] Build one draggable mesh/shader page turn with commit and cancel.
- [ ] Add paper sound, optional haptic, buttons, and reduced motion.
- [ ] Measure the character and book proof on physical phones.
- [ ] Lock flat-cel 2D for production or reopen live 3D from preserved evidence.

Paused fallback queue:

- [x] Preserve the rejected r006 broad-face bridge and all 3D evidence.
- [x] Install and smoke-test Faceit 2.3.71 in Blender 5.1.2.
- [ ] Resume 3D facial topology, Faceit, S50–S90 only if Mau reopens live 3D.

## Decision register

| Decision | Status | Document |
|---|---|---|
| Flat-cel 2D visual direction | Founder-selected; production proof pending | [2D animation/screen proof](visual-explorations/2d-flat-cel-animation-and-screen-proof-v2.md) |
| Mobile display baseline | Locked: 720 × 1280 logical canvas, native target rendering, ultratall expand, safe-area UI | [Display quality contract](mobile-display-quality-contract-v001.md) |
| Godot live-3D production stack | Preserved last lock; paused during 2D proof | [Engine decision](engine-decision-live-3d-godot-v1.md) |
| Blender owns 3D meshes, materials, rigs, and clips | Preserved for fallback | [3D/UI/animation ownership](hybrid-3d-ui-and-animation-ownership-v1.md) |
| Character binaries use Git LFS selectively | Active | [Storage policy](character-binary-storage-policy-v1.md) |
| Physical 3D mouth, cavity, and tongue | Preserved fallback; topology not approved | [Current status](current-status.md) |
| Faceit-style facial authoring | Preserved for a bounded pilot only if 3D reopens | [Faceit/AI strategy](facial-animation-faceit-ai-pipeline-v1.md) |
| Full 52-shape ARKit face | Not required for the game | [Faceit/AI strategy](facial-animation-faceit-ai-pipeline-v1.md) |
| Full custom Faceit clone | Rejected before the pilot | [Faceit/AI strategy](facial-animation-faceit-ai-pipeline-v1.md) |
| Notion as canonical documentation | Retired | This page |
| Flat-cel 2D contingency | Superseded by active visual direction | [2D feasibility](visual-explorations/2d-flat-cel-production-feasibility-v1.md) |

## Document states

- **Locked**: do not reopen without one of the documented trigger conditions.
- **Active**: current plan or contract.
- **Research**: evidence that informs a decision but is not an implementation
  promise.
- **Frozen experiment**: reproducible evidence, including rejected work.
- **Superseded**: retained for history; follow the replacement document.

## Documentation rules

1. New decisions go in `docs/` and link from this page.
2. Native character sources and visual evidence live under `art/`.
3. Runtime contracts and captures live under `game/docs/`.
4. Every frozen experiment records status, inputs, outputs, SHA-256 hashes,
   cost, stop conditions, and whether Mau approved it.
5. Rejected experiments remain clearly marked and never silently enter the
   production lineage.
6. API credentials, signed URLs, and authorization headers never enter Git.
7. Notion is not updated or consulted unless Mau explicitly reactivates it.
