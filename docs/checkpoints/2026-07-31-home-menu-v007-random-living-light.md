# Home Menu V007 — Random Living Light

Status: implemented, verified, installed, and launched on the reference iPhone;
founder aesthetic review pending

Date: 2026-07-31

## Outcome

V006 proved on the physical iPhone that explicit RGB emission motion survives
the full rain, Retina, preset-3 anime, stall, and ultratall composite. Mau
confirmed both its breath and its local fixture flick were visible. V007 removes
that fixed test timeline and installs the first production-shaped behavior.

The result is intentionally not a looping animation. It combines one slow,
irregular village-wide light drift with rare localized imperfections.

## Irregular breathing

- Core emission alternates between randomized low targets of `0.78–0.86` and
  high targets of `0.94–1.00`.
- Low journeys take `4.8–8.6 s`; high journeys take `5.4–11.5 s`.
- Alternating separated bands prevent the random walk from choosing two nearly
  identical targets and becoming invisible again.
- Halos inherit `72%` of the core excursion.
- Indirect warm spill inherits `42%`.
- Wet-pavement reflections remain completely fixed.
- Every transition uses smootherstep interpolation; there is no mechanical
  sine period and no brightness overshoot.

The four Metal frames below cover one seeded startup and first irregular breath
inside the complete ultratall composite:

![V007 irregular living-light composite](assets/home-menu-v007-random-living-light.png)

## Rare fixture flicks

- The first event waits a random `60–105 s` after the light wake.
- Every later event waits another `60–105 s` after the previous burst ends.
- An event randomly contains **one, two, or three** individual flicks.
- Every dip receives independent timing and a core RGB floor of `0.36–0.56`.
- Small randomized holds, recoveries, and inter-flick gaps prevent a repeated
  canned rhythm.
- One of six certainly visible windows or lanterns is chosen per event.
- The immediately previous fixture cannot be selected again.
- Halos inherit `78%` and local spill `38%` inside registered circular masks.
- Recovery stops at `1.0`; no rebound can clip the additive composite.

## Accessibility and QA

`--reduced-motion` holds every emission multiplier at `1.0` after the normal
light wake while retaining the scene, weather, and audio. This is the runtime
contract for a future in-game reduced-motion setting.

Deterministic tests prove at 30, 60, and 120 Hz that:

- seeded event times, fixture choices, and 1–3 counts are identical;
- the first and subsequent event cadence can never violate the one-minute
  minimum;
- fixture selection never repeats immediately;
- core, halo, and spill values remain bounded and unclipped;
- stable layer alpha and wet-pavement reflections do not animate.

All 11 Godot contracts pass, as do deterministic, reduced-weather, and
reduced-motion Home Village variants.

The iOS export passed the personal-signing guard, Xcode built with `Apple
Development: Mauricio Vargas (CRAZV8U43J)` under team `53RJ43876F`, strict
code-sign verification passed, and V007 was installed and launched on the
iPhone 17 Pro Max.
