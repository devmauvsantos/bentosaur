# Tripo Hero Character — Full-Quality Run Research v1

Status: research complete; paid execution paused  
Date: 2026-07-29  
Decision owner: Mau  
Current Tripo balance: 4,795 credits; frozen: 0  
Current source task: `f23a7b24-a3d5-433c-a404-3d9d2d8c0787`

## Decision

Do **not** generate another character mesh.

The best next paid operation is one standalone **8K Extreme texture pass** on the existing H3.1 Detailed geometry task, guided again by the exact four canonical views. This preserves the strongest current body, face, horns, frill, hands, feet, and tail instead of gambling on a new geometry seed.

Estimated cost: **30 credits**  
Projected balance after success: **4,765 credits**  
Additional geometry cost: **0 credits**

This is the completion of the existing hero-source pipeline, not another character attempt.

## What the research says

### Tripo's current official guidance

- H3.1 (`v3.1-20260211`) is Tripo's highest-fidelity generation model and supports up to 2,000,000 faces in Detailed/Ultra geometry mode.
- P1 is a fast, low-poly model capped at 20,000 faces. It is appropriate for prototypes, background characters, secondary props, and strict real-time budgets.
- Tripo's own Smart Mesh tutorial recommends:
  - Smart Mesh for prototypes and batch assets.
  - HD Model plus auto-retopology for hero stills.
  - HD Model plus **manual retopology** for final animated characters.
- The standalone texture endpoint accepts an existing H3.1 task and exactly four texture references in `[front, left, back, right]` order.
- For an H3.1 source, the current texture endpoint explicitly recommends texture model `v3.0-20250812`.
- `texture_alignment: original_image` prioritizes source-color fidelity.
- `texture_quality: extreme` produces the maximum 8K texture tier.
- Tripo strongly recommends re-supplying the source image references when texturing an existing task.
- Rigging must happen after mesh editing. Retopology, segmentation, completion, or other mesh changes invalidate an existing rig.
- Tripo's documented rigging is a body-skeleton and preset-motion system. It does not document production facial blendshapes, a mouth seal, tongue, or chewing shapes.

### YouTube workflow findings

The useful videos agree on a hybrid pipeline, even when their marketing tone differs:

- PixelArtistry's Tripo Ultra walkthrough uses Ultra geometry, HD texture, triangle topology, and no face cap for the high-detail source. It then retopologizes and bakes the high-poly detail onto a usable low-poly mesh in Blender. The video is affiliate-supported, so its quality claims are treated as promotional, but its workflow is technically useful.
- Stefan 3D AI's January 2026 retopology comparison found Tripo's Smart Low Poly output cleaner than several alternatives in some tests, but still showed disconnected pieces, intersections, and areas requiring manual cleanup.
- Stefan's April 2026 production workflow separates geometry, sculpt cleanup, retopology, UVs, baking, texturing, rigging, and weight correction. It explicitly says current AI retopology does not deliver a perfect production wireframe and that textures still need paint/fix work.
- Stefan's July 2025 critical review warns that polished demos are cherry-picked, consistency is the main production risk, and generated output should be treated as a strong starting point rather than deterministic final art.

### Community signal

Recent Tripo community reports say 8K improves close-up clarity around eyes and small edges, but higher resolution does not correct wrong semantic placement, UV errors, or an incorrect expression. Those issues still require Blender or texture-paint correction.

The implication for Bentosaur is simple: 8K is useful for the **master source**, but approval must be based on feature placement and identity, not sharpness.

## Options considered

| Option | New Tripo cost | Preserves current geometry | Hero-animation suitability | Decision |
| --- | ---: | --- | --- | --- |
| Texture current H3.1 Detailed source at 8K Extreme | 30 | Yes | Best source for manual production rebuild | **Recommended** |
| Generate a fresh H3.1 Ultra + 8K Extreme character | 70 | No | High detail, but repeats the geometry lottery | Reject |
| Generate P1/Smart Mesh and texture it | 40+ depending on texture tier | No | Useful for prototypes/NPCs; insufficient for this hero face | Reject |
| Generate H3.1 in editable parts, then texture later | 60 before texturing | No | Adds segmentation risk and cannot texture in the same generation request | Reject for this gate |
| Hand-paint/material the source in Blender only | 0 | Yes | Maximum control, slower | Production fallback and cleanup path |

## Preflight before the paid texture task

No paid request is allowed until all checks pass:

1. Freeze the H3.1 source task and confirm its task ID and GLB hash.
2. Prepare a texture-specific four-view pack from the same canonical turnaround:
   - exactly 1024 × 1024;
   - identical framing, scale, and silhouette;
   - front, left, back, right;
   - one dark eye per side with no catchlight;
   - neutral closed or barely parted mouth;
   - cream horns, frill knobs, belly, fingers, and toes;
   - peach cheeks;
   - no props;
   - neutral background;
   - no floor shadow, baked highlight, dramatic light, or ambient-occlusion stain.
3. Compare the new files against the geometry inputs and reject any silhouette or feature-position drift.
4. Upload the four files and record file tokens plus SHA-256 hashes.
5. Verify live balance and frozen balance.
6. Show the exact request and 30-credit estimate before submission.

## Recommended request

Use the v3 texture endpoint directly because the current CLI does not expose the new four-image texture prompt as a first-class flag.

```json
{
  "input": "f23a7b24-a3d5-433c-a404-3d9d2d8c0787",
  "model": "v3.0-20250812",
  "texture_prompt": {
    "images": [
      { "file_token": "<front>" },
      { "file_token": "<left>" },
      { "file_token": "<back>" },
      { "file_token": "<right>" }
    ]
  },
  "texture_quality": "extreme",
  "texture_alignment": "original_image",
  "pbr": true,
  "bake": false,
  "texture_seed": 29072026
}
```

Why these values:

- `input`: keeps the exact existing geometry.
- `v3.0-20250812`: Tripo's documented texture engine for v3.0 and v3.1 sources.
- four image descriptors: maximum view coverage and explicit color guidance.
- `extreme`: 8K master texture.
- `original_image`: prioritizes the canonical Bentosaur palette and markings.
- `pbr: true`: retains base color, roughness, metallic, and normal maps as separate optional source maps.
- `bake: false`: avoids baking inferred lighting/material effects into canonical base color.
- locked seed: makes the request reproducible.

The endpoint, texture model, nested field, and four-view ordering are explicit in the current API documentation. The `{ "file_token": "..." }` descriptor form for each array member is the conservative implementation of Tripo's documented File input type because the current v3 page does not include a complete four-image JSON example. The raw request must therefore pass schema validation before any paid task is confirmed; the July 2026 Go SDK has not yet typed this newer nested four-image texture field.

For the final soft chibi material in Blender and Godot, metallic should be forced to 0, roughness should be high, and the generated normal map should be weakened or disabled if it introduces unwanted surface noise. PBR generation does not require a realistic art style; it preserves optional material channels.

## Approval package after the one texture task

Stop immediately after the result is downloaded. Do not rig, retopologize, animate, reroll, or submit another texture task.

Render two evidence sets from the unchanged source:

1. **Unlit base-color board** — proves eye, mouth, cheek, belly, horn, frill, finger, toe, and back placement without lighting hiding errors.
2. **Target matte look board** — metallic 0, high roughness, controlled soft light, generated normal reduced or disabled.

Both boards must show front, left, right, back, both three-quarter views, face close-up, hands, feet, horns, frill, belly, and tail.

Mau approves or rejects the actual visual result.

## Pass/fail gate

Hard failures:

- double eye, duplicate eye texture, or offset eye color;
- eye or mouth printed outside the intended raised feature;
- malformed, doubled, or wrongly colored horns;
- cheek, belly, toe, finger, or frill colors crossing semantic boundaries;
- asymmetric texture not present in the canonical references;
- visible UV seam through the face;
- props or clothing added to the character;
- source geometry changed;
- expression or silhouette no longer reads as the canonical Bentosaur.

If the pass fails, do **not** buy another blind reroll. Diagnose whether the issue is:

- a local texture/UV repair that can be painted in Blender;
- a source-reference defect that must be fixed before one explicitly approved retry;
- a geometry mismatch that means Tripo should be retired for this hero and the mesh rebuilt manually.

## Production path after visual approval

1. Treat H3.1 as the high-poly visual source.
2. Manually retopologize the animation master in Blender with deliberate loops around eyes, mouth, shoulders, elbows, hips, knees, and tail.
3. Build the neutral mouth seal, cavity, tongue, jaw control, open smile, and chew shapes on the same topology.
4. UV the production mesh and bake useful high-poly information.
5. Transfer and clean the approved color treatment.
6. Rig and weight-paint only after all topology and mouth work is complete.
7. Export GLB with body animation and facial morph targets to Godot.

An independently generated open-mouth model is not a valid facial-animation solution because it cannot become a safe blend shape unless it shares identical topology and vertex order with the neutral master.

## Sources

- Tripo API pricing: https://developers.tripo3d.ai/en/pricing
- Tripo H3.1 model card: https://developers.tripo3d.ai/en/models/v3-1
- Tripo P1 model card: https://developers.tripo3d.ai/en/models/p1
- Tripo multiview H-Series API: https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard
- Tripo texture API: https://developers.tripo3d.ai/en/docs/models-texture
- Tripo rig check: https://developers.tripo3d.ai/en/docs/animations-rig-check
- Tripo auto rig: https://developers.tripo3d.ai/en/docs/animations-rig
- Tripo Smart Mesh tutorial: https://www.tripo3d.ai/blog/smart-mesh-tutorial
- Tripo stylized asset best practices: https://www.tripo3d.ai/blog/explore/smart-mesh-best-practices-for-stylized-game-assets
- PixelArtistry, “Create Next-Level 3D AI Models in Seconds (Tripo Ultra)”: https://www.youtube.com/watch?v=SibpwWJ3Xxk
- Stefan 3D AI, “Game-Ready Topology with AI? I Compared Best AI Tools”: https://www.youtube.com/watch?v=3hagi51IxeY
- Stefan 3D AI, “My Complete FREE AI 3D Workflow — Characters & Props Pipeline”: https://www.youtube.com/watch?v=MjsQhbaonDc
- Stefan 3D AI, “I'm Done with 3D AI Tools — What I Learned After Spending $1K+”: https://www.youtube.com/watch?v=LFCdkayDni4
