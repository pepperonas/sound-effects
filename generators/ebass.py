"""E-bass — electric bass guitar: fingered, picked, slapped and muted lines.

Karplus-Strong strings again, but voiced the other way round from the guitar:
a soft fingertip instead of a plectrum (`pick` low), very little damping so the
note sustains, and an amp that keeps the bottom instead of scooping it. The
distinction from the existing `bass` category is deliberate — that one is a
synthesiser, this one is a played instrument, and the motifs are what a bass
player actually does: octave pumps, walking lines, ghost notes, slap.
"""
from synth import pluck, noise_burst, mix, adsr, perc, lowpass, highpass, drive, \
    normalize, note, Noise
from ._music import motif, glide

CATEGORY = "ebass"
GROUP = "music"
DESCRIPTION = "Electric bass: fingered, picked and slapped lines, octave pumps, walks."


def _str(pitch, dur, v=1.0, damp=0.90, decay=0.9986, pick=0.35, mute=0.0, click=0.0):
    """One bass string. `click` adds the slap/pop transient of a string
    snapping back against the frets — the sound slap is really made of."""
    f0 = note(pitch) if isinstance(pitch, str) else pitch
    seed = f0(0.0) if callable(f0) else float(f0)
    n = dur + 0.06
    s = pluck(f0, n,
              damp=min(1.0, damp + 0.20 * mute),
              decay=decay - 0.020 * mute,
              pick=min(1.0, pick + 0.5 * click) * (1.0 - 0.4 * mute),
              env=adsr(0.0015, 0.03, 0.9, 0.06, n),
              noise=Noise(int(seed * 23) | 1))
    if click:
        mix(s, highpass(noise_burst(0.010, perc(200), 0.0, Noise(311)), 1400),
            0.0, 0.30 * click)
    return [x * (0.45 + 0.55 * v) for x in s]


def _rig(s, gain=2.0, tone=2200.0, sub=32.0, level=0.7):
    """Bass rig: a little valve grit, then a cabinet that keeps the bottom."""
    return highpass(lowpass(drive(normalize(s, level), gain), tone), sub)


def _line(steps, gain=2.0, tone=2200.0, **kw):
    return _rig(motif(_str, steps, **kw), gain=gain, tone=tone)


# --------------------------------------------------------------------------- #
# Articulations.
# --------------------------------------------------------------------------- #
def ebass_note():
    """Fingered note — C2, soft attack, long sustain. The default bass sound."""
    return _line([(0, "C2", 10, 1.0)])


def ebass_pick():
    """Picked note — plectrum attack, more edge and a faster front."""
    return _line([(0, "C2", 8, 1.0, {"pick": 0.85, "damp": 0.84})], gain=2.6, tone=2800)


def ebass_slap():
    """Slap — thumb against the string, bright and snapping."""
    return _line([(0, "C2", 5, 1.0, {"click": 1.0, "damp": 0.60, "decay": 0.9975})],
                 gain=3.0, tone=3400)


def ebass_pop():
    """Pop — a finger yanking the high string off the fretboard."""
    return _line([(0, "C3", 4, 1.0, {"click": 1.0, "pick": 0.9, "damp": 0.44})],
                 gain=3.0, tone=4000)


def ebass_mute():
    """Muted note — palm on the strings, short and woody."""
    return _line([(0, "C2", 2, 1.0, {"mute": 0.9})], gain=2.2)


# --------------------------------------------------------------------------- #
# Octave pumps and root work — the bread and butter.
# --------------------------------------------------------------------------- #
def ebass_octave_2():
    """Octave pump — C2 up to C3, the house and disco engine."""
    return _line([(0, "C2", 2, 1.0), (2, "C3", 2, 0.85)])


def ebass_octave_4():
    """Four-step octave pump — low, high, low, high across a bar."""
    return _line([(i, p, 2, g) for i, p, g in
                  ((0, "C2", 1.0), (2, "C3", 0.8), (4, "C2", 0.95), (6, "C3", 0.8))])


def ebass_root_fifth():
    """Root and fifth — C2 to G2, the country and rock alternation."""
    return _line([(0, "C2", 2, 1.0), (2, "G2", 2, 0.9),
                  (4, "C2", 2, 0.95), (6, "G2", 4, 0.9)])


def ebass_pump_8():
    """Straight eighth-note root pump — driving, unshowy, always works."""
    return _line([(i * 2, "C2", 2, 1.0 if i % 2 == 0 else 0.82) for i in range(4)])


def ebass_hold():
    """Long held root — C2 left to ring, for pads and slow sections."""
    return _line([(0, "C2", 18, 0.9, {"decay": 0.9993})])


# --------------------------------------------------------------------------- #
# Walking and melodic lines.
# --------------------------------------------------------------------------- #
def ebass_walk_up():
    """Walking up — C D Eb F, quarter notes, jazz and blues staple."""
    return _line([(i * 4, p, 4, 0.9 + 0.03 * i) for i, p in
                  enumerate(("C2", "D2", "Eb2", "F2"))])


def ebass_walk_down():
    """Walking down — F Eb D C, landing on the root."""
    return _line([(i * 4, p, 4, 0.95) for i, p in
                  enumerate(("F2", "Eb2", "D2", "C2"))])


def ebass_chrom():
    """Chromatic approach — B1 leaning into C2, the way a walk resolves."""
    return _line([(0, "B1", 2, 0.85), (2, "C2", 8, 1.0)])


def ebass_riff_min():
    """Minor riff — C Eb F, the pentatonic bass hook."""
    return _line([(0, "C2", 2, 1.0), (2, "Eb2", 1, 0.85), (3, "F2", 5, 0.95)])


def ebass_climb():
    """Climb — C Eb G Bb into the octave, a rising fill."""
    return _line([(i, p, 1 if i < 4 else 6, 0.8 + 0.05 * i) for i, p in
                  enumerate(("C2", "Eb2", "G2", "Bb2", "C3"))])


def ebass_fall():
    """Fall — C3 down through the minor pentatonic to the low root."""
    return _line([(i, p, 1 if i < 4 else 6, 0.95) for i, p in
                  enumerate(("C3", "Bb2", "G2", "Eb2", "C2"))])


def ebass_fifths():
    """Alternating fifths — C G C G, sixteenths, propulsive."""
    return _line([(i, p, 1 if i < 3 else 4, 0.9) for i, p in
                  enumerate(("C2", "G2", "C2", "G2"))])


def ebass_triplet():
    """Triplet fill — three even notes crammed into two beats."""
    return _line([(0, "C2", 1, 1.0), (1, "Eb2", 1, 0.85), (2, "F2", 1, 0.9),
                  (3, "G2", 5, 1.0)])


def ebass_drop():
    """Octave drop — C3 falling to the low C1, ends a phrase."""
    return _line([(0, "C3", 2, 0.9), (2, "C1", 10, 1.0)])


def ebass_slide_up():
    """Slide into the root — the finger travels up the neck onto C2."""
    return _line([(0, glide("G1", "C2", 0.05, 0.15), 10, 1.0)])


# --------------------------------------------------------------------------- #
# Slap and ghost-note grooves.
# --------------------------------------------------------------------------- #
def ebass_slap_2():
    """Two slaps — thumb, thumb, both on the root."""
    sl = {"click": 1.0, "damp": 0.60, "decay": 0.9975}
    return _line([(0, "C2", 2, 1.0, sl), (3, "C2", 3, 0.9, sl)], gain=3.0, tone=3400)


def ebass_slap_pop():
    """Slap and pop — thumb on the low root, finger popping the octave."""
    sl = {"click": 1.0, "damp": 0.60, "decay": 0.9975}
    pop = {"click": 1.0, "pick": 0.9, "damp": 0.44}
    return _line([(0, "C2", 2, 1.0, sl), (2, "C3", 2, 0.95, pop),
                  (4, "C2", 4, 0.9, sl)], gain=3.0, tone=3600)


def ebass_slap_groove():
    """Slap groove — thumb, ghost, pop, thumb: a whole bar of funk."""
    sl = {"click": 1.0, "damp": 0.60, "decay": 0.9975}
    gh = {"mute": 1.0, "click": 0.5}
    pop = {"click": 1.0, "pick": 0.9, "damp": 0.44}
    return _line([(0, "C2", 2, 1.0, sl), (2, "C2", 1, 0.45, gh),
                  (3, "C3", 1, 0.95, pop), (4, "Eb2", 1, 0.5, gh),
                  (5, "C2", 5, 0.9, sl)], gain=3.0, tone=3600)


def ebass_ghost():
    """Ghost notes — two dead thuds leading into the real note."""
    gh = {"mute": 1.0}
    return _line([(0, "C2", 1, 0.4, gh), (1, "C2", 1, 0.4, gh), (2, "C2", 8, 1.0)])


def ebass_fill():
    """Busy fill — six fast notes running back to the root, end of a bar."""
    return _line([(i, p, 1 if i < 5 else 5, 0.8 + 0.04 * i) for i, p in
                  enumerate(("C2", "Eb2", "F2", "G2", "Bb2", "C3"))], gain=2.4)


SOUNDS = [
    ("ebass_note",        "Fingered sustained note",       ebass_note),
    ("ebass_pick",        "Plectrum-picked note",          ebass_pick),
    ("ebass_slap",        "Thumb slap on the root",        ebass_slap),
    ("ebass_pop",         "Popped high string",            ebass_pop),
    ("ebass_mute",        "Palm-muted woody note",         ebass_mute),
    ("ebass_octave_2",    "Two-step octave pump",          ebass_octave_2),
    ("ebass_octave_4",    "Four-step octave pump",         ebass_octave_4),
    ("ebass_root_fifth",  "Root-fifth alternation",        ebass_root_fifth),
    ("ebass_pump_8",      "Straight eighth-note pump",     ebass_pump_8),
    ("ebass_hold",        "Long held ringing root",        ebass_hold),
    ("ebass_walk_up",     "Walking line up C-D-Eb-F",      ebass_walk_up),
    ("ebass_walk_down",   "Walking line down F-Eb-D-C",    ebass_walk_down),
    ("ebass_chrom",       "Chromatic approach into C",     ebass_chrom),
    ("ebass_riff_min",    "Minor pentatonic bass hook",    ebass_riff_min),
    ("ebass_climb",       "Rising fill to the octave",     ebass_climb),
    ("ebass_fall",        "Descending pentatonic fall",    ebass_fall),
    ("ebass_fifths",      "Alternating fifths, sixteenths", ebass_fifths),
    ("ebass_triplet",     "Triplet fill into the fifth",   ebass_triplet),
    ("ebass_drop",        "Octave drop to the low root",   ebass_drop),
    ("ebass_slide_up",    "Slide up the neck into C",      ebass_slide_up),
    ("ebass_slap_2",      "Two thumb slaps",               ebass_slap_2),
    ("ebass_slap_pop",    "Slap and pop octave",           ebass_slap_pop),
    ("ebass_slap_groove", "Full funk slap groove",         ebass_slap_groove),
    ("ebass_ghost",       "Ghost notes into the root",     ebass_ghost),
    ("ebass_fill",        "Six-note run back to the root", ebass_fill),
]
