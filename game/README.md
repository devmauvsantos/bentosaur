# Bentosaur Godot Project

Engine contract: Godot 4.7.1 Standard, typed GDScript, Mobile renderer.

The current main scene is the layered Home Village menu:

`res://scenes/home/home_menu.tscn`

It currently proves:

- the registered rainy street and animated light wake-up;
- source-synchronized wet-pavement reflection breathing and flicks;
- the uniformly scaled V002 empty stall;
- the registered flat-cel Bentosaur proprietor proof with live breathing,
  randomized blinks, and a reduced-motion endpoint;
- the approved modular hanging lanterns with OFF/ON layers and restrained sway;
- the approved anime-transfer shader preset 3 with full-viewport lifecycle
  coverage repair;
- separate looping Music and Weather audio buses;
- aspect-cover presentation on ultratall iPhones.

The complete bounded gameplay loop remains available at:

`res://scenes/vertical_slice/first_playable.tscn`

That preserved slice implements:

- classic-stall Home;
- one three-customer shift;
- ordered three-ingredient bento assembly;
- correctable submissions with no dead end;
- ten coins per completed customer;
- one star per first-try order;
- local coin persistence;
- shift summary and immediate replay.

The flattened concept screens under `assets/vertical_slice/` are temporary
visual scaffolding, not shipping assets. The gameplay state, validation,
counters, controls, feedback, and persistence are real.

The older 3D facial-animation lab remains available at:

`res://scenes/labs/facial_animation_options_lab.tscn`

The isolated native-2D skeleton proof is available at:

`res://scenes/labs/bentosaur_skeleton_animation_lab.tscn`

Run it directly:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path game \
  res://scenes/labs/bentosaur_skeleton_animation_lab.tscn
```

The lab uses a real `Skeleton2D` with torso, head, and two arm `Bone2D`
pivots. Toggle **Bones** to reveal the rig, leave **Auto** enabled for quiet
randomized gestures, or trigger Nod, Look, Hands, Chew, and Delight manually.
The mouth actions intentionally demonstrate bone motion only until an authored
mouthless face plate and registered mouth swaps exist.

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
  --script res://tests/bento_shift_session_test.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/first_playable_ui_test.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/facial_rig_contract_test.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/home_village_rain_lab_test.gd \
  -- --deterministic-capture --audio-off

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/anime_post_process_coverage_test.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/bentosaur_proprietor_idle_test.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/bentosaur_skeleton_animation_lab_test.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/stall_lantern_fixture_test.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path game \
  --script res://tests/stall_foreground_relight_test.gd
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
production patch is `4.7.1`. This first playable may be developed with the
installed editor, but the patch mismatch must be resolved before a release
gate.
