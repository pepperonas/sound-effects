<div align="center">

# 🔊 sound-effects

**Procedurally synthesized UI sound effects for computer interfaces — generated from scratch in pure Python.**

[![Made with Python](https://img.shields.io/badge/Made%20with-Python%203-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![No dependencies](https://img.shields.io/badge/dependencies-none-success)](#requirements)
[![Stdlib only](https://img.shields.io/badge/stdlib-only-informational)](synth/core.py)
[![Sounds](https://img.shields.io/badge/sounds-55-ff69b4)](output/)
[![Categories](https://img.shields.io/badge/categories-8-blueviolet)](#-categories)
[![Format WAV](https://img.shields.io/badge/format-WAV%2044.1kHz-orange)](#output-layout)
[![Format MP3](https://img.shields.io/badge/format-MP3-orange)](#output-layout)
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

- 🧰 **55 ready-to-use sounds** across **8 categories** of computer interactions
- 🐍 **Pure Python standard library** — clone and run, nothing to install
- 🗂️ **Sorted output** — one folder per category + a machine-readable `manifest.json`
- ♻️ **Reproducible** — seeded noise means identical output everywhere
- 🎛️ **Hackable** — every sound is a tiny self-contained function; tweak pitch, length, decay
- 🪶 **Tiny** — the whole synth engine is one ~200-line file with zero dependencies

## 📁 Categories

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

> See the full annotated list any time with `python3 build.py --list`.

### A taste of what's inside

**clipboard** · `paste` · `paste_bubble` · `paste_mechkey` · `paste_scifi` · `copy` · `cut`
**status** · `success` · `success_short` · `error_buzz` · `error_descend` · `warning_pulse` · `complete` · `denied`
**system** · `startup` · `shutdown` · `connect` · `disconnect` · `login` · `logout` · `battery_low` · `usb_plug`
**notifications** · `ping` · `chime_two_note` · `chime_three_note` · `message_pop` · `alert_attention` · `bell_soft`

## 🚀 Usage

```bash
python3 build.py                 # build everything (WAV + MP3 if ffmpeg is present)
python3 build.py --list          # list every category & sound, generate nothing
python3 build.py -c clicks ui    # build only specific categories
python3 build.py --no-mp3        # WAV only, skip MP3 encoding
```

Preview a sound (macOS `afplay`, Linux `aplay`/`ffplay`):

```bash
afplay output/clipboard/paste.wav
aplay  output/status/success.wav
```

### Output layout

```
output/
├── clipboard/
│   ├── paste.wav
│   ├── paste.mp3
│   └── …
├── clicks/
├── notifications/
├── status/
├── ui/
├── system/
├── typing/
├── messaging/
└── manifest.json      ← machine-readable index of every sound
```

`manifest.json` lists each sound's name, description, duration and file paths — handy
for wiring the sounds into an app, a design system or a sound picker.

## 🧠 How it works

The whole engine lives in [`synth/core.py`](synth/core.py):

- **Oscillators** — `sine`, `square`, `saw`, `triangle`; frequency can be a constant
  *or a function of time* for glides and sweeps.
- **Envelopes** — `perc` (percussive decay), `ad`, `adsr`, `bell`.
- **Effects** — `ring_mod`, `noise_burst`, `fade_in/out`, `normalize`.
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
2. A new generator module just needs three things:

   ```python
   from synth import sine, mix, silence, perc

   CATEGORY = "my_category"
   DESCRIPTION = "What this family of sounds is for."

   def my_sound():
       return sine(880, 0.2, perc(10))

   SOUNDS = [
       ("my_sound", "Short description", my_sound),
   ]
   ```
3. Run `python3 build.py` — it's auto-discovered, sorted into `output/my_category/`
   and added to the manifest. No registration needed.

## 🗂️ Project structure

```
sound-effects/
├── build.py            # orchestrator: discovers generators, sorts output, writes manifest
├── synth/
│   ├── core.py         # the dependency-free synthesis toolkit
│   └── __init__.py
├── generators/         # one module per sound category
│   ├── clipboard.py
│   ├── clicks.py
│   ├── notifications.py
│   ├── status.py
│   ├── ui.py
│   ├── system.py
│   ├── typing.py
│   └── messaging.py
└── output/             # generated sounds, sorted by category (+ manifest.json)
```

## 🧩 Requirements

- **Python 3** — standard library only (tested on 3.11–3.14).
- **ffmpeg** *(optional)* — only needed for MP3 encoding. Without it, `build.py`
  falls back to WAV-only automatically.

## 📄 License

[MIT](LICENSE) — free to use, modify and ship in commercial and personal projects.
The sounds are generated by this code, so they're **royalty-free**: use them anywhere.
