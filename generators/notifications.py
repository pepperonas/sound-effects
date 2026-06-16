"""Notifications and alerts — pings, chimes, message tones."""
import math
from synth import sine, triangle, mix, silence, perc, ad, adsr

CATEGORY = "notifications"
DESCRIPTION = "Pings, chimes, message and alert tones."


def ping_simple():
    """Single bright notification ping."""
    s = sine(1320, 0.3, perc(9))
    mix(s, sine(2640, 0.3, perc(16)), 0.0, 0.2)
    return s


def chime_two_note():
    """Pleasant two-note chime (C6 → G6)."""
    s = silence(0.5)
    mix(s, sine(1046.5, 0.35, perc(8)), 0.0, 0.7)
    mix(s, sine(1568.0, 0.4, perc(7)), 0.08, 0.7)
    return s


def chime_three_note():
    """Three-note ascending chime — classic 'you've got mail' feel."""
    s = silence(0.7)
    for i, f in enumerate((784.0, 988.0, 1318.5)):  # G5 B5 E6
        mix(s, sine(f, 0.4, perc(7)), i * 0.10, 0.6)
        mix(s, sine(2 * f, 0.4, perc(12)), i * 0.10, 0.15)
    return s


def message_pop():
    """Incoming message — soft bubbly pop."""
    f = lambda t: 520 + 700 * (1 - math.exp(-50 * t))
    s = sine(f, 0.28, perc(13))
    mix(s, sine(lambda t: 2 * f(t), 0.28, perc(20)), 0.0, 0.25)
    return s


def alert_attention():
    """Attention alert — two firm repeated tones."""
    s = silence(0.45)
    for off in (0.0, 0.18):
        mix(s, triangle(880, 0.12, ad(0.005, 0.08)), off, 0.7)
    return s


def bell_soft():
    """Soft mallet bell with shimmer."""
    s = sine(1174.7, 0.6, perc(6))            # D6
    mix(s, sine(2349.3, 0.6, perc(11)), 0.0, 0.3)
    mix(s, sine(3524.0, 0.6, perc(18)), 0.0, 0.12)
    return s


SOUNDS = [
    ("ping",            "Single bright ping",                 ping_simple),
    ("chime_two_note",  "Two-note chime (C6→G6)",             chime_two_note),
    ("chime_three_note","Ascending three-note chime",         chime_three_note),
    ("message_pop",     "Soft bubbly message pop",            message_pop),
    ("alert_attention", "Two firm attention tones",           alert_attention),
    ("bell_soft",       "Soft mallet bell with shimmer",      bell_soft),
]
