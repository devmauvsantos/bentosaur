# First Playable v1 Runtime Capture

Captured from Godot 4.7-stable on 2026-07-30 using the Mobile renderer at the
540×960 window override backed by the 720×1280 portrait viewport.

`home-service-summary.png` shows the live Home, Service, and perfect-shift
Summary states. Dynamic counters, order text, progress, bento slots, ingredient
hit states, buttons, and results are Godot controls. The surrounding concept
art is temporary flattened visual scaffolding.

SHA-256:

```text
515e28f388a01f0898d0e5732c80ea5906679dec12750fcdfcb2d3f96bd78275  home-service-summary.png
```

The Service and Summary capture states can be reproduced with:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --write-movie /absolute/output/frame.png \
  --fixed-fps 30 \
  --quit-after 2 \
  --disable-vsync \
  -- \
  --capture-service
```

Replace the final argument with `--capture-summary` for a deterministic perfect
shift. Capture flags do not write save progress.
