"""
synth.core — a tiny, dependency-free audio synthesis toolkit.

Everything is built from sine/square/saw/triangle oscillators, envelopes and a
deterministic noise source, mixed into a float buffer and written to 44.1 kHz
mono 16-bit WAV. No numpy, no samples, no external audio libraries.

Frequencies may be a constant or a callable f(t) -> Hz for glides/sweeps.
"""
import math
import wave
import struct

SR = 44100  # sample rate (Hz)


# --------------------------------------------------------------------------- #
# Deterministic noise (seeded LCG) — reproducible builds across machines.
# --------------------------------------------------------------------------- #
class Noise:
    def __init__(self, seed=12345):
        self._s = seed & 0x7FFFFFFF

    def __call__(self):
        self._s = (self._s * 1103515245 + 12345) & 0x7FFFFFFF
        return (self._s / 0x3FFFFFFF) - 1.0


# --------------------------------------------------------------------------- #
# Envelopes — all return a function e(t_seconds) -> gain in [0, 1].
# --------------------------------------------------------------------------- #
def perc(decay=10.0):
    """Percussive exponential decay. Higher `decay` = snappier."""
    return lambda t: math.exp(-decay * t)


def ad(attack, decay):
    """Linear attack then exponential decay (seconds)."""
    def e(t):
        if t < attack:
            return t / attack if attack > 0 else 1.0
        return math.exp(-(t - attack) / decay) if decay > 0 else 0.0
    return e


def adsr(a, d, s, r, dur):
    """Classic ADSR over a note of length `dur` seconds; sustain level `s`."""
    rel_start = max(0.0, dur - r)

    def e(t):
        if t < a:
            return t / a if a > 0 else 1.0
        if t < a + d:
            return 1.0 - (1.0 - s) * ((t - a) / d) if d > 0 else s
        if t < rel_start:
            return s
        if t < dur:
            return s * (1.0 - (t - rel_start) / r) if r > 0 else 0.0
        return 0.0
    return e


def bell(dur):
    """Smooth half-sine swell, peaks in the middle. Good for whooshes."""
    return lambda t: math.sin(math.pi * max(0.0, min(1.0, t / dur)))


# --------------------------------------------------------------------------- #
# Oscillators — return a list of float samples of length dur*SR.
# `freq` is a constant Hz or a callable f(t)->Hz.
# --------------------------------------------------------------------------- #
def _freq_at(freq, t):
    return freq(t) if callable(freq) else freq


def osc(shape, freq, dur, env=None, phase=0.0):
    n = int(dur * SR)
    out = [0.0] * n
    ph = phase
    for i in range(n):
        t = i / SR
        f = _freq_at(freq, t)
        ph += 2 * math.pi * f / SR
        if shape == "sine":
            v = math.sin(ph)
        elif shape == "square":
            v = 1.0 if math.sin(ph) >= 0 else -1.0
        elif shape == "saw":
            v = (ph / math.pi) % 2 - 1.0
        elif shape == "triangle":
            v = 2 / math.pi * math.asin(math.sin(ph))
        else:
            raise ValueError("unknown shape: %s" % shape)
        out[i] = v * (env(t) if env else 1.0)
    return out


def sine(freq, dur, env=None):
    return osc("sine", freq, dur, env)


def square(freq, dur, env=None):
    return osc("square", freq, dur, env)


def saw(freq, dur, env=None):
    return osc("saw", freq, dur, env)


def triangle(freq, dur, env=None):
    return osc("triangle", freq, dur, env)


def pluck(freq, dur, damp=0.5, decay=0.996, pick=1.0, env=None, noise=None):
    """Karplus-Strong plucked string — a noise burst circulating through a
    damped delay line. Sounds like a real plucked string, not like a filtered
    saw, because the physics are the same: a wave travelling a fixed length.

    `damp` 0..1  how fast the highs die away (0 = glassy, 1 = dull thud)

    The damper is a two-point average whose loss at Nyquist is |1 - 2a|, so its
    strength peaks at a = 0.5 and falls back to nothing at a = 1. Feeding `damp`
    straight in would therefore be non-monotonic — 0.85 would ring LONGER than
    0.5 — so it is mapped onto the useful half of the range.
    `decay` <1   overall sustain of the string
    `pick` 0..1  brightness of the pluck itself (1 = hard plectrum, 0.2 = thumb)

    `freq` may be a callable f(t)->Hz: the delay line is re-read every sample,
    so bends, slides and string vibrato all work.
    """
    n = int(dur * SR)
    if n <= 0:
        return []
    dq = 0.5 * max(0.0, min(1.0, damp))                  # monotonic damping
    f_min = min(_freq_at(freq, 0.0), _freq_at(freq, dur)) if callable(freq) else freq
    size = int(SR / max(20.0, f_min * 0.5)) + 4          # room for the lowest pitch
    line = [0.0] * size
    src = noise or Noise(9631)

    # Excite the stretch of line the first read will touch.
    d0 = max(2.0, SR / _freq_at(freq, 0.0) - dq)
    lp = 0.0
    for k in range(int(d0) + 1):
        x = src()
        lp = lp * (1.0 - pick) + x * pick                # duller pick = softer attack
        line[k] = lp

    out = [0.0] * n
    w = int(d0) + 1                                      # write head sits past the burst
    prev = 0.0
    for i in range(n):
        t = i / SR
        d = max(2.0, SR / _freq_at(freq, t) - dq)        # dq = the damper's own delay
        r = (w - d) % size
        i0 = int(r)
        frac = r - i0
        a = line[i0]
        v = a + frac * (line[(i0 + 1) % size] - a)       # fractional read = in tune
        out[i] = v * (env(t) if env else 1.0)
        line[w] = decay * ((1.0 - dq) * v + dq * prev)
        prev = v
        w = (w + 1) % size
    return out


def fm(freq, dur, ratio=1.0, index=2.0, env=None, mod_env=None, phase=0.0):
    """Two-operator FM (phase modulation) — one sine bending another's phase.

    This is how an electric piano, a bell and a marimba are actually made:
    integer `ratio` gives harmonic timbres (1 = reedy, 2 = hollow, 3-4 = woody),
    non-integer gives inharmonic bells. `index` is the modulation depth; a
    `mod_env` that decays makes the tone bright on the attack and mellow after
    — the single most recognisable "struck tine" cue.
    """
    n = int(dur * SR)
    out = [0.0] * n
    cph = phase
    mph = 0.0
    for i in range(n):
        t = i / SR
        f = _freq_at(freq, t)
        cph += 2 * math.pi * f / SR
        mph += 2 * math.pi * f * ratio / SR
        depth = index * (mod_env(t) if mod_env else 1.0)
        out[i] = math.sin(cph + depth * math.sin(mph)) * (env(t) if env else 1.0)
    return out


def noise_burst(dur, env=None, color=0.0, noise=None):
    """White-ish noise. `color` in [0,1] applies a one-pole low-pass (warmer)."""
    n = int(dur * SR)
    out = [0.0] * n
    src = noise or Noise()
    lp = 0.0
    a = color
    for i in range(n):
        t = i / SR
        x = src()
        lp = lp * a + x * (1 - a)
        out[i] = lp * (env(t) if env else 1.0)
    return out


# --------------------------------------------------------------------------- #
# Mixing & shaping
# --------------------------------------------------------------------------- #
def mix(target, src, at=0.0, gain=1.0):
    """Add `src` into `target` starting at `at` seconds (target may grow)."""
    start = int(at * SR)
    need = start + len(src)
    if need > len(target):
        target.extend([0.0] * (need - len(target)))
    for i, v in enumerate(src):
        target[start + i] += v * gain
    return target


def silence(dur):
    return [0.0] * int(dur * SR)


def ring_mod(samples, freq, depth=1.0):
    """Multiply by a sine — metallic/digital shimmer."""
    out = [0.0] * len(samples)
    for i, v in enumerate(samples):
        t = i / SR
        m = (1 - depth) + depth * math.sin(2 * math.pi * freq * t)
        out[i] = v * m
    return out


def lowpass(samples, cutoff):
    """One-pole RC low-pass. `cutoff` in Hz (constant or callable f(t)->Hz)."""
    out = [0.0] * len(samples)
    dt = 1.0 / SR
    y = 0.0
    for i, x in enumerate(samples):
        fc = cutoff(i / SR) if callable(cutoff) else cutoff
        rc = 1.0 / (2 * math.pi * max(1.0, fc))
        a = dt / (rc + dt)
        y += a * (x - y)
        out[i] = y
    return out


def highpass(samples, cutoff):
    """One-pole RC high-pass. `cutoff` in Hz (constant or callable f(t)->Hz)."""
    out = [0.0] * len(samples)
    dt = 1.0 / SR
    prev_x = 0.0
    prev_y = 0.0
    for i, x in enumerate(samples):
        fc = cutoff(i / SR) if callable(cutoff) else cutoff
        rc = 1.0 / (2 * math.pi * max(1.0, fc))
        a = rc / (rc + dt)
        y = a * (prev_y + x - prev_x)
        out[i] = y
        prev_x = x
        prev_y = y
    return out


def drive(samples, amount=2.0):
    """Soft tanh saturation — fattens kicks, basses and stabs."""
    return [math.tanh(amount * s) for s in samples]


def reverse(samples):
    """Reverse a buffer — for reverse cymbals, swooshes, suck-ins."""
    return list(samples)[::-1]


# --------------------------------------------------------------------------- #
# Musical pitch helpers — turn note names into frequencies for melodic samples.
# --------------------------------------------------------------------------- #
_SEMITONE = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def note(name):
    """Note name -> Hz, scientific pitch (A4 = 440). e.g. note('C2'), note('F#3')."""
    name = name.strip()
    letter = name[0].lower()
    if letter not in _SEMITONE:
        raise ValueError("bad note: %s" % name)
    semi = _SEMITONE[letter]
    i = 1
    while i < len(name) and name[i] in "#b":
        semi += 1 if name[i] == "#" else -1
        i += 1
    octave = int(name[i:])
    midi = semi + (octave + 1) * 12  # C-1 = midi 0, C4 = 60
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def vibrato(freq, rate=5.5, depth=0.006, onset=0.0):
    """Wrap a pitch in vibrato -> f(t). `depth` is a fraction of the pitch.

    `onset` seconds of straight tone before the wobble fades in, the way a
    player leans into a held note; without it sustained instruments sound
    mechanical from the very first sample.
    """
    base = note(freq) if isinstance(freq, str) else freq

    def f(t):
        f0 = base(t) if callable(base) else base
        grow = 1.0 if onset <= 0 else min(1.0, t / onset)
        return f0 * (1.0 + depth * grow * math.sin(2 * math.pi * rate * t))
    return f


def chord(root, intervals):
    """List of Hz from a root note name and semitone offsets, e.g. (0,4,7)."""
    base = note(root) if isinstance(root, str) else float(root)
    return [base * 2 ** (i / 12.0) for i in intervals]


def fade_in(samples, ms=10):
    f = min(int(ms / 1000 * SR), len(samples))
    for k in range(f):
        samples[k] *= k / f
    return samples


def fade_out(samples, ms=40):
    f = min(int(ms / 1000 * SR), len(samples))
    n = len(samples)
    for k in range(f):
        samples[n - 1 - k] *= k / f
    return samples


def normalize(samples, peak=0.9):
    p = max(1e-9, max(abs(s) for s in samples))
    g = peak / p
    return [s * g for s in samples]


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def write_wav(path, samples, do_normalize=True, peak=0.9, fade=30):
    s = list(samples)
    if fade:
        fade_out(s, fade)
    if do_normalize:
        s = normalize(s, peak)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for v in s:
            iv = int(max(-1.0, min(1.0, v)) * 32767)
            frames += struct.pack("<h", iv)
        w.writeframes(bytes(frames))
    return len(s) / SR
