"""Strings — a bowed string section: swells, stabs, pizzicato and runs.

A string *section* is not one violin made louder. It is a dozen players whose
pitches never quite agree and whose vibrato never quite lines up, and that
disagreement is the sound: it turns a thin sawtooth into something wide and
breathing. So the voice here is a detuned unison stack, and the ensemble size
is a parameter — two players for a lean solo line, six for a film-score wall.

The bow is the other half. It takes time to get the string moving, so the
attack is slow and the brightness arrives *after* the volume does: the filter
opens as the bow digs in. Pizzicato is the exception — there the string is
plucked, so it uses the plucked-string model instead.
"""
from synth import pluck, mix, adsr, perc, lowpass, highpass, vibrato, note, Noise
from ._music import motif, stack, filter_env

CATEGORY = "strings"
GROUP = "music"
DESCRIPTION = "Bowed string section: swells, stabs, tremolo, pizzicato and runs."

MIN = ("C3", "Eb3", "G3")
MAJ = ("C3", "E3", "G3")


def _bowed(pitch, dur, v=1.0, bow=0.09, players=4, detune=0.006, vib=0.005,
           rel=0.22, bright=1.0, sus=0.85):
    """One bowed line. `bow` is how long the string takes to speak; `players`
    is how many of them are playing it."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + rel
    f = vibrato(f0, rate=5.4, depth=vib, onset=0.35) if vib else f0
    env = adsr(bow, 0.10, sus, rel, n)
    s = stack("saw", f, n, env, detune=detune, voices=players, side=0.78)
    lo = min(700.0, f0 * 1.5)
    span = (f0 * 7.0 + 900.0) * bright * (0.5 + 0.5 * v)
    s = lowpass(s, filter_env(lo, span, rise=0.075, fall=0.5, sustain=0.6))
    return [x * (0.4 + 0.6 * v) / players ** 0.5 for x in s]


def _pizz(pitch, dur, v=1.0, rel=0.10, **_):
    """Pizzicato — the string plucked, not bowed: short, dry, woody."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + rel
    s = pluck(f0, n, damp=0.76, decay=0.9955, pick=0.55,
              env=adsr(0.002, 0.03, 0.8, rel, n), noise=Noise(int(f0 * 13) | 1))
    return [x * (0.45 + 0.55 * v) for x in s]


def _play(steps, voice=_bowed, tone=4800.0, **kw):
    return highpass(lowpass(motif(voice, steps, **kw), tone), 55.0)


# --------------------------------------------------------------------------- #
# Sustained textures.
# --------------------------------------------------------------------------- #
def strings_swell():
    """Swell — one note bowed in slowly and let go, the film-score gesture."""
    return _play([(0, "C3", 14, 0.95, {"bow": 0.30, "players": 6, "rel": 0.5})])


def strings_swell_chord():
    """Chord swell — the whole section arriving together on a minor triad."""
    return _play([(0, MIN, 14, 0.9, {"bow": 0.32, "players": 6, "rel": 0.5})])


def strings_hold_maj():
    """Held major triad — steady, warm, the bed under everything."""
    return _play([(0, MAJ, 12, 0.85, {"players": 5, "rel": 0.4})])


def strings_hold_min():
    """Held minor triad — the same bed, darker."""
    return _play([(0, MIN, 12, 0.85, {"players": 5, "rel": 0.4})])


def strings_solo():
    """Solo line — two players only, lean and exposed, wide vibrato."""
    return _play([(0, "G3", 12, 0.9, {"players": 2, "vib": 0.009, "bow": 0.12})])


def strings_high():
    """High sustain — the violins up top, thin and tense."""
    return _play([(0, "C5", 12, 0.8, {"players": 5, "bright": 1.3})])


def strings_low():
    """Low sustain — cellos and basses, dark and slow to speak."""
    return _play([(0, "C2", 12, 0.9, {"players": 5, "bow": 0.16, "bright": 0.7})])


# --------------------------------------------------------------------------- #
# Short bowed articulations.
# --------------------------------------------------------------------------- #
def strings_stab():
    """Stab — the whole section attacking one chord and stopping dead."""
    return _play([(0, MIN, 2, 1.0, {"bow": 0.012, "players": 6, "rel": 0.10,
                                    "vib": 0.0, "bright": 1.4})])


def strings_stab_3():
    """Three stabs — the Psycho shower-scene rhythm, minus the screaming."""
    k = {"bow": 0.012, "players": 6, "rel": 0.09, "vib": 0.0, "bright": 1.4}
    return _play([(0, MIN, 1, 1.0, k), (2, MIN, 1, 0.9, k), (4, MIN, 2, 1.0, k)])


def strings_staccato():
    """Staccato line — four short bowed notes walking up the triad."""
    k = {"bow": 0.020, "players": 4, "rel": 0.10, "vib": 0.0}
    return _play([(i * 2, p, 1, 0.9, k) for i, p in
                  enumerate(("C3", "Eb3", "G3", "C4"))])


def strings_marcato():
    """Marcato — heavily accented long notes, each one dug into."""
    k = {"bow": 0.025, "players": 6, "rel": 0.15, "bright": 1.25}
    return _play([(0, "C3", 3, 1.0, k), (4, "Eb3", 3, 0.95, k), (8, "G3", 6, 1.0, k)])


def strings_tremolo():
    """Tremolo — the bow shivering on one note, pure suspense."""
    k = {"bow": 0.006, "players": 5, "rel": 0.05, "vib": 0.0}
    return _play([(i, "C3", 1, 0.75 + 0.08 * (i % 2), k) for i in range(14)])


def strings_tremolo_chord():
    """Tremolo chord — the same shiver across a minor triad."""
    k = {"bow": 0.006, "players": 4, "rel": 0.05, "vib": 0.0}
    return _play([(i, MIN, 1, 0.72 + 0.08 * (i % 2), k) for i in range(12)])


# --------------------------------------------------------------------------- #
# Pizzicato.
# --------------------------------------------------------------------------- #
def strings_pizz():
    """Pizzicato — one plucked note, dry and short."""
    return _play([(0, "C3", 2, 1.0)], voice=_pizz)


def strings_pizz_2():
    """Two pizzicato notes — root and fifth, the walking-bass gesture."""
    return _play([(0, "C3", 2, 1.0), (2, "G3", 3, 0.9)], voice=_pizz)


def strings_pizz_riff():
    """Pizzicato riff — four plucked notes, the spy-film ostinato."""
    return _play([(i * 2, p, 2, 0.9) for i, p in
                  enumerate(("C3", "Eb3", "G3", "Eb3"))], voice=_pizz)


def strings_pizz_chord():
    """Plucked chord — the section pizzing a minor triad together."""
    return _play([(0, MIN, 3, 1.0)], voice=_pizz)


# --------------------------------------------------------------------------- #
# Lines and progressions.
# --------------------------------------------------------------------------- #
def strings_pizz_low():
    """Low pizzicato — a plucked bass note, the section's footstep."""
    return _play([(0, "C2", 3, 1.0)], voice=_pizz)


def strings_rise_3():
    """Three rising notes — the section climbing the triad."""
    return _play([(0, "C3", 3, 0.85, {"bow": 0.05}), (3, "Eb3", 3, 0.9, {"bow": 0.05}),
                  (6, "G3", 8, 1.0, {"bow": 0.06, "players": 6})])


def strings_fall_3():
    """Three falling notes — settling back onto the root."""
    return _play([(0, "G3", 3, 0.95, {"bow": 0.05}), (3, "Eb3", 3, 0.9, {"bow": 0.05}),
                  (6, "C3", 8, 1.0, {"bow": 0.06, "players": 6})])


def strings_run_up():
    """Run up — six quick bowed notes through the minor scale."""
    k = {"bow": 0.018, "rel": 0.10, "players": 4, "vib": 0.0}
    return _play([(i, p, 1 if i < 5 else 6, 0.85, k) for i, p in
                  enumerate(("C4", "D4", "Eb4", "F4", "G4", "Ab4"))])


def strings_run_down():
    """Run down — the same scale falling back."""
    k = {"bow": 0.018, "rel": 0.10, "players": 4, "vib": 0.0}
    return _play([(i, p, 1 if i < 5 else 6, 0.9, k) for i, p in
                  enumerate(("Ab4", "G4", "F4", "Eb4", "D4", "C4"))])


def strings_cadence():
    """Cadence — Fm to G to Cm, the section resolving a phrase."""
    return _play([(0, ("F3", "Ab3", "C4"), 4, 0.9, {"players": 5}),
                  (4, ("G3", "B3", "D4"), 4, 0.95, {"players": 5}),
                  (8, MIN, 10, 1.0, {"players": 6})])


def strings_octaves():
    """Octaves — C3 and C4 bowed together, the unison power move."""
    return _play([(0, ("C3", "C4"), 12, 0.95, {"players": 5})])


def strings_crescendo():
    """Crescendo — one chord growing from nothing to full section."""
    s = _play([(0, MIN, 16, 1.0, {"bow": 0.5, "players": 6, "rel": 0.4})])
    n = int(0.75 * 44100)
    return [x * min(1.0, (i / n) ** 1.5) if i < n else x for i, x in enumerate(s)]


SOUNDS = [
    ("strings_swell",        "Single note bowed in",        strings_swell),
    ("strings_swell_chord",  "Minor chord swell",           strings_swell_chord),
    ("strings_hold_maj",     "Held major triad",            strings_hold_maj),
    ("strings_hold_min",     "Held minor triad",            strings_hold_min),
    ("strings_solo",         "Exposed two-player line",     strings_solo),
    ("strings_high",         "High tense violin sustain",   strings_high),
    ("strings_low",          "Dark cello/bass sustain",     strings_low),
    ("strings_stab",         "Full-section chord stab",     strings_stab),
    ("strings_stab_3",       "Three shrieking stabs",       strings_stab_3),
    ("strings_staccato",     "Four short bowed notes",      strings_staccato),
    ("strings_marcato",      "Accented rising long notes",  strings_marcato),
    ("strings_tremolo",      "Single-note bow tremolo",     strings_tremolo),
    ("strings_tremolo_chord", "Tremolo across a triad",     strings_tremolo_chord),
    ("strings_pizz",         "Single pizzicato note",       strings_pizz),
    ("strings_pizz_2",       "Pizzicato root and fifth",    strings_pizz_2),
    ("strings_pizz_riff",    "Four-note pizzicato ostinato", strings_pizz_riff),
    ("strings_pizz_chord",   "Plucked minor triad",         strings_pizz_chord),
    ("strings_rise_3",       "Three rising bowed notes",    strings_rise_3),
    ("strings_fall_3",       "Three falling bowed notes",   strings_fall_3),
    ("strings_run_up",       "Quick ascending bowed run",   strings_run_up),
    ("strings_run_down",     "Quick descending bowed run",  strings_run_down),
    ("strings_cadence",      "Fm-G-Cm section cadence",     strings_cadence),
    ("strings_octaves",      "Bowed octaves in unison",     strings_octaves),
    ("strings_crescendo",    "Chord growing from nothing",  strings_crescendo),
    ("strings_pizz_low",     "Low plucked bass note",       strings_pizz_low),
]
