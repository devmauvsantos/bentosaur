# Bentosaur First Playable v1

Status: active implementation contract

Effective: 2026-07-30

## Purpose

Stop expanding the concept surface and test Bentosaur's smallest complete
mobile loop:

```text
home → open stall → serve three neighbors → shift result → home or replay
```

This build answers three questions before the project spends more time on
content:

1. Is assembling a requested three-part bento immediately understandable?
2. Does serving and pleasing a dinosaur feel emotionally rewarding?
3. Does a three-customer shift create a satisfying reason to replay?

The numbers in this document are slice constants, not the final economy.

## Included loop

The home screen uses the classic text-stall concept for immediate clarity.
Only `OPEN STALL` advances the build. The other visible destinations explain
that they are intentionally unavailable.

One shift contains three sequential orders. Each order:

1. shows one neighbor's requested ingredients from left to right;
2. lets the player tap four unlimited ingredient bins;
3. places the selections into three ordered bento compartments;
4. enables `SERVE BENTO` only when all compartments are filled;
5. keeps the same customer waiting after a mistake so the player can correct
   it without a timer, penalty, or dead end;
6. awards ten coins after the correct bento;
7. awards one shift star when the first submission was correct.

The fixed orders are data, not code:

| Visit | Order |
|---|---|
| Nori | rice → berry → leaf |
| Momo | leaf → tofu → rice |
| Kumo | berry → rice → tofu |

Coins persist locally through Godot's `user://` storage. A finished shift shows
neighbors served, first-try orders, shift coins, total coins, and zero to three
stars. The player can return home or replay immediately.

## Implementation boundaries

Runtime:

- Godot 4.7.x Standard;
- Mobile renderer;
- portrait 720×1280 reference viewport;
- typed GDScript;
- JSON-authored shift content;
- touch-sized Godot `Control` nodes;
- deterministic gameplay model independent of the screen art.

Temporary visual scaffolding:

- `game/assets/vertical_slice/home_classic_stall_v1.png`;
- `game/assets/vertical_slice/service_counter_flat_cel_v1.png`.

These are flattened generated concept screens with baked characters, UI,
weather, text, and props. They are useful for validating the loop in its
intended atmosphere, but they are not production backgrounds and must not
ship. All live counters, order text, bento slots, ingredient hit states,
buttons, feedback, and summary values are real Godot UI layered above them.

## Explicitly out of scope

- regulars book and page turning;
- pantry, stock, recipes, or inventory;
- decorating, stall upgrades, seasons, and weather selection;
- unique production art for three customers;
- walk-in, handoff, chewing, and departure animation;
- production cutout layers or frame animation;
- timers, lives, abandonment, or hard failure;
- final balancing, inflation, sinks, monetization, ads, or purchases;
- accounts, analytics, cloud saves, localization, and live operations;
- resuming the paused live-3D character pipeline.

## Acceptance gate

The slice passes its repository gate when:

- the project boots directly to Home;
- all three customers can be completed without a dead end;
- sequence validation, correction, first-try stars, coins, replay, and local
  saving behave deterministically;
- the model contract test passes headlessly;
- Home, Service, and Summary render without overflow at the portrait reference
  viewport;
- Mau plays it and decides the loop is clear enough to keep developing.

The next milestone after that approval is emotional payoff: replace the baked
counter customer with one registered front-facing character that idles,
blinks, receives the bento, chews, and delights. The book and progression do
not start before that serving reaction feels good.

## Run and validate

Run the game:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --path /Users/mauvsantos/Workspace/games/Bentosaur/game
```

Validate the gameplay model:

```sh
/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path /Users/mauvsantos/Workspace/games/Bentosaur/game \
  --script res://tests/bento_shift_session_test.gd

/Applications/Godot.app/Contents/MacOS/Godot \
  --headless \
  --path /Users/mauvsantos/Workspace/games/Bentosaur/game \
  --script res://tests/first_playable_ui_test.gd
```

The installed editor currently reports `4.7-stable`; the earlier production
lock names `4.7.1`. The slice may be developed with the installed editor, but
release/export gates must resolve that patch mismatch.
