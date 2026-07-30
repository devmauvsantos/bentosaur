# Bentosaur AI Art Pipeline — Live Test 02: Upright Biped

**Date:** July 28, 2026  
**Status:** Complete — upright-biped anatomy pass; human identity approval pending  
**Provider:** PixelLab Pro  
**Provider job:** `c39149e0-f696-4c75-913c-7b2f49566580`  
**Seed:** `184726`  
**Cost:** 20 PixelLab subscription generations  
**Output size:** 56×56 candidates for placement inside a fixed 64×64 game cell

## Correction being tested

Bentosaur dinosaurs are **cute upright bipeds**. The first live test copied the face and palette successfully but generated a naturalistic four-footed body plan. That entire candidate lineage is rejected.

The canonical rule is stored in `art/character-anatomy.json`:

- exactly two weight-bearing hind legs;
- elevated torso and hips;
- two short forelimbs used as free hands;
- no forelimb ground contact;
- visible tail counterbalancing side and three-quarter poses;
- no quadruped, crawling, pet-like, or dog-like silhouette;
- portrait/emote crops may omit the lower body because they are not locomotion assets.

The deciding human-review question is:

> Could this dinosaur walk into the stall carrying a bento with both hands without changing its anatomy?

If the answer is no, the candidate is rejected.

## Labelled reference stack

PixelLab Pro accepts up to four labelled reference images. Test 02 deliberately separates what the model should learn from each source:

1. `art/references/bentosaur-biped-anatomy-reference.png`
   - use only for the upright two-leg body plan, free forearms, elevated torso, and tail counterbalance;
   - do not copy its tray, food, motion, or rainy background.
2. `art/references/bentosaur-front-face-reference.png`
   - use only for the Triceratops frill, horn arrangement, joyful face, coral cheeks, and hand-like forearms;
   - this is a portrait, not the full-body anatomy source.
3. `art/references/bentosaur-character-reference.png`
   - use only for the sage/cream/coral identity and the Bentosaur outline, shading, and pixel-cluster treatment.

The third image is also passed as `style_image_base64`, limited to `color_palette`, `outline`, `detail`, and `shading`.

**Rule:** reference labels are part of the art contract. Never pass multiple unlabeled images and ask the model to infer which anatomy, palette, prop, pose, or environment to copy.

## Generation contract

- Operation: `create_image_pro`
- Request: `art/jobs/pixellab-bentosaur-anchor-biped-02.json`
- Metadata: `art/jobs/pixellab-bentosaur-anchor-biped-02.meta.json`
- Candidate count: 16
- Transparent background: required
- Internal canvas: 56×56
- Final game cell: 64×64
- Fixed seed: `184726`

The prompt repeats the non-negotiable anatomy in positive and negative form:

- upright biped;
- exactly two weight-bearing hind legs;
- short forearms held freely as hands;
- long visible counterbalancing tail;
- not quadrupedal;
- not on all fours;
- no forelimb ground contact;
- no dog-like horizontal torso;
- no extra legs.

The output is intentionally generated at 56×56. A selected sprite can be placed inside the 64×64 cell without rescaling, leaving room for a fixed pivot, baseline, and safe transparent padding.

## Acceptance gate

Each candidate receives:

1. **Biped anatomy**
   - two hind feet bear weight;
   - forearms remain above the ground;
   - torso is elevated;
   - body is not horizontal;
   - tail is visible.
2. **Species identity**
   - readable Triceratops frill;
   - three horns;
   - no missing or duplicated limb/horn.
3. **Bentosaur identity**
   - sage-green dominant body;
   - cream horns/highlights;
   - coral blush;
   - warm, expressive, non-generic personality.
4. **Production structure**
   - complete visible silhouette;
   - transparent background;
   - safe padding;
   - binary alpha;
   - no prop, text, UI, or cast shadow.

No candidate advances merely because its face is cute.

## Results

Generation result: success.

- 16 candidates returned.
- 16/16 read as upright bipeds.
- 16/16 place weight on two hind legs.
- 16/16 keep the forearms above the ground as hands.
- 16/16 retain a readable balancing tail.
- 16/16 are 56×56 with binary alpha.
- 0/16 match the canonical 24-color palette without normalization.
- Visible color count ranges from 32 to 38.

The body-plan correction is decisive: the earlier face-only reference produced compact quadrupeds, while the labelled stack produced an entire batch of coherent upright service-character silhouettes. Explicitly telling PixelLab what to copy from each reference was more effective than adding more descriptive adjectives to one mixed reference.

All candidates still touch at least the top, left, or bottom edge of their 56×56 internal canvas. This is acceptable only because the image is an internal sprite footprint, not the final cell: it will be placed unscaled inside 64×64, yielding at least four source pixels of cell-level breathing room. The feet are then aligned to baseline `y=58`.

### Current recommendation

Advance `candidate-12` to normalization, pending human approval.

Why:

- strongest balance of clean pixel clusters and cozy expression;
- unambiguous two-hind-leg stance;
- both forearms read as hands;
- long tail balances the large frill;
- simple, unpatterned surface that will quantize more predictably;
- compact upright silhouette that remains readable without becoming quadrupedal.

Required identity cleanup:

- add a restrained row of cream scalloped knobs around the outer frill;
- strengthen the brow horns;
- shorten the muzzle by approximately one source pixel;
- separate the near hand from the cream belly;
- add a tiny coral smile without changing the calm expression.

The missing frill-rim knobs are a batch-wide identity failure. They do not invalidate the successful body-plan experiment, but no candidate can become the canonical Bentosaur until this signature feature is restored.

Strong alternates:

- `candidate-00`: strongest service/tray-carry potential and clean anatomy, but its smooth frill and tiny horns feel more generic;
- `candidate-10`: useful neutral animation anchor with open eye and clear hands, but less emotionally warm;
- `candidate-05`: high personality, but the cream frill mottling is noisy and should not become an identity mark accidentally.

The batch is intentionally consistent rather than diverse. It proves the body plan, not the final breadth of facial expressions, outfits, or poses.

PixelLab balance after this test: 1,938 of 2,000 subscription generations remain; 62 have been used across both live tests.

## Next action after selection

1. Obtain human approval for candidate 12 or select another candidate.
2. Place the chosen 56×56 anchor inside the untrimmed 64×64 cell.
3. Quantize it to the canonical 24-color palette.
4. Align the hind-foot baseline and pivot `[32, 58]`.
5. Create the neutral side/three-quarter anchor first.
6. Derive the front-facing counter-host pose and the side-facing service walk from that same approved anatomy.
7. Only then compare persistent-object animation with authored key poses.
