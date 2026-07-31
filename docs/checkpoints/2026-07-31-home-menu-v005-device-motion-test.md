# Home Menu V005 — Device Motion Test

Status: device-rejected as imperceptible; roof-impact architecture retained,
lighting profile superseded by V006

Date: 2026-07-31

## Why this build exists

The V004 living-light treatment was technically correct but too quiet to judge
on the iPhone 17 Pro Max. The fixture breathing was difficult to see, the first
flick could take more than a minute to arrive, and the sparse roof impacts did
not yet include the Bentosaur stall.

V005 was deliberately intended as an exaggerated approval instrument. It
proved placement and scheduling in automated captures, but it failed the only
important gate: Mau could see neither the breathing nor the flick on the
physical phone.

## Rejected phone-test profile

| Motion | V004 baseline | V005 test |
|---|---:|---:|
| Core breathing level | `0.992–1.006` | `0.940–1.008` |
| Breathing segment | `3.8–10.5 s` | `3.0–7.0 s` |
| Halo inheritance | `55%` | `70%` |
| First flick after light wake | `60–105 s` | `3–6 s` |
| Later flick cadence | `60–105 s` | `8–15 s` |
| Local dip | `0.955–0.975` | `0.78–0.87` |
| Dip/rebound duration | `0.18–0.28 s` | `0.30–0.46 s` |

Only eight fixtures that remain visible around the current Pro Max stall crop
participate. Consecutive flicks cannot select the same fixture. The strongest
allowed core output remains below clipping:

`0.99 × 1.008 × 1.002 = 0.999916`

The broad ambient spill and pavement reflections remain fixed after wake; only
the registered cores, their quieter halos, and one local fixture mask move.

## Device result and root cause

Mau reported no visible pulse and no visible flick after the signed V005 build
was installed and launched on the reference iPhone 17 Pro Max.

The scheduler was running, but the final composite hid its output:

- cores occupy only about `1.18%` of the authored canvas;
- halos occupy only about `2.76%`;
- the much broader indirect spill and reflections stayed fixed;
- randomized targets did not guarantee a complete excursion;
- the local event lasted only `0.30–0.46 s`;
- preset-3 grain continued moving at phone scale;
- the additive shader varied alpha rather than explicitly scaling emission
  RGB.

The saved left-lantern proof changed its small region by only about `4.9%` for
one frame, while whole-frame change was negligible. This is an evidence-backed
failure, not a request to increase the same percentages again.

## Roof-impact expansion

- The shared randomized scheduler now runs every `0.26–0.62 s` at full weather
  and every `0.90–1.80 s` with `--reduced-weather`.
- `34%` of scheduled roof events route to the stall while it is present.
- Village impacts keep their original registered roof anchors.
- Stall impacts use sixteen independent anchors on the tile planes and eaves.
- The stall receiver is a child of `StallStage` at z-index `16`, so it preserves
  the approved framing on both `720 × 1280` and ultratall displays.
- Stall impacts use `48–60%` opacity, small perspective scales, slight jitter,
  and the same eight-frame cool rain atlas.
- One scheduler owns both target sets. Disabling rain stops scheduling and
  clears active splashes on both layers.

This component boundary is intentional: village weather uses the aspect-cover
world transform, while stall impacts must inherit the responsive contain-stage
transform. Mixing their authored coordinates would make the drops drift off the
stall on an ultratall phone.

## Visual proof

![V005 integrated Pro Max render](assets/home-menu-v005-device-motion-test-promax.png)

The following four frames cover the first deterministic fixture dip and
recovery. The changing rain and animated transfer grain remain active because
this is an integrated runtime proof, not a reconstructed lighting mockup.

![V005 first-flick sequence](assets/home-menu-v005-flick-sequence.png)

The next sequence shows one stall-roof splash advancing through the shared
eight-frame rain atlas while remaining registered to the stall roof.

![V005 stall-roof impact sequence](assets/home-menu-v005-stall-roof-impact-sequence.png)

## Verification

- All 11 Godot contract tests pass.
- Full and reduced deterministic weather variants pass.
- The stronger motion timeline is identical at 30, 60, and 120 Hz.
- A seven-second `720 × 1564` Forward Mobile / Metal capture passes.
- Godot iOS debug export passes.
- The generated Xcode project passes the personal-signing guard.
- Strict code-sign verification passes with entitlement
  `53RJ43876F.com.mauvsantos.bentosaur`.
- Xcode signs with `Apple Development: Mauricio Vargas (CRAZV8U43J)`; no
  Mellow identity or team is present.
- The build installs and launches on Mauricio's iPhone 17 Pro Max.

## Disposition

- Reject V005 lighting values and alpha-only control.
- Retain the denser shared roof scheduler, stall-local receiver, anchors, and
  rain lifecycle behavior for continued device review.
- Use V006 as one deterministic RGB-path diagnostic before designing the final
  randomized production motion.
- Keep V004 as the documented calm rollback baseline.
