"""Drops — short transitions: tape stops, brakes, risers, impacts, rewinds.

The glue between two records, cut short enough to trigger by hand rather than
automate. Everything here is under a second and a quarter, which is the real
constraint: the long cinematic riser in the `fx` category is something you
schedule, this is something you hit.

Two families. The *mechanical* ones — tape stop, vinyl brake, backspin — are
all the same idea as a scratch: pitch follows the speed of a machine slowing
down, so the curve is the sound. The *electronic* ones — risers, impacts, sub
drops — are pitch and filter moving in the same direction at once, because
either alone reads as a effect and both together read as momentum.
"""
import math
from synth import (sine, saw, square, noise_burst, mix, silence, adsr, perc, bell,
                   lowpass, highpass, drive, reverse, normalize, note, Noise)

CATEGORY = "drops"
GROUP = "dj"
DESCRIPTION = "Short transitions: tape stop, brake, backspin, risers, impacts."

def _tight(xs):
    """Top-and-tail: trim the dead head so the sample triggers on the beat.

    A riser or an air-suction starts at true zero by design; on a deck that
    silence is latency you cannot compensate, so it comes off — the shape is
    unchanged, it simply starts where it becomes audible.
    """
    lead = next((i for i, x in enumerate(xs) if abs(x) > 0.002), 0)
    return xs[lead:] if lead else xs


CHORD = (0, 3, 7, 12)


def _tonal(dur, speed, root="A2", env=None, drv=1.6, tone=6000.0):
    """A chord read at a varying playback speed — a machine slowing or lifting."""
    out = silence(dur)
    f0 = note(root)
    for i in CHORD:
        f = f0 * 2 ** (i / 12.0)
        for mult, g in ((1.0, 0.45), (2.0, 0.22), (3.0, 0.12), (5.0, 0.06)):
            out = mix(out, saw(lambda t, _f=f * mult: _f * speed(t), dur, env), 0.0, g * 0.5)
    out = lowpass(out, tone)
    return _tight(highpass(drive(normalize(out, 0.75), drv), 45.0))


def _smooth(x):
    return x * x * (3.0 - 2.0 * x)


# --------------------------------------------------------------------------- #
# Mechanical: something is slowing down or spinning up.
# --------------------------------------------------------------------------- #
def drop_tape_stop():
    """Tape stop — the reel losing power, pitch sagging into nothing."""
    d = 0.65
    return _tonal(d, lambda t: max(0.02, 1.0 - _smooth(min(1.0, t / 0.55))), "A2",
                  env=lambda t: min(1.0, (1.0 - t / d) * 1.6))


def drop_tape_stop_fast():
    """Fast tape stop — a 250 ms sag, for a stop on the beat."""
    d = 0.32
    return _tonal(d, lambda t: max(0.02, 1.0 - _smooth(min(1.0, t / 0.25))), "A2",
                  env=lambda t: min(1.0, (1.0 - t / d) * 1.8))


def drop_brake():
    """Vinyl brake — the platter stopped by hand, harder than a tape stop."""
    d = 0.45
    return _tonal(d, lambda t: max(0.02, (1.0 - min(1.0, t / 0.36)) ** 2.2), "A2",
                  env=lambda t: min(1.0, (1.0 - t / d) * 1.7), drv=2.0)


def drop_backspin():
    """Backspin — the record thrown back, everything reversing away."""
    d = 0.55
    return _tonal(d, lambda t: -4.5 * math.exp(-4.0 * t) - 0.25, "A2",
                  env=lambda t: math.exp(-2.4 * t), drv=1.8)


def drop_spinup():
    """Spin-up — the deck pulling from stopped up to pitch."""
    d = 0.55
    return _tonal(d, lambda t: 0.05 + 0.95 * _smooth(min(1.0, t / 0.45)), "A2",
                  env=lambda t: min(1.0, t / 0.10) * 0.9 + 0.1)


def drop_rewind():
    """Rewind — the pull-up: everything rushing backwards and up in pitch."""
    d = 0.50
    return _tonal(d, lambda t: -(1.0 + 5.0 * (t / d) ** 1.5), "A2",
                  env=lambda t: 0.4 + 0.6 * (t / d), drv=2.0)


# --------------------------------------------------------------------------- #
# Risers and falls.
# --------------------------------------------------------------------------- #
def drop_riser():
    """Short riser — noise and tone climbing together, 700 ms into a drop."""
    d = 0.70
    n = noise_burst(d, lambda t: (t / d) ** 1.8, 0.0, Noise(19))
    n = highpass(n, lambda t: 300.0 + 7000.0 * (t / d))
    mix(n, sine(lambda t: 220.0 + 2200.0 * (t / d) ** 1.7, d,
                lambda t: 0.25 + 0.75 * (t / d)), 0.0, 0.45)
    return _tight(normalize(n, 0.85))


def drop_riser_short():
    """Quarter-second riser — a flick of tension, not a build."""
    d = 0.28
    n = noise_burst(d, lambda t: (t / d) ** 1.6, 0.0, Noise(23))
    n = highpass(n, lambda t: 500.0 + 8000.0 * (t / d))
    return _tight(normalize(n, 0.85))


def drop_downlifter():
    """Downlifter — pitch and filter falling away after the drop lands."""
    d = 0.70
    s = saw(lambda t: 1400.0 * math.exp(-4.5 * t) + 90.0, d, lambda t: math.exp(-2.6 * t))
    s = lowpass(s, lambda t: 5000.0 * math.exp(-4.0 * t) + 260.0)
    mix(s, highpass(noise_burst(d, lambda t: math.exp(-4.0 * t), 0.0, Noise(29)),
                    lambda t: 4000.0 * math.exp(-4.0 * t) + 300.0), 0.0, 0.4)
    return _tight(normalize(s, 0.85))


def drop_sweep_up():
    """Noise sweep up — a filtered whoosh straight into a hit."""
    d = 0.40
    return _tight(normalize(highpass(noise_burst(d, bell(d), 0.0, Noise(37)),
                              lambda t: 300.0 + 8000.0 * (t / d)), 0.85))


def drop_sweep_down():
    """Noise sweep down — the whoosh out of a section."""
    d = 0.40
    return _tight(normalize(highpass(noise_burst(d, bell(d), 0.0, Noise(41)),
                              lambda t: 8000.0 * (1.0 - t / d) + 300.0), 0.85))


def drop_sub():
    """Sub drop — a sine sliding from 110 Hz into the floor. Feel, not hear."""
    d = 0.80
    s = sine(lambda t: 110.0 * math.exp(-5.0 * t) + 26.0, d, perc(3.4))
    return _tight(highpass(drive(s, 1.5), 20.0))


# --------------------------------------------------------------------------- #
# Impacts and hits.
# --------------------------------------------------------------------------- #
def drop_impact():
    """Impact — the boom on the downbeat: sub, body and a slam of air."""
    d = 0.80
    s = silence(d)
    mix(s, sine(lambda t: 105.0 * math.exp(-6.0 * t) + 33.0, d, perc(4.0)), 0.0, 1.0)
    mix(s, lowpass(noise_burst(0.35, perc(9.0), 0.0, Noise(101)), 1600), 0.0, 0.45)
    mix(s, highpass(noise_burst(0.05, perc(45.0), 0.0, Noise(103)), 3000), 0.0, 0.35)
    return _tight(highpass(drive(normalize(s, 0.8), 1.9), 25.0))


def drop_impact_short():
    """Short impact — 300 ms, all punch and no tail."""
    d = 0.32
    s = silence(d)
    mix(s, sine(lambda t: 120.0 * math.exp(-11.0 * t) + 38.0, d, perc(11.0)), 0.0, 1.0)
    mix(s, highpass(noise_burst(0.04, perc(60.0), 0.0, Noise(107)), 2600), 0.0, 0.4)
    return _tight(highpass(drive(normalize(s, 0.8), 2.1), 28.0))


def drop_reverse_hit():
    """Reverse hit — an impact played backwards, sucking into the downbeat."""
    return _tight(reverse(drop_impact_short()))


def drop_reverse_crash():
    """Reverse crash — a cymbal swelling backwards, the oldest lead-in there is."""
    d = 0.75
    c = highpass(noise_burst(d, perc(6.0), 0.0, Noise(211)), 5200)
    return _tight(normalize(reverse(c), 0.85))


def drop_noise_hit():
    """Noise hit — one flat burst of white, a shutter closing."""
    d = 0.16
    return _tight(normalize(highpass(noise_burst(d, perc(30.0), 0.0, Noise(223)), 700), 0.85))


def drop_roll():
    """Snare roll — hits accelerating into the bar line."""
    d = 1.15
    out = silence(d)
    # The gaps must have a floor. Shrinking them geometrically without one is
    # a series that converges (0.115/(1-0.8) = 0.575 s) and never reaches the
    # end of the bar, so the loop never terminates.
    t, gap = 0.0, 0.115
    while t < 0.95:
        hit = highpass(noise_burst(0.09, perc(26.0), 0.0, Noise(int(t * 9000) | 1)), 1500)
        mix(hit, sine(190.0, 0.05, perc(30.0)), 0.0, 0.35)
        mix(out, hit, t, 0.5 + 0.5 * (t / 0.95))
        t += gap
        gap = max(0.030, gap * 0.84)             # each hit closer, but never zero
    return _tight(normalize(out, 0.85))


def drop_uplift_stab():
    """Uplift into a stab — a short rise that lands on a chord hit."""
    d = 0.55
    n = highpass(noise_burst(0.34, lambda t: (t / 0.34) ** 1.8, 0.0, Noise(53)),
                 lambda t: 600.0 + 7000.0 * (t / 0.34))
    out = silence(d)
    mix(out, n, 0.0, 0.55)
    hit = silence(0.21)
    for i in CHORD:
        f = note("A3") * 2 ** (i / 12.0)
        mix(hit, saw(f, 0.21, adsr(0.004, 0.09, 0.25, 0.06, 0.21)), 0.0, 0.28)
    mix(out, highpass(drive(hit, 2.0), 90.0), 0.34, 1.0)
    return _tight(normalize(out, 0.85))


def drop_air():
    """Air suction — a thin reversed whoosh, the inhale before a drop."""
    d = 0.45
    n = noise_burst(d, lambda t: (t / d) ** 2.4, 0.0, Noise(67))
    n = lowpass(highpass(n, lambda t: 900.0 + 4000.0 * (t / d)), 9000.0)
    return _tight(normalize(n, 0.8))


SOUNDS = [
    ("drop_tape_stop",      "Tape sagging to a stop",        drop_tape_stop),
    ("drop_tape_stop_fast", "250 ms tape stop",              drop_tape_stop_fast),
    ("drop_brake",          "Hand brake on the platter",     drop_brake),
    ("drop_backspin",       "Record thrown backwards",       drop_backspin),
    ("drop_spinup",         "Deck pulling up to pitch",      drop_spinup),
    ("drop_rewind",         "Pull-up rewind rush",           drop_rewind),
    ("drop_riser",          "700 ms noise-and-tone riser",   drop_riser),
    ("drop_riser_short",    "Quarter-second tension flick",  drop_riser_short),
    ("drop_downlifter",     "Falling post-drop lifter",      drop_downlifter),
    ("drop_sweep_up",       "Filtered whoosh up",            drop_sweep_up),
    ("drop_sweep_down",     "Filtered whoosh down",          drop_sweep_down),
    ("drop_sub",            "Sub sliding into the floor",    drop_sub),
    ("drop_impact",         "Full downbeat impact",          drop_impact),
    ("drop_impact_short",   "300 ms punch, no tail",         drop_impact_short),
    ("drop_reverse_hit",    "Impact played backwards",       drop_reverse_hit),
    ("drop_reverse_crash",  "Backwards cymbal swell",        drop_reverse_crash),
    ("drop_noise_hit",      "Flat white-noise burst",        drop_noise_hit),
    ("drop_roll",           "Accelerating snare roll",       drop_roll),
    ("drop_uplift_stab",    "Short rise landing on a stab",  drop_uplift_stab),
    ("drop_air",            "Thin air-suction lead-in",      drop_air),
]
