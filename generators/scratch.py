"""Scratch — turntablism one-shots: baby, chirp, transformer, flare, backspin.

A scratch is not a sound, it is a *motion*. The record carries some fixed
audio and the hand moves it under the needle, so the pitch you hear is the
platter's velocity: push it at twice speed and everything is an octave up,
pull it backwards and it plays in reverse. That is exactly how these are
built — a harmonic source read at ``f0 * speed(t)``, where a negative speed
runs the phase accumulator backwards and the sample genuinely reverses.

The other half is the crossfader. The difference between a baby scratch and a
chirp, a transformer and a flare is not the hand at all: it is *when the fader
is open*. So every sound here is one speed curve plus one gate curve, which is
how a turntablist would describe it too.
"""
import math
from synth import osc, mix, noise_burst, perc, lowpass, highpass, drive, \
    normalize, note, Noise

CATEGORY = "scratch"
GROUP = "dj"
DESCRIPTION = "Turntable scratches: baby, chirp, transformer, flare, crab, backspin."

# What is actually on the record. A vocal-ish stack scratches far better than a
# sine: the harmonics are what make the pitch change audible as *movement*.
SOURCE = ((1.0, 1.00), (2.0, 0.55), (3.0, 0.32), (4.0, 0.20),
          (5.0, 0.13), (6.0, 0.09), (8.0, 0.05))


def _platter(speed, dur, f0=None, gate=None, hiss=0.5, drv=1.5):
    """Render the record moving under the needle.

    `speed` is the platter velocity in playback-rate units (1.0 = normal,
    -1.0 = backwards at normal speed), `gate` is the crossfader, 0 or 1.
    """
    f0 = f0 or note("A2")
    out = None
    for mult, gain in SOURCE:
        v = osc("saw" if mult == 1.0 else "sine",
                lambda t, m=mult: f0 * m * speed(t), dur)
        if out is None:
            out = [x * gain for x in v]
        else:
            mix(out, v, 0.0, gain)
    if hiss:                                   # needle in the groove
        n = noise_burst(dur, None, 0.4, Noise(4242))
        mix(out, [x * min(1.0, abs(speed(i / 44100.0))) for i, x in enumerate(n)],
            0.0, 0.05 * hiss)
    if gate:
        out = [x * gate(i / 44100.0) for i, x in enumerate(out)]
    out = lowpass(out, 7000.0)
    out = highpass(drive(normalize(out, 0.75), drv), 60.0)
    # Top-and-tail. A chirp begins with the fader shut, which is the technique
    # — but a dead head means the sample triggers late on a deck, so it is
    # trimmed the way any sample-pack producer would trim it.
    lead = next((i for i, x in enumerate(out) if abs(x) > 0.002), 0)
    return out[lead:] if lead else out


def _smooth(x):
    return x * x * (3.0 - 2.0 * x)


def _push_pull(dur, top=2.0, back=1.0):
    """Forward then backward — the hand going out and coming home."""
    def sp(t):
        u = min(1.0, max(0.0, t / dur))
        return top * math.sin(math.pi * u) if u < 0.5 else -back * math.sin(math.pi * u)
    return sp


def _chop(times, dur, closed_first=False):
    """Crossfader gate: a list of switch instants across the sound."""
    def g(t):
        state = 0.0 if closed_first else 1.0
        for k, ts in enumerate(times):
            if t >= ts:
                state = 1.0 - state
        return state
    return g


def _click(g, ms=1.2):
    """Round the fader's edges — a real fader is fast, not instantaneous, and
    a true step would put a click in the sample."""
    w = ms / 1000.0

    def gg(t):
        a = g(t)
        b = g(max(0.0, t - w))
        return a if a == b else (a * 0.5 + b * 0.5)
    return gg


# --------------------------------------------------------------------------- #
# Fader open throughout — the hand alone.
# --------------------------------------------------------------------------- #
def scratch_baby():
    """Baby scratch — forward and back, fader never touched. The first one
    anybody learns, and the shape every other scratch is built on."""
    return _platter(_push_pull(0.36), 0.36)


def scratch_baby_fast():
    """Fast baby — the same motion at double speed, an octave higher."""
    return _platter(_push_pull(0.20, top=3.0, back=1.6), 0.20)


def scratch_drag(): 
    """Drag — the record pushed slowly, so it growls well below pitch."""
    return _platter(lambda t: 0.45 * math.sin(math.pi * min(1.0, t / 0.55)), 0.55)


def scratch_stab():
    """Stab — one short forward shove and nothing back. The full stop."""
    return _platter(lambda t: 2.6 * math.exp(-9.0 * t), 0.22)


def scratch_tear():
    """Tear — forward, hold, forward again: the pull broken into two steps."""
    def sp(t):
        if t < 0.09: return 1.9
        if t < 0.15: return 0.25
        return -1.6
    return _platter(sp, 0.34)


def scratch_scribble():
    """Scribble — the forearm shaking, a fast blur of tiny pushes."""
    return _platter(lambda t: 2.2 * math.sin(2 * math.pi * 17.0 * t), 0.42)


def scratch_hydro():
    """Hydroplane — the thumb dragging on the record, a wavering hold."""
    return _platter(lambda t: 0.7 + 0.5 * math.sin(2 * math.pi * 30.0 * t), 0.40,
                    hiss=1.4)


# --------------------------------------------------------------------------- #
# Fader work — the same hand motion, different cuts.
# --------------------------------------------------------------------------- #
def scratch_chirp():
    """Chirp — the fader closes as the record is released, so the sound is
    squeezed off at both ends and the pitch bends inside the gap."""
    return _platter(_push_pull(0.30), 0.30,
                    gate=_click(_chop([0.015, 0.13, 0.155, 0.27], 0.30,
                                      closed_first=True)))


def scratch_transformer():
    """Transformer — the record runs steadily while the fader chops it into
    even pieces. All rhythm, no pitch movement."""
    return _platter(lambda t: 1.35, 0.34,
                    gate=_click(_chop([0.0, 0.05, 0.085, 0.135, 0.17, 0.22,
                                       0.255, 0.305], 0.34, closed_first=True)))


def scratch_flare():
    """Flare — one fader click in the middle of a forward push, splitting it
    into two notes without stopping the hand."""
    return _platter(_push_pull(0.30, top=2.2), 0.30,
                    gate=_click(_chop([0.10, 0.135], 0.30)))


def scratch_flare_2():
    """Two-click flare — three sounds out of a single motion."""
    return _platter(_push_pull(0.34, top=2.2), 0.34,
                    gate=_click(_chop([0.075, 0.105, 0.175, 0.205], 0.34)))


def scratch_crab():
    """Crab — four fingers rippling across the fader inside one push. The
    fastest thing a hand can do to a crossfader."""
    return _platter(_push_pull(0.30, top=2.0), 0.30,
                    gate=_click(_chop([0.05, 0.075, 0.10, 0.125, 0.15, 0.175,
                                       0.20, 0.225], 0.30)))


def scratch_orbit():
    """Orbit — a flare carried through the backwards half as well, so the
    pattern repeats symmetrically."""
    return _platter(_push_pull(0.40, top=2.0), 0.40,
                    gate=_click(_chop([0.07, 0.10, 0.27, 0.30], 0.40)))


def scratch_chop():
    """Chop — the fader closed on the return, so only the forward push speaks."""
    return _platter(_push_pull(0.30, top=2.2), 0.30,
                    gate=_click(_chop([0.155], 0.30)))


# --------------------------------------------------------------------------- #
# Platter moves — spinning the record itself.
# --------------------------------------------------------------------------- #
def scratch_backspin():
    """Backspin — the record thrown backwards and left to run down."""
    return _platter(lambda t: -6.0 * math.exp(-4.5 * t) - 0.3, 0.55, hiss=1.2)


def scratch_backspin_short():
    """Quick backspin — a half turn, straight into the next track."""
    return _platter(lambda t: -7.5 * math.exp(-11.0 * t), 0.28, hiss=1.2)


def scratch_spinup():
    """Spin-up — the motor pulling the record from stopped up to speed."""
    return _platter(lambda t: 2.2 * _smooth(min(1.0, t / 0.45)), 0.50, hiss=1.0)


def scratch_brake():
    """Brake — the platter stopped by hand, pitch falling into the floor."""
    return _platter(lambda t: max(0.02, 1.3 * (1.0 - _smooth(min(1.0, t / 0.30)))),
                    0.36, hiss=1.0)


def scratch_rub():
    """Rub — the needle worked slowly back and forth, all groove noise."""
    return _platter(lambda t: 0.8 * math.sin(2 * math.pi * 4.5 * t), 0.45,
                    hiss=2.2, drv=1.2)


def scratch_zigzag():
    """Zig-zag — three quick alternations, the hand never settling."""
    return _platter(lambda t: 2.0 * math.sin(2 * math.pi * 6.5 * t), 0.42)


SOUNDS = [
    ("scratch_baby",          "Forward-back baby scratch",     scratch_baby),
    ("scratch_baby_fast",     "Double-speed baby scratch",     scratch_baby_fast),
    ("scratch_drag",          "Slow growling drag",            scratch_drag),
    ("scratch_stab",          "Single forward stab",           scratch_stab),
    ("scratch_tear",          "Two-step tear",                 scratch_tear),
    ("scratch_scribble",      "Fast scribble blur",            scratch_scribble),
    ("scratch_hydro",         "Hydroplane thumb drag",         scratch_hydro),
    ("scratch_chirp",         "Fader-squeezed chirp",          scratch_chirp),
    ("scratch_transformer",   "Even fader chopping",           scratch_transformer),
    ("scratch_flare",         "One-click flare",               scratch_flare),
    ("scratch_flare_2",       "Two-click flare",               scratch_flare_2),
    ("scratch_crab",          "Four-finger crab",              scratch_crab),
    ("scratch_orbit",         "Symmetrical orbit flare",       scratch_orbit),
    ("scratch_chop",          "Forward only, return cut",      scratch_chop),
    ("scratch_backspin",      "Full backspin run-down",        scratch_backspin),
    ("scratch_backspin_short", "Quick half-turn backspin",     scratch_backspin_short),
    ("scratch_spinup",        "Motor pulling up to speed",     scratch_spinup),
    ("scratch_brake",         "Hand brake into the floor",     scratch_brake),
    ("scratch_rub",           "Slow needle rub",               scratch_rub),
    ("scratch_zigzag",        "Three quick alternations",      scratch_zigzag),
]
