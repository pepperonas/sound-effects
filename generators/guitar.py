"""Guitar — electric guitar: power chords, chugs, riffs, bends and arpeggios.

The strings are real Karplus-Strong: a noise burst circulating in a damped
delay line, the same physics as a plucked string, which is why these read as
"guitar" and not as "filtered saw with a fast decay".

The amp is applied to the *whole performance*, not to each note — that is the
one detail that makes a power chord sound like a power chord. Distorting the
summed signal lets the root and the fifth intermodulate, which is exactly what
happens in front of a real speaker; distorting each string on its own gives a
clean stack of fuzzy notes and no weight at all.
"""
from synth import pluck, noise_burst, mix, adsr, perc, lowpass, highpass, drive, \
    normalize, note, Noise
from ._music import motif, glide

CATEGORY = "guitar"
GROUP = "music"
DESCRIPTION = "Electric guitar: power chords, palm-muted chugs, riffs, bends, arpeggios."

# Power chord = root, fifth, octave. With distortion a full triad turns to mud;
# the third is what muddies it, so rock guitar simply leaves it out.
def _power(root):
    o = {"C2": ("C2", "G2", "C3"), "D2": ("D2", "A2", "D3"),
         "Eb2": ("Eb2", "Bb2", "Eb3"), "F2": ("F2", "C3", "F3"),
         "G2": ("G2", "D3", "G3"), "Bb2": ("Bb2", "F3", "Bb3"),
         "C3": ("C3", "G3", "C4")}
    return o[root]


def _string(pitch, dur, v=1.0, damp=0.80, decay=0.9967, pick=0.85, mute=0.0):
    """One picked string. `mute` 0..1 is the palm resting on the bridge."""
    f0 = note(pitch) if isinstance(pitch, str) else pitch
    seed = f0(0.0) if callable(f0) else float(f0)     # bends arrive as f(t)
    n = dur + 0.05
    # The hand damps the string itself — it shortens the decay AND kills the
    # top end. Faking a mute with a short amp envelope alone sounds like a
    # gate, not like a palm.
    s = pluck(f0, n,
              damp=min(1.0, damp + 0.24 * mute),
              decay=decay - 0.055 * mute,
              pick=pick * (1.0 - 0.45 * mute),
              env=adsr(0.0012, 0.02, 0.9, 0.05, n),
              noise=Noise(int(seed * 17) | 1))
    if mute > 0.5:                                    # pick attack on a dead note
        mix(s, highpass(noise_burst(0.008, perc(240), 0.0, Noise(77)), 1800), 0.0, 0.25)
    return [x * (0.45 + 0.55 * v) for x in s]


def _amp(s, gain=5.0, tone=3600.0, tight=95.0, level=0.7):
    """Distortion into a speaker cab. Normalising first makes `gain` mean the
    same thing whether it is fed one string or a six-string chord."""
    s = drive(normalize(s, level), gain)
    return highpass(lowpass(s, tone), tight)


def _riff(steps, gain=5.0, tone=3600.0, spread=0.0, **kw):
    return _amp(motif(_string, steps, spread=spread, **kw), gain=gain, tone=tone)


# --------------------------------------------------------------------------- #
# Articulations — one note or one chord.
# --------------------------------------------------------------------------- #
def guitar_note():
    """Single picked note — C3, light crunch, left to ring."""
    return _riff([(0, "C3", 8, 1.0)], gain=2.2, tone=4200)


def guitar_power():
    """Power chord — C2/G2/C3 strummed and held, full distortion."""
    return _riff([(0, _power("C2"), 10, 1.0)], spread=0.010)


def guitar_chug():
    """Palm-muted chug — the muted C2 power chord, short and percussive."""
    return _riff([(0, _power("C2"), 1, 1.0, {"mute": 0.85})], spread=0.004, gain=6.5)


def guitar_harmonic():
    """Natural harmonic — glassy bell tone, clean, rings on."""
    return _riff([(0, "C5", 10, 0.75, {"damp": 0.24, "decay": 0.9992, "pick": 1.0})],
                 gain=1.6, tone=6500)


# --------------------------------------------------------------------------- #
# Chug figures — the rhythm-guitar backbone.
# --------------------------------------------------------------------------- #
def guitar_chug_2():
    """Two chugs — even eighths on the muted C power chord."""
    m = {"mute": 0.85}
    return _riff([(0, _power("C2"), 1, 1.0, m), (2, _power("C2"), 1, 0.95, m)],
                 spread=0.004, gain=6.5)


def guitar_gallop():
    """Gallop — long-short-short, the metal rhythm signature."""
    m = {"mute": 0.85}
    return _riff([(0, _power("C2"), 2, 1.0, m), (2, _power("C2"), 1, 0.85, m),
                  (3, _power("C2"), 1, 0.9, m)], spread=0.004, gain=6.5)


def guitar_chug_open():
    """Chug-chug-ring — two muted hits released into an open chord."""
    m = {"mute": 0.85}
    return _riff([(0, _power("C2"), 1, 0.95, m), (1, _power("C2"), 1, 0.9, m),
                  (2, _power("C2"), 8, 1.0)], spread=0.008, gain=6.0)


# --------------------------------------------------------------------------- #
# Power-chord moves.
# --------------------------------------------------------------------------- #
def guitar_power_up():
    """Rising power chords — C, F, G, the oldest move in rock."""
    return _riff([(0, _power("C2"), 3, 0.9), (4, _power("F2"), 3, 0.95),
                  (8, _power("G2"), 8, 1.0)], spread=0.009)


def guitar_power_down():
    """Falling power chords — G, F, C, landing home."""
    return _riff([(0, _power("G2"), 3, 0.95), (4, _power("F2"), 3, 0.9),
                  (8, _power("C2"), 8, 1.0)], spread=0.009)


def guitar_power_flat6():
    """Flat-six turnaround — C, Bb, Eb: the heavy-rock minor cadence."""
    return _riff([(0, _power("C2"), 3, 1.0), (4, _power("Bb2"), 3, 0.9),
                  (8, _power("Eb2"), 8, 0.95)], spread=0.009)


def guitar_stop():
    """Full stop — one big chord, cut dead. The end of the section."""
    return _riff([(0, _power("C2"), 3, 1.0)], spread=0.012, gain=5.5)


def guitar_octaves():
    """Octave stab — C2 with C3 on top, hit twice."""
    return _riff([(0, ("C2", "C3"), 2, 1.0), (3, ("C2", "C3"), 5, 0.95)], gain=4.5)


# --------------------------------------------------------------------------- #
# Single-note riffs and runs — C minor pentatonic.
# --------------------------------------------------------------------------- #
def guitar_riff_low():
    """Low riff — C, Eb, F on the bottom string, chunky."""
    return _riff([(0, "C2", 2, 1.0), (2, "Eb2", 1, 0.85), (3, "F2", 4, 0.95)], gain=5.5)


def guitar_riff_min():
    """Minor pentatonic riff — C, Eb, F, G, the four notes every riff is made of."""
    return _riff([(0, "C3", 2, 1.0), (2, "Eb3", 1, 0.85), (3, "F3", 1, 0.9),
                  (4, "G3", 6, 1.0)], gain=4.0)


def guitar_riff_chug():
    """Chug into riff — muted low hits answered by a pentatonic phrase."""
    m = {"mute": 0.85}
    return _riff([(0, "C2", 1, 1.0, m), (1, "C2", 1, 0.9, m),
                  (2, "Eb3", 1, 0.9), (3, "F3", 1, 0.9), (4, "G3", 6, 1.0)], gain=5.5)


def guitar_run_up():
    """Fast ascending run — C Eb F G Bb C, sixteenths."""
    return _riff([(i, p, 1 if i < 5 else 6, 0.8 + 0.04 * i) for i, p in
                  enumerate(("C3", "Eb3", "F3", "G3", "Bb3", "C4"))], gain=3.6, tone=4200)


def guitar_run_down():
    """Fast descending run — C Bb G F Eb C."""
    return _riff([(i, p, 1 if i < 5 else 6, 1.0 - 0.03 * i) for i, p in
                  enumerate(("C4", "Bb3", "G3", "F3", "Eb3", "C3"))], gain=3.6, tone=4200)


def guitar_tremolo():
    """Tremolo picking — one note hammered eight times, black-metal texture."""
    return _riff([(i, "C3", 1, 0.85 + (0.1 if i % 2 == 0 else 0.0)) for i in range(8)],
                 gain=5.0)


# --------------------------------------------------------------------------- #
# Bends and slides — where the variable delay line earns its keep.
# --------------------------------------------------------------------------- #
def guitar_bend():
    """Whole-tone bend — G3 pushed up to A3 and held."""
    return _riff([(0, glide("G3", "A3", 0.10, 0.13), 10, 1.0)], gain=4.5)


def guitar_bend_release():
    """Bend and release — up a tone and back down, the blues cry."""
    f_up = glide("G3", "A3", 0.10, 0.12)
    f_dn = glide("A3", "G3", 0.34, 0.14)
    return _riff([(0, lambda t: f_up(t) if t < 0.34 else f_dn(t), 12, 1.0)], gain=4.5)


def guitar_slide_up():
    """Slide up — the finger travels from F2 into the C3 power chord."""
    return _riff([(0, glide("F2", "C3", 0.045, 0.13), 4, 1.0),
                  (4, _power("C2"), 8, 1.0)], spread=0.009, gain=5.5)


# --------------------------------------------------------------------------- #
# Clean playing.
# --------------------------------------------------------------------------- #
def guitar_strum_down():
    """Clean downstroke — full C minor chord, strummed low to high."""
    return _riff([(0, ("C3", "Eb3", "G3", "C4"), 10, 1.0)], spread=0.016,
                 gain=1.8, tone=4600)


def guitar_strum_up():
    """Clean upstroke — the same chord raked high to low, lighter."""
    return _riff([(0, ("C3", "Eb3", "G3", "C4"), 10, 0.8)], spread=-0.013,
                 gain=1.8, tone=4600)


def guitar_arp():
    """Picked arpeggio — C minor, one string at a time, left ringing."""
    return _riff([(i, p, 10 - i, 0.8 + 0.05 * i) for i, p in
                  enumerate(("C3", "Eb3", "G3", "C4"))], gain=1.8, tone=4800,
                 decay=0.9985)


def guitar_arp_down():
    """Descending arpeggio — C4 down to C3, clean and ringing."""
    return _riff([(i, p, 10 - i, 0.9) for i, p in
                  enumerate(("C4", "G3", "Eb3", "C3"))], gain=1.8, tone=4800,
                 decay=0.9985)


SOUNDS = [
    ("guitar_note",       "Single picked crunch note",      guitar_note),
    ("guitar_power",      "Held C power chord",             guitar_power),
    ("guitar_chug",       "Single palm-muted chug",         guitar_chug),
    ("guitar_harmonic",   "Glassy natural harmonic",        guitar_harmonic),
    ("guitar_chug_2",     "Two palm-muted chugs",           guitar_chug_2),
    ("guitar_gallop",     "Long-short-short metal gallop",  guitar_gallop),
    ("guitar_chug_open",  "Two chugs into an open chord",   guitar_chug_open),
    ("guitar_power_up",   "Rising C-F-G power chords",      guitar_power_up),
    ("guitar_power_down", "Falling G-F-C power chords",     guitar_power_down),
    ("guitar_power_flat6", "Flat-six C-Bb-Eb turnaround",   guitar_power_flat6),
    ("guitar_stop",       "Single full-stop chord",         guitar_stop),
    ("guitar_octaves",    "Octave stab, hit twice",         guitar_octaves),
    ("guitar_riff_low",   "Chunky low-string riff",         guitar_riff_low),
    ("guitar_riff_min",   "Minor pentatonic riff",          guitar_riff_min),
    ("guitar_riff_chug",  "Chugs answered by a riff",       guitar_riff_chug),
    ("guitar_run_up",     "Fast ascending pentatonic run",  guitar_run_up),
    ("guitar_run_down",   "Fast descending run",            guitar_run_down),
    ("guitar_tremolo",    "Tremolo-picked single note",     guitar_tremolo),
    ("guitar_bend",       "Whole-tone bend, held",          guitar_bend),
    ("guitar_bend_release", "Bend up and release",          guitar_bend_release),
    ("guitar_slide_up",   "Slide into a power chord",       guitar_slide_up),
    ("guitar_strum_down", "Clean downstroke strum",         guitar_strum_down),
    ("guitar_strum_up",   "Clean upstroke strum",           guitar_strum_up),
    ("guitar_arp",        "Clean picked arpeggio up",       guitar_arp),
    ("guitar_arp_down",   "Clean arpeggio down",            guitar_arp_down),
]
