"""Stabs — short tonal hits for a sample deck.

Everything here is one chord, struck and gone: the sound a DJ drops on a
downbeat to punctuate a mix. Length is the point — nothing runs past 600 ms,
most are under 300 — so they land on the beat and get out of the way.

The centrepiece is the orchestra hit. It is not one instrument: the famous
Fairlight ORCH5 was a snatch of a whole orchestra hitting a chord at once, and
what makes it read as "orchestra" rather than "synth" is the pile-up of brass,
strings, piano and the thud of the hall all arriving together. That is exactly
how it is built here — four layers with slightly different attacks, because
players never land on the same millisecond.

All rooted on C so they mix harmonically with the rest of the pack.
"""
import math
from synth import (saw, square, triangle, sine, noise_burst, mix, silence, adsr,
                   perc, lowpass, highpass, drive, normalize, note, Noise)
from ._music import motif, filter_env, stack, additive

CATEGORY = "stabs"
GROUP = "dj"
DESCRIPTION = "Short tonal one-shot hits: orchestra, brass, organ, piano, synth."

MAJ = (0, 4, 7, 12)
MIN = (0, 3, 7, 12)
SUS = (0, 5, 7, 12)
DIM = (0, 3, 6, 9)
DOM = (0, 4, 7, 10)
MIN9 = (0, 3, 7, 10, 14)


def _freqs(root, intervals):
    f0 = note(root)
    return [f0 * 2 ** (i / 12.0) for i in intervals]


def _orch(root="C3", intervals=MAJ, dur=0.30, bright=1.0, weight=1.0, seed=17):
    """An orchestra hit: brass, strings, piano and hall, struck together.

    The layers are offset by a few milliseconds each. A section that lands on
    exactly the same sample sounds like one fat synth; the small disagreement
    is what the ear reads as many players.
    """
    n = dur + 0.10
    out = silence(n)
    env = adsr(0.004, dur * 0.45, 0.30, 0.10, n)
    for f in _freqs(root, intervals):
        # brass: detuned saws through a filter that snaps open
        b = stack("saw", f, n, env, detune=0.006, voices=3, side=0.7)
        mix(out, lowpass(b, filter_env(f * 1.6, (f * 12 + 1400) * bright)), 0.0, 0.30)
        # strings an octave up, thinner and later
        mix(out, stack("saw", f * 2, n, adsr(0.012, dur * 0.4, 0.22, 0.09, n),
                       detune=0.008, voices=2, side=0.6), 0.004, 0.12)
        # piano-ish struck partials underneath
        mix(out, additive(f, n, [(k, 0.9 / k ** 1.3, 5.0 + 3.0 * k) for k in (1, 2, 3, 5)]),
            0.002, 0.22 * weight)
    # the hall: a short filtered thud, the room being hit
    mix(out, lowpass(noise_burst(0.09, perc(30), 0.0, Noise(seed)), 900), 0.0, 0.30 * weight)
    mix(out, highpass(noise_burst(0.02, perc(120), 0.0, Noise(seed + 1)), 2600), 0.0, 0.12)
    return highpass(drive(normalize(out, 0.72), 1.7), 55.0)


def _brass_hit(root="C3", intervals=MAJ, dur=0.22, bright=1.4, drv=2.2):
    """A pure brass stab — no strings, no piano, just horns and drive."""
    n = dur + 0.08
    out = silence(n)
    env = adsr(0.005, dur * 0.5, 0.34, 0.08, n)
    for f in _freqs(root, intervals):
        s = stack("saw", f, n, env, detune=0.007, voices=3, side=0.72)
        mix(s, square(f, n, env), 0.0, 0.28)
        mix(out, lowpass(s, filter_env(f * 1.6, (f * 13 + 1300) * bright)), 0.0, 0.30)
    return highpass(drive(normalize(out, 0.7), drv), 70.0)


def _key_hit(root="C3", intervals=MIN, dur=0.20, bars=(8, 8, 8, 6, 0, 4, 0, 0, 3)):
    """An organ stab — drawbars, keys down and straight back up.

    Drawbars do not decay, so a plain gated chord peaks wherever its partials
    happen to line up in phase — measured at 92 ms on the first version, which
    for a sample-deck trigger means the punch lands after the beat. A Hammond
    solves this itself with "percussion": a fast-decaying harmonic on the
    attack. That is what puts the peak at the front here too.
    """
    foot = (0.5, 1.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)
    n = dur + 0.06
    out = silence(n)
    # A flat sustain lets partials realign late and beat the attack (measured
    # 245 ms on the five-note ninth). An overall decay on top makes the front
    # of the sample the loudest point by construction, whatever the chord.
    gate = adsr(0.004, 0.05, 0.62, 0.06, n)
    env = lambda t: gate(t) * math.exp(-3.2 * t)
    for f in _freqs(root, intervals):
        parts = [(foot[i], (b / 8.0) ** 1.4, 0.0) for i, b in enumerate(bars) if b]
        s = additive(f, n, parts, attack=0.003)
        mix(out, [x * env(i / 44100.0) for i, x in enumerate(s)], 0.0, 0.26)
        mix(out, sine(f * 4, n, perc(34.0)), 0.0, 0.20)        # Hammond percussion
    mix(out, highpass(noise_burst(0.008, perc(320), 0.0, Noise(31)), 2200), 0.0, 0.16)
    return highpass(drive(normalize(out, 0.7), 1.5), 60.0)


# --------------------------------------------------------------------------- #
# Orchestra hits.
# --------------------------------------------------------------------------- #
def stab_orch():
    """Orchestra hit — the classic ORCH5 downbeat punctuation, C major."""
    return _orch()


def stab_orch_min():
    """Orchestra hit, minor — the same weight, darker."""
    return _orch(intervals=MIN)


def stab_orch_low():
    """Low orchestra hit — an octave down, all chest and hall."""
    return _orch(root="C2", intervals=MAJ, dur=0.36, bright=0.75, weight=1.3)


def stab_orch_short():
    """Clipped orchestra hit — cut to 150 ms, pure impact, no ring."""
    return _orch(dur=0.13, bright=1.15)


def stab_orch_sus():
    """Suspended orchestra hit — no third, so it sits over any chord."""
    return _orch(intervals=SUS)


def stab_orch_dim():
    """Diminished hit — evenly tense, the cliffhanger."""
    return _orch(intervals=DIM, dur=0.26)


# --------------------------------------------------------------------------- #
# Brass stabs.
# --------------------------------------------------------------------------- #
def stab_brass():
    """Brass stab — horns only, hard and bright."""
    return _brass_hit()


def stab_brass_min():
    """Minor brass stab — the same punch, darker."""
    return _brass_hit(intervals=MIN)


def stab_brass_low():
    """Low brass stab — trombones and tuba, C2, chesty."""
    return _brass_hit(root="C2", dur=0.28, bright=0.8, drv=2.6)


def stab_brass_7():
    """Dominant 7th brass — leaning, wants the next chord."""
    return _brass_hit(intervals=DOM)


def stab_brass_tight():
    """Very tight brass — 120 ms, barely more than a transient."""
    return _brass_hit(dur=0.10, bright=1.6, drv=2.8)


# --------------------------------------------------------------------------- #
# Keys and organ.
# --------------------------------------------------------------------------- #
def stab_organ():
    """Organ stab — full drawbars, keys down and straight back up."""
    return _key_hit()


def stab_organ_maj():
    """Major organ stab — brighter registration."""
    return _key_hit(intervals=MAJ, bars=(8, 8, 8, 8, 6, 6, 0, 0, 4))


def stab_organ_9():
    """Minor 9th organ stab — the house-record chord."""
    return _key_hit(intervals=MIN9, dur=0.26)


def stab_piano():
    """Piano stab — a struck minor chord, damped immediately."""
    n = 0.26
    out = silence(n)
    for f in _freqs("C3", MIN):
        B = 0.0004
        parts = [(k * math.sqrt(1 + B * k * k), 1.0 / k ** 1.25, 6.0 + 3.5 * k)
                 for k in range(1, 8)]
        mix(out, additive(f, n, parts), 0.0, 0.30)
    mix(out, lowpass(noise_burst(0.015, perc(180), 0.0, Noise(9)), 2600), 0.0, 0.22)
    return highpass(normalize(out, 0.82), 50.0)


# --------------------------------------------------------------------------- #
# Synth stabs.
# --------------------------------------------------------------------------- #
def _synth_hit(intervals=MIN, dur=0.18, cut=4200.0, drv=1.8, sub=0.5):
    n = dur + 0.06
    out = silence(n)
    env = adsr(0.003, dur * 0.55, 0.25, 0.06, n)
    for f in _freqs("C3", intervals):
        s = stack("saw", f, n, env, detune=0.009, voices=3, side=0.75)
        mix(out, lowpass(s, lambda t, c=cut: 300 + c * math.exp(-14 * t)), 0.0, 0.30)
    mix(out, sine(note("C2"), n, perc(14)), 0.0, 0.35 * sub)
    return highpass(drive(normalize(out, 0.72), drv), 45.0)


def stab_synth():
    """Synth stab — detuned saws under a fast filter drop, house-record staple."""
    return _synth_hit()


def stab_synth_maj():
    """Major synth stab — the same shape, lifted."""
    return _synth_hit(intervals=MAJ)


def stab_hoover():
    """Hoover stab — the rave chord: detuned saws, hard drive, short."""
    return _synth_hit(intervals=MIN, dur=0.24, cut=5200.0, drv=3.2)


def stab_pluck():
    """Pluck stab — one bright filtered chord, 120 ms, sits on off-beats."""
    return _synth_hit(intervals=MIN9, dur=0.10, cut=6000.0, drv=1.4, sub=0.2)


def stab_sub():
    """Sub stab — a short C1 sine punch to sit under any of the others."""
    n = 0.22
    s = sine(lambda t: note("C1") * (1 + 0.9 * math.exp(-70 * t)), n, perc(16))
    mix(s, noise_burst(0.004, perc(260), 0.0, Noise(3)), 0.0, 0.14)
    # A sub whose first half-cycle outlasts its own envelope leaves a DC step
    # (measured +0.013), which eats headroom in a mix and can click on trigger.
    return highpass(drive(s, 2.0), 22.0)


SOUNDS = [
    ("stab_orch",        "Classic orchestra hit, major",   stab_orch),
    ("stab_orch_min",    "Orchestra hit, minor",           stab_orch_min),
    ("stab_orch_low",    "Low octave orchestra hit",       stab_orch_low),
    ("stab_orch_short",  "Clipped 150 ms orchestra hit",   stab_orch_short),
    ("stab_orch_sus",    "Suspended orchestra hit",        stab_orch_sus),
    ("stab_orch_dim",    "Diminished tension hit",         stab_orch_dim),
    ("stab_brass",       "Bright brass stab",              stab_brass),
    ("stab_brass_min",   "Minor brass stab",               stab_brass_min),
    ("stab_brass_low",   "Low chesty brass stab",          stab_brass_low),
    ("stab_brass_7",     "Dominant 7th brass stab",        stab_brass_7),
    ("stab_brass_tight", "Ultra-tight 120 ms brass",       stab_brass_tight),
    ("stab_organ",       "Full-drawbar organ stab",        stab_organ),
    ("stab_organ_maj",   "Bright major organ stab",        stab_organ_maj),
    ("stab_organ_9",     "Minor 9th organ stab",           stab_organ_9),
    ("stab_piano",       "Damped piano chord stab",        stab_piano),
    ("stab_synth",       "Filter-drop synth stab",         stab_synth),
    ("stab_synth_maj",   "Major synth stab",               stab_synth_maj),
    ("stab_hoover",      "Rave hoover stab",               stab_hoover),
    ("stab_pluck",       "Short bright pluck stab",        stab_pluck),
    ("stab_sub",         "Sub punch to layer underneath",  stab_sub),
]
