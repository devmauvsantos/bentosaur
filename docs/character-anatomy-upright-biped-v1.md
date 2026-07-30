# Canonical Dinosaur Anatomy — Upright Biped v1

**Status:** Canonical  
**Decision date:** July 28, 2026  
**Machine-readable source:** `art/character-anatomy.json`

## Decision

Bentosaur's dinosaurs are cute, compact **upright bipeds**.

They stand, walk, carry bentos, cook, hold umbrellas, turn book pages, gesture, and emote on two weight-bearing hind legs. Their short forelimbs behave as hands. Their tails counterbalance the large head and make the species silhouette readable.

This is a stylized world rule, not a paleontology rule. It applies even to species that were quadrupedal in reality. A generated Ankylosaurus, Triceratops, or other grounded cast member must be adapted into Bentosaur's anthropomorphic two-leg body language.

“Cute” does not mean crawling, pet-like, baby-animal, dog-like, or four-footed.

## Full-body silhouette contract

Every full-body hero, customer, and grounded street-pedestrian dinosaur must show:

- exactly two weight-bearing hind legs;
- an elevated torso and pelvis;
- two short forearms held above the ground as hands;
- a large readable species-specific head;
- a visible tail in side and three-quarter views;
- enough foot width to make the pose feel balanced at 64 source pixels.

The spine reads vertically or with a gentle forward lean:

```text
head / frill
      ↓
elevated torso
      ↓
hips
      ↓
two hind feet

tail extends behind as counterweight
forearms remain free as hands
```

## Pose classes

### Neutral full body

Two planted hind feet, upright torso, relaxed or gesturing hands, and a balancing tail.

### Service walk

The hind legs alternate through the stride while both arms remain available to hold a bento, cup, umbrella, ingredient, parcel, or book.

This is the fastest practical anatomy test:

> Could this dinosaur walk into the stall carrying a bento with both hands without changing its anatomy?

If not, reject it.

### Counter host

The upright body may be partially hidden by the counter. Hands may support the cheeks, prepare food, hold utensils, ring the bell, or present a finished bento.

### Portrait or album emote

The book may crop to the head, frill, shoulders, and hands. The legs do not need to be visible because the asset does not depict locomotion. Portrait cropping never changes the underlying full-body contract.

## Proportion guidance

- Head and frill: roughly 42–58% of full sprite height.
- Hind legs: roughly 18–30% of full sprite height.
- Tail: roughly 30–65% of body length when the view permits it.
- Forearms: short but articulated enough to hold a prop or touch the cheeks.
- Feet: broad and separated enough to sell two-leg balance.
- Body: compact and rounded without becoming horizontal.

These are guides, not automatic scaling formulas. Silhouette and action readability take priority.

## Automatic rejection

Reject a candidate when:

- a forelimb, knuckle, or front foot touches the ground;
- four limbs bear weight;
- the torso reads horizontally like a dog or cat;
- the character crawls or sits in a pet-like posture when a standing pose was requested;
- forearms are shaped as a second pair of walking feet;
- the side or three-quarter full-body pose loses its tail;
- an animation changes between biped and quadruped anatomy;
- the pose cannot plausibly carry a tray with both hands while moving.

A perfect face, palette, or expression never overrides an anatomy failure.

## Reference responsibilities

| Reference | Use |
|---|---|
| `bentosaur-biped-anatomy-reference.png` | Upright body plan, hind-leg locomotion, free hands, torso elevation, tail counterbalance |
| `bentosaur-front-face-reference.png` | Triceratops frill, horn placement, joyful face, cheeks, hands |
| `bentosaur-character-reference.png` | Sage/cream/coral identity, outline, shading, cozy pixel treatment |

References must be labelled by responsibility when the provider supports it. Do not pass a mixed pile of images and expect the model to infer which anatomy, palette, prop, pose, or environment is authoritative.

## Prompt lock

Positive anatomy language:

```text
upright bipedal dinosaur; standing on exactly two weight-bearing hind
legs; elevated torso and hips; two short free forearms used as hands;
long visible tail used as counterbalance; anthropomorphic service posture
```

Negative anatomy language:

```text
not quadrupedal; not on all fours; no forelimb ground contact; no
dog-like horizontal torso; no four walking legs; no crawling posture
```

Use both. Positive instructions define what to construct; negative instructions close the model's common fallback.

## Animation implications

- Walk cycles alternate only the hind legs.
- Arms remain independently available for carrying and gesturing.
- The tail follows the hips with restrained counter-motion.
- Root and foot baselines are locked before in-betweens are generated.
- The biped gate is evaluated on every frame, not only frame one.
- Portrait reactions may animate hands and face without displaying the legs.

## Hard asset-separation contract

Generate and maintain every dinosaur master as an isolated, prop-free,
clothing-free character. Permanent body colors and facial surfaces belong to
the character. A pose may later be authored to receive, carry, bite, or open an
object, but that object is never fused into the character asset.

The character master owns:

- species anatomy, including horns, frill knobs, cheeks, hands, feet, and tail;
- base palette material slots;
- armature, weights, corrective shapes, and replaceable face system;
- prop-free body actions and interaction poses;
- stable sockets for hands, tray, mouth, hat, back, umbrella, and apron.

For the first production proof it explicitly excludes:

- umbrella, tray, bento, bowl, cup, utensils, and book;
- every clothing mesh, outfit variant, and wardrobe system;
- accessories, which are deferred;
- counter, floor, background, shadow, weather, and VFX;
- food fused to a hand or mouth;
- one permanently painted expression.

Required socket names:

```text
socket_hand_l
socket_hand_r
socket_tray
socket_mouth_bite
socket_head_hat
socket_back
socket_umbrella
```

The first proof does not implement these deferred accessory sockets. They
remain reserved names for a later explicit accessory decision.

Boundary test:

> If removing it changes the dinosaur's species identity or bare neutral
> anatomy, it belongs to the character master. If it can be swapped between
> compatible customers, it is a prop or accessory.

## Live validation

Live Test 01 used only a tight face/style crop and generated appealing quadrupeds. Those candidates are rejected.

Live Test 02 used three labelled references plus explicit positive and negative anatomy language. All 16 candidates passed the upright-biped body-plan gate. Candidate 12 is the current normalization recommendation, pending human approval; it still requires the signature cream frill-rim knobs and small hand/horn cleanup.
