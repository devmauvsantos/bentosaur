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
| Game | Cozy live-3D mobile bento-stall game populated by cute upright dinosaur characters |
| Engine | Godot 4.7.1 Standard, Mobile renderer, typed GDScript |
| DCC authority | Blender |
| Engine boundary | Deterministic GLB |
| Visual direction | Warm chibi diorama; Nintendo-like toy-box readability without copying protected characters or assets |
| Hero source | H3.1 Extreme is the immutable appearance and silhouette authority |
| Production stage | S40 production topology, in progress |
| Current blocker | One clean canonical neutral face with deformable lips, oral cavity, tongue, and expression-supporting edge flow |
| Facial direction | Faceit-style authoring and baked morph targets; Faceit 2.3 receives one bounded pilot after the topology gate |
| Approval owner | Mau approves all visual character, material, expression, animation, and gameplay gates |

## Start here

1. [Current project status](current-status.md)
2. [Engine lock](engine-decision-live-3d-godot-v1.md)
3. [Character production pipeline](character-production-pipeline-v1.md)
4. [Faceit and AI facial-animation strategy](facial-animation-faceit-ai-pipeline-v1.md)
5. [Binary storage and recovery policy](character-binary-storage-policy-v1.md)
6. [3D/UI/animation ownership](hybrid-3d-ui-and-animation-ownership-v1.md)

## Active work queue

- [ ] Approve one canonical neutral production face before rigging.
- [ ] Approve the maximum delighted-open expression on the same topology.
- [ ] Run one bounded Faceit 2.3 pilot; do not purchase without Mau's approval.
- [ ] Validate blink, happy eyes, delight, and chew as combined controls.
- [ ] Bake the approved controls to morph targets and deform bones.
- [ ] Validate the GLB in the Godot mobile facial lab.
- [ ] Complete S50 UV and bake.
- [ ] Complete S60 final materials and appearance.
- [ ] Complete S70 body/facial rig and skin.
- [ ] Complete the S80 animation library.
- [ ] Build the S90 mobile runtime slice and measure it on physical devices.

## Decision register

| Decision | Status | Document |
|---|---|---|
| Godot live-3D production stack | Locked | [Engine decision](engine-decision-live-3d-godot-v1.md) |
| Blender owns meshes, materials, rigs, and clips | Locked | [3D/UI/animation ownership](hybrid-3d-ui-and-animation-ownership-v1.md) |
| Character binaries use Git LFS selectively | Active | [Storage policy](character-binary-storage-policy-v1.md) |
| Physical 3D mouth, cavity, and tongue | Active; topology not yet approved | [Current status](current-status.md) |
| Faceit-style facial authoring | Selected for bounded proof | [Faceit/AI strategy](facial-animation-faceit-ai-pipeline-v1.md) |
| Full 52-shape ARKit face | Not required for the game | [Faceit/AI strategy](facial-animation-faceit-ai-pipeline-v1.md) |
| Full custom Faceit clone | Rejected before the pilot | [Faceit/AI strategy](facial-animation-faceit-ai-pipeline-v1.md) |
| Notion as canonical documentation | Retired | This page |

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
