"""Drum kit — kicks, snares, claps, hats, toms, cymbals and percussion.

The building blocks of a beat, the way Fruity Loops / FL Studio ships a kit:
punchy kicks, snappy snares, crisp hats and a handful of percs. Each is a
one-shot you can drop straight onto a step sequencer.
"""
import math
from synth import (sine, triangle, square, noise_burst, mix, silence,
                   perc, ad, ring_mod, lowpass, highpass, drive, Noise)

CATEGORY = "drums"
GROUP = "music"
DESCRIPTION = "Kicks, snares, claps, hats, toms, cymbals and percussion one-shots."


def kick():
    """Punchy kick — pitch-dropping sine body with a click transient."""
    s = silence(0.4)
    body = sine(lambda t: 48 + 120 * math.exp(-32 * t), 0.4, perc(8))
    mix(s, body, 0.0, 1.0)
    mix(s, noise_burst(0.004, perc(280), 0.0), 0.0, 0.35)   # beater click
    mix(s, triangle(180, 0.02, perc(120)), 0.0, 0.3)        # attack snap
    return drive(s, 1.6)


def kick_808():
    """808 kick — long boomy sub with a glide, the trap/hip-hop staple."""
    s = silence(0.8)
    body = sine(lambda t: 42 + 90 * math.exp(-45 * t), 0.8, perc(3.2))
    mix(s, body, 0.0, 1.0)
    mix(s, noise_burst(0.003, perc(320), 0.0), 0.0, 0.25)
    return drive(s, 2.2)


def kick_sub():
    """Deep sub kick — clean, almost click-less, for layering under a punch."""
    return sine(lambda t: 38 + 70 * math.exp(-28 * t), 0.5, perc(6))


def snare():
    """Snare — tonal shell plus a bright high-passed noise crack."""
    s = silence(0.3)
    mix(s, sine(180, 0.16, perc(20)), 0.0, 0.5)
    mix(s, triangle(330, 0.12, perc(26)), 0.0, 0.3)
    body = highpass(noise_burst(0.2, perc(17), 0.0, Noise(7)), 1400)
    mix(s, body, 0.0, 0.85)
    return s


def snare_rim():
    """Tight rimshot snare — short, woody, cutting."""
    s = silence(0.16)
    mix(s, triangle(420, 0.06, perc(60)), 0.0, 0.6)
    mix(s, highpass(noise_burst(0.05, perc(70), 0.0), 2200), 0.0, 0.5)
    mix(s, square(1700, 0.008, perc(200)), 0.0, 0.25)
    return s


def clap():
    """Hand clap — staggered noise bursts with a short diffuse tail."""
    s = silence(0.32)
    n = Noise(31)
    burst = lambda d, dec: highpass(noise_burst(d, perc(dec), 0.0, n), 1100)
    for off in (0.0, 0.011, 0.022, 0.033):
        mix(s, burst(0.05, 45), off, 0.5)
    mix(s, burst(0.2, 11), 0.035, 0.45)                      # room tail
    return s


def hat_closed():
    """Closed hi-hat — short metallic high-passed noise tick."""
    n = highpass(noise_burst(0.05, perc(120), 0.0, Noise(53)), 7000)
    return ring_mod(n, 8200, depth=0.25)


def hat_open():
    """Open hi-hat — same metallic noise with a long sizzling decay."""
    n = highpass(noise_burst(0.35, perc(11), 0.0, Noise(53)), 6500)
    return ring_mod(n, 8200, depth=0.25)


def tom_low():
    """Low tom — round pitch-dropping drum tone."""
    return _tom(150)


def tom_mid():
    """Mid tom."""
    return _tom(210)


def tom_high():
    """High tom."""
    return _tom(300)


def _tom(f0):
    s = sine(lambda t: f0 * (1 + 0.4 * math.exp(-26 * t)), 0.35, perc(9))
    mix(s, noise_burst(0.005, perc(200), 0.2), 0.0, 0.18)
    return drive(s, 1.3)


def crash():
    """Crash cymbal — bright wash of high-passed noise, slow decay."""
    n = highpass(noise_burst(1.4, perc(3.0), 0.0, Noise(97)), 4500)
    n = ring_mod(n, 5200, depth=0.2)
    mix(n, highpass(noise_burst(0.02, perc(120), 0.0, Noise(2)), 8000), 0.0, 0.6)
    return n


def ride():
    """Ride cymbal — tonal ping with a controlled shimmer."""
    s = silence(0.7)
    mix(s, highpass(noise_burst(0.6, perc(6), 0.0, Noise(13)), 5500), 0.0, 0.4)
    for f in (520, 1180, 1560):                              # bell partials
        mix(s, sine(f, 0.5, perc(7)), 0.0, 0.18)
    return s


def cowbell():
    """808 cowbell — two detuned squares, the classic 540/800 Hz ratio."""
    s = silence(0.4)
    env = perc(12)
    a = square(540, 0.4, env)
    b = square(800, 0.4, env)
    mix(s, a, 0.0, 0.4)
    mix(s, b, 0.0, 0.4)
    return lowpass(s, 5000)


def shaker():
    """Shaker — soft burst of band-limited noise."""
    n = highpass(noise_burst(0.12, ad(0.01, 0.04), 0.0, Noise(71)), 5000)
    return lowpass(n, 11000)


def snap():
    """Finger snap — single sharp high-passed crack with a click."""
    s = highpass(noise_burst(0.08, perc(40), 0.0, Noise(5)), 1800)
    mix(s, sine(2400, 0.006, perc(160)), 0.0, 0.3)
    return s


def rimshot():
    """Rimshot click — ultra short woody tick for ghost notes."""
    s = triangle(560, 0.03, perc(120))
    mix(s, highpass(noise_burst(0.02, perc(160), 0.0), 3000), 0.0, 0.4)
    return s


SOUNDS = [
    ("kick",       "Punchy kick with click transient",   kick),
    ("kick_808",   "Long boomy 808 sub kick",            kick_808),
    ("kick_sub",   "Clean deep sub kick for layering",   kick_sub),
    ("snare",      "Tonal snare with bright crack",      snare),
    ("snare_rim",  "Tight cutting rimshot snare",        snare_rim),
    ("clap",       "Staggered hand clap with tail",      clap),
    ("hat_closed", "Short metallic closed hi-hat",       hat_closed),
    ("hat_open",   "Sizzling open hi-hat",               hat_open),
    ("tom_low",    "Low round tom",                      tom_low),
    ("tom_mid",    "Mid tom",                            tom_mid),
    ("tom_high",   "High tom",                           tom_high),
    ("crash",      "Bright crash cymbal wash",           crash),
    ("ride",       "Tonal ride cymbal ping",             ride),
    ("cowbell",    "Classic 808 cowbell",                cowbell),
    ("shaker",     "Soft band-limited shaker",           shaker),
    ("snap",       "Sharp finger snap",                  snap),
    ("rimshot",    "Ultra-short woody rimshot",          rimshot),
]
