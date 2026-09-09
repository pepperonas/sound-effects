"""Perc — percussion one-shots for layering on top of a running beat.

The `drums` category is a kit you build a beat *from*. These go *over* one:
the shaker that gives a loop its swing, the clave that makes it Latin, the
woodblock that marks a bar. They are the shortest things in the pack, most
under 150 ms, because a percussion hit that outstays its welcome fights the
groove instead of decorating it.

Struck idiophones — block, clave, triangle, cowbell — are all the same recipe
with different numbers: two or three *inharmonic* partials, because a bar of
wood or metal free at both ends does not vibrate in a harmonic series. Getting
those ratios wrong is what makes a synthesised woodblock sound like a beep.
"""
import math
from synth import (sine, triangle, square, noise_burst, mix, silence, perc, ad,
                   ring_mod, lowpass, highpass, drive, normalize, Noise)
from ._music import additive

CATEGORY = "perc"
GROUP = "dj"
DESCRIPTION = "Percussion one-shots to layer over a beat: shakers, claves, blocks."


def _bar(f0, modes, dur, decay, click=0.25, seed=5, colour=2200.0):
    """A struck bar or block: inharmonic partials plus the stick."""
    parts = [(m, g, decay * r) for m, g, r in modes]
    s = additive(f0, dur, parts, attack=0.0008)
    mix(s, highpass(noise_burst(0.008, perc(300.0), 0.0, Noise(seed)), colour),
        0.0, click)
    return normalize(s, 0.85)


def _shake(dur, dec, seed, lo=5200.0, hi=11000.0, grains=0):
    """Many small things rattling: filtered noise, optionally in grains."""
    n = noise_burst(dur, perc(dec), 0.0, Noise(seed))
    n = lowpass(highpass(n, lo), hi)
    if grains:
        g = Noise(seed + 1)
        n = [x * (0.35 + 0.65 * abs(g())) if i % 12 == 0 else x
             for i, x in enumerate(n)]
    return normalize(n, 0.85)


def _drum(f, dur, dec, bend=1.0, body=1.0, skin=0.35, seed=9):
    """A hand drum: a membrane, so the pitch drops as the skin relaxes."""
    s = sine(lambda t: f * (1 + bend * math.exp(-30.0 * t)), dur, perc(dec))
    mix(s, triangle(f * 2.4, dur * 0.4, perc(dec * 2.2)), 0.0, 0.18 * body)
    mix(s, highpass(noise_burst(0.012, perc(160.0), 0.0, Noise(seed)), 1800),
        0.0, skin)
    return normalize(drive(s, 1.3), 0.85)


# --------------------------------------------------------------------------- #
# Shakers and rattles.
# --------------------------------------------------------------------------- #
def perc_shaker():
    """Shaker — one forward stroke, the swing engine of a loop."""
    return _shake(0.09, 55.0, 71)


def perc_shaker_back():
    """Back stroke — softer and shorter, the answer to the forward one."""
    return _shake(0.06, 80.0, 73)


def perc_cabasa():
    """Cabasa — steel beads on a cylinder, grainier and drier than a shaker."""
    return _shake(0.11, 46.0, 77, lo=3800.0, hi=9000.0, grains=1)


def perc_tambourine():
    """Tambourine — the jingles keep ringing after the skin is struck."""
    s = _shake(0.34, 11.0, 79, lo=5800.0, hi=13000.0)
    return normalize(ring_mod(s, 6100.0, depth=0.28), 0.85)


def perc_tamb_hit():
    """Tambourine struck with the hand — a thud under the jingle."""
    s = silence(0.30)
    mix(s, _shake(0.28, 13.0, 83, lo=5800.0, hi=13000.0), 0.0, 0.85)
    mix(s, sine(230.0, 0.06, perc(40.0)), 0.0, 0.35)
    return normalize(s, 0.85)


def perc_guiro():
    """Guiro — the stick dragged across the ridges, one scrape per notch."""
    out = silence(0.36)
    t, gap = 0.0, 0.030
    for k in range(11):
        mix(out, _shake(0.030, 120.0, 91 + k, lo=2600.0, hi=8000.0), t,
            0.5 + 0.04 * k)
        t += gap
        gap = max(0.020, gap * 0.96)
    return normalize(out, 0.85)


# --------------------------------------------------------------------------- #
# Struck wood and metal — inharmonic partials, not a harmonic series.
# --------------------------------------------------------------------------- #
def perc_woodblock():
    """Woodblock — a hollow box, dry and pitched, gone in 90 ms."""
    return _bar(880.0, [(1.0, 1.0, 1.0), (2.7, 0.42, 1.7), (5.1, 0.16, 2.6)],
                0.13, 42.0, click=0.32, seed=101)


def perc_woodblock_low():
    """Low woodblock — the bigger box, a fifth down."""
    return _bar(586.0, [(1.0, 1.0, 1.0), (2.7, 0.40, 1.7), (5.1, 0.14, 2.6)],
                0.16, 34.0, click=0.30, seed=103)


def perc_clave():
    """Clave — two hardwood sticks, almost pure pitch and very loud."""
    return _bar(1230.0, [(1.0, 1.0, 1.0), (3.4, 0.22, 2.2)],
                0.14, 30.0, click=0.22, seed=107, colour=3500.0)


def perc_stick():
    """Stick click — the count-in, wood on wood with no tone at all."""
    s = highpass(noise_burst(0.020, perc(200.0), 0.0, Noise(109)), 2600)
    mix(s, triangle(1900.0, 0.010, perc(220.0)), 0.0, 0.35)
    return normalize(s, 0.85)


def perc_rim():
    """Rim click — the stick on the hoop, thin and papery."""
    s = _bar(1650.0, [(1.0, 1.0, 1.0), (2.4, 0.35, 1.9)], 0.09, 60.0,
             click=0.45, seed=113, colour=3000.0)
    return normalize(highpass(s, 500.0), 0.85)


def perc_cowbell():
    """Cowbell — two square waves a tritone-ish apart, the 808 recipe."""
    d = 0.30
    s = square(587.0, d, perc(14.0))
    mix(s, square(845.0, d, perc(14.0)), 0.0, 0.9)
    return normalize(lowpass(highpass(s, 480.0), 5200.0), 0.85)


def perc_triangle():
    """Triangle — a bent metal rod: no fundamental you can name, rings for ever."""
    return _bar(2400.0, [(1.0, 1.0, 1.0), (2.13, 0.7, 1.15), (3.61, 0.5, 1.4),
                         (5.43, 0.3, 1.8)], 1.10, 3.0, click=0.10, seed=127,
                colour=6000.0)


def perc_agogo():
    """Agogo — the higher of the two bells, bright and clanging."""
    return _bar(1050.0, [(1.0, 1.0, 1.0), (2.76, 0.55, 1.3), (5.4, 0.25, 1.9)],
                0.34, 12.0, click=0.28, seed=131, colour=4000.0)


# --------------------------------------------------------------------------- #
# Hand drums.
# --------------------------------------------------------------------------- #
def perc_conga_hi():
    """Conga, open high tone — struck near the rim, the skin rings."""
    return _drum(310.0, 0.30, 11.0, bend=0.55, seed=141)


def perc_conga_lo():
    """Conga, low tone — the bigger drum, more chest."""
    return _drum(190.0, 0.38, 8.5, bend=0.65, seed=143)


def perc_conga_slap():
    """Conga slap — the flat hand: all crack, almost no pitch."""
    s = _drum(360.0, 0.16, 26.0, bend=0.4, body=0.4, skin=1.1, seed=147)
    return normalize(highpass(s, 260.0), 0.85)


def perc_bongo():
    """Bongo — small, high and tight, the drum that sits on top of everything."""
    return _drum(520.0, 0.18, 22.0, bend=0.5, body=0.7, seed=151)


def perc_djembe():
    """Djembe bass tone — the palm in the middle of the skin."""
    return _drum(105.0, 0.44, 7.0, bend=0.8, body=1.2, skin=0.22, seed=157)


def perc_timbale():
    """Timbale — a metal shell, so the tone is bright and the rim rings."""
    s = _drum(430.0, 0.26, 15.0, bend=0.35, body=0.5, skin=0.55, seed=163)
    mix(s, _bar(1400.0, [(1.0, 1.0, 1.0), (2.6, 0.3, 1.8)], 0.12, 45.0,
                click=0.0, seed=167), 0.0, 0.25)
    return normalize(s, 0.85)


SOUNDS = [
    ("perc_shaker",       "Forward shaker stroke",        perc_shaker),
    ("perc_shaker_back",  "Softer back stroke",           perc_shaker_back),
    ("perc_cabasa",       "Grainy steel-bead cabasa",     perc_cabasa),
    ("perc_tambourine",   "Ringing tambourine jingles",   perc_tambourine),
    ("perc_tamb_hit",     "Tambourine struck by hand",    perc_tamb_hit),
    ("perc_guiro",        "Scraped guiro, notch by notch", perc_guiro),
    ("perc_woodblock",    "Dry hollow woodblock",         perc_woodblock),
    ("perc_woodblock_low", "Lower, bigger woodblock",     perc_woodblock_low),
    ("perc_clave",        "Hardwood clave, loud and pitched", perc_clave),
    ("perc_stick",        "Wood-on-wood count-in click",  perc_stick),
    ("perc_rim",          "Thin papery rim click",        perc_rim),
    ("perc_cowbell",      "Two-square 808 cowbell",       perc_cowbell),
    ("perc_triangle",     "Long-ringing triangle",        perc_triangle),
    ("perc_agogo",        "Bright clanging agogo bell",   perc_agogo),
    ("perc_conga_hi",     "High open conga tone",         perc_conga_hi),
    ("perc_conga_lo",     "Low conga tone",               perc_conga_lo),
    ("perc_conga_slap",   "Flat-hand conga slap",         perc_conga_slap),
    ("perc_bongo",        "Tight high bongo",             perc_bongo),
    ("perc_djembe",       "Djembe bass tone",             perc_djembe),
    ("perc_timbale",      "Metal-shell timbale",          perc_timbale),
]
