"""Clipboard operations — copy, cut, paste."""
import math
from synth import (sine, square, noise_burst, mix, silence, ring_mod,
                   perc, ad, bell, Noise)

CATEGORY = "clipboard"
GROUP = "interface"
DESCRIPTION = "Copy, cut and paste — the clipboard family."


def paste_default():
    """Layered click + pop-in + low thump. The signature paste sound."""
    s = silence(0.5)
    # tick
    mix(s, sine(2200, 0.012, perc(180)), 0.0, 0.35)
    mix(s, sine(3400, 0.012, perc(220)), 0.0, 0.18)
    # pop-in body, pitch glides up
    f = lambda t: 320 + 520 * (1 - math.exp(-40 * t))
    mix(s, sine(f, 0.12, ad(0.004, 0.05)), 0.04, 0.5)
    mix(s, sine(lambda t: 2 * f(t), 0.12, ad(0.004, 0.05)), 0.04, 0.2)
    # low thump
    mix(s, sine(lambda t: 150 * math.exp(-6 * t), 0.10, perc(22)), 0.045, 0.45)
    return s


def paste_bubble():
    """Soft bubble pop — friendly, water-droplet-ish."""
    f = lambda t: 420 + 900 * (1 - math.exp(-60 * t))
    s = sine(f, 0.45, perc(14))
    mix(s, sine(lambda t: 2 * f(t), 0.45, perc(22)), 0.0, 0.3)
    return s


def paste_mechkey():
    """Mechanical keyboard click — snappy two-stage clack."""
    s = silence(0.4)
    n = Noise()
    mix(s, noise_burst(0.01, perc(260), 0.0, n), 0.0, 0.5)
    mix(s, sine(1800, 0.01, perc(260)), 0.0, 0.5)
    mix(s, sine(lambda t: 320 * math.exp(-30 * t), 0.06, perc(45)), 0.018, 0.7)
    return s


def paste_scifi():
    """Sci-fi teleport-in — bright digital materialize."""
    f = lambda t: 200 + 5200 * t
    body = sine(f, 0.5, lambda t: (1 - math.exp(-40 * t)) * math.exp(-6 * t))
    body = ring_mod(body, 90, depth=0.4)
    return body


def copy_blip():
    """Copy — short, neutral, slightly rising confirmation blip."""
    f = lambda t: 700 + 260 * t / 0.18
    s = sine(f, 0.18, ad(0.003, 0.06))
    mix(s, sine(lambda t: 2 * f(t), 0.18, ad(0.003, 0.05)), 0.0, 0.25)
    return s


def cut_snip():
    """Cut — two quick scissor-like ticks."""
    s = silence(0.25)
    for off in (0.0, 0.05):
        mix(s, noise_burst(0.02, perc(160), 0.3), off, 0.5)
        mix(s, sine(2600, 0.02, perc(180)), off, 0.35)
    return s


SOUNDS = [
    ("paste",          "Layered click + pop-in + low thump",       paste_default),
    ("paste_bubble",   "Soft bubble pop, water-droplet-ish",        paste_bubble),
    ("paste_mechkey",  "Mechanical keyboard clack",                 paste_mechkey),
    ("paste_scifi",    "Sci-fi digital materialize",                paste_scifi),
    ("copy",           "Short rising confirmation blip",            copy_blip),
    ("cut",            "Two quick scissor-like ticks",              cut_snip),
]
