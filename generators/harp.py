"""Harp — glissandi, rolled chords and arpeggios.

The same plucked-string physics as the guitar, voiced at the opposite extreme:
a soft fingertip (`pick` low), almost no damping and a decay long enough that
the strings keep ringing under everything played after them. That overlap is
the whole sound of a harp — the notes of a gliss are not separate events, they
pile up into one shimmering chord.

Glissandi run on a pentatonic ladder. A real harpist sets the pedals so that
raking the strings cannot produce a wrong note; the five-note scale is the
same trick, and it is why a harp gliss always sounds "right" over any chord.
"""
from synth import pluck, adsr, lowpass, highpass, note, Noise
from ._music import motif

CATEGORY = "harp"
GROUP = "music"
DESCRIPTION = "Harp: glissandi, rolled chords, arpeggios and cascades."

PENT = ("C", "D", "E", "G", "A")          # no semitones — nothing can clash
MINOR_PENT = ("C", "Eb", "F", "G", "Bb")


def _ladder(names, lo, hi):
    """Every named degree from octave `lo` to `hi`, ascending."""
    return ["%s%d" % (n, o) for o in range(lo, hi + 1) for n in names]


def _harp(pitch, dur, v=1.0, damp=0.56, decay=0.99915, pick=0.45, ring=0.85):
    """One harp string. `ring` is how long it keeps sounding past its nominal
    length — a harp string is never stopped, so this is far longer than the
    note value in the motif."""
    f0 = note(pitch) if isinstance(pitch, str) else pitch
    seed = f0(0.0) if callable(f0) else float(f0)
    n = dur + ring
    s = pluck(f0, n, damp=damp, decay=decay, pick=pick,
              env=adsr(0.0018, 0.04, 0.94, ring, n), noise=Noise(int(seed * 31) | 1))
    return [x * (0.4 + 0.6 * v) for x in s]


def _play(steps, tone=5200.0, **kw):
    return highpass(lowpass(motif(_harp, steps, **kw), tone), 55.0)


def _rake(names, start=0, gap=1.0, ring=0.9, v0=0.75, v1=1.0, hold=1):
    """A gliss: one event per string, evenly spaced, velocity easing across."""
    n = len(names)
    return [(start + i * gap, p, hold, v0 + (v1 - v0) * i / max(1, n - 1),
             {"ring": ring}) for i, p in enumerate(names)]


# --------------------------------------------------------------------------- #
# Single strings and rolled chords.
# --------------------------------------------------------------------------- #
def harp_note():
    """Single string — C4, plucked and left to ring out."""
    return _play([(0, "C4", 1, 1.0, {"ring": 1.6})])


def harp_low():
    """Low string — C2, the harp's bass register, long and woody."""
    return _play([(0, "C2", 1, 1.0, {"ring": 2.0, "damp": 0.72})])


def harp_harmonic():
    """Harmonic — a string touched at its midpoint, glassy and pure."""
    return _play([(0, "C6", 1, 0.8, {"ring": 1.2, "damp": 0.20, "pick": 0.8})],
                 tone=8000)


def harp_roll_maj():
    """Rolled C major — strings struck in sequence, the harp's signature chord."""
    return _play(_rake(("C3", "E3", "G3", "C4", "E4"), gap=0.55, ring=1.7))


def harp_roll_min():
    """Rolled C minor — the same gesture, darker."""
    return _play(_rake(("C3", "Eb3", "G3", "C4", "Eb4"), gap=0.55, ring=1.7))


def harp_roll_maj7():
    """Rolled C major 7th — lush, film-score harmony."""
    return _play(_rake(("C3", "E3", "G3", "B3", "E4"), gap=0.55, ring=1.7))


def harp_roll_sus():
    """Rolled sus2 — open and unresolved, hangs in the air."""
    return _play(_rake(("C3", "D3", "G3", "C4", "D4"), gap=0.55, ring=1.7))


def harp_final():
    """Closing chord — a wide slow roll across two octaves, left to decay."""
    return _play(_rake(("C2", "G2", "C3", "E3", "G3", "C4", "E4", "G4"),
                       gap=0.7, ring=2.2, v0=0.8))


# --------------------------------------------------------------------------- #
# Glissandi — the gesture everyone knows a harp for.
# --------------------------------------------------------------------------- #
def harp_gliss_up():
    """Gliss up — a pentatonic rake across two octaves."""
    return _play(_rake(_ladder(PENT, 3, 4) + ["C5"], gap=0.62, ring=1.4))


def harp_gliss_down():
    """Gliss down — the same rake, top to bottom."""
    names = (_ladder(PENT, 3, 4) + ["C5"])[::-1]
    return _play(_rake(names, gap=0.62, ring=1.4, v0=1.0, v1=0.75))


def harp_gliss_long():
    """Long gliss — three octaves, the full sweep into a downbeat."""
    return _play(_rake(_ladder(PENT, 2, 4) + ["C5"], gap=0.5, ring=1.6))


def harp_gliss_fast():
    """Fast gliss — a quick flick across one octave, a decoration not a feature."""
    return _play(_rake(_ladder(PENT, 4, 4) + ["C5"], gap=0.38, ring=1.0))


def harp_gliss_minor():
    """Minor gliss — the minor pentatonic ladder, darker and more urgent."""
    return _play(_rake(_ladder(MINOR_PENT, 3, 4) + ["C5"], gap=0.6, ring=1.4))


def harp_cascade():
    """Cascade — a falling gliss that slows as it lands on the low root."""
    names = (_ladder(PENT, 3, 5))[::-1][:13]
    steps = []
    at = 0.0
    for i, p in enumerate(names):
        steps.append((at, p, 1, 1.0 - 0.02 * i, {"ring": 1.5}))
        at += 0.45 + 0.06 * i                       # each string a little later
    return _play(steps + [(at + 0.5, "C3", 1, 1.0, {"ring": 2.0})])


def harp_sweep_up():
    """Sweep — the fastest possible rake, almost a single chord."""
    return _play(_rake(_ladder(PENT, 3, 5), gap=0.28, ring=1.5))


# --------------------------------------------------------------------------- #
# Arpeggios and melodic figures.
# --------------------------------------------------------------------------- #
def harp_arp_up():
    """Arpeggio up — C minor, one string per sixteenth, all left ringing."""
    return _play([(i, p, 1, 0.8 + 0.05 * i, {"ring": 1.3}) for i, p in
                  enumerate(("C3", "Eb3", "G3", "C4", "Eb4", "G4"))])


def harp_arp_down():
    """Arpeggio down — the same shape falling."""
    return _play([(i, p, 1, 0.95, {"ring": 1.3}) for i, p in
                  enumerate(("G4", "Eb4", "C4", "G3", "Eb3", "C3"))])


def harp_arp_updown():
    """Arpeggio up and back — a complete little turn."""
    seq = ("C3", "Eb3", "G3", "C4", "G3", "Eb3", "C3")
    return _play([(i, p, 1, 0.9, {"ring": 1.2}) for i, p in enumerate(seq)])


def harp_arp_wide():
    """Wide arpeggio — spread over three octaves, the cinematic version."""
    return _play([(i * 2, p, 2, 0.85 + 0.03 * i, {"ring": 1.8}) for i, p in
                  enumerate(("C2", "G2", "C3", "G3", "C4", "E4"))])


def harp_octaves():
    """Octaves — C3 and C4 struck together, then again an octave up."""
    return _play([(0, ("C3", "C4"), 2, 1.0, {"ring": 1.6}),
                  (4, ("C4", "C5"), 2, 0.9, {"ring": 1.6})])


def harp_rise_3():
    """Three rising strings — C Eb G, deliberate and spaced."""
    return _play([(0, "C4", 2, 0.85, {"ring": 1.3}), (2, "Eb4", 2, 0.9, {"ring": 1.3}),
                  (4, "G4", 2, 1.0, {"ring": 1.8})])


def harp_fall_3():
    """Three falling strings — G Eb C, settling."""
    return _play([(0, "G4", 2, 0.95, {"ring": 1.3}), (2, "Eb4", 2, 0.9, {"ring": 1.3}),
                  (4, "C4", 2, 1.0, {"ring": 1.8})])


def harp_call():
    """Question — a rising figure that stops on the fifth."""
    return _play([(0, "C4", 2, 0.9, {"ring": 1.2}), (2, "E4", 1, 0.85, {"ring": 1.2}),
                  (3, "F4", 1, 0.9, {"ring": 1.2}), (4, "G4", 4, 1.0, {"ring": 1.8})])


def harp_answer():
    """Answer — the figure falling back home, resolved."""
    return _play([(0, "G4", 2, 0.95, {"ring": 1.2}), (2, "F4", 1, 0.85, {"ring": 1.2}),
                  (3, "E4", 1, 0.9, {"ring": 1.2}), (4, "C4", 4, 1.0, {"ring": 2.0})])


def harp_bisbig():
    """Bisbigliando — the whispered tremolo, one chord fluttered eight times."""
    seq = ("C4", "Eb4", "G4", "C4", "Eb4", "G4", "C4", "Eb4")
    return _play([(i, p, 1, 0.55 + 0.03 * i, {"ring": 1.0, "pick": 0.3})
                  for i, p in enumerate(seq)])


SOUNDS = [
    ("harp_note",       "Single ringing string",         harp_note),
    ("harp_low",        "Low bass string",               harp_low),
    ("harp_harmonic",   "Glassy string harmonic",        harp_harmonic),
    ("harp_roll_maj",   "Rolled C major chord",          harp_roll_maj),
    ("harp_roll_min",   "Rolled C minor chord",          harp_roll_min),
    ("harp_roll_maj7",  "Rolled major 7th chord",        harp_roll_maj7),
    ("harp_roll_sus",   "Rolled sus2 chord",             harp_roll_sus),
    ("harp_final",      "Wide two-octave closing roll",  harp_final),
    ("harp_gliss_up",   "Pentatonic gliss up",           harp_gliss_up),
    ("harp_gliss_down", "Pentatonic gliss down",         harp_gliss_down),
    ("harp_gliss_long", "Three-octave gliss",            harp_gliss_long),
    ("harp_gliss_fast", "Quick one-octave flick",        harp_gliss_fast),
    ("harp_gliss_minor", "Minor pentatonic gliss",       harp_gliss_minor),
    ("harp_cascade",    "Falling, slowing cascade",      harp_cascade),
    ("harp_sweep_up",   "Fastest rake, near-chord",      harp_sweep_up),
    ("harp_arp_up",     "Minor arpeggio up",             harp_arp_up),
    ("harp_arp_down",   "Minor arpeggio down",           harp_arp_down),
    ("harp_arp_updown", "Arpeggio up and back",          harp_arp_updown),
    ("harp_arp_wide",   "Three-octave wide arpeggio",    harp_arp_wide),
    ("harp_octaves",    "Octave pairs, twice",           harp_octaves),
    ("harp_rise_3",     "Three rising strings",          harp_rise_3),
    ("harp_fall_3",     "Three falling strings",         harp_fall_3),
    ("harp_call",       "Rising question figure",        harp_call),
    ("harp_answer",     "Falling answer, resolved",      harp_answer),
    ("harp_bisbig",     "Whispered bisbigliando flutter", harp_bisbig),
]
