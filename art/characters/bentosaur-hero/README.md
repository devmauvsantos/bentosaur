# Bentosaur Hero

Canonical character record: `character.json`  
Active production pipeline: `char-v001/pipeline.json`  
Current stage: S40 Production Topology  
Current revision: r003  
Human approval owner: Mau

The character pipeline is append-only. Open the canonical source referenced by
the active stage manifest. Do not edit a frozen revision or historical
`art/candidates/` file.

Full production documentation:

```text
docs/character-production-pipeline-v1.md
```

Validation:

```sh
node tools/character_pipeline/validate_character_pipeline.mjs \
  --root /Users/mauvsantos/Workspace/games/Bentosaur \
  --pipeline art/characters/bentosaur-hero/char-v001/pipeline.json \
  --report art/characters/bentosaur-hero/char-v001/pipeline-validation.json
```
