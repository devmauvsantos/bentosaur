# Spine Runtime Desktop Pilot V001

**Date:** 2026-08-02
**Status:** desktop runtime gate passed; product integration not started

## Outcome

The official Spine runtime can animate a weighted skeletal character in the
Godot version family selected for Bentosaur. The successful pair is:

| Component | Validated version |
|---|---|
| Spine Runtimes | 4.3 stable |
| Runtime/sample commit | `4be2da7d25fdf046bddaf1633d6bde73e25cce81` |
| GDExtension build | Godot 4.7.1-stable |
| Godot | 4.7.0 and 4.7.1 stable |
| Desktop renderer | Metal 4.0 on Apple M5 |

The pinned `01-helloworld` sample imported all Spine atlas and skeleton
resources, played its animation, produced a two-second 60 FPS render, and held
the display's 145 FPS cap in a 600-frame headless playback run. The official
weighted Raptor lighting/walk scene also rendered and animated successfully
with Bentosaur's currently installed Godot 4.7.0.

This proves only the official runtime boundary. It does not yet prove the
approved Bentosaur art separation, mesh weights, deformation quality, crowd
cost under the village shaders, or physical-iPhone behavior.

## Failed unpinned sample and correction

The first attempt paired the published extension with the latest 4.3 branch
sample rather than the artifact's exact source commit. The first editor import
was incomplete and the sample returned a null animation state.

The artifact was traced to its official successful build at commit
`4be2da7d25fdf046bddaf1633d6bde73e25cce81`. The sample from that commit then
ran cleanly on both the installed Godot 4.7.0 and a temporary Godot 4.7.1.

The rule is to pin the runtime binary, sample/export schema, and Spine editor
minor version together. Godot 4.7.1 remains a sensible maintenance upgrade,
but it is not required to explain or fix the failed first attempt.

Validated official archive:

```text
URL: https://spine-godot.s3.eu-central-1.amazonaws.com/4.3/4.7.1-stable/spine-godot-extension-4.3-4.7.1-stable.zip
Size: 15,530,416 bytes
SHA-256: 0bfd296040d2a28bea9031df1edbd2591201ede54199335bf21e8f9d225b6cda
macOS: universal x86_64 + arm64 editor/debug/release frameworks
iOS: arm64 device debug/release frameworks; minimum iOS 12
```

Spine 4.4 is source-only today; no official 4.4 package has been published.

## Licensing gate

The Spine Trial license explicitly does not grant rights to integrate,
distribute, or otherwise use the Spine Runtimes in a product. Product
integration requires a valid Spine Editor license at the time of integration.

Therefore this pilot deliberately kept the runtime and sample outside the
Bentosaur repository. No third-party binary or sample asset was committed,
and no Bentosaur iOS build contains Spine.

The next implementation step requires Mau's purchase of Spine Professional;
Spine Essential lacks the weighted-mesh features required by the approved
pipeline.

This checkpoint records the observed restriction and is not legal advice. Read
the current official terms before purchase and distribution:

- [Spine Runtimes License](https://esotericsoftware.com/spine-runtimes-license)
- [Spine Editor License](https://esotericsoftware.com/spine-editor-license)

## Local evidence

Ignored local build artifacts:

```text
build/spine-evaluation/official-spineboy-godot-4.7.1-proof.png
build/spine-evaluation/official-spineboy-godot-4.7.1-proof.avi
build/spine-evaluation/official-raptor-godot-4.7.0-proof.png
build/spine-evaluation/official-raptor-godot-4.7.0-proof.avi
```

These are evidence only and must remain untracked because they depict the
official third-party sample.

## Isolated Bentosaur performance lab after licensing

The production Home menu remains untouched. Add a separate lab scene that
instances the existing registered stack:

```text
SpineRuntimePerformanceLab
├── WorldCanvas
│   ├── ApprovedStallComposition   # existing home_menu_stall_lab.tscn
│   └── SpineActorField            # beneath rain, within anime transfer
├── Anime90sPostProcess
└── BenchmarkHUD                   # above filter
```

Use the official weighted raptor sample before the Bentosaur authoring work.
Spawn 0, 1, 10, and 20 instances from one shared skeleton data resource. Warm
each tier for ten seconds, sample for thirty seconds, then soak 20 instances
for eight minutes.

Record mean, p50, p95, p99 and maximum frame delta; FPS; process time; draw
calls; primitives; rendered objects; texture/video/static memory; device;
viewport; engine version; build type; and actor count. Performance thresholds
belong to a rendered release/device test, not a headless contract.

Pass requirements:

- 1 and 10 live rigs sustain the 60 FPS / 16.67 ms production baseline;
- 20 rigs do not crash, leak, corrupt slots, or break the anime filter;
- rain renders above actors and the anime filter remains fixed for eight
  minutes;
- slot orientation, alpha edges, animation mixing, and shared-resource reuse
  are correct;
- if a crowd is too expensive, foreground actors remain live and background
  walkers bake to sprite sheets from the same Spine source.

## Physical-iPhone gate

Personal signing is already valid:

- Apple team `53RJ43876F`;
- bundle `com.mauvsantos.bentosaur` for production;
- certificate `Apple Development: Mauricio Vargas (CRAZV8U43J)`;
- personal provisioning profile valid through 2027-06-15.

The target iPhone 17 Pro Max is paired and Developer Mode is enabled, but it was
offline during this checkpoint. It must be unlocked and connected by USB or
available on the same network before install and profiling.

After licensing, run the lab under a temporary pilot bundle, verify the actual
app signature and entitlements, install through `devicectl`, and profile the
0/1/10/20 tiers with Xcode's Game Performance, Game Memory, Metal System Trace,
and Time Profiler instruments.

## Decision

Spine remains the recommended authoring/runtime pipeline. The runtime gate is
technically positive, but buying Spine Professional and connecting the phone
are required before the next product-integrated checkpoint.
