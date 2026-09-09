"""Horns — air horns, sirens and alarms: the signals a DJ shouts with.

None of these are subtle and none of them are supposed to be. What they have
in common is a *reed*: an air horn, a klaxon and a siren all make their noise
by chopping a stream of air, which is why they are built from stacked square
and saw waves rather than sines, and why the interesting part is always the
pitch curve, not the timbre.

The reggae air horn is three horns bolted together and blown at once. They are
never quite in tune with each other, and that beating is the sound — a single
horn sounds like a car, three sound like a soundsystem.
"""
import math
from synth import (osc, square, saw, sine, noise_burst, mix, silence, adsr, perc,
                   lowpass, highpass, drive, normalize, note, Noise)

CATEGORY = "horns"
GROUP = "dj"
DESCRIPTION = "Air horns, sirens, klaxons, alarms and lasers for calling a drop."


def _reed(freqs, dur, env, detune=0.011, bright=1.0, drv=2.4, sq=0.55):
    """A stack of reeds: squares for the buzz, saws for the body."""
    out = silence(dur)
    for f in freqs:
        for d in (1.0, 1.0 + detune, 1.0 - detune):
            ff = (lambda t, _f=f, _d=d: _f(t) * _d) if callable(f) else f * d
            mix(out, osc("square", ff, dur, env), 0.0, 0.30 * sq)
            mix(out, osc("saw", ff, dur, env), 0.0, 0.24)
    out = lowpass(out, 2400.0 * bright)
    return highpass(drive(normalize(out, 0.7), drv), 180.0)


def _sweep(a, b, dur, shape=1.0):
    """Pitch curve from a to b across the sound."""
    fa = note(a) if isinstance(a, str) else a
    fb = note(b) if isinstance(b, str) else b
    return lambda t: fa + (fb - fa) * min(1.0, (t / dur)) ** shape


# --------------------------------------------------------------------------- #
# Air horns.
# --------------------------------------------------------------------------- #
def horn_air():
    """Air horn — three horns blown together, the soundsystem signal."""
    d = 0.90
    return _reed([note("A3"), note("C#4"), note("E4")], d,
                 adsr(0.020, 0.06, 0.92, 0.18, d))


def horn_air_short():
    """Short air horn — a single blast, 400 ms, straight in and out."""
    d = 0.42
    return _reed([note("A3"), note("C#4"), note("E4")], d,
                 adsr(0.014, 0.04, 0.92, 0.10, d))


def horn_air_low():
    """Low air horn — an octave down, more chest, less shriek."""
    d = 0.80
    return _reed([note("A2"), note("C#3"), note("E3")], d,
                 adsr(0.022, 0.06, 0.92, 0.16, d), bright=0.7)


def horn_air_double():
    """Double blast — two hits, the way it is actually used over a drop."""
    d = 0.26
    one = _reed([note("A3"), note("C#4"), note("E4")], d,
                adsr(0.012, 0.04, 0.92, 0.08, d))
    out = list(one)
    mix(out, one, 0.34, 0.95)
    return out


def horn_air_rise():
    """Rising air horn — the pitch pulled up as it sounds, calling a lift."""
    d = 0.70
    base = _sweep("G3", "B3", d, shape=0.6)
    return _reed([base, lambda t: base(t) * 2 ** (4 / 12.0),
                  lambda t: base(t) * 2 ** (7 / 12.0)], d,
                 adsr(0.018, 0.06, 0.92, 0.16, d))


def horn_fog():
    """Fog horn — one huge low reed, slow and flat."""
    d = 1.10
    return _reed([note("D2"), note("A2")], d, adsr(0.10, 0.10, 0.9, 0.30, d),
                 bright=0.45, drv=1.8, detune=0.006)


# --------------------------------------------------------------------------- #
# Sirens.
# --------------------------------------------------------------------------- #
def horn_siren_up():
    """Siren rising — one sweep up, the classic build signal."""
    d = 1.10
    return _reed([_sweep("A3", "A5", d, 1.6)], d, adsr(0.03, 0.05, 0.95, 0.14, d),
                 bright=1.3, drv=2.0)


def horn_siren_down():
    """Siren falling — the same sweep coming back down."""
    d = 1.00
    return _reed([_sweep("A5", "A3", d, 1.6)], d, adsr(0.02, 0.05, 0.95, 0.16, d),
                 bright=1.3, drv=2.0)


def horn_siren_wail():
    """Wailing siren — up and down inside one sound, the police curve."""
    d = 1.20
    f = lambda t: note("A3") * 2 ** (2.0 * math.sin(math.pi * min(1.0, t / d)))
    return _reed([f], d, adsr(0.03, 0.05, 0.95, 0.16, d), bright=1.3, drv=2.0)


def horn_siren_fast():
    """Fast siren — three quick wails, urgent."""
    d = 0.90
    f = lambda t: note("A3") * 2 ** (1.4 * (0.5 - 0.5 * math.cos(2 * math.pi * 3.4 * t)))
    return _reed([f], d, adsr(0.02, 0.05, 0.95, 0.12, d), bright=1.3, drv=2.0)


def horn_klaxon():
    """Klaxon — two tones alternating, the ship's horn."""
    d = 0.85
    f = lambda t: note("F3") if (t * 5.0) % 2.0 < 1.0 else note("Ab3")
    return _reed([f], d, adsr(0.012, 0.04, 0.95, 0.12, d), drv=2.8)


def horn_alarm():
    """Alarm — a hard two-tone alternation, faster and higher than the klaxon."""
    d = 0.80
    f = lambda t: note("C5") if (t * 11.0) % 2.0 < 1.0 else note("G4")
    return _reed([f], d, adsr(0.006, 0.03, 0.95, 0.10, d), bright=1.5, drv=3.0)


def horn_warble():
    """Warble — a siren wobbling around one pitch, the evacuation tone."""
    d = 0.95
    f = lambda t: note("A4") * 2 ** (0.35 * math.sin(2 * math.pi * 7.0 * t))
    return _reed([f], d, adsr(0.02, 0.05, 0.95, 0.14, d), bright=1.4)


# --------------------------------------------------------------------------- #
# Electronic signals.
# --------------------------------------------------------------------------- #
def horn_laser():
    """Laser — a fast fall, the arcade zap DJs use as a stinger."""
    d = 0.30
    s = saw(lambda t: 3200.0 * math.exp(-14.0 * t) + 180.0, d, perc(11))
    mix(s, square(lambda t: 1600.0 * math.exp(-14.0 * t) + 90.0, d, perc(11)), 0.0, 0.4)
    return highpass(drive(normalize(s, 0.8), 1.6), 120.0)


def horn_laser_up():
    """Reverse laser — the same zap climbing instead, a short lift."""
    d = 0.32
    s = saw(lambda t: 200.0 * math.exp(11.0 * t), d, lambda t: (t / d) ** 0.7)
    return highpass(drive(normalize(s, 0.8), 1.5), 120.0)


def horn_zap():
    """Zap — a single ring-modulated crack, very short."""
    d = 0.16
    s = square(lambda t: 900.0 * math.exp(-22.0 * t) + 140.0, d, perc(26))
    mix(s, highpass(noise_burst(0.03, perc(90), 0.0, Noise(71)), 3000), 0.0, 0.35)
    return highpass(drive(normalize(s, 0.8), 2.2), 140.0)


def horn_beep():
    """Beep — one flat tone, the censor bleep, 200 ms."""
    d = 0.20
    return _reed([note("A4")], d, adsr(0.004, 0.01, 1.0, 0.02, d), detune=0.0,
                 bright=1.6, drv=1.2, sq=1.4)


def horn_beep_3():
    """Three beeps — a countdown into the drop."""
    d = 0.10
    one = _reed([note("A4")], d, adsr(0.004, 0.01, 1.0, 0.02, d), detune=0.0,
                bright=1.6, drv=1.2, sq=1.4)
    out = list(one)
    mix(out, one, 0.20, 1.0)
    mix(out, [x * 1.0 for x in _reed([note("A5")], d,
                                     adsr(0.004, 0.01, 1.0, 0.02, d), detune=0.0,
                                     bright=1.6, drv=1.2, sq=1.4)], 0.40, 1.0)
    return out


def horn_stinger():
    """Stinger — a very short rising horn, a comma rather than a sentence."""
    d = 0.26
    base = _sweep("G3", "D4", d, 0.7)
    return _reed([base, lambda t: base(t) * 2 ** (7 / 12.0)], d,
                 adsr(0.010, 0.03, 0.92, 0.07, d), bright=1.2)


def horn_pull_up():
    """Pull-up — the rewind signal: a rising siren cut off dead at the top."""
    d = 0.65
    return _reed([_sweep("A3", "A5", d, 1.2)], d,
                 lambda t: 1.0 if t < d - 0.01 else 0.0, bright=1.3, drv=2.2)


SOUNDS = [
    ("horn_air",         "Three-reed reggae air horn",   horn_air),
    ("horn_air_short",   "Single 400 ms blast",          horn_air_short),
    ("horn_air_low",     "Low chesty air horn",          horn_air_low),
    ("horn_air_double",  "Two-blast air horn",           horn_air_double),
    ("horn_air_rise",    "Air horn pulled upward",       horn_air_rise),
    ("horn_fog",         "Huge slow fog horn",           horn_fog),
    ("horn_siren_up",    "Rising siren sweep",           horn_siren_up),
    ("horn_siren_down",  "Falling siren sweep",          horn_siren_down),
    ("horn_siren_wail",  "Up-and-down police wail",      horn_siren_wail),
    ("horn_siren_fast",  "Three urgent quick wails",     horn_siren_fast),
    ("horn_klaxon",      "Two-tone ship's klaxon",       horn_klaxon),
    ("horn_alarm",       "Fast high two-tone alarm",     horn_alarm),
    ("horn_warble",      "Warbling evacuation tone",     horn_warble),
    ("horn_laser",       "Fast falling laser zap",       horn_laser),
    ("horn_laser_up",    "Rising reverse laser",         horn_laser_up),
    ("horn_zap",         "Very short electric crack",    horn_zap),
    ("horn_beep",        "Flat 200 ms censor beep",      horn_beep),
    ("horn_beep_3",      "Three-beep countdown",         horn_beep_3),
    ("horn_pull_up",     "Rewind pull-up signal",        horn_pull_up),
    ("horn_stinger",     "Short rising horn stinger",    horn_stinger),
]
