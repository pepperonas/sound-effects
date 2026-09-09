"""Piano — acoustic piano: chords, arpeggios, runs and cadences.

Built additively, because that is what a struck string actually is: a stack of
partials that die at different speeds. Two details do almost all the work of
making it read as a piano rather than as an organ:

* **Inharmonicity.** A real string is stiff, so its partials sit progressively
  sharp — f(n) = n*f0*sqrt(1 + B*n^2). That "stretch" is why piano tuners tune
  the top of the instrument sharp and the bottom flat, and why a perfectly
  harmonic stack sounds synthetic. B rises as the strings get shorter and
  thicker, so the bass is far more inharmonic than the treble.
* **Partials die top-down.** The bright clang of the hammer is gone within a
  few hundred milliseconds while the fundamental rings on for seconds.

On top of that a hammer thump, and a second set of slightly detuned partials
for the two or three strings a real piano has per note — that beating is the
shimmer you hear on a held chord.
"""
import math
from synth import noise_burst, mix, perc, lowpass, highpass, note, Noise
from ._music import motif, additive

CATEGORY = "piano"
GROUP = "music"
DESCRIPTION = "Acoustic piano: chords, arpeggios, runs, cadences and stride figures."

MAJ = ("C3", "E3", "G3")
MIN = ("C3", "Eb3", "G3")


def _piano(pitch, dur, v=1.0, ring=1.1, bright=1.0):
    """One struck note. `ring` is how long the string sounds past its written
    length — a piano note is released by the damper, not by the hammer."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + ring
    # Stiffer, shorter strings are more inharmonic: the bass stretches hard,
    # the treble barely at all.
    B = 0.00018 + 0.0016 * min(1.0, (65.4 / f0) ** 1.4)
    # Bass strings ring for many seconds, treble strings die fast.
    rate = 1.05 * (f0 / 261.63) ** 0.45
    parts = []
    for k in range(1, 11):
        stretch = math.sqrt(1.0 + B * k * k)
        g = (1.0 / k ** 1.25) * (bright ** (0.35 * (k - 1)))
        parts.append((k * stretch, g, rate * (1.0 + 0.42 * (k - 1))))
        if k <= 3:                                   # 2-3 strings per note, detuned
            parts.append((k * stretch * 1.0015, g * 0.7, rate * (1.0 + 0.42 * (k - 1))))
    s = additive(f0, n, parts)
    # Hammer felt hitting the string: a short, dull thud, brighter when struck hard.
    mix(s, lowpass(noise_burst(0.020, perc(150), 0.0, Noise(int(f0) | 1)),
                   900 + 2600 * v), 0.0, 0.30 * v)
    return [x * (0.35 + 0.65 * v) for x in s]


def _play(steps, tone=7000.0, **kw):
    return highpass(lowpass(motif(_piano, steps, **kw), tone), 45.0)


# --------------------------------------------------------------------------- #
# Single notes.
# --------------------------------------------------------------------------- #
def piano_note():
    """Single note — C4, struck firmly and left to ring."""
    return _play([(0, "C4", 4, 1.0, {"ring": 1.7})])


def piano_low():
    """Low note — C2, where the strings are longest and most inharmonic."""
    return _play([(0, "C2", 4, 1.0, {"ring": 2.2})])


def piano_high():
    """High note — C6, short, bright and almost bell-like."""
    return _play([(0, "C6", 3, 1.0, {"ring": 1.0})])


def piano_soft():
    """Soft note — struck gently: quieter, and far darker, not just quieter."""
    return _play([(0, "C4", 4, 0.4, {"ring": 1.6, "bright": 0.72})])


def piano_stac():
    """Staccato — the damper drops straight back onto the string."""
    return _play([(0, "C4", 1, 1.0, {"ring": 0.12})])


# --------------------------------------------------------------------------- #
# Chords.
# --------------------------------------------------------------------------- #
def piano_maj():
    """C major triad, struck together."""
    return _play([(0, MAJ, 6, 1.0, {"ring": 1.7})])


def piano_min():
    """C minor triad."""
    return _play([(0, MIN, 6, 1.0, {"ring": 1.7})])


def piano_maj7():
    """C major 7th — C E G B, warm and unresolved."""
    return _play([(0, ("C3", "E3", "G3", "B3"), 6, 1.0, {"ring": 1.7})])


def piano_min7():
    """C minor 7th — the smoky jazz voicing."""
    return _play([(0, ("C3", "Eb3", "G3", "Bb3"), 6, 1.0, {"ring": 1.7})])


def piano_dom7():
    """C dominant 7th — wants to resolve down a fifth."""
    return _play([(0, ("C3", "E3", "G3", "Bb3"), 6, 1.0, {"ring": 1.7})])


def piano_sus4():
    """C sus4 — the third replaced by the fourth, open and hanging."""
    return _play([(0, ("C3", "F3", "G3"), 6, 1.0, {"ring": 1.7})])


def piano_roll():
    """Rolled chord — the notes spread under the hand instead of struck flat."""
    return _play([(0, ("C3", "E3", "G3", "C4", "E4"), 6, 1.0, {"ring": 1.9})],
                 spread=0.035)


# --------------------------------------------------------------------------- #
# Figures.
# --------------------------------------------------------------------------- #
def piano_arp_up():
    """Arpeggio up — C minor across an octave and a half, pedal down."""
    return _play([(i, p, 1, 0.8 + 0.04 * i, {"ring": 1.4}) for i, p in
                  enumerate(("C3", "Eb3", "G3", "C4", "Eb4", "G4"))])


def piano_arp_down():
    """Arpeggio down — the same notes falling."""
    return _play([(i, p, 1, 0.95, {"ring": 1.4}) for i, p in
                  enumerate(("G4", "Eb4", "C4", "G3", "Eb3", "C3"))])


def piano_arp_updown():
    """Arpeggio up and back down — a complete turn over one bar."""
    seq = ("C3", "Eb3", "G3", "C4", "G3", "Eb3", "C3")
    return _play([(i, p, 1, 0.9, {"ring": 1.2}) for i, p in enumerate(seq)])


def piano_run_up():
    """Ascending run — the C minor scale, eight fast notes."""
    seq = ("C4", "D4", "Eb4", "F4", "G4", "Ab4", "Bb4", "C5")
    return _play([(i, p, 1, 0.78 + 0.03 * i, {"ring": 0.9}) for i, p in enumerate(seq)])


def piano_run_down():
    """Descending run — the same scale falling back to the root."""
    seq = ("C5", "Bb4", "Ab4", "G4", "F4", "Eb4", "D4", "C4")
    return _play([(i, p, 1, 0.95, {"ring": 1.1}) for i, p in enumerate(seq)])


def piano_octaves():
    """Octaves — C3 and C4 together, struck twice. The dramatic gesture."""
    return _play([(0, ("C3", "C4"), 2, 1.0, {"ring": 0.9}),
                  (4, ("C3", "C4"), 4, 0.95, {"ring": 1.6})])


def piano_riff():
    """Riff — a minor figure in the left hand, C Eb F G."""
    return _play([(0, "C3", 2, 1.0, {"ring": 0.8}), (2, "Eb3", 1, 0.85, {"ring": 0.6}),
                  (3, "F3", 1, 0.9, {"ring": 0.6}), (4, "G3", 6, 1.0, {"ring": 1.5})])


def piano_cadence():
    """ii-V-I — Dm7, G7, Cmaj7. The sentence every tonal piece ends with."""
    return _play([(0, ("D3", "F3", "A3", "C4"), 4, 0.9, {"ring": 1.0}),
                  (4, ("G3", "B3", "D4", "F4"), 4, 0.95, {"ring": 1.0}),
                  (8, ("C3", "E3", "G3", "B3"), 8, 1.0, {"ring": 2.0})])


def piano_vamp():
    """Two-chord vamp — Cm to Fm and back, the loop under a verse."""
    return _play([(0, MIN, 3, 1.0, {"ring": 0.8}),
                  (4, ("F3", "Ab3", "C4"), 3, 0.9, {"ring": 0.8}),
                  (8, MIN, 6, 0.95, {"ring": 1.6})])


def piano_stride():
    """Stride — bass note on the beat, chord on the off-beat, twice."""
    return _play([(0, "C2", 2, 1.0, {"ring": 0.7}), (2, MIN, 2, 0.8, {"ring": 0.6}),
                  (4, "G2", 2, 0.95, {"ring": 0.7}), (6, MIN, 4, 0.85, {"ring": 1.3})])


def piano_grace():
    """Grace note — a note crushed into the chord that follows it."""
    return _play([(0, "B2", 1, 0.6, {"ring": 0.4}), (0.6, MAJ, 6, 1.0, {"ring": 1.8})])


def piano_call():
    """Question — a rising right-hand phrase that stops on the fifth."""
    return _play([(0, "C4", 2, 0.9, {"ring": 0.8}), (2, "Eb4", 1, 0.85, {"ring": 0.7}),
                  (3, "F4", 1, 0.9, {"ring": 0.7}), (4, "G4", 5, 1.0, {"ring": 1.6})])


def piano_answer():
    """Answer — the phrase falling home to the root."""
    return _play([(0, "G4", 2, 0.95, {"ring": 0.8}), (2, "F4", 1, 0.85, {"ring": 0.7}),
                  (3, "Eb4", 1, 0.9, {"ring": 0.7}), (4, "C4", 5, 1.0, {"ring": 2.0})])


SOUNDS = [
    ("piano_note",      "Single ringing note",           piano_note),
    ("piano_low",       "Low inharmonic bass note",      piano_low),
    ("piano_high",      "Bright high note",              piano_high),
    ("piano_soft",      "Softly struck, darker note",    piano_soft),
    ("piano_stac",      "Staccato damped note",          piano_stac),
    ("piano_maj",       "C major triad",                 piano_maj),
    ("piano_min",       "C minor triad",                 piano_min),
    ("piano_maj7",      "Major 7th chord",               piano_maj7),
    ("piano_min7",      "Minor 7th chord",               piano_min7),
    ("piano_dom7",      "Dominant 7th chord",            piano_dom7),
    ("piano_sus4",      "Suspended 4th chord",           piano_sus4),
    ("piano_roll",      "Rolled spread chord",           piano_roll),
    ("piano_arp_up",    "Minor arpeggio up",             piano_arp_up),
    ("piano_arp_down",  "Minor arpeggio down",           piano_arp_down),
    ("piano_arp_updown", "Arpeggio up and back",         piano_arp_updown),
    ("piano_run_up",    "Ascending minor scale run",     piano_run_up),
    ("piano_run_down",  "Descending scale run",          piano_run_down),
    ("piano_octaves",   "Octave hits, twice",            piano_octaves),
    ("piano_riff",      "Left-hand minor riff",          piano_riff),
    ("piano_cadence",   "ii-V-I cadence",                piano_cadence),
    ("piano_vamp",      "Two-chord vamp",                piano_vamp),
    ("piano_stride",    "Stride bass and chord",         piano_stride),
    ("piano_grace",     "Grace note into a chord",       piano_grace),
    ("piano_call",      "Rising question phrase",        piano_call),
    ("piano_answer",    "Falling answer phrase",         piano_answer),
]
