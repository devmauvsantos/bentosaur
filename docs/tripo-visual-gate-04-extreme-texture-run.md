# Visual Gate 04 — H3.1 Extreme Texture Run

**Date:** 2026-07-29  
**Approval owner:** Mau  
**Status:** Awaiting Mau's visual decision  
**Rigging / animation:** Not authorized

## Outcome

The single authorized Tripo Extreme/8K texture task succeeded on the frozen
H3.1 Detailed geometry. It consumed exactly 30 Tripo credits, preserved the
surface geometry exactly, and produced a coherent Bentosaur palette and face
across six views.

This is a visual-master and look-approval candidate. It is not a mobile-ready
asset and it is not automatically approved.

## Paid run receipt

- Source task: `f23a7b24-a3d5-433c-a404-3d9d2d8c0787`
- Texture task: `26811821-3e6d-4b62-a695-679275c04f60`
- Endpoint: `POST https://openapi.tripo3d.ai/v3/models/texture`
- Texture model: `v3.0-20250812`
- Quality: `extreme` / 8K
- Alignment: `original_image`
- PBR: `true`
- Bake advanced effects into base color: `false`
- Texture seed: `29072026`
- Submission retries: `0`
- Task submissions: exactly `1`
- Created: `2026-07-29T18:22:38.676514Z`
- Completed: `2026-07-29T18:27:32.771060Z`
- Credits consumed: `30`
- Balance: `4,795 → 4,765`
- Frozen balance after completion: `0`
- Cumulative H3.1 hero source + texture: `70` credits

Official references:

- [Tripo Texture API](https://developers.tripo3d.ai/en/docs/models-texture)
- [Tripo API pricing](https://developers.tripo3d.ai/en/pricing)

## One-shot safety policy

The exact four images used to create the H3.1 source were re-supplied in the
required `[front, left, back, right]` order. They were not redrawn, de-lit, or
re-uploaded. The original accepted Tripo file tokens were reused.

The normal CLI task submission path was not used because it can retry transient
POST failures and Tripo exposes no idempotency key. A dedicated wrapper locally
validated the authorization, payload, four unique reference tokens, fixed seed,
and 30-credit cap, then made one request with `maxRetries: 0`.

Files:

- Payload: `art/jobs/tripo-visual-gate-04-h31-extreme-texture-payload.json`
- Run manifest: `art/jobs/tripo-visual-gate-04-h31-extreme-texture.json`
- Submission wrapper: `tools/tripo/submit_single_texture_task.mjs`

## Artifact integrity

- Textured GLB: `85,259,072` bytes
- Textured GLB SHA-256:
  `40de6b43b0dc0313e084005b711cb549dfe6dfceeebe45c6275761c99b96dc79`
- Locked source GLB SHA-256:
  `4b9ad1cc5562986ff587718c0dbd1f00a5fdf99b33de3c905c3cc0e87ce69607`
- Triangle count: `1,974,918` in both files
- Indexed surface position mismatches: `0`
- Maximum position delta: `0.0`
- Bounds: exactly equal
- Added vertices: `23,189`, all verified UV-seam splits

The texture task did not replace, deform, or simplify the approved H3.1 shape.

## Material payload

- One PBR material
- Base color: `8192 × 8192`, RGB JPEG, sRGB
- Normal: `4096 × 4096`, RGB JPEG, Non-Color
- Metallic/roughness: `4096 × 4096`, RGB PNG, Non-Color
- UVs: finite and within `[0,1]`
- No armature, skin, action, or animation

Production notes:

- The geometry and maps are far beyond the eventual mobile runtime budget.
- The source material is double-sided.
- The normal is lossy JPEG and the GLB has no stored tangent attribute.
- The metallic channel contains small nonzero values; the organic production
  material should force metallic to zero.
- Retopology, LODs, texture downsizing/compression, tangent validation, and
  single-sided material review are mandatory after appearance approval.

## Approval evidence

The evaluator never edits geometry, the face, or the mouth. It creates deep
duplicates in a disposable Blender process and changes only evidence materials.
It does not save or pack a `.blend`.

Evaluator:
`tools/blender/evaluate_textured_hero_candidate.py`

### Base-color truth

The actual linked 8K base-color image is connected directly to Emission using
the Standard view transform. There are no lights, normal/ORM maps, or color
corrections.

- Six views:
  `art/candidates/tripo/visual-gate-04/h31-extreme-texture/evaluation/boards/vg04_basecolor_six_view.png`
- Feature close-ups:
  `art/candidates/tripo/visual-gate-04/h31-extreme-texture/evaluation/boards/vg04_basecolor_feature_closeups.png`
- Canonical comparison:
  `art/candidates/tripo/visual-gate-04/h31-extreme-texture/evaluation/boards/vg04_basecolor_reference_comparison.png`

### Soft-matte target

The same unchanged base color is used with metallic `0`, roughness `0.82`,
specular IOR level `0.18`, soft neutral lights, and AgX. Generated normal and
ORM maps are disconnected so they cannot hide projection problems or make the
skin noisy/plastic.

- Six views:
  `art/candidates/tripo/visual-gate-04/h31-extreme-texture/evaluation/boards/vg04_matte_six_view.png`
- Feature close-ups:
  `art/candidates/tripo/visual-gate-04/h31-extreme-texture/evaluation/boards/vg04_matte_feature_closeups.png`
- Canonical comparison:
  `art/candidates/tripo/visual-gate-04/h31-extreme-texture/evaluation/boards/vg04_matte_reference_comparison.png`

### Notion approval package

The four most useful boards are embedded on
[Visual Gate 04 — H3.1 Extreme Texture Approval](https://app.notion.com/p/3acbcf1d0403812db3c9fc7818401dbe).
Notion review copies are quality-90 JPEGs below the free-workspace 5 MB upload
limit. The canonical PNG evidence above remains untouched.

- `evaluation/notion-review/vg04_basecolor_six_view.jpg`
- `evaluation/notion-review/vg04_matte_six_view.jpg`
- `evaluation/notion-review/vg04_basecolor_feature_closeups.jpg`
- `evaluation/notion-review/vg04_basecolor_reference_comparison.jpg`

## Honest visual findings

What succeeded:

- The character reads as the same Bentosaur from all required angles.
- Sage, cream, coral, and dark facial regions land coherently.
- The eyes are single and readable; there is no doubled-eye texture.
- The three horns, frill knobs, belly, hands, toes, and tail accents remain
  legible.
- No prop, clothing, accessory, base, or scenery is fused to the character.

What still needs authored Blender work if Mau approves the look:

- Remove subtle sage albedo mottling.
- Remove the baked dark transition above the belly and under the chin.
- Clean minor projection transitions around the arms and belly.
- Rebuild semantic materials from the approved palette rather than shipping the
  projected atlas unchanged.
- Build the neutral lip seal, real mouth cavity, separate tongue, jaw-ready
  topology, and delighted open smile on the same production master.

## Decision gate

Mau should decide one of:

1. **Approve the character/look direction.** Stop all Tripo generation and use
   this as the visual target for clean Blender retopology, materials, and mouth.
2. **Approve with explicit changes.** Record the changes, then perform them in
   Blender without rerolling the character.
3. **Reject the look direction.** Stop before retopology, rigging, or animation.

This run does not authorize another Tripo task. It does not authorize rigging,
skinning, deformation, or animation.
