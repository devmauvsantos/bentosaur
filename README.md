# Bentosaur

Bentosaur is a cozy mobile game about serving tiny bentos to a living street
of upright dinosaur neighbors.

## Active development direction

- Engine: Godot 4.7.x, Mobile renderer, typed GDScript
- Visual direction: flat-cel 2D
- Runtime: registered 2D character parts plus authored full-pose sequences
- UI: screen-space Godot controls
- Props, food, effects, and accessories remain separate assets
- Human approval owner: Mau

The former live-3D Blender/GLB direction remains preserved as a paused
fallback; it is not the active implementation path.

## Current build status

The Godot project now boots the layered Home Village menu:

- registered rainy street and animated warm lighting;
- uniformly scaled V002 empty stall;
- approved anime-transfer shader preset 3;
- separate looping music and rain ambience;
- V011-corrected crate perspective, rank sockets, and stockpot lid contact;
- physical iPhone 17 Pro Max deployment under Mau's personal Apple team.

The bounded first playable remains preserved as a separate scene with:

- classic text-stall Home;
- three sequential bento orders;
- four ingredients and three ordered compartments;
- correctable submissions with no timer or dead end;
- local coins, first-try stars, shift summary, and replay;
- JSON-authored shift content and a passing headless model test.

The concept screens are temporary backdrops. The next gate is founder playtest,
followed by replacing the baked customer with one registered animated 2D
character.

Run the current build:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path game
```

## Documentation and character pipeline

Start here:

- `docs/README.md`
- `docs/current-status.md`
- `docs/first-playable-v1.md`
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
