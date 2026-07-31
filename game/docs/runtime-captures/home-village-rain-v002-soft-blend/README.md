# Home Village Rain V002 — Soft-Blend Checkpoint

Captured from the isolated Godot lab scene on 2026-07-31.

- Engine: Godot 4.7 stable
- Renderer: Forward Mobile / Metal
- Logical canvas: 720 × 1280 portrait
- Review capture: 540 × 960 window override
- Fixed capture rate: 30 FPS
- Fixed particle seeds: enabled for reproducible review
- Scene: `res://scenes/labs/home_village_rain_lab.tscn`
- State: full rain density, registered lights awake
- Opening contract: rain present from frame one; only lighting fades in
- Blend contract: normal alpha, cool scene-derived tint, 23% back rain,
  37% front rain, 50% splash tint alpha

Files:

- `home-village-rain-v002-soft-blend-checkpoint.png`: representative settled
  frame
- `home-village-rain-v002-soft-blend-motion.gif`: compact review loop
- `home-village-rain-v002-soft-blend-motion.mp4`: full-quality motion
  checkpoint

Mau approved the overall Home Village rain result as a major visual
checkpoint. V002 applies the requested final restraint pass so streaks sit
inside the night palette instead of reading as bright white overlays.

This approves the composition and motion direction. It is not yet the physical
iPhone performance gate or the production ultratall environment master.
