"""Shared machinery for the melodic music categories.

Not a category itself — `generators.discover()` skips modules whose name starts
with "_", so this file is importable by the instrument modules without ever
turning into an output folder.

Every melodic category answers the same two questions in the same way:

    voice(pitch, dur, v=…)   what one note of this instrument sounds like
    motif(voice, steps)      when those notes happen

Only the first is instrument-specific. Keeping the second here means a fanfare,
a guitar riff and a harp arpeggio are all written as the same little table of
events, and a fix to the sequencer reaches all of them at once.
"""
import math
from synth import SR, osc, mix, note

# One step = a 1/16 at 140 BPM. Motif rhythms are written in these steps, so a
# figure reads as musical note values instead of as raw seconds.
STEP = 60.0 / 140.0 / 4.0


def motif(voice, steps, step=STEP, tail=0.025, spread=0.0, **kw):
    """Render a list of events with `voice` into one buffer.

    Each event is ``(start, pitch, length, velocity)`` — start and length in
    1/16th steps — with an optional 5th element, a dict of per-note overrides
    for the voice (one muted note in an otherwise open riff, say).

    `pitch` is a note name (or Hz), or a tuple of them for a chord. `spread`
    staggers a chord's notes by that many seconds: a guitar strum, a rolled
    piano chord, a harp roll. A negative value strums from the top down.

    The buffer grows with the notes, so it begins exactly on the first attack
    and runs to the end of the last release — no leading silence, no truncated
    tail — plus `tail` seconds for write_wav's fade to land on.
    """
    out = []
    for ev in steps:
        start, pitch, length, v = ev[:4]
        over = ev[4] if len(ev) > 4 else {}
        notes = list(pitch) if isinstance(pitch, (tuple, list)) else [pitch]
        if spread < 0:
            notes.reverse()
        # Voices add incoherently, so a chord's RMS grows as sqrt(n). Scaling by
        # n**-0.6 leaves a chord slightly bigger than a single note instead of
        # n times louder, which would make every single note in the same motif
        # vanish once the file is normalised.
        g = (0.55 + 0.45 * v) * len(notes) ** -0.6
        for k, p in enumerate(notes):
            mix(out, voice(p, length * step, v=v, **dict(kw, **over)),
                start * step + k * abs(spread), g)
    out.extend([0.0] * int(tail * SR))
    return out


def glide(a, b, hold=0.05, rise=0.13):
    """Pitch curve f(t): hold `a`, travel to `b` over `rise` s, stay there.

    Smoothstep rather than linear because a finger sliding on a string
    accelerates out of the first note and settles into the second; a straight
    ramp reads as a synthesiser portamento, not as a played slide.
    """
    f0 = note(a) if isinstance(a, str) else float(a)
    f1 = note(b) if isinstance(b, str) else float(b)

    def f(t):
        if t <= hold:
            return f0
        if t >= hold + rise:
            return f1
        x = (t - hold) / rise
        return f0 + (f1 - f0) * (x * x * (3.0 - 2.0 * x))
    return f


def filter_env(lo, span, rise=0.010, fall=0.085, sustain=0.22):
    """Cutoff f(t): snaps open on the attack, then settles to a held brightness.

    The signature gesture of a blown or bowed instrument — the ear reads that
    opening bark as "something was excited", which no static filter gives you.

    (1-e^-t/rise)·e^-t/fall peaks well below 1, so it is normalised by its own
    maximum — otherwise `span` would not mean what it says.
    """
    u = rise / (rise + fall)
    gmax = (1.0 - u) * u ** (rise / fall)
    bump = 1.0 - sustain

    def cut(t):
        opening = 1.0 - math.exp(-t / rise)
        bark = opening * math.exp(-t / fall) / gmax
        return min(17000.0, lo + span * (bump * bark + sustain * opening))
    return cut


def additive(f0, dur, partials, attack=0.002, vib=None):
    """Sum decaying sine partials in a single pass.

    `partials` is a list of ``(multiplier, gain, decay_rate)``; each is a sine
    at ``f0 * multiplier`` fading as ``exp(-rate*t)``. The decay is applied by
    multiplying the running amplitude once per sample instead of calling
    math.exp per sample per partial, which is what makes a ten-partial piano
    note cheap enough to stack four of them into a chord.

    A struck string is exactly this: a set of partials that are NOT quite
    harmonic and that die at different speeds — the top ones first. Both of
    those are why a piano reads as a piano and not as an organ.

    `vib=(rate, depth)` bends every partial together, which is what a singer or
    a flautist actually does — the whole tone moves, not each overtone
    separately. It costs one extra sine per sample no matter how many partials
    there are, because they all share the same modulation.
    """
    n = int(dur * SR)
    if n <= 0:
        return []
    k = len(partials)
    ph = [0.0] * k
    dph = [2.0 * math.pi * f0 * m / SR for m, _, _ in partials]
    amp = [g for _, g, _ in partials]
    dec = [math.exp(-r / SR) for _, _, r in partials]
    ramp = max(1, int(attack * SR))
    out = [0.0] * n
    vr, vd = vib if vib else (0.0, 0.0)
    w = 2.0 * math.pi * vr / SR
    for i in range(n):
        bend = 1.0 + vd * math.sin(w * i) if vd else 1.0
        v = 0.0
        for j in range(k):
            ph[j] += dph[j] * bend
            v += amp[j] * math.sin(ph[j])
            amp[j] *= dec[j]
        out[i] = v * (i / ramp) if i < ramp else v      # no click on the attack
    return out


def stack(shape, freq, dur, env, detune=0.007, voices=3, side=0.72):
    """Detuned unison stack — the core of any ensemble timbre.

    `detune` is the TOTAL half-spread, not a per-voice step: the voices are
    distributed evenly inside it, so adding players thickens the sound instead
    of widening it. Getting that wrong is audible — six voices at multiples of
    0.006 put the outer pair 31 cents out, which reads as out of tune rather
    than as an ensemble. A real section spreads about ten cents.

    Voices alternate sharp/flat around the centre pitch, so the beating stays
    symmetrical and the perceived pitch does not drift as `voices` grows.
    """
    base = freq if callable(freq) else (lambda t, _f=freq: _f)
    out = osc(shape, freq, dur, env)
    rings = max(1, (voices - 1 + 1) // 2)                 # how many pairs out
    for k in range(1, voices):
        d = detune * (((k + 1) // 2) / rings) * (1 if k % 2 else -1)
        mix(out, osc(shape, lambda t, _d=d: base(t) * (1 + _d), dur, env), 0.0, side)
    return out
