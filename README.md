# Bentosaur

Bentosaur is a cozy live-3D chibi-diorama mobile game about serving tiny
bentos to a living street of upright dinosaur neighbors.

## Locked production direction

- Engine: Godot 4.7.x, Mobile renderer, typed GDScript
- DCC authority: Blender
- Runtime boundary: deterministic GLB
- World: live 3D
- UI: screen-space 2D/2.5D over the 3D diorama
- Character props and accessories: always separate assets
- Human approval owner: Mau

## Current build status

The project is in S40 Production Topology for
`bentosaur-hero/char-v001`.

- H3.1 Extreme: frozen visual/high source
- repaired Smart LowPoly: frozen scaffold only
- S40 r003: active all-quad body bootstrap
- r005: frozen rejected static Tripo-mouth transfer research
- current blocker: one canonical neutral/deformable face
- facial direction: bounded Faceit 2.3 authoring pilot after topology approval
- Godot mobile facial-control lab: functional proof, not final art
- UVs, final materials, production rig, animation, and Godot runtime: blocked
  until G40 passes and Mau approves it

## Documentation and character pipeline

Start here:

- `docs/README.md`
- `docs/current-status.md`
- `docs/facial-animation-faceit-ai-pipeline-v1.md`
- `docs/character-production-pipeline-v1.md`
- `docs/character-binary-storage-policy-v1.md`
- `art/characters/bentosaur-hero/char-v001/pipeline.json`
- `tools/character_pipeline/README.md`

Check the source chain:

```sh
node tools/character_pipeline/character_pipeline.mjs status \
  --root "$PWD" \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json

node tools/character_pipeline/validate_character_pipeline.mjs \
  --root "$PWD" \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json \
  --report art/characters/bentosaur-hero/char-v001/pipeline-validation.json
```

Run the automation tests:

```sh
node --test tools/character_pipeline/tests/character_pipeline.test.mjs
```

## Source rule

Every meaningful topology, UV, material, rig, weight, corrective-shape,
animation, or export-contract operation gets a numbered native checkpoint.
Frozen revisions are never overwritten. Human visual approval is distinct
from automated QA.

Large DCC binaries are preserved and hashed locally and routed through Git
LFS. Do not push new binary checkpoints until remote LFS quota, billing, and
restore behavior have been explicitly accepted; multiple Blender sources
exceed GitHub's ordinary file limit.

## Secrets

Never commit API keys, authorization headers, signed URLs, vendor credentials,
or private receipts containing secrets.
