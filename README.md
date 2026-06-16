# sound-effects

Procedurally synthesized **"paste from clipboard"** UI sound effects. Every sound is
generated from scratch in pure Python (standard library only — no numpy, no samples,
no external audio) and rendered to 44.1 kHz mono WAV, plus an MP3 copy.

All sounds are short (~0.35–0.55 s), royalty-free, and built by hand from sine/square
oscillators, envelopes and a deterministic noise generator.

## Sounds

The original `paste.*` is a layered click + pop-in + thump. Plus 11 styled variants:

| File | Style | Duration |
|------|-------|----------|
| `paste`              | Layered click + pop-in + low thump (the default) | 0.50 s |
| `paste_01_bubble`    | Soft bubble pop — friendly, water-droplet-ish     | 0.45 s |
| `paste_02_mechkey`   | Mechanical keyboard click — snappy two-stage clack | 0.40 s |
| `paste_03_scifi`     | Sci-fi teleport-in — bright, digital materialize  | 0.50 s |
| `paste_04_8bit`      | Retro 8-bit blip — square-wave arpeggio           | 0.35 s |
| `paste_05_thunk`     | Deep UI thunk — weighty, premium drop-in          | 0.50 s |
| `paste_06_whoosh`    | Whoosh + snap — air swipe landing on a click      | 0.45 s |
| `paste_07_marimba`   | Glassy marimba ping — musical two-note tonk (E5→B5) | 0.55 s |
| `paste_08_databurst` | Modem / data-burst — glitchy digital paste        | 0.50 s |
| `paste_09_tape`      | Analog "tape" stick — warm noise swell + thud     | 0.50 s |
| `paste_10_doubletick`| Bright double-tick — crisp modern confirm         | 0.40 s |

Each entry has a `.wav` (lossless) and a `.mp3` (compressed) version.

## Regenerate / customize

No dependencies — just Python 3.

```bash
python3 make_paste.py            # regenerates paste.wav
python3 make_paste_variants.py   # regenerates paste_01..10.wav
```

To create the MP3 copies (requires `ffmpeg`):

```bash
for f in *.wav; do
  ffmpeg -y -i "$f" -codec:a libmp3lame -qscale:a 4 "${f%.wav}.mp3"
done
```

Tweak pitch, duration, decay or click sharpness directly in the generator scripts —
each sound is a small, self-contained function.

## License

MIT
