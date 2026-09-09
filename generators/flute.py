"""Flute — solo woodwind: phrases, trills, runs and grace notes.

The easiest orchestral instrument to synthesise honestly, because a flute
really is close to a sine wave: an edge tone splitting a stream of air across
a hole. Almost all the energy is in the fundamental, the second harmonic sits
far below it, and above that there is very little.

What makes it a flute and not a sine oscillator is the air. Breath noise runs
underneath the whole note, and every tongued attack begins with a "chiff" — a
burst of turbulence before the tube settles into oscillation. Take those two
away and you have a test tone; leave them in and the ear hears a player.

The vibrato is delayed rather than constant: a flautist leans into a held note
after it has spoken, so the wobble fades in instead of being there at the
attack.
"""
import math
from synth import noise_burst, mix, adsr, perc, lowpass, highpass, note, Noise
from ._music import motif, additive

CATEGORY = "flute"
GROUP = "music"
DESCRIPTION = "Solo flute: phrases, trills, runs, grace notes and flutter-tongue."

# A flute's harmonic recipe: fundamental, a distant second, almost nothing else.
HARM = [(1.0, 1.00, 0.0), (2.0, 0.16, 0.0), (3.0, 0.055, 0.0), (4.0, 0.018, 0.0)]


def _flute(pitch, dur, v=1.0, air=1.0, chiff=1.0, vib=0.008, attack=0.045,
           rel=0.10, bright=1.0):
    """One blown note. `air` is breath noise, `chiff` the turbulent onset."""
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + rel
    env = adsr(attack, 0.06, 0.9, rel, n)
    parts = [(m, g * (bright ** i), r) for i, (m, g, r) in enumerate(HARM)]
    # Vibrato only after the note has spoken — a player leans into it.
    s = additive(f0, n, parts, attack=0.004, vib=(5.0, vib))
    s = [x * env(i / 44100.0) for i, x in enumerate(s)]
    if air:                                        # breath running under the tone
        mix(s, lowpass(highpass(noise_burst(n, env, 0.0, Noise(int(f0) | 11)), 1400),
                       6500), 0.0, 0.075 * air)
    if chiff:                                      # turbulence before it speaks
        mix(s, highpass(noise_burst(0.045, perc(55), 0.0, Noise(int(f0) | 13)), 2000),
            0.0, 0.16 * chiff * v)
    return [x * (0.4 + 0.6 * v) for x in s]


def _play(steps, tone=8000.0, **kw):
    return highpass(lowpass(motif(_flute, steps, **kw), tone), 120.0)


def _flutter(s, rate=27.0, depth=0.55):
    """Flutter-tongue — the player rolling an R into the mouthpiece."""
    return [x * (1.0 - depth * 0.5 * (1.0 - math.cos(2 * math.pi * rate * i / 44100)))
            for i, x in enumerate(s)]


# --------------------------------------------------------------------------- #
# Single notes and registers.
# --------------------------------------------------------------------------- #
def flute_note():
    """Single note — C5, normally tongued, the reference tone."""
    return _play([(0, "C5", 8, 0.9)])


def flute_soft():
    """Softly blown — quieter, and proportionally far more air."""
    return _play([(0, "C5", 8, 0.45, {"air": 1.8, "chiff": 0.4, "bright": 0.75})])


def flute_low():
    """Low register — C4, where a flute is breathy and thick."""
    return _play([(0, "C4", 8, 0.9, {"air": 1.9, "bright": 1.15})])


def flute_high():
    """High register — C6, pure and piercing, hardly any air left."""
    return _play([(0, "C6", 7, 0.9, {"air": 0.4, "bright": 0.7})])


def flute_chiff():
    """Hard tongued — the attack turbulence exaggerated, a spitting start."""
    return _play([(0, "C5", 6, 1.0, {"chiff": 2.6, "attack": 0.018})])


def flute_breathy():
    """Breathy — deliberately under-blown, more air than tone."""
    return _play([(0, "G4", 8, 0.6, {"air": 3.2, "chiff": 1.4, "bright": 0.8})])


def flute_vib():
    """Held note with a wide vibrato that grows as it is sustained."""
    return _play([(0, "G5", 14, 0.9, {"vib": 0.016})])


def flute_straight():
    """Straight tone — no vibrato at all, cold and flat."""
    return _play([(0, "C5", 10, 0.85, {"vib": 0.0})])


# --------------------------------------------------------------------------- #
# Ornaments.
# --------------------------------------------------------------------------- #
def flute_trill():
    """Trill — two notes a tone apart alternating fast, ending on the lower."""
    seq = ("C5", "D5") * 5 + ("C5",)
    return _play([(i, p, 1 if i < 10 else 6, 0.85, {"chiff": 0.25, "attack": 0.012})
                  for i, p in enumerate(seq)])


def flute_trill_half():
    """Half-tone trill — tighter and more anxious than the whole-tone one."""
    seq = ("C5", "Db5") * 5 + ("C5",)
    return _play([(i, p, 1 if i < 10 else 6, 0.85, {"chiff": 0.25, "attack": 0.012})
                  for i, p in enumerate(seq)])


def flute_mordent():
    """Mordent — a single flick to the note above and straight back."""
    return _play([(0, "C5", 1, 0.9, {"attack": 0.012}),
                  (0.7, "D5", 1, 0.85, {"chiff": 0.3, "attack": 0.010}),
                  (1.4, "C5", 8, 0.95, {"chiff": 0.3, "attack": 0.012})])


def flute_grace():
    """Grace note — a note crushed onto the front of the main one."""
    return _play([(0, "Bb4", 1, 0.7, {"attack": 0.010, "chiff": 0.5}),
                  (0.8, "C5", 9, 1.0, {"attack": 0.014})])


def flute_turn():
    """Turn — above, home, below, home: the standard four-note ornament."""
    return _play([(0, "D5", 1, 0.85, {"attack": 0.012}),
                  (1, "C5", 1, 0.85, {"attack": 0.012}),
                  (2, "B4", 1, 0.85, {"attack": 0.012}),
                  (3, "C5", 8, 0.95, {"attack": 0.014})])


def flute_flutter():
    """Flutter-tongue — a rolled R against the tone, breathy and rattling."""
    return _flutter(_play([(0, "C5", 12, 0.9, {"air": 1.5})]))


# --------------------------------------------------------------------------- #
# Runs and arpeggios.
# --------------------------------------------------------------------------- #
def flute_run_up():
    """Run up — the C minor scale, eight quick tongued notes."""
    seq = ("C5", "D5", "Eb5", "F5", "G5", "Ab5", "Bb5", "C6")
    return _play([(i, p, 1 if i < 7 else 6, 0.8 + 0.02 * i,
                   {"attack": 0.014, "chiff": 0.5}) for i, p in enumerate(seq)])


def flute_run_down():
    """Run down — the same scale falling back to the root."""
    seq = ("C6", "Bb5", "Ab5", "G5", "F5", "Eb5", "D5", "C5")
    return _play([(i, p, 1 if i < 7 else 6, 0.9, {"attack": 0.014, "chiff": 0.5})
                  for i, p in enumerate(seq)])


def flute_arp_up():
    """Arpeggio up — the minor triad across an octave and a half."""
    return _play([(i, p, 1 if i < 5 else 6, 0.85, {"attack": 0.016}) for i, p in
                  enumerate(("C5", "Eb5", "G5", "C6", "Eb6", "G6"))])


def flute_arp_down():
    """Arpeggio down — the same shape falling."""
    return _play([(i, p, 1 if i < 5 else 6, 0.9, {"attack": 0.016}) for i, p in
                  enumerate(("G6", "Eb6", "C6", "G5", "Eb5", "C5"))])


def flute_chromatic():
    """Chromatic run — six semitones climbing, restless."""
    seq = ("C5", "Db5", "D5", "Eb5", "E5", "F5")
    return _play([(i, p, 1 if i < 5 else 6, 0.85, {"attack": 0.014})
                  for i, p in enumerate(seq)])


def flute_octave():
    """Octave leap — the flute's easiest and most dramatic jump."""
    return _play([(0, "C5", 3, 0.85), (3, "C6", 9, 1.0, {"chiff": 1.4})])


def flute_staccato():
    """Staccato — four short tongued notes, dry and separated."""
    return _play([(i * 2, p, 1, 0.9, {"attack": 0.010, "rel": 0.06, "chiff": 1.3})
                  for i, p in enumerate(("C5", "Eb5", "G5", "C6"))])


# --------------------------------------------------------------------------- #
# Phrases.
# --------------------------------------------------------------------------- #
def flute_call():
    """Question — rising to the fifth and hanging there."""
    return _play([(0, "C5", 2, 0.85), (2, "Eb5", 1, 0.8, {"chiff": 0.5}),
                  (3, "F5", 1, 0.85, {"chiff": 0.5}), (4, "G5", 8, 0.95)])


def flute_answer():
    """Answer — the phrase settling back onto the root."""
    return _play([(0, "G5", 2, 0.9), (2, "F5", 1, 0.8, {"chiff": 0.5}),
                  (3, "Eb5", 1, 0.85, {"chiff": 0.5}), (4, "C5", 9, 0.95)])


def flute_phrase():
    """Melodic phrase — a complete little tune with a breath at the end."""
    return _play([(0, "G4", 2, 0.8), (2, "C5", 2, 0.9), (4, "Eb5", 2, 0.9),
                  (6, "D5", 1, 0.85, {"chiff": 0.5}), (7, "C5", 9, 0.95)])


def flute_sigh():
    """Sigh — a note falling a tone and fading away, the wistful gesture."""
    return _play([(0, "Eb5", 4, 0.9), (4, "C5", 10, 0.6, {"chiff": 0.3, "air": 1.6})])


SOUNDS = [
    ("flute_note",       "Normally tongued note",        flute_note),
    ("flute_soft",       "Softly blown, airy",           flute_soft),
    ("flute_low",        "Breathy low register",         flute_low),
    ("flute_high",       "Pure piercing high note",      flute_high),
    ("flute_chiff",      "Hard spitting attack",         flute_chiff),
    ("flute_breathy",    "Under-blown, air-heavy",       flute_breathy),
    ("flute_vib",        "Held note, growing vibrato",   flute_vib),
    ("flute_straight",   "Straight tone, no vibrato",    flute_straight),
    ("flute_trill",      "Whole-tone trill",             flute_trill),
    ("flute_trill_half", "Half-tone trill",              flute_trill_half),
    ("flute_mordent",    "Single mordent flick",         flute_mordent),
    ("flute_grace",      "Grace note into the main note", flute_grace),
    ("flute_turn",       "Four-note turn ornament",      flute_turn),
    ("flute_flutter",    "Flutter-tongue rattle",        flute_flutter),
    ("flute_run_up",     "Ascending minor scale run",    flute_run_up),
    ("flute_run_down",   "Descending scale run",         flute_run_down),
    ("flute_arp_up",     "Minor arpeggio up",            flute_arp_up),
    ("flute_arp_down",   "Minor arpeggio down",          flute_arp_down),
    ("flute_chromatic",  "Restless chromatic climb",     flute_chromatic),
    ("flute_octave",     "Dramatic octave leap",         flute_octave),
    ("flute_staccato",   "Four dry staccato notes",      flute_staccato),
    ("flute_call",       "Rising question phrase",       flute_call),
    ("flute_answer",     "Falling answer phrase",        flute_answer),
    ("flute_phrase",     "Complete melodic phrase",      flute_phrase),
    ("flute_sigh",       "Falling, fading sigh",         flute_sigh),
]
