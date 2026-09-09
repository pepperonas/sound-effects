"""Choir — synthetic voices: vowels, swells, stabs and chords.

Proper source-filter vocal synthesis rather than a pad with a nice name. The
vocal tract is a tube whose resonances — the formants — sit at fixed
frequencies no matter what note you sing; a vowel IS its formant pattern. So
every harmonic of the sung pitch is given the gain the tract would lend it at
that frequency, and changing "ah" to "oo" moves the resonances, not the pitch.

That is also why the vowel survives transposition here: sing the same "ah" an
octave up and the formants stay put while the harmonics move through them,
exactly as in a real voice.

A choir is many singers, so every note is doubled with a detuned partner whose
vibrato runs at a different rate — no two people ever wobble together, and
that mismatch is what turns one voice into a section.
"""
import math
from synth import noise_burst, mix, adsr, lowpass, highpass, note, Noise
from ._music import motif, additive

CATEGORY = "choir"
GROUP = "music"
DESCRIPTION = "Synthetic choir: vowel formants, swells, stabs, chords and cadences."

# (centre Hz, strength, bandwidth) per formant — the shape of the tract.
VOWELS = {
    "ah": ((730, 1.00, 130), (1090, 0.50, 170), (2440, 0.22, 240)),
    "oo": ((300, 1.00, 90), (870, 0.26, 130), (2240, 0.08, 200)),
    "oh": ((570, 1.00, 110), (840, 0.55, 150), (2410, 0.11, 220)),
    "eh": ((530, 1.00, 110), (1840, 0.52, 190), (2480, 0.28, 240)),
    "mm": ((280, 1.00, 80), (1200, 0.12, 150), (2200, 0.04, 200)),
}


def _parts(f0, vowel):
    """Harmonic gains shaped by the tract's resonances."""
    out = []
    for k in range(1, 25):
        f = k * f0
        if f > 3400.0:
            break
        g = sum(a * math.exp(-((f - fc) / bw) ** 2) for fc, a, bw in VOWELS[vowel])
        g /= 1.0 + 0.28 * (k - 1)                  # the glottal source rolls off
        if g > 0.005:
            out.append((k, g, 0.0))
    return out or [(1, 1.0, 0.0)]


def _voice(pitch, dur, v=1.0, vowel="ah", attack=0.16, rel=0.35, vib=0.006,
           section=True, breath=0.5):
    """One sung note, doubled by a second singer if `section`."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + rel
    env = adsr(attack, 0.15, 0.88, rel, n)
    s = additive(f0, n, _parts(f0, vowel), attack=0.004, vib=(5.1, vib))
    if section:
        # A second singer: 7 cents flat, wobbling at a different speed.
        d = additive(f0 * 0.9960, n, _parts(f0 * 0.9960, vowel),
                     attack=0.004, vib=(6.3, vib * 1.25))
        mix(s, d, 0.0, 0.85)
    s = [x * env(i / 44100.0) for i, x in enumerate(s)]
    if breath:                                     # air escaping past the folds
        mix(s, lowpass(highpass(noise_burst(n, env, 0.0, Noise(int(f0) | 7)), 700),
                       3000), 0.0, 0.045 * breath)
    return [x * (0.4 + 0.6 * v) for x in s]


def _play(steps, tone=5000.0, **kw):
    return highpass(lowpass(motif(_voice, steps, **kw), tone), 60.0)


MIN = ("C3", "Eb3", "G3")
MAJ = ("C3", "E3", "G3")


# --------------------------------------------------------------------------- #
# The vowels themselves.
# --------------------------------------------------------------------------- #
def choir_ah():
    """"Ah" — the open vowel, the default choir sound."""
    return _play([(0, "C3", 10, 0.9)])


def choir_oo():
    """"Oo" — rounded and dark, almost a flute."""
    return _play([(0, "C3", 10, 0.9, {"vowel": "oo"})])


def choir_oh():
    """"Oh" — between the two, warm and round."""
    return _play([(0, "C3", 10, 0.9, {"vowel": "oh"})])


def choir_eh():
    """"Eh" — the bright vowel, its second formant far up."""
    return _play([(0, "C3", 10, 0.9, {"vowel": "eh"})])


def choir_hum():
    """Hummed "mm" — lips closed, almost no upper formants."""
    return _play([(0, "C3", 12, 0.8, {"vowel": "mm", "breath": 0.2})])


def choir_low():
    """Basses — the same "ah" an octave down, chesty."""
    return _play([(0, "C2", 12, 0.9, {"vowel": "oh"})])


def choir_high():
    """Sopranos — high and bright, the harmonics sweeping past the formants."""
    return _play([(0, "C4", 10, 0.85, {"vowel": "ah"})])


def choir_solo():
    """Solo voice — one singer, no doubling, wide vibrato and exposed."""
    return _play([(0, "G3", 10, 0.85, {"section": False, "vib": 0.011})])


# --------------------------------------------------------------------------- #
# Chords.
# --------------------------------------------------------------------------- #
def choir_maj():
    """Major triad — the whole section on one chord."""
    return _play([(0, MAJ, 12, 0.9)])


def choir_min():
    """Minor triad — the same, darker."""
    return _play([(0, MIN, 12, 0.9)])


def choir_min7():
    """Minor 7th — four parts, close harmony."""
    return _play([(0, ("C3", "Eb3", "G3", "Bb3"), 12, 0.9)])


def choir_sus():
    """Sus4 — no third, the open medieval sound."""
    return _play([(0, ("C3", "F3", "G3"), 12, 0.9)])


def choir_octaves():
    """Octaves — the men enter first, the women join an octave above."""
    return _play([(0, ("C2", "C3"), 12, 0.9, {"vowel": "oh"}),
                  (3, "C4", 9, 0.8, {"vowel": "oh", "attack": 0.22})])


def choir_wide():
    """Wide voicing — built from the bottom up, three octaves of the chord."""
    return _play([(0, ("C2", "G2"), 12, 0.9),
                  (2, ("C3", "E3"), 10, 0.85),
                  (4, "G3", 8, 0.8, {"attack": 0.22})])


def choir_cluster():
    """Cluster — three neighbouring notes at once, deliberately uneasy."""
    return _play([(0, ("C3", "D3", "Eb3"), 10, 0.85, {"vowel": "oo"})])


# --------------------------------------------------------------------------- #
# Gestures.
# --------------------------------------------------------------------------- #
def choir_swell():
    """Swell — the section breathing in on a minor chord."""
    return _play([(0, MIN, 14, 0.95, {"attack": 0.55, "rel": 0.6})])


def choir_swell_maj():
    """Major swell — the same breath, resolved and bright."""
    return _play([(0, MAJ, 14, 0.95, {"attack": 0.55, "rel": 0.6})])


def choir_stab():
    """Stab — a shouted "ah", cut off immediately."""
    return _play([(0, MIN, 2, 1.0, {"attack": 0.020, "rel": 0.10, "vib": 0.0})])


def choir_stab_2():
    """Two stabs — the shouted-chorus rhythm."""
    k = {"attack": 0.020, "rel": 0.10, "vib": 0.0}
    return _play([(0, MIN, 1, 1.0, k), (2, MIN, 2, 0.95, k)])


def choir_hit():
    """Two hard "eh" hits — the shouted accent, answered by itself."""
    k = {"vowel": "eh", "attack": 0.016, "rel": 0.12, "vib": 0.0}
    return _play([(0, ("C3", "G3", "C4"), 1, 1.0, k),
                  (3, ("C3", "G3", "C4"), 3, 0.9, k)])


def choir_rise():
    """Rising line — three chords climbing, the section lifting."""
    return _play([(0, MIN, 4, 0.85, {"attack": 0.10}),
                  (4, ("Eb3", "G3", "Bb3"), 4, 0.9, {"attack": 0.10}),
                  (8, ("G3", "Bb3", "D4"), 10, 1.0, {"attack": 0.12})])


def choir_fall():
    """Falling line — the same three chords coming back down."""
    return _play([(0, ("G3", "Bb3", "D4"), 4, 0.95, {"attack": 0.10}),
                  (4, ("Eb3", "G3", "Bb3"), 4, 0.9, {"attack": 0.10}),
                  (8, MIN, 10, 1.0, {"attack": 0.12})])


def choir_cadence():
    """Cadence — Fm to G to Cm, the section resolving."""
    return _play([(0, ("F3", "Ab3", "C4"), 5, 0.9, {"attack": 0.10}),
                  (5, ("G3", "B3", "D4"), 5, 0.95, {"attack": 0.10}),
                  (10, MIN, 12, 1.0, {"attack": 0.12})])


def choir_amen():
    """Plagal "amen" — F major into C major, sung on "ah" then "eh"."""
    return _play([(0, ("F3", "A3", "C4"), 6, 0.9, {"attack": 0.12}),
                  (6, MAJ, 14, 0.95, {"vowel": "eh", "attack": 0.14})])


def choir_vowel_shift():
    """Vowel change — the same chord held while the section opens from oo to ah."""
    a = _play([(0, MIN, 6, 0.9, {"vowel": "oo", "rel": 0.5})])
    b = _play([(0, MIN, 8, 0.9, {"vowel": "ah", "attack": 0.35, "rel": 0.6})])
    out = list(a)
    mix(out, b, 0.42, 1.0)
    return out


SOUNDS = [
    ("choir_ah",         "Open 'ah' vowel",            choir_ah),
    ("choir_oo",         "Dark rounded 'oo'",          choir_oo),
    ("choir_oh",         "Warm 'oh' vowel",            choir_oh),
    ("choir_eh",         "Bright 'eh' vowel",          choir_eh),
    ("choir_hum",        "Closed-lip hum",             choir_hum),
    ("choir_low",        "Bass section, octave down",  choir_low),
    ("choir_high",       "Bright soprano note",        choir_high),
    ("choir_solo",       "Single exposed voice",       choir_solo),
    ("choir_maj",        "Major triad",                choir_maj),
    ("choir_min",        "Minor triad",                choir_min),
    ("choir_min7",       "Minor 7th, four parts",      choir_min7),
    ("choir_sus",        "Open sus4 chord",            choir_sus),
    ("choir_octaves",    "Three-octave unison",        choir_octaves),
    ("choir_wide",       "Wide spread voicing",        choir_wide),
    ("choir_cluster",    "Uneasy three-note cluster",  choir_cluster),
    ("choir_swell",      "Minor chord swell",          choir_swell),
    ("choir_swell_maj",  "Major chord swell",          choir_swell_maj),
    ("choir_stab",       "Shouted chord stab",         choir_stab),
    ("choir_stab_2",     "Two shouted stabs",          choir_stab_2),
    ("choir_hit",        "Single hard downbeat hit",   choir_hit),
    ("choir_rise",       "Three rising chords",        choir_rise),
    ("choir_fall",       "Three falling chords",       choir_fall),
    ("choir_cadence",    "Fm-G-Cm cadence",            choir_cadence),
    ("choir_amen",       "Plagal 'amen' cadence",      choir_amen),
    ("choir_vowel_shift", "Held chord opening oo->ah", choir_vowel_shift),
]
