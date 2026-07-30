# Bentosaur Godot Project

Engine contract: Godot 4.7.1 Standard, typed GDScript, Mobile renderer.

The current main scene is the temporary facial-animation options lab. It loads
the frozen r002 facial proof and exposes:

- hybrid, morph-only, and bone-only mouth modes;
- continuous mouth opening;
- happy eyes;
- independent blinks;
- a chew loop;
- deterministic automatic demo states.

The lab validates runtime orchestration. It does not promote the layered proof
to final character art. The automated r002 contract passes, but the human
visual gate fails: the tongue is still not correctly seated inside a real
mouth cavity. See `docs/runtime-captures/v002/` and the experiment README.

Run:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path game
```

Validate headlessly:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --import \
  --quit

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/facial_rig_contract_test.gd
```

Capture a fixed fully-open comparison pose:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  --write-movie /absolute/output/frame.png \
  --fixed-fps 30 \
  --quit-after 10 \
  --disable-vsync \
  -- \
  --capture-mouth-mode=hybrid
```

Accepted values are `morph`, `bone`, and `hybrid`. Add `--capture-happy` for
the happy-eye state.

The installed local editor currently reports `4.7-stable`; the locked
production patch is `4.7.1`. This proof may be inspected with the installed
editor, but the patch mismatch must be resolved before a production gate.
