# Bentosaur Mobile Facial Animation Proof V1

**Decision status:** control architecture selected; current proxy failed the
production visual gate.

## Outcome

One reusable 3D Bentosaur can carry mobile-friendly facial controls through
Blender, GLB, and Godot. The experiment validated named morph targets,
independent eye expressions, a three-bone facial skeleton, runtime binding,
and a 21.3K-triangle Mobile-renderer scene.

It did **not** validate the current tongue or jaw deformation as final art.
That distinction is now preserved in both the experiment manifest and the
engine visual-gate report.

## Options tested at the same pose

| Option | What worked | What failed | Decision |
|---|---|---|---|
| Morph-only | Keeps the wide delighted smile silhouette | No physical jaw arc; current tongue remains mostly hidden | Useful baseline |
| Bone-only | Cheap control path is callable | Does not form the smile; the tongue remains occluded behind the uncut muzzle | Reject for hero face |
| Hybrid | Preserves the morph smile while retaining a jaw-control path | Current proxy does not have authored jaw volume, so it looks almost identical to morph-only | Production direction, not yet visually proven |

The target production stack remains:

```text
jaw bone
+ authored delighted-open mouth corrective
+ separate tongue mesh and tongue bone
+ small independent eye morphs
```

The choice is based on the intended final topology—not on pretending the
layered proxy already looks finished.

## Attempt history and stop rule

- `r001`: Blender round trip passed; Godot placed the tongue near the nose.
- `r002`: transforms were applied before binding; structural contract passed;
  tongue moved away from the nose but remains below/behind the mouth, while
  bone-only does not create a visible aperture.
- No blind `r003` tweak is authorized by this result.

After two failed visual passes, the next attempt must change the authoring
approach, not guess another transform:

1. create real lip loops, an aperture, and a recessed mouth cavity;
2. create the tongue in its neutral in-mouth pose;
3. validate only jaw + tongue in Godot;
4. add the smile corrective and eye shapes after that small gate passes.

This makes the next run cheaper in time and easier to diagnose.

The next visual checkpoint must also match the soft reference-art finish:

- one clean, rounded mouth silhouette with smooth corners;
- no cyan/body-colored rim visible inside or below the aperture;
- no faceted or jagged edge at the gameplay camera distance;
- a readable coral tongue contained by the dark cavity;
- the closed state must not show the hidden cavity or tongue.

## Durable evidence

- Blender source/checkpoints:
  `art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r002/`
- Godot lab:
  `game/scenes/labs/facial_animation_options_lab.tscn`
- Engine contract:
  `game/docs/contracts/v002/facial_rig_contract_report.json`
- Runtime states:
  `game/docs/runtime-captures/v002/facial_states_runtime_contact_sheet.png`
- Mouth-method comparison:
  `game/docs/runtime-captures/v002/mouth_mode_comparison.png`
- Human visual-gate report:
  `art/characters/bentosaur-hero/char-v001/experiments/facial-animation-options/r002/qa/godot-runtime/runtime_visual_gate.json`

## Cost

No paid generation or Tripo call was used for either facial-control proof.
Credits spent: `0`. Recorded Tripo balance: `4,695`.
