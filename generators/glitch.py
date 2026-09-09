"""Glitch — digital and analogue failure, used on purpose.

Every one of these is a machine doing something wrong, which is why they work
as transitions: the ear knows the sound of a broken signal and reads it as an
interruption rather than as music.

The two families fail in opposite directions. *Digital* faults are quantisers
running out of resolution — a bit-crusher throws away amplitude steps, a
sample-rate reducer throws away time, and both add harmonics that were never
in the source, which is why they sound harsh rather than dull. *Analogue*
faults are mechanical: a warped record wanders in pitch, a worn tape flutters,
a dirty groove clicks. So the digital ones here are built by damaging a clean
signal, and the analogue ones by moving it.
"""
import math
from synth import (sine, saw, square, triangle, noise_burst, mix, silence, perc,
                   adsr, lowpass, highpass, drive, reverse, normalize, note, Noise)
from ._music import additive

CATEGORY = "glitch"
GROUP = "dj"
DESCRIPTION = "Digital and analogue faults: stutter, bit-crush, static, tape wow."

CHORD = (0, 3, 7, 12)


def _source(dur, root="C4", bright=1.0):
    """Something clean to break: a chord with enough harmonics to damage."""
    out = silence(dur)
    f0 = note(root)
    for i in CHORD:
        f = f0 * 2 ** (i / 12.0)
        mix(out, saw(f, dur, adsr(0.004, 0.10, 0.55, 0.06, dur)), 0.0, 0.26)
    return lowpass(out, 5000.0 * bright)


def _crush(xs, bits=4):
    """Bit reduction: fewer amplitude steps than the signal needs."""
    levels = max(2, 2 ** bits)
    return [round(x * levels) / levels for x in xs]


def _decimate(xs, factor=12):
    """Sample-and-hold: fewer time steps than the signal needs."""
    out = [0.0] * len(xs)
    held = 0.0
    for i, x in enumerate(xs):
        if i % factor == 0:
            held = x
        out[i] = held
    return out


def _stutter(xs, slice_s, repeats, decay=1.0):
    """Buffer repeat: one slice held and fired again."""
    n = int(slice_s * 44100)
    piece = xs[:n]
    out = []
    for k in range(repeats):
        g = decay ** k
        out.extend(x * g for x in piece)
    return out


def _tight(xs):
    lead = next((i for i, x in enumerate(xs) if abs(x) > 0.002), 0)
    return xs[lead:] if lead else xs


def _out(xs, peak=0.85):
    return _tight(normalize(xs, peak))


# --------------------------------------------------------------------------- #
# Buffer faults — time repeating or vanishing.
# --------------------------------------------------------------------------- #
def glitch_stutter():
    """Stutter — one 60 ms slice fired six times, the buffer stuck."""
    return _out(_stutter(_source(0.5), 0.060, 6))


def glitch_stutter_fast():
    """Fast stutter — 25 ms slices, fast enough to become a pitch of its own."""
    return _out(_stutter(_source(0.5), 0.025, 14))


def glitch_stutter_fade():
    """Stutter dying away — each repeat quieter, the buffer running out."""
    return _out(_stutter(_source(0.5), 0.055, 8, decay=0.80))


def glitch_stutter_accel():
    """Accelerating stutter — the slices get shorter, so it speeds up."""
    src = _source(0.6)
    out, sl = [], 0.085
    while sl > 0.018:
        out.extend(src[:int(sl * 44100)])
        sl *= 0.80
    return _out(out)


def glitch_reverse_stutter():
    """Every other repeat backwards — the buffer read in both directions."""
    src = _source(0.5)
    n = int(0.055 * 44100)
    out = []
    for k in range(7):
        piece = src[:n]
        out.extend(reverse(piece) if k % 2 else piece)
    return _out(out)


def glitch_dropout():
    """Dropout — the signal cut out and back in, twice. A dead cable."""
    xs = _source(0.55)
    def g(i):
        t = i / 44100.0
        return 0.0 if (0.11 < t < 0.17) or (0.29 < t < 0.33) else 1.0
    return _out([x * g(i) for i, x in enumerate(xs)])


def glitch_gate():
    """Gated chord — chopped into even sixteenths, the trance gate."""
    xs = _source(0.60)
    step = 0.0375
    return _out([x * (1.0 if (i / 44100.0) % (2 * step) < step else 0.0)
                 for i, x in enumerate(xs)])


# --------------------------------------------------------------------------- #
# Quantiser faults — resolution running out.
# --------------------------------------------------------------------------- #
def glitch_bitcrush():
    """Bit-crush — four bits of amplitude, so the quiet parts turn to gravel."""
    return _out(_crush(_source(0.35), bits=4))


def glitch_bitcrush_hard():
    """Two bits — barely a waveform left, all harmonics."""
    return _out(_crush(_source(0.30), bits=2))


def glitch_downsample():
    """Sample-rate reduction — aliasing, the sound of a machine too slow."""
    return _out(_decimate(_source(0.35), factor=14))


def glitch_crush_sweep():
    """Resolution collapsing across the sound — clean into gravel."""
    xs = _source(0.55)
    out = []
    for i, x in enumerate(xs):
        bits = max(2, int(10 - 8 * i / len(xs)))
        lv = 2 ** bits
        out.append(round(x * lv) / lv)
    return _out(out)


def glitch_alias():
    """Aliasing sweep — a rising tone folded back down by a slow sampler."""
    s = sine(lambda t: 800.0 + 9000.0 * (t / 0.45), 0.45, perc(3.0))
    return _out(_decimate(s, factor=9))


# --------------------------------------------------------------------------- #
# Mechanical faults — the medium itself failing.
# --------------------------------------------------------------------------- #
def glitch_vinyl_click():
    """Vinyl click — one piece of dirt in the groove, plus surface noise."""
    n = lowpass(noise_burst(0.22, perc(9.0), 0.0, Noise(5)), 3800)
    out = [x * 0.16 for x in n]
    mix(out, highpass(noise_burst(0.004, perc(400.0), 0.0, Noise(7)), 2200), 0.0, 1.0)
    return _out(out)


def glitch_crackle():
    """Crackle — a worn record: hiss with pops scattered through it."""
    n = lowpass(noise_burst(0.60, lambda t: 1.0, 0.0, Noise(13)), 4200)
    out = [x * 0.18 for x in n]
    pop = Noise(17)
    for i in range(len(out)):
        if abs(pop()) > 0.9955:
            out[i] += pop() * 0.9
    return _out(out)


def glitch_static():
    """Static burst — the signal replaced by noise for a quarter second."""
    n = highpass(noise_burst(0.26, adsr(0.002, 0.02, 0.85, 0.05, 0.26), 0.0,
                             Noise(19)), 500)
    return _out(_crush(n, bits=5))


def glitch_tape_wow():
    """Tape wow — a stretched reel, the pitch wandering slowly."""
    f = lambda t: 1.0 + 0.045 * math.sin(2 * math.pi * 2.4 * t)
    out = silence(0.65)
    f0 = note("C4")
    for i in CHORD:
        ff = f0 * 2 ** (i / 12.0)
        mix(out, saw(lambda t, _f=ff: _f * f(t), 0.65,
                     adsr(0.01, 0.10, 0.7, 0.10, 0.65)), 0.0, 0.26)
    return _out(lowpass(out, 4200.0))


def glitch_flutter():
    """Flutter — the same fault an octave faster: a worn capstan."""
    f = lambda t: 1.0 + 0.020 * math.sin(2 * math.pi * 17.0 * t)
    out = silence(0.50)
    f0 = note("C4")
    for i in CHORD:
        ff = f0 * 2 ** (i / 12.0)
        mix(out, saw(lambda t, _f=ff: _f * f(t), 0.50,
                     adsr(0.01, 0.08, 0.7, 0.08, 0.50)), 0.0, 0.26)
    return _out(lowpass(out, 4200.0))


def glitch_cd_skip():
    """CD skip — the same 40 ms read three times, then the disc gives up."""
    src = _source(0.6)
    n = int(0.040 * 44100)
    piece = src[int(0.10 * 44100):int(0.10 * 44100) + n]
    # A real skip announces itself with the read error, and a sample that
    # opens on its quietest block does not trigger with any punch.
    out = list(_crush(highpass(noise_burst(0.006, perc(300.0), 0.0, Noise(23)),
                               3000), bits=3))
    for _ in range(3):
        out.extend(piece)
    out.extend(_crush(src[:int(0.06 * 44100)], bits=3))
    return _out(out, peak=0.85)


def glitch_telephone():
    """Telephone — the chord through a 300-3400 Hz band, thin and nasal."""
    xs = _source(0.40, bright=1.4)
    return _out(lowpass(highpass(xs, 620.0), 2600.0))


def glitch_megaphone():
    """Megaphone — the same band, driven until it distorts and honks."""
    xs = _source(0.40, bright=1.4)
    # Filter AFTER the drive as well: hard saturation is asymmetric and leaves
    # a DC step behind it (measured +0.02 with the highpass only in front).
    return _out(highpass(drive(lowpass(highpass(xs, 700.0), 2800.0), 6.0), 400.0))


SOUNDS = [
    ("glitch_stutter",         "Buffer stuck, six repeats",   glitch_stutter),
    ("glitch_stutter_fast",    "25 ms slices, near-pitched",  glitch_stutter_fast),
    ("glitch_stutter_fade",    "Stutter dying away",          glitch_stutter_fade),
    ("glitch_stutter_accel",   "Accelerating slice repeat",   glitch_stutter_accel),
    ("glitch_reverse_stutter", "Alternating forward/back",    glitch_reverse_stutter),
    ("glitch_dropout",         "Signal cutting in and out",   glitch_dropout),
    ("glitch_gate",            "Sixteenth-gated chord",       glitch_gate),
    ("glitch_bitcrush",        "Four-bit gravel",             glitch_bitcrush),
    ("glitch_bitcrush_hard",   "Two-bit, barely a waveform",  glitch_bitcrush_hard),
    ("glitch_downsample",      "Sample-rate reduction",       glitch_downsample),
    ("glitch_crush_sweep",     "Resolution collapsing",       glitch_crush_sweep),
    ("glitch_alias",           "Folded aliasing sweep",       glitch_alias),
    ("glitch_vinyl_click",     "Single groove click",         glitch_vinyl_click),
    ("glitch_crackle",         "Worn-record crackle",         glitch_crackle),
    ("glitch_static",          "Quarter-second static burst", glitch_static),
    ("glitch_tape_wow",        "Slow tape pitch wander",      glitch_tape_wow),
    ("glitch_flutter",         "Fast capstan flutter",        glitch_flutter),
    ("glitch_cd_skip",         "Disc reading the same block", glitch_cd_skip),
    ("glitch_telephone",       "Narrow-band telephone",       glitch_telephone),
    ("glitch_megaphone",       "Driven honking megaphone",    glitch_megaphone),
]
