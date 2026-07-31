# Home Menu V006 — Guaranteed Light Diagnostic

Status: implemented, verified, installed, and launched on the reference iPhone;
founder visibility confirmation pending

Date: 2026-07-31

## Purpose

V005 proved that changing small alpha-only core and halo overlays is not a
useful physical-device test. V006 makes one bounded compositor diagnosis. It is
not an aesthetic proposal and it is intentionally too strong for production.

The test answers exactly one question: can emission breathing and a localized
fixture flick remain visible through rain, the anime transfer, Retina density,
and the complete stall composition when the correct light layers participate?

## Guaranteed eight-second sequence

The sequence starts after the normal registered light wake and repeats every
eight seconds:

| Cycle time | State |
|---:|---|
| `0.00–0.80 s` | all dynamic emission at full strength |
| `0.80–2.20 s` | smooth breath down |
| `2.20–3.00 s` | hold the diagnostic minimum |
| `3.00–4.40 s` | smooth recovery |
| `4.40–5.30 s` | full-strength hold |
| `5.30–5.85 s` | fixed double-flick on the brightest left lantern |
| `5.85–8.00 s` | full-strength hold |

Breath minima:

- core RGB: `0.55`;
- halo RGB: `0.6175` (85% inheritance);
- indirect-spill RGB: `0.7075` (65% inheritance).

The wet-pavement reflections, unlit background, and stall stay fixed.

The fixed local flick uses the registered fixture at authored `(93, 283)`:

`1.00 → 0.12 → hold → 0.55 → 0.20 → 1.00`

The first fall takes `0.08 s`, the first hold `0.10 s`, rebound `0.08 s`,
second dip `0.08 s`, and recovery `0.21 s`. Halos inherit 85% and the broader
indirect spill inherits 50% inside larger registered masks.

## Corrected compositor path

The registered additive-light shader now exposes `global_intensity` and
multiplies `source.rgb` explicitly. Its local spatial mask also multiplies RGB
instead of alpha. All maxima stay at `1.0`, so the diagnostic cannot introduce
emission clipping.

The indirect warm spill now uses the same registered shader as cores and halos,
with a wider local radius. Reflections remain a stable additive layer. This
tests the physical light hierarchy instead of asking a tiny core-only overlay
to overpower the complete composite.

## Metal visual proof

The four columns show full emission, minimum hold, recovered emission, and the
fixed left-lantern flick in the complete ultratall runtime:

![V006 guaranteed light diagnostic](assets/home-menu-v006-guaranteed-light-diagnostic.png)

Full-versus-minimum frames differ by a whole-frame RGB MAE of about `1.60%`
even with rain and animated preset-3 grain active. The difference is visibly
obvious in the integrated render rather than only in internal uniforms.

## Verification and deployment

- The exact trajectory passes at 30, 60, and 120 Hz.
- All 11 Godot contracts plus the reduced-weather variant pass.
- The complete `720 × 1564` Forward Mobile / Metal sequence renders correctly.
- Godot iOS export and the generated-Xcode personal-signing guard pass.
- Xcode signs with `Apple Development: Mauricio Vargas (CRAZV8U43J)` and team
  `53RJ43876F`.
- Strict code-sign verification passes.
- The diagnostic installs and launches on Mauricio's iPhone 17 Pro Max.

## Stop condition

Do not tune another number before Mau answers whether both the slow breath and
the fixed double-flick are visible on this build. If either remains invisible,
stop this shader path and inspect the physical-device render/lifecycle directly.
If both are visible, remove the fixed diagnostic timeline and design the final
irregular production profile using these proven RGB layer relationships.
