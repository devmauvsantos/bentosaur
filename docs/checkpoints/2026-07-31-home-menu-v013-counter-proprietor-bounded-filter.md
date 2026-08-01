# Home Menu V013 — Counter Proprietor and Bounded Anime Filter

**Status:** implemented and captured; founder character approval and physical
iPhone longevity gate pending

**Date:** 2026-07-31

## Outcome

The proprietor now uses the actual home-menu pose: both arms are continuously
connected to the body and both three-clawed hands rest on the stall counter.
The stall itself is not baked into the character asset.

![Registered neutral and blink states](../../game/docs/runtime-captures/home-menu-v013-counter-proprietor-bounded-filter/home-menu-v013-neutral-vs-blink-1080x960.png)

Godot renders the pose with a deliberate sandwich rather than cutting up the
stall image:

```text
Proprietor body and expression       effective z14
StallStructure                       effective z15
Proprietor foreground arms/hands     effective z16
Stall attachments                    effective z16+
Weather                              effective z20
```

The body and foreground hands share the same bottom-anchored breathing root,
so the fingers cannot drift away from the counter during the idle. The shared
counter-contact origin is `(360, 699)` on the `720 × 1280` logical canvas; the
runtime art uses a `0.20` logical scale.

## Registration-safe blink

The neutral source is immutable appearance and registration authority. The
generated blink source is not swapped as a second complete redraw. The V002
builder composites only two feathered eye patches over the neutral source, so
every pixel outside the face gate remains tied to the neutral registration.
The same neutral source also produces the foreground hand layer.

The reproducible builder is:

`tools/art/promote_bentosaur_proprietor_counter_v002.py`

Candidate source, complete built-in ImageGen prompts, chroma exports, and the
approval boundary live under:

`art/candidates/2d/proprietor-counter-pose-v001/`

Runtime output and source/output hashes live under:

`game/assets/characters/bentosaur_proprietor/v002/`

This is a visual candidate, not a silent art approval. Mau owns the decision on
the final character size, expression, and fit in the stall.

## Five-minute anime-filter failure — leading diagnosis

The leading diagnosis is that the iPhone screenshot does not show the filter
rectangle moving. The boundary's measured slope is approximately `-0.16`,
matching the old procedural grain hash's constant-phase slope:

```text
-12.9898 / 78.233 = -0.166
```

The old shader combined ever-growing engine time with a large sine argument.
The screenshot's matching slope strongly implicates iPhone fragment precision
collapsing that noise into a moving diagonal band after roughly five minutes,
but causality remains provisional until the failing phone passes. V013 removes
both risky inputs. A controller now supplies one of 256 bounded grain frames
at 12 FPS, and the shader hashes only bounded pixel/frame coordinates.

The viewport-pinning and application-resume coverage repair remains in place
for the separate drawable-recreation failure mode.

## Longevity evidence and remaining gate

A Forward Mobile / Metal Movie Maker run rendered 360 frames at one simulated
frame per second, covering six simulated minutes. The final `t=358 s` frame
and stall crop remain coherent with no diagonal boundary:

![Six-minute bounded-filter frame](../../game/docs/runtime-captures/home-menu-v013-counter-proprietor-bounded-filter/home-menu-v013-filter-t358s-540x960.png)

This desktop-Metal acceleration is strong regression evidence, but it is not a
substitute for the failing device. The release gate remains:

1. run uninterrupted on the iPhone for 8–10 minutes;
2. inspect around 30 seconds, 4 minutes, 5.5 minutes, and 8 minutes;
3. background/resume the app;
4. inspect for another 1–2 minutes.

If the bounded procedural hash still fails physically, the next bounded
fallback is a tiny precomputed tileable grain atlas. A SubViewport rewrite is
not justified by the present evidence.

## Evidence

- complete Godot contract suite: **22 passed, 0 failed**; two unrelated fixture
  tests retain non-failing ObjectDB exit-cleanup warnings;
- fresh iOS debug export and generic-device Xcode build: **succeeded**;
- signature: `com.mauvsantos.bentosaur`, personal Team `53RJ43876F`,
  `Apple Development: Mauricio Vargas (CRAZV8U43J)`;
- repository capture evidence is excluded from mobile packing through
  `game/docs/.gdignore`, reducing the debug PCK from `56 MB` to `37 MB`;
- [six-second idle motion proof](../../game/docs/runtime-captures/home-menu-v013-counter-proprietor-bounded-filter/home-menu-v013-idle-motion.mp4);
- [neutral runtime frame](../../game/docs/runtime-captures/home-menu-v013-counter-proprietor-bounded-filter/home-menu-v013-neutral-540x960.png);
- [blink runtime frame](../../game/docs/runtime-captures/home-menu-v013-counter-proprietor-bounded-filter/home-menu-v013-blink-540x960.png);
- [counter-contact detail](../../game/docs/runtime-captures/home-menu-v013-counter-proprietor-bounded-filter/home-menu-v013-counter-contact-detail.png);
- [six-minute filter frame](../../game/docs/runtime-captures/home-menu-v013-counter-proprietor-bounded-filter/home-menu-v013-filter-t358s-540x960.png);
- [six-minute stall detail](../../game/docs/runtime-captures/home-menu-v013-counter-proprietor-bounded-filter/home-menu-v013-filter-t358s-stall-detail.png).

The signed app is ready at
`build/ios-derived/Build/Products/Debug-iphoneos/Bentosaur.app`. Installation
was not attempted because Mauricio's iPhone 17 Pro Max reported `unavailable`.
