# Home Menu V008 — Linked Reflections and Stable Anime Coverage

Status: implemented, automated contracts pass, Metal capture approved for
device review; signed iOS build ready, physical install pending reconnection

Date: 2026-07-31

## Outcome

V008 supersedes V007's fixed-reflection and one-minute-flick assumptions.
Every painted light source is now registered, each source owns its corresponding
wet-pavement reflection band where one exists, and both are driven by the same
motion state in the same frame.

The post-process was hardened after Mau observed the 1990s-anime treatment
sliding upward and exposing an untreated region on the physical iPhone. The
filter now owns an explicit full-viewport back-buffer copy and continuously
repairs its coverage after viewport or iOS lifecycle changes.

## Source and reflection contract

- `18` source entries cover every visible window and lantern in the approved
  village painting: `17` complete fixtures plus the clipped far-left window.
- `9` independently painted floor-reflection bands are registered as `R0–R8`.
- The clipped far-left source has no on-canvas reflection and therefore uses a
  zero-weight reflection record.
- Shared reflection bands use source-contribution weights instead of turning
  the whole painted band off when only one contributing fixture flicks.
- The complete right side is registered: the upper-right-center window,
  right-center lantern and window, large lower-right window, narrow door
  window, large upper-right window, and far-right lantern.

The reflection bands are:

| Band | Runtime rectangle |
| --- | --- |
| R0 | `x 70–135, y 507–814` |
| R1 | `x 161–238, y 471–973` |
| R2 | `x 256–294, y 458–572` |
| R3 | `x 321–354, y 420–476` |
| R4 | `x 355–397, y 431–596` |
| R5 | `x 398–454, y 433–833` |
| R6 | `x 455–490, y 478–636` |
| R7 | `x 552–626, y 504–964` |
| R8 | `x 627–709, y 514–900` |

## Motion contract

- Source and reflection breathing are exactly in phase.
- Core emission keeps the approved randomized `0.78–0.86` low and
  `0.94–1.00` high targets.
- Halos inherit `72%` of the core excursion, indirect spill `42%`, and floor
  reflections `36%`.
- The first local flick begins after a random `6–12 s`.
- Later events begin `14–28 s` after the previous burst ends.
- Every event independently chooses one, two, or three dips.
- The selected source, its broader halo/spill neighborhood, and its reflection
  use the same dip timing. Per-source core radii end before the nearest other
  registered core, while the softer shared illumination can still overlap
  naturally. The reflection receives `62%` of that local motion, multiplied by
  its contribution weight when the painted band is shared.
- Reflections never lag, lead, or start an independent flick.
- Broad layer alpha remains stable; RGB emission carries the motion through
  the Retina/Metal composite.
- `--reduced-motion` holds every light and reflection multiplier at `1.0`
  after the normal wake sequence.

## Anime post-process repair

The screen-reading pass now:

1. places one `BackBufferCopy` before the filter in viewport-copy mode;
2. runs its coverage controller in `PROCESS_MODE_ALWAYS`;
3. pins the filter to the current viewport visible rectangle on ready,
   deferred ready, and every viewport-size change;
4. explicitly re-arms the copy after mobile resume and focus-in notifications,
   including same-size drawable recreation;
5. repairs unexpected position, size, transform, or copy-mode drift while the
   app is running or paused;
6. uses an opaque, unshaded replacement pass.

This removes the launch-time rectangle assumption that allowed an untreated
band to appear after the iOS surface changed.

## Verification

- All `12` Godot test scripts pass.
- Normal, reduced-weather, and reduced-motion Home Village variants pass,
  for `14/14` executed contracts.
- The motion schedule is deterministic at `30`, `60`, and `120 Hz`.
- A forced far-right-lantern check proves source `S17` drives normalized band
  `R8` from the same local flick state, attenuated by `0.62 × 0.55` coupling.
- The full right-side tuple list, every per-band weight sum, and all 18
  nearest-neighbor core-radius separations are regression-tested.
- The post-process coverage test exercises `720×1280`, `720×1564`,
  `440×956`, and `1024×1366`, then injects geometry and copy-mode drift while
  paused and proves recovery.
- A `390`-frame Forward Mobile / Metal capture completed at `540×960` and
  `30 FPS`; the anime pass remained edge-to-edge and the scene composite was
  visually intact.
- The iOS device build succeeds with identifier
  `com.mauvsantos.bentosaur`, personal team `53RJ43876F`, and
  `Apple Development: Mauricio Vargas (CRAZV8U43J)`. Strict code-sign
  verification passes.

The connected iPhone was unavailable at the final install step. Physical
validation remains required for the original slide-away report and the final
motion strength.
