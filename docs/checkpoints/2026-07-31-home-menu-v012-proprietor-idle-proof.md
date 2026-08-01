# Home Menu V012 — Bentosaur Proprietor Idle Proof

**Status:** implemented, captured, tested 22/22; founder visual approval pending

**Date:** 2026-07-31

## Outcome

The approved flat-cel Bentosaur identity now lives behind the real stall for
the first time. The runtime character breathes from a stable bottom-center
pivot, blinks on a randomized schedule, occasionally double-blinks, and obeys
the game's reduced-motion boundary.

![Neutral and blink runtime proof](../../game/docs/runtime-captures/home-menu-v012-proprietor-idle-proof/home-menu-v012-neutral-vs-blink-1080x960.png)

The complete stall shell is the occluder. This keeps the proprietor's body
behind the counter without adding a duplicate counter overlay:

```text
MainCharacter                         z14
StallStructure                        z15
StallAttachmentKit and foreground     z16+
Weather                               z20
```

## Runtime motion

- breath period: `3.4 s`;
- per-session speed: randomized `0.94–1.06×`;
- per-session starting phase: randomized;
- vertical expansion: at most `0.5%`;
- horizontal compensation: at most `0.25%`;
- blink duration: `0.18 s`;
- blink interval: randomized `2.3–5.4 s`;
- double-blink chance: `12%`, with a `0.14 s` open gap;
- reduced motion: spatial breathing disabled, discrete blink retained.

The controller advances from elapsed time rather than frame counts. Seeded
tests prove the same breath and blink state at 30, 60, and 120 FPS.

## Asset promotion

The immutable registered V3 neutral and blink sources are hash-verified and
losslessly common-cropped by:

`tools/art/promote_bentosaur_proprietor_v001.py`

Runtime output lives under:

`game/assets/characters/bentosaur_proprietor/v001/`

The manifest records source hashes, output hashes, crop, origin, logical scale,
and the complete first-playable motion contract.

## Honest limitation

This is a whole-sprite proof, not the final character rig. It validates
identity, scale, occlusion, breathing, blink cadence, and phone-sized presence.
It does not yet provide independently controlled eyes, mouth, laugh accents,
or counter-resting foreground hands.

If Mau approves this in-scene presence, the next visual gate is a registered
shared-body reconstruction:

```text
MainCharacter
├── BodyBreathRoot        # body, head, eyes and mouth behind stall
└── ForegroundArmsRoot    # continuous hands above the counter
```

That pass reuses the accepted controller instead of replacing the motion work.
No walking, waving, chewing, or customer system is being implied by V012.

## Evidence

- [six-second idle motion proof](../../game/docs/runtime-captures/home-menu-v012-proprietor-idle-proof/home-menu-v012-idle-motion.mp4);
- [neutral runtime frame](../../game/docs/runtime-captures/home-menu-v012-proprietor-idle-proof/home-menu-v012-neutral-540x960.png);
- [blink runtime frame](../../game/docs/runtime-captures/home-menu-v012-proprietor-idle-proof/home-menu-v012-blink-540x960.png);
- [reduced-motion runtime frame](../../game/docs/runtime-captures/home-menu-v012-proprietor-idle-proof/home-menu-v012-reduced-motion-540x960.png).

The transient 180-frame sequences and capture WAV files were not added to the
repository.
