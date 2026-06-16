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
