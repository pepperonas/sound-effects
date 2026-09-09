"""Subs — short bass hits: 808s, slides, drops and growls.

Bass you trigger rather than sequence. The `bass` category is an instrument
for writing lines; this is the single low event you drop under a mix, so
everything is one hit and everything is tuned to C.

The physics that matters down here is that **you cannot hear a sub, you feel
it** — and a club system reproduces the transient long before it reproduces
the fundamental. So every one of these has something audible on top of the
low end: a click, a short mid-range body, or the harmonics that saturation
generates. A pure 30 Hz sine is silent on a laptop and shapeless on a rig.

Anything that slides gets a real glide rather than two notes crossfaded: the
808 slide is one continuous string of low frequency, which is exactly why it
reads as a single instrument moving and not as two hits.
"""
import math
from synth import (sine, saw, triangle, noise_burst, mix, silence, perc, adsr,
                   lowpass, highpass, drive, normalize, note, Noise)
from ._music import glide

CATEGORY = "subs"
GROUP = "dj"
DESCRIPTION = "Short bass hits: 808s, pitch slides, sub drops, growls and stabs."


def _sub(f, dur, dec=3.2, click=0.28, drv=2.2, body=0.30, bend=0.0):
    """One low hit. `bend` is the pitch drop at the attack an 808 always has."""
    fn = (f if callable(f)
          else (lambda t, _f=f: _f * (1 + bend * math.exp(-45.0 * t))))
    s = sine(fn, dur, perc(dec))
    if body:                                   # a mid octave, so it survives a laptop
        mix(s, triangle(lambda t: fn(t) * 2, dur, perc(dec * 1.5)), 0.0, body)
    if click:
        mix(s, lowpass(noise_burst(0.006, perc(240.0), 0.0, Noise(11)), 4000),
            0.0, click)
    # A sub whose first half-cycle outlasts its envelope leaves a DC step.
    return highpass(drive(normalize(s, 0.8), drv), 20.0)


# --------------------------------------------------------------------------- #
# 808s.
# --------------------------------------------------------------------------- #
def sub_808():
    """808 — C1 with the pitch drop at the front, the trap staple."""
    return _sub(note("C1"), 0.85, dec=2.9, bend=1.1)


def sub_808_short():
    """Short 808 — the same hit clipped to a third of a second."""
    return _sub(note("C1"), 0.32, dec=9.0, bend=1.1)


def sub_808_low():
    """Low 808 — C0, right at the bottom of what a rig will move."""
    return _sub(note("C0") * 2 ** (0 / 12.0), 0.95, dec=2.4, bend=0.9, body=0.42)


def sub_808_hard():
    """Distorted 808 — driven until the harmonics carry it on small speakers."""
    return _sub(note("C1"), 0.70, dec=3.4, bend=1.1, drv=5.5, body=0.45)


def sub_808_clean():
    """Clean 808 — no click, no drive, just the note. For layering."""
    return _sub(note("C1"), 0.80, dec=3.0, bend=0.9, click=0.0, drv=1.0, body=0.18)


# --------------------------------------------------------------------------- #
# Slides — one continuous low tone moving, not two hits.
# --------------------------------------------------------------------------- #
def sub_slide_up():
    """808 slide up — C1 to G1, the fifth every trap record slides."""
    return _sub(glide(note("C1"), note("G1"), 0.16, 0.16), 0.90, dec=2.8)


def sub_slide_down():
    """808 slide down — G1 falling back to C1."""
    return _sub(glide(note("G1"), note("C1"), 0.16, 0.16), 0.90, dec=2.8)


def sub_slide_oct():
    """Octave slide — C2 down to C1, a whole octave inside one hit."""
    return _sub(glide(note("C2"), note("C1"), 0.12, 0.22), 0.95, dec=2.6)


def sub_slide_long():
    """Long slide — C1 up a minor third, taking its time about it."""
    return _sub(glide(note("C1"), note("Eb1"), 0.22, 0.35), 1.15, dec=2.2)


def sub_fall():
    """Sub drop — a slide with no destination: straight into the floor."""
    return _sub(lambda t: 120.0 * math.exp(-4.2 * t) + 27.0, 1.10, dec=2.6,
                click=0.14, body=0.12)


def sub_dive():
    """Dive — a fast fall, a quarter of a second, for a stop."""
    return _sub(lambda t: 180.0 * math.exp(-14.0 * t) + 30.0, 0.30, dec=9.0,
                click=0.30, body=0.20)


def sub_rise():
    """Rise — the opposite: low to high, a lift under a build."""
    return _sub(lambda t: 34.0 * math.exp(3.6 * t), 0.55, dec=1.6,
                click=0.10, body=0.16)


# --------------------------------------------------------------------------- #
# Stabs and growls.
# --------------------------------------------------------------------------- #
def sub_stab():
    """Sub stab — 150 ms of low, gone before it rings. Sits on off-beats."""
    return _sub(note("C1"), 0.16, dec=22.0, bend=0.7, drv=2.6)


def sub_thump():
    """Thump — no pitch to speak of, just the movement of air."""
    return _sub(lambda t: 60.0 * math.exp(-24.0 * t) + 26.0, 0.24, dec=14.0,
                click=0.45, body=0.10, drv=1.6)


def sub_donk():
    """Donk — the hard, short, mid-heavy bass hit of bounce and donk records."""
    s = _sub(note("C2"), 0.18, dec=20.0, bend=0.4, drv=3.0, body=0.9)
    return normalize(highpass(s, 70.0), 0.85)


def _growl(f0, dur, rate, dec=3.0, drv=4.0):
    """Detuned saws under a moving filter: the reese/growl recipe."""
    env = perc(dec)
    s = saw(f0, dur, env)
    mix(s, saw(f0 * 1.012, dur, env), 0.0, 0.9)
    mix(s, saw(f0 * 0.988, dur, env), 0.0, 0.9)
    s = lowpass(s, lambda t: 220.0 + 1500.0 * (0.5 + 0.5 * math.sin(
        2 * math.pi * rate * t)))
    mix(s, sine(f0 * 0.5, dur, env), 0.0, 0.7)
    return highpass(drive(normalize(s, 0.75), drv), 24.0)


def sub_reese():
    """Reese — two detuned saws beating against each other, half a second."""
    return _growl(note("C1") * 2, 0.55, 5.0, dec=3.4, drv=3.0)


def sub_growl():
    """Growl — the same, chewed harder by a faster filter."""
    return _growl(note("C1") * 2, 0.60, 11.0, dec=3.0, drv=5.0)


def sub_wobble():
    """Wobble — one slow sweep of the filter, a single dubstep chew."""
    return _growl(note("C1") * 2, 0.75, 2.6, dec=2.2, drv=4.0)


def sub_pluck():
    """Sub pluck — a filtered attack over the low note, short and defined."""
    f0 = note("C1")
    s = sine(lambda t: f0 * (1 + 0.6 * math.exp(-50.0 * t)), 0.35, perc(8.0))
    mix(s, lowpass(saw(f0 * 4, 0.35, perc(26.0)),
                   lambda t: 200.0 + 2600.0 * math.exp(-22.0 * t)), 0.0, 0.45)
    return highpass(drive(normalize(s, 0.8), 2.0), 22.0)


def sub_double():
    """Two hits — the same note struck twice, an eighth apart."""
    one = _sub(note("C1"), 0.30, dec=9.0, bend=1.0)
    out = list(one)
    mix(out, one, 0.23, 0.9)
    return normalize(out, 0.88)


SOUNDS = [
    ("sub_808",         "Tuned 808 with pitch drop",     sub_808),
    ("sub_808_short",   "Clipped third-second 808",      sub_808_short),
    ("sub_808_low",     "Bottom-octave 808",             sub_808_low),
    ("sub_808_hard",    "Driven, harmonically rich 808", sub_808_hard),
    ("sub_808_clean",   "Clean 808 for layering",        sub_808_clean),
    ("sub_slide_up",    "808 sliding up a fifth",        sub_slide_up),
    ("sub_slide_down",  "808 sliding back down",         sub_slide_down),
    ("sub_slide_oct",   "Octave slide inside one hit",   sub_slide_oct),
    ("sub_slide_long",  "Slow minor-third slide",        sub_slide_long),
    ("sub_fall",        "Sub falling into the floor",    sub_fall),
    ("sub_dive",        "Fast quarter-second dive",      sub_dive),
    ("sub_rise",        "Low-to-high lift",              sub_rise),
    ("sub_stab",        "150 ms sub stab",               sub_stab),
    ("sub_thump",       "Pitchless movement of air",     sub_thump),
    ("sub_donk",        "Hard mid-heavy donk hit",       sub_donk),
    ("sub_reese",       "Beating detuned reese",         sub_reese),
    ("sub_growl",       "Fast-chewed growl",             sub_growl),
    ("sub_wobble",      "Single slow dubstep wobble",    sub_wobble),
    ("sub_pluck",       "Filtered sub pluck",            sub_pluck),
    ("sub_double",      "Two 808 hits an eighth apart",  sub_double),
]
