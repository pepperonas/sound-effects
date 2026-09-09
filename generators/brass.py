"""Brass — synthetic horn stabs and 2–5 note fanfare motifs.

Deliberately *not* an orchestral recording: these are hard-driven electronic
brass hits — the "DÜB-DÜB" / "DA-DA" stab a modern pop or trap record throws
on a downbeat. The value is in the motifs: each file is a complete little
figure (call, answer, fanfare, riff) you can drop on a beat as one sample.

Each note is built the way a subtractive synth fakes a brass section: detuned
saws plus a hollow square, a short lip-scoop into the pitch, and above all a
filter that snaps open on the attack and settles back — that opening bark is
what the ear reads as "brass". A tanh drive glues the layers into one
compressed hit. Everything is rooted on C so it sits with the bass and chord
kits; minor figures use C minor, fanfares C major.
"""
import math
from synth import (saw, square, triangle, noise_burst, mix,
                   adsr, perc, lowpass, highpass, drive, note, Noise)
from ._music import STEP, filter_env, motif as _motif

CATEGORY = "brass"
GROUP = "music"
DESCRIPTION = "Synthetic brass stabs and 2-5 note fanfare motifs, rooted on C."

# Timbre presets — passed straight through to _stab().
BRIGHT = dict(bright=1.45, drive_amt=1.9)
DARK = dict(bright=0.55, drive_amt=1.6, sub=1.3, air=0.4)
AGGRO = dict(bright=1.75, drive_amt=2.6, detune=0.010, attack=0.003)
SOFT = dict(bright=0.85, drive_amt=1.0, attack=0.022, air=1.7, sub=0.8)
WIDE = dict(bright=1.25, drive_amt=1.7, detune=0.018)


def _stab(pitch, dur=0.19, v=1.0, bright=1.0, detune=0.007, drive_amt=1.8,
          sub=1.0, air=1.0, attack=0.006, rel=0.07):
    """One brass note: detuned saws + square + sub through the barking filter."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + rel
    # Lip scoop — starts a touch flat and pulls onto the note within ~10 ms.
    f = lambda t: f0 * (1.0 - 0.030 * math.exp(-t / 0.009))
    env = adsr(attack, min(0.06, dur * 0.5), 0.45, rel, n)
    # Below ~100 Hz an octave-down layer is inaudible rumble — double at pitch.
    sub_mult = 0.5 if f0 >= 100.0 else 1.0

    g_det, g_sq, g_sub = 0.72, 0.30, 0.45 * sub
    g_sheen, g_air = 0.26 * bright, 0.09 * air

    s = saw(f, n, env)
    mix(s, saw(lambda t: f(t) * (1 + detune), n, env), 0.0, g_det)
    mix(s, saw(lambda t: f(t) * (1 - detune), n, env), 0.0, g_det)
    mix(s, square(f, n, env), 0.0, g_sq)                          # hollow horn
    mix(s, triangle(lambda t: f(t) * sub_mult, n, env), 0.0, g_sub)
    mix(s, saw(lambda t: f(t) * 2, n, perc(13)), 0.0, g_sheen)    # sheen
    mix(s, highpass(noise_burst(0.03, perc(90), 0.0, Noise(4211)), 2600),
        0.0, g_air)                                               # breath chiff

    lo = min(900.0, f0 * 1.6)
    span = (f0 * 13.0 + 1250.0) * bright * (0.55 + 0.45 * v)
    s = lowpass(s, filter_env(lo, span))
    # Give the tanh room to be expressive. Un-scaled, the summed layers hit it
    # at ~2.4 and *every* preset saturates flat to 1.0 — which silently kills
    # both the velocity response and the difference between SOFT and AGGRO.
    head = 0.85 / (1.0 + 2 * g_det + g_sq + g_sub + g_sheen)
    s = drive([x * head for x in s], drive_amt * (0.72 + 0.28 * v))
    return highpass(s, min(80.0, f0 * 0.55))


# --------------------------------------------------------------------------- #
# Single stabs — the building blocks, one note each.
# --------------------------------------------------------------------------- #
def brass_stab():
    """Signature brass stab — one bright C3 hit, the core one-shot."""
    return _motif(_stab, [(0, "C3", 3, 1.0)], **BRIGHT)


def brass_stab_low():
    """Low brass stab — C2, dark and heavy, for weight under a mid stab."""
    return _motif(_stab, [(0, "C2", 4, 1.0)], **DARK)


def brass_stab_soft():
    """Soft brass stab — C3 with a slower lip attack, warm and unforced."""
    return _motif(_stab, [(0, "C3", 4, 0.7)], **SOFT)


# --------------------------------------------------------------------------- #
# Two-note figures.
# --------------------------------------------------------------------------- #
def brass_duo_up():
    """Two stabs a fifth up — C3 → G3, even eighths, the classic lift."""
    return _motif(_stab, [(0, "C3", 2, 0.85), (2, "G3", 3, 1.0)], **BRIGHT)


def brass_duo_down():
    """Two stabs a fifth down — G3 → C3, even eighths, lands home."""
    return _motif(_stab, [(0, "G3", 2, 0.9), (2, "C3", 3, 1.0)], **BRIGHT)


def brass_dub_dub():
    """"DÜB-DÜB" — two hard C3 stabs a sixteenth apart, aggressive and tight."""
    return _motif(_stab, [(0, "C3", 1, 0.95), (1, "C3", 2, 1.0)], **AGGRO)


def brass_da_da():
    """"DA-DA" — Eb3 → C3, short then long-accented, a minor third down."""
    return _motif(_stab, [(0, "Eb3", 2, 0.85), (2, "C3", 4, 1.0)], **BRIGHT)


def brass_double_hit():
    """Two C3 stabs a quarter apart — a rest between them, wide and detuned."""
    return _motif(_stab, [(0, "C3", 2, 1.0), (4, "C3", 4, 0.95)], **WIDE)


def brass_octave():
    """Octave leap — C3 → C4, short then held, wide detune for size."""
    return _motif(_stab, [(0, "C3", 2, 0.85), (2, "C4", 5, 1.0)], **WIDE)


def brass_fanfare_2():
    """Bugle fourth — G3 pickup into a long C4, the two-note fanfare."""
    return _motif(_stab, [(0, "G3", 1, 0.8), (1, "C4", 6, 1.0)], **BRIGHT)


# --------------------------------------------------------------------------- #
# Three-note figures.
# --------------------------------------------------------------------------- #
def brass_rise_3():
    """Three rising stabs — C3 Eb3 G3, the C minor triad in even eighths."""
    return _motif(_stab, [(0, "C3", 2, 0.8), (2, "Eb3", 2, 0.9), (4, "G3", 4, 1.0)])


def brass_fall_3():
    """Three falling stabs — G3 Eb3 C3, the minor triad down to the root."""
    return _motif(_stab, [(0, "G3", 2, 0.9), (2, "Eb3", 2, 0.85), (4, "C3", 4, 1.0)])


def brass_fanfare_3():
    """Short-short-LONG major fanfare — C3 E3 G3, triumphant and bright."""
    return _motif(_stab, [(0, "C3", 1, 0.85), (1, "E3", 1, 0.9), (2, "G3", 7, 1.0)],
                  **BRIGHT)


def brass_call():
    """Question figure — long C3, then F3 G3 rising to the unresolved fifth."""
    return _motif(_stab, [(0, "C3", 4, 1.0), (4, "F3", 2, 0.85), (6, "G3", 3, 0.9)])


def brass_answer():
    """Response to brass_call — G3 F3 fall back into a long C3, resolved."""
    return _motif(_stab, [(0, "G3", 2, 0.9), (2, "F3", 2, 0.85), (4, "C3", 6, 1.0)])


# --------------------------------------------------------------------------- #
# Longer motifs.
# --------------------------------------------------------------------------- #
def brass_triumph():
    """Da-da-da-DAAA — three short G3 hits into a held C4 a fourth above."""
    return _motif(_stab, [(0, "G3", 1, 0.85), (2, "G3", 1, 0.85), (4, "G3", 1, 0.9),
                   (6, "C4", 8, 1.0)], **BRIGHT)


def brass_riff_4():
    """Syncopated minor riff — C3 Eb3 C3 then a low Bb2 off the beat."""
    return _motif(_stab, [(0, "C3", 2, 1.0), (2, "Eb3", 1, 0.8), (3, "C3", 1, 0.85),
                   (5, "Bb2", 4, 0.95)], **AGGRO)


def brass_stomp():
    """Low marching stomp — C2 C2 Eb2, heavy and dark, sits under a beat."""
    return _motif(_stab, [(0, "C2", 2, 1.0), (2, "C2", 2, 0.9), (4, "Eb2", 5, 1.0)],
                  **DARK)


def brass_climb_5():
    """Five-note climb — C3 Eb3 G3 Bb3 into a held C4, a run into the hit."""
    return _motif(_stab, [(0, "C3", 1, 0.75), (1, "Eb3", 1, 0.8), (2, "G3", 1, 0.85),
                   (3, "Bb3", 1, 0.9), (4, "C4", 9, 1.0)], **BRIGHT)


SOUNDS = [
    ("brass_stab",       "Bright single brass stab (C3)",   brass_stab),
    ("brass_stab_low",   "Dark heavy low stab (C2)",        brass_stab_low),
    ("brass_stab_soft",  "Soft warm stab for layering",     brass_stab_soft),
    ("brass_duo_up",     "Two stabs, fifth up",             brass_duo_up),
    ("brass_duo_down",   "Two stabs, fifth down",           brass_duo_down),
    ("brass_dub_dub",    "Two fast hard stabs (DÜB-DÜB)",   brass_dub_dub),
    ("brass_da_da",      "Short-long minor third (DA-DA)",  brass_da_da),
    ("brass_double_hit", "Two wide stabs with a gap",       brass_double_hit),
    ("brass_octave",     "Octave leap C3 to C4",            brass_octave),
    ("brass_fanfare_2",  "Two-note bugle fourth fanfare",   brass_fanfare_2),
    ("brass_rise_3",     "Rising minor triad, three stabs", brass_rise_3),
    ("brass_fall_3",     "Falling minor triad, three stabs", brass_fall_3),
    ("brass_fanfare_3",  "Short-short-long major fanfare",  brass_fanfare_3),
    ("brass_call",       "Rising question figure",          brass_call),
    ("brass_answer",     "Falling answer, resolves home",   brass_answer),
    ("brass_triumph",    "Three hits into a held octave",   brass_triumph),
    ("brass_riff_4",     "Syncopated four-note minor riff", brass_riff_4),
    ("brass_stomp",      "Low three-note marching stomp",   brass_stomp),
    ("brass_climb_5",    "Five-note climb into a held hit", brass_climb_5),
]
