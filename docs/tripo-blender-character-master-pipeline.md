# Tripo + Blender MCP Character Master Pipeline

**Status:** Recommended controlled bake-off; not yet the production character
pipeline  
**Decision date:** July 29, 2026  
**Parent decision:** `3d-characters-with-2d-pixel-look-prototype.md`  
**Machine-readable test:** `art/jobs/tripo-blender-character-master-bakeoff-v1.json`

## Decision

Run one controlled Tripo-to-Blender-to-Godot character test before producing the
cast.

Use:

- **Tripo CLI/API** to propose multiview base meshes, perform the first rig
  check, and generate a disposable locomotion test;
- **Blender Lab MCP** to inspect and iterate on the Blender scene;
- **reviewed, versioned Blender Python scripts** for repeatable cleanup, camera,
  palette, validation, rendering, and export;
- **Blender** as the only authoritative character-master file;
- **Godot** to compare a live toon/pixel character against sprite sheets baked
  from the same master.

Tripo is a base-mesh and initial-rig factory. It does not own Bentosaur's
silhouette, face, palette, skeleton extensions, animations, or final model.

## Live Test 01 result

The July 29, 2026 prop-free P1 text test completed successfully. Full evidence
is in `tripo-live-test-01-p1-text.md` and
`art/jobs/tripo-live-test-01-p1-text.json`.

For 75 API credits total:

- P1 produced one 4,826-triangle upright biped with two free arms and no fused
  prop;
- the free rig check returned `riggable: true`, `rig_type: biped`;
- Tripo produced a 32-bone armature with a three-bone tail chain;
- one animated GLB imported into Blender with named idle and walk actions;
- the same model rendered correctly from front, left, back, right, and
  three-quarter cameras.

**API credit ledger:** 5,000 starting → 75 consumed (USD 0.75) → 4,925
remaining. Tripo calls these credits, not tokens.

Pipeline verdict: pass. Canonical identity verdict: fail. Default animation
shipping verdict: fail.

The test model is too puppy-faced, lacks the rounded cream frill knobs, and has
generic hand and motion language. The retargeted motions require grounding and
short-leg deformation cleanup. Keep it as a disposable proof; do not turn it
into the hero.

The test proves the reusable-master architecture. The canonical request still
requires four approved orthographic views and the P1 versus H3.1 bake-off below.

## Hard Gate 0: complete visual 3D approval before rigging or animation

Every production character run stops after the candidate has both:

1. a bare-geometry inspection; and
2. its complete Bentosaur surface treatment.

“Complete visual candidate” means the final body shape, sage/cream/coral
materials, texture where needed, neutral face, and the intended toon/pixel
presentation. It does not mean rigged or animated.

Before rig checking, rigging, retargeting, or custom animation, the run must
produce:

- raw GLB and complete task receipt;
- surfaced GLB plus every texture/material artifact and receipt;
- clay front, left, back, right, and three-quarter orthographic renders;
- surfaced front, left, back, right, and three-quarter orthographic renders;
- front and side 64 px silhouette renders;
- front and side 64/96 px surfaced game-look renders;
- one wireframe or topology inspection;
- vertex, face, triangle, object, material, texture, and disconnected-island
  metrics;
- stage-specific and cumulative API credits consumed plus account credits
  remaining.

The human review asks:

1. Does this unmistakably read as the approved Bentosaur identity?
2. Are the muzzle, cheeks, frill, rounded rim knobs, horns, hands, feet, belly,
   and tail correct from every required view?
3. Is the character prop-free, clothing-free, symmetrical, and neutral enough
   to become a reusable master?
4. Do the sage body, cream belly/horns/frill knobs, coral cheeks, eyes, and
   mouth match the approved identity?
5. Does the surfaced character still feel like Bentosaur under the intended
   toon/pixel render at game scale?
6. Is the complete visual candidate worth spending cleanup, rigging, and
   animation time on?

Only the user may approve a production master. The assistant may diagnose,
score, and recommend rejection, but cannot approve or advance it. The old
candidate-ID command is superseded because Visual Gate 01 selected only a
provisional form. The next valid authorization follows review of the complete
Visual Gate 02 package:

```text
APPROVE visual-gate-02-final-materials-face-and-mouth FOR RIGGING
```

A model that is riggable but visually wrong is rejected. A visually right
model may be repaired or manually rigged if automated rigging later fails.
Identity therefore gates technology, not the other way around.

Live Test 01 deliberately continued through rigging and animation after its
identity failure to prove the end-to-end plumbing. That was a one-time
experiment and is not the production precedent.

## Important discovery: Blender now has a first-party MCP

Blender 5.1.2 is installed locally. It already contains the official
**Blender Lab MCP 1.0.0** extension:

```text
~/Library/Application Support/Blender/5.1/extensions/user_default/mcp
```

Its manifest identifies Blender Lab as the maintainer and links to:

```text
https://www.blender.org/lab/mcp-server/
```

This changes the tool choice. Do not install the older community
`ahujasid/blender-mcp` for Bentosaur unless the first-party implementation
proves unable to perform a required task.

The official MCP provides:

- Blender file, data-block, object, library, and missing-file inspection;
- Blender Python API and manual lookup;
- viewport/window screenshots;
- object focus and workspace navigation;
- thumbnail and viewport rendering;
- arbitrary Blender Python execution;
- interactive Blender and background/CLI execution paths.

The Blender-side bridge and an official Blender MCPB package are both already
present. Claude has a pre-existing official v1.0.0 package with a known-good
`mcp==1.27.0` dependency. Codex is not yet connected.

Fresh official source currently resolves `mcp==2.0.0`, which removes an import
used by Blender MCP 1.0.0 and prevents startup. A source installation must pin a
known-good MCP SDK below 2, currently `mcp[cli]==1.29.0`, lock it, and run it
with the frozen lockfile. Do not run `uvx blender-mcp`: that PyPI name resolves
to the older community project, not Blender Lab's server.

A read-only end-to-end local validation succeeded on July 29, 2026:

1. Blender 5.1.2 launched in background mode with the official bridge on
   `127.0.0.1:9876`.
2. The pinned official stdio client completed its MCP handshake.
3. It exposed 26 tools.
4. `get_blendfile_summary_datablocks` returned the blank scene summary through
   the complete MCP-to-socket-to-Blender path.
5. The test Blender process and listener were stopped afterward.

No Blender preferences, Codex MCP configuration, or Bentosaur files were changed
by that validation.

## Security decision

The official Blender page explicitly warns that LLM-generated code executes
inside Blender without protection against deleting or transmitting data. The
installed `WeakSandboxForLLM` is not a security sandbox: it blocks a few
Blender-exit/preferences-reset operations, but it does not block Python file,
process, environment, or network access.

Therefore:

1. Bind the Blender bridge to `localhost` only.
2. Never expose port `9876` to the LAN or internet.
3. Disable add-on Auto Start; start the bridge only for the active task and
   stop it afterward.
4. Use MCP stdio only. Do not enable the official HTTP transport.
5. Keep unrelated `.blend` files closed and save a checkpoint before an MCP
   session.
6. Run production experiments in a dedicated macOS user or VM without access
   to unrelated credentials and private files when practical.
7. Keep API credentials out of Blender's environment, `.blend`, prompts,
   screenshots, job JSON, and the repository.
8. Prefer named, reviewed Blender scripts over large one-off generated Python
   payloads.
9. Save raw imports separately. Never let cleanup overwrite the downloaded
   source asset.
10. Require a human checkpoint before topology destruction, rig replacement,
   weight transfer, or final export.
11. Allow only one agent to control Blender at a time.

MCP is the conversational control surface. Versioned scripts and `.blend`
files are the reproducible production system.

## Tool roles

| Tool | Production role | Decision |
|---|---|---|
| Tripo CLI | Agent-friendly generation, previews, task history, processing, rigging, and downloads | Primary Tripo interface |
| Tripo API v3 | Exact pinned requests, seeds, batch automation, and provenance | Primary repeatable interface |
| Tripo MCP | Natural-language generation and Blender import | Defer; official but alpha and too narrow |
| Tripo Blender extension | Manual generation/import inside Blender | Optional convenience |
| Tripo Godot bridge | Browser-to-editor transfer | Optional; do not make it the source pipeline |
| Blender Lab MCP | Scene inspection, visual iteration, reviewed Blender operations | Use |
| Blender Python scripts | Deterministic validation, cleanup, render, and export recipes | Required |
| Blender `.blend` | Canonical mesh, materials, rig, shape keys, actions, cameras | Source of truth |
| Godot | Live 3D versus baked-sprite runtime proof | Final integration |

The Tripo Studio subscription and Tripo API have separate billing systems.
Studio credits must not be assumed to fund CLI/API calls.

## Why Tripo is a credible candidate

### P1

`P1-20260311` is designed for stylized and mobile-ready low-poly output:

- text, image, and multiview input;
- strict 50–20,000 face control;
- clean low-poly topology;
- bare-mesh output;
- deterministic `model_seed`;
- approximately ten seconds for untextured geometry according to Tripo.

### H3.1

`v3.1-20260211` is the fidelity fallback:

- multiview reconstruction;
- quad output;
- Smart Low Poly;
- stronger geometry detail when P1 removes the cheeks, frill, feet, or horns
  that make the character lovable.

### Rig and motion

Tripo v3 exposes:

- free rig checking;
- biped and several non-humanoid rig families;
- native or Mixamo bone specifications;
- GLB and FBX output;
- animation retargeting.

Bentosaur is a nonstandard upright biped with a large head, tiny arms, short
legs, thick tail, frill, and horns. A `biped` result is only a starting point.
The tail/frill bones, weights, face system, and service acting remain Blender
work.

## The test subject

Use the canonical upright Triceratops identity, not a generic realistic
dinosaur.

Do not send the existing 64 px sprite directly to 3D generation. Pixel outlines
can become false geometry, and the sprite does not contain enough information
about the back and hidden surfaces.

First author a clean 1024 px turnaround:

1. front;
2. left;
3. back;
4. right.

All four are orthographic, neutral, flat-lit, and show the same proportions and
A-pose.

### Turnaround prompt

```text
Canonical Bentosaur baby triceratops turnaround model sheet showing the
exact same single character in four separate orthographic views: front,
left, back and right. Upright biped. Oversized round head and broad
circular frill, three wide blunt cream horns, short rounded muzzle,
plump pear-shaped torso, tiny arms clearly separated from the body in a
neutral A-pose, short stout hind legs, broad flat feet and one thick
tapering tail. Cute chibi proportions but unmistakably a dinosaur, not
a human in a costume. Neutral closed mouth. Smooth simple toy-like
forms. Symmetrical construction and identical proportions in every
view. Flat diffuse colours, minimal shading, plain light-grey
background. No perspective, no props, no clothing, no scenery, no
ground plane and no cast shadow.
```

### Negative constraints

```text
quadruped, realistic dinosaur, human anatomy, long limbs, muscular body,
open mouth, teeth, realistic scales, fur, dramatic lighting,
perspective, fused arms, tail fused to legs, thin horns, accessories,
pedestal
```

### Turnaround rejection gate

Reject the reference set before any paid 3D request when:

- any view changes head/body proportion;
- horn, frill-rim, cheek, hand, foot, or tail placement disagrees;
- an arm or tail fuses into the torso;
- a forelimb bears weight;
- the left/right images are independently redesigned rather than rotations of
  one identity;
- lighting, perspective, expression, or outline changes obscure form.

## Phase 1: bare-geometry bake-off

Generate two candidates from the same four views. Use no generated textures.
This reveals whether the character-defining features are true geometry instead
of an attractive texture painted over a generic blob.

### Candidate A — P1, 5,000-face target

```json
{
  "inputs": [
    {"front": "<front_file_token>"},
    {"left": "<left_file_token>"},
    {"back": "<back_file_token>"},
    {"right": "<right_file_token>"}
  ],
  "model": "P1-20260311",
  "model_seed": 28102026,
  "face_limit": 5000,
  "texture": false,
  "pbr": false,
  "export_uv": false
}
```

### Candidate B — H3.1 plus Smart Low Poly

```json
{
  "inputs": [
    {"front": "<front_file_token>"},
    {"left": "<left_file_token>"},
    {"back": "<back_file_token>"},
    {"right": "<right_file_token>"}
  ],
  "model": "v3.1-20260211",
  "model_seed": 28102026,
  "face_limit": 5000,
  "smart_low_poly": true,
  "texture": false,
  "pbr": false,
  "export_uv": false
}
```

Keep:

- every input image;
- model name and snapshot;
- seed and full payload;
- task JSON and credit receipt;
- preview image;
- raw GLB;
- a dated copy/link of the applicable terms.

Do not continue both branches. Review the rotating model, wireframe, front
camera, side camera, and 64 px silhouette, then choose one winner.

Stop here and obtain the Hard Gate 0 approval. Do not run even a free rig check
until one visual candidate is explicitly approved; keeping all rig-related work
behind the same gate makes the process and credit ledger unambiguous.

## Character appearance scope for the first production proof

The first candidate is one unclothed canonical dinosaur:

- no clothing mesh;
- no apron;
- no outfit variants;
- no clothing sockets;
- no outfit inventory or wardrobe UI;
- no held object;
- no environment fused into the asset.

Its sage body, cream belly/horns/frill knobs, coral cheeks, eyes, mouth, and
other permanent markings are part of the character's materials and texture.
They are not a swappable outfit.

Accessories are deferred. If added later, they remain separate assets attached
through a deliberately approved small socket set. Do not build that system
during this validation.

## Phase 2 — blocked until Visual Gate 02 approval: rig the approved final-look master

Do not run this phase yet. After Mau approves Visual Gate 02, run the free rig
check first. If it approves a biped rig, test:

```json
{
  "input": "<winning_generation_task_id>",
  "model": "v2.5-20260210",
  "rig_type": "biped",
  "spec": "tripo",
  "out_format": "glb"
}
```

Use Tripo-native naming for the first test. A Mixamo humanoid skeleton is useful
for generic libraries but is more likely to omit or simplify dinosaur-specific
tail behavior.

The rig must be rejected or extended in Blender if it lacks:

- a stable root and pelvis;
- independently useful arms/hands;
- sensible short-leg deformation;
- a tail chain or a clean place to add one;
- weights that do not pull the frill, horns, cheeks, or belly incorrectly.

Test only disposable diagnostic motions:

```json
{
  "input": "<rig_task_id>",
  "animations": [
    "preset:idle",
    "preset:walk",
    "preset:turn"
  ],
  "out_format": "glb",
  "bake_animation": true,
  "animate_in_place": true
}
```

Do not let a larger generic preset library dictate the production rig.
`order`, `receive`, `delight`, `chomp`, tray holding, page turning, cooking, and
umbrella acting are authored Bentosaur actions.

## Phase 3: Blender source-of-truth pass

Create this non-destructive file chain:

```text
raw/
  p1/model.glb
  h31/model.glb
  winner-rigged.glb

blender/
  00_import.blend
  10_geometry-clean.blend
  20_character-master.blend
  30_animation-test.blend

exports/
  bentosaur_triceratops_master_v001.glb
  sprite-tests/
  reports/
```

### Deterministic validation

The Blender scripts produce a report for:

- object, mesh, material, armature, and action names;
- face/triangle count;
- loose and non-manifold geometry;
- duplicate vertices;
- zero-area faces;
- normals and negative scale;
- disconnected or suspicious mesh islands;
- UV/material count;
- armature, bone, and vertex-group inventory;
- unweighted and multiply weighted vertices;
- animation duration and root displacement;
- GLB export warnings.

### Character correction

Human-reviewed cleanup may:

- correct horn spacing and taper;
- restore cheek and frill-rim volume;
- shorten the muzzle;
- separate tiny hands from the belly;
- widen and flatten the feet;
- repair the tail attachment;
- add clean loops for shoulders, hips, mouth, and tail;
- add tail and frill bones;
- repaint weights;
- add front/side corrective shape keys.

If this takes more than roughly two competent hours, record why. If most of the
model must be rebuilt, Tripo has failed as a production character generator even
if it remains useful for blocking.

### Bentosaur face and palette

Do not keep an AI-painted fixed face.

Create:

- neutral;
- blink;
- order/speak;
- wait;
- delight;
- disappointment;
- chomp.

Use small opaque face planes, discrete expression meshes, or a tiny
nearest-filtered atlas. Use shape keys only for useful cheek, lid, jaw, and
mouth-volume changes.

Replace generated materials with the declared Bentosaur palette:

- flat base colours or vertex colours;
- two to four hard light bands;
- specular disabled;
- no generated normal/metallic realism;
- one deterministic outline path;
- fixed orthographic front and side cameras.

### Modular sockets

Add these stable sockets/bones:

```text
socket_hand_l
socket_hand_r
socket_tray
socket_mouth_bite
socket_head_hat
socket_back
socket_umbrella
socket_apron_chest
socket_apron_waist_l
socket_apron_waist_r
```

The umbrella, apron, tray, bowl, and bento are separate reusable assets, not
baked into each customer mesh.

The character master owns species-defining anatomy, palette slots, armature,
weights, corrective shapes, face system, prop-free actions, and sockets. It
does not own held props, clothing, accessories, food, environment, weather, or
VFX. A deformable apron may share the compatible armature but remains a
separate mesh and export.

## Phase 4: one master, three proofs

From `20_character-master.blend`, produce:

1. **Pure 2D control** — current approved pixel pipeline.
2. **Baked 3D** — 64/96 px orthographic sprite sheets.
3. **Live 3D** — the same GLB in Bentosaur's transparent Godot character
   `SubViewport`.

### Baked-sprite factory amendment — July 29, 2026

The full video, description, linked Blender file, linked render script, and
companion resources from KitagawaGameDev's Blender pixel-art tutorial have now
been audited. The method materially strengthens the baked branch:

- native-resolution rendering with pixel filter `0`;
- fixed orthographic camera profiles;
- `Standard` view transform and dither `0`;
- flat palette materials or vertex colors;
- stepped 8–12 fps animation;
- deterministic silhouette outline at target resolution;
- optional camera-space normal pass;
- mandatory Aseprite cleanup and a Godot JSON manifest.

The linked starter `.blend` and Gist have no verified reuse license, so they are
learning references only. Bentosaur will create its own Blender 5.1.2 template
and renderer.

Do not batch eight directions by default. Produce only:

- front and optional authored three-quarter views for the counter;
- left/right side views for street walkers;
- controlled front/three-quarter portraits for the album.

The static proof runs before animation. It renders native 96/64 px counter
stills and native 48/32 px walker stills. A separate simplified silhouette LOD
is expected for tiny walkers. Normal maps are a later optional test for the
foreground customer only.

Full evidence and the exact gates are in
`3d-to-2d-pixel-sprite-factory-research-v1.md`; the machine-readable job is
`art/jobs/bentosaur-sprite-factory-proof-v1.json`.

Test:

- side walk;
- front stall idle;
- order;
- receive;
- delight;
- chomp;
- one apron;
- one umbrella;
- one bento tray.

The background walkers use baked side renders even if the counter customer
passes as live 3D.

## Acceptance gate

Tripo advances only if:

1. The winner is unmistakably the approved Bentosaur identity from front and
   side.
2. Horns, frill, cheeks, hands, feet, and tail are real readable form.
3. Arms, legs, horns, and tail are not fused.
4. Runtime geometry is near or below 5,000 faces without losing the silhouette.
5. The diagnostic walk has no severe foot slide or limb collapse.
6. Tail/frill weights remain stable.
7. Eyes, horns, hands, and feet remain readable at a 64 px orthographic render.
8. The first competent cleanup takes no more than about two hours.
9. Baked motion has no unacceptable pixel shimmer.
10. Live motion passes the existing mobile GPU and emotional-readability gate.
11. A palette skin and apron reuse the same model.
12. The complete run can be repeated from saved inputs, payloads, scripts, and
    pinned versions.

Decision routing:

- **P1 passes:** prefer P1 for the cast.
- **P1 loses the face but H3.1 passes:** use H3.1 plus controlled retopology.
- **Live fails, baked passes:** retain Blender masters as the sprite factory.
- **Rig fails, mesh passes:** rig manually in Blender; Tripo may still be the
  base-mesh supplier.
- **Both meshes require reconstruction:** stop using Tripo for production
  characters.
- **Both lose the heart:** return to directional 2D kits.

## Cost

Tripo API currently prices 100 credits at USD 1.

| Operation | Credits |
|---|---:|
| P1 multiview, no texture | 40 |
| H3.1 multiview + Smart Low Poly, no texture | 30 |
| Rig check | 0 |
| One auto-rig | 25 |
| Idle, walk, and turn | 30 |
| **Controlled bake-off** | **125 ≈ USD 1.25** |

Allow another small buffer for retries or conversion. The cost is not the
production risk; cleanup time and loss of art direction are.

Tripo Studio currently lists:

- Free: 200 monthly credits, public CC BY 4.0 models;
- Pro: USD 19.90 month-to-month, or USD 167.16 annually at the displayed annual
  discount; 3,000 monthly Studio credits, multiview, Smart Mesh, private models,
  and commercial use.

The API is separately funded and currently advertises 300 introductory credits
for two weeks. Purchased API credits do not expire according to its FAQ.

## Rights and privacy rule

Do not upload the canonical private Bentosaur turnaround as a free user.

The current Tripo terms give broad rights over free-user inputs and outputs.
For paid users, the terms generally grant the user broad use, modification,
licensing, transfer, and monetization rights, and state that paid-user inputs
and outputs will not be used to train, validate, test, or improve Tripo's AI.
They do not guarantee output uniqueness, exclusivity, or non-infringement.

Production rule:

1. Use a generic non-secret dinosaur for free plumbing tests.
2. Establish paid status before the canonical turnaround is uploaded.
3. Save the exact terms/date, input rights, task provenance, and purchase
   record.
4. Make meaningful human-authored mesh, topology, material, rig, face, and
   animation changes.
5. Keep an internal asset ledger linking the source references, raw model,
   cleaned `.blend`, and exported GLB.

This is production hygiene, not legal advice.

## Local readiness

Confirmed:

- Blender 5.1.2 installed;
- official Blender Lab MCP add-on 1.0.0 installed;
- official Blender MCPB v1.0.0 already present in Claude with
  `mcp==1.27.0`;
- a user Blender GUI process was observed listening on
  `127.0.0.1:9876` during final verification and was deliberately left
  untouched;
- `uv` and `uvx` installed;
- Node and npm meet Tripo CLI requirements;
- official Tripo CLI 0.2.0 installed;
- Tripo browser login completed with a local mode-0600 profile;
- API balance funded and verified;
- paid-user status reported by the user;
- one prop-free P1 model generated, rig-checked, rigged, animated, imported,
  measured, and rendered in Blender;
- canonical 1024 px turnaround created;
- P1 versus H3.1 canonical multiview bake-off completed;
- reusable Blender inspection and animation-preview scripts created.

Not yet done:

- disable the Blender add-on's Auto Start preference after confirming the
  current GUI session may be safely interrupted;
- Blender Lab MCP server pinned and connected to Codex;
- Visual Gate 02 canonical material, face, and mouth pass;
- user approval of the final-look package before rigging;
- canonical socket, rig, deformation, and custom-animation pass;
- Godot live-versus-baked proof.

## Exact independent Codex MCP setup

Perform this only after approving the MCP security boundary. Keep the GPL MCP
tool outside the game repository.

```bash
mkdir -p /Users/mauvsantos/Workspace/tools
git clone --branch v1.0.0 --depth 1 \
  https://projects.blender.org/lab/blender_mcp.git \
  /Users/mauvsantos/Workspace/tools/blender_mcp_official

cd /Users/mauvsantos/Workspace/tools/blender_mcp_official/mcp
uv add 'mcp[cli]==1.29.0'
uv run --frozen blender-mcp --help
```

Then register the official stdio server with Codex:

```bash
codex mcp add blender-official \
  --env BLENDER_MCP_HOST=127.0.0.1 \
  --env BLENDER_MCP_PORT=9876 \
  --env 'BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender' \
  -- /opt/homebrew/bin/uv \
  --directory /Users/mauvsantos/Workspace/tools/blender_mcp_official/mcp \
  run --frozen blender-mcp
```

Do not reuse Claude's private MCPB executable for production. It is a useful
known-good reference, but coupling Bentosaur to Claude's extension lifecycle
would make the pipeline fragile.

## Next execution

The smallest meaningful next session is:

1. preserve the user-approved turnaround and untouched P1 source GLB;
2. use P1 only as the provisional geometry/lookdev base;
3. create the mouth-expression addendum and art-directed material system;
4. weld/clean or retopologize P1 without changing the accepted form;
5. rebuild the muzzle with deformation loops, a real mouth cavity, and tongue;
6. return neutral, open-delight, three-quarter, mouth-interior, mobile-scale,
   and rainy-stall-camera evidence for final appearance approval;
7. only after that approval, create the production skeleton, bind, weight, and
   return deformation evidence;
8. only after the deformation gate, author the first animation clips and
   compare live Godot 3D against sprite sheets baked from the same master.

Do not generate the cast before this gate.

## Sources

- Blender Lab MCP:
  https://www.blender.org/lab/mcp-server/
- Blender Lab MCP source:
  https://projects.blender.org/lab/blender_mcp
- Tripo CLI:
  https://developers.tripo3d.ai/en/docs/cli
- Tripo official MCP:
  https://github.com/VAST-AI-Research/tripo-mcp
- Tripo Blender extension:
  https://github.com/VAST-AI-Research/tripo-3d-for-blender
- Tripo Godot bridge:
  https://www.tripo3d.ai/blog/tripo-dcc-bridge-for-godot
- Tripo P1:
  https://developers.tripo3d.ai/en/models/p1
- Tripo H3.1:
  https://developers.tripo3d.ai/en/models/v3-1
- Tripo multiview P endpoint:
  https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/p
- Tripo rigging:
  https://developers.tripo3d.ai/en/docs/animations-rig
- Tripo animation retargeting:
  https://developers.tripo3d.ai/en/docs/animations-retarget
- Tripo API pricing:
  https://docs.tripo3d.ai/get-started/pricing.html
- Tripo Studio pricing:
  https://www.tripo3d.ai/pricing
- Tripo terms:
  https://www.tripo3d.ai/terms
