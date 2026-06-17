"""Chords — stacked-note stabs for instant harmony (all rooted on C).

Drop one on a beat for an off-beat house stab, or hold for a progression.
Built by stacking detuned saws at chord intervals through a low-pass.
"""
from synth import saw, sine, mix, silence, adsr, perc, lowpass, drive, chord


def _stab(intervals, dur=0.4, root="C3", cutoff=3000, sustained=False):
    """Stack detuned saws at the given semitone intervals above the root."""
    freqs = chord(root, intervals)
    env = (adsr(0.02, 0.1, 0.85, 0.25, dur) if sustained else perc(8))
    s = silence(dur + (0.1 if sustained else 0.0))
    for f in freqs:
        mix(s, saw(f, dur, env), 0.0, 0.32)
        mix(s, saw(f * 1.006, dur, env), 0.0, 0.32)         # detune layer
    return drive(lowpass(s, cutoff), 1.3)


def major():
    """Major triad stab (C E G)."""
    return _stab((0, 4, 7))


def minor():
    """Minor triad stab (C Eb G)."""
    return _stab((0, 3, 7))


def maj7():
    """Major 7th — lush, jazzy (C E G B)."""
    return _stab((0, 4, 7, 11), cutoff=3500)


def min7():
    """Minor 7th — smooth, deep-house flavoured (C Eb G Bb)."""
    return _stab((0, 3, 7, 10), cutoff=3200)


def dom7():
    """Dominant 7th — bluesy tension (C E G Bb)."""
    return _stab((0, 4, 7, 10))


def sus4():
    """Suspended 4th — open, unresolved (C F G)."""
    return _stab((0, 5, 7))


def power():
    """Power chord — root + fifth + octave, fat and tonal-neutral."""
    return _stab((0, 7, 12), root="C2", cutoff=2400)


def major_pad():
    """Sustained major pad chord — slow, lush hold."""
    return _stab((0, 4, 7, 12), dur=1.2, cutoff=2600, sustained=True)


def minor_pad():
    """Sustained minor pad chord — moody hold."""
    return _stab((0, 3, 7, 12), dur=1.2, cutoff=2400, sustained=True)


CATEGORY = "chords"
GROUP = "music"
DESCRIPTION = "Major, minor, 7th, sus and power chord stabs + pads (rooted on C)."

SOUNDS = [
    ("major",      "Major triad stab",            major),
    ("minor",      "Minor triad stab",            minor),
    ("maj7",       "Lush major 7th stab",         maj7),
    ("min7",       "Smooth minor 7th stab",       min7),
    ("dom7",       "Bluesy dominant 7th stab",    dom7),
    ("sus4",       "Open suspended-4th stab",     sus4),
    ("power",      "Root-fifth-octave power chord", power),
    ("major_pad",  "Sustained major pad chord",   major_pad),
    ("minor_pad",  "Sustained minor pad chord",   minor_pad),
]
