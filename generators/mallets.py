"""Mallets — marimba, vibraphone and glockenspiel: runs, ostinatos and rolls.

A tuned bar is not a string: its overtones are not a harmonic series but the
bending modes of a beam, and the maker files the underside of the bar until
they land on musically useful ratios. A marimba bar is undercut until its
first two overtones sit at roughly 4x and 10x the fundamental — two octaves
and three octaves plus a major third. That 1 : 4 : 10 stack is the entire
reason a marimba sounds hollow and woody rather than warm like a piano, and
it is what is synthesised here, one partial per mode.

Glockenspiel bars are steel and much less carefully undercut, so their modes
sit at awkward ratios and ring for a long time — which is why they read as
"bell" rather than as "pitch".
"""
from synth import noise_burst, mix, perc, lowpass, highpass, note, Noise
from ._music import motif, additive
import math

CATEGORY = "mallets"
GROUP = "music"
DESCRIPTION = "Marimba, vibraphone and glockenspiel: runs, ostinatos, rolls, arpeggios."

# (mode ratio, gain, decay rate) — the bending modes of each kind of bar.
MARIMBA = [(1.0, 1.0, 5.5), (3.93, 0.34, 10.0), (9.35, 0.11, 17.0)]
VIBES = [(1.0, 1.0, 1.5), (4.0, 0.28, 2.8), (10.0, 0.09, 4.6)]
GLOCK = [(1.0, 1.0, 2.8), (2.76, 0.44, 4.6), (5.40, 0.20, 6.5), (8.9, 0.08, 9.0)]


def _bar(pitch, dur, v=1.0, modes=MARIMBA, ring=0.7, hard=1.0, rate=1.0):
    """One struck bar. `hard` is the mallet: a hard rubber head excites the
    upper modes, a soft yarn head barely touches them."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + ring
    parts = [(m, g * (hard ** (0.9 * i)), r * rate) for i, (m, g, r) in enumerate(modes)]
    s = additive(f0, n, parts)
    # The mallet head itself hitting wood or steel.
    mix(s, lowpass(noise_burst(0.012, perc(260), 0.0, Noise(int(f0) | 3)),
                   1500 + 5000 * hard), 0.0, 0.18 * v * hard)
    return [x * (0.4 + 0.6 * v) for x in s]


def _play(steps, tone=9000.0, **kw):
    return highpass(lowpass(motif(_bar, steps, **kw), tone), 60.0)


def _motor(s, rate=4.6, depth=0.5):
    """The vibraphone's rotating discs opening and closing the resonators."""
    return [x * (1.0 - depth * 0.5 * (1.0 - math.cos(2 * math.pi * rate * i / 44100)))
            for i, x in enumerate(s)]


# --------------------------------------------------------------------------- #
# The three instruments, single notes.
# --------------------------------------------------------------------------- #
def mallets_marimba():
    """Marimba — a rosewood bar, woody and quick to die."""
    return _play([(0, "C4", 3, 1.0, {"ring": 1.0})])


def mallets_marimba_low():
    """Low marimba — C3, where the bars are long and the tone is deepest."""
    return _play([(0, "C3", 4, 1.0, {"ring": 1.6})])


def mallets_vibes():
    """Vibraphone — aluminium bars, sweet and ringing on for seconds."""
    return _play([(0, "C4", 4, 0.9, {"modes": VIBES, "ring": 2.4, "hard": 0.6})])


def mallets_glock():
    """Glockenspiel — steel, piercing, deliberately inharmonic."""
    return _play([(0, "C6", 3, 0.9, {"modes": GLOCK, "ring": 1.8, "hard": 1.2})])


def mallets_soft():
    """Soft mallet — yarn head, almost no upper modes, nearly a sine."""
    return _play([(0, "C4", 4, 0.7, {"ring": 1.2, "hard": 0.35})])


def mallets_hard():
    """Hard mallet — the bar's upper modes rung out, bright and clacky."""
    return _play([(0, "C4", 3, 1.0, {"ring": 1.0, "hard": 1.8})])


# --------------------------------------------------------------------------- #
# Rolls and sustained gestures.
# --------------------------------------------------------------------------- #
def mallets_roll():
    """Roll — the only way a mallet player sustains: hit it again, fast."""
    return _play([(i, "C4", 1, 0.6 + 0.05 * (i % 3), {"ring": 0.7, "hard": 0.7})
                  for i in range(10)])


def mallets_roll_chord():
    """Rolled chord — two bars alternating, a sustained minor third."""
    seq = ("C4", "Eb4") * 5
    return _play([(i, p, 1, 0.65, {"ring": 0.8, "hard": 0.7}) for i, p in enumerate(seq)])


def mallets_tremolo():
    """Vibraphone tremolo — one note held under the motor."""
    return _motor(_play([(0, "C4", 6, 0.9, {"modes": VIBES, "ring": 2.6, "hard": 0.6})]))


def mallets_vibes_chord():
    """Vibraphone chord — C minor 9th left to ring, jazz-vibes flavour."""
    return _play([(0, ("C4", "Eb4", "G4", "Bb4", "D5"), 6, 0.85,
                   {"modes": VIBES, "ring": 2.6, "hard": 0.55})])


# --------------------------------------------------------------------------- #
# Runs, arpeggios and ostinatos.
# --------------------------------------------------------------------------- #
def mallets_run_up():
    """Run up — the C minor scale, eight even sixteenths."""
    seq = ("C4", "D4", "Eb4", "F4", "G4", "Ab4", "Bb4", "C5")
    return _play([(i, p, 1, 0.8 + 0.025 * i, {"ring": 0.8}) for i, p in enumerate(seq)])


def mallets_run_down():
    """Run down — the same scale falling to the root."""
    seq = ("C5", "Bb4", "Ab4", "G4", "F4", "Eb4", "D4", "C4")
    return _play([(i, p, 1, 0.95, {"ring": 0.9}) for i, p in enumerate(seq)])


def mallets_arp_up():
    """Arpeggio up — C minor across an octave and a half."""
    return _play([(i, p, 1, 0.8 + 0.04 * i, {"ring": 1.0}) for i, p in
                  enumerate(("C4", "Eb4", "G4", "C5", "Eb5", "G5"))])


def mallets_arp_down():
    """Arpeggio down — the same shape falling."""
    return _play([(i, p, 1, 0.9, {"ring": 1.0}) for i, p in
                  enumerate(("G5", "Eb5", "C5", "G4", "Eb4", "C4"))])


def mallets_ostinato():
    """Ostinato — a four-note figure that loops, the minimalist engine."""
    seq = ("C4", "G4", "Eb4", "G4", "C4", "G4", "Eb4", "G4")
    return _play([(i, p, 1, 0.9 if i % 4 == 0 else 0.72, {"ring": 0.8})
                  for i, p in enumerate(seq)])


def mallets_ostinato_5():
    """Five-beat ostinato — the same idea in an odd metre, restless."""
    seq = ("C4", "Eb4", "G4", "Bb4", "G4", "C4", "Eb4", "G4", "Bb4", "G4")
    return _play([(i, p, 1, 0.9 if i % 5 == 0 else 0.7, {"ring": 0.8})
                  for i, p in enumerate(seq)])


def mallets_octaves():
    """Octaves — two mallets, C4 and C5 struck together, then again."""
    return _play([(0, ("C4", "C5"), 2, 1.0, {"ring": 1.0}),
                  (4, ("C4", "C5"), 3, 0.9, {"ring": 1.4})])


def mallets_thirds():
    """Thirds — the classic two-mallet parallel motion up the scale."""
    return _play([(i * 2, p, 2, 0.85 + 0.03 * i, {"ring": 1.0}) for i, p in
                  enumerate((("C4", "Eb4"), ("D4", "F4"), ("Eb4", "G4")))])


# --------------------------------------------------------------------------- #
# Phrases.
# --------------------------------------------------------------------------- #
def mallets_rise_3():
    """Three rising bars — C Eb G, deliberate."""
    return _play([(0, "C4", 2, 0.85, {"ring": 0.9}), (2, "Eb4", 2, 0.9, {"ring": 0.9}),
                  (4, "G4", 4, 1.0, {"ring": 1.5})])


def mallets_fall_3():
    """Three falling bars — G Eb C, settling."""
    return _play([(0, "G4", 2, 0.95, {"ring": 0.9}), (2, "Eb4", 2, 0.9, {"ring": 0.9}),
                  (4, "C4", 4, 1.0, {"ring": 1.5})])


def mallets_call():
    """Question — rising to the fifth and stopping there."""
    return _play([(0, "C4", 2, 0.85, {"ring": 0.8}), (2, "Eb4", 1, 0.8, {"ring": 0.7}),
                  (3, "F4", 1, 0.85, {"ring": 0.7}), (4, "G4", 4, 1.0, {"ring": 1.4})])


def mallets_answer():
    """Answer — falling back home."""
    return _play([(0, "G4", 2, 0.9, {"ring": 0.8}), (2, "F4", 1, 0.8, {"ring": 0.7}),
                  (3, "Eb4", 1, 0.85, {"ring": 0.7}), (4, "C4", 4, 1.0, {"ring": 1.6})])


def mallets_glock_run():
    """Glockenspiel run — five bright steel notes, a music-box flourish."""
    return _play([(i, p, 1, 0.85, {"modes": GLOCK, "ring": 1.4, "hard": 1.1})
                  for i, p in enumerate(("C5", "Eb5", "G5", "Bb5", "C6"))], tone=12000)


def mallets_glock_chime():
    """Glockenspiel chime — two struck notes left to ring against each other."""
    return _play([(0, "G5", 2, 0.9, {"modes": GLOCK, "ring": 2.0, "hard": 1.0}),
                  (3, "C6", 4, 0.95, {"modes": GLOCK, "ring": 2.4, "hard": 1.0})],
                 tone=12000)


def mallets_stagger():
    """Staggered pair — two bars a beat apart, the marimba's own echo."""
    return _play([(0, "C4", 2, 1.0, {"ring": 1.0}), (3, "G4", 2, 0.8, {"ring": 1.0}),
                  (6, "C5", 4, 0.9, {"ring": 1.6})])


SOUNDS = [
    ("mallets_marimba",     "Marimba single bar",           mallets_marimba),
    ("mallets_marimba_low", "Low woody marimba bar",        mallets_marimba_low),
    ("mallets_vibes",       "Vibraphone ringing bar",       mallets_vibes),
    ("mallets_glock",       "Glockenspiel steel bar",       mallets_glock),
    ("mallets_soft",        "Soft yarn mallet, near-sine",  mallets_soft),
    ("mallets_hard",        "Hard mallet, bright modes",    mallets_hard),
    ("mallets_roll",        "Single-note sustaining roll",  mallets_roll),
    ("mallets_roll_chord",  "Rolled minor third",           mallets_roll_chord),
    ("mallets_tremolo",     "Vibraphone motor tremolo",     mallets_tremolo),
    ("mallets_vibes_chord", "Vibraphone minor 9th chord",   mallets_vibes_chord),
    ("mallets_run_up",      "Ascending scale run",          mallets_run_up),
    ("mallets_run_down",    "Descending scale run",         mallets_run_down),
    ("mallets_arp_up",      "Minor arpeggio up",            mallets_arp_up),
    ("mallets_arp_down",    "Minor arpeggio down",          mallets_arp_down),
    ("mallets_ostinato",    "Four-note looping ostinato",   mallets_ostinato),
    ("mallets_ostinato_5",  "Five-beat odd-metre ostinato", mallets_ostinato_5),
    ("mallets_octaves",     "Two-mallet octaves",           mallets_octaves),
    ("mallets_thirds",      "Parallel thirds up the scale", mallets_thirds),
    ("mallets_rise_3",      "Three rising bars",            mallets_rise_3),
    ("mallets_fall_3",      "Three falling bars",           mallets_fall_3),
    ("mallets_call",        "Rising question figure",       mallets_call),
    ("mallets_answer",      "Falling answer figure",        mallets_answer),
    ("mallets_glock_run",   "Bright glockenspiel run",      mallets_glock_run),
    ("mallets_glock_chime", "Two ringing glock chimes",     mallets_glock_chime),
    ("mallets_stagger",     "Staggered rising pair",        mallets_stagger),
]
