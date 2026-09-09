"""Crowd — applause, cheers, whistles and chants: the room reacting.

A crowd is not one sound made louder, it is hundreds of small events whose
*timing* is random and whose *rate* is not. Applause is the clearest case:
each pair of hands is a short filtered click, and what makes a room of two
thousand people different from one person clapping is only the density —
enough overlapping claps and the individual events stop being audible at all
and become a texture. So these are built as sparse impulse fields, and the
density is the parameter that turns polite applause into an ovation.

Voices are the choir's formant machinery again, but deliberately smeared:
every voice on a slightly different pitch, entering at a slightly different
moment, because a crowd that agrees sounds like a choir, not a crowd.
"""
import math
from synth import (sine, noise_burst, mix, silence, perc, adsr, bell, lowpass,
                   highpass, drive, normalize, note, vibrato, Noise)
from ._music import additive

CATEGORY = "crowd"
GROUP = "dj"
DESCRIPTION = "Applause, cheers, whistles and chants — the room reacting."

VOWELS = {
    "ah": ((730, 1.00, 130), (1090, 0.50, 170), (2440, 0.22, 240)),
    "oh": ((570, 1.00, 110), (840, 0.55, 150), (2410, 0.11, 220)),
    "oo": ((300, 1.00, 90), (870, 0.26, 130), (2240, 0.08, 200)),
}


def _clap_field(dur, density, env, seed=1, lo=1200.0, hi=7000.0, size=1.0):
    """A field of hand claps: `density` claps per second, timing random.

    Each clap is one short noise impulse; the room is the sum. Below about
    twenty a second you still hear individual pairs of hands, above a hundred
    it turns to a texture — which is the whole difference between a few people
    and a full house.
    """
    n = int(dur * 44100)
    out = [0.0] * n
    rng = Noise(seed)
    body = Noise(seed + 1)
    per = 44100.0 / density
    t = 0.0
    while t < dur:
        i = int(t * 44100)
        amp = (0.35 + 0.65 * abs(rng())) * env(t)
        dec = 190.0 + 90.0 * abs(rng()) / max(0.05, size)
        k = 0
        while k < 700 and i + k < n:
            out[i + k] += body() * math.exp(-dec * k / 44100.0) * amp
            k += 1
        # Random spacing around the mean rate: a crowd is Poisson, not a grid.
        t += max(1.0, per * (0.4 + 1.2 * abs(rng()))) / 44100.0
    return lowpass(highpass(out, lo), hi)


def _voices(pitches, dur, vowel="ah", spread=0.06, seed=3, vib=0.012):
    """Several voices on a vowel, none of them quite together."""
    out = silence(dur + 0.22)
    rng = Noise(seed)
    for k, p in enumerate(pitches):
        f0 = (note(p) if isinstance(p, str) else p) * (1.0 + 0.012 * rng())
        parts = []
        for h in range(1, 20):
            f = h * f0
            if f > 3400:
                break
            g = sum(a * math.exp(-((f - fc) / bw) ** 2)
                    for fc, a, bw in VOWELS[vowel]) / (1.0 + 0.28 * (h - 1))
            if g > 0.005:
                parts.append((h, g, 0.0))
        env = adsr(0.09 + 0.05 * abs(rng()), 0.15, 0.8, 0.28, dur)
        s = additive(f0, dur, parts or [(1, 1.0, 0.0)], attack=0.004,
                     vib=(5.2 + 1.4 * abs(rng()), vib))
        # Bounded by `spread`, not multiplied by the voice index: scaling with
        # k meant the eighth voice entered over a second late and pushed the
        # sample past its length budget.
        mix(out, [x * env(i / 44100.0) for i, x in enumerate(s)],
            spread * abs(rng()), 0.5)
    return out


def _out(xs, peak=0.85):
    lead = next((i for i, x in enumerate(xs) if abs(x) > 0.002), 0)
    return normalize(xs[lead:] if lead else xs, peak)


# --------------------------------------------------------------------------- #
# Applause — density is the only thing that changes.
# --------------------------------------------------------------------------- #
def crowd_clap_few():
    """A few people clapping — sparse enough that you hear individual hands."""
    return _out(_clap_field(0.90, 14.0, lambda t: 1.0, seed=11))


def crowd_applause():
    """Applause — a room, dense enough to become a texture."""
    return _out(_clap_field(1.10, 95.0, lambda t: min(1.0, t / 0.03), seed=13))


def crowd_ovation():
    """Ovation — a full house, as dense as it gets."""
    return _out(_clap_field(1.20, 220.0, lambda t: min(1.0, t / 0.025), seed=17,
                            lo=900.0))


def crowd_applause_in():
    """Applause starting — the room catching on over half a second."""
    return _out(_clap_field(1.15, 130.0, lambda t: min(1.0, (t / 0.55) ** 1.8),
                            seed=19))


def crowd_applause_out():
    """Applause dying — the last few hands, trailing off."""
    return _out(_clap_field(1.15, 120.0, lambda t: max(0.0, 1.0 - t / 1.1) ** 1.4,
                            seed=23))


def crowd_slow_clap():
    """Slow hand-clap — five deliberate claps, unimpressed."""
    out = silence(1.20)
    for k in range(5):
        c = _clap_field(0.16, 9.0, lambda t: 1.0, seed=29 + k, size=1.6)
        mix(out, c, k * 0.23, 0.9)
    return _out(out)


def crowd_stomp():
    """Stomp — feet rather than hands: the same field, an octave down."""
    return _out(_clap_field(1.05, 22.0, lambda t: 1.0, seed=31,
                            lo=90.0, hi=1400.0, size=2.5))


# --------------------------------------------------------------------------- #
# Voices.
# --------------------------------------------------------------------------- #
def crowd_cheer():
    """Cheer — a wall of voices on an open ah, with hands underneath."""
    v = _voices(("G3", "A3", "C4", "D4", "F4", "A4"), 0.72, "ah", seed=37)
    mix(v, _clap_field(1.0, 70.0, lambda t: min(1.0, t / 0.04), seed=41), 0.02, 0.55)
    return _out(v)


def crowd_cheer_big():
    """Big cheer — more voices, wider spread, longer to gather."""
    v = _voices(("E3", "G3", "A3", "C4", "D4", "E4", "G4", "A4"), 0.80, "ah",
                spread=0.08, seed=43)
    mix(v, _clap_field(1.15, 140.0, lambda t: min(1.0, t / 0.05), seed=47), 0.02, 0.6)
    return _out(v)


def crowd_woo():
    """Woo — the rising whoop a room makes when a track drops."""
    v = _voices(("D4", "F4", "A4", "D5"), 0.75, "oo", spread=0.07, seed=53,
                vib=0.02)
    return _out(v)


def crowd_gasp():
    """Gasp — a sharp intake, more air than voice."""
    n = highpass(noise_burst(0.36, lambda t: min(1.0, t / 0.20) ** 2.0, 0.0,
                             Noise(59)), 900)
    v = _voices(("C4", "E4", "G4"), 0.34, "ah", spread=0.02, seed=61, vib=0.004)
    mix(v, lowpass(n, 5000.0), 0.0, 0.7)
    return _out(v)


def crowd_boo():
    """Boo — low voices on an oo, disapproving and slightly out of tune."""
    return _out(_voices(("E2", "G2", "A2", "C3"), 0.90, "oo", spread=0.09,
                        seed=67, vib=0.016))


def crowd_murmur():
    """Murmur — a room talking, no pitch you can name."""
    v = _voices(("C3", "D3", "E3", "G3", "A3"), 0.88, "oh", spread=0.11, seed=71,
                vib=0.022)
    return _out([x * 0.6 for x in v])


def crowd_chant():
    """Chant — two shouted syllables on the beat, a terrace."""
    one = _voices(("A3", "C4", "E4"), 0.22, "oh", spread=0.02, seed=73, vib=0.01)
    out = list(one)
    mix(out, one, 0.34, 0.95)
    return _out(out)


def crowd_chant_3():
    """Three-note chant — the pitch rising, a call to attention."""
    out = silence(1.15)
    for k, p in enumerate((("F3", "A3", "C4"), ("G3", "B3", "D4"),
                           ("Bb3", "D4", "F4"))):
        mix(out, _voices(p, 0.18, "oh", spread=0.02, seed=79 + k, vib=0.01),
            k * 0.28, 0.95)
    return _out(out)


# --------------------------------------------------------------------------- #
# Whistles.
# --------------------------------------------------------------------------- #
def _whistle(f, dur, vibr=0.02, rate=6.0, breath=0.10, rise=0.0):
    """A finger whistle: nearly a pure tone, with air at the start."""
    fn = vibrato(f * (1.0 - rise), rate=rate, depth=vibr, onset=0.10)
    s = sine(lambda t: fn(t) * (1.0 + rise * min(1.0, t / (dur * 0.6))), dur,
             adsr(0.020, 0.05, 0.9, 0.10, dur))
    mix(s, sine(lambda t: 2 * fn(t), dur, adsr(0.02, 0.05, 0.9, 0.10, dur)), 0.0, 0.09)
    mix(s, highpass(noise_burst(0.05, perc(40.0), 0.0, Noise(83)), 2500), 0.0, breath)
    return _out(s)


def crowd_whistle():
    """Whistle — two fingers, loud and steady."""
    return _whistle(note("C6"), 0.55)


def crowd_whistle_up():
    """Whistle sliding up — the approving one."""
    return _whistle(note("A5"), 0.55, rise=0.35)


def crowd_whistle_two():
    """Two-tone whistle — the "over here" call."""
    a = _whistle(note("A5"), 0.22, breath=0.14)
    b = _whistle(note("E6"), 0.34, breath=0.08)
    out = list(a)
    mix(out, b, 0.24, 1.0)
    return _out(out)


def crowd_whistle_crowd():
    """Several whistles at once — the end of a set."""
    out = silence(1.0)
    for k, (p, off) in enumerate((("C6", 0.0), ("D6", 0.13), ("A5", 0.26),
                                  ("E6", 0.41))):
        mix(out, _whistle(note(p), 0.55, rate=5.5 + k, breath=0.06), off, 0.7)
    mix(out, _clap_field(1.0, 60.0, lambda t: min(1.0, t / 0.2), seed=89), 0.0, 0.35)
    return _out(out)


def crowd_stomp_clap():
    """Stomp-stomp-clap — the oldest rhythm a crowd knows."""
    out = silence(1.15)
    st = _clap_field(0.26, 20.0, lambda t: 1.0, seed=97, lo=90.0, hi=1400.0, size=2.5)
    cl = _clap_field(0.30, 60.0, lambda t: 1.0, seed=101)
    mix(out, st, 0.00, 1.0)
    mix(out, st, 0.27, 0.95)
    mix(out, cl, 0.54, 1.0)
    return _out(out)


SOUNDS = [
    ("crowd_clap_few",      "A few individual hands",      crowd_clap_few),
    ("crowd_applause",      "A room, dense enough to blur", crowd_applause),
    ("crowd_ovation",       "Full-house ovation",          crowd_ovation),
    ("crowd_applause_in",   "Applause catching on",        crowd_applause_in),
    ("crowd_applause_out",  "Applause trailing off",       crowd_applause_out),
    ("crowd_slow_clap",     "Five unimpressed claps",      crowd_slow_clap),
    ("crowd_stomp",         "Feet instead of hands",       crowd_stomp),
    ("crowd_cheer",         "Voices and hands together",   crowd_cheer),
    ("crowd_cheer_big",     "Bigger, wider cheer",         crowd_cheer_big),
    ("crowd_woo",           "Rising whoop on a drop",      crowd_woo),
    ("crowd_gasp",          "Sharp collective intake",     crowd_gasp),
    ("crowd_boo",           "Low disapproving boo",        crowd_boo),
    ("crowd_murmur",        "A room talking",              crowd_murmur),
    ("crowd_chant",         "Two-syllable terrace chant",  crowd_chant),
    ("crowd_chant_3",       "Rising three-note chant",     crowd_chant_3),
    ("crowd_whistle",       "Loud two-finger whistle",     crowd_whistle),
    ("crowd_whistle_up",    "Approving rising whistle",    crowd_whistle_up),
    ("crowd_whistle_two",   "Two-tone 'over here' call",   crowd_whistle_two),
    ("crowd_whistle_crowd", "Several whistles at once",    crowd_whistle_crowd),
    ("crowd_stomp_clap",    "Stomp-stomp-clap",            crowd_stomp_clap),
]
