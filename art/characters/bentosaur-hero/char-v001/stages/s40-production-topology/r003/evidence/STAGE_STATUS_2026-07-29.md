# S40 r003 — Post-Probe Status

Status: WIP technical bootstrap  
Human approval: pending  
Rig-ready: no

## Mouth decision

The first welded-mouth experiment proved that a four-loop aperture, recessed
bag, separate tongue, separate eyes, and exact symmetric neutral/open states
can be integrated into one closed body mesh.

It failed the visual target. Its circular/oval aperture and visible outer lip
ring read as an `O`/pacifier muzzle, not the approved Bentosaur expression.
Mau explicitly rejected it on July 29, 2026.

The replacement must have:

- a shallow curved smile line in neutral;
- a wider-than-tall, soft bean/rounded-triangle delighted opening;
- visibly lifted mouth corners;
- jaw rotation plus lip-corner and corrective shapes;
- a recessed dark cavity and small separate tongue;
- no protruding circular lip ring.

The rejected topology proof remains in the hashed Tier C experiment archive.
It is not part of the canonical r003 source.

## Bounded deformation result

The probe used the exact canonical source:

```text
source/bentosaur_hero_s40_production_topology_r003.blend
SHA-256 181d93014f1667d9044d12e24fa297f4b391c9eb8d1164ddc5f45f3971f7caf9
```

It confirmed front `-Y`, character-left `+X`, up `+Z`, floor `Z = 0`,
bilateral local `X = 0` symmetry, and the approximate one-metre height.

Results:

- neutral: pass;
- reach/tray hold: fail at shoulder/armpit;
- squat: fail at hip/groin plus local knee/leg outliers;
- extreme walk: fail at shoulder and hip/knee;
- tail bend: pass.

The 16 diagnostic `.blend` checkpoints remain preserved in:

```text
.tmp/subagents/deformation_rig_probe/r003-confirmation/stages/
```

Their 67-file hash inventory is copied into `qa/deformation-probe/` together
with compact reports, exact recipes, and visual evidence.

## Next valid production work

1. Replace the rejected oval mouth with the target smile system.
2. Author localized symmetric shoulder/armpit and pelvis/groin/knee flow.
3. Retain the passing tail.
4. Merge only successful mouth and joint branches into the next S40 revision.
5. Rerun neutral, reach, squat, walk, tail, smile, chew, and delighted-open
   tests.
6. Present the complete G40 visual and deformation reel to Mau.

No UV, final material, production rig, or animation-library work is authorized
until G40 is technically complete and Mau approves it.
