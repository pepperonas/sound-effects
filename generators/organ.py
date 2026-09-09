"""Organ — drawbar organ: stabs, chords, progressions and glissandi.

A Hammond has no filter and no envelope worth speaking of. It is pure additive
synthesis: nine sine wheels at fixed ratios to the played note, each faded in
by its own drawbar, and that is the whole instrument. The ratios are organ
"footages" — 16' sounds an octave below the key, 8' at pitch, 4' an octave up,
and the odd ones (5 1/3', 2 2/3', 1 3/5') are the fifths and thirds that give
a drawbar registration its colour.

Two things make it sound played rather than computed: the *key click*, a burst
of contact noise as nine busbars close at slightly different moments, and the
Leslie — a rotating horn whose Doppler shift and amplitude sweep are the
reason an organ chord never sits still.
"""
import math
from synth import noise_burst, mix, adsr, perc, lowpass, highpass, note, Noise
from ._music import motif, additive

CATEGORY = "organ"
GROUP = "music"
DESCRIPTION = "Drawbar organ: registrations, chord stabs, progressions and glissandi."

# Footage -> frequency ratio.       16'   5 1/3'  8'   4'   2 2/3'  2'   1 3/5'  1 1/3'  1'
FOOTAGE = (0.5, 1.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)

# Drawbar settings, written the way an organist writes them (0-8 per bar).
FULL = (8, 8, 8, 0, 0, 0, 0, 0, 0)          # the fat rock/gospel sound
JAZZ = (8, 8, 8, 8, 0, 0, 0, 0, 0)          # Jimmy Smith's everyday setting
FLUTE = (0, 0, 8, 0, 0, 0, 0, 0, 0)         # one sine: the pure 8' flute
BRIGHT = (8, 8, 8, 8, 8, 8, 8, 8, 8)        # every bar out, screaming
HOLLOW = (8, 0, 8, 0, 0, 8, 0, 0, 0)        # no fifths: stopped-pipe colour


def _organ(pitch, dur, v=1.0, bars=JAZZ, rel=0.08, click=1.0, sus=0.92):
    """One key held down. The wheels never decay, so the note is shaped only by
    the key going down and coming back up — that is why an organ has no
    dynamics: `v` changes how many bars speak, not how loud the wheel is."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + rel
    parts = [(FOOTAGE[i], (b / 8.0) ** 1.4, 0.0) for i, b in enumerate(bars) if b]
    s = additive(f0, n, parts, attack=0.004)
    env = adsr(0.006, 0.02, sus, rel, n)
    s = [x * env(i / 44100.0) for i, x in enumerate(s)]
    if click:                                    # nine contacts closing at once
        mix(s, highpass(noise_burst(0.009, perc(320), 0.0, Noise(int(f0) | 5)), 2200),
            0.0, 0.20 * click)
    return [x * (0.55 + 0.45 * v) for x in s]


def _play(steps, tone=9000.0, **kw):
    return highpass(lowpass(motif(_organ, steps, **kw), tone), 50.0)


def _leslie(s, rate=6.4, depth=0.38):
    """Rotating horn: amplitude sweep as it turns towards and away from you."""
    return [x * (1.0 - depth * 0.5 * (1.0 - math.cos(2 * math.pi * rate * i / 44100)))
            for i, x in enumerate(s)]


MIN = ("C3", "Eb3", "G3")
MAJ = ("C3", "E3", "G3")


# --------------------------------------------------------------------------- #
# Registrations — the same note, five drawbar settings.
# --------------------------------------------------------------------------- #
def organ_full():
    """Full registration — 16', 5 1/3' and 8' out: the fat gospel sound."""
    return _play([(0, "C3", 8, 1.0, {"bars": FULL})])


def organ_jazz():
    """Jazz registration — the everyday four-bar setting, round and warm."""
    return _play([(0, "C3", 8, 1.0, {"bars": JAZZ})])


def organ_flute():
    """Flute registration — a single 8' sine, no harmonics at all."""
    return _play([(0, "C4", 8, 0.9, {"bars": FLUTE, "click": 0.3})])


def organ_bright():
    """All drawbars out — every wheel speaking, harsh and enormous."""
    return _play([(0, "C3", 8, 1.0, {"bars": BRIGHT})])


def organ_hollow():
    """No fifths — a stopped-pipe colour, oddly hollow and church-like."""
    return _play([(0, "C3", 8, 1.0, {"bars": HOLLOW})])


# --------------------------------------------------------------------------- #
# Chords.
# --------------------------------------------------------------------------- #
def organ_maj():
    """C major triad, held."""
    return _play([(0, MAJ, 10, 1.0)])


def organ_min():
    """C minor triad, held."""
    return _play([(0, MIN, 10, 1.0)])


def organ_min7():
    """C minor 7th — the organ trio chord."""
    return _play([(0, ("C3", "Eb3", "G3", "Bb3"), 10, 1.0)])


def organ_dom7():
    """C dominant 7th, on the full registration — gospel tension."""
    return _play([(0, ("C3", "E3", "G3", "Bb3"), 10, 1.0, {"bars": FULL})])


def organ_sus():
    """C sus4 — no third, wide and unresolved."""
    return _play([(0, ("C3", "F3", "G3"), 10, 1.0)])


def organ_stab():
    """Chord stab — keys down and straight back up, percussive."""
    return _play([(0, MIN, 1, 1.0, {"rel": 0.05})])


def organ_stab_2():
    """Two stabs — the off-beat organ punch behind a horn line."""
    return _play([(0, MIN, 1, 1.0, {"rel": 0.05}), (3, MIN, 1, 0.9, {"rel": 0.05})])


def organ_leslie():
    """Held chord through a spinning Leslie — the sound never sits still."""
    return _leslie(_play([(0, ("C3", "Eb3", "G3", "Bb3"), 16, 1.0)]))


# --------------------------------------------------------------------------- #
# Progressions and figures.
# --------------------------------------------------------------------------- #
def organ_cadence():
    """ii-V-I — Dm7, G7, C, on the jazz registration."""
    return _play([(0, ("D3", "F3", "A3", "C4"), 4, 0.95),
                  (4, ("G3", "B3", "D4", "F4"), 4, 1.0),
                  (8, ("C3", "E3", "G3", "B3"), 10, 1.0)])


def organ_vamp():
    """Gospel vamp — Cm to Fm and back, full drawbars."""
    return _play([(0, MIN, 4, 1.0, {"bars": FULL}),
                  (4, ("F3", "Ab3", "C4"), 4, 0.95, {"bars": FULL}),
                  (8, MIN, 8, 1.0, {"bars": FULL})])


def organ_plagal():
    """Plagal cadence — F to C, the "amen" at the end of a hymn."""
    return _play([(0, ("F3", "A3", "C4"), 6, 0.95), (6, MAJ, 12, 1.0)])


def organ_pedal():
    """Pedal note — a low 16' root held under a chord above it."""
    return _play([(0, "C2", 16, 1.0, {"bars": FULL}), (2, MIN, 12, 0.8)])


def organ_shout():
    """Shout chorus — three rising stabs, the gospel climax."""
    return _play([(0, MIN, 1, 0.95, {"bars": FULL, "rel": 0.05}),
                  (2, ("F3", "Ab3", "C4"), 1, 1.0, {"bars": FULL, "rel": 0.05}),
                  (4, ("G3", "Bb3", "D4"), 8, 1.0, {"bars": FULL})])


def organ_gliss_up():
    """Glissando up — a palm dragged up the white keys."""
    seq = ("C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5")
    return _play([(i * 0.5, p, 1, 0.8, {"rel": 0.05}) for i, p in enumerate(seq)])


def organ_gliss_down():
    """Glissando down — the same palm coming back."""
    seq = ("C5", "B4", "A4", "G4", "F4", "E4", "D4", "C4")
    return _play([(i * 0.5, p, 1 if i < 7 else 6, 0.85, {"rel": 0.05})
                  for i, p in enumerate(seq)])


def organ_arp_up():
    """Arpeggio up — the minor chord spelled out, keys clicking."""
    return _play([(i, p, 1, 0.9, {"rel": 0.05}) for i, p in
                  enumerate(("C3", "Eb3", "G3", "C4", "Eb4"))])


def organ_arp_down():
    """Arpeggio down — the same shape falling into a held root."""
    return _play([(i, p, 1 if i < 4 else 8, 0.9, {"rel": 0.05}) for i, p in
                  enumerate(("Eb4", "C4", "G3", "Eb3", "C3"))])


def organ_riff():
    """Riff — a bluesy right-hand figure over the drawbars."""
    return _play([(0, "C4", 2, 1.0, {"rel": 0.05}), (2, "Eb4", 1, 0.9, {"rel": 0.05}),
                  (3, "F4", 1, 0.9, {"rel": 0.05}), (4, "Gb4", 1, 0.95, {"rel": 0.05}),
                  (5, "G4", 8, 1.0)])


def organ_octaves():
    """Octaves — C3 and C4 held together, the organist's left hand."""
    return _play([(0, ("C3", "C4"), 12, 1.0, {"bars": FULL})])


def organ_swell():
    """Swell — a chord brought in slowly on the expression pedal."""
    s = _play([(0, ("C3", "G3", "C4", "Eb4"), 16, 1.0)])
    n = int(0.55 * 44100)
    return [x * min(1.0, (i / n) ** 1.6) if i < n else x for i, x in enumerate(s)]


SOUNDS = [
    ("organ_full",       "Fat 16-5⅓-8 registration",    organ_full),
    ("organ_jazz",       "Everyday jazz registration",  organ_jazz),
    ("organ_flute",      "Single 8' flute sine",        organ_flute),
    ("organ_bright",     "All drawbars out",            organ_bright),
    ("organ_hollow",     "Stopped-pipe, no fifths",     organ_hollow),
    ("organ_maj",        "C major triad held",          organ_maj),
    ("organ_min",        "C minor triad held",          organ_min),
    ("organ_min7",       "Minor 7th organ chord",       organ_min7),
    ("organ_dom7",       "Gospel dominant 7th",         organ_dom7),
    ("organ_sus",        "Open sus4 chord",             organ_sus),
    ("organ_stab",       "Single percussive stab",      organ_stab),
    ("organ_stab_2",     "Two off-beat stabs",          organ_stab_2),
    ("organ_leslie",     "Held chord through a Leslie", organ_leslie),
    ("organ_cadence",    "ii-V-I cadence",              organ_cadence),
    ("organ_vamp",       "Gospel two-chord vamp",       organ_vamp),
    ("organ_plagal",     "Plagal 'amen' cadence",       organ_plagal),
    ("organ_pedal",      "Low pedal under a chord",     organ_pedal),
    ("organ_shout",      "Rising gospel shout stabs",   organ_shout),
    ("organ_gliss_up",   "Palm glissando up",           organ_gliss_up),
    ("organ_gliss_down", "Palm glissando down",         organ_gliss_down),
    ("organ_arp_up",     "Minor arpeggio up",           organ_arp_up),
    ("organ_arp_down",   "Minor arpeggio down",         organ_arp_down),
    ("organ_riff",       "Bluesy right-hand riff",      organ_riff),
    ("organ_octaves",    "Held octaves, full bars",     organ_octaves),
    ("organ_swell",      "Chord swelled in on the pedal", organ_swell),
]
