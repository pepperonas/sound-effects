"""Synth tones — plucks, stabs, leads, keys, bells and pads.

Melodic one-shots tuned to musical notes (default C major area) for building
melodies, arps and chord progressions on a step sequencer.
"""
import math
from synth import (sine, saw, square, triangle, noise_burst, mix, silence,
                   perc, ad, adsr, bell, ring_mod, lowpass, highpass, drive, note)

CATEGORY = "synth"
GROUP = "music"
DESCRIPTION = "Plucks, stabs, leads, keys, bells and pads — tuned melodic one-shots."


def pluck():
    """Synth pluck — bright saw with a fast filter decay, the workhorse note."""
    f0 = note("C4")
    s = saw(f0, 0.4, perc(9))
    mix(s, saw(f0 * 1.003, 0.4, perc(9)), 0.0, 0.5)
    return lowpass(s, lambda t: 400 + 5000 * math.exp(-16 * t))


def stab():
    """Hoover-ish stab — detuned saw triad, short and punchy."""
    s = silence(0.3)
    for f in (note("C4"), note("E4"), note("G4")):
        e = perc(10)
        mix(s, saw(f, 0.3, e), 0.0, 0.3)
        mix(s, saw(f * 1.006, 0.3, e), 0.0, 0.3)
    return drive(lowpass(s, 3500), 1.4)


def lead():
    """Lead synth — sustained saw with vibrato, cuts through a mix."""
    f0 = note("C4")
    vib = lambda t: f0 * (1 + 0.01 * math.sin(2 * math.pi * 5.5 * t))
    s = saw(vib, 0.7, adsr(0.02, 0.1, 0.8, 0.2, 0.7))
    mix(s, square(vib, 0.7, adsr(0.02, 0.1, 0.8, 0.2, 0.7)), 0.0, 0.3)
    return lowpass(s, 4500)


def key():
    """Electric-piano-ish key — sine + soft harmonic, gentle attack."""
    f0 = note("C4")
    s = sine(f0, 0.6, ad(0.005, 0.4))
    mix(s, sine(f0 * 2, 0.6, perc(8)), 0.0, 0.3)
    mix(s, sine(f0 * 3, 0.6, perc(14)), 0.0, 0.12)
    return s


def bell_tone():
    """Bell — FM-style inharmonic ring with a long shimmer (mallet/glock)."""
    f0 = note("C5")
    s = sine(f0, 0.9, perc(4))
    s = ring_mod(s, f0 * 1.41, depth=0.5)                   # inharmonic partial
    mix(s, sine(f0 * 2, 0.9, perc(6)), 0.0, 0.25)
    return s


def organ():
    """Organ — additive drawbar sines, sustained, slightly chorused."""
    f0 = note("C4")
    env = adsr(0.01, 0.02, 0.95, 0.1, 0.7)
    s = silence(0.7)
    for mult, g in ((1, 0.5), (2, 0.3), (3, 0.18), (4, 0.12)):
        mix(s, sine(f0 * mult, 0.7, env), 0.0, g)
    return s


def pad():
    """Warm pad — slow-swelling detuned saws through a soft filter."""
    f0 = note("C3")
    env = adsr(0.18, 0.1, 0.9, 0.3, 1.2)
    s = silence(1.2)
    for d in (1.0, 1.007, 0.993):
        mix(s, saw(f0 * d, 1.2, env), 0.0, 0.4)
        mix(s, saw(f0 * 2 * d, 1.2, env), 0.0, 0.15)
    return lowpass(s, 2200)


def arp_blip():
    """Arp blip — tiny bright square note for fast arpeggio sequences."""
    return square(note("C5"), 0.1, perc(28))


def saw_lead_oct():
    """Octave saw lead — root + octave stacked, fat single-note hit."""
    f0 = note("C4")
    s = saw(f0, 0.5, adsr(0.005, 0.08, 0.7, 0.2, 0.5))
    mix(s, saw(f0 * 2, 0.5, adsr(0.005, 0.08, 0.7, 0.2, 0.5)), 0.0, 0.5)
    return drive(lowpass(s, 4000), 1.3)


SOUNDS = [
    ("pluck",        "Bright filter-pluck note",        pluck),
    ("stab",         "Detuned saw triad stab",          stab),
    ("lead",         "Sustained vibrato saw lead",      lead),
    ("key",          "Electric-piano-ish key",          key),
    ("bell_tone",    "Inharmonic FM bell",              bell_tone),
    ("organ",        "Additive drawbar organ",          organ),
    ("pad",          "Warm swelling saw pad",           pad),
    ("arp_blip",     "Tiny square arp blip",            arp_blip),
    ("saw_lead_oct", "Octave-stacked saw lead",         saw_lead_oct),
]
