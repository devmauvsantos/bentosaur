# Home Menu V014 — Static Foreground Relight Evidence

Date: 2026-07-31

Status: implementation, Forward Mobile/Metal capture, personal signing, and
physical iPhone installation complete; founder phone-scale visual approval
pending.

## Captures

- `home-menu-v014-relight-off-540x960.png`
- `home-menu-v014-relight-on-brighter-buttons-540x960.png`
- `home-menu-v014-static-relight-ab-1080x1012.png`

The A/B frames are from the same deterministic timestamp. OFF restores the
V013 checkpoint. ON applies the approved night relationship and Mau's follow-up
request to keep the menu buttons brighter than the lower cabinet.

## Runtime treatment

- Cool modulation affects only the stall, proprietor, and non-emissive props.
- The four button frames use a brighter `0.90` base than the stall and props.
- Live labels receive one additional `1.078` readability multiplier.
- Two hanging-lantern pools and one counter-lantern pool use bounded procedural
  `256 × 256` radial textures.
- Practical lights affect only receiver mask `2`, absolute z range `14–19`, and
  canvas layers `0–1`.
- Village lighting remains at z `10`; weather remains at z `20`.
- Lantern cores/halos, stockpot steam, roof rain, and buttons are excluded from
  the practical-light receiver mask.
- The pools have no shadows and no process loop.
- Pulse/flick coupling is deliberately deferred until the static device image
  is approved.

## A/B controls

Runtime API:

```gdscript
home_menu.set_foreground_relight_enabled(false)
home_menu.set_foreground_relight_enabled(true)
```

Capture the original checkpoint appearance by adding:

```text
--foreground-relight-off
```

## Validation

- Godot import/parse: pass.
- All `23/23` contract tests: pass.
- New relight contract verifies exact registration, gradient bounds, energies,
  z/layer/mask isolation, brighter buttons and labels, emissive exclusions, and
  reversible restoration.
- Forward Mobile / Metal deterministic A/B: pass.
- Personal-team iOS export, Xcode build, codesign verification, installation,
  and launch on Mauricio's iPhone 17 Pro Max: pass.

The visual was rendered from the existing approved assets. The earlier AI
lighting concept remains a design reference only and is not used by the game.
