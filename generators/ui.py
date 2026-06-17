"""General UI motion — open, close, hover, swipe, expand, pop."""
import math
from synth import sine, noise_burst, mix, silence, perc, ad, bell, Noise

CATEGORY = "ui"
GROUP = "interface"
DESCRIPTION = "Open, close, hover, swipe, expand and popover motion."


def open_panel():
    """Open — rising airy swish into a soft tone."""
    s = silence(0.35)
    n = Noise()
    mix(s, noise_burst(0.15, bell(0.15), 0.6, n), 0.0, 0.4)
    mix(s, sine(lambda t: 500 + 400 * t / 0.2, 0.2, ad(0.01, 0.12)), 0.05, 0.4)
    return s


def close_panel():
    """Close — falling swish into a low tap."""
    s = silence(0.32)
    n = Noise()
    mix(s, noise_burst(0.13, bell(0.13), 0.7, n), 0.0, 0.35)
    mix(s, sine(lambda t: 600 - 300 * t / 0.18, 0.18, ad(0.005, 0.1)), 0.04, 0.4)
    return s


def hover_tick():
    """Hover — very subtle high tick."""
    return sine(2400, 0.018, perc(220))


def swipe_whoosh():
    """Swipe — quick filtered-noise whoosh."""
    n = Noise()
    return noise_burst(0.22, bell(0.22), 0.55, n)


def expand():
    """Expand/grow — short upward glide."""
    return sine(lambda t: 440 + 660 * (1 - math.exp(-30 * t)), 0.18, ad(0.005, 0.12))


def collapse():
    """Collapse/shrink — short downward glide."""
    return sine(lambda t: 1100 - 660 * (1 - math.exp(-30 * t)), 0.18, ad(0.005, 0.12))


def popup():
    """Popover appear — quick bouncy pop."""
    f = lambda t: 600 + 500 * (1 - math.exp(-70 * t))
    s = sine(f, 0.16, perc(20))
    mix(s, sine(lambda t: 2 * f(t), 0.16, perc(28)), 0.0, 0.2)
    return s


def dismiss():
    """Dismiss/back — soft descending blip."""
    return sine(lambda t: 900 * math.exp(-3 * t) + 200, 0.14, perc(18))


SOUNDS = [
    ("open",          "Rising airy open swish",       open_panel),
    ("close",         "Falling close swish",          close_panel),
    ("hover",         "Subtle high hover tick",       hover_tick),
    ("swipe",         "Quick noise whoosh",           swipe_whoosh),
    ("expand",        "Short upward expand glide",    expand),
    ("collapse",      "Short downward collapse",      collapse),
    ("popup",         "Bouncy popover pop",           popup),
    ("dismiss",       "Soft descending dismiss",      dismiss),
]
