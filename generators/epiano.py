"""E-piano — Rhodes and Wurlitzer: chords, comping, licks and that tine bark.

This is the one instrument in the pack that is genuinely FM and not an
imitation of it: a Rhodes is a tine struck next to a pickup, and the DX7 patch
that replaced it on every record of the 1980s is two operators, a carrier bent
by a modulator at the same frequency. The single cue that sells it is the
*modulation* envelope decaying much faster than the amplitude envelope — the
note barks bright for 100 ms and then settles into a soft sine. Hit it harder
and the bark gets louder, not just the note; that is why `v` drives the
modulation index here and not only the gain.

A Wurlitzer is the same trick with the modulator an octave up and driven
harder, which is where its reedier, more hollow growl comes from.
"""
import math
from synth import fm, sine, mix, perc, lowpass, highpass, note
from ._music import motif

CATEGORY = "epiano"
GROUP = "music"
DESCRIPTION = "Rhodes/Wurlitzer e-piano: 7th and 9th chords, comping, licks, tremolo."

MIN7 = ("C3", "Eb3", "G3", "Bb3")
MAJ7 = ("C3", "E3", "G3", "B3")


def _rhodes(pitch, dur, v=1.0, ring=0.9, ratio=1.0, index=3.4, bark=26.0,
            tine=1.0, body=0.28):
    """One tine. `bark` is how fast the modulation index collapses — the whole
    difference between an e-piano and a plain sine lives in that number."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + ring
    rate = 1.6 * (f0 / 261.63) ** 0.35            # high notes die faster
    amp = perc(rate)
    s = fm(f0, n, ratio=ratio, index=index * (0.45 + 0.55 * v),
           env=amp, mod_env=perc(bark))
    # The tine itself: a short inharmonic ping well above the fundamental.
    if tine:
        mix(s, fm(f0, n, ratio=9.0, index=1.5, env=perc(20.0)), 0.0, 0.16 * tine * v)
    # A little pure fundamental underneath keeps the low notes from sounding hollow.
    mix(s, sine(f0, n, perc(rate * 0.8)), 0.0, body)
    return [x * (0.4 + 0.6 * v) for x in s]


def _play(steps, tone=6500.0, **kw):
    return highpass(lowpass(motif(_rhodes, steps, **kw), tone), 55.0)


def _trem(s, rate=5.2, depth=0.42):
    """The Rhodes 'vibrato' — actually amplitude panning, mono here."""
    return [x * (1.0 - depth * 0.5 * (1.0 - math.cos(2 * math.pi * rate * i / 44100)))
            for i, x in enumerate(s)]


# --------------------------------------------------------------------------- #
# Single notes and timbres.
# --------------------------------------------------------------------------- #
def epiano_note():
    """Single tine — C4, struck normally, the reference sound."""
    return _play([(0, "C4", 6, 0.85, {"ring": 1.5})])


def epiano_bark():
    """Struck hard — the modulation index jumps and the tine barks."""
    return _play([(0, "C4", 6, 1.0, {"ring": 1.5, "index": 5.2, "tine": 1.6})])


def epiano_soft():
    """Struck gently — almost a pure sine, no bark at all."""
    return _play([(0, "C4", 6, 0.32, {"ring": 1.6, "index": 1.6, "tine": 0.3})])


def epiano_bell():
    """Bell tone — high and tine-forward, glassy."""
    return _play([(0, "C5", 5, 0.9, {"ring": 1.4, "tine": 2.2, "index": 2.6})],
                 tone=9000)


def epiano_wurli():
    """Wurlitzer — modulator an octave up and driven hard: reedy and hollow."""
    return _play([(0, "C3", 6, 1.0, {"ring": 1.2, "ratio": 2.0, "index": 4.6,
                                     "bark": 14.0, "tine": 0.4, "body": 0.18})])


# --------------------------------------------------------------------------- #
# Chords — sevenths and ninths, which is what this instrument is for.
# --------------------------------------------------------------------------- #
def epiano_min7():
    """C minor 7th — the default Rhodes chord."""
    return _play([(0, MIN7, 8, 0.9, {"ring": 1.6})])


def epiano_maj7():
    """C major 7th — warm and open."""
    return _play([(0, MAJ7, 8, 0.9, {"ring": 1.6})])


def epiano_dom7():
    """C dominant 7th — leaning, wants to move."""
    return _play([(0, ("C3", "E3", "G3", "Bb3"), 8, 0.9, {"ring": 1.6})])


def epiano_min9():
    """C minor 9th — the ninth on top, the sound of a Rhodes ballad."""
    return _play([(0, ("C3", "Eb3", "G3", "Bb3", "D4"), 8, 0.9, {"ring": 1.7})])


def epiano_maj9():
    """C major 9th — lush, floating, unresolved in a pleasant way."""
    return _play([(0, ("C3", "E3", "G3", "B3", "D4"), 8, 0.9, {"ring": 1.7})])


def epiano_sus():
    """C sus4 add9 — no third at all, wide open."""
    return _play([(0, ("C3", "F3", "G3", "D4"), 8, 0.9, {"ring": 1.6})])


def epiano_dim():
    """C diminished 7th — evenly tense, goes anywhere."""
    return _play([(0, ("C3", "Eb3", "Gb3", "A3"), 7, 0.9, {"ring": 1.4})])


def epiano_roll():
    """Rolled 9th chord — spread under the hand rather than struck flat."""
    return _play([(0, ("C3", "Eb3", "G3", "Bb3", "D4"), 8, 0.95, {"ring": 1.8})],
                 spread=0.030)


def epiano_stab():
    """Chord stab — hit and damped, a rhythmic punctuation."""
    return _play([(0, MIN7, 1, 1.0, {"ring": 0.18, "index": 4.4})])


# --------------------------------------------------------------------------- #
# Comping and progressions.
# --------------------------------------------------------------------------- #
def epiano_comp():
    """Comping — chords pushed onto the off-beats, the way a player fills a bar."""
    return _play([(0, MIN7, 1, 0.9, {"ring": 0.5}), (3, MIN7, 1, 0.75, {"ring": 0.5}),
                  (6, MIN7, 1, 0.85, {"ring": 0.5}), (8, MIN7, 4, 0.95, {"ring": 1.4})])


def epiano_vamp():
    """Two-chord vamp — Cm9 to Fm9 and back, a whole verse in three chords."""
    return _play([(0, ("C3", "Eb3", "G3", "Bb3"), 4, 0.9, {"ring": 0.9}),
                  (4, ("F3", "Ab3", "C4", "Eb4"), 4, 0.85, {"ring": 0.9}),
                  (8, ("C3", "Eb3", "G3", "Bb3"), 6, 0.95, {"ring": 1.6})])


def epiano_cadence():
    """ii-V-I in C — Dm7, G7, Cmaj7, the jazz sentence."""
    return _play([(0, ("D3", "F3", "A3", "C4"), 4, 0.88, {"ring": 1.0}),
                  (4, ("G3", "B3", "D4", "F4"), 4, 0.92, {"ring": 1.0}),
                  (8, MAJ7, 8, 0.95, {"ring": 2.0})])


def epiano_turn():
    """Turnaround — Cm7 to Ab maj7, the flat-six move that resets a loop."""
    return _play([(0, MIN7, 5, 0.9, {"ring": 1.0}),
                  (6, ("Ab2", "C3", "Eb3", "G3"), 8, 0.95, {"ring": 1.8})])


# --------------------------------------------------------------------------- #
# Melodic figures.
# --------------------------------------------------------------------------- #
def epiano_arp_up():
    """Arpeggio up — the minor 9th spelled out one note at a time."""
    return _play([(i, p, 1, 0.75 + 0.04 * i, {"ring": 1.2}) for i, p in
                  enumerate(("C3", "Eb3", "G3", "Bb3", "D4"))])


def epiano_arp_down():
    """Arpeggio down — the same chord falling."""
    return _play([(i, p, 1, 0.9, {"ring": 1.2}) for i, p in
                  enumerate(("D4", "Bb3", "G3", "Eb3", "C3"))])


def epiano_lick():
    """Lick — a short blues phrase over the minor chord."""
    return _play([(0, "G3", 1, 0.9, {"ring": 0.6}), (1, "Bb3", 1, 0.85, {"ring": 0.6}),
                  (2, "C4", 2, 0.95, {"ring": 0.8}), (4, "Bb3", 1, 0.8, {"ring": 0.6}),
                  (5, "G3", 5, 0.9, {"ring": 1.6})])


def epiano_riff():
    """Riff — a repeating two-note figure with the chord underneath."""
    return _play([(0, MIN7, 4, 0.85, {"ring": 1.0}), (0, "C4", 1, 0.9, {"ring": 0.5}),
                  (2, "Eb4", 1, 0.85, {"ring": 0.5}), (4, "C4", 1, 0.9, {"ring": 0.5}),
                  (6, "G3", 6, 0.95, {"ring": 1.4})])


def epiano_call():
    """Question — rising, stopping on the ninth, hanging."""
    return _play([(0, "C4", 2, 0.85, {"ring": 0.8}), (2, "Eb4", 1, 0.8, {"ring": 0.7}),
                  (3, "F4", 1, 0.85, {"ring": 0.7}), (4, "G4", 5, 0.95, {"ring": 1.6})])


def epiano_answer():
    """Answer — falling back onto the root, settled."""
    return _play([(0, "G4", 2, 0.9, {"ring": 0.8}), (2, "F4", 1, 0.8, {"ring": 0.7}),
                  (3, "Eb4", 1, 0.85, {"ring": 0.7}), (4, "C4", 5, 0.95, {"ring": 1.8})])


def epiano_tremolo():
    """Tremolo — a held chord under the Rhodes' amplitude wobble."""
    return _trem(_play([(0, ("C3", "Eb3", "G3", "Bb3", "D4"), 14, 0.9, {"ring": 1.4})]))


SOUNDS = [
    ("epiano_note",     "Single tine, normal touch",     epiano_note),
    ("epiano_bark",     "Hard-struck barking tine",      epiano_bark),
    ("epiano_soft",     "Gently struck, near-sine",      epiano_soft),
    ("epiano_bell",     "High glassy bell tone",         epiano_bell),
    ("epiano_wurli",    "Reedy Wurlitzer timbre",        epiano_wurli),
    ("epiano_min7",     "C minor 7th chord",             epiano_min7),
    ("epiano_maj7",     "C major 7th chord",             epiano_maj7),
    ("epiano_dom7",     "C dominant 7th chord",          epiano_dom7),
    ("epiano_min9",     "C minor 9th chord",             epiano_min9),
    ("epiano_maj9",     "C major 9th chord",             epiano_maj9),
    ("epiano_sus",      "Sus4 add9, no third",           epiano_sus),
    ("epiano_dim",      "Diminished 7th chord",          epiano_dim),
    ("epiano_roll",     "Rolled 9th chord",              epiano_roll),
    ("epiano_stab",     "Damped chord stab",             epiano_stab),
    ("epiano_comp",     "Off-beat comping figure",       epiano_comp),
    ("epiano_vamp",     "Two-chord minor vamp",          epiano_vamp),
    ("epiano_cadence",  "ii-V-I jazz cadence",           epiano_cadence),
    ("epiano_turn",     "Flat-six turnaround",           epiano_turn),
    ("epiano_arp_up",   "Minor 9th arpeggio up",         epiano_arp_up),
    ("epiano_arp_down", "Minor 9th arpeggio down",       epiano_arp_down),
    ("epiano_lick",     "Short blues lick",              epiano_lick),
    ("epiano_riff",     "Two-note riff over the chord",  epiano_riff),
    ("epiano_call",     "Rising question phrase",        epiano_call),
    ("epiano_answer",   "Falling answer phrase",         epiano_answer),
    ("epiano_tremolo",  "Held chord with tremolo",       epiano_tremolo),
]
