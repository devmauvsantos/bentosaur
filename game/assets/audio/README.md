# Bentosaur Audio Sources

Status: runtime trial assets

Imported: 2026-07-31

The files in this directory are preserved byte-for-byte from the user-provided
downloads. Godot imports the MP3 sources directly; no normalized or transcoded
derivative is currently used.

## Music

File:

`music/late_night_radio_kevin_macleod.mp3`

Metadata:

- Title: `Late Night Radio`
- Artist: Kevin MacLeod
- ISRC: `USUAN2100003`
- Duration: 4:23.602
- Encoding: stereo MP3, 44.1 kHz, approximately 160 kb/s
- SHA-256:
  `d720ee8c55abceef59ff5778bd47bca80713e903bc49719960888a68f6d40ecd`

License and required attribution:

> “Late Night Radio” Kevin MacLeod (incompetech.com)<br>
> Licensed under Creative Commons: By Attribution 4.0 License<br>
> <https://creativecommons.org/licenses/by/4.0/>

Track page:
<https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN2100003>

## Rain ambience

File:

`ambience/gentle_rain_01_dragon_studio.mp3`

Metadata:

- Title: `Gentle Rain 01`
- Creator: DRAGON-STUDIO
- Pixabay asset: `437305`
- Duration: 10:00.024
- Encoding: stereo MP3, 48 kHz, 256 kb/s
- SHA-256:
  `eaca9330832a38ebcd85c90ad2fa45b1234272a660ed4ff0ba28fb094344887f`

License:

- Pixabay Content License
- Attribution is optional under the license; Bentosaur credits DRAGON-STUDIO
  anyway.
- Source:
  <https://pixabay.com/sound-effects/nature-gentle-rain-01-437305/>
- License summary: <https://pixabay.com/service/license-summary/>

## Runtime balance

The source tracks have very different measured loudness:

| Source | Integrated loudness | Runtime player gain |
|---|---:|---:|
| Late Night Radio | -13.18 LUFS | -19 dB |
| Gentle Rain 01 | -27.43 LUFS | -19 dB |

This intentionally keeps the rain as a quiet bed behind the radio instead of
letting the broad-band ambience dominate the village. Both channels were
lowered after the first physical iPhone 17 Pro Max listening pass. These gains
remain an in-engine listening balance, not the final mix.

On iOS, Godot's default `Ambient` audio-session category respects Silent Mode.
The first physical-device check therefore produced silence until Silent Mode
was disabled; both packaged streams and both runtime players were healthy.
