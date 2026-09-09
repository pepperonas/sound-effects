"""Vox — shouts and vocal chops: hey, ho, yeah, crowd, chants.

Built the way a voice is actually built, not sampled: the vocal tract is a
tube whose resonances sit at fixed frequencies, and a vowel *is* its formant
pattern. A word is therefore a path between formant targets — "hey" is the
tract moving from an open eh towards a closed ih while the pitch falls, and
"ho" is a burst of breath into a rounded oh.

That is why these are more than tone with a filter on it: the consonant is
noise shaped by the same tract as the vowel that follows it, and the vowel
moves. A static formant sounds like a synthesiser saying "aaah"; a moving one
sounds like somebody shouting.

Nobody will mistake them for a recording of a person. They are shouts in the
same sense the brass kit is brass: deliberately synthetic, and useful.
"""
import math
from synth import (noise_burst, mix, silence, adsr, perc, lowpass, highpass,
                   drive, normalize, note, Noise)
from ._music import additive

CATEGORY = "vox"
GROUP = "dj"
DESCRIPTION = "Synthetic vocal shouts and chops: hey, ho, yeah, chants, crowd."

# (centre Hz, strength, bandwidth) — the tract shape for each vowel.
VOWELS = {
    "ah": ((730, 1.00, 130), (1090, 0.50, 170), (2440, 0.22, 240)),
    "eh": ((530, 1.00, 110), (1840, 0.52, 190), (2480, 0.28, 240)),
    "ih": ((390, 1.00, 100), (1990, 0.42, 200), (2550, 0.22, 240)),
    "oh": ((570, 1.00, 110), (840, 0.55, 150), (2410, 0.11, 220)),
    "oo": ((300, 1.00, 90), (870, 0.26, 130), (2240, 0.08, 200)),
    "uh": ((640, 1.00, 120), (1190, 0.45, 170), (2390, 0.16, 230)),
}


def _tight(xs):
    """Top-and-tail: trim the dead head so the sample triggers on the beat.

    A shout begins with breath and a riser begins at zero; on a deck that
    silence is latency you cannot compensate, so it comes off. The shape is
    unchanged, the sample simply starts where it becomes audible.
    """
    lead = next((i for i, x in enumerate(xs) if abs(x) > 0.002), 0)
    return xs[lead:] if lead else xs


def _blend(a, b, x):
    """Interpolate between two tract shapes — the tongue actually moving."""
    return tuple((fa + (fb - fa) * x, aa + (ab - aa) * x, ba + (bb - ba) * x)
                 for (fa, aa, ba), (fb, ab, bb) in zip(VOWELS[a], VOWELS[b]))


def _gains(f0, shape):
    out = []
    for k in range(1, 26):
        f = k * f0
        if f > 3600.0:
            break
        g = sum(a * math.exp(-((f - fc) / bw) ** 2) for fc, a, bw in shape)
        g /= 1.0 + 0.26 * (k - 1)
        if g > 0.004:
            out.append((k, g, 0.0))
    return out or [(1, 1.0, 0.0)]


def _shout(pitch, dur, vowel="eh", to=None, bend=-2.0, rasp=0.35, breath=0.9,
           attack=0.014, rel=0.10, voices=2, seed=5):
    """One shouted syllable.

    `to` moves the tract towards a second vowel across the sound; `bend` is
    how many semitones the pitch falls, which is what makes it a shout rather
    than a sung note — people do not hold pitch when they yell.
    """
    f0 = note(pitch) if isinstance(pitch, str) else float(pitch)
    n = dur + rel
    # People do not hold a shout level: it is loudest the instant it leaves
    # and falls away. Without the overall decay the later tract segments beat
    # the front (measured: "hey" peaked 210 ms in, far too late to trigger on).
    gate = adsr(attack, dur * 0.30, 0.62, rel, n)
    env = lambda t: gate(t) * math.exp(-3.6 * t)
    out = silence(n)
    # The vowel is rendered in short segments so the tract can move through it.
    segs = 6 if to else 1
    for i in range(segs):
        x = i / max(1, segs - 1) if segs > 1 else 0.0
        shape = _blend(vowel, to, x) if to else VOWELS[vowel]
        seg_dur = n / segs + (0.012 if segs > 1 else 0.0)
        for v in range(voices):
            det = 1.0 + (0.004 * (v - 0.5) * 2)
            f = f0 * det * 2 ** (bend * (i / segs) / 12.0)
            s = additive(f, seg_dur, _gains(f, shape), attack=0.003,
                         vib=(6.0, 0.004))
            mix(out, s, i * n / segs, 0.55 / voices)
    out = [x * env(i / 44100.0) for i, x in enumerate(out)]
    if breath:                                     # air past the folds
        mix(out, lowpass(highpass(noise_burst(n, env, 0.0, Noise(seed)), 900), 3400),
            0.0, 0.075 * breath)
    if rasp:                                       # the throat under strain
        out = drive(out, 1.0 + 2.6 * rasp)
    return _tight(highpass(normalize(out, 0.8), 90.0))


def _consonant(kind, seed=11):
    """The noise burst in front of a vowel. /h/ is breath, /y/ is a soft rise."""
    if kind == "h":
        return lowpass(highpass(noise_burst(0.045, perc(38.0), 0.0, Noise(seed)),
                                800), 4200)
    if kind == "t":
        return highpass(noise_burst(0.020, perc(140.0), 0.0, Noise(seed)), 3000)
    return lowpass(noise_burst(0.030, perc(55.0), 0.0, Noise(seed)), 1800)


def _word(cons, body, lead=0.030, cgain=0.30):
    out = silence(len(body) / 44100.0 + lead)
    mix(out, _consonant(cons), 0.0, cgain)
    mix(out, body, lead, 1.0)
    return _tight(normalize(out, 0.85))


# --------------------------------------------------------------------------- #
# Shouts.
# --------------------------------------------------------------------------- #
def vox_hey():
    """"Hey" — breath, then the tract closing from eh to ih as the pitch drops."""
    return _word("h", _shout("A3", 0.24, "eh", to="ih", bend=-2.5))


def vox_hey_high():
    """"Hey" up an octave — thinner, more urgent."""
    return _word("h", _shout("A4", 0.20, "eh", to="ih", bend=-3.0, rasp=0.45))


def vox_ho():
    """"Ho" — the same breath into a rounded oh, heavier."""
    return _word("h", _shout("F3", 0.26, "oh", to="oo", bend=-2.0, rasp=0.30))


def vox_yeah():
    """"Yeah" — a soft glide into eh, opening towards ah."""
    return _word("y", _shout("G3", 0.30, "eh", to="ah", bend=-2.5), cgain=0.22)


def vox_uh():
    """"Uh" — a short grunt, no consonant, all body."""
    return _shout("E3", 0.16, "uh", bend=-1.5, rasp=0.5, attack=0.008)


def vox_ah():
    """"Ah" — one open shout, held a little longer."""
    return _shout("A3", 0.34, "ah", bend=-1.8)


def vox_oh():
    """"Oh" — rounded and surprised, falling away."""
    return _shout("F3", 0.30, "oh", bend=-3.0)


def vox_ay():
    """"Ay" — the call across a room: bright, and it bends up before it falls."""
    body = _shout("A3", 0.28, "ah", to="ih", bend=-4.0, rasp=0.45)
    return _tight(normalize(body, 0.85))


def vox_woo():
    """"Woo" — the crowd noise: oo held and sliding up."""
    return _shout("D4", 0.40, "oo", to="oh", bend=+3.0, rasp=0.2, breath=1.4)


def vox_hut():
    """"Hut" — clipped, consonant at both ends, a drill-call."""
    body = _shout("G3", 0.13, "uh", bend=-1.0, rasp=0.5, attack=0.006, rel=0.05)
    out = _word("h", body)
    mix(out, _consonant("t", seed=19), len(out) / 44100.0 - 0.03, 0.30)
    return normalize(out, 0.85)


# --------------------------------------------------------------------------- #
# Chops — vowels treated as instruments.
# --------------------------------------------------------------------------- #
def vox_chop_ah():
    """Chop — a 120 ms slice of "ah", the house-record vocal stab."""
    return _shout("C4", 0.12, "ah", bend=0.0, rasp=0.15, attack=0.006, rel=0.05)


def vox_chop_oo():
    """Chop — the same slice on a rounded oo, darker."""
    return _shout("C4", 0.12, "oo", bend=0.0, rasp=0.15, attack=0.006, rel=0.05)


def vox_chop_eh():
    """Chop — a bright eh slice, cuts through a busy mix."""
    return _shout("C4", 0.12, "eh", bend=0.0, rasp=0.2, attack=0.006, rel=0.05)


def vox_chop_low():
    """Low chop — an octave down, more chest than air."""
    return _shout("C3", 0.16, "oh", bend=0.0, rasp=0.2, attack=0.006, rel=0.06)


def vox_chop_3():
    """Three chops — the same syllable stuttered, a built-in fill."""
    one = _shout("C4", 0.09, "ah", bend=0.0, rasp=0.2, attack=0.005, rel=0.04)
    out = list(one)
    mix(out, one, 0.13, 0.9)
    mix(out, one, 0.26, 0.95)
    return _tight(normalize(out, 0.85))


def vox_rise():
    """Rising chop — one vowel bent up a fourth, a mini lift."""
    return _shout("A3", 0.34, "oo", to="ah", bend=+5.0, rasp=0.2)


# --------------------------------------------------------------------------- #
# Groups.
# --------------------------------------------------------------------------- #
def _crowd(pitches, dur, vowel="ah", spread=0.035, rasp=0.3):
    out = silence(dur + 0.4)
    for i, p in enumerate(pitches):
        mix(out, _shout(p, dur, vowel, bend=-1.2, rasp=rasp, voices=2,
                        seed=7 + 5 * i), i * spread, 0.7)
    return _tight(normalize(out, 0.85))


def vox_crowd():
    """Crowd — several voices on the same shout, none of them together."""
    return _crowd(("G3", "A3", "C4", "D4"), 0.34)


def vox_crowd_low():
    """Crowd, low — a room of men, chest-deep."""
    return _crowd(("E2", "G2", "A2", "C3"), 0.40, vowel="oh", rasp=0.2)


def vox_chant():
    """Chant — two shouts on the beat, a terrace call."""
    one = _shout("A3", 0.20, "oh", bend=-1.5, rasp=0.35)
    out = list(one)
    mix(out, one, 0.30, 0.95)
    return _tight(normalize(out, 0.85))


def vox_chant_3():
    """Three-note chant — the pitch rising each time, a call to attention."""
    out = silence(0.9)
    for i, p in enumerate(("F3", "G3", "Bb3")):
        mix(out, _shout(p, 0.16, "oh", bend=-1.0, rasp=0.35), i * 0.22, 0.95)
    return _tight(normalize(out, 0.85))


SOUNDS = [
    ("vox_hey",       "Shouted 'hey', eh to ih",        vox_hey),
    ("vox_hey_high",  "High urgent 'hey'",              vox_hey_high),
    ("vox_ho",        "Heavy rounded 'ho'",             vox_ho),
    ("vox_yeah",      "Glided 'yeah', eh to ah",        vox_yeah),
    ("vox_uh",        "Short grunted 'uh'",             vox_uh),
    ("vox_ah",        "Open held 'ah' shout",           vox_ah),
    ("vox_oh",        "Falling rounded 'oh'",           vox_oh),
    ("vox_ay",        "Bright calling 'ay'",            vox_ay),
    ("vox_woo",       "Rising crowd 'woo'",             vox_woo),
    ("vox_hut",       "Clipped drill-call 'hut'",       vox_hut),
    ("vox_chop_ah",   "120 ms 'ah' vocal chop",         vox_chop_ah),
    ("vox_chop_oo",   "Dark 'oo' chop",                 vox_chop_oo),
    ("vox_chop_eh",   "Bright 'eh' chop",               vox_chop_eh),
    ("vox_chop_low",  "Low chesty chop",                vox_chop_low),
    ("vox_chop_3",    "Stuttered triple chop",          vox_chop_3),
    ("vox_rise",      "Vowel bent up a fourth",         vox_rise),
    ("vox_crowd",     "Four staggered voices",          vox_crowd),
    ("vox_crowd_low", "Low room of voices",             vox_crowd_low),
    ("vox_chant",     "Two-shout terrace chant",        vox_chant),
    ("vox_chant_3",   "Rising three-note chant",        vox_chant_3),
]
