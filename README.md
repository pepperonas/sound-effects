<div align="center">

# 🔊 sound-effects

**Procedurally synthesized UI sound effects *and* music-production samples — generated from scratch in pure Python.**

[![Made with Python](https://img.shields.io/badge/Made%20with-Python%203-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![No dependencies](https://img.shields.io/badge/dependencies-none-success)](#requirements)
[![Stdlib only](https://img.shields.io/badge/stdlib-only-informational)](synth/core.py)
[![Sounds](https://img.shields.io/badge/sounds-128-ff69b4)](output/)
[![Categories](https://img.shields.io/badge/categories-15-blueviolet)](#-categories)
[![Format WAV](https://img.shields.io/badge/format-WAV%2044.1kHz-orange)](#output-layout)
[![MP3 optional](https://img.shields.io/badge/MP3-optional-lightgrey)](#output-layout)
[![Royalty free](https://img.shields.io/badge/royalty-free-brightgreen)](#-license)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Reproducible](https://img.shields.io/badge/builds-reproducible-9cf)](#how-it-works)
[![Platform](https://img.shields.io/badge/platform-cross--platform-lightgrey)](#requirements)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-adding-your-own-sounds)
[![Maintained](https://img.shields.io/badge/maintained-yes-success)](https://github.com/pepperonas/sound-effects)

</div>

---

Every sound is built by hand from **sine / square / saw / triangle oscillators**, envelopes
and a deterministic noise source — then mixed into a float buffer and rendered to
**44.1 kHz mono WAV** (plus an MP3 copy). No samples, no numpy, no external audio engine.
Because the noise source is seeded, **builds are bit-for-bit reproducible** on any machine.

```bash
python3 build.py          # → output/<category>/<name>.{wav,mp3} + manifest.json
```

## ✨ Highlights

- 🧰 **128 ready-to-use sounds** across **15 categories** — UI interactions **and** music-production samples
- 🎹 **FL-Studio-style sample kit** — drums, basses, synth tones, chord stabs and production FX, tuned to musical notes
- 🐍 **Pure Python standard library** — clone and run, nothing to install
- 🗂️ **Sorted output** — one folder per category + a machine-readable `manifest.json`
- ♻️ **Reproducible** — seeded noise means identical output everywhere
- 🎛️ **Hackable** — every sound is a tiny self-contained function; tweak pitch, length, decay
- 🪶 **Tiny** — the whole synth engine is one ~200-line file with zero dependencies

## 📁 Categories

### 🖥️ UI & interface

| Category | What's in it | Sounds |
|----------|--------------|:------:|
| 📋 **clipboard** | copy, cut & the signature *paste* family | 6 |
| 🖱️ **clicks** | buttons, taps, toggles, switches | 7 |
| 🔔 **notifications** | pings, chimes, message & alert tones | 6 |
| ✅ **status** | success, error, warning, completion | 7 |
| 🪟 **ui** | open, close, hover, swipe, expand, popover | 8 |
| ⚙️ **system** | startup, shutdown, connect, login, power | 8 |
| ⌨️ **typing** | keystrokes, backspace, space, enter | 7 |
| 💬 **messaging** | send, receive, delivered, typing, call tones | 6 |
| ⏯️ **media** | play, pause, stop, skip, volume, record, screenshot | 10 |
| 🎮 **game** | coin, powerup, jump, level-up, achievement, game-over | 10 |

### 🎹 Music production (FL-Studio-style sample kit)

| Category | What's in it | Sounds |
|----------|--------------|:------:|
| 🥁 **drums** | kicks, 808s, snares, claps, hats, toms, cymbals, percs | 17 |
| 🎸 **bass** | 808, sub, reese, saw/square, pluck, wobble, FM — tuned to notes | 8 |
| 🎛️ **synth** | plucks, stabs, leads, keys, bells, organ, pad, arp | 9 |
| 🎵 **chords** | major / minor / 7th / sus / power stabs + pads, rooted on C | 9 |
| 💥 **fx** | risers, downlifters, impacts, sweeps, reverse cymbal, vinyl | 10 |

> See the full annotated list any time with `python3 build.py --list`.

### A taste of what's inside

**clipboard** · `paste` · `paste_bubble` · `paste_mechkey` · `paste_scifi` · `copy` · `cut`
**status** · `success` · `success_short` · `error_buzz` · `error_descend` · `warning_pulse` · `complete` · `denied`
**system** · `startup` · `shutdown` · `connect` · `disconnect` · `login` · `logout` · `battery_low` · `usb_plug`
**media** · `play` · `pause` · `stop` · `next_track` · `prev_track` · `volume_up` · `volume_down` · `mute` · `record` · `screenshot`
**game** · `coin` · `powerup` · `jump` · `hurt` · `level_up` · `achievement` · `game_over` · `select` · `laser` · `explosion`
**drums** · `kick` · `kick_808` · `kick_sub` · `snare` · `snare_rim` · `clap` · `hat_closed` · `hat_open` · `tom_low/mid/high` · `crash` · `ride` · `cowbell` · `shaker` · `snap` · `rimshot`
**bass** · `bass_808` · `sub_bass` · `saw_bass` · `square_bass` · `reese` · `pluck_bass` · `wobble_bass` · `fm_bass`
**synth** · `pluck` · `stab` · `lead` · `key` · `bell_tone` · `organ` · `pad` · `arp_blip` · `saw_lead_oct`
**chords** · `major` · `minor` · `maj7` · `min7` · `dom7` · `sus4` · `power` · `major_pad` · `minor_pad`
**fx** · `riser` · `downlifter` · `impact` · `sub_drop` · `sweep_up` · `sweep_down` · `reverse_cymbal` · `white_riser` · `vinyl_crackle` · `laser_zap`

## 🚀 Usage

```bash
python3 build.py                       # build everything (WAV only)
python3 build.py --list                # list every group, category & sound, generate nothing
python3 build.py -g music              # only one use case (interface | music)
python3 build.py -c clicks ui          # build only specific categories
python3 build.py -c drums bass synth   # just part of the music-production kit
python3 build.py --mp3                 # also encode an MP3 copy (needs ffmpeg)
```

Preview a sound (macOS `afplay`, Linux `aplay`/`ffplay`):

```bash
afplay output/interface/clipboard/paste.wav
aplay  output/music/drums/kick_808.wav
```

### Output layout

Sounds are split by use case into two top-level groups:

```
output/
├── interface/                 ← computer & UI interaction sounds
│   ├── clipboard/
│   │   ├── paste.wav
│   │   └── …
│   ├── clicks/
│   ├── notifications/
│   ├── status/ ui/ system/ typing/ messaging/ media/ game/
│   └── …
├── music/                     ← FL-Studio-style production samples
│   ├── drums/
│   │   ├── kick_808.wav
│   │   └── …
│   ├── bass/ synth/ chords/ fx/
│   └── …
└── manifest.json              ← machine-readable index of every sound
```

`manifest.json` is organized by group → category → sound, listing each sound's name,
description, duration and file path — handy for wiring the sounds into an app, a
design system, a sample browser or a sound picker.

## 🧠 How it works

The whole engine lives in [`synth/core.py`](synth/core.py):

- **Oscillators** — `sine`, `square`, `saw`, `triangle`; frequency can be a constant
  *or a function of time* for glides and sweeps.
- **Envelopes** — `perc` (percussive decay), `ad`, `adsr`, `bell`.
- **Filters & shaping** — `lowpass`, `highpass` (Hz cutoff, constant or `f(t)`),
  `drive` (soft saturation), `ring_mod`, `reverse`, `noise_burst`, `fade_in/out`, `normalize`.
- **Musical pitch** — `note('C2')` → Hz and `chord('C3', (0, 4, 7))` → frequency list,
  so melodic samples land on real notes.
- **Mixing** — `mix(target, src, at=seconds, gain=…)` layers voices into a buffer.
- **Output** — `write_wav()` normalizes, fades the tail and writes 16-bit PCM.

A sound is just a function returning a sample buffer, e.g.:

```python
def popup():
    """Bouncy popover pop."""
    f = lambda t: 600 + 500 * (1 - math.exp(-70 * t))   # quick upward glide
    s = sine(f, 0.16, perc(20))
    mix(s, sine(lambda t: 2 * f(t), 0.16, perc(28)), 0.0, 0.2)
    return s
```

## ➕ Adding your own sounds

1. Open the matching module in [`generators/`](generators/) (or create a new one).
2. A new generator module just needs a few things:

   ```python
   from synth import sine, mix, silence, perc

   CATEGORY = "my_category"
   GROUP = "interface"        # "interface" or "music" — which use case it belongs to
   DESCRIPTION = "What this family of sounds is for."

   def my_sound():
       return sine(880, 0.2, perc(10))

   SOUNDS = [
       ("my_sound", "Short description", my_sound),
   ]
   ```
3. Run `python3 build.py` — it's auto-discovered, sorted into
   `output/<group>/my_category/` and added to the manifest. No registration needed.

## 🗂️ Project structure

```
sound-effects/
├── build.py            # orchestrator: discovers generators, sorts output, writes manifest
├── synth/
│   ├── core.py         # the dependency-free synthesis toolkit
│   └── __init__.py
├── generators/         # one module per sound category (each declares GROUP)
│   ├── clipboard.py     ┐
│   ├── clicks.py        │
│   ├── notifications.py │
│   ├── status.py        │
│   ├── ui.py            │ GROUP = "interface"
│   ├── system.py        │
│   ├── typing.py        │
│   ├── messaging.py     │
│   ├── media.py         │
│   ├── game.py          ┘
│   ├── drums.py         ┐
│   ├── bass.py          │
│   ├── synthtones.py    │ GROUP = "music"  (synthtones → CATEGORY "synth")
│   ├── chords.py        │
│   └── fx.py            ┘
└── output/             # generated WAVs: output/<group>/<category>/ (+ manifest.json)
```

## 🧩 Requirements

- **Python 3** — standard library only (tested on 3.11–3.14). Builds WAV out of the box.
- **ffmpeg** *(optional)* — only needed for the opt-in `--mp3` flag. Without it,
  `--mp3` falls back to WAV-only automatically.

## 📄 License

[MIT](LICENSE) — free to use, modify and ship in commercial and personal projects.
The sounds are generated by this code, so they're **royalty-free**: use them anywhere.
