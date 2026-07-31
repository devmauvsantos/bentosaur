# Home Menu Stall V003 — Responsive Distance

Status: implemented and installed on the reference iPhone

Date: 2026-07-31

## Founder feedback

The V002 stall silhouette and aspect ratio were approved, but the iPhone
composition made the stall feel too close compared with
`bentosaur-home-menu-refined-classic-guestbook-v2.png`.

## Locked correction

- Keep the rainy Home Village full-bleed with the existing aspect-cover world.
- Present the complete stall assembly through one responsive `StallStage`.
- Center the 9:16 authored composition inside ultratall viewports.
- Apply a uniform `0.86` founder-framing scale around the approved stall's
  visible-center pivot `(360, 634)`.
- Never independently resize future proprietor, occluder, props, lanterns, or
  stall-local effects; all of them inherit `StallStage`.

The approved concept uses approximately `67.7%` of its width for the stall.
The runtime V003 framing uses approximately `67.6%` (`486.76 / 720`), with
about `116.6 px` of breathing room on each side of the Pro Max logical canvas.

## Ultratall proof

![Home Menu Stall V003 at 720 by 1564](assets/home-menu-stall-v003-pro-max.png)

The proof was captured through Godot Movie Maker at the iPhone 17 Pro Max
logical aspect. Preset 3, rain, environment lighting, and the full-bleed
background are active.

## Verification

- All 10 Godot contract tests pass.
- Godot iOS debug export succeeds.
- Personal-signing contract passes.
- Xcode device build succeeds.
- Bundle `com.mauvsantos.bentosaur` is signed by personal team `53RJ43876F`
  with `Apple Development: Mauricio Vargas (CRAZV8U43J)`.
- The V003 build was installed and launched on the connected iPhone 17 Pro Max.
