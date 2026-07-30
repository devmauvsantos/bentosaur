# Bentosaur AI Art Pipeline — Live Test 01

**Date:** July 28, 2026  
**Status:** Complete — superseded; all character candidates rejected for incorrect quadruped anatomy  
**Scope:** One 64×64 Triceratops identity anchor and one four-frame idle-loop probe  
**Providers:** PixelLab MCP and Retro Diffusion MCP

## Goal

Prove that the “one prompt” workflow can create reproducible Bentosaur pixel-art candidates while preserving:

- character identity;
- front-facing gameplay perspective;
- transparent output;
- exact source dimensions;
- the canonical 24-color palette;
- animation anatomy and loop closure;
- provider/model/prompt/seed/cost provenance.

This test is deliberately narrow. None of its outputs are approved shipping art yet.

## Canonical anatomy correction

The user clarified after this test that Bentosaur's dinosaurs are **cute upright bipeds**, not naturalistic quadrupeds. They stand and walk on two hind legs, use their short forelimbs as hands, elevate the torso from the hips, and retain a visible balancing tail.

That correction invalidates the apparent character success below. Candidate 07 and the entire `anchor-pro-crop-01` batch are now rejected as identity anchors because their compact four-footed body plan violates the game silhouette, even though their faces, palette direction, and rendering are appealing. The derived idle animation is also rejected as a production lineage.

The canonical machine-readable rule is now `art/character-anatomy.json`. Any full-body candidate is automatically rejected when a forelimb bears weight, the torso reads horizontally, the sprite presents four walking feet, or the side/three-quarter silhouette loses its balancing tail. Portrait/emote crops may omit the lower body because they are not locomotion assets.

## Security and configuration

Both MCP servers are configured project-locally through Claude Code:

- `pixellab` → `https://api.pixellab.ai/mcp`
- `retro-diffusion` → `https://mcp.retrodiffusion.ai/mcp`

Credentials remain in the user's Claude configuration. They are never stored in this project, printed by the helper scripts, embedded in a job manifest, or sent to the game runtime.

The local helpers read the configured server URL and headers at execution time:

- `tools/mcp_probe.mjs` lists live tool schemas.
- `tools/mcp_call.mjs` executes a named tool from a JSON request.
- `tools/validate_sprite.mjs` checks dimensions, alpha, palette membership, color count, visible bounds, and padding.

Aseprite `1.3.18.1-arm64` is installed with the PixelLab extension enabled. Its current extension emits four `handle-pose.lua` `dlg` warnings during headless CLI startup, although Aseprite still exits successfully with code 0. GUI generation is unaffected in this test. Until the extension fixes its headless guard, automated exports must judge success from the process exit code and output hashes rather than requiring empty stderr; if the warnings begin affecting exports, disable the extension for the export run instead of weakening asset QA.

## Canonical inputs

- Gameplay concept: `art/references/bentosaur-gameplay-concept.png`
- Character-only crop: `art/references/bentosaur-character-reference.png`
- Palette image: `art/palettes/bentosaur-warm-v1.png`
- Palette data: `art/palettes/bentosaur-warm-v1.json`
- Required output cell: `64×64`
- Required pivot: `[32, 58]`
- Required alpha mode: binary
- Required maximum visible colors: 24

## Test results

### PixelLab Pixflux baseline

- Operation: `create_image_pixflux`
- Provider job: `395954ca-b671-4ec5-a773-b02cf918a7d1`
- Seed: `184722`
- Cost: 1 subscription generation
- Request: `art/jobs/pixellab-bentosaur-anchor-01.json`
- Output: `art/candidates/pixellab/anchor-01/get_image-00.png`

Technical result:

- 64×64: pass
- binary alpha: pass
- forced 24-color palette membership: pass
- visible colors: 13
- visible bounds: 44×55 at `(11, 4)`

Semantic result: fail.

The image was cute and technically valid, but it ignored the requested south/front direction and became a generic side-facing baby dinosaur. Cheap text-only generation is useful for exploratory props, not for the canonical character identity.

### PixelLab Pro with full gameplay composition

- Operation: `create_image_pro`
- Provider job: `2a0d48a9-1145-41b1-949e-5befcf733b82`
- Seed: `184723`
- Cost: 20 subscription generations
- Candidates: 16
- Request: `art/jobs/pixellab-bentosaur-anchor-pro-01.json`
- Contact sheet: `art/candidates/pixellab/anchor-pro-01/contact-sheet.png`

Structural/semantic result: partial success.

The batch produced readable front-facing Triceratops characters with stable anatomy. However, the full composition's dominant counter/roof colors overwhelmed the local character palette, yielding red/brown dinosaurs instead of the approved sage green.

**Rule learned:** never use a complete gameplay composition as the only character style reference. A style reference carries local content and global color statistics, not merely an abstract art direction.

### PixelLab Pro with tight character crop

- Operation: `create_image_pro`
- Provider job: `835c5fc2-6ac0-4190-b0f3-1100fbd04182`
- Seed: `184724`
- Cost: 20 subscription generations
- Candidates: 16
- Request: `art/jobs/pixellab-bentosaur-anchor-pro-crop-01.json`
- Contact sheet: `art/candidates/pixellab/anchor-pro-crop-01/contact-sheet.png`
- Animation probe candidate: index 07

Visual-identity result: partial success. Canonical anatomy result: fail.

The tight crop preserved the character's:

- sage-green frill/body;
- cream horns and highlights;
- coral blush;
- closed joyful eyes;
- large rounded silhouette;
- cozy, hand-authored personality.

Technical normalization is still required:

- candidate 07 uses 37 visible colors;
- Pro did not constrain it to the canonical palette;
- the opaque silhouette touches all four edges of the 64×64 canvas.
- the character is a compact quadruped rather than the required upright biped.

**Rules learned:**

1. Use a tightly cropped identity reference for character generation, but never assume a face crop communicates the full-body anatomy.
2. Generate future character art on an internal canvas smaller than the final cell, then place it into an untrimmed 64×64 cell at the fixed pivot.
3. PixelLab Pro is the identity/candidate generator, not the palette compiler.
4. Palette quantization, padding, pivots, tags, and final export belong to Aseprite/local tooling.
5. A full-body anatomy reference and explicit biped rejection language are mandatory.

### PixelLab loose-image idle animation

- Operation: `animate_image`
- Provider job: `b8c2918c-1952-4cbf-a3d8-d50a34b5eb8d`
- Seed: `184725`
- Cost: 1 subscription generation
- Source: cropped-reference candidate 07
- Request: `art/jobs/pixellab-bentosaur-idle-loose-01.json`
- Frames: 5 returned: the source frame, three generated in-betweens, and an exact duplicate of the source as the closing frame
- Contact sheet: `art/candidates/pixellab/idle-loose-01/contact-sheet.png`
- Preview: `art/candidates/pixellab/idle-loose-01/idle-4-frame-preview.gif`

Loop-closure result: pass.

The first and fifth frames are byte-identical. Supplying the same source image as both the first and final target is therefore a reliable way to request exact closure; the compiler can remove the duplicated closing frame and retain a four-frame loop.

Identity/anatomy result: fail for shipping.

The motion idea is cute and readable, but the in-betweens redraw the body rather than deforming it conservatively. The torso shrinks, and the face, frill, forearms, feet, and silhouette drift between frames. Visible colors also vary from 29 to 45, and several frames touch the canvas edges. This is useful as motion reference or a rough key-pose proposal, not as a canonical game animation.

**Rules learned:**

1. Repeating the first frame as the final target is a dependable loop-closure technique.
2. `animate_image` is appropriate for exploration, VFX, and non-critical props; it is not yet identity-stable enough for Bentosaur's hero idle.
3. Normalize the approved anchor before animation so palette, padding, baseline, and pivot become hard constraints.
4. Prefer persistent object animation or human-authored key poses with AI-assisted in-betweens for the next dinosaur test.

PixelLab balance after all four calls: 1,958 of 2,000 subscription generations remain; 42 were used.

### PixelLab persistent-object route

PixelLab's live help recommends this route for an arbitrary dinosaur that has no built-in quadruped template:

1. create an eight-direction object from the approved isolated reference;
2. retain the returned `object_id`;
3. animate only `south` for the first comparison;
4. request four frames and keep the first frame;
5. score identity stability, foot drift, palette drift, and loop seam against the loose-image result.

This is a hypothesis, not a proven production path. The live schema also warns that identity transfer for character-like subjects is not guaranteed in the object workflow. Creating the persistent object costs another 20–40 subscription generations, so it should happen only after the human selects the canonical anchor. If it fails, use authored start/end key poses and Aseprite cleanup rather than repeatedly regenerating.

### Retro Diffusion RD Pro comparison

- Operation: `create_inference`
- Style: `rd_pro__default`
- Seed: `184723`
- Estimated/actual cost: $0.18
- Reference count: 1
- Forced palette: yes
- Request: `art/jobs/retro-bentosaur-anchor-pro-01.json`

Generation completed, but the synchronous MCP response reported one base64 image while returning neither the image payload nor a hosted URL. The $0.18 charge succeeded; artifact transport did not.

**Operational rule:** treat this result as a provider-transport failure. Do not blindly resubmit a charged job. For the next Retro test, use an async job and verify that `get_inference_job` returns a hosted URL before making Retro part of the automated pipeline.

Current Retro image balance after the call: $0.32.

## Test verdict

| Question | Result |
|---|---|
| Can AI generate a recognizable Bentosaur face/style candidate from the concept? | Yes — PixelLab Pro with a tight character crop |
| Did Test 01 produce the canonical Bentosaur body plan? | No — every candidate is quadrupedal and rejected |
| Does a full-scene reference preserve the green identity? | No — global scene colors dominate |
| Does the cheaper forced-palette model follow the character view closely enough? | No — technically valid, semantically wrong |
| Does PixelLab Pro emit shipping-ready palette/padding? | No — local normalization is required |
| Can the loose-image animator close a loop exactly? | Yes — use the same image as first and final target |
| Is the loose-image result identity-stable enough to ship? | No — anatomy and silhouette drift |
| Did the Retro Diffusion synchronous MCP test return a usable artifact? | No — generation was charged but the artifact was not transported |

The corrected route is:

```text
full-body biped anatomy reference + tight identity crop
  → PixelLab Pro candidate batch
  → automatic upright-biped anatomy gate
  → human anchor selection
  → local palette/padding/pivot normalization
  → persistent-object vs authored-key-pose animation bake-off
  → Aseprite repair and tagging
  → deterministic QA
  → Godot preview
```

## Provider-specific prompting contract

### PixelLab still generation

Appearance prompt:

- describe identity, silhouette, materials, expression, and exclusions;
- put view, direction, outline, shading, detail, size, transparency, seed, and palette in structured fields;
- keep a stable seed while changing only one variable;
- use Pixflux for cheap forced-palette drafts;
- use Pro with a tight style/identity crop for canonical anchors;
- never mix an environmental composition into a character reference set unless it is explicitly labelled only as environment/style.

Reference hierarchy:

1. approved transparent identity sprite;
2. tightly cropped character reference;
3. isolated palette/outline reference;
4. full gameplay composition only as a secondary mood reference.

Do not describe environment or behavior in a character appearance prompt.

### PixelLab animation

Motion prompt:

- describe movement only;
- explicitly lock feet/root when required;
- request one readable action;
- keep camera, appearance, clothing, palette, lighting, and environment out of the motion prompt;
- use the approved first frame;
- use the same image as the final frame for a closed idle loop;
- use a distinct authored final pose for non-looping `look` and `chomp`;
- generate one clip at a time;
- retain provider seed and job ID.

Exact v1 clip strategy:

- `idle`: first frame = final frame; four generated frames; compile the best four-frame closed sequence.
- `walk`: use character/object animation if the identity anchor survives the character workflow; otherwise animate the loose approved sprite and manually enforce feet.
- `look`: approved neutral start plus authored look target.
- `chomp`: approved neutral start plus authored impact target.

### Retro Diffusion

- Call `list_available_styles`; never guess style dimensions or capabilities.
- Call `estimate_inference_cost` before every paid request.
- Describe the subject only; never add “pixel art,” “8-bit,” or “pixelated.”
- Choose the style through `prompt_style`.
- Reuse a fixed seed for controlled changes.
- Use `reference_images` for identity and `input_palette` for palette enforcement.
- Use `remove_bg` rather than prompting for transparency.
- Use async jobs for animation and batches.
- Poll the existing task ID after a timeout; never resubmit blindly.

## Intended production flow

```text
one creative prompt
  → schema-valid job manifest
  → reference and palette hash check
  → free cost estimate where available
  → provider generation
  → immediate artifact download
  → local deterministic QA
  → semantic/contact-sheet review
  → palette and padding normalization
  → Aseprite assembly, pivots, and tags
  → loop QA and Godot preview
  → human approval
  → approved export
```

Provider output never writes directly to `approved/` or the shipping atlas.

## Next gate

Live Test 02 is recorded in `docs/ai-art-pipeline-test-02-biped.md`. Its labelled multi-reference batch passed the upright-biped anatomy gate for all 16 candidates.

1. Human-select the upright-biped anchor; Test 02 recommends candidate 12.
2. Recompose the selected sprite inside the 64×64 cell with safe padding.
3. Quantize it to the 24-color palette and align it to pivot `[32, 58]`.
4. Run one controlled persistent-object animation test against one authored-key-pose test.
5. Assemble the winner into an `.aseprite` source with an `idle` tag.
6. Retest Retro through its asynchronous artifact path only after deciding whether the remaining $0.32 is worth spending.
