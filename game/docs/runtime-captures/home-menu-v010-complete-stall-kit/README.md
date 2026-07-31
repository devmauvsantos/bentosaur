# Home Menu V010 — Complete Stall Kit Runtime Evidence

**Status:** normal/reduced Metal evidence and personal install/launch complete;
founder physical-device review pending

**Checkpoint:**
[Home Menu V010 complete modular stall kit](../../../../docs/checkpoints/2026-07-31-home-menu-v010-complete-stall-kit.md)

This directory holds reproducible runtime evidence for the complete
founder-approved V004 stall attachment integration.

![Normal versus reduced motion](home-menu-v010-normal-vs-reduced-1080x960.png)

## Evidence checklist

- [x] Final complete Godot suite result and contract count.
- [x] Deterministic Forward Mobile / Metal capture.
- [x] Reduced-motion capture and endpoint contract evidence.
- [ ] Phone-scale review of attachment registration and control legibility.
- [x] Personally signed physical-iPhone install and launch.
- [ ] Founder approval or rejection note.

## Capture record

| Field | Evidence |
|---|---|
| Runtime capture file | `home-menu-v010-normal-540x960.png` |
| Reduced-motion file | `home-menu-v010-reduced-motion-540x960.png` |
| Comparison file | `home-menu-v010-normal-vs-reduced-1080x960.png` |
| Godot version | `4.7-stable` (`5b4e0cb0f`) |
| Renderer / graphics API | Forward Mobile / Metal; Apple M5 capture host |
| Capture command | Godot `--write-movie`, fixed 30 FPS, 60 frames, deterministic/audio-off; reduced run adds `--reduced-motion` |
| Logical canvas | `720 × 1280`, responsive `canvas_items` / `expand` contract |
| Output dimensions | `540 × 960` per frame |
| Frame count / duration | 60 frames / 2.0 seconds per mode |
| Full-suite result | 21/21 `game/tests/*_test.gd` contracts pass |
| Personal iOS export/build | Strictly verified: `Apple Development: Mauricio Vargas (CRAZV8U43J)`, team `53RJ43876F`, bundle `com.mauvsantos.bentosaur` |
| Physical device and OS | Installed and launched on Mauricio's iPhone 17 Pro Max (`iPhone18,2`), iOS `26.5.1` |
| Mau's decision | **PENDING phone-scale review** |

## Runtime acceptance targets

The capture must show:

- the stall and all attachments inheriting one uniform `StallStage` transform;
- stockpot body, separate lid, procedural steam, and contact shadow;
- counter lantern OFF shell plus independently lit core and halo;
- bowl, plant, modular bottle crate, bottles, and draped cloth;
- three-star rank fixture;
- live Lilita One labels on Open Stall, Guestbook, Decorations, and Pantry;
- the semantic settings control;
- rain, registered practical lights, and the anime post-process remaining
  edge-to-edge;
- no main character or destination-screen claim.

The physical-device pass must additionally confirm no aspect distortion,
black band, unsafe touch target, missing audio, shader coverage gap, or
company-account signing. Reduced motion must retain clear state endpoints while
removing nonessential ambient travel.

The captures show exact registered placement, live Lilita One labels, modular
crate/bottles, three practical lanterns, rain, and edge-to-edge anime transfer.
Soft translucent steam did not survive the mobile transfer, so the final
runtime supplements it with deterministic outlined curls. The effect remains
procedural, has no raster sheet or particles, and becomes a single static cue
under reduced motion.
