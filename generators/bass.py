"""Bass — 808s, subs, reese, plucks and synth basses for the low end.

Tuned to musical notes (default key of C) so they sit in a track without
re-pitching. Layer an 808 under a kick, or sequence a pluck bass line.
"""
import math
from synth import (sine, saw, square, triangle, noise_burst, mix, silence,
                   perc, ad, adsr, lowpass, highpass, drive, note)

CATEGORY = "bass"
GROUP = "music"
DESCRIPTION = "808s, sub, reese, pluck and synth basses, tuned to musical notes."


def bass_808():
    """Tuned 808 — sine sub with a short pitch glide into C1, saturated."""
    f0 = note("C1")
    s = sine(lambda t: f0 * (1 + 1.2 * math.exp(-60 * t)), 0.9, perc(2.8))
    mix(s, noise_burst(0.003, perc(300), 0.0), 0.0, 0.2)
    return drive(s, 2.4)


def sub_bass():
    """Pure sub — clean sine at C1, sustained, no harmonics."""
    f0 = note("C1")
    return sine(f0, 0.7, adsr(0.01, 0.05, 0.85, 0.2, 0.7))


def saw_bass():
    """Saw bass — fat C2 saw through a low-pass, classic synth bass timbre."""
    f0 = note("C2")
    s = saw(f0, 0.5, adsr(0.006, 0.08, 0.7, 0.15, 0.5))
    mix(s, saw(f0 * 1.005, 0.5, adsr(0.006, 0.08, 0.7, 0.15, 0.5)), 0.0, 0.6)
    return drive(lowpass(s, 900), 1.4)


def square_bass():
    """Square bass — hollow, woody C2, good for funk and chiptune lines."""
    f0 = note("C2")
    s = square(f0, 0.4, adsr(0.005, 0.06, 0.7, 0.12, 0.4))
    return lowpass(s, 1400)


def reese():
    """Reese bass — detuned saws beating against each other (DnB/dubstep)."""
    f0 = note("C1") * 2  # C2-ish
    env = adsr(0.01, 0.1, 0.8, 0.2, 0.8)
    s = saw(f0, 0.8, env)
    mix(s, saw(f0 * 1.012, 0.8, env), 0.0, 0.9)
    mix(s, saw(f0 * 0.988, 0.8, env), 0.0, 0.9)
    return drive(lowpass(s, 1100), 1.8)


def pluck_bass():
    """Pluck bass — saw with a fast downward filter sweep, snappy and short."""
    f0 = note("C2")
    s = saw(f0, 0.3, perc(11))
    mix(s, saw(f0 * 1.004, 0.3, perc(11)), 0.0, 0.6)
    return lowpass(s, lambda t: 200 + 3000 * math.exp(-22 * t))


def wobble_bass():
    """Wobble bass — saw under a rhythmic low-pass + tremolo (dubstep-ish)."""
    f0 = note("C1") * 2
    env = adsr(0.01, 0.05, 0.9, 0.15, 0.9)
    s = saw(f0, 0.9, env)
    mix(s, saw(f0 * 1.01, 0.9, env), 0.0, 0.8)
    s = lowpass(s, lambda t: 500 + 2200 * (0.5 + 0.5 * math.sin(2 * math.pi * 6 * t)))
    # amplitude tremolo locked to the same LFO
    return [v * (0.55 + 0.45 * math.sin(2 * math.pi * 6 * (i / 44100)))
            for i, v in enumerate(drive(s, 1.6))]


def fm_bass():
    """FM-ish growl bass — sine carrier ring-shaped by a tracking modulator."""
    f0 = note("C2")
    env = adsr(0.005, 0.08, 0.75, 0.15, 0.5)
    car = sine(f0, 0.5, env)
    out = [0.0] * len(car)
    for i, v in enumerate(car):
        t = i / 44100
        m = 0.6 + 0.4 * math.sin(2 * math.pi * f0 * 2 * t)   # 2:1 ratio
        out[i] = v * m
    return drive(lowpass(out, 1600), 1.5)


SOUNDS = [
    ("bass_808",     "Tuned 808 sub with glide",        bass_808),
    ("sub_bass",     "Pure clean sine sub",             sub_bass),
    ("saw_bass",     "Fat low-passed saw bass",         saw_bass),
    ("square_bass",  "Hollow woody square bass",        square_bass),
    ("reese",        "Detuned reese bass",              reese),
    ("pluck_bass",   "Snappy filter-pluck bass",        pluck_bass),
    ("wobble_bass",  "LFO wobble bass",                 wobble_bass),
    ("fm_bass",      "FM growl bass",                   fm_bass),
]
